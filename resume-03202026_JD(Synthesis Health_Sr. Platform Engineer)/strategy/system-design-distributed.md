# 分散式系統設計與效能優化 / Distributed System Design & Performance Tuning

## Why this matters｜為什麼這個主題重要

**1. Platform Engineering vs. App Development**
The JD specifically asks for a "Sr. Platform Engineer" who can "identify performance bottlenecks" and "improve system architecture." Unlike typical application development, this role requires you to look "under the hood."
JD 特別徵求「資深平台工程師」來「識別效能瓶頸」與「改進系統架構」。不同於一般的應用開發，這個職位要求你必須具備「掀開引擎蓋」看底層運作的能力。

**2. The "Healthcare Data" Factor**
You are dealing with medical imaging (Innova experience) and healthcare data. These involve large payloads (DICOM) and strict consistency requirements. Standard web app scaling strategies often fail here.
你過去在 Innova 的醫療影像經驗是關鍵。醫療數據通常涉及巨大的檔案（DICOM）與嚴格的一致性要求，一般的 Web App 擴展策略在這裡往往行不通，你需要展現針對此領域的特殊設計思維。

**3. Bridging the "GCP Cert" to "Reality"**
You hold a Google Professional Cloud Architect certification. Interviewers will test if you only know the *theory* (exam answers) or if you can apply it to *messy, real-world problems* (race conditions, latency, cost optimization).
你擁有 Google 雲端架構師證照。面試官會測試你是否只懂「理論」（考試答案），還是能將其應用於「混亂的現實問題」（如競爭條件、延遲、成本優化）。

---

## Step‑by‑step strategy｜具體行動步驟

### Week 1: Audit & Retrofit (盤點與重構)
*   **Deep Dive into Innova Projects:**
    Review your work at Innova Solutions. Identify one specific bottleneck you solved. Did the "GCP Storage Bucket Auto-Creation" ever fail? How did you handle retries?
    **回顧 Innova 專案：** 深入檢視你在 Innova 的工作。找出一個你解決過的具體瓶頸。例如那個「GCP Storage Bucket 自動建立」的功能曾經失敗過嗎？你如何處理重試機制？
*   **Rewrite Resume Bullets:**
    Update your resume to highlight *metrics* and *architecture*.
    **改寫履歷重點：** 更新履歷，強調「數據指標」與「架構決策」。
    *   *Before:* "Designed and developed features for Imaging Share..."
    *   *After:* "Architected an event-driven ingestion pipeline on GCP to process high-volume DICOM metadata, reducing retrieval latency by 40%."

### Week 2: Knowledge Gap Filling (填補知識缺口)
*   **GCP Pub/Sub & Event-Driven Patterns:**
    The JD explicitly mentions "GCP Pub/Sub" and "Kafka." Since you have the GCP cert, review the specific patterns: Fan-out, Dead Letter Queues, and Ordering keys.
    **GCP Pub/Sub 與事件驅動模式：** JD 明確提到 Pub/Sub 和 Kafka。既然你有 GCP 證照，請複習特定模式：扇出（Fan-out）、死信隊列（DLQ）與排序鍵（Ordering keys）。
*   **Observability Stack:**
    Platform engineers live in dashboards. Familiarize yourself with OpenTelemetry, Prometheus, or Google Cloud Monitoring concepts. How do you trace a request across microservices?
    **可觀測性技術棧：** 平台工程師靠儀表板生存。熟悉 OpenTelemetry、Prometheus 或 Google Cloud Monitoring 的概念。你如何在微服務之間追蹤一個請求？

### Week 3: System Design Drills (系統設計演練)
*   **Practice "Healthcare Platform" Scenarios:**
    Don't just practice "Design Twitter." Practice "Design a scalable Medical Imaging Storage System."
    **練習「醫療平台」場景：** 不要只練習「設計 Twitter」。請練習「設計一個可擴展的醫療影像儲存系統」。
    *   *Key Constraints:* HIPAA compliance (encryption at rest/transit), large file handling (CDN/Signed URLs), high availability.
    *   *關鍵限制：* HIPAA 合規（靜態/傳輸加密）、大檔案處理（CDN/簽名 URL）、高可用性。

### Week 4: Mock Interview Prep (模擬面試準備)
*   **Prepare the "War Story":**
    Script a 2-minute story about a time a distributed system failed. What broke? How did you debug it? What did you fix permanently?
    **準備「戰場故事」：** 寫下一個 2 分鐘的故事，描述一次分散式系統崩潰的經歷。哪裡壞了？你如何除錯？你最後如何永久修復它？

---

## Examples & templates｜範例與句型

### Resume Bullet Rewrite (履歷改寫範本)
*   **Original (Innova):** "Maintained a cloud-native medical imaging platform..."
*   **Optimized:** "Scaled a cloud-native medical imaging platform on **GCP (GKE)**, optimizing **microservices communication** to handle concurrent DICOM uploads with **99.9% availability**."
*   **Why:** Adds specific tech (GKE), problem (concurrency), and metric (availability).
*   **理由：** 加入了具體技術（GKE）、問題（並發）與指標（可用性）。

### Interview "STAR" Response Template (面試回答句型)
*   **Situation:** "At Innova, we faced a bottleneck where large imaging datasets caused timeouts in our monolithic API..."
    （在 Innova，我們面臨一個瓶頸，大型影像資料集導致我們的單體 API 逾時...）
*   **Task:** "We needed to decouple the upload process from the processing logic to improve user experience."
    （我們需要將上傳流程與處理邏輯解耦，以改善使用者體驗。）
*   **Action:** "I introduced an **event-driven architecture using GCP Pub/Sub**. When a file landed in the bucket, it triggered a Cloud Function event, allowing the backend to process metadata asynchronously."
    （我引入了使用 **GCP Pub/Sub 的事件驅動架構**。當檔案進入 Bucket 時，會觸發 Cloud Function 事件，讓後端能非同步處理詮釋資料。）
*   **Result:** "This reduced API latency from 5 seconds to 200ms and allowed us to scale processing workers independently."
    （這將 API 延遲從 5 秒降至 200 毫秒，並允許我們獨立擴展處理用的 Worker。）

### Questions to Ask the Interviewer (反問面試官的問題)
*   "I noticed you use AlloyDB. Are you using it primarily for transactional consistency for patient records, and how do you handle read-replicas for analytics?"
    （我注意到你們使用 AlloyDB。你們主要是為了病歷的事務一致性而使用它嗎？你們如何處理分析用的讀取副本？）
*   "Regarding observability, are you currently using distributed tracing to identify latency bottlenecks across your microservices?"
    （關於可觀測性，你們目前是否有使用分散式追蹤來識別微服務之間的延遲瓶頸？）

---

## Signals for interviewers｜要讓面試官看到的訊號

**1. You measure before you optimize (先測量，再優化)**
*   *Signal:* You don't guess where the bug is. You talk about metrics, logs, and tracing.
*   *訊號：* 你不瞎猜 Bug 在哪。你會談論指標（Metrics）、日誌（Logs）和追蹤（Tracing）。

**2. You understand Trade-offs (你懂權衡)**
*   *Signal:* You acknowledge that "Eventual Consistency" is okay for a search index (ElasticSearch) but NOT okay for a patient's diagnosis record.
*   *訊號：* 你承認「最終一致性」對搜尋索引（ElasticSearch）是可以接受的，但對病人的診斷紀錄則是**不可接受**的。

**3. You are "Cloud-Native" Native (你是真正的雲原生專家)**
*   *Signal:* You discuss "Infrastructure as Code" (Terraform/Helm) and "Container Orchestration" (K8s) naturally, not just as buzzwords.
*   *訊號：* 你能自然地討論「基礎設施即程式碼」與「容器編排」，而不只是把它們當作流行術語。

---

## Common pitfalls｜常見錯誤與避免方式

**1. Over-Engineering (過度設計)**
*   *Mistake:* Suggesting a complex Kafka setup for a simple problem that a cron job or a simple queue could solve.
*   *Correction:* Always start simple. "We could start with a simple Cloud Task, but if volume grows beyond X, we should migrate to Pub/Sub."
*   *錯誤：* 針對簡單問題建議複雜的 Kafka 架構。
*   *修正：* 總是從簡單開始。「我們可以先用 Cloud Task，但如果量級超過 X，我們就遷移到 Pub/Sub。」

**2. Ignoring Failure Modes (忽略故障模式)**
*   *Mistake:* Designing a system that assumes the database is always up and the network is always fast.
*   *Correction:* Explicitly mention: "What happens if the consumer service is down? The messages should go to a Dead Letter Queue for manual inspection."
*   *錯誤：* 設計系統時假設資料庫永遠在線、網路永遠很快。
*   *修正：* 明確提到：「如果消費者服務掛了怎麼辦？訊息應該進入死信隊列（DLQ）以供人工檢查。」

**3. Confusing "Feature" with "Platform" (混淆「功能」與「平台」)**
*   *Mistake:* Focusing too much on the UI/UX of the feature.
*   *Correction:* Focus on the *plumbing*. How is the data moved? How is it secured? How is it monitored?
*   *錯誤：* 過度專注於功能的 UI/UX。
*   *修正：* 專注於「管線」。資料如何移動？如何確保安全？如何監控？

---

## Checklist｜檢查清單

- [ ] **Resume Update:** Have I added "GCP Pub/Sub," "Microservices," and "Performance Tuning" to my Innova experience bullets? (履歷更新：我是否將這些關鍵字加入 Innova 的經歷中？)
- [ ] **Story Prep:** Do I have one solid example of debugging a slow system using tools/logs? (故事準備：我是否準備好一個使用工具/日誌除錯慢速系統的具體案例？)
- [ ] **Concept Review:** Can I explain the difference between "Throughput" and "Latency" in the context of API design? (觀念複習：我能否解釋 API 設計中「吞吐量」與「延遲」的差異？)
- [ ] **Healthcare Context:** Do I have an answer for how to handle PII/PHI (Patient Data) in logs? (Hint: Don't log it!) (醫療情境：我知道如何在日誌中處理病人個資嗎？提示：別記錄它！)