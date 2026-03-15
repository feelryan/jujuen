# Chapter 05: Scaling Git and Monorepo Management
# 第 05 章：大型儲存庫與 Monorepo 管理

## 1. Introduction & Learning Objectives
## 1. 前言與學習目標

As a Senior Engineer, you have likely encountered repositories that have become sluggish over time—`git status` takes seconds instead of milliseconds, or `git clone` consumes excessive bandwidth and disk space. In Big Tech environments, where Monorepos (like Google's or Meta's) are common, standard Git usage patterns break down. This chapter focuses on the advanced tooling and strategies required to maintain performance and manageability at scale.
身為資深工程師，您很可能遇過隨著時間推移而變得遲緩的儲存庫——`git status` 需要數秒而非毫秒，或者 `git clone` 消耗過多的頻寬與磁碟空間。在 Big Tech 環境中，Monorepo（如 Google 或 Meta 的單一儲存庫模式）相當普遍，標準的 Git 使用模式往往會失效。本章將聚焦於在大規模環境下，維持效能與可管理性所需的進階工具與策略。

By the end of this chapter, you will be able to:
完成本章後，您將能夠：

1.  **Evaluate and Implement Monorepo Strategies**: Decide when to use Submodules vs. Subtrees vs. a pure Monorepo, and understand the trade-offs.
    **評估與實作 Monorepo 策略**：決定何時使用 Submodules、Subtrees 或純粹的 Monorepo，並理解其中的權衡。
2.  **Optimize Large Repository Performance**: Utilize **Sparse Checkout** and **Partial Clone** to drastically reduce clone time and disk usage for developers.
    **最佳化大型儲存庫效能**：利用 **Sparse Checkout** 與 **Partial Clone** 大幅減少開發者的 clone 時間與磁碟佔用。
3.  **Manage Binary Assets Correctly**: Explain the internal mechanism of **Git LFS** and deploy it to prevent repository bloat.
    **正確管理二進位資產**：解釋 **Git LFS** 的內部機制並進行部署，以防止儲存庫膨脹。
4.  **Debug Complex Dependency Issues**: Resolve "Detached HEAD" states in Submodules and handle merge conflicts in Subtrees.
    **除錯複雜的依賴問題**：解決 Submodules 中的「Detached HEAD」狀態，並處理 Subtrees 中的合併衝突。

---

## 2. Core Concepts & Mental Model
## 2. 核心觀念與心智模型

### 2.1 The "Pointer" vs. "Embed" Model
### 2.1 「指標」與「嵌入」模型

To scale Git, we must stop thinking of a repository as a single, monolithic container of all files. Instead, think of it as a **graph of references**.
為了擴展 Git，我們必須停止將儲存庫視為包含所有檔案的單一巨型容器。相反地，應將其視為一個 **參照圖（graph of references）**。

*   **Git Submodules (The Pointer)**:
    Think of a Submodule as a **symlink to a specific commit hash** in another repository. It does not contain the code; it contains a reference.
    *   *Mental Model:* A bookmark in a book pointing to a specific page in another book.
    *   *Key Characteristic:* Strict version control. You are locked to a specific commit, not a moving branch.

*   **Git Submodules（指標）**：
    將 Submodule 想像成指向另一個儲存庫中 **特定 commit hash 的符號連結（symlink）**。它不包含程式碼，只包含參照。
    *   *心智模型*：書中的書籤，指向另一本書的特定頁面。
    *   *關鍵特性*：嚴格的版本控制。您被鎖定在特定的 commit，而不是變動的 branch。

*   **Git Subtree (The Embed)**:
    Think of a Subtree as **copy-pasting** another project's code into a folder of your project, but keeping the commit history intact.
    *   *Mental Model:* Merging two rivers into one. The history is blended.
    *   *Key Characteristic:* Ease of use for consumers (no extra setup commands), but harder to contribute back upstream.

*   **Git Subtree（嵌入）**：
    將 Subtree 想像成將另一個專案的程式碼 **複製貼上** 到您專案的資料夾中，但保留了 commit 歷史紀錄。
    *   *心智模型*：兩條河流匯聚成一條。歷史紀錄是混合的。
    *   *關鍵特性*：對使用者來說易於使用（無需額外的設定指令），但較難回饋程式碼到上游。

### 2.2 Git LFS (Large File Storage)
### 2.2 Git LFS（大型檔案儲存）

Standard Git stores every version of every file in the `.git/objects` database. This is disastrous for binaries (images, compiled libs).
標準 Git 會在 `.git/objects` 資料庫中儲存每個檔案的每個版本。這對於二進位檔案（圖片、編譯過的函式庫）來說是災難性的。

*   **Concept**: Git LFS replaces the large file in Git with a tiny **text pointer** (containing the SHA-256 and URL). The actual blob is stored in a separate object store (like S3).
*   **Download**: The blob is lazily downloaded only when `git checkout` needs that specific version of the file.

*   **觀念**：Git LFS 用一個微小的 **文字指標**（包含 SHA-256 與 URL）取代 Git 中的大型檔案。實際的 blob 儲存在分開的物件儲存區（如 S3）。
*   **下載**：只有當 `git checkout` 需要該檔案的特定版本時，才會延遲下載（lazy download）該 blob。

### 2.3 Partial Clone & Sparse Checkout
### 2.3 Partial Clone 與 Sparse Checkout

These are the modern solutions for Monorepos.
這是 Monorepo 的現代化解決方案。

*   **Partial Clone (Network/Storage Optimization)**: "Don't download the history of blobs I don't need." (e.g., `blobless` clones).
*   **Sparse Checkout (Working Directory Optimization)**: "I have the history, but only show me the `backend/service-A` folder in my file explorer."

*   **Partial Clone（網路/儲存最佳化）**：「不要下載我不需要的 blob 歷史紀錄。」（例如：`blobless` clones）。
*   **Sparse Checkout（工作目錄最佳化）**：「我有歷史紀錄，但在我的檔案總管中只顯示 `backend/service-A` 資料夾。」

---

## 3. Real-World & System Design View
## 3. 實務場景與系統設計視角

### 3.1 The Monorepo Architecture in Big Tech
### 3.1 Big Tech 中的 Monorepo 架構

In a System Design interview or a real-world architect role, the choice of repository structure impacts CI/CD pipelines, developer velocity, and dependency management.
在系統設計面試或實際架構師職位中，儲存庫結構的選擇會影響 CI/CD 流程、開發速度與依賴管理。

*   **Consistency vs. Decoupling**:
    *   **Monorepo**: Enforces "One Version of Truth". If you update a shared library, you must update all consumers immediately (Atomic Commits). This prevents "Dependency Hell" but requires sophisticated tooling (Bazel, Buck, Nx).
    *   **Polyrepo**: Decouples teams. Service A can use `Lib v1.0` while Service B uses `Lib v2.0`. However, cross-service refactoring is painful.

*   **一致性 vs. 解耦**：
    *   **Monorepo**：強制執行「單一真理版本（One Version of Truth）」。如果您更新了共用函式庫，必須立即更新所有使用者（原子性提交）。這防止了「依賴地獄」，但需要複雜的工具支援（Bazel, Buck, Nx）。
    *   **Polyrepo**：解耦團隊。Service A 可以使用 `Lib v1.0`，而 Service B 使用 `Lib v2.0`。然而，跨服務重構會非常痛苦。

### 3.2 CI/CD Performance Implications
### 3.2 CI/CD 效能影響

When designing a CI pipeline for a 50GB repo:
當為一個 50GB 的儲存庫設計 CI pipeline 時：

1.  **Shallow Clones are not enough**: `git clone --depth 1` is standard, but if the repo has 1 million files, the checkout phase is still slow.
2.  **Solution**: Use **Sparse Checkout** in CI jobs. If a job only tests the "Billing Service", the agent should only materialize the files related to Billing.
3.  **Caching**: Git LFS objects should be heavily cached in the CI infrastructure to avoid egress costs and latency.

1.  **Shallow Clones 是不夠的**：`git clone --depth 1` 是標準做法，但如果儲存庫有 100 萬個檔案，checkout 階段仍然很慢。
2.  **解決方案**：在 CI job 中使用 **Sparse Checkout**。如果一個 job 只測試「計費服務」，Agent 應該只實體化與計費相關的檔案。
3.  **快取**：Git LFS 物件應在 CI 基礎設施中被大量快取，以避免流量成本與延遲。

---

## 4. Walkthrough / Example
## 4. 逐步示例

### Scenario: Optimizing a Growing Monorepo
### 情境：最佳化一個成長中的 Monorepo

**Context**: Your team maintains a backend Monorepo containing 50 microservices. The `.git` folder is 5GB. Developers complain that `git clone` takes 20 minutes, and their laptops run out of space.
**背景**：您的團隊維護一個包含 50 個微服務的後端 Monorepo。`.git` 資料夾高達 5GB。開發者抱怨 `git clone` 需要 20 分鐘，且筆電空間不足。

#### Step 1: Analyze the Bloat (Naive Approach)
#### 步驟 1：分析膨脹（直覺做法）

You might try to delete large files from `HEAD`, but they remain in history.
您可能會嘗試從 `HEAD` 刪除大型檔案，但它們仍保留在歷史紀錄中。

```bash
# Check the size of the packfile
git count-objects -vH
```

#### Step 2: Implement Partial Clone (The Modern Solution)
#### 步驟 2：實作 Partial Clone（現代化解法）

Instead of a full clone, we use a "blobless" clone. This downloads all commits and trees (so `git log` works fast) but downloads file contents (blobs) only on demand.
我們不使用完整 clone，而是使用「blobless」clone。這會下載所有 commits 和 trees（所以 `git log` 運作很快），但只在需要時才下載檔案內容（blobs）。

```bash
# Clone with a filter to exclude blobs (file contents) initially
# 初始 clone 時設定過濾器以排除 blobs（檔案內容）
git clone --filter=blob:none <repo-url>

# Result: Clone size drops from 5GB to ~200MB (metadata only).
# 結果：Clone 大小從 5GB 降至約 200MB（僅含中繼資料）。
```

#### Step 3: Configure Sparse Checkout
#### 步驟 3：設定 Sparse Checkout

A developer only working on `service-payment` doesn't need the files for `service-inventory`.
一位只負責 `service-payment` 的開發者不需要 `service-inventory` 的檔案。

```bash
cd my-monorepo

# Initialize sparse-checkout (Git 2.25+)
# 初始化 sparse-checkout (Git 2.25+)
git sparse-checkout init --cone

# Set the directories you actually want to see
# 設定您實際想要看到的目錄
git sparse-checkout set service-payment shared-libs

# Now, your working directory only contains root files, service-payment/, and shared-libs/.
# 現在，您的工作目錄只包含根目錄檔案、service-payment/ 與 shared-libs/。
```

*Note on `cone` mode*: Always use `--cone` mode for performance. It restricts patterns to directories rather than complex regex, making git significantly faster.
*關於 `cone` 模式的註記*：為了效能，請務必使用 `--cone` 模式。它將模式限制為目錄而非複雜的正則表達式，這讓 git 速度顯著提升。

#### Step 4: Handling Binary Assets with LFS
#### 步驟 4：使用 LFS 處理二進位資產

If the repo contains design assets or ML models:
如果儲存庫包含設計資產或機器學習模型：

```bash
# Install LFS hooks
git lfs install

# Track large files
git lfs track "*.psd"
git lfs track "models/*.bin"

# This creates/updates .gitattributes. Commit this file!
# 這會建立/更新 .gitattributes。請提交此檔案！
git add .gitattributes
```

---

## 5. Common Pitfalls & Anti-patterns
## 5. 常見錯誤與反模式

### 5.1 The "Submodule Detached HEAD" Trap
### 5.1 「Submodule Detached HEAD」陷阱

*   **Anti-pattern**: A developer enters a submodule directory, makes changes, commits, and pushes the main repo, but forgets to push the submodule or is not on a branch.
*   **Why it's bad**: The main repo points to a commit hash that exists only on the developer's local machine. CI/CD will fail with "reference not found".
*   **Solution**: Always ensure submodules are on a branch before committing.
    ```bash
    git submodule foreach 'git checkout main || :'
    ```

*   **反模式**：開發者進入 submodule 目錄，進行修改、提交，並推送主儲存庫，但忘記推送 submodule 或未處於 branch 上。
*   **為何不好**：主儲存庫指向了一個僅存在於該開發者本機的 commit hash。CI/CD 會因「reference not found」而失敗。
*   **解決方案**：提交前務必確認 submodules 處於 branch 上。

### 5.2 Committing Build Artifacts
### 5.2 提交建置產物

*   **Anti-pattern**: Committing `dist/`, `bin/`, or `node_modules/` to the repo.
*   **Why it's bad**: Causes massive repository bloat and merge conflicts. Git is for source code, not artifacts.
*   **Solution**: Strict `.gitignore` and use Artifactory/S3/Docker Registry for binaries.

*   **反模式**：將 `dist/`、`bin/` 或 `node_modules/` 提交到儲存庫。
*   **為何不好**：導致儲存庫巨大膨脹與合併衝突。Git 是用來放原始碼的，不是放產物的。
*   **解決方案**：嚴格的 `.gitignore`，並使用 Artifactory/S3/Docker Registry 存放二進位檔。

### 5.3 Overusing Submodules for Code Sharing
### 5.3 過度使用 Submodules 共享程式碼

*   **Anti-pattern**: Using submodules for every shared library in a tightly coupled system.
*   **Why it's bad**: Updating a core library requires a "ripple effect" of commits across 10 different repos.
*   **Solution**: For tightly coupled code, a Monorepo (folder separation) is often better than Submodules. Use Submodules for truly independent, third-party dependencies.

*   **反模式**：在緊密耦合的系統中，為每個共用函式庫使用 submodules。
*   **為何不好**：更新核心函式庫需要在 10 個不同的儲存庫中進行「連鎖反應」式的提交。
*   **解決方案**：對於緊密耦合的程式碼，Monorepo（資料夾分隔）通常優於 Submodules。將 Submodules 用於真正獨立的第三方依賴。

---

## 6. Interview & Discussion Hooks
## 6. 面試與實務問答切入點

### Q1: How would you architect the repository strategy for a new startup aiming for rapid growth vs. a mature enterprise migrating to microservices?
### Q1: 你會如何為一家追求快速成長的新創公司，與一家正在遷移至微服務的成熟企業，設計不同的儲存庫策略？

*   **Key Points**:
    *   **Startup**: Start with a Monorepo. It reduces overhead (one CI pipeline, easy code sharing). Don't over-engineer with submodules yet.
    *   **Enterprise**: If migrating, a Monorepo is still ideal (Google style), but requires heavy tooling investment (Bazel). If tooling teams are scarce, Polyrepo (one repo per service) might be safer pragmatically, despite the dependency management pain.
*   **關鍵要點**：
    *   **新創**：從 Monorepo 開始。它減少了開銷（單一 CI pipeline，易於程式碼共享）。暫時不要過度設計使用 submodules。
    *   **企業**：若正在遷移，Monorepo 仍是理想選擇（Google 風格），但需要大量的工具投資（Bazel）。如果缺乏工具團隊，Polyrepo（每個服務一個儲存庫）在實務上可能較安全，儘管會有依賴管理的痛苦。

### Q2: Explain the difference between Git Submodules and Git Subtrees. When would you use one over the other?
### Q2: 請解釋 Git Submodules 與 Git Subtrees 的差異。你會在何時選擇其中之一？

*   **Key Points**:
    *   **Submodule**: Reference based. Best for strictly versioned external dependencies (e.g., a specific version of `openssl`). Requires user to run `git submodule update`.
    *   **Subtree**: Code copy based. Best for shared code you want to modify easily alongside your project. Easier for consumers, harder for upstream contribution.
*   **關鍵要點**：
    *   **Submodule**：基於參照。最適合嚴格版本控制的外部依賴（例如：`openssl` 的特定版本）。需要使用者執行 `git submodule update`。
    *   **Subtree**：基於程式碼複製。最適合您希望隨專案一起輕鬆修改的共用程式碼。對使用者較簡單，但對上游貢獻較難。

### Q3: We have a 10GB Monorepo. Developers are complaining. What is your step-by-step plan to fix this?
### Q3: 我們有一個 10GB 的 Monorepo。開發者正在抱怨。你的逐步修復計畫是什麼？

*   **Key Points**:
    1.  **Audit**: Use `git-sizer` or `git count-objects` to find the culprit (large binaries?).
    2.  **Migrate Binaries**: Move large assets to Git LFS using `BFG Repo-Cleaner` or `git filter-repo`.
    3.  **Workflow**: Enforce `git clone --filter=blob:none` (Partial Clone) and `git sparse-checkout` for developers.
    4.  **CI**: Optimize CI to only checkout relevant paths.
*   **關鍵要點**：
    1.  **稽核**：使用 `git-sizer` 或 `git count-objects` 找出罪魁禍首（大型二進位檔？）。
    2.  **遷移二進位檔**：使用 `BFG Repo-Cleaner` 或 `git filter-repo` 將大型資產移至 Git LFS。
    3.  **工作流程**：強制開發者使用 `git clone --filter=blob:none` (Partial Clone) 與 `git sparse-checkout`。
    4.  **CI**：最佳化 CI 以僅 checkout 相關路徑。

---

## 7. Summary & Next Steps
## 7. 小結與後續延伸

### Summary
### 小結

1.  **Monorepo vs. Polyrepo** is a trade-off between consistency/tooling cost and decoupling/dependency hell.
    **Monorepo vs. Polyrepo** 是在「一致性/工具成本」與「解耦/依賴地獄」之間的權衡。
2.  **Git Submodules** are pointers to commits; useful for strict dependencies but have poor UX.
    **Git Submodules** 是指向 commits 的指標；對嚴格依賴有用，但使用者體驗（UX）較差。
3.  **Git LFS** is mandatory for storing binary assets in Git to prevent repo bloat.
    **Git LFS** 是在 Git 中儲存二進位資產的必要手段，以防止儲存庫膨脹。
4.  **Partial Clone (`--filter=blob:none`)** and **Sparse Checkout** are the modern standard for handling large repositories without splitting them.
    **Partial Clone (`--filter=blob:none`)** 與 **Sparse Checkout** 是現代處理大型儲存庫而不需拆分它們的標準做法。

### Next Steps
### 後續延伸

*   **Practice**: Try converting a folder in your personal project into a Submodule, then convert it back using Subtree to feel the difference.
    **實作**：嘗試將個人專案中的一個資料夾轉換為 Submodule，然後再用 Subtree 轉回來，感受兩者的差異。
*   **Read**: Explore **"VFS for Git" (Scalar)**, the technology Microsoft developed to handle the Windows OS repository (300GB+), which inspired modern Partial Clone features.
    **閱讀**：探索 **"VFS for Git" (Scalar)**，這是微軟為了處理 Windows 作業系統儲存庫（300GB+）所開發的技術，它啟發了現代的 Partial Clone 功能。
*   **Next Chapter**: Proceed to **CI/CD Integration & Git Hooks**, where we automate the checks discussed here.
    **下一章**：前往 **CI/CD 整合與 Git Hooks**，我們將自動化這裡討論到的檢查流程。