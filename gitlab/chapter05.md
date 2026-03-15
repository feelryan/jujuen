# 1. 前言與學習目標 (Introduction and Learning Goals)

在資深工程師的職涯中，CI（持續整合）通常已經是標準配備，但 CD（持續部署）的成熟度往往決定了團隊的交付速度與穩定性。本章將超越基礎的 `script` 執行，深入探討如何利用 GitLab 的進階功能來實現企業級的部署策略。

In the career of a Senior Software Engineer, CI (Continuous Integration) is usually standard practice, but the maturity of CD (Continuous Deployment) often dictates a team's delivery speed and stability. This chapter moves beyond basic script execution to explore how to leverage GitLab's advanced features for enterprise-grade deployment strategies.

完成本章後，你將能夠：
By the end of this chapter, you will be able to:

1.  **區分並實作進階部署策略**：理解 Canary（金絲雀）與 Blue-Green（藍綠）部署在 GitLab 中的配置方式，並知曉何時使用哪一種。
    **Distinguish and implement advanced deployment strategies**: Understand how to configure Canary and Blue-Green deployments in GitLab, and know when to use which.
2.  **掌握 Feature Flags（功能開關）的生命週期**：學會如何利用 GitLab Feature Flags 解耦「部署（Deploy）」與「發布（Release）」，降低上線風險。
    **Master the Feature Flag lifecycle**: Learn how to use GitLab Feature Flags to decouple "Deployment" from "Release," reducing rollout risk.
3.  **建立 GitOps 工作流**：利用 GitLab Agent for Kubernetes 實現 Pull-based 的部署架構，提升安全性與狀態一致性。
    **Establish a GitOps workflow**: Use the GitLab Agent for Kubernetes to implement a Pull-based deployment architecture, enhancing security and state consistency.

---

# 2. 核心觀念與心智模型 (Core Concepts & Mental Model)

## 2.1 部署策略：漸進式交付 (Deployment Strategies: Progressive Delivery)

**概念 (Concept)**：
傳統的部署往往是「全有或全無（All-or-Nothing）」，一旦出錯，所有使用者都會受影響。**漸進式交付**則像是一個調光器（Dimmer Switch），而非開關（Toggle Switch）。
Traditional deployment is often "All-or-Nothing"; if something goes wrong, all users are affected. **Progressive Delivery** is like a dimmer switch, not a toggle switch.

-   **Canary Deployment (金絲雀部署)**：將新版本部署給一小部分流量（例如 5%），確認無誤後再逐步擴大。
    **Canary Deployment**: Deploys the new version to a small percentage of traffic (e.g., 5%). Once verified, the traffic is gradually increased.
-   **Blue-Green Deployment (藍綠部署)**：同時維持兩個生產環境（藍與綠）。新版本部署在閒置環境，測試通過後，透過負載平衡器瞬間切換流量。
    **Blue-Green Deployment**: Maintains two production environments (Blue and Green). The new version is deployed to the idle environment. After testing, traffic is instantly switched via the load balancer.

**心智模型 (Mental Model)**：
想像你在更換飛機引擎。
-   **Canary** 是先換一顆引擎，看看飛機飛得順不順，再換其他的。
-   **Blue-Green** 是旁邊準備了一架已經換好引擎的新飛機，乘客直接換機搭乘。

Imagine you are changing airplane engines.
-   **Canary** is changing one engine first, seeing if the plane flies smoothly, then changing the others.
-   **Blue-Green** is having a new plane with new engines ready next door, and passengers simply switch planes.

## 2.2 GitOps：Push vs. Pull

**概念 (Concept)**：
-   **Push-based (CIOps)**：CI Pipeline 擁有叢集的憑證（Credentials），主動執行 `kubectl apply`。這就像是你拿著鑰匙去開門。
    **Push-based (CIOps)**: The CI Pipeline holds the cluster credentials and actively executes `kubectl apply`. This is like you holding the key to open the door.
-   **Pull-based (GitOps)**：叢集內部的 Agent 主動監控 Git Repository 的變化，並將叢集狀態同步至 Git 定義的狀態。這就像門鎖會自動感應你是否有權限並開啟，你不需要把鑰匙（憑證）交給外部系統。
    **Pull-based (GitOps)**: An Agent inside the cluster actively monitors changes in the Git Repository and synchronizes the cluster state to match the Git definition. This is like a lock that automatically senses if you have permission and opens; you don't need to give the key (credentials) to an external system.

**GitLab 的角色 (GitLab's Role)**：
GitLab 透過 **GitLab Agent for Kubernetes** 同時支援這兩種模式，但在資深架構設計中，我們傾向於 Pull-based 以獲得更好的安全性（CI 不需要 Cluster Admin 權限）。
GitLab supports both modes via the **GitLab Agent for Kubernetes**, but in senior architectural designs, we favor Pull-based for better security (CI doesn't need Cluster Admin permissions).

---

# 3. 實務場景與系統設計視角 (Real-World & System Design View)

在設計一個高可用性（High Availability）的微服務系統時，持續部署的架構直接影響系統的 **MTTR (Mean Time To Recovery)** 和 **安全性 (Security)**。

When designing a High Availability microservices system, the continuous deployment architecture directly impacts the system's **MTTR (Mean Time To Recovery)** and **Security**.

## 3.1 架構設計 (Architecture Design)

在典型的 Kubernetes 環境中，GitLab 的整合架構如下：
In a typical Kubernetes environment, the GitLab integration architecture looks like this:

1.  **Code & Config**: 應用程式碼與 Helm Charts/Kustomize 設定檔存放在 GitLab Repo。
    **Code & Config**: Application code and Helm Charts/Kustomize configs are stored in the GitLab Repo.
2.  **CI Pipeline**: 負責 Build Docker Image、執行單元測試、掃描弱點，並將 Image 推送到 Container Registry。
    **CI Pipeline**: Responsible for building Docker Images, running unit tests, scanning for vulnerabilities, and pushing images to the Container Registry.
3.  **GitLab Agent (The Bridge)**: 安裝在 K8s Cluster 內。它與 GitLab 實例建立雙向通道（WebSocket）。
    **GitLab Agent (The Bridge)**: Installed inside the K8s Cluster. It establishes a bidirectional channel (WebSocket) with the GitLab instance.
4.  **Ingress Controller**: 配合 GitLab 的 Canary 設定（透過 Annotations），動態調整流量權重（例如 NGINX Ingress 或 Istio）。
    **Ingress Controller**: Works with GitLab's Canary settings (via Annotations) to dynamically adjust traffic weights (e.g., NGINX Ingress or Istio).

## 3.2 對系統屬性的影響 (Impact on System Attributes)

-   **安全性 (Security)**：使用 GitLab Agent 後，我們不需要將 `KUBECONFIG` 或 Cluster Admin Token 儲存在 GitLab CI/CD Variables 中。這消除了憑證洩漏的巨大風險。
    **Security**: With GitLab Agent, we don't need to store `KUBECONFIG` or Cluster Admin Tokens in GitLab CI/CD Variables. This eliminates a massive risk of credential leakage.
-   **可觀測性 (Observability)**：GitLab 環境儀表板（Environment Dashboard）能直接顯示哪些 Pods 正在運行、Canary 的流量比例為何，讓開發者不需切換到 `kubectl` 即可掌握部署狀態。
    **Observability**: The GitLab Environment Dashboard can directly show which Pods are running and what the Canary traffic percentage is, allowing developers to grasp deployment status without switching to `kubectl`.
-   **解耦 (Decoupling)**：透過 Feature Flags，行銷活動的發布（Release）可以由 Product Manager 控制，而不需等待工程師部署（Deploy）。這降低了工程團隊在非上班時間待命的需求。
    **Decoupling**: Through Feature Flags, marketing releases can be controlled by Product Managers without waiting for engineers to Deploy. This reduces the need for engineering teams to be on-call during off-hours.

---

# 4. 逐步示例 (Walkthrough / Example)

本節將演示如何結合 **GitLab Agent for Kubernetes** 與 **Canary Deployment**。
This section demonstrates how to combine **GitLab Agent for Kubernetes** with **Canary Deployment**.

## 4.1 前置準備：註冊 Agent (Prerequisite: Registering the Agent)

首先，在 Repository 中建立 Agent 設定檔。
First, create the Agent configuration file in the repository.

```yaml
# .gitlab/agents/my-k8s-agent/config.yaml
gitops:
  manifest_projects:
    - id: "group/project-name"
      paths:
        - glob: "k8s-manifests/**/*.yaml"
ci_access:
  projects:
    - id: "group/project-name"
```

*說明*：這告訴 Agent 監控 `k8s-manifests` 目錄下的變更，並允許 CI Pipeline 透過此 Agent 進行操作。
*Explanation*: This tells the Agent to monitor changes in the `k8s-manifests` directory and allows the CI Pipeline to operate via this Agent.

## 4.2 CI/CD Pipeline 設定 (CI/CD Pipeline Configuration)

在 `.gitlab-ci.yml` 中定義 Canary 與 Production 階段。
Define Canary and Production stages in `.gitlab-ci.yml`.

```yaml
stages:
  - build
  - deploy-canary
  - deploy-production

variables:
  KUBE_CONTEXT: "group/project-name:my-k8s-agent"

deploy_canary:
  stage: deploy-canary
  image: dtzar/helm-kubectl:latest
  environment:
    name: production
    action: start
    deployment_tier: production
  script:
    # 假設使用 Helm，設定 canary.enabled=true 與權重
    # Assuming Helm usage, setting canary.enabled=true and weight
    - helm upgrade --install my-app ./charts/my-app 
      --set canary.enabled=true 
      --set canary.weight=10 
      --kube-context $KUBE_CONTEXT
  rules:
    - if: $CI_COMMIT_TAG

deploy_production:
  stage: deploy-production
  image: dtzar/helm-kubectl:latest
  environment:
    name: production
    action: start
  script:
    # 提升至 100% 流量，關閉 Canary
    # Promote to 100% traffic, disable Canary
    - helm upgrade --install my-app ./charts/my-app 
      --set canary.enabled=false 
      --kube-context $KUBE_CONTEXT
  when: manual # 手動確認後執行 (Execute after manual confirmation)
  needs: ["deploy_canary"]
```

## 4.3 實作 Feature Flags (Implementing Feature Flags)

除了基礎設施層面的 Canary，我們在應用層使用 Feature Flags。GitLab 內建支援 Unleash 協議。
Beyond infrastructure-level Canary, we use Feature Flags at the application layer. GitLab has built-in support for the Unleash protocol.

**Python 範例 (Python Example)**:

```python
from UnleashClient import UnleashClient

# 初始化 Client (Initialize Client)
client = UnleashClient(
    url="https://gitlab.com/api/v4/feature_flags/unleash/PROJECT_ID",
    app_name="production",
    instance_id="GL_INSTANCE_ID_TOKEN"
)
client.initialize()

def process_payment(user_id, amount):
    # 檢查 Flag 狀態 (Check Flag status)
    if client.is_enabled("new_payment_flow", context={'userId': user_id}):
        return new_payment_provider.charge(amount)
    else:
        return legacy_payment_provider.charge(amount)
```

**思考步驟 (Thinking Steps)**：
1.  **定義 Flag**：在 GitLab UI 中建立 `new_payment_flow`。
    **Define Flag**: Create `new_payment_flow` in the GitLab UI.
2.  **策略設定**：設定策略為 "Percent of users" (例如 10%) 或 "User IDs" (針對特定測試者)。
    **Strategy Setup**: Set the strategy to "Percent of users" (e.g., 10%) or "User IDs" (for specific testers).
3.  **部署程式碼**：程式碼部署後，`new_payment_flow` 預設為關閉，不影響現有邏輯。
    **Deploy Code**: After code deployment, `new_payment_flow` is off by default, not affecting existing logic.
4.  **開啟開關**：在 UI 上開啟 Flag，即時生效，無需重新部署。
    **Toggle On**: Turn on the Flag in the UI; it takes effect immediately without redeployment.

---

# 5. 常見錯誤與反模式 (Common Pitfalls & Anti-patterns)

## 5.1 資料庫遷移的陷阱 (The Database Migration Trap)

**錯誤 (Mistake)**：在 Canary 部署階段執行了破壞性的資料庫變更（例如刪除欄位），導致舊版本（佔 90% 流量）的應用程式崩潰。
**Mistake**: Executing destructive database changes (e.g., dropping a column) during the Canary deployment phase, causing the old version (handling 90% of traffic) to crash.

**修正 (Fix)**：
-   **Expand and Contract Pattern**：資料庫變更必須向後相容（Backward Compatible）。
    **Expand and Contract Pattern**: Database changes must be backward compatible.
-   第一階段（Expand）：新增欄位，舊程式碼不讀取它。
    Phase 1 (Expand): Add the new column; old code ignores it.
-   第二階段（Migrate）：部署新程式碼，開始寫入新欄位。
    Phase 2 (Migrate): Deploy new code that writes to the new column.
-   第三階段（Contract）：待舊版本完全退役後，再刪除舊欄位。
    Phase 3 (Contract): After the old version is fully retired, drop the old column.

## 5.2 Feature Flag 債務 (Feature Flag Debt)

**錯誤 (Mistake)**：Feature Flags 為了測試而加，但在功能穩定全量上線後，沒有回頭清理程式碼中的 `if/else` 邏輯。
**Mistake**: Feature Flags are added for testing, but after the feature is stable and fully rolled out, the `if/else` logic in the code is never cleaned up.

**後果 (Consequence)**：程式碼複雜度指數上升，測試案例組合爆炸，且可能因為意外關閉 Flag 導致系統回到幾年前的舊邏輯（甚至該邏輯已無法運作）。
**Consequence**: Code complexity skyrockets, test case permutations explode, and accidentally turning off a flag could revert the system to years-old logic (which might not even work anymore).

**修正 (Fix)**：在 Backlog 中建立清理任務。當 Flag 開啟 100% 超過兩週且無異常，應立即刪除 Flag 與相關死代碼（Dead Code）。
**Fix**: Create cleanup tasks in the backlog. Once a flag has been at 100% for two weeks without issues, immediately remove the flag and associated dead code.

## 5.3 混合 GitOps 與手動操作 (Mixing GitOps with Manual Operations)

**錯誤 (Mistake)**：使用了 GitLab Agent 同步 K8s 狀態，但緊急時刻工程師仍使用 `kubectl edit` 直接修改 Cluster 資源。
**Mistake**: Using GitLab Agent to sync K8s state, but engineers still use `kubectl edit` to modify Cluster resources directly during emergencies.

**後果 (Consequence)**：Agent 會偵測到狀態不一致（Drift）並嘗試覆蓋回去，或者下次部署時覆蓋手動修改，導致「修好了又壞掉」的幽靈問題。
**Consequence**: The Agent will detect state drift and try to overwrite it, or the next deployment will overwrite the manual fix, leading to "fixed then broken again" phantom issues.

---

# 6. 面試與實務問答切入點 (Interview & Discussion Hooks)

## Q1: 你會如何設計一個支援「一鍵回滾（One-Click Rollback）」的部署 Pipeline？
**How would you design a deployment pipeline that supports "One-Click Rollback"?**

*   **高分回答要點 (Key Points for a High Score)**：
    *   **不可變基礎設施 (Immutable Infrastructure)**：強調每次部署都是新的 Docker Image Tag，而不是覆蓋 `latest`。
        **Immutable Infrastructure**: Emphasize that every deployment is a new Docker Image Tag, not overwriting `latest`.
    *   **GitOps / Version Control**：回滾不應該是重新跑 CI Build，而是 `git revert` 部署設定檔（Manifests）到上一個 Commit，讓 GitLab Agent 自動同步舊狀態。
        **GitOps / Version Control**: Rollback shouldn't be re-running the CI Build, but `git revert`-ing the deployment manifests to the previous commit, letting the GitLab Agent automatically sync the old state.
    *   **快速切換**：如果是 Blue-Green，回滾只是 Load Balancer 指回舊環境，速度最快。
        **Fast Switching**: If using Blue-Green, rollback is just pointing the Load Balancer back to the old environment, which is instant.

## Q2: 在微服務架構中，Feature Flags 與環境變數（Environment Variables）有什麼區別？何時使用哪個？
**In a microservices architecture, what is the difference between Feature Flags and Environment Variables? When to use which?**

*   **高分回答要點 (Key Points for a High Score)**：
    *   **靜態 vs 動態**：環境變數通常需要重啟 Pod/Service 才能生效（部署成本）；Feature Flags 可以在 Runtime 動態切換（無部署成本）。
        **Static vs. Dynamic**: Environment variables usually require restarting the Pod/Service to take effect (deployment cost); Feature Flags can be toggled dynamically at Runtime (no deployment cost).
    *   **粒度 (Granularity)**：環境變數是對整個實例生效；Feature Flags 可以針對特定 User ID、地區或百分比流量生效。
        **Granularity**: Environment variables apply to the whole instance; Feature Flags can target specific User IDs, regions, or traffic percentages.
    *   **使用情境**：資料庫連線字串、API Key 用環境變數；新功能測試、斷路器（Circuit Breaker）控制用 Feature Flags。
        **Use Cases**: DB connection strings, API Keys use Environment Variables; New feature testing, Circuit Breaker controls use Feature Flags.

## Q3: 引入 GitLab Agent for Kubernetes 後，如何管控開發者的權限？
**After introducing GitLab Agent for Kubernetes, how do you manage developer permissions?**

*   **高分回答要點 (Key Points for a High Score)**：
    *   **RBAC 映射**：說明如何透過 `config.yaml` 將 GitLab 的 User/Group 映射到 Kubernetes 的 ServiceAccount 或 RBAC Role。
        **RBAC Mapping**: Explain how to map GitLab Users/Groups to Kubernetes ServiceAccounts or RBAC Roles via `config.yaml`.
    *   **最小權限原則**：CI Pipeline 只需要特定 Namespace 的部署權限，不需要 Cluster Admin。
        **Least Privilege**: The CI Pipeline only needs deployment permissions for specific Namespaces, not Cluster Admin.
    *   **Impersonation**：Agent 可以使用 Impersonation 功能，讓 K8s Audit Log 記錄是哪個 GitLab User 觸發的操作。
        **Impersonation**: The Agent can use Impersonation, so K8s Audit Logs record which GitLab User triggered the operation.

---

# 7. 小結與後續延伸 (Summary & Next Steps)

## 本章重點 (Key Takeaways)
1.  **GitOps 是趨勢**：透過 GitLab Agent 實現 Pull-based 部署，解決了傳統 CI Push 模式的安全性與憑證管理問題。
    **GitOps is the trend**: Implementing Pull-based deployment via GitLab Agent solves security and credential management issues inherent in traditional CI Push models.
2.  **部署 != 發布**：利用 Feature Flags 將程式碼部署（Deployment）與功能對使用者可見（Release）解耦，是降低風險的關鍵。
    **Deployment != Release**: Decoupling code deployment from feature visibility using Feature Flags is key to reducing risk.
3.  **策略性部署**：Canary 適合逐步驗證效能與錯誤率；Blue-Green 適合需要瞬間切換且資源充足的場景。
    **Strategic Deployment**: Canary is suitable for gradual verification of performance and error rates; Blue-Green is suitable for scenarios requiring instant switching and ample resources.
4.  **資料庫是瓶頸**：進階部署策略必須配合「向後相容」的資料庫遷移策略（Expand-Contract）。
    **Database is the bottleneck**: Advanced deployment strategies must be paired with "backward compatible" database migration strategies (Expand-Contract).
5.  **環境即代碼**：所有的環境設定、Flag 規則、部署清單都應納入版本控制。
    **Environment as Code**: All environment settings, Flag rules, and deployment manifests should be under version control.

## 後續延伸 (Next Steps)
-   **Observability Integration**: 學習如何將 Prometheus/Grafana 與 GitLab CI 整合，實現「自動回滾（Auto-Rollback）」——當 Canary 錯誤率超過閾值時，GitLab 自動停止部署。
    **Observability Integration**: Learn how to integrate Prometheus/Grafana with GitLab CI to implement "Auto-Rollback"—automatically halting deployment when Canary error rates exceed a threshold.
-   **Security Scanning (DevSecOps)**: 下一章將探討如何在 Pipeline 中加入 SAST/DAST 與 Container Scanning，確保部署出去的 Image 是安全的。
    **Security Scanning (DevSecOps)**: The next chapter will explore adding SAST/DAST and Container Scanning to the Pipeline to ensure deployed Images are secure.