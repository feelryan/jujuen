# 部署模式與發布策略 / Deployment Patterns & Release Strategies

## Mental model｜心智模型

在微服務架構中，最關鍵的思維轉變是將 **「部署 (Deployment)」** 與 **「發布 (Release)」** 解耦。

- **Deployment (部署)**：是一個技術操作。指將新版本的軟體二進位檔或容器映像檔安裝到基礎設施（如 Kubernetes Cluster）上。此時，新版本可能已經在運行，但**不一定**有使用者流量進入。
- **Release (發布)**：是一個業務決策。指將生產環境的流量（Traffic）導向新版本，讓使用者真正接觸到新功能。

### The Valve Metaphor (閥門隱喻)
想像你的基礎設施是一個巨大的水管系統，流量是水。
- **傳統模式**：更換水管時必須關閉總水源（Downtime），換好後重新打開。
- **微服務模式**：你並聯安裝了一根新水管（Deployment），然後透過調節閥門（Load Balancer / Service Mesh / Feature Flags），慢慢將水流從舊管轉向新管（Release）。

**核心目標**：
1. **Zero Downtime**：服務永不中斷。
2. **Blast Radius Containment (控制爆炸半徑)**：若新版本有 Bug，受影響的用戶應被限制在最小範圍（如 1% 的流量）。
3. **Progressive Delivery (漸進式交付)**：透過數據（Metrics）驅動流量切換，而非憑感覺。

---

## Patterns & best practices｜常見模式與最佳實務

### 1. Blue-Green Deployment (藍綠部署)
最簡單的「全有或全無」切換模式。
- **機制**：同時維護兩套完全相同的環境（Blue 為舊版 Current，Green 為新版 Next）。
- **流程**：部署 Green -> 在 Green 跑測試 -> Load Balancer 瞬間切換 100% 流量至 Green -> 觀察 -> 若失敗則瞬間切回 Blue。
- **適用場景**：資源充裕、無法進行細粒度流量分割的 legacy 系統、或簡單的無狀態服務。
- **關鍵點**：資料庫必須向後相容（Backward Compatibility），否則切換回 Blue 時會崩潰。

### 2. Canary Release (金絲雀發布)
微服務的主流標準，風險最低。
- **機制**：先讓一小部分使用者（如 1% -> 5% -> 25%）使用新版本，確認無誤後再全量推廣。
- **實作方式**：
  - **Weighted Routing (權重路由)**：基於 Service Mesh (Istio/Linkerd) 或 Ingress Controller (Nginx/Traefik)。
  - **User Segmentation (用戶分群)**：基於 HTTP Header (e.g., `x-user-type: beta-tester`) 定向路由。
- **自動化 (Automated Canary Analysis)**：結合 Prometheus 與 CD 工具 (如 Flagger, Argo Rollouts)，若 Error Rate 超過閾值自動 Rollback。

### 3. Feature Toggles / Flags (功能開關)
將發布控制權下放到「程式碼層級」，而非「基礎設施層級」。
- **機制**：在程式碼中包覆 `if (featureManager.isEnabled("new-algo")) { ... }`。
- **優勢**：
  - 實現 **Trunk-based Development**：未完成的程式碼可以先 merge 到 main branch 並部署，只要開關關閉即可。
  - **Operational Toggle**：當系統負載過高時，可以透過開關降級服務（如關閉推薦系統）。

### 4. Shadow Deployment / Dark Launch (影子部署)
- **機制**：將生產流量「複製」一份發送到新版本（Fire-and-forget），但**丟棄**新版本的回傳結果。
- **目的**：在不影響使用者的情況下，測試新版本在高併發下的效能與穩定性。
- **工具**：Istio Mirroring, Goreplay。

### 5. Service Mesh 的角色
Service Mesh (如 Istio) 是現代微服務部署的加速器：
- **Traffic Shifting**：將流量控制邏輯從應用程式碼中剝離（Sidecar 模式）。
- **Observability**：在 Canary 期間提供黃金指標（Latency, Error Rate, Saturation）作為自動回滾的依據。

---

## Anti-patterns & pitfalls｜反模式與踩雷點

### 1. The Distributed Monolith Deployment (分散式單體部署)
- **現象**：Service A 的新版本必須和 Service B、Service C 的新版本**同時**部署，否則會壞掉。
- **後果**：失去了微服務獨立部署的優勢，協調成本極高。
- **解法**：嚴格遵守 API 契約測試（Contract Testing），確保服務間的向後相容性。

### 2. Breaking Schema Changes in Blue-Green (藍綠部署中的破壞性 Schema 變更)
- **現象**：新版程式碼（Green）修改了資料庫欄位（例如 rename column），導致切換回舊版（Blue）時，舊版程式碼無法讀取資料。
- **解法**：使用 **Expand and Contract (擴展-收縮)** 模式進行資料庫遷移：
  1. **Expand**: 新增欄位，舊欄位保留（雙寫）。
  2. **Migrate**: 部署新版程式碼，讀新欄位。
  3. **Contract**: 待舊版完全退役後，刪除舊欄位。

### 3. Toggle Debt (開關債)
- **現象**：Feature Flags 用完後不刪除，程式碼充滿了過期的 `if/else` 邏輯。
- **後果**：程式碼複雜度爆炸，甚至發生舊開關意外被觸發的事故（如 Knight Capital 4.4億美元虧損事件）。
- **解法**：將「刪除 Flag」視為 Feature 完成 Definition of Done (DoD) 的一部分。

### 4. Manual Canary Verification (人工驗證金絲雀)
- **現象**：部署了 Canary，然後工程師盯著 Log 視窗看 10 分鐘，憑感覺決定是否放行。
- **後果**：人類無法察覺 0.1% 的錯誤率上升，且反應速度太慢。
- **解法**：必須自動化。使用工具（如 Flagger）設定明確指標（例如：HTTP 500 < 1%, Latency P99 < 200ms）。

---

## Checklists & workflows｜檢查清單與流程

### Decision Tree: Choosing a Strategy
- **涉及資料庫破壞性變更？**
  - YES -> 使用 **Expand-Contract** 模式配合 Rolling Update。
  - NO -> 繼續。
- **前端 UI 重大改版？**
  - YES -> 使用 **Feature Flags** (針對特定 User ID 開啟) 或 Blue-Green (切換 DNS/Route)。
  - NO -> 繼續。
- **高流量核心後端服務？**
  - YES -> 使用 **Automated Canary** (Argo Rollouts / Flagger)。
  - NO (內部後台/低流量) -> **Rolling Update** 即可。

### Deployment Checklist (The "Go-No-Go" Check)

#### Pre-deployment (部署前)
- [ ] **Contract Check**: 新版本 API 是否兼容舊版 Consumer？（Consumer-Driven Contracts 驗證通過？）
- [ ] **DB Migration**: 是否有 Schema 變更？是否已執行 Non-breaking migration？
- [ ] **Observability**: 相關的 Metrics Dashboard 與 Alerts 是否已就緒？
- [ ] **Feature Flags**: 新功能的開關預設狀態是否正確（通常預設為 False）？

#### During Deployment (部署中 - Canary 階段)
- [ ] **Health Check**: Pod/Container 是否順利啟動 (Liveness/Readiness probes)？
- [ ] **Smoke Test**: 對新版本執行基本的合成監控測試 (Synthetic Monitoring)。
- [ ] **Metrics Watch**:
  - Error Rate 是否異常升高？
  - Latency (P95/P99) 是否顯著變慢？
  - CPU/Memory 使用率是否暴增（Memory Leak 徵兆）？

#### Post-deployment (部署後)
- [ ] **Cleanup**: 移除舊版本資源（Scale down Blue environment）。
- [ ] **Toggle Cleanup**: 若確認穩定，建立 Ticket 安排時間移除 Feature Flag 程式碼。
- [ ] **Notification**: 自動通知相關團隊（Slack/Teams）發布完成。

---

## Real-world examples｜實戰案例

### Scenario: High-Risk Payment Service Update with Istio & Kubernetes

**情境**：你需要更新支付服務 `payment-svc`，修復一個 Bug，但擔心新邏輯會影響交易成功率。

#### 1. Define the Traffic Split (Istio VirtualService)
不直接替換 Deployment，而是部署 `payment-svc-v2`，並利用 Istio 進行流量分割。

```yaml
apiVersion: networking.istio.io/v1alpha3
kind: VirtualService
metadata:
  name: payment-route
spec:
  hosts:
  - payment-svc
  http:
  - route:
    - destination:
        host: payment-svc
        subset: v1
      weight: 90  # 90% 流量維持在舊版
    - destination:
        host: payment-svc
        subset: v2
      weight: 10  # 10% 流量導入新版 (Canary)
```

#### 2. Automated Analysis (Conceptual Flagger Config)
使用 Flagger 定義自動回滾規則。

```yaml
analysis:
  interval: 1m
  threshold: 5
  stepWeight: 10
  maxWeight: 50
  metrics:
    - name: request-success-rate
      thresholdRange:
        min: 99.9  # 成功率低於 99.9% 立即切回 v1
      interval: 1m
    - name: request-duration
      thresholdRange:
        max: 500   # P99 延遲超過 500ms 立即切回 v1
```

#### 3. Feature Flag for Specific Logic
在 `payment-svc-v2` 內部，對於尚未完全驗證的「新信用卡驗證邏輯」，使用 Feature Flag 包覆：

```python
# Python pseudo-code
def process_payment(request):
    user_context = {"user_id": request.user_id, "region": request.region}
    
    # 即使流量進來了，只有特定 User 才會走到新邏輯
    if ld_client.variation("new-validation-logic", user_context, False):
        return validate_with_new_provider(request)
    else:
        return validate_with_legacy_provider(request)
```

### Summary of the Strategy
1. **Deployment**: `v2` Pods 啟動，但無流量。
2. **Canary Release**: Istio 開始導流 10%。
3. **Safety Net**: Flagger 監控 Metrics，若失敗自動改寫 VirtualService 回 100% v1。
4. **Fine-grained Control**: 即使 v2 上線，核心邏輯仍受 Feature Flag 保護，可隨時關閉。