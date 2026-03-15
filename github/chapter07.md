# 1. 前言與學習目標 (Introduction & Learning Objectives)

對於資深工程師而言，GitHub 不僅僅是一個版本控制的託管服務，更是一個可程式化的平台（Programmable Platform）。掌握 GitHub API 與整合工具，意味著你有能力構建自動化工作流（Workflows）、內部開發者平台（Internal Developer Platforms, IDP）以及高效率的治理工具。本章將帶你從「使用者」轉變為「工具製造者」。

For senior engineers, GitHub is not just a version control hosting service, but a **Programmable Platform**. Mastering the GitHub API and integration tools means you have the capability to build automated workflows, Internal Developer Platforms (IDP), and efficient governance tools. This chapter will guide your transition from a "user" to a "toolmaker".

完成本章後，你應該能夠：
By the end of this chapter, you should be able to:

1.  **區分並選擇正確的整合模型**：清楚解釋 GitHub Apps 與 OAuth Apps 的差異，並知道何時該使用哪一種（特別是在安全性與權限控制方面）。
    **Distinguish and select the correct integration model**: Clearly explain the differences between GitHub Apps and OAuth Apps, and know when to use which (especially regarding security and permission control).
2.  **熟練操作 GitHub API**：能夠比較 REST API 與 GraphQL API 的優劣，並針對大量數據抓取場景（如分析 PR 週期）選擇高效的查詢方式。
    **Master the GitHub API**: Compare the pros and cons of REST API vs. GraphQL API, and select efficient query methods for data-heavy scenarios (e.g., analyzing PR cycle times).
3.  **構建強健的 Webhook 處理系統**：設計能夠處理並發請求、驗證安全性簽章（Signature Verification）且具備重試機制的 Webhook 接收服務。
    **Build robust Webhook handlers**: Design a webhook receiver service capable of handling concurrent requests, verifying security signatures, and implementing retry mechanisms.
4.  **利用 GitHub CLI (`gh`) 提升生產力**：不只是用來開 PR，而是將 `gh` 作為腳本中的核心元件，快速實現自動化任務。
    **Leverage GitHub CLI (`gh`) for productivity**: Use `gh` not just for opening PRs, but as a core component in scripts to rapidly implement automation tasks.

---

# 2. 核心觀念與心智模型 (Core Concepts & Mental Model)

## 2.1 兩種 API 典範：REST vs. GraphQL
## 2.1 Two API Paradigms: REST vs. GraphQL

GitHub 同時提供 REST API (v3) 與 GraphQL API (v4)。
GitHub offers both REST API (v3) and GraphQL API (v4).

-   **REST (v3)**：就像「點套餐」。介面穩定、易於理解，但容易發生 Over-fetching（拿了不需要的欄位）或 Under-fetching（需要多次請求才能湊齊資料，即 N+1 問題）。適合簡單的 CRUD 操作。
    **REST (v3)**: Like "ordering a set menu." The interface is stable and easy to understand, but prone to **Over-fetching** (getting unneeded fields) or **Under-fetching** (requiring multiple requests to gather data, i.e., the N+1 problem). Suitable for simple CRUD operations.

-   **GraphQL (v4)**：就像「自助餐」。你可以精確指定需要的欄位與關聯資料。對於需要一次獲取複雜關聯（例如：「列出所有 Repo 的前 5 個 PR 及其最後一條評論」）的場景，GraphQL 是效能優化的關鍵。
    **GraphQL (v4)**: Like a "buffet." You can precisely specify the fields and relationships you need. For scenarios requiring complex relationships in one go (e.g., "list the top 5 PRs of all repos and their last comment"), GraphQL is key to performance optimization.

## 2.2 身份驗證模型：User vs. App
## 2.2 Authentication Models: User vs. App

這是資深工程師最常混淆或設計錯誤的地方。
This is where senior engineers most often get confused or make design errors.

| Feature | Personal Access Token (PAT) / OAuth App | GitHub App |
| :--- | :--- | :--- |
| **Identity (身份)** | 代表「使用者」(Acting as a User) | 代表「應用程式/機器人」(Acting as a Bot/Service) |
| **Permissions (權限)** | 粗粒度 (Scopes)，通常繼承使用者的所有權限 | 細粒度 (Permissions)，僅授權特定 Repo 或資源 |
| **Rate Limit (速率限制)** | 綁定使用者 (e.g., 5000 requests/hr) | 隨安裝數量擴展 (Scaling with installations) |
| **Security (安全性)** | Token 洩漏等同使用者帳號被盜 | 使用私鑰簽署 JWT，生成短效期的 Installation Token |
| **Use Case (適用場景)** | 個人腳本、CLI 登入、簡單的第三方登入 | CI/CD 整合、大型自動化工具、企業級 Bot |

**心智模型**：將 OAuth App 想像成「代理人」，它拿著你的識別證去辦事；將 GitHub App 想像成一個擁有自己識別證的「專職僱員」，它有明確的職責範圍（權限），且離職（移除安裝）後權限即刻失效。
**Mental Model**: Think of an OAuth App as a **"Delegate"** holding your ID badge to do things; think of a GitHub App as a **"Dedicated Employee"** with its own ID badge, having a clear scope of duty (permissions), and whose access is immediately revoked upon termination (uninstall).

---

# 3. 實務場景與系統設計視角 (Real-World & System Design View)

在企業級系統設計中，GitHub 整合通常出現在以下場景：
In enterprise system design, GitHub integration typically appears in the following scenarios:

## 3.1 內部開發者平台 (Internal Developer Platform, IDP)
## 3.1 Internal Developer Platform (IDP)

當公司規模擴大，你需要一個 IDP 來管理數百個 Microservices。
As the company scales, you need an IDP to manage hundreds of microservices.

-   **Scaffolding**：工程師在 IDP 點擊「Create Service」，後端呼叫 GitHub API 建立 Repo、設定 Branch Protection Rules、並注入 CI/CD 設定檔。
    **Scaffolding**: Engineers click "Create Service" on the IDP. The backend calls the GitHub API to create a repo, configure Branch Protection Rules, and inject CI/CD configurations.
-   **Governance**：定期掃描所有 Repos，檢查是否包含敏感資訊或過時的依賴（Dependency），並自動開 Issue 或 PR 修復。
    **Governance**: Periodically scan all repos to check for sensitive information or outdated dependencies, and automatically open Issues or PRs to fix them.

## 3.2 事件驅動自動化 (Event-Driven Automation)
## 3.2 Event-Driven Automation

架構通常如下：
The architecture typically looks like this:

`GitHub (Webhook)` -> `API Gateway` -> `Lambda/Worker` -> `Business Logic` -> `GitHub API (Feedback)`

-   **安全性 (Security)**：Webhook 接收端必須驗證 `X-Hub-Signature-256` header，確保請求真的來自 GitHub，防止偽造攻擊。
    **Security**: The Webhook receiver must validate the `X-Hub-Signature-256` header to ensure the request genuinely originates from GitHub, preventing spoofing attacks.
-   **非同步處理 (Async Processing)**：GitHub Webhook 預期在短時間內收到回應。若處理邏輯耗時（如執行測試、部署），應將事件丟入 Message Queue (SQS/Kafka)，回傳 202 Accepted，再由 Worker 非同步處理。
    **Async Processing**: GitHub Webhooks expect a response within a short timeframe. If the processing logic is time-consuming (e.g., running tests, deployment), push the event to a Message Queue (SQS/Kafka), return 202 Accepted, and handle it asynchronously via a Worker.

---

# 4. 逐步示例：使用 GitHub CLI 與 GraphQL 進行批量操作 (Walkthrough / Example)

## 情境 (Scenario)
你需要找出組織內所有處於 "Open" 狀態且超過 30 天未更新的 Pull Requests，並在上面留言提醒開發者。
You need to identify all "Open" Pull Requests in your organization that haven't been updated in over 30 days and comment on them to nudge the developers.

## 解決方案 (Solution)

我們可以使用 `gh` CLI 結合 GraphQL 來高效完成此任務，避免 REST API 的多次往返。
We can use the `gh` CLI combined with GraphQL to efficiently accomplish this task, avoiding the multiple round-trips of the REST API.

### Step 1: 設計 GraphQL Query
### Step 1: Design the GraphQL Query

我們需要查詢 Organization 下的所有 Repositories，再查每個 Repo 的 Pull Requests。
We need to query all Repositories under an Organization, and then the Pull Requests for each Repo.

```graphql
query($orgName: String!, $limit: Int!) {
  organization(login: $orgName) {
    repositories(first: $limit, orderBy: {field: UPDATED_AT, direction: DESC}) {
      nodes {
        name
        pullRequests(first: 20, states: OPEN, orderBy: {field: UPDATED_AT, direction: ASC}) {
          nodes {
            id
            title
            url
            updatedAt
          }
        }
      }
    }
  }
}
```

### Step 2: 撰寫自動化腳本 (Bash + gh)
### Step 2: Write the Automation Script (Bash + gh)

這個腳本展示了如何將 `gh api` 的結果傳遞給 `jq` 進行過濾，再回頭呼叫 `gh` 進行寫入操作。
This script demonstrates how to pipe the output of `gh api` to `jq` for filtering, and then call `gh` again for write operations.

```bash
#!/bin/bash

ORG_NAME="my-org"
DAYS_THRESHOLD=30
# 計算 30 天前的日期 (Linux date format, adjust for macOS if needed)
DATE_LIMIT=$(date -d "$DAYS_THRESHOLD days ago" +%Y-%m-%dT%H:%M:%SZ)

echo "Fetching stale PRs for organization: $ORG_NAME..."

# 1. 使用 gh api 執行 GraphQL 查詢
# 1. Execute GraphQL query using gh api
gh api graphql -F orgName="$ORG_NAME" -F limit=10 -f query='
query($orgName: String!, $limit: Int!) {
  organization(login: $orgName) {
    repositories(first: $limit) {
      nodes {
        name
        pullRequests(first: 50, states: OPEN) {
          nodes {
            id
            title
            url
            updatedAt
          }
        }
      }
    }
  }
}' > raw_data.json

# 2. 使用 jq 過濾出過期的 PR (這裡簡化了邏輯，實務上需處理分頁)
# 2. Use jq to filter stale PRs (Logic simplified here; pagination is needed in practice)
# 注意：這裡僅為邏輯演示，jq 的日期比較需要轉換格式
jq -r --arg limit "$DATE_LIMIT" '
  .data.organization.repositories.nodes[].pullRequests.nodes[] 
  | select(.updatedAt < $limit) 
  | "\(.id) \(.url) \(.title)"
' raw_data.json | while read -r pr_id pr_url pr_title; do
  
  echo "Found Stale PR: $pr_title ($pr_url)"
  
  # 3. 執行操作：留言提醒 (Dry run)
  # 3. Action: Comment to nudge (Dry run)
  # gh pr comment "$pr_url" --body "This PR has been inactive for over 30 days. Please close or update it."
  echo "Would comment on $pr_url"

done
```

### 實務考量 (Practical Considerations)
-   **分頁 (Pagination)**：GraphQL 回傳的資料量有限制（通常 100 個節點）。對於大型組織，必須實作 `pageInfo { endCursor, hasNextPage }` 的遞迴查詢。
    **Pagination**: GraphQL response size is limited (usually 100 nodes). For large organizations, you must implement recursive queries using `pageInfo { endCursor, hasNextPage }`.
-   **Rate Limiting**：GraphQL 的 Rate Limit 是根據「複雜度 (Complexity)」計算的，而非請求次數。查詢越多欄位，消耗的點數越多。
    **Rate Limiting**: GraphQL Rate Limits are calculated based on "Complexity," not request count. The more fields you query, the more points you consume.

---

# 5. 常見錯誤與反模式 (Common Pitfalls & Anti-patterns)

## 5.1 在 CI/CD 中使用個人 PAT (Using Personal PATs in CI/CD)
-   **錯誤**：使用某位資深工程師的 Personal Access Token 來設定 CI/CD 流程。
    **Mistake**: Using a specific senior engineer's Personal Access Token to configure CI/CD pipelines.
-   **後果**：當該工程師離職或更改密碼時，所有自動化流程瞬間崩潰（Bus Factor = 1）。且該 Token 權限通常過大，有安全隱憂。
    **Consequence**: When that engineer leaves or changes their password, all automation pipelines break instantly (Bus Factor = 1). Also, the token usually has excessive permissions, posing a security risk.
-   **修正**：使用 **GitHub Apps** 或 **Machine Users** (專用的服務帳號)，並嚴格限制權限範圍。
    **Fix**: Use **GitHub Apps** or **Machine Users** (dedicated service accounts) with strictly scoped permissions.

## 5.2 忽略 Webhook 的冪等性 (Ignoring Webhook Idempotency)
-   **錯誤**：假設 GitHub 只會發送一次 Webhook，直接在接收端執行不可逆操作（如扣款、部署）。
    **Mistake**: Assuming GitHub sends a webhook only once and directly executing irreversible operations (e.g., charging, deploying) on the receiver.
-   **後果**：GitHub 在超時或錯誤時會重試發送，導致重複觸發。
    **Consequence**: GitHub retries on timeouts or errors, leading to duplicate triggers.
-   **修正**：根據 `X-GitHub-Delivery` ID 記錄已處理過的事件，確保操作是冪等的（Idempotent）。
    **Fix**: Track processed events using the `X-GitHub-Delivery` ID to ensure operations are idempotent.

## 5.3 輪詢而非監聽 (Polling instead of Listening)
-   **錯誤**：寫一個 Cron Job 每分鐘去問 GitHub API "有沒有新的 PR？"。
    **Mistake**: Writing a Cron Job that asks the GitHub API "Are there any new PRs?" every minute.
-   **後果**：浪費 API Quota，且即時性差。
    **Consequence**: Wastes API Quota and suffers from poor real-time performance.
-   **修正**：優先使用 Webhooks。只有在無法使用 Webhooks 或需要資料修復（Reconciliation）時才使用輪詢。
    **Fix**: Prioritize Webhooks. Use polling only when Webhooks are unavailable or for data reconciliation.

---

# 6. 面試與實務問答切入點 (Interview & Discussion Hooks)

## Q1: 請設計一個系統，當 GitHub Repo 有新的 Release 時，自動更新內部的部署系統。
## Q1: Design a system that automatically updates an internal deployment system when a new Release is published in a GitHub Repo.

-   **高分回答要點 (Key Points)**：
    -   **Trigger**: 使用 Webhook 監聽 `release` 事件。
    -   **Security**: 提到 HMAC 簽章驗證 (`X-Hub-Signature-256`)。
    -   **Reliability**: 使用 Queue 處理 Webhook，避免部署腳本執行過久導致 Webhook Timeout。
    -   **Auth**: 部署系統回寫 GitHub（例如更新 Deployment status）時，應使用 GitHub App 的 Installation Token，而非 PAT。

## Q2: 比較 GitHub App 與 OAuth App，你會在什麼情況下選擇哪一個？
## Q2: Compare GitHub Apps and OAuth Apps. In what scenarios would you choose one over the other?

-   **高分回答要點 (Key Points)**：
    -   **OAuth App**: 適合「代表使用者」的操作，例如 "Sign in with GitHub" 或 CLI 工具。權限跟隨使用者。
    -   **GitHub App**: 適合「自動化流程」與「跨使用者」的操作，例如 CI Server、Linter Bot。權限是安裝在 Repo 上的，且 Token 是短效期的，安全性更高，Rate Limit 也更高。

## Q3: 你的自動化腳本遇到了 GitHub API Rate Limit 限制，你會如何解決？
## Q3: Your automation script is hitting GitHub API Rate Limits. How do you resolve this?

-   **高分回答要點 (Key Points)**：
    -   **短期**: 實作 Exponential Backoff 重試機制；檢查 Response Header 中的 `X-RateLimit-Reset`。
    -   **優化**: 從 REST 切換到 GraphQL 以減少請求次數；僅請求必要欄位以降低 GraphQL 複雜度分數。
    -   **架構**: 如果是使用 PAT，改用 GitHub App（因為 App 的 Rate Limit 是根據安裝數擴展的）；或者使用 Conditional Requests (Etag) 來利用 304 Not Modified 節省 Quota。

---

# 7. 小結與後續延伸 (Summary & Next Steps)

## 記憶錨點 (Key Takeaways)
1.  **API 選擇**：簡單操作用 REST，複雜關聯查詢用 GraphQL。
    **API Selection**: Use REST for simple operations; use GraphQL for complex relational queries.
2.  **安全性優先**：在企業環境中，優先使用 **GitHub Apps** 而非 PAT，以獲得更細粒度的權限控制與短效期 Token。
    **Security First**: In enterprise environments, prioritize **GitHub Apps** over PATs for granular permission control and short-lived tokens.
3.  **Webhook 最佳實踐**：驗證簽章、快速回應 (Async)、處理重複發送 (Idempotency)。
    **Webhook Best Practices**: Verify signatures, respond quickly (Async), and handle duplicate deliveries (Idempotency).
4.  **工具整合**：`gh` CLI 是強大的腳本工具，善用 `gh api` 結合 `jq` 可以解決大部分輕量級自動化需求。
    **Tool Integration**: The `gh` CLI is a powerful scripting tool. Leveraging `gh api` with `jq` can solve most lightweight automation needs.

## 後續延伸 (Next Steps)
-   **GitHub Actions (Chapter 08)**：本章學習了 API 與工具，下一章將學習如何將這些邏輯嵌入到 GitHub Actions 中，建立完整的 CI/CD Pipeline。
    **GitHub Actions (Chapter 08)**: Having learned the API and tools, the next chapter will cover how to embed this logic into GitHub Actions to build complete CI/CD pipelines.
-   **進階實作**：嘗試建立一個簡單的 GitHub App，並部署到 AWS Lambda 或 Google Cloud Functions 上，接收 Webhook 並自動回應 PR。
    **Advanced Practice**: Try building a simple GitHub App and deploying it to AWS Lambda or Google Cloud Functions to receive webhooks and automatically reply to PRs.