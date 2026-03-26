# 技術堆疊橋接 (Java/TS to Go/Rust) / Bridging the Tech Stack Gap

## Why this matters｜為什麼這個主題重要

**1. Platform Engineering is dominated by Go/Rust**
**平台工程領域由 Go/Rust 主導**
雖然 JD 提到 Java 和 TypeScript，但 "Sr. Platform Engineer" 的職位通常涉及 Kubernetes、Terraform 或高效能微服務，這些生態系高度依賴 Go。若團隊核心基礎設施是用 Go 寫的，他們需要確認你能在入職後迅速上手，而不是只會寫 Java Spring Boot。
While the JD lists Java and TypeScript, "Sr. Platform Engineer" roles often revolve around Kubernetes, Terraform, or high-performance microservices—ecosystems dominated by Go. If the team's core infrastructure is in Go, they need assurance you can ramp up immediately, rather than being stuck in "Java Spring Boot mode."

**2. Proving "Polyglot" capability reduces hiring risk**
**證明「多語言能力」能降低招聘風險**
JD 明確列出了 `TypeScript, Go, C/C++, Java, Rust`。這暗示該公司可能正在進行技術轉型，或者針對不同場景使用不同語言。如果你能展現「我精通語言設計原理，換個語法只需一週」，你將比單純的「Java 專家」更具吸引力。
The JD explicitly lists `TypeScript, Go, C/C++, Java, Rust`. This implies the company might be transitioning stacks or using the right tool for the job. Proving you understand *language design principles* (and can switch syntax in a week) makes you far more attractive than a "Java Specialist."

**3. Leveraging your C++ background**
**利用你的 C++ 背景作為橋樑**
你的履歷上有 C++ 經驗。這是學習 Rust（記憶體管理）或 Go（指標與效能）的絕佳基石。強調這一點可以消除面試官對你「只懂高階垃圾回收語言 (Java/JS/Python)」的疑慮。
Your resume shows C++ experience. This is a perfect foundation for Rust (memory management) or Go (pointers & performance). Highlighting this removes the fear that you only know high-level, garbage-collected languages like Java/JS/Python.

---

## Step‑by‑step strategy｜具體行動步驟

### Week 1: Concept Mapping & Syntax Crash Course (概念對齊與語法速成)
*   **Action:** 不要從頭學起，而是建立「對照表」。
    *   **Java vs. Go:** 比較 `Thread` vs. `Goroutine`，`Interface` (Explicit) vs. `Interface` (Implicit/Duck typing)，`Exception` vs. `Error handling`。
    *   **Java vs. Rust:** 比較 `Garbage Collection` vs. `Ownership/Borrowing`。
*   **Goal:** 在面試中能說出：「雖然我主要寫 Java，但我知道 Go 的併發模型更輕量，適合高吞吐量的平台服務。」
    *   *Goal: To be able to say, "While I primarily write Java, I understand Go's concurrency model is more lightweight, making it ideal for high-throughput platform services."*

### Week 2: Build a "Tiny" Cloud-Native Tool (實作微型雲原生工具)
*   **Action:** 利用你的 GCP 架構師背景，用 Go 寫一個簡單的 CLI 工具。
    *   題目建議：一個讀取 GCP Pub/Sub 並將訊息寫入 Local File 或 Log 的小程式（呼應 JD 的 Pub/Sub 需求）。
    *   *Project Idea: A small CLI that reads from GCP Pub/Sub and writes to a local file/log (aligning with the JD's Pub/Sub requirement).*
*   **Why:** 這證明你已經準備好進入他們的技術棧，而不僅僅是嘴上說說。

### Week 3: Resume & Narrative Refinement (履歷與敘事優化)
*   **Action:** 在履歷的 Skills 區塊或 Summary 中，加入 "Polyglot Mindset" 的關鍵字。
*   **Action:** 準備一個「學習新技術」的故事。回想你過去如何從 C++ 轉到 Java，或從 Java 轉到 Node.js。
    *   *Action: Prepare a "Learning Agility" story. Recall how you transitioned from C++ to Java, or Java to Node.js previously.*

### Week 4: System Design with Language Trade-offs (系統設計中的語言取捨)
*   **Action:** 在準備系統設計面試時，主動討論語言選擇。
    *   例如：「對於這個支付服務，我們可以用 Java 因為它的生態系成熟；但對於這個 Sidecar Proxy，我建議用 Go 或 Rust，因為啟動速度快且記憶體佔用低。」
    *   *E.g., "For this payment service, Java is great for its ecosystem; but for this Sidecar Proxy, I'd suggest Go or Rust due to faster cold starts and lower memory footprint."*

---

## Examples & templates｜範例與句型

### 1. Resume Bullet Points (履歷修改建議)
*   **Current:** Languages: TypeScript/JavaScript... Java... C++...
*   **Proposed (Add a "Learning/Polyglot" angle):**
    *   "Polyglot Engineer with deep expertise in Java/TypeScript and foundational knowledge of Go/Rust for cloud-native tooling."
    *   "Leveraged C++ background to rapidly prototype high-performance modules, demonstrating readiness to adopt Go/Rust for platform-level services."
    *   "Designed distributed systems on GCP, selecting appropriate tech stacks (Java for business logic, evaluating Go for infrastructure agents) based on performance requirements."

### 2. Interview Q&A Script (面試問答腳本)

**Q: We use Go heavily here. You seem to be a Java/TS guy. Are you comfortable switching?**
**問：我們這裡大量使用 Go。你看起來主要是做 Java/TS。你願意轉換嗎？**

*   **Bad Answer:** "I haven't used Go much, but I can learn." (Too passive / 太被動)
*   **Winning Answer:**
    "Absolutely. I view languages as tools to solve specific problems.
    Coming from a background that includes **C++ (manual memory management)** and **Java (concurrency patterns)**, I find the transition to Go very natural.
    In fact, I recently built a small **GCP Pub/Sub consumer in Go** to familiarize myself with its channel patterns and error handling. I appreciate Go's simplicity for platform engineering tasks compared to the JVM's overhead. I’m confident I can be productive in your stack within the first two weeks."
    (強調 C++ 基礎 + 實際動手做的經驗 + 對 Go 適用場景的理解)

### 3. Technical Analogy (技術類比 - 用於展示深度)
*   "I understand that moving from Java to Go means shifting from a 'Thread-per-request' model to a 'Goroutine' model. This is crucial for the **scalability** required in the platform services mentioned in your JD."
    「我理解從 Java 轉向 Go 意味著從『每個請求一個執行緒』轉向『Goroutine』模型。這對於貴公司 JD 中提到的平台服務所需的**擴展性**至關重要。」

---

## Signals for interviewers｜要讓面試官看到的訊號

若你照著上述策略準備，面試官會接收到以下訊號：

1.  **Fundamental Strength (基礎紮實):** 你不只是會背 API，你懂記憶體、併發、型別系統。這讓你學什麼都快。
    *   *You understand memory, concurrency, and type systems, not just APIs.*
2.  **Pragmatism (務實主義):** 你不會堅持只用 Java，而是會根據「平台工程」的需求（啟動快、二進制檔小）去擁抱 Go/Rust。
    *   *You choose the right tool for the job (e.g., Go for platform tools due to binary size/startup time).*
3.  **Proactive Learner (主動學習者):** 你沒有等到入職才學，你為了面試已經先寫了一個 Demo。
    *   *You didn't wait to be hired; you built a demo just for the interview.*

---

## Common pitfalls｜常見錯誤與避免方式

1.  **Trying to write "Java in Go" (試圖用 Java 的方式寫 Go)**
    *   **Mistake:** 提到你會在 Go 裡面使用大量的 Interface 和 Factory Pattern。
    *   **Correction:** Go 講究 "Composition over Inheritance" 和簡潔。展示你知道 Go 的 idiomatic（道地）寫法。
2.  **Ignoring the Tooling (忽略工具鏈)**
    *   **Mistake:** 只談語法，不談生態。
    *   **Correction:** 平台工程師非常依賴工具。提到你熟悉 `go mod`, `go fmt`, 或 Rust 的 `cargo`，這顯示你懂「現代開發流程」。
3.  **Over-selling without evidence (過度吹噓卻無證據)**
    *   **Mistake:** 說「我精通所有語言」。
    *   **Correction:** 誠實說「我精通 Java/TS，熟悉 C++，目前正在將這些經驗映射到 Go/Rust」。誠實且自信更具說服力。

---

## Checklist｜檢查清單

- [ ] **Mindset:** 我已準備好將自己定位為「多語言工程師 (Polyglot Engineer)」，而不僅是 Java 開發者。
- [ ] **Knowledge:** 我能解釋 Java Thread 與 Go Goroutine 的區別。
- [ ] **Knowledge:** 我能解釋 Java GC 與 Rust Ownership (或是 C++ 手動管理) 的區別。
- [ ] **Hands-on:** 我已經看過 Go 的基礎語法，並寫過至少 50 行能跑的程式碼（最好與 GCP 相關）。
- [ ] **Resume:** 我已更新履歷，強調 C++ 背景與快速學習新技術的能力。
- [ ] **Interview:** 我準備好了一個「為什麼在這個場景下 Go/Rust 比 Java 更適合」的論述。