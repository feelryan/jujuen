# 規模化治理與程式碼審查文化 / Governance at Scale and Code Review Culture

## Mental model｜心智模型

在 GitLab 中進行規模化治理時，不應將其僅視為「程式碼倉庫的集合」，而應視為一個 **「具備繼承特性的組織樹狀結構」 (Hierarchical Inheritance Tree)**。

### 1. 繼承優先 (Inheritance First)
GitLab 的核心治理邏輯建立在 Group（群組）與 Subgroup（子群組）之上。變數 (CI/CD Variables)、權限 (Members)、標籤 (Labels) 與 Runner 資源，預設都是**由上而下繼承**的。
*   **Think like CSS:** 父層定義樣式（規範），子層繼承並在必要時覆寫（Override）。
*   **Don't Repeat Yourself (DRY):** 如果你需要重複設定 10 次相同的變數，表示你的 Group 結構設計有誤。

### 2. 程式碼即合規 (Policy as Code)
審查文化不應只靠口頭約束，而應具現化為程式碼與設定檔。
*   **`CODEOWNERS` as Law:** 誰負責哪塊程式碼，不是看組織圖，而是看 Repo 裡的 `CODEOWNERS` 檔案。
*   **MR as a Gatekeeper:** Merge Request 不只是合併程式碼的動作，它是品質控制、安全掃描與知識傳遞的「閘門」。

---

## Patterns & best practices｜常見模式與最佳實務

### 1. 組織結構設計模式 (Structuring Groups & Projects)

在大型組織中，Group 的結構決定了治理的難易度。

*   **依產品/價值流分組 (Product-based Structure)**：
    *   推薦模式：`Organization` -> `Product Line` -> `Service/Component`。
    *   優點：人員權限容易管理（團隊專注於特定產品線），CI/CD 變數隔離清晰。
*   **基礎設施與共享程式庫分離**：
    *   建立專門的 `Platform-Engineering` 或 `Shared-Libs` Group。
    *   將共用的 CI Templates、Terraform Modules 放在此處，並設定較嚴格的寫入權限。

### 2. Code Owners 進階應用 (Advanced Code Owners)

不要只把 `CODEOWNERS` 當作指派審核人的工具，它是權責劃分的機制。

*   **分區段治理 (Sectional Governance)**：
    利用 `[Section]` 語法區分不同類型的審核需求。
    ```plaintext
    [Backend]
    *.go @backend-team

    [Frontend]
    /frontend/ @frontend-team

    [Security Critical]
    /auth/ @security-team
    ```
*   **強制核准 (Require Approval)**：
    在 Settings 中開啟 "Require approval from code owners"，確保關鍵路徑（如資料庫遷移腳本、鑑權邏輯）未經特定專家審核無法合併。

### 3. Merge Request (MR) 協作標準

*   **MR Templates (樣板)**：
    在 `.gitlab/merge_request_templates/` 中定義多種樣板（例如 `Feature.md`, `Bugfix.md`）。
    *   *Must-have:* "What is changing?", "Why?", "How to test?", "Screenshots/Logs".
*   **Approval Rules (核准規則)**：
    設定 `Minimum approvals`（通常建議至少 2 人：1 位 Code Owner + 1 位 Peer）。
*   **Draft 模式 (WIP)**：
    鼓勵儘早開啟 MR 並標記為 `Draft:`，讓 CI Pipeline 儘早介入掃描，而非開發完成後才發現安全漏洞。

---

## Anti-patterns & pitfalls｜反模式與踩雷點

### 1. 扁平化地獄 (Flat Structure Hell)
*   **現象**：所有專案都直接開在同一個頂層 Group 下，或者完全沒有 Group 概念。
*   **後果**：無法共用 CI 變數（每個專案都要手貼 AWS Key），權限管理混亂（新進員工要被加入 50 個專案）。
*   **修正**：依據康威定律（Conway's Law）或產品邊界重構 Group 層級。

### 2. 幽靈 Code Owner (The Phantom Owner)
*   **現象**：`CODEOWNERS` 指派給 `@cto` 或 `@tech-lead`，但他們根本沒時間看 code。
*   **後果**：MR 堆積如山，最後被迫開啟 "Override" 強制合併，制度形同虛設。
*   **修正**：指派給實際開發的 Group（如 `@backend-guild`），而非個人；或設定輪值機制。

### 3. 橡皮圖章文化 (Rubber Stamping)
*   **現象**：審核者只看標題就按 "Approve"，或者只檢查語法不檢查邏輯。
*   **後果**：Bug 流入生產環境，Code Review 變成單純的流程拖延。
*   **修正**：引入自動化工具（Linting, SAST）處理語法問題，人腦專注於架構與邏輯；在 MR Template 中加入 "Reviewer Checklist"。

### 4. 長壽分支 (Long-lived Feature Branches)
*   **現象**：一個 MR 包含 50 個檔案變更，開發週期長達兩週。
*   **後果**：Code Review 極其痛苦，Merge Conflict 風險極高。
*   **修正**：強制執行 "Short-lived branches" 策略，超過一定行數或天數的 MR 應被拆分。

---

## Checklists & workflows｜檢查清單與流程

### Decision Tree: Group vs Project
當你需要一個新空間時：
1. **是否包含多個相關的微服務/儲存庫？** -> Create **Subgroup**.
2. **是否需要獨立的權限控管或變數範圍？** -> Create **Subgroup**.
3. **是否只是一個單純的程式碼倉庫？** -> Create **Project**.

### Workflow: Setting up a Governed Project (專案治理設定流程)

- [ ] **繼承檢查**：確認專案位於正確的 Subgroup，以繼承正確的 CI/CD 變數與 Runner。
- [ ] **分支保護 (Protected Branches)**：
    - [ ] `main`/`master` 設定為 "No one can push" (強制走 MR)。
    - [ ] 設定 "Allowed to merge" 僅限 Maintainers。
- [ ] **合併檢查 (Merge Checks)**：
    - [ ] 勾選 "Pipelines must succeed"。
    - [ ] 勾選 "All discussions must be resolved"。
- [ ] **Code Owners**：
    - [ ] 建立 `CODEOWNERS` 檔案。
    - [ ] 勾選 "Require approval from code owners"。
- [ ] **MR 設定**：
    - [ ] 設定預設 MR Template。
    - [ ] 開啟 "Squash commits when merging" (保持主分支乾淨)。

### Checklist: High-Quality Code Review (審查者清單)

- [ ] **CI 狀態**：Pipeline 是否全綠？測試覆蓋率是否下降？
- [ ] **範圍 (Scope)**：變更是否符合 MR 標題描述？有無夾帶無關的修改？
- [ ] **安全性**：是否有 Hard-coded secrets？是否有 SQL Injection 風險？
- [ ] **可維護性**：變數命名是否清晰？是否有重複程式碼？
- [ ] **文件**：若修改了 API 或設定，README/Wiki 是否同步更新？

---

## Real-world examples｜實戰案例

### Scenario: 金融科技公司的合規治理

**背景**：一家 FinTech 公司要求所有資料庫變更必須由 DBA 審核，且所有程式碼必須通過資安掃描才能合併。

#### 1. Group Structure
```text
/fintech-corp (Root)
  ├── /platform (Infra, CI Templates)
  │     └── [Project] ci-templates
  ├── /banking-app (Subgroup for Product A)
  │     ├── [Settings] CI Variables: AWS_ACCESS_KEY (Inherited)
  │     ├── [Project] core-api
  │     └── [Project] frontend-web
  └── /security (Subgroup for Security Team)
```

#### 2. `CODEOWNERS` Implementation
在 `core-api` 專案中：

```plaintext
# 預設所有檔案由後端團隊負責
* @fintech-corp/backend-team

# 資料庫遷移腳本必須由 DBA 團隊核准
/db/migrations/ @fintech-corp/dba-team

# 敏感設定檔必須由資安團隊與 Tech Lead 共同核准
/config/production.yaml @fintech-corp/security-team @tech-lead
```

#### 3. Merge Request Policy (Settings)
*   **Merge checks**:
    *   `Pipelines must succeed` (強制執行 SAST/DAST 掃描 job)。
    *   `Skipped pipelines are considered successful` -> **Disabled** (不能跳過掃描)。
*   **Approval Rules**:
    *   Rule Name: `Security Check`
    *   Target Branch: `main`
    *   Approvals required: `1`
    *   Approvers: `@fintech-corp/security-team`

#### 4. 結果
當開發者提交一個包含 `/db/migrations/V1__init.sql` 的 MR 時：
1. GitLab 自動將 `@fintech-corp/dba-team` 加入審核者列表。
2. 即使 `@backend-team` 核准了，若 DBA 未核准，Merge 按鈕為灰色（不可點擊）。
3. 若 CI Pipeline 中的 `sast` job 失敗，Merge 按鈕同樣鎖定。

這確保了治理規範（Governance）不是依賴人為記憶，而是由 GitLab 平台強制執行。