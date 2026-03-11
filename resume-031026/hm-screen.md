# 用人主管篩選 / Hiring Manager Screen | Hiring Manager Screen

## 1. 目標與範圍 | Goal & Scope
- **驗證技術深度與廣度**：確認你是否具備履歷上所述的「T 型」技能（前端實作能力 + 雲端架構視野）。
  - **Validate technical depth and breadth**: Confirm you possess the "T-shaped" skills listed on your resume (Frontend execution + Cloud Architecture vision).
- **評估領域專業度**：深入了解你在 Innova Solutions 的醫療影像專案，特別是合規性（FDA 510K）與 GCP 雲端整合。
  - **Assess domain expertise**: Deep dive into your medical imaging projects at Innova Solutions, specifically compliance (FDA 510K) and GCP cloud integration.
- **檢視資深工程師特質**：觀察你是否具備跨部門溝通、流程改進（CI/CD、AI 輔助開發）以及解決複雜問題的能力。
  - **Check for Senior Engineer traits**: Observe if you demonstrate cross-functional communication, process improvement (CI/CD, AI-assisted dev), and complex problem-solving skills.

---

## 2. 簡短開場稿 | Opening Script

### 60 秒電梯簡介（重點摘要） | 60-Second Elevator Pitch (Highlights)
「你好，我是 Ryan。我是一位擁有超過 15 年經驗的資深軟體工程師，專精於建構雲端原生系統。目前我在 Innova Solutions 負責醫療影像平台的開發，這是一個基於 GCP 的高合規性環境。我的核心優勢是『T 型人才』：我既能處理複雜的前端互動（React/TypeScript），也具備 Google 認證的雲端架構師能力（GCP/Java/Spring Boot）。我熱衷於結合技術架構與業務需求，交付高品質、可擴展的解決方案。」

"Hi, I'm Ryan. I am a Senior Software Engineer with over 15 years of experience specializing in building cloud-native systems. Currently, at Innova Solutions, I work on a medical imaging platform within a highly compliant GCP environment. My core strength is being 'T-shaped': I can handle complex frontend interactions (React/TypeScript) while also bringing the expertise of a Google Certified Professional Cloud Architect (GCP/Java/Spring Boot). I am passionate about bridging technical architecture with business needs to deliver high-quality, scalable solutions."

### 3 分鐘完整版（背景脈絡） | 3-Minute Full Version (Context & Journey)
「我的職涯始於大型系統設計，早期在中華電信負責國家級警報系統的架構，這奠定了我對高可用性與系統整合的基礎。

隨後我轉往美國發展，在 USTOSHOP 和 Hiveel 累積了電商與搜尋引擎的實戰經驗。這段期間，我使用 Java Spring Boot 和 ElasticSearch 處理百萬級別的資料索引與高併發 API 設計，同時也深入前端開發。

目前在 Innova Solutions，我擔任資深工程師，專注於 Change Healthcare 的企業級影像共享平台。我的工作涵蓋全端：
1.  **在後端與雲端方面**：我利用 GCP 服務（如 Storage Buckets）自動化客戶引導流程，並維護符合 FDA 510K 規範的產品規格。
2.  **在前端方面**：我負責 UI 在地化（英國/加拿大市場）以及開發複雜的互動功能，如自動化排程報告。
3.  **在流程優化方面**：我推動了 CI/CD 的改進，並導入 AI 輔助開發來提升程式碼審查效率。

我現在正在尋找一個能讓我同時發揮雲端架構思維與全端實作能力的機會。」

"My career began with large-scale system design. Early on at Chunghwa Telecom, I led the architecture for a national-level emergency alert system, which laid my foundation in high availability and system integration.

I then moved to the US, gaining hands-on experience in e-commerce and search engines at USTOSHOP and Hiveel. During this time, I used Java Spring Boot and ElasticSearch to handle million-level data indexing and high-concurrency API design, while also diving deep into frontend development.

Currently, at Innova Solutions, I serve as a Senior Software Engineer focusing on the Change Healthcare Enterprise Imaging Share platform. My work is full-stack:
1.  **On the Backend & Cloud side**: I leverage GCP services (like Storage Buckets) to automate customer onboarding and maintain product specs compliant with FDA 510K regulations.
2.  **On the Frontend side**: I handle UI localization (for UK/Canadian markets) and develop complex interactive features like automated scheduled reporting.
3.  **On Process Optimization**: I drove CI/CD improvements and leveraged AI-assisted development to enhance code review efficiency.

I am now looking for an opportunity where I can apply both my cloud architecture mindset and full-stack implementation skills."

---

## 3. 關鍵故事與成就 | Key Stories & Achievements

### 故事一：醫療影像平台的自動化與合規性 | Story 1: Automation & Compliance in Medical Imaging
- **情境 (Situation)**: 在 Innova，新客戶（醫院/診所）的引導流程涉及手動建立 GCP 資源，且需嚴格符合 FDA 510K 規範。
  - **Situation**: At Innova, onboarding new customers (hospitals/clinics) involved manual GCP resource creation and required strict adherence to FDA 510K regulations.
- **任務 (Task)**: 設計一套機制自動化建立 GCP Storage Buckets，並確保資料分享功能的安全性與合規性。
  - **Task**: Design a mechanism to automate GCP Storage Bucket creation and ensure the security and compliance of data sharing features.
- **行動 (Action)**: 我開發了後端邏輯來觸發 GCP API 自動配置資源，並在前端實作了「Push2Pacs」自動化動作與事件監控介面。
  - **Action**: I developed backend logic to trigger GCP APIs for automatic resource provisioning and implemented "Push2Pacs" automated actions and event monitoring interfaces on the frontend.
- **結果 (Result)**: 大幅縮短新客戶上線時間，減少人為錯誤，並成功支援了產品在英國與加拿大的在地化擴展。
  - **Result**: Significantly reduced new customer onboarding time, minimized human error, and successfully supported product localization expansion in the UK and Canada.

### 故事二：搜尋引擎效能優化 | Story 2: Search Engine Performance Optimization
- **情境 (Situation)**: 在 Hiveel 與 USTOSHOP，面對百萬級別的車輛與商品資料，傳統資料庫查詢速度過慢。
  - **Situation**: At Hiveel and USTOSHOP, traditional database queries were too slow for million-level vehicle and product datasets.
- **任務 (Task)**: 提升搜尋精準度與回應速度，支援全文檢索與多欄位查詢。
  - **Task**: Improve search accuracy and response speed, supporting full-text and multi-field queries.
- **行動 (Action)**: 導入 ElasticSearch 建立索引，並使用 Spring Boot/MyBatis 優化 API 層；針對資料庫 Schema 進行正規化設計。
  - **Action**: Implemented ElasticSearch for indexing and optimized the API layer using Spring Boot/MyBatis; designed normalized database schemas.
- **結果 (Result)**: 實現了毫秒級的搜尋回應，並支援了複雜的地理位置（Proximity）查詢功能。
  - **Result**: Achieved millisecond-level search responses and supported complex proximity query features.

### 故事三：工程效能與 AI 導入 | Story 3: Engineering Efficiency & AI Adoption
- **情境 (Situation)**: 團隊在程式碼審查與交付速度上遇到瓶頸。
  - **Situation**: The team faced bottlenecks in code reviews and delivery velocity.
- **行動 (Action)**: 我主動推動 CI/CD 流程改進，並在開發流程中導入 AI 輔助工具進行重構與初步審查。
  - **Action**: I proactively drove CI/CD process improvements and introduced AI-assisted tools into the development workflow for refactoring and preliminary reviews.
- **結果 (Result)**: 減少了 Code Review 的來回時間，提升了整體交付速度 (Delivery Velocity)。
  - **Result**: Reduced back-and-forth time in code reviews and increased overall delivery velocity.

---

## 4. 常見追問與應對 | Likely Follow‑ups & Responses

### Q1: 你同時做前端與後端，你更偏好哪一邊？
### Q1: You do both frontend and backend. Which do you prefer?
- **回答角度**: 強調「解決問題」而非選邊站。
  - **Response Angle**: Emphasize "problem-solving" rather than picking a side.
- **建議回答**: 「我將自己定位為 T 型工程師。雖然我近期在 React 前端投入很多，但我擁有 Google Cloud Architect 認證與深厚的 Java 後端背景。我喜歡能讓我從『系統設計』到『用戶體驗』端到端負責的角色，這讓我能做出更全面的技術決策。」
  - **Suggested Answer**: "I position myself as a T-shaped engineer. While I've invested heavily in React frontend recently, I hold a Google Cloud Architect certification and have a strong Java backend background. I enjoy roles that allow me to own features end-to-end—from system design to user experience—as it enables me to make more holistic technical decisions."

### Q2: 在受監管產業（醫療）開發軟體，最大的挑戰是什麼？
### Q2: What is the biggest challenge developing software in a regulated industry (Healthcare)?
- **回答角度**: 合規性 vs. 開發速度的平衡。
  - **Response Angle**: Balancing compliance vs. development velocity.
- **建議回答**: 「最大的挑戰是在維持敏捷開發速度的同時，確保符合 FDA 510K 與 HIPAA 等規範。例如，任何功能變更都需要更新設計規範文件（Product Area Design Specification）。我的應對方式是將合規檢查整合進 CI/CD 與自動化測試中，確保安全性不成為事後補救。」
  - **Suggested Answer**: "The biggest challenge is maintaining agile development velocity while ensuring compliance with regulations like FDA 510K and HIPAA. For example, any feature change requires updating the Product Area Design Specification. I address this by integrating compliance checks into CI/CD and automated testing, ensuring security isn't an afterthought."

---

## 5. 技術深挖提示（如適用） | Technical Deep‑Dive Prompts (if relevant)

面試官可能會針對你的「T 型」技能進行技術抽查：
The interviewer might spot-check your "T-shaped" skills:

1.  **雲端與架構 (Cloud & Architecture)**:
    -   *Prompt*: "How did you design the GCP Storage Bucket auto-creation? How do you handle permissions?"
    -   *Key Points*: Service Accounts, IAM roles, Event-driven architecture (e.g., Cloud Functions or Pub/Sub triggers), Audit logs.
2.  **前端複雜度 (Frontend Complexity)**:
    -   *Prompt*: "Tell me about the UI Localization challenges for UK/Canada."
    -   *Key Points*: i18n libraries, handling date/time formats, dynamic content replacement, ensuring layout doesn't break with longer text.
3.  **資料庫設計 (DB Design)**:
    -   *Prompt*: "Compare your experience with MongoDB vs. MySQL/SQL Server."
    -   *Key Points*: Schema design (Flexible vs. Rigid), ACID compliance needs (Crucial for payment/healthcare), Scaling strategies.

---

## 6. 常見陷阱與糾正 | Pitfalls & Corrections

-   **陷阱 (Pitfall)**: 過度強調「維護 (Maintained)」而忽略「創造 (Created)」。
    -   *Correction*: 履歷上有許多 "Maintained"，但在口語中要強調你在維護過程中做的**優化 (Optimizations)** 或 **新功能開發 (New Features)**（如 Push2Pacs, Auto-creation）。
    -   *Correction*: Your resume says "Maintained" a lot, but verbally emphasize the **optimizations** or **new features** you built during maintenance (e.g., Push2Pacs, Auto-creation).
-   **陷阱 (Pitfall)**: 講述技術細節時忘記提及業務影響（Business Impact）。
    -   *Correction*: 不要只說「我用了 ElasticSearch」，要說「我用了 ElasticSearch 讓搜尋速度從數秒降至毫秒級，提升了用戶留存」。
    -   *Correction*: Don't just say "I used ElasticSearch." Say "I used ElasticSearch to reduce search time from seconds to milliseconds, improving user retention."
-   **陷阱 (Pitfall)**: 被認為技術過於分散（Generalist）而不夠專精。
    -   *Correction*: 利用 Google Cloud Architect 認證作為你技術深度的背書，證明你在架構層面有系統性的理解。
    -   *Correction*: Use your Google Cloud Architect certification as proof of your technical depth, demonstrating a systematic understanding at the architectural level.

---

## 7. 收尾與反問 | Closing & Questions for Interviewer

### 收尾句 | Closing Statement
「總結來說，我具備醫療領域的嚴謹開發紀律，結合了雲端架構師的視野與全端工程師的實作力。我有信心能協助貴團隊解決複雜的技術挑戰。」
"In summary, I bring the disciplined development approach of the healthcare domain, combined with the vision of a Cloud Architect and the execution skills of a Full Stack Engineer. I am confident I can help your team tackle complex technical challenges."

### 建議提問 | Suggested Questions
1.  **關於團隊結構**: "Can you describe the composition of the team? How do frontend, backend, and DevOps engineers collaborate?" (展現你對跨部門合作的重視)
2.  **關於技術挑戰**: "What is the most significant technical challenge the team is currently facing regarding cloud scalability or frontend performance?" (展現你的 T 型技能興趣)
3.  **關於成功指標**: "What would a successful first 90 days look like for someone in this role?" (展現積極度)