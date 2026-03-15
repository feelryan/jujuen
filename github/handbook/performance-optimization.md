# 效能優化與資源限制管理 / Performance Optimization & Resource Management

## Mental model｜心智模型

在 GitHub 生態系中，效能優化不只是「讓 Git clone 快一點」，而是一個涉及 **數據傳輸 (Data Transfer)**、**計算資源 (Compute Resources)** 與 **API 消耗 (API Consumption)** 的多維度平衡遊戲。

要掌握此主題，請建立以下三個核心觀點：

1.  **Git 是圖形資料庫，不是檔案伺服器 (Git is a graph database, not a file server)**：
    *   每一次 `clone` 或 `fetch` 都是在遍歷 commit graph。效能問題通常源自於 graph 過於龐大（歷史過深）或 node 過重（二進位大檔）。
    *   **策略**：只獲取當下需要的數據（Shallow Clone, Sparse Checkout）。

2.  **CI/CD 是計費流水線 (CI/CD is a metered pipeline)**：
    *   GitHub Actions 的每一分鐘、每一個 Byte 的 Network Egress 都是成本（時間或金錢）。
    *   **策略**：以空間換取時間（Caching），以過濾換取準確度（Path Filtering）。

3.  **API 是有限資源 (API is a scarce resource)**：
    *   GitHub API 有嚴格的 Rate Limits。將其視為一個有「預算上限」的錢包，而非無限取用的水龍頭。
    *   **策略**：從「輪詢 (Polling)」轉向「事件驅動 (Event-driven/Webhooks)」，從 REST 轉向 GraphQL（精準獲取）。

---

## Patterns & best practices｜常見模式與最佳實務

### 1. 大型儲存庫優化 (Monorepo & Large Repo Strategies)

針對 Monorepo 或歷史悠久的專案，減少本地與 CI 環境的負載是首要任務。

*   **淺層複製 (Shallow Clones)**：
    *   在 CI/CD pipeline 中，絕大多數時候你不需要 5 年前的 commit 紀錄。
    *   使用 `fetch-depth: 1`。
    *   *注意*：若你的 pipeline 需要計算版本號（基於 git tag 距離）或分析變更（git diff），可能需要適度增加 depth 或 fetch 完整歷史。
*   **稀疏檢出 (Sparse Checkout)**：
    *   當 Repo 巨大（如 10GB+）但開發者只關注特定服務目錄時使用。
    *   **Command**: `git sparse-checkout set <dir1> <dir2>`
*   **Git LFS (Large File Storage)**：
    *   將 PSD, MP4, DLL 等二進位檔案移出 Git 核心歷史，改用指標（Pointer）儲存。
    *   **Pattern**: 配置 `.gitattributes` 鎖定特定副檔名，並開啟 File Locking 防止二進位檔合併衝突。

### 2. GitHub Actions 加速與快取 (Actions Acceleration & Caching)

*   **依賴快取 (Dependency Caching)**：
    *   不要每次都重新下載 `node_modules` 或 Maven packages。
    *   使用 `actions/setup-*` 內建的 cache 功能，或 `actions/cache`。
    *   **Key Key Design**: Cache Key 應包含 `os`, `lock-file hash`。
*   **路徑過濾 (Path Filtering)**：
    *   在 Monorepo 中，修改前端程式碼不應觸發後端服務的 Build。
    *   使用 `on.push.paths` 或 `paths-ignore` 來限制觸發條件。
*   **Docker Layer Caching**：
    *   若 Actions 涉及 `docker build`，利用 GitHub Actions Cache exporter (`gha`) 來重用 Docker layers，大幅減少 build time。

### 3. API Rate Limits 應對 (Handling API Constraints)

*   **使用 GraphQL API**：
    *   REST API 可能需要呼叫 5 次才能組出你要的資料（消耗 5 點 quota），GraphQL 可以在一次 Request 中精準拿取（消耗 1 點）。
*   **條件式請求 (Conditional Requests)**：
    *   使用 `If-None-Match` header (ETag)。若資源未變更，GitHub 回傳 `304 Not Modified`，這**不消耗** Rate Limit quota。
*   **使用 GitHub App Token**：
    *   GitHub App 的 Rate Limit 通常高於個人 PAT (Personal Access Token)，且是根據安裝數擴展 (scale with installations)。

---

## Anti-patterns & pitfalls｜反模式與踩雷點

### 1. 儲存庫膨脹 (Repository Bloat)
*   ❌ **Commit Build Artifacts**：將 `dist/`, `bin/`, `node_modules/` 直接 commit 進 repo。這會導致 repo 體積指數級增長且無法被 garbage collected。
*   ❌ **LFS 遷移不完全**：只在 `.gitattributes` 加入 LFS 規則，卻沒有使用 `git lfs migrate` 清洗歷史中的舊大檔。結果是 repo 體積 = 舊歷史大檔 + 新 LFS 物件（雙倍浪費）。

### 2. CI/CD 資源浪費 (CI Resource Waste)
*   ❌ **Cache Thrashing (快取抖動)**：Cache Key 設計不良（例如包含 timestamp），導致每次 run 都無法命中 cache，反而浪費時間在上傳/下載 cache。
*   ❌ **忽略 Timeout 設定**：Actions 預設 timeout 為 6 小時。若某個 job 卡死（例如等待 user input 或無窮迴圈），會燒掉大量分鐘數。應顯式設定 `timeout-minutes`。
*   ❌ **過度觸發 (Trigger Spam)**：Bot 自動 commit (如 formatting) 再次觸發 CI，造成無限迴圈。應在 commit message 加入 `[skip ci]` 或檢查 `github.actor`。

### 3. API 濫用 (API Abuse)
*   ❌ **高頻輪詢 (Polling)**：每分鐘打 API 檢查 PR 狀態。應改用 Webhook 監聽 `pull_request` 事件。
*   ❌ **同步處理大量數據**：在單一 workflow 中嘗試透過 API 遍歷所有 issues，容易觸發 `403 Forbidden` 或 `502 Bad Gateway`。應使用分頁 (Pagination) 並配合 `sleep` 或重試機制。

---

## Checklists & workflows｜檢查清單與流程

### Performance Health Check (Repo & CI)

- [ ] **Repo Size Analysis**: 執行 `git count-objects -vH` 檢查 `.git` 目錄大小。若超過 1GB，考慮清理歷史。
- [ ] **LFS Verification**: 檢查 `.gitattributes` 是否涵蓋所有常見二進位格式 (png, jpg, dll, so, exe)。
- [ ] **CI Fetch Depth**: 確認所有 CI workflows 的 `actions/checkout` 是否設定了 `fetch-depth: 1` (除非必要)。
- [ ] **Cache Configuration**: 檢查 `actions/cache` 的 Key 是否依賴於 `package-lock.json` 或 `go.sum` 等鎖定檔。
- [ ] **Concurrency Control**: 是否設定了 `concurrency` group，以確保同一 PR 的新 push 會自動取消舊的、正在跑的 build？
- [ ] **Timeout Safety**: 每個 Job 是否都設定了合理的 `timeout-minutes` (例如 10-30 分鐘)？

### Large Repo Migration Workflow (簡化版)

1.  **Analyze**: 使用 `git-sizer` 或 `gdu` 分析 repo 瓶頸。
2.  **Filter**: 使用 `git-filter-repo` (推薦) 或 BFG Repo-Cleaner 移除大檔或敏感資訊。
3.  **LFS Setup**: 初始化 Git LFS 並遷移現有大檔 (`git lfs migrate import --include="*.psd"`).
4.  **GC**: 執行 `git reflog expire --expire=now --all` 和 `git gc --prune=now --aggressive`。
5.  **Force Push**: 通知團隊成員重新 clone (這是破壞性變更)。

---

## Real-world examples｜實戰案例

### 1. GitHub Actions Caching for Node.js
最常見的 CI 優化，利用 hash 鎖定檔來管理快取。

```yaml
steps:
  - uses: actions/checkout@v4
  
  - name: Setup Node.js with cache
    uses: actions/setup-node@v4
    with:
      node-version: '20'
      # 自動處理 npm/yarn/pnpm 的 cache 儲存與恢復
      cache: 'npm' 
      
  - name: Install dependencies
    # 若 cache hit，npm ci 會極快完成
    run: npm ci
```

### 2. 防止 Monorepo 無效構建 (Path Filtering)
避免修改了文件 (`docs/`) 卻觸發後端 (`backend/`) 的測試。

```yaml
name: Backend CI
on:
  push:
    branches: [ "main" ]
    paths:
      - 'backend/**'
      - '.github/workflows/backend.yml'
    paths-ignore:
      - 'docs/**'
      - 'frontend/**'
      - '**/*.md'
```

### 3. 處理 API Rate Limit 的重試邏輯 (JavaScript/Octokit)
當你需要寫 script 自動化操作時，必須處理 `403` 和 `Retry-After`。

```javascript
const { Octokit } = require("@octokit/rest");
const { throttling } = require("@octokit/plugin-throttling");

const MyOctokit = Octokit.plugin(throttling);

const octokit = new MyOctokit({
  auth: process.env.GITHUB_TOKEN,
  throttle: {
    onRateLimit: (retryAfter, options, octokit) => {
      octokit.log.warn(`Request quota exhausted for request ${options.method} ${options.url}`);
      
      // 如果重試次數少於 3 次，自動等待後重試
      if (options.request.retryCount < 3) {
        octokit.log.info(`Retrying after ${retryAfter} seconds!`);
        return true;
      }
    },
    onSecondaryRateLimit: (retryAfter, options, octokit) => {
      // 處理 Abuse Rate Limit (短時間發送太多請求)
      octokit.log.warn(`SecondaryRateLimit detected for request ${options.method} ${options.url}`);
      return true;
    },
  },
});
```

### 4. 節省併發資源 (Concurrency Group)
在 PR 頻繁更新時，自動取消「過期」的 CI 執行，節省 Runner 時間。

```yaml
# 在 workflow 頂層配置
concurrency:
  # Group 名稱：如果是同一個 PR (github.ref)，則視為同一組
  group: ${{ github.workflow }}-${{ github.ref }}
  # 當新的 run 進來時，取消正在跑的舊 run
  cancel-in-progress: true
```