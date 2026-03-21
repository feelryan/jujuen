# 消費者實戰：群組協調與重平衡策略 / Consumer Mastery: Group Coordination and Rebalancing

## Mental model｜心智模型

要掌握 Kafka Consumer，必須先打破「Consumer 只是單純讀取資料」的想像。在 Production 環境中，Consumer Group 是一個**動態協調的分散式系統**。

### 1. The "Team Assignment" Model (團隊分工模型)
想像 Consumer Group 是一個工班（Group），Topic Partitions 是待處理的任務清單。
- **Group Coordinator (Broker 端)** 是工頭，負責維護成員名單。
- **Consumer (Client 端)** 是工人。
- **Rebalance (重平衡)** 是「重新分配任務」的會議。

### 2. The Cost of Coordination (協調的代價)
Rebalance 是必要的惡（Necessary Evil）。當工人加入（Scale out）、離開（Crash/Scale in）或任務數量改變時，必須重新分配。
- **Eager Rebalance (The Old Way)**: "Stop the world". 工頭大喊：「所有人停手！把手上的任務全部丟回桌上！」大家閒置等待，直到重新分配完畢。這會導致 Consumer Lag 瞬間飆高。
- **Cooperative Rebalance (The Modern Way)**: "Incremental". 工頭說：「大家繼續做手上的事，只有負責 Task A 的人把任務交出來給新來的。」這極大化了可用性（Availability）。

### 3. Heartbeat vs. Logic Health (心跳與邏輯健康)
Consumer 有兩條生命線：
1.  **Network Health (`session.timeout.ms`)**: 背景 Thread 發送心跳。如果斷了，代表機器掛了。
2.  **Processing Health (`max.poll.interval.ms`)**: 主 Thread 呼叫 `poll()` 的頻率。如果太久沒 poll，代表程式邏輯卡死（Deadlock 或處理太慢）。

---

## Patterns & best practices｜常見模式與最佳實務

### 1. 啟用 Cooperative Sticky Assignor (黃金標準)
除非你還在使用極舊版本的 Kafka，否則應將 `partition.assignment.strategy` 設為 `CooperativeStickyAssignor`。
- **Why**: 它將 Rebalance 從「全域暫停」變為「漸進式轉移」。
- **Impact**: 在 Rolling Restart（如 K8s Deployment 更新）期間，吞吐量幾乎不會中斷。

### 2. Static Membership (Kubernetes 必備)
在容器化環境中，Pod 重啟會導致 IP 變動，被視為「新成員加入」，觸發 Rebalance。
- **Pattern**: 設定 `group.instance.id`（例如使用 K8s StatefulSet 的 Pod Name）。
- **Effect**: 當 Consumer 短暫離線又回來（在 `session.timeout.ms` 內），Coordinator 認得它是「老員工」，**完全不會觸發 Rebalance**，直接繼續處理原有的 Partition。

### 3. Commit Strategies (提交策略)
Offset 代表「我處理完了」，而不是「我讀到了」。
- **At-Least-Once (Standard)**: 處理訊息 -> `commitSync()` / `commitAsync()`。
- **Batch Commit**: 不要每處理一條就 Commit。累積一批（例如 100 條或每 5 秒）再 Commit，減少 Broker IO 壓力。
- **Async with Sync Fallback**: 平常使用 `commitAsync()` 追求效能（不阻塞），但在 `finally` block 或關閉時使用 `commitSync()` 確保最後狀態被儲存。

### 4. Decoupling Processing (解耦處理)
如果單條訊息處理時間極長（例如 > 1分鐘）：
- **Pattern**: `poll()` 下來的資料丟進內部的 Thread Pool 或 Queue，主 Thread 立即再次 `poll()`。
- **Risk**: 必須小心 Offset 提交順序。若 Thread 2 失敗但 Thread 3 成功，不能隨意 Commit Thread 3 的 Offset。通常需配合 `pause()` / `resume()` 機制來控制流量。

---

## Anti-patterns & pitfalls｜反模式與踩雷點

### 1. The "Infinite Rebalance" Loop (無限重平衡迴圈)
這是最常見的生產環境事故。
- **Symptom**: Consumer 不斷加入又被踢出 Group，Log 出現 "Member ... leaving group"。
- **Root Cause**: 單批資料處理時間超過 `max.poll.interval.ms`（預設 5 分鐘）。Coordinator 認為該 Consumer 邏輯卡死，將其踢出。
- **Fix**: 減少 `max.poll.records`（單次抓取量）或增加 `max.poll.interval.ms`。

### 2. Blocking the Poll Loop (阻塞 Poll 迴圈)
- **Anti-pattern**: 在 `poll()` 迴圈中執行同步的外部 API 呼叫（HTTP/DB），且沒有 Timeout 保護。
- **Consequence**: 外部系統變慢時，直接拖垮 Consumer，導致 Rebalance 甚至 Lag 堆積。

### 3. Committing "Read" instead of "Processed"
- **Anti-pattern**: 開啟 `enable.auto.commit=true` 但業務邏輯是異步執行的。
- **Consequence**: Consumer 收到訊息後自動 Commit，但在異步處理完成前 Crash。重啟後，該訊息被視為「已處理」，導致**資料遺失（Data Loss）**。

### 4. Misunderstanding Session Timeout
- **Pitfall**: 將 `session.timeout.ms` 設得極短（例如 3s）以求快速偵測故障。
- **Consequence**: 輕微的網路抖動或 GC Pause 就會導致頻繁的 Rebalance 風暴。建議值通常在 10s - 45s 之間。

---

## Checklists & workflows｜檢查清單與流程

### Configuration Tuning Checklist (上線前必查)

- [ ] **Rebalance Strategy**: `partition.assignment.strategy` 是否包含 `org.apache.kafka.clients.consumer.CooperativeStickyAssignor`？
- [ ] **Processing Time**: 你的 `max.poll.records` * 平均單條處理時間，是否遠小於 `max.poll.interval.ms`？（建議預留 50% buffer）。
- [ ] **Failure Detection**: `session.timeout.ms` 是否設為合理值（如 45s）？`heartbeat.interval.ms` 是否為 session timeout 的 1/3（如 15s）？
- [ ] **Auto Offset Reset**: `auto.offset.reset` 是 `earliest` 還是 `latest`？（生產環境通常建議 `earliest` 以免漏掉部署期間的資料）。
- [ ] **Static Membership**: 若在 K8s 上運行，是否配置了 `group.instance.id`？

### Debugging Rebalance Issues Workflow (除錯流程)

1.  **Check Logs**: 搜尋 `RebalanceInProgress` 或 `JoinGroup`。頻率是多少？
2.  **Identify Trigger**:
    - 是因為 **Member Leave**？（正常部署或 Crash）
    - 是因為 **Member Failure**？（沒收到 Heartbeat -> 檢查 GC logs 或網路）
    - 是因為 **Max Poll Interval Exceeded**？（邏輯處理太慢 -> 這是最常見原因）
3.  **Analyze Lag**: Rebalance 期間 Lag 是否直線上升？如果是，考慮切換到 Cooperative Rebalance。

---

## Real-world examples｜實戰案例

### Scenario 1: The Kubernetes Rolling Update
**情境**: 你有一個 Consumer Group 部署在 K8s Deployment，有 10 個 Pods。你需要更新 Image。

- **Bad Practice (Default)**:
  K8s 逐一砍掉 Pod 再啟動新 Pod。每次 Pod 消失觸發一次 Rebalance，新 Pod 起來又觸發一次。總共 20 次 Rebalance。每次都會 "Stop the world"。
  *結果*: 整個更新過程 Consumer 幾乎處於癱瘓狀態，Lag 暴增。

- **Good Practice (Static Membership)**:
  配置 `group.instance.id = "consumer-pod-${POD_ORDINAL}"` (配合 StatefulSet) 且 `session.timeout.ms = 60000`。
  當 Pod 重啟（假設 30秒內完成），Coordinator 只是標記它 "Away"，**不會觸發 Rebalance**。Partition 歸屬權保持不變。
  *結果*: 只有該 Pod 負責的 Partition 暫停消費 30秒，其餘 9 個 Pod 完全不受影響。

### Scenario 2: The Heavy Image Processor
**情境**: Consumer 收到圖片 URL，需要下載並進行 OCR 辨識，平均耗時 3 秒。

- **Problem**: 預設 `max.poll.records = 500`。
  `500 * 3s = 1500s (25分鐘)` >> `max.poll.interval.ms (5分鐘)`。
  Consumer 處理到第 100 張圖時，被 Coordinator 踢出群組。Commit 失敗。重啟後又從第 1 張開始，陷入無窮迴圈。

- **Solution**:
  1.  **調降 Batch Size**: 設定 `max.poll.records = 20`。 (20 * 3s = 60s < 5min)。
  2.  **手動 Commit**: 使用 `enable.auto.commit = false`。每處理完一張圖（或一小批）就 `commitSync`，避免重複處理太多。