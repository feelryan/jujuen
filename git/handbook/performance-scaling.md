# 大型儲存庫與 LFS 效能優化 / Scaling Git: Large Repositories and LFS

當專案成長為 Monorepo，或是涉及遊戲開發、機器學習模型等需要儲存大型二進位檔案（Binary Files）的情境時，標準的 Git 操作會變得極其緩慢。本章節專注於解決 `.git` 資料夾膨脹與操作延遲的問題。

## Mental model｜心智模型

要優化 Git 效能，必須先理解 Git 在處理「大型檔案」與「大量檔案」時的瓶頸所在。

### 1. 指標與實體分離 (Pointer vs. Blob)
在標準 Git 中，每個版本的檔案都是一個完整的 Blob。如果你修改了一個 100MB 的 PSD 檔，Git 儲存庫就會增加 100MB。
**Git LFS (Large File Storage)** 的核心概念是「**圖書館目錄卡**」。
- **Standard Git**: 把整座圖書館的書都背在背包裡。
- **Git LFS**: 背包裡只放目錄卡（Pointer file，約 1KB）。當你真的要「閱讀」（Checkout）某本書時，Git 才會根據目錄卡去伺服器下載真正的內容。

### 2. 視野與下載範圍 (Scope & Reachability)
針對 Monorepo（單一儲存庫包含多個專案），效能瓶頸在於「檔案數量（Index size）」與「歷史深度」。
- **Sparse Checkout (稀疏檢出)**：戴上「隧道視力眼鏡」。你的硬碟上只會有你關心的資料夾（例如 `/frontend`），Git 會忽略其他部分，大幅減少 `git status` 的掃描時間。
- **Partial Clone (部分複製)**：類似串流影片。你不需要下載整部電影（完整的歷史物件）才能開始看。你可以只下載 Commit metadata，當需要查看某個檔案內容時，Git 會自動按需下載（On-demand）。

---

## Patterns & best practices｜常見模式與最佳實務

### 1. Git LFS 的正確使用姿勢
適用於：遊戲資產、設計檔、ML 模型、編譯後的二進位檔。

- **及早啟用 (Enable Early)**：在專案第一天就設定 LFS。事後遷移（Migrate）需要重寫歷史（Rewrite History），風險極高且痛苦。
- **鎖定二進位檔案 (File Locking)**：二進位檔案無法進行文字合併（Merge）。啟用 LFS 的 File Locking 功能，當一人編輯時，其他人無法 Push 修改，避免覆蓋衝突。
  ```bash
  # 設定追蹤
  git lfs track "*.psd"
  # 確保 .gitattributes 被提交
  git add .gitattributes
  ```

### 2. 現代化 Clone 策略：Partial Clone + Sparse Checkout
適用於：大型 Monorepo 開發者。

不要再用 `git clone --depth 1` (Shallow Clone) 進行日常開發，它會破壞 Merge Base，導致 Push/Merge 困難。請改用 **Blobless Clone**。

- **Blobless Clone (推薦)**：下載所有 Commits 和 Trees，但不下載 Blobs（檔案內容）。檔案內容會在 Checkout 時下載。
  ```bash
  # 這是目前平衡速度與開發體驗的最佳解
  git clone --filter=blob:none <repo-url>
  ```
- **Treeless Clone**：連目錄結構都不下載。只適用於 CI/CD 或極少需要讀取歷史的情境。
  ```bash
  git clone --filter=tree:0 <repo-url>
  ```

### 3. 啟用 Git Maintenance
Git 內建了背景優化任務，可以自動壓縮 Packfiles 和更新 Commit Graph。

- **Pattern**: 在開發機上對大型專案啟用維護模式。
  ```bash
  git maintenance start
  ```

---

## Anti-patterns & pitfalls｜反模式與踩雷點

### 1. 將 `node_modules` 或 Build Artifacts 放入 Git
- **Anti-pattern**: 為了部署方便，將 `dist/` 或 `vendor/` 資料夾 commit 進去。
- **Consequence**: 儲存庫急速膨脹，且這些檔案變更頻率高，LFS 也救不了這種碎片化的變更。
- **Solution**: 使用 Artifact Repository (如 Nexus, Artifactory) 或 Docker Registry，永遠不要把 Git 當作備份硬碟。

### 2. LFS 遷移時的「幽靈物件」
- **Pitfall**: 使用 `git lfs migrate` 後，以為檔案變小了，但 `.git` 資料夾依然巨大。
- **Reason**: 舊的 commit 依然參照著舊的大型物件，且這些物件還在 reflog 中。
- **Solution**: 必須徹底清理 Reflog 並執行 GC (Garbage Collection)，或者通知團隊重新 Clone。

### 3. 濫用 Sparse Checkout 卻不優化 Index
- **Pitfall**: 只做了 Sparse Checkout，但沒有啟用 `sparse-index` (Git 2.25+)。
- **Consequence**: 雖然硬碟檔案變少了，但 Git 內部的 Index 結構依然包含所有檔案，`git status` 依然慢。
- **Solution**: 確保啟用 `git config core.sparseCheckoutCone true`。

---

## Checklists & workflows｜檢查清單與流程

### Workflow: Setting up a Huge Repo for Dev (新進員工設定流程)

當你加入一個 10GB+ 的 Monorepo 團隊時，請依此流程操作：

1.  **Blobless Clone (避免下載所有歷史檔案內容)**
    ```bash
    git clone --filter=blob:none <repo_url>
    cd <repo_name>
    ```
2.  **Initialize Sparse Checkout (只關注你的專案)**
    ```bash
    git sparse-checkout init --cone
    git sparse-checkout set apps/my-service libs/shared
    ```
3.  **Verify LFS (確保 LFS 指標正確解析)**
    ```bash
    git lfs install
    git lfs pull
    ```
4.  **Enable Maintenance (開啟背景優化)**
    ```bash
    git maintenance start
    ```

### Checklist: Before Committing Large Files (提交前檢查)

- [ ] **檔案類型檢查**：這是原始碼嗎？還是二進位檔（圖片、影片、Zip）？
- [ ] **LFS Tracking**：如果是二進位檔，執行 `git lfs track "*.ext"` 了嗎？
- [ ] **.gitattributes**：檢查 `.gitattributes` 是否有被 staged？
- [ ] **Size Check**：檔案是否超過 100MB？（GitHub 等平台會直接拒絕非 LFS 的大檔 Push）。

---

## Real-world examples｜實戰案例

### Scenario 1: The Game Studio (LFS & Locking)
**情境**：一個 Unity 遊戲專案，包含大量 `.png` 貼圖與 `.fbx` 模型。美術人員與程式設計師協作。

**問題**：美術 A 修改了 `hero.fbx`，美術 B 同時也修改了 `hero.fbx`。Git 視為二進位衝突，無法合併，導致一人工作白費。

**解決方案**：
1.  設定 LFS 追蹤所有資產：`git lfs track "*.fbx"`。
2.  設定 `.gitattributes` 加入鎖定屬性：
    ```text
    *.fbx filter=lfs diff=lfs merge=lfs -text lockable
    ```
3.  **工作流**：美術 A 在編輯前執行 `git lfs lock Assets/hero.fbx`。美術 B 嘗試 push 時會被拒絕，直到 A 解鎖。

### Scenario 2: The Enterprise Monorepo (Partial Clone)
**情境**：公司將 Backend (Go), Frontend (React), Mobile (iOS) 全部放在同一個 Repo。歷史紀錄長達 10 年，`.git` 大小超過 5GB。

**問題**：前端工程師只想改一個按鈕顏色，卻要花 30 分鐘 `git clone`，且硬碟空間不足。

**解決方案**：
採用 **Blobless Clone + Sparse Checkout**。
```bash
# 1. 快速 Clone (只下載 Commit Graph，不下載檔案內容)
git clone --filter=blob:none git@github.com:company/monorepo.git

# 2. 進入目錄
cd monorepo

# 3. 設定只看前端目錄 (此時 Git 會去下載這兩個目錄所需的 Blob)
git sparse-checkout set packages/frontend packages/ui-kit

# 結果：Clone 時間縮短至 2 分鐘，硬碟佔用僅需數百 MB。
```