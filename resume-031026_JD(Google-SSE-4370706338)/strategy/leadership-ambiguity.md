# 行為面試：Googleyness 與技術領導力 / Behavioral: Googleyness & Technical Leadership

## Why this matters｜為什麼這個主題重要

在 Google 的 Senior Software Engineer (L5) 面試中，技術能力只是入場券，**Googleyness（文化契合度）與 Leadership（領導力）往往是決定能否錄取或定級的關鍵**。

針對這份 **Diagnostics, Tools (MSCA)** 的 JD 與你的履歷，這個主題有三個關鍵切入點：

1.  **JD 明確要求 "Lead members"**：
    雖然你的職稱是 Senior SE，但你的履歷在 Innova Solutions 的描述較多是 "Maintained" 或 "Designed"，較少強調「帶領他人」。面試官會嚴格檢視你是否具備「不帶職權的領導力 (Influence without authority)」。
2.  **NPI (New Product Introduction) 本質就是「模糊 (Ambiguity)」**：
    JD 提到 NPI 與 Hardware interaction。硬體開發週期長且變數多，軟體規格常不明確。面試官需要確認：當需求不清楚時，你是否能主動定義問題，而不是等待指令？
3.  **跨領域溝通**：
    JD 提到要與 Hardware、Networking 團隊合作。你的履歷有醫療 (Innova) 與電信 (Chunghwa) 背景，這些都是高合規、高複雜度的領域，這是你的優勢，但需轉化為「如何解決跨部門衝突」的故事。

---

## Step‑by‑step strategy｜具體行動步驟

### Week 1: Story Mining (挖掘故事)
不要只看最近的工作，要回顧整個 15+ 年職涯，但重點放在 Innova (近期) 與 Chunghwa (正式領導經驗)。

*   **找出 3 個「模糊性」故事 (Ambiguity)**：
    *   *Target:* 在 Innova 推動 "GCP Storage Bucket Auto-Creation" 或 "FDA 510K" 相關功能時，是否曾面臨需求不清？或是流程混亂？
    *   *Action:* 寫下當時「資訊最缺乏」的時刻，你做了什麼來釐清現狀？
*   **找出 3 個「技術領導」故事 (Technical Leadership)**：
    *   *Target:* 履歷提到 "Drove CI/CD and code quality improvements"。這是一個完美的題材。
    *   *Action:* 描述你如何「說服」團隊採用新流程？有沒有人反對？你如何透過數據或 POC (Proof of Concept) 證明你的方案更好？
*   **找出 2 個「失敗/衝突」故事 (Failure/Conflict)**：
    *   Google 非常看重你如何處理失敗。
    *   *Target:* 過去在 System Design 或 API 設計上，是否曾做錯決定？或者與 PM/UI (如 Hiveel 時期) 有過意見不合？

### Week 2: STAR-L Structuring (結構化敘事)
將上述故事改寫為 **STAR-L** 格式 (Situation, Task, Action, Result, **Learning/Leadership**)。

*   **重點調整**：
    *   把 "We" 改成 "I"：不要說「我們團隊決定...」，要說「我觀察到...因此我提議...」。
    *   加入數據：利用你履歷中的 "reduce review time" 或 "increase delivery velocity" 作為 Result。

### Week 3: Mock & Refine (模擬與修飾)
*   **針對 "Lead members" 的修飾**：
    即使在 Innova 不是 Manager，你要強調 "Mentorship"。例如：「我發現資淺工程師常犯某個錯誤，因此我引入了 AI-assisted refactoring 工具，並撰寫了文件指導他們。」
*   **針對 "Googleyness" 的修飾**：
    確保故事展現：Psychological Safety (心理安全感)、Bias for Action (行動偏好)、Put the User First (用戶至上)。

---

## Examples & templates｜範例與句型

### 1. 處理模糊性 (Dealing with Ambiguity)
**情境：** JD 裡的 NPI 專案通常規格未定。
**履歷連結：** Innova 的 FDA 510K 專案或 Chunghwa 的國家級警報系統。

*   **Template:**
    > "In my previous role at Innova, we faced a challenge where the requirements for [Feature X] were vague due to changing compliance regulations. Instead of waiting for final specs, I took the initiative to..."
    > (在 Innova 時，我們面臨 [功能 X] 需求不明確的挑戰，因為合規法規一直在變。我沒有等待最終規格，而是主動...)
    >
    > *   **Action:** "I created a prototype to visualize the workflow for stakeholders..." (我建立了一個原型來向利害關係人視覺化工作流...)
    > *   **Action:** "I facilitated a workshop between the backend and compliance teams to define the API contract early." (我促成了後端與合規團隊的工作坊，提早定義 API 介面。)

### 2. 技術領導力與影響力 (Influencing without Authority)
**情境：** 推動 CI/CD 或 Code Quality。
**履歷連結：** "Drove CI/CD and code quality improvements" (Innova).

*   **Template:**
    > "I noticed that our deployment cycle was slow due to manual testing. I proposed adopting a new CI/CD pipeline, but some team members were hesitant about the learning curve."
    > (我注意到部署週期因手動測試而緩慢。我提議採用新的 CI/CD 流程，但部分成員對學習曲線感到猶豫。)
    >
    > *   **Action:** "To address this, I didn't just enforce the rule. I built a 'paved road' (template) that made adoption easy and held a lunch-and-learn session." (為了並解決這點，我沒有強制執行。我建立了一個「鋪好的路（模板）」讓採用變簡單，並舉辦了分享會。)
    > *   **Result:** "This reduced code review time by X% and eventually became the team standard."

### 3. 失敗與反思 (Failure & Growth)
**情境：** 系統設計錯誤或溝通失誤。

*   **Template:**
    > "Early in the [Project Name], I optimized for [Metric A] but overlooked [Metric B], which caused latency issues at scale."
    > (在 [專案名] 初期，我針對 [指標 A] 進行優化，但忽略了 [指標 B]，導致擴展時出現延遲。)
    >
    > *   **Learning:** "I learned that for infrastructure tools, reliability must take precedence over feature speed. Now, I always start with a design doc reviewing SLAs before coding." (我學到對於基礎設施工具，可靠性必須優於功能開發速度。現在，我在寫 code 前一定先寫設計文件並檢視 SLA。)

---

## Signals for interviewers｜要讓面試官看到的訊號

若你照著上述策略準備，面試官會在你的回答中捕捉到以下 **L5 (Senior)** 等級的訊號：

1.  **Navigating Ambiguity (駕馭模糊)**：
    *   訊號：你不怕沒有說明書。你會主動找人、找資源、定義路徑。
    *   *Evidence:* 你在 Innova 處理 FDA 合規變更的故事。
2.  **Ownership (當責)**：
    *   訊號：你把產品的問題當作自己的問題，而不只是 Jira 上的一張票。
    *   *Evidence:* 你主動推動 CI/CD 改善，而不是老闆叫你做才做。
3.  **Scalable Leadership (可擴展的領導力)**：
    *   訊號：你透過工具、文件、自動化來幫助團隊，而不只是自己埋頭苦幹。
    *   *Evidence:* "Leveraged AI-assisted development" 來提升團隊效率。
4.  **Cross-functional Empathy (跨職能同理心)**：
    *   訊號：你理解硬體/維運團隊的痛點（JD 提到 "Keep the Google test fleet in perfect shape"）。
    *   *Evidence:* 你在 Chunghwa Telecom 與政府/跨部門合作的經驗。

---

## Common pitfalls｜常見錯誤與避免方式

1.  **The "Manager" Trap (經理陷阱)**：
    *   *錯誤：* 以為 Leadership 就是「分配工作」或「管理時程」。
    *   *修正：* Google 定義的 Technical Leadership 是「親手解決複雜技術難題並帶動他人」。要強調你參與了 Architecture Review，你寫了核心程式碼，同時指導了他人。
2.  **Too specific on Tech, vague on People (技術太細，人際太空)**：
    *   *錯誤：* 花 5 分鐘講 MongoDB 的 index 細節，卻只花 10 秒講如何說服團隊使用它。
    *   *修正：* 在行為面試中，技術只是背景。重點是「人」與「決策過程」。
3.  **Ignoring the "Why" (忽略初衷)**：
    *   *錯誤：* "I implemented X because it's a best practice." (太標準化)
    *   *修正：* "I implemented X because our specific bottleneck was Y, and X solved it by..." (展現你的分析能力)。

---

## Checklist｜檢查清單

在面試前，請確認你已準備好：

- [ ] **3 個核心故事**：已準備好 Ambiguity、Leadership、Conflict 三類故事，並能用英文流暢敘述 (STAR 格式)。
- [ ] **數據支持**：故事中的 Result 都有具體的量化指標 (e.g., reduced time by 20%, handled 1M+ requests)。
- [ ] **連結 JD 關鍵字**：練習時，自然地將 "Diagnostic", "Infrastructure", "Automation" 等詞彙融入故事背景中。
- [ ] **失敗的勇氣**：準備好一個真實的失敗案例，並展現出真誠的反省與具體的改進措施（這是 Googleyness 的必考題）。
- [ ] **提問準備**：準備 2-3 個關於團隊文化或 NPI 流程挑戰的問題，展現你對這個職位的深度思考。