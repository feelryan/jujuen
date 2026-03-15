# Kubernetes 整合與 GitOps 實踐 / Kubernetes Integration and GitOps Practices

## Mental model｜心智模型

在將 GitLab 與 Kubernetes 整合時，工程師往往會陷入「如何把 `kubectl` 指令塞進 `.gitlab-ci.yml`」的思維陷阱。要掌握 GitOps，你需要轉變心智模型：從 **「命令式 (Imperative)」** 轉向 **「聲明式 (Declarative)」**。

### 1. Source of Truth vs. Reality
- **Git Repository (Source of Truth):** 這是世界的「應然」狀態。所有的 Kubernetes Manifests (YAMLs)、Helm Charts 都在這裡。如果 Git 裡沒有，它就不該存在於叢集中。
- **Kubernetes Cluster (Reality):** 這是世界的「實然」狀態。
- **GitOps Agent (The Reconciler):** 無論是 GitLab Agent for Kubernetes、ArgoCD 或 Flux，它們的角色是「自動調溫器」。它們不斷觀察 Git (設定溫度) 與 Cluster (室溫) 的差異，並自動進行調節。

### 2. Push vs. Pull Architecture
- **Push-based (CIOps):** 傳統做法。CI Pipeline 負責編譯程式碼，**並且** 負責連線到 K8s 執行部署 (`kubectl apply`)。這就像是你親自去開關冷氣。
  - *風險：* CI 需要擁有 Cluster 的高權限憑證 (God mode risk)。
- **Pull-based (GitOps):** 現代做法。CI Pipeline 只負責產出 Artifact (Docker Image) 並更新 Git 設定檔。Cluster 內部的 Agent 主動拉取 (Pull) 變更並應用。這就像設定好恆溫器，讓系統自己運作。
  - *優勢：* Cluster 不需要對外暴露 API，且 CI 不需要 Cluster 的寫入憑證。

---

## Patterns & best practices｜常見模式與最佳實務

### 1. The Repository Split Pattern (程式碼與設定檔分離)
不要將 Application Code 和 Kubernetes Manifests 放在同一個 Repo（除非是極簡單的微服務）。
- **App Repo:** 包含原始碼、Dockerfile、CI 流程。CI 結束後，觸發 Config Repo 的更新。
- **Config Repo (Manifest Repo):** 包含 Helm Charts、Kustomize 檔案。這是 GitOps Agent 監聽的對象。
- **Why:** 這樣可以避免無限迴圈 (CI 修改 YAML -> 觸發 CI -> 修改 YAML...)，並且讓權限控管更清晰（開發者可以改 Code，但 SRE 才能 Merge Config Repo 的 Prod 分支）。

### 2. GitLab Agent for Kubernetes: CI Tunnel (Hybrid Mode)
如果你還沒準備好全面導入 ArgoCD，GitLab Agent 提供的 **CI Tunnel** 是一個極佳的過渡方案。
- **做法：** 在 Cluster 安裝 GitLab Agent，但在 `.gitlab-ci.yml` 中使用 `kubectl`。
- **關鍵差異：** 你不需要將 `KUBECONFIG` 或 Token 存入 CI Variables。CI Job 會透過 Agent 建立的安全通道與 Cluster 通訊。
- **適用場景：** 快速遷移舊專案、執行一次性的 Job (如 Database Migration)、Review Apps 的動態建立。

### 3. Image Tag Immutability (映像檔標籤不可變性)
在 GitOps 流程中，**絕對不要使用 `latest` 標籤**。
- **Pattern:** 每次 CI 建置都產生唯一的 Tag (如 `git commit sha` 或 `semantic version`)。
- **Flow:** CI Build -> Push Image `v1.0.1` -> Update Config Repo (`image: myapp:v1.0.1`) -> GitOps Sync.
- **Why:** 確保可追溯性與回滾能力。如果用 `latest`，K8s 可能因為 ImagePullPolicy 設定而不更新，或者回滾時拉到錯誤的版本。

### 4. Secret Management Integration
GitOps 的最大挑戰是「Secret 不能進 Git」。
- **Sealed Secrets / SOPS:** 將加密過的 Secret 存入 Git，Cluster 內部的 Controller 負責解密。
- **External Secrets Operator (ESO):** 推薦做法。Git 裡只存 Reference (如指向 AWS Secrets Manager 或 HashiCorp Vault 的 key)，ESO 負責在 Cluster 內同步真實的 Secret。

---

## Anti-patterns & pitfalls｜反模式與踩雷點

### 1. The "KUBECONFIG in CI Variable" Trap (憑證裸奔)
- **反模式：** 將 `~/.kube/config` 的內容 Base64 編碼後塞入 GitLab CI/CD Variables。
- **後果：** 這是資安惡夢。一旦 CI Variable 洩漏，攻擊者擁有 Cluster 完整控制權。且憑證輪替 (Rotation) 極其困難。
- **修正：** 使用 GitLab Agent for Kubernetes (CI Tunnel) 或 OIDC 整合。

### 2. Manual `kubectl edit` (手動修改)
- **反模式：** 線上出問題時，直接用 `kubectl edit deployment` 修改設定。
- **後果：** GitOps Agent 會在下一次 Sync 時把你的修改覆蓋掉（因為 Git 才是 Source of Truth）。或者造成 "Configuration Drift"，導致 Git 狀態與線上不一致，下次部署時引發預期外的錯誤。

### 3. Mixing Build and Deploy Logic tightly
- **反模式：** 一個巨大的 `.gitlab-ci.yml` 同時做 Build, Test, Security Scan, 和 Deploy to Prod。
- **後果：** 部署變成「全有或全無」。如果只想重新部署舊版本 (Rollback)，卻被迫重新 Build 一次 Image。
- **修正：** Build 產出 Artifacts；Deploy 只是「選擇某個 Artifact 版本並更新 Manifest」。

### 4. Ignoring Resource Limits
- **反模式：** 在 Manifest 中未定義 `resources.requests` 和 `limits`。
- **後果：** 這是導致 Kubernetes 節點崩潰或 Pod 被 OOMKilled 的主因。GitOps 自動化部署會讓不良設定擴散得更快。

---

## Checklists & workflows｜檢查清單與流程

### Decision Workflow: Push vs. Pull?
- [ ] **團隊規模小 (< 5 人) 且專案單純？** -> 使用 **Push-based** (GitLab Agent CI Tunnel)。設定最快，學習曲線低。
- [ ] **需要高度合規、稽核與多叢集管理？** -> 使用 **Pull-based** (ArgoCD / Flux)。
- [ ] **需要動態環境 (Review Apps)？** -> 混合模式。Review Apps 使用 Push (CI Tunnel) 建立，Staging/Prod 使用 Pull (GitOps) 管理。

### GitOps Implementation Checklist
在將專案導入 Kubernetes GitOps 前，請確認：

- [ ] **Connectivity:** GitLab Agent 已安裝在 Cluster 中，且連線狀態為 `Connected`。
- [ ] **RBAC:** Agent 的 ServiceAccount 權限已最小化（僅限於特定 Namespace）。
- [ ] **Secrets:** 已經決定 Secret 管理策略 (SealedSecrets / External Secrets)，確認沒有明文密碼在 Git 中。
- [ ] **Manifests:** 所有的 K8s YAML 檔案都已參數化 (Helm/Kustomize)，並從 App Code 中分離（或妥善分層）。
- [ ] **CI Pipeline:** CI 流程已移除 `docker login` / `kubectl apply` 等依賴外部憑證的步驟（改用 Agent Context）。
- [ ] **Drift Detection:** 如果使用 ArgoCD/Flux，是否已開啟 Prune (自動刪除 Git 中不存在的資源)？

---

## Real-world examples｜實戰案例

### Example 1: Push-based Deployment via GitLab Agent (CI Tunnel)
這是最容易上手的模式，適合從傳統 VM 部署遷移到 K8s 的團隊。不需要額外的 ArgoCD，直接利用 GitLab CI。

**.gitlab/agents/my-agent/config.yaml** (Agent 設定)
```yaml
ci_access:
  projects:
    - id: my-group/my-project
```

**.gitlab-ci.yml** (CI 流程)
```yaml
deploy:
  stage: deploy
  image:
    name: bitnami/kubectl:latest
    entrypoint: [""]
  script:
    # 使用 Agent Context，無需手動設定 KUBECONFIG
    - kubectl config use-context my-group/my-project:my-agent
    # 更新 Image Tag
    - kubectl set image deployment/my-app my-app-container=registry.example.com/my-app:$CI_COMMIT_SHORT_SHA
    # 或者應用新的設定
    - kubectl apply -f k8s/
  environment:
    name: production
```

### Example 2: Pull-based GitOps Workflow (The "Enterprise" Way)
適合大型團隊，實現真正的 GitOps。

**架構流：**
1. **Dev:** Push code to `App Repo`.
2. **CI:** Build Docker Image -> Push to Registry -> **Trigger Downstream Pipeline** in `Config Repo`.
3. **CD (Config Repo):** 接收變數 (Image Tag)，使用 `yq` 或 `sed` 修改 `values.yaml` 中的 image tag，並 Commit & Push。
4. **K8s Cluster (ArgoCD/GitLab Agent):** 偵測到 `Config Repo` 變更，自動拉取並 Apply 到 Cluster。

**Config Repo Update Script (Pseudo-code):**
```bash
# 在 CI 中執行，用於更新 Config Repo
git clone https://gitlab.com/my-group/config-repo.git
cd config-repo
# 更新 Helm Values 中的 Image Tag
yq e -i ".image.tag = \"$NEW_TAG\"" values-prod.yaml
git commit -am "Bump image tag to $NEW_TAG"
git push origin main
# 任務結束，剩下的交給 Cluster 內的 Agent
```