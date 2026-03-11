# 1. 前言與學習目標 (Introduction & Learning Goals)

在傳統的 CI/CD 流程中，CD（Continuous Deployment）往往被視為 CI pipeline 的最後一步：執行一段 script 將 artifact 推送到伺服器。然而，在 Cloud-Native 的世界裡，隨著 Kubernetes 與微服務架構的普及，這種「推播式（Push-based）」的部署方式面臨了安全性、狀態一致性與可觀測性的挑戰。

In traditional CI/CD workflows, CD (Continuous Deployment) is often treated as the final step of the CI pipeline: running a script to push artifacts to servers. However, in the Cloud-Native world, with the ubiquity of Kubernetes and microservices, this "Push-based" deployment approach faces challenges regarding security, state consistency, and observability.

本章將探討 **GitOps** 模型與 **漸進式部署（Progressive Deployment）**。這不僅是工具的轉換（如從 Jenkins 轉向 ArgoCD），更是思維模式從「命令式操作（Imperative）」轉向「宣告式調和（Declarative Reconciliation）」的過程。

This chapter explores the **GitOps** model and **Progressive Deployment**. This is not just a tooling shift (e.g., from Jenkins to ArgoCD) but a paradigm shift from "Imperative Operations" to "Declarative Reconciliation."

完成本章後，你應該能夠：
By the end of this chapter, you should be able to:

1.  **解釋並實作 GitOps 核心循環**：理解為何將 Git 作為「單一事實來源（Single Source of Truth）」，並利用 Pull-based 機制自動同步叢集狀態。
    **Explain and implement the GitOps core loop:** Understand why Git serves as the "Single Source of Truth" and utilize the Pull-based mechanism to automatically synchronize cluster state.
2.  **設計漸進式部署策略**：區分 Canary（金絲雀）與 Blue/Green（藍綠）部署的適用場景，並使用 Argo Rollouts 或 Flux Flagger 實作。
    **Design progressive deployment strategies:** Distinguish between Canary and Blue/Green deployment scenarios and implement them using Argo Rollouts or Flux Flagger.
3.  **整合自動化回滾機制**：結合 Prometheus/Datadog metrics，當新版本錯誤率上升時，系統能自動停止發布並回滾，無需人工介入。
    **Integrate automated rollback mechanisms:** Combine Prometheus/Datadog metrics so that if the error rate rises, the system automatically halts the release and rolls back without human intervention.

---

# 2. 核心觀念與心智模型 (Core Concepts & Mental Model)

## 2.1 GitOps：基礎設施的自動調溫器 (GitOps: The Infrastructure Thermostat)

最直觀理解 GitOps 的方式是將其類比為**空調恆溫器（Thermostat）**。
The most intuitive way to understand GitOps is to compare it to an **AC Thermostat**.

-   **Git Repository (Desired State / 預期狀態)**：你設定的溫度（例如 24°C）。這是你希望系統達到的狀態。
    **Git Repository (Desired State):** The temperature you set (e.g., 24°C). This is the state you want the system to achieve.
-   **Kubernetes Cluster (Actual State / 實際狀態)**：房間目前的溫度（例如 28°C）。
    **Kubernetes Cluster (Actual State):** The current room temperature (e.g., 28°C).
-   **GitOps Controller (e.g., ArgoCD)**：空調主機。它不斷監測兩者的差異（Drift），並啟動冷氣（Apply Changes）直到兩者一致。
    **GitOps Controller (e.g., ArgoCD):** The AC unit. It continuously monitors the difference (Drift) and activates cooling (Apply Changes) until both match.

與傳統 CI/CD 的差異在於：傳統 CD 是「射後不理（Fire and Forget）」，一旦 script 跑完，CI server 就不再關心叢集狀態；GitOps 則是「持續調和（Continuous Reconciliation）」，若有人手動修改了叢集（Configuration Drift），GitOps Controller 會偵測到並將其改回 Git 定義的狀態。

The difference from traditional CI/CD is: Traditional CD is "Fire and Forget"—once the script finishes, the CI server no longer cares about the cluster state. GitOps is "Continuous Reconciliation"—if someone manually modifies the cluster (Configuration Drift), the GitOps Controller detects it and reverts it to the state defined in Git.

## 2.2 漸進式部署 (Progressive Deployment)

漸進式部署是為了控制**爆炸半徑（Blast Radius）**。
Progressive deployment is about controlling the **Blast Radius**.

-   **Big Bang Deployment**：一次將所有實例更新為 v2。若 v2 有 bug，100% 的用戶受影響。
    **Big Bang Deployment:** Updating all instances to v2 at once. If v2 has a bug, 100% of users are affected.
-   **Canary Deployment**：先將 5% 流量導向 v2，觀察一段時間（Metrics Analysis），若無異常則逐步增加流量（20% -> 50% -> 100%）。
    **Canary Deployment:** Direct 5% of traffic to v2 first, observe for a period (Metrics Analysis), and if normal, gradually increase traffic (20% -> 50% -> 100%).
-   **Blue/Green Deployment**：同時維持 v1 (Blue) 與 v2 (Green) 兩套完整環境。測試通過後，透過 Load Balancer 瞬間切換流量。適合不允許版本共存的場景。
    **Blue/Green Deployment:** Maintain two full environments, v1 (Blue) and v2 (Green), simultaneously. After testing, switch traffic instantly via Load Balancer. Suitable for scenarios where version coexistence is not allowed.

---

# 3. 實務場景與系統設計視角 (Real-World & System Design View)

在資深工程師的系統設計中，GitOps 不僅僅是部署工具，更是**安全性**與**多叢集管理**的基石。
In senior-level system design, GitOps is not just a deployment tool but a cornerstone for **Security** and **Multi-Cluster Management**.

## 3.1 安全性架構：Pull vs. Push (Security Architecture: Pull vs. Push)

在傳統 Push 模型（如 Jenkins/GitLab CI）中，CI Server 必須持有 Kubernetes Cluster 的 `admin` 或 `deployer` 憑證（Kubeconfig）。這意味著 CI Server 成為了極高風險的攻擊目標。
In the traditional Push model (e.g., Jenkins/GitLab CI), the CI Server must hold the Kubernetes Cluster's `admin` or `deployer` credentials (Kubeconfig). This makes the CI Server a high-risk attack target.

**GitOps (Pull Model) 的優勢：**
**Advantages of GitOps (Pull Model):**

-   **Cluster Credentials stay inside**: ArgoCD/Flux 運行在叢集內部，不需要將憑證暴露給外部 CI 系統。
    **Cluster Credentials stay inside:** ArgoCD/Flux runs inside the cluster and does not need to expose credentials to external CI systems.
-   **Read-Only Access for CI**: CI 系統只需要有權限寫入 Git Repository（更新 Image Tag），而不需要觸碰 Production Cluster。
    **Read-Only Access for CI:** The CI system only needs permission to write to the Git Repository (to update Image Tags) and does not need to touch the Production Cluster.

## 3.2 可擴展性：多叢集管理 (Scalability: Multi-Cluster Management)

當公司擴展到數十個 K8s 叢集（Dev, Staging, Prod-US, Prod-EU, Prod-APAC）時，維護數百個 Jenkins Pipelines 是不可行的。
When a company scales to dozens of K8s clusters (Dev, Staging, Prod-US, Prod-EU, Prod-APAC), maintaining hundreds of Jenkins Pipelines is unfeasible.

**GitOps 解決方案：**
**GitOps Solution:**
使用如 ArgoCD ApplicationSets，你可以定義一個規則：「所有標記為 `env=prod` 的叢集，都必須同步 `git-repo/overlays/prod` 的配置」。新增一個叢集只需給它打上標籤，GitOps Controller 會自動將應用部署上去。
Using tools like ArgoCD ApplicationSets, you can define a rule: "All clusters labeled `env=prod` must sync with the configuration in `git-repo/overlays/prod`." Adding a new cluster simply involves tagging it, and the GitOps Controller automatically deploys the applications.

---

# 4. 逐步示例 (Walkthrough / Example)

## 案例背景 (Scenario)

我們有一個核心支付服務（Payment Service），目前使用標準的 Kubernetes `Deployment`。業務要求在發布新版本時，必須確保 HTTP 500 錯誤率低於 1%，否則自動回滾。
We have a core Payment Service currently using a standard Kubernetes `Deployment`. The business requirement is that when releasing a new version, the HTTP 500 error rate must remain below 1%; otherwise, it should automatically rollback.

## 解決方案：Argo Rollouts (Solution: Argo Rollouts)

標準的 K8s Deployment 物件只支援基本的 `RollingUpdate`，無法根據 Metrics 自動判斷是否該繼續部署。我們將引入 `Argo Rollouts` CRD。
The standard K8s Deployment object only supports basic `RollingUpdate` and cannot automatically decide whether to proceed based on metrics. We will introduce the `Argo Rollouts` CRD.

### Step 1: 定義 Rollout 物件 (Define Rollout Object)

將原本的 `Deployment` 替換為 `Rollout`。注意 `strategy` 部分。
Replace the original `Deployment` with `Rollout`. Note the `strategy` section.

```yaml
apiVersion: argoproj.io/v1alpha1
kind: Rollout
metadata:
  name: payment-service
spec:
  replicas: 10
  selector:
    matchLabels:
      app: payment
  template:
    metadata:
      labels:
        app: payment
    spec:
      containers:
      - name: payment
        image: payment:v1.0.0
        ports:
        - containerPort: 8080
  strategy:
    canary:
      # 定義分析模板 (Reference to AnalysisTemplate)
      analysis:
        templates:
        - templateName: success-rate-check
        startingStep: 2 # 從第2步開始進行分析 (Start analysis from step 2)
      steps:
      - setWeight: 20
      - pause: {duration: 1m} # 暫停1分鐘讓流量進入 (Pause 1m to let traffic in)
      - setWeight: 50
      - pause: {duration: 10s} # 這裡會持續執行 Analysis (Analysis runs continuously here)
      - setWeight: 100
```

### Step 2: 定義分析模板 (Define AnalysisTemplate)

這是 Argo Rollouts 的大腦，它告訴控制器如何查詢 Prometheus 來判斷版本好壞。
This is the brain of Argo Rollouts; it tells the controller how to query Prometheus to judge the version quality.

```yaml
apiVersion: argoproj.io/v1alpha1
kind: AnalysisTemplate
metadata:
  name: success-rate-check
spec:
  args:
  - name: service-name
  metrics:
  - name: success-rate
    interval: 1m
    successCondition: result[0] >= 0.99
    failureLimit: 3
    provider:
      prometheus:
        address: http://prometheus-server:9090
        query: |
          sum(rate(http_requests_total{app="{{args.service-name}}", status!~"5.*"}[1m])) / 
          sum(rate(http_requests_total{app="{{args.service-name}}"}[1m]))
```

### Step 3: 執行流程 (Execution Flow)

1.  **CI**: 建置 Docker Image `payment:v2.0.0`，並更新 Git Repo 中的 `image` tag。
    **CI:** Build Docker Image `payment:v2.0.0` and update the `image` tag in the Git Repo.
2.  **Sync**: ArgoCD 偵測到 Git 變更，同步 `Rollout` 物件。
    **Sync:** ArgoCD detects the Git change and syncs the `Rollout` object.
3.  **Canary Step 1**: 新版 Pod 啟動，接收 20% 流量。
    **Canary Step 1:** New version Pods start, receiving 20% of traffic.
4.  **Analysis**: `AnalysisTemplate` 每分鐘查詢 Prometheus。
    **Analysis:** `AnalysisTemplate` queries Prometheus every minute.
    *   **Case A (Success)**: 錯誤率低，成功率 >= 0.99。Rollout 繼續增加權重至 50%，最終至 100%。
        **Case A (Success):** Error rate is low, success rate >= 0.99. Rollout increases weight to 50%, eventually to 100%.
    *   **Case B (Failure)**: 錯誤率飆升。Analysis 失敗次數達到 `failureLimit`。Rollout 立即將權重切回 0% (v1)，並標記為 `Degraded`。
        **Case B (Failure):** Error rate spikes. Analysis failure count hits `failureLimit`. Rollout immediately cuts weight back to 0% (v1) and marks status as `Degraded`.

---

# 5. 常見錯誤與反模式 (Common Pitfalls & Anti-patterns)

## 5.1 CI/CD 職責混淆 (Mixing CI and CD Responsibilities)

-   **Anti-pattern**: 在 CI Pipeline (e.g., GitHub Actions) 中直接執行 `kubectl apply -f ...`。
    **Anti-pattern:** Directly executing `kubectl apply -f ...` inside the CI Pipeline (e.g., GitHub Actions).
-   **Why it's bad**: 這樣做無法感知叢集當前狀態，且需要將高權限憑證放入 CI。此外，如果部署失敗，CI logs 可能難以除錯，且無法自動確保狀態一致性。
    **Why it's bad:** This lacks awareness of the cluster's current state and requires placing high-privilege credentials in CI. Also, if deployment fails, CI logs can be hard to debug, and state consistency isn't automatically enforced.
-   **Better Approach**: CI 只負責 Build & Test & Push Image，最後一步是 `git commit` 更新 Manifest repo。讓 ArgoCD 負責 Apply。
    **Better Approach:** CI is only responsible for Build & Test & Push Image, with the final step being a `git commit` to update the Manifest repo. Let ArgoCD handle the Apply.

## 5.2 忽略資料庫遷移 (Ignoring Database Migrations)

-   **Anti-pattern**: 假設程式碼回滾（Rollback）時，資料庫也能自動回滾。
    **Anti-pattern:** Assuming that when code rolls back, the database automatically rolls back too.
-   **Why it's bad**: GitOps 可以輕易回滾 Deployment YAML，但無法回滾 DB Schema。如果 v2 的 migration 刪除了某個欄位，回滾到 v1 後，v1 程式碼會崩潰。
    **Why it's bad:** GitOps can easily rollback Deployment YAML, but not DB Schema. If v2 migration deleted a column, rolling back to v1 will cause v1 code to crash.
-   **Better Approach**: 遵循 **Expand and Contract** 模式。資料庫變更必須向後相容（Backward Compatible）。例如：先新增欄位（v2），等所有服務都升級後，再於下個版本（v3）刪除舊欄位。使用 Kubernetes Job 或 ArgoCD Hooks (`PreSync`) 來執行 Migration。
    **Better Approach:** Follow the **Expand and Contract** pattern. Database changes must be backward compatible. E.g., Add a column first (v2), and only after all services are upgraded, remove the old column in the next version (v3). Use Kubernetes Jobs or ArgoCD Hooks (`PreSync`) to run migrations.

## 5.3 在 Git 中儲存明文 Secrets (Storing Plaintext Secrets in Git)

-   **Anti-pattern**: 為了方便，將 Secret YAML 直接 commit 到 Git。
    **Anti-pattern:** Committing Secret YAML directly to Git for convenience.
-   **Better Approach**: 使用 **Sealed Secrets** (Bitnami) 或 **External Secrets Operator** (整合 AWS Secrets Manager / HashiCorp Vault)。Git 中只儲存加密後的字串或 Secret 的參照（Reference）。
    **Better Approach:** Use **Sealed Secrets** (Bitnami) or **External Secrets Operator** (integrating AWS Secrets Manager / HashiCorp Vault). Only store encrypted strings or references to Secrets in Git.

---

# 6. 面試與實務問答切入點 (Interview & Discussion Hooks)

## Q1: 如何處理 GitOps 中的緊急修復（Hotfix）？
**How do you handle Hotfixes in GitOps?**

-   **Key Points**:
    -   絕對不能直接 `kubectl edit` 修改線上環境（會被 GitOps 自動還原）。
        Never directly `kubectl edit` the production environment (GitOps will automatically revert it).
    -   必須走標準流程：開 PR 修改 Git Repo。
        Must follow the standard process: Open a PR to modify the Git Repo.
    -   如果緊急，可以使用 ArgoCD 的 UI 暫時停用 "Auto Sync"，手動修改參數止血，但必須隨後立即補上 Git Commit 以恢復同步。這被稱為 "Break Glass" procedure。
        If urgent, you can temporarily disable "Auto Sync" in ArgoCD UI, manually tweak parameters to stop the bleeding, but must immediately follow up with a Git Commit to restore sync. This is known as the "Break Glass" procedure.

## Q2: Canary Deployment 與 Blue/Green Deployment 如何選擇？
**How to choose between Canary and Blue/Green Deployment?**

-   **Key Points**:
    -   **Canary**: 適合對「錯誤容忍度稍高」且「需要真實流量驗證」的服務。資源消耗較少（只需額外起少量 Pods）。
        **Canary:** Suitable for services with "slightly higher error tolerance" that "need real traffic validation." Consumes fewer resources (only spins up a few extra Pods).
    -   **Blue/Green**: 適合「不允許任何錯誤請求」或「新舊版本無法共存（例如 DB 鎖定機制衝突）」的場景。缺點是資源消耗加倍（需兩倍 Pods）。
        **Blue/Green:** Suitable for scenarios "allowing zero error requests" or where "versions cannot coexist (e.g., DB locking conflicts)." Downside is double resource consumption (needs 2x Pods).

## Q3: 在微服務架構下，如何管理數百個服務的 GitOps 配置？
**In a microservices architecture, how do you manage GitOps configurations for hundreds of services?**

-   **Key Points**:
    -   **Monorepo vs Polyrepo**: 討論配置檔（Manifests）應該跟原始碼放在一起，還是集中在一個獨立的 Infra Repo。通常建議 **App Source Code** 與 **K8s Manifests** 分離，避免 CI loop 死循環。
        **Monorepo vs Polyrepo:** Discuss whether manifests should live with source code or in a separate Infra Repo. It is usually recommended to separate **App Source Code** from **K8s Manifests** to avoid CI loop cycles.
    -   **Templating**: 使用 Helm 或 Kustomize 來減少重複配置（DRY principle）。
        **Templating:** Use Helm or Kustomize to reduce configuration duplication (DRY principle).

---

# 7. 小結與後續延伸 (Summary & Next Steps)

## 本章重點 (Key Takeaways)

1.  **GitOps is the Source of Truth**: Git 是系統的唯一事實來源，Kubernetes 叢集只是 Git 狀態的投影。
    **GitOps is the Source of Truth:** Git is the single source of truth for the system; the Kubernetes cluster is just a projection of the Git state.
2.  **Pull over Push**: 使用叢集內部的 Controller (ArgoCD/Flux) 拉取配置，比外部 CI 推送更安全、更具可視性。
    **Pull over Push:** Using an in-cluster Controller (ArgoCD/Flux) to pull configurations is safer and more visible than external CI pushing.
3.  **Progressive Delivery**: 利用 Canary 或 Blue/Green 部署，配合 Metrics 自動分析，將部署風險降至最低。
    **Progressive Delivery:** Use Canary or Blue/Green deployments combined with automated metric analysis to minimize deployment risk.
4.  **Automated Rollback**: 不要依賴人工監控部署；讓系統根據錯誤率自動決定是否回滾。
    **Automated Rollback:** Do not rely on human monitoring for deployments; let the system automatically decide whether to rollback based on error rates.
5.  **Database Strategy**: 資料庫變更必須與程式碼部署解耦，並保持向後相容。
    **Database Strategy:** Database changes must be decoupled from code deployment and remain backward compatible.

## 下一步 (Next Steps)

-   **Service Mesh (Chapter 11)**: 雖然 Argo Rollouts 可以透過標準 Service 做簡單流量切換，但結合 Istio 或 Linkerd 可以實現更細緻的 Header-based routing（例如：只讓內部員工看到新版本）。
    **Service Mesh (Chapter 11):** While Argo Rollouts can do simple traffic shifting via standard Services, combining it with Istio or Linkerd allows for finer-grained Header-based routing (e.g., only letting internal employees see the new version).
-   **Observability Deep Dive**: 深入學習如何撰寫精確的 Prometheus Queries (PromQL) 來支援更複雜的 AnalysisTemplate。
    **Observability Deep Dive:** Dive deeper into writing precise Prometheus Queries (PromQL) to support more complex AnalysisTemplates.