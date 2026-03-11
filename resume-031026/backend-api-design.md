# 後端與 API 設計 / Backend & API Design | Backend & API Design

## 1. 目標與範圍 | Goal & Scope
- 展示您在 Java Spring Boot 與 Node.js/Express 雙棲的後端開發能力。 | Demonstrate your versatility in backend development using both Java Spring Boot and Node.js/Express.
- 強調 RESTful API 設計原則、資料庫互動（SQL/NoSQL）與安全性實作（OAuth, RSA, FDA 合規）。 | Emphasize RESTful API design principles, database interactions (SQL/NoSQL), and security implementations (OAuth, RSA, FDA compliance).
- 證明您具備處理高併發（搜尋引擎、緊急警報系統）與複雜業務邏輯（醫療、支付）的架構經驗。 | Prove your architectural experience in handling high concurrency (search engines, emergency alerts) and complex business logic (healthcare, payments).

## 2. 簡短開場稿 | Opening Script

**60秒電梯簡介 (Elevator Pitch):**
「我有超過 15 年的軟體工程經驗，其中 10 年專注於雲端原生系統。我的後端專長是『混合型』的——我精通 **Java Spring Boot** 處理嚴謹的企業級交易（如我在 Innova 的醫療影像平台與 Hiveel 的車輛交易系統），同時也擅長使用 **Node.js** 構建高靈活度的 API 與微服務（如 USTOSHOP 的電商後端）。我曾設計過支撐數百萬筆商品索引的搜尋系統，也處理過國家級的緊急警報平台，因此我非常熟悉如何在**高併發**與**高安全性**（如 FDA 合規）之間取得平衡。」

"I have over 15 years of software engineering experience, with 10+ years focused on cloud-native systems. My backend expertise is 'hybrid'—I am proficient in **Java Spring Boot** for strict enterprise transactions (such as my work on the medical imaging platform at Innova and the vehicle trading system at Hiveel), and I also excel at using **Node.js** to build flexible APIs and microservices (like the eCommerce backend at USTOSHOP). I have designed search systems supporting millions of product indexes and handled national-level emergency alert platforms, so I am very familiar with balancing **high concurrency** with **high security** (such as FDA compliance)."

## 3. 關鍵故事與成就 | Key Stories & Achievements

**故事一：雙語言後端架構與搜尋優化 (Node.js + Java)**
**Story 1: Polyglot Backend Architecture & Search Optimization**
- **情境 (Situation):** 在 USTOSHOP，我們需要處理數百萬件商品的搜尋與電商交易流程。 | At USTOSHOP, we needed to handle search and eCommerce transactions for millions of products.
- **任務 (Task):** 建立高效能的後端 API 以支援全文檢索與即時交易。 | Build high-performance backend APIs to support full-text search and real-time transactions.
- **行動 (Action):** 我採用混合架構，使用 **Node.js** 處理輕量級 I/O 請求，並結合 **Java Spring Boot** 處理複雜業務邏輯；同時實作 **ElasticSearch** 索引以支援多欄位與鄰近查詢 (proximity queries)。 | I adopted a hybrid architecture, using **Node.js** for lightweight I/O requests combined with **Java Spring Boot** for complex business logic; I also implemented **ElasticSearch** indexing to support multi-field and proximity queries.
- **結果 (Result):** 成功實現了數百萬商品的秒級搜尋回應，並整合了 PayPal 與加密貨幣錢包（含 RSA 簽章）的支付功能。 | Successfully achieved sub-second search responses for millions of products and integrated payment features for PayPal and crypto wallets (including RSA signatures).

**故事二：高可靠性 REST API 與 TDD 實踐 (Java Spring Boot)**
**Story 2: High-Reliability REST API & TDD Practice**
- **情境 (Situation):** 在 Hiveel，車輛搜尋引擎的後端需要極高的穩定性與準確的資料檢索。 | At Hiveel, the vehicle search engine backend required extreme stability and accurate data retrieval.
- **任務 (Task):** 設計標準化的 RESTful API 並優化資料庫效能。 | Design standardized RESTful APIs and optimize database performance.
- **行動 (Action):** 我使用 Spring Boot 與 MyBatis 設計 API，並引入 **JUnit5 + H2** 進行測試驅動開發 (TDD)，確保每個端點的輸入輸出皆符合預期。 | I designed APIs using Spring Boot and MyBatis, and introduced **Test-Driven Development (TDD)** with JUnit5 + H2 to ensure every endpoint's input/output met expectations.
- **結果 (Result):** 透過優化 SQL 查詢與索引，顯著提升了後端效能，並透過嚴格的測試減少了線上錯誤。 | Significantly improved backend performance through optimized SQL queries and indexing, and reduced production bugs through rigorous testing.

**故事三：醫療合規與自動化排程 (GCP + Backend Logic)**
**Story 3: Healthcare Compliance & Automated Scheduling**
- **情境 (Situation):** 在 Innova，我們需要處理敏感的醫療影像分享與稽核報告，必須符合 FDA 規範。 | At Innova, we handled sensitive medical image sharing and audit reports, requiring FDA compliance.
- **任務 (Task):** 設計自動化機制來處理客戶稽核報告與儲存桶 (Bucket) 管理。 | Design automated mechanisms to handle customer audit reports and storage bucket management.
- **行動 (Action):** 我開發了後端排程機制 (Scheduling mechanism) 自動生成稽核報告，並實作了 GCP Storage Bucket 的自動建立功能，確保資料隔離與安全性。 | I developed a backend scheduling mechanism to automatically generate audit reports and implemented auto-creation for GCP Storage Buckets to ensure data isolation and security.
- **結果 (Result):** 確保了系統符合 FDA 510K 設計規範，並自動化了繁瑣的手動流程。 | Ensured the system met FDA 510K design specifications and automated tedious manual processes.

## 4. 常見追問與應對 | Likely Follow‑ups & Responses

**Q1: 你如何選擇 Node.js 與 Java Spring Boot？兩者有何優缺點？**
**Q1: How do you choose between Node.js and Java Spring Boot? What are the pros and cons?**
- **回答角度:** 強調「工具適配性」。Java 適合運算密集、強型別約束、大型企業級應用（如 Innova/Hiveel）；Node.js 適合 I/O 密集、高併發連線、快速原型開發（如 USTOSHOP 前台 API）。
- **Response Strategy:** Emphasize "right tool for the job." Java is best for CPU-intensive tasks, strong typing constraints, and large enterprise apps (e.g., Innova/Hiveel); Node.js excels at I/O-intensive tasks, high concurrency connections, and rapid prototyping (e.g., USTOSHOP frontend APIs).

**Q2: 在設計 REST API 時，你如何處理版本控制與向後相容性？**
**Q2: How do you handle versioning and backward compatibility when designing REST APIs?**
- **回答角度:** 提及在 URL 中使用版本號 (e.g., `/api/v1/resource`) 或使用 Header 版本控制。在 Hiveel 與 Innova 的經驗中，我會避免對現有欄位進行破壞性修改 (Breaking Changes)，而是新增欄位或端點。
- **Response Strategy:** Mention using version numbers in the URL (e.g., `/api/v1/resource`) or Header versioning. In my experience at Hiveel and Innova, I avoid breaking changes to existing fields, preferring to add new fields or endpoints instead.

**Q3: 你如何確保 API 的安全性，特別是在涉及支付或醫療資料時？**
**Q3: How do you ensure API security, especially involving payments or healthcare data?**
- **回答角度:** 提及 **HTTPS/TLS** 傳輸加密、**OAuth2/JWT** 身份驗證。舉例 USTOSHOP 的 **RSA 簽章**驗證加密貨幣交易，以及 Innova 的 **FDA 合規**存取控制與稽核日誌 (Audit Logs)。
- **Response Strategy:** Mention **HTTPS/TLS** for encryption and **OAuth2/JWT** for authentication. Cite the **RSA signature** verification for crypto transactions at USTOSHOP, and **FDA-compliant** access controls and audit logs at Innova.

**Q4: 面對高流量（如中華電信的警報系統或 USTOSHOP 搜尋），你如何設計架構？**
**Q4: How do you architect for high traffic (like Chunghwa Telecom's alert system or USTOSHOP search)?**
- **回答角度:** 提及 **Caching (Redis)** 減少資料庫負載、**非同步處理 (Message Queues)** 解耦耗時任務、以及資料庫讀寫分離或分片 (Sharding)。
- **Response Strategy:** Mention **Caching (Redis)** to reduce DB load, **Asynchronous Processing (Message Queues)** to decouple time-consuming tasks, and database read/write splitting or sharding.

## 5. 技術深挖提示 | Technical Deep‑Dive Prompts

**主題 A: 資料庫設計與 ORM (Database Design & ORM)**
- **預期問題:** MyBatis (Hiveel) 與 Hibernate/JPA 的差異？為何選擇 EER diagrams 建模？
- **Expected Question:** Difference between MyBatis (Hiveel) and Hibernate/JPA? Why model with EER diagrams?
- **準備:** 解釋 MyBatis 提供對 SQL 的精細控制（適合複雜查詢優化），而 JPA 適合標準 CRUD。強調 EER 圖在與 UI/PM 確認需求時的重要性。
- **Prep:** Explain MyBatis offers fine-grained SQL control (good for complex query optimization), while JPA is good for standard CRUD. Emphasize the importance of EER diagrams for validating requirements with UI/PM.

**主題 B: 搜尋引擎實作 (Search Engine Implementation)**
- **預期問題:** ElasticSearch 的倒排索引 (Inverted Index) 原理？如何處理資料同步？
- **Expected Question:** How does ElasticSearch's Inverted Index work? How do you handle data synchronization?
- **準備:** 描述在 USTOSHOP 如何將 SQL 資料同步到 ElasticSearch（Logstash 或應用層雙寫），以及如何設計 Mapping 來支援模糊搜尋。
- **Prep:** Describe how you synced SQL data to ElasticSearch at USTOSHOP (Logstash or application-layer dual writes), and how you designed Mappings to support fuzzy search.

**主題 C: 驗證與授權 (Authentication & Authorization)**
- **預期問題:** Session vs. Token (JWT)？如何處理 Token 失效？
- **Expected Question:** Session vs. Token (JWT)? How to handle token revocation?
- **準備:** 比較有狀態 (Stateful) 與無狀態 (Stateless) 的優劣。在雲端原生環境 (Innova GCP) 中，JWT 更適合微服務擴展。
- **Prep:** Compare Stateful vs. Stateless pros/cons. In a cloud-native environment (Innova GCP), JWT is better suited for microservices scaling.

## 6. 常見陷阱與糾正 | Pitfalls & Corrections

- **陷阱 (Pitfall):** 過度強調框架 (Framework)，忽略底層原理 (Fundamentals)。
- **糾正 (Correction):** 不要只說「我用了 Spring Boot」，要解釋「我利用 Spring Boot 的依賴注入 (DI) 和 AOP 來解耦業務邏輯與橫切關注點（如 Logging/Security）」。
- **Better Phrasing:** Don't just say "I used Spring Boot"; explain "I leveraged Spring Boot's Dependency Injection (DI) and AOP to decouple business logic from cross-cutting concerns like logging and security."

- **陷阱 (Pitfall):** 忽略錯誤處理 (Error Handling) 的重要性。
- **糾正 (Correction):** 在 API 設計中，明確定義 HTTP 狀態碼（200, 400, 401, 500）與統一的錯誤訊息結構，這對前端整合與除錯至關重要。
- **Better Phrasing:** In API design, explicitly define HTTP status codes (200, 400, 401, 500) and a unified error message structure, which is crucial for frontend integration and debugging.

## 7. 收尾與反問 | Closing & Questions for Interviewer

**收尾總結 (Closing Recap):**
「總結來說，我具備從底層資料庫設計 (MySQL/MongoDB) 到上層 API 實作 (Java/Node.js) 的完整後端能力。無論是追求極致效能的搜尋引擎，還是講求絕對安全的醫療系統，我都有實戰經驗能確保系統既可擴展又合規。」
"In summary, I possess end-to-end backend capabilities, from low-level database design (MySQL/MongoDB) to high-level API implementation (Java/Node.js). Whether it's a search engine demanding extreme performance or a healthcare system requiring absolute security, I have the hands-on experience to ensure the system is both scalable and compliant."

**建議提問 (Questions to Ask):**
1. 「貴團隊目前在後端面臨最大的效能瓶頸或擴展挑戰是什麼？」
   "What is the biggest performance bottleneck or scaling challenge your backend team is currently facing?"
2. 「考慮到我的雙語言背景，貴公司目前的技術棧是更傾向於統一語言，還是鼓勵針對不同服務選擇最適合的工具？」
   "Given my polyglot background, does your current tech stack lean towards a unified language, or do you encourage choosing the best tool for each specific service?"
3. 「在 API 設計流程中，開發團隊如何與前端或行動端團隊協作定義合約 (Contract)？」
   "In your API design process, how does the development team collaborate with frontend or mobile teams to define the API contracts?"