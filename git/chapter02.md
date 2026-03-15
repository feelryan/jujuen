# Chapter 02: Advanced History Rewriting and Recovery
# 第 02 章：進階歷史重寫與災難救援

## 1. Introduction & Learning Objectives
## 1. 前言與學習目標

As a Senior Software Engineer, your interaction with Git shifts from merely "saving code" to "crafting a narrative." A clean commit history is not just about aesthetics; it is a critical component of maintainable software, enabling effective code reviews and easier debugging via `git bisect`. Furthermore, the ability to recover from "catastrophic" errors distinguishes a senior engineer from a junior one.
作為資深軟體工程師，你與 Git 的互動應從單純的「儲存程式碼」轉變為「編撰開發敘事」。整潔的提交歷史不僅是為了美觀，更是軟體可維護性的關鍵組成部分，它能提升 Code Review 的效率，並讓透過 `git bisect` 進行除錯變得更容易。此外，能否從「災難性」錯誤中救援資料，是區分資深與初階工程師的重要指標。

By the end of this chapter, you will be able to:
完成本章後，你將能夠：

1.  **Master Interactive Rebase**: Confidently use `rebase -i` to squash, reword, split, and reorder commits to tell a clear story before merging.
    **精通互動式 Rebase**：自信地使用 `rebase -i` 來壓縮（Squash）、重寫（Reword）、拆分（Split）與重新排序提交，在合併前整理出清晰的開發脈絡。
2.  **Internalize Reset Modes**: Clearly explain and utilize the differences between `--soft`, `--mixed`, and `--hard` resets, specifically regarding how they manipulate the HEAD, Index (Staging Area), and Working Directory.
    **內化 Reset 模式**：清楚解釋並運用 `--soft`、`--mixed` 與 `--hard` 之間的差異，特別是它們如何操作 HEAD、索引（暫存區）與工作目錄。
3.  **Perform Data Recovery**: Utilize `git reflog` to restore "lost" commits or branches, understanding that almost nothing in Git is truly deleted immediately.
    **執行資料救援**：利用 `git reflog` 恢復「遺失」的提交或分支，並理解在 Git 中幾乎沒有什麼資料是會被立即真正刪除的。

---

## 2. Core Concepts & Mental Model
## 2. 核心觀念與心智模型

### The Three Trees Architecture
### 三棵樹架構

To understand history rewriting, you must visualize Git as managing three distinct states (often called "trees"):
要理解歷史重寫，你必須將 Git 視為管理著三種不同的狀態（通常稱為「樹」）：

1.  **HEAD (The Repository)**: The snapshot of your last commit.
    **HEAD（儲存庫）**：你上一次提交的快照。
2.  **Index (Staging Area)**: The proposed next commit.
    **Index（暫存區）**：預計進行的下一次提交。
3.  **Working Directory**: The actual files you are editing on your disk.
    **Working Directory（工作目錄）**：你磁碟上正在編輯的實際檔案。

`git reset` is essentially a tool to move the **HEAD** pointer and optionally update the **Index** and **Working Directory** to match.
`git reset` 本質上是一個用來移動 **HEAD** 指標的工具，並可選擇性地更新 **Index** 和 **Working Directory** 以使其同步。

### Rebase as "Replaying"
### Rebase 即「重播」

Unlike `merge`, which ties two histories together, `rebase` picks up commits from one branch and "replays" them onto another base.
與將兩段歷史綁在一起的 `merge` 不同，`rebase` 會從一個分支提取提交，並將它們在另一個基底上「重新播放」。

> **Mental Model**: Think of commits as a stack of patches. `rebase` lifts your stack of patches, moves to a new starting point, and applies them one by one. Crucially, this creates **new commit hashes**. The old commits are abandoned (and eventually garbage collected), but the content is preserved in new objects.
>
> **心智模型**：將提交視為一疊補丁（Patches）。`rebase` 將你這疊補丁拿起來，移動到一個新的起點，然後逐一貼上。關鍵在於，這會產生**新的 Commit Hashes**。舊的提交會被遺棄（最終被垃圾回收），但內容會被保存在新的物件中。

### The Safety Net: Reflog
### 安全網：Reflog

The `reflog` (Reference Log) is a local journal that records every time the tip of branches (HEAD) is updated. Even if you delete a branch or hard reset away a commit, the SHA-1 is still in the `reflog` for a default period (usually 30-90 days).
`reflog`（參照日誌）是一份本地日誌，記錄了分支尖端（HEAD）每次更新的時刻。即使你刪除了一個分支或透過 Hard Reset 丟棄了一個提交，其 SHA-1 雜湊值在預設期間內（通常為 30–90 天）仍然存在於 `reflog` 中。

---

## 3. Real-World & System Design View
## 3. 實務場景與系統設計視角

### The Role of Clean History in CI/CD and Debugging
### 整潔歷史在 CI/CD 與除錯中的角色

In a large-scale distributed system, a clean Git history is a documentation artifact.
在大型分散式系統中，整潔的 Git 歷史是一種文件產物。

*   **Bisectability**: When a regression occurs in a microservice, engineers often use `git bisect` to identify the culprit. If the history is littered with "fix typo" or broken intermediate commits, the bisection process becomes painful and inaccurate.
    **二分搜尋能力（Bisectability）**：當微服務出現回歸錯誤（Regression）時，工程師常使用 `git bisect` 來找出罪魁禍首。如果歷史紀錄充滿了「修正錯字」或無法編譯的中間提交，二分搜尋的過程將變得痛苦且不準確。
*   **Revertability**: Atomic commits (one logical change per commit) allow for clean reverts. If a feature commit also includes unrelated refactoring, reverting the feature breaks the refactoring.
    **可還原性（Revertability）**：原子化提交（每個提交只包含一個邏輯變更）允許乾淨的還原。如果一個功能提交同時包含了不相關的重構，還原該功能就會破壞重構。

### Security Compliance
### 安全合規性

Accidentally committing secrets (API keys, DB credentials) is a common incident. Simply adding a new commit to remove the file is insufficient, as the secret remains in the history.
意外提交機密資訊（API Key、資料庫憑證）是常見的事故。僅僅新增一個提交來刪除該檔案是不夠的，因為機密資訊仍然存在於歷史紀錄中。

*   **Solution**: You must rewrite history (using `git filter-repo` or `git rebase`) to scrub the object entirely. This is a form of "Disaster Recovery" where understanding how Git stores objects is vital.
    **解決方案**：你必須重寫歷史（使用 `git filter-repo` 或 `git rebase`）來徹底清除該物件。這是一種「災難救援」的形式，理解 Git 如何儲存物件至關重要。

---

## 4. Walkthrough / Example
## 4. 逐步示例

### Scenario 1: The "Interactive Rebase" Cleanup
### 場景 1：「互動式 Rebase」清理

**Context**: You have been working on a feature branch `feat/user-auth`. You have 5 commits locally, including some "WIP" (Work In Progress) snapshots and typo fixes. You want to merge this as a single, clean unit of work.
**背景**：你正在開發 `feat/user-auth` 功能分支。你在本地有 5 個提交，包含一些「WIP」（進行中）的快照與錯字修正。你希望將其合併為一個單一、乾淨的工作單元。

**Current History (on `feat/user-auth`):**
**當前歷史（在 `feat/user-auth` 上）：**
```text
A --- B (main)
       \
        C (Implement login logic)
        D (WIP: fixing tests)
        E (Fix typo in variable name)
        F (Add logout endpoint)
        G (Fix lint errors) <- HEAD
```

**Step 1: Start Interactive Rebase**
**步驟 1：啟動互動式 Rebase**

Target the parent of your first commit (Commit `B`, which is `HEAD~5` or `main`).
鎖定你第一個提交的父節點（提交 `B`，即 `HEAD~5` 或 `main`）。

```bash
git rebase -i main
```

**Step 2: Edit the Rebase Todo List**
**步驟 2：編輯 Rebase 待辦清單**

Git opens your editor. You will see:
Git 會開啟你的編輯器。你會看到：

```text
pick C Implement login logic
pick D WIP: fixing tests
pick E Fix typo in variable name
pick F Add logout endpoint
pick G Fix lint errors
```

**The Strategy**:
*   Keep `C` as the start.
*   Squash `D` and `E` into `C` (they are part of the login logic).
*   Keep `F` as a separate logical unit (Logout is distinct from Login).
*   Fixup `G` into `F` (lint errors shouldn't be their own commit).

**策略**：
*   保留 `C` 作為開頭。
*   將 `D` 和 `E` 壓縮（Squash）進 `C`（它們屬於登入邏輯的一部分）。
*   保留 `F` 作為獨立的邏輯單元（登出與登入是不同的）。
*   將 `G` 修正（Fixup）進 `F`（Lint 錯誤不應單獨佔一個提交）。

**Modified List**:
**修改後的清單**：
```text
pick C Implement login logic
squash D WIP: fixing tests
squash E Fix typo in variable name
pick F Add logout endpoint
fixup G Fix lint errors
```

**Result**: You now have 2 clean commits on top of `main`.
**結果**：你現在在 `main` 之上有 2 個乾淨的提交。

---

### Scenario 2: The "Reset" Rescue
### 場景 2：「Reset」救援

**Context**: You realized the last 3 commits on your local branch are completely wrong direction-wise, but you want to keep the code changes in your working directory to refactor them.
**背景**：你意識到本地分支上最後 3 個提交的方向完全錯誤，但你希望保留工作目錄中的程式碼變更以便重構。

**Command**:
**指令**：
```bash
# Move HEAD back 3 steps, but keep changes in Staging (Index)
# 將 HEAD 後退 3 步，但保留變更在暫存區（Index）
git reset --soft HEAD~3

# OR

# Move HEAD back 3 steps, keep changes in Working Directory (unstaged)
# 將 HEAD 後退 3 步，保留變更在工作目錄（未暫存）
git reset --mixed HEAD~3
```

**Why not `--hard`?**
`--hard` would destroy your work in the Working Directory. Only use `--hard` if you truly want to discard the code.
**為什麼不用 `--hard`？**
`--hard` 會摧毀你工作目錄中的成果。只有當你真的想要丟棄這些程式碼時才使用 `--hard`。

---

### Scenario 3: Recovering from a Bad `git reset --hard`
### 場景 3：從錯誤的 `git reset --hard` 中復原

**Context**: You accidentally ran `git reset --hard HEAD~5` and lost a week's worth of commits. Panic sets in.
**背景**：你意外執行了 `git reset --hard HEAD~5`，遺失了一週的提交量。恐慌隨之而來。

**Step 1: Check Reflog**
**步驟 1：檢查 Reflog**

```bash
git reflog
```

**Output**:
**輸出**：
```text
a1b2c3d HEAD@{0}: reset: moving to HEAD~5
e5f6g7h HEAD@{1}: commit: Finalize feature X
i8j9k0l HEAD@{2}: commit: Work on feature X
...
```

**Step 2: Reset to the state before the accident**
**步驟 2：重置到事故前的狀態**

You see that `HEAD@{1}` (hash `e5f6g7h`) was the state before you ran the reset command.
你看到 `HEAD@{1}`（雜湊值 `e5f6g7h`）是你執行 reset 指令前的狀態。

```bash
git reset --hard e5f6g7h
```

**Result**: Everything is back.
**結果**：一切都回來了。

---

## 5. Common Pitfalls & Anti-patterns
## 5. 常見錯誤與反模式

### 1. Rebasing Public/Shared Branches
### 1. Rebase 公開/共享的分支

*   **Anti-pattern**: Running `git rebase` on `main` or `develop` branches that other team members have pulled.
    **反模式**：在其他團隊成員已經 Pull 下來的 `main` 或 `develop` 分支上執行 `git rebase`。
*   **Why it's bad**: Rebase rewrites history (changes commit hashes). When teammates try to pull, Git will see divergent histories, forcing them to resolve complex conflicts or accidentally re-introducing old commits.
    **為何不好**：Rebase 會重寫歷史（改變 Commit Hashes）。當隊友嘗試 Pull 時，Git 會看到分歧的歷史，迫使他們解決複雜的衝突，或意外地重新引入舊的提交。
*   **Correction**: **Only rebase branches that belong exclusively to you** (local branches or feature branches not yet shared/collaborated on).
    **修正**：**只 Rebase 專屬於你的分支**（本地分支或尚未共享/協作的功能分支）。

### 2. The "Backup Branch" Clutter
### 2. 「備份分支」的混亂

*   **Anti-pattern**: Creating `feat-backup-1`, `feat-backup-final`, `feat-backup-real-final` before doing a rebase, "just in case."
    **反模式**：在做 Rebase 之前建立 `feat-backup-1`、`feat-backup-final`、`feat-backup-real-final`，「以防萬一」。
*   **Why it's bad**: It pollutes the repository and indicates a lack of trust in Git's recovery tools.
    **為何不好**：這會污染儲存庫，並顯示出對 Git 救援工具缺乏信任。
*   **Correction**: Trust `git reflog`. You can always jump back to the state before the rebase using the reflog.
    **修正**：信任 `git reflog`。你隨時可以使用 reflog 跳回 Rebase 之前的狀態。

### 3. Misunderstanding `reset` vs `checkout`
### 3. 誤解 `reset` 與 `checkout`

*   **Anti-pattern**: Using `git reset` to view an old commit, then coding on top of it in a "detached HEAD" state.
    **反模式**：使用 `git reset` 來查看舊的提交，然後在「Detached HEAD」狀態下進行開發。
*   **Correction**: Use `git checkout <commit-hash>` (or `git switch --detach`) to view old states. Use `git reset` primarily to move the current branch pointer.
    **修正**：使用 `git checkout <commit-hash>`（或 `git switch --detach`）來查看舊狀態。`git reset` 主要用於移動當前的分支指標。

---

## 6. Interview & Discussion Hooks
## 6. 面試與實務問答切入點

### Q1: "Explain the difference between `git merge` and `git rebase`. When would you use one over the other in a team workflow?"
### Q1：「請解釋 `git merge` 與 `git rebase` 的差異。在團隊工作流程中，你何時會選擇其中之一？」

*   **Key Points**:
    *   **Merge**: Preserves history exactly as it happened (chronological). Non-destructive. Can create "merge bubbles" (cluttered history). Good for preserving the context of a feature branch integration.
    *   **Rebase**: Rewrites history to be linear. Cleaner history, easier `bisect`. Destructive (changes hashes). Good for keeping a local feature branch up-to-date with `main` before a PR.
    *   **Golden Rule**: Never rebase public history.
*   **關鍵點**：
    *   **Merge**：如實保留歷史發生的過程（依時間序）。非破壞性。可能會產生「合併氣泡」（歷史雜亂）。適合保留功能分支整合的上下文。
    *   **Rebase**：將歷史重寫為線性。歷史較乾淨，易於 `bisect`。破壞性（改變 Hashes）。適合在 PR 之前，讓本地功能分支與 `main` 保持同步。
    *   **黃金準則**：永遠不要 Rebase 公開的歷史。

### Q2: "You accidentally committed a file containing a hardcoded AWS Secret Key to a public repository. What steps do you take?"
### Q2：「你意外地將一個包含寫死 AWS Secret Key 的檔案提交到了公開儲存庫。你會採取什麼步驟？」

*   **Key Points**:
    *   **Immediate Action**: Revoke the key in AWS console (rotate credentials). This is the most critical step.
    *   **Git Action**: A simple `git revert` or deleting the file in a new commit is not enough (the secret remains in history).
    *   **Remediation**: Use `git filter-repo` (preferred over the deprecated `filter-branch`) or BFG Repo-Cleaner to rewrite history and remove the object. Force push (`git push --force`) is required.
*   **關鍵點**：
    *   **立即行動**：在 AWS 控制台撤銷該金鑰（輪替憑證）。這是最關鍵的一步。
    *   **Git 行動**：簡單的 `git revert` 或在新提交中刪除檔案是不夠的（機密仍留在歷史中）。
    *   **補救措施**：使用 `git filter-repo`（優於已棄用的 `filter-branch`）或 BFG Repo-Cleaner 重寫歷史並移除該物件。需要強制推送（`git push --force`）。

### Q3: "How does `git reset --soft HEAD~1` differ from `git reset --mixed HEAD~1` internally?"
### Q3：「`git reset --soft HEAD~1` 與 `git reset --mixed HEAD~1` 在內部運作上有何不同？」

*   **Key Points**:
    *   Both move the HEAD pointer back one commit.
    *   `--soft`: Leaves the **Index (Staging)** and **Working Directory** alone. The changes from the undone commit are now "staged" and ready to be committed again.
    *   `--mixed` (Default): Resets the **Index** to match the new HEAD, but leaves the **Working Directory** alone. The changes are now "unstaged" (modified but not added).
*   **關鍵點**：
    *   兩者都會將 HEAD 指標往後移一個提交。
    *   `--soft`：不更動 **Index（暫存區）** 與 **Working Directory**。被撤銷的提交內容現在處於「已暫存」狀態，隨時可再次提交。
    *   `--mixed`（預設值）：將 **Index** 重置為與新的 HEAD 一致，但不更動 **Working Directory**。變更內容現在處於「未暫存」狀態（已修改但未 Add）。

---

## 7. Summary & Next Steps
## 7. 小結與後續延伸

### Recap
### 重點回顧

1.  **History is Mutable**: Until you push, your local history is a draft. Use `git rebase -i` to polish it.
    **歷史是可變的**：在你 Push 之前，本地歷史只是草稿。使用 `git rebase -i` 來潤飾它。
2.  **Reset Levels**:
    **Reset 層級**：
    *   `Soft`: Move HEAD only (Keep Staged).
    *   `Mixed`: Move HEAD + Index (Keep Working Dir).
    *   `Hard`: Move HEAD + Index + Working Dir (Destructive).
3.  **Reflog is King**: It is your undo button for "destructive" operations. If you messed up a rebase or reset, `git reflog` can save you.
    **Reflog 是王道**：它是你「破壞性」操作的復原按鈕。如果你搞砸了 Rebase 或 Reset，`git reflog` 能救你一命。
4.  **Don't Rebase Public**: Respect the shared history of your team.
    **不要 Rebase 公開分支**：尊重團隊的共享歷史。

### Next Steps
### 下一步

*   **Advanced Configuration**: Explore **Git Hooks** (`pre-commit`, `pre-push`) to automate the "clean history" checks (e.g., linting before commit).
    **進階配置**：探索 **Git Hooks**（`pre-commit`、`pre-push`）來自動化「整潔歷史」的檢查（例如：提交前進行 Linting）。
*   **Internal Mechanics**: Dive deeper into Git's object model (Blobs, Trees, Commits) to understand exactly *how* `rebase` constructs new trees.
    **內部機制**：深入研究 Git 的物件模型（Blobs、Trees、Commits），以理解 `rebase` 究竟是 *如何* 建構新樹的。