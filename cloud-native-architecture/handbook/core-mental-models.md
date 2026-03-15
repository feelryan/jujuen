# 核心思維：不可變基礎設施與宣告式 API / Core Mental Models: Immutable Infrastructure & Declarative APIs

在踏入雲原生（Cloud-Native）架構的世界之前，最困難的往往不是學習 Kubernetes 的指令，而是**思維模式的轉變（Mindset Shift）**。本章節不談工具操作，而是聚焦於兩個決定系統設計成敗的基石：**Immutable Infrastructure（不可變基礎設施）** 與 **Declarative APIs（宣告式 API）**。

如果不具備這些思維，你只是把舊時代的單體應用「搬運」到了容器裡，卻無法享受雲原生的彈性與自動化優勢。

---

## Mental model｜心智模型

### 1. 寵物 vs. 牛群 (Pets vs. Cattle)
這是最經典但最重要的比喻。
- **傳統思維 (Pets)**：每一台伺服器都有名字（如 `db-prod-01`），我們精心照料它。如果它生病了（故障），我們會 SSH 進去「治療」它（重啟服務、修補 Config）。
- **雲原生思維 (Cattle)**：伺服器或容器是編號的（如 `pod-x89s1`）。如果它生病了，我們不治療，而是直接**殺掉並替換**一隻新的。

### 2. 期望狀態 vs. 當前狀態 (Desired State vs. Current State)
宣告式系統的核心在於**Reconciliation Loop（協調迴圈）**。你不再告訴系統「如何做（How）」，而是告訴它「要什麼（What）」。

- **Imperative (命令式)**：一步步下指令。
  > 「先啟動 A，再啟動 B，然後把 B 加入 Load Balancer。」
  > *風險：如果中間一步失敗，系統會卡在未知狀態。*
- **Declarative (宣告式)**：定義最終樣貌。
  > 「我需要一個由 3 個實例組成的服務，且掛載在 Load Balancer 後面。」
  > *優勢：系統會不斷比對 Current State 與 Desired State，自動修正差異（Self-healing）。*

### 3. 基礎設施即軟體 (Infrastructure is Software)
在雲原生架構中，基礎設施不再是硬體資產，而是**可版本控制的 artifact**。你的 OS Image、你的 Network Policy、你的 Replica Count，全部都是 Code。一旦 Build 完成，這個 Artifact 就是唯讀（Read-only）的。

---

## Patterns & best practices｜常見模式與最佳實務

### 1. Golden Image Pattern (黃金映像檔模式)
不要在容器啟動時執行 `apt-get update` 或 `pip install`。
- **做法**：所有的依賴套件、Runtime 環境、甚至 Application Code 都應該在 Build 階段打包進 Image。
- **優勢**：確保 Dev、Staging、Prod 跑的是完全一樣的位元組（Byte-for-byte identical），消除 "It works on my machine" 問題。

### 2. Externalized Configuration (配置外置)
既然 Image 是不可變的，那不同環境（Dev/Prod）的差異怎麼辦？
- **做法**：將配置（Config）從程式碼中剝離，透過環境變數（Environment Variables）或掛載設定檔（ConfigMaps/Secrets）注入。
- **原則**：**Build once, deploy anywhere.** 同一個 Image 可以在任何環境運行，行為差異僅由注入的 Config 決定。

### 3. The Reconciliation Loop (協調迴圈模式)
這通常由平台（如 K8s Controller）負責，但在設計 Operator 或自定義腳本時需遵循此模式：
1. **Observe**: 觀察當前系統狀態。
2. **Diff**: 比較當前狀態與期望狀態（Manifest）。
3. **Act**: 執行操作以消除差異。
*你的自動化腳本應該是冪等的（Idempotent），即執行多次結果相同，不會產生副作用。*

### 4. Ephemeral Storage (短暫儲存)
假設任何容器隨時可能被重啟或移動。
- **做法**：不要將 Logs 或持久化數據寫入容器的本地檔案系統。Logs 應導向 `stdout/stderr`，數據應寫入外部資料庫或掛載的 Persistent Volume (PV)。

---

## Anti-patterns & pitfalls｜反模式與踩雷點

### 1. Configuration Drift (配置漂移)
這是最常見的災難源頭。
- **現象**：運維人員為了緊急修復，直接 SSH 進 Production 伺服器修改 Nginx 設定檔。
- **後果**：當下次透過 CI/CD 部署新版本時，這個手動修改會被覆蓋，導致舊 Bug 復活（Regression）；或者該伺服器與其他擴展出來的伺服器行為不一致。
- **解法**：**禁止 SSH 到生產環境進行變更**。所有變更必須走 Git Commit -> Build -> Deploy 流程。

### 2. IP Address Dependency (依賴固定 IP)
- **現象**：在設定檔中寫死後端服務的 IP 位址。
- **後果**：在雲原生環境中，Pod/VM 的 IP 是動態且短暫的。重啟後 IP 變更，服務即中斷。
- **解法**：依賴 **Service Discovery**（DNS 名稱或 Service Mesh），而非 IP。

### 3. "Baked-in" Secrets (內嵌機密資訊)
- **現象**：將 API Key 或 DB Password 寫死在 Dockerfile 或 Source Code 中。
- **後果**：安全性漏洞，且無法針對不同環境更換金鑰。
- **解法**：使用 Secret Management 工具（如 Vault, AWS Secrets Manager, K8s Secrets）在 Runtime 動態注入。

### 4. Imperative Scripts in CI/CD (CI/CD 中的命令式腳本)
- **現象**：Pipeline 中充滿了 `kubectl scale ...` 或 `sed -i ...` 等指令。
- **後果**：難以追蹤系統當下的真實狀態，且容易因腳本錯誤導致部分部署。
- **解法**：使用 `kubectl apply -f` 或 GitOps 工具（ArgoCD/Flux）來同步狀態。

---

## Checklists & workflows｜檢查清單與流程

在設計或審查雲原生服務時，請使用此清單確認是否符合核心思維：

### Design & Build Phase
- [ ] **Immutability Check**: 應用程式啟動時，是否會嘗試更新自身的程式碼或系統套件？（應為 No）
- [ ] **State Check**: 如果我現在隨機殺掉這個實例（Instance），資料會遺失嗎？（應為 No，資料應在 DB 或 Object Storage）
- [ ] **Config Check**: 是否可以在不重新 Build Image 的情況下，透過修改環境變數來切換連線的資料庫？（應為 Yes）
- [ ] **Secret Check**: Image 內是否包含任何明文密碼？（應為 No）

### Deployment & Ops Phase
- [ ] **No SSH Policy**: 是否已經移除了開發者對 Production 容器的 SSH 寫入權限？
- [ ] **Idempotency**: 部署腳本如果連續執行兩次，第二次會報錯還是保持現狀？（應保持現狀）
- [ ] **Self-Healing**: 如果手動刪除一個 Pod，系統會自動補回來嗎？（應為 Yes）

### Decision Workflow: Handling a Production Bug
當生產環境發生 Bug 時的決策樹：
1. **緊急止血**：是否需要立即恢復服務？
   - Yes -> Rollback 到上一個穩定的 Image 版本（宣告式變更）。
   - No -> 進入修復流程。
2. **修復流程**：
   - ❌ **錯誤做法**：SSH 進去修改程式碼或設定檔重啟。
   - ✅ **正確做法**：在 Local 修復 -> Commit Code -> CI Build New Image -> CD Update Manifest -> Deploy。

---

## Real-world examples｜實戰案例

### Case 1: The "Snowflake" Server Disaster
**情境**：
某團隊維護一個 Legacy 系統，有一台名為 `payment-processor` 的 VM。這台機器運行了三年，期間運維人員無數次 SSH 上去手動升級 Java 版本、調整 Kernel 參數、修改 Cron Job。

**問題**：
某天硬體故障，這台 VM 毀損。團隊嘗試用 Ansible 腳本重新部署，發現完全跑不起來。因為這三年間的「手動微調」沒有被記錄在 Code 裡。這台伺服器變成了一片獨一無二的「雪花（Snowflake）」，融化了就沒了。

**雲原生解法**：
使用 Dockerfile 定義環境，任何參數調整都必須修改 Dockerfile 或 K8s ConfigMap 並重新部署。即使機器爆炸，1 分鐘內就能在另一台機器拉起一模一樣的環境。

### Case 2: Imperative vs. Declarative Scaling
**需求**：
雙 11 流量大增，需要將 Web Server 從 2 台擴容到 10 台。

**Imperative Approach (Bash script / CLI)**:
```bash
# 運維人員手動執行迴圈
for i in {3..10}; do
  ssh server-$i "systemctl start web-app"
done
```
*風險*：如果 `server-5` 網路不通，腳本中斷，你不知道現在到底有幾台成功了。如果流量下降，你還得寫另一個腳本一台台關掉。

**Declarative Approach (Kubernetes YAML)**:
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: web-app
spec:
  replicas: 10  # 只需要改這個數字
  selector: ...
```
*優勢*：你只需要將 `replicas` 從 2 改為 10 並 `apply`。K8s Control Plane 會發現「現在有 2 個，期望有 10 個，差異是 8 個」，於是自動調度新增 8 個 Pod。如果其中一個節點掛了，總數變 9，K8s 會自動再補 1 個維持 10。這就是 **Declarative** 的威力。