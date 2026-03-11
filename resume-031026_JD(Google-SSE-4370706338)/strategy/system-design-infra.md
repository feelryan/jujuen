# 面試準備：針對基礎設施的系統設計 / System Design for Infrastructure & Tools

## Why this matters｜為什麼這個主題重要

**1. The "Web App" Trap (Web App 的陷阱)**
Your resume highlights extensive experience in building "Medical Imaging Platforms" and "E-commerce Search Engines." These are typical **User-facing Applications**. However, the JD is for a **"Diagnostics, Tools, Google Cloud"** role within the **MSCA (ML, Systems, & Cloud AI)** team.
Google 的面試官極有可能不會考你「設計一個 Instagram」，而是考你「設計一個分散式日誌收集系統」或「設計一個管理百萬台伺服器的健康檢查系統」。如果你用設計 Web App 的 CRUD 思維來回答 Infra 題目，會被視為 "Wrong Level" 或 "Lack of Domain Knowledge"。

**2. Scale & Reliability over Features (規模與可靠性優於功能)**
The JD mentions "Keep the Google test fleet in perfect shape" and "Hyperscale computing."
在基礎設施的設計中，重點不在於豐富的 UI/UX 功能，而在於：
- **High Throughput:** How to ingest terabytes of diagnostic logs per second?
- **Agent Efficiency:** How to ensure your diagnostic tool doesn't crash the host machine?
- **Fault Tolerance:** What happens if the network partitions inside a Data Center?

**3. Bridging the Gap (填補履歷缺口)**
You are a Google Certified Professional Cloud Architect, which proves you know how to *use* GCP tools. This interview requires you to demonstrate how to *build* tools like GCP (or internal equivalents like Borg, Monarch).

---

## Step‑by‑step strategy｜具體行動步驟

### Week 1: Shift Mental Model (思維轉換)
*   **Action:** Stop thinking about "Users" (User) and "Requests" (HTTP). Start thinking about "Nodes" (Machines) and "Events/Telemetries" (Signals).
*   **Study:** Research Google’s internal infrastructure papers to understand the scale.
    *   *Borg (Cluster Management)* - Understand scheduling.
    *   *Monarch (In-memory Time Series Database)* - Understand monitoring.
    *   *Dapper (Distributed Tracing)* - Understand diagnostics.

### Week 2: Master the "Infra Design Patterns" (掌握基礎設施設計模式)
Focus on two specific archetypes relevant to "Diagnostics & Tools":
1.  **Data Aggregation System (資料聚合系統):**
    *   *Scenario:* "Design a system to collect CPU usage from 1 million servers."
    *   *Key Components:* Sidecar Agents, Push vs. Pull model, Buffering (Kafka/PubSub), Time-series DB.
2.  **Distributed Task Scheduler (分散式任務排程):**
    *   *Scenario:* "Design a system to schedule hardware diagnostic tests on new server racks (NPI)."
    *   *Key Components:* Central Manager (Control Plane), Worker Nodes, State Machine (Pending -> Running -> Failed), Leases/Heartbeats.

### Week 3: Operational & Hardware Constraints (維運與硬體限制)
*   **Action:** Practice "Back-of-the-envelope" calculations specifically for infrastructure.
    *   *Instead of:* "How many users are online?"
    *   *Ask:* "What is the network bandwidth per rack?", "What is the write throughput to disk?", "How much CPU overhead can the agent consume?" (e.g., < 1% CPU).
*   **Resume Connection:** Review your "Change Healthcare" experience. How did you handle logs? Refine that story to sound more "system-level" (e.g., "Optimized log ingestion pipeline" rather than just "Checked logs").

### Week 4: Mock Interviews with Specific Prompts (針對性模擬面試)
*   **Practice Prompt 1:** Design a "Health Check Service" for Google Cloud's fleet.
*   **Practice Prompt 2:** Design a "Deployment System" that pushes binary updates to 100k machines.
*   **Focus:** Concurrency control, handling "Stragglers" (slow machines), and cascading failures.

---

## Examples & templates｜範例與句型

### 1. Clarifying Questions (釐清需求範本)
Instead of asking about user demographics, ask about the **Fleet & Environment**:
*   "Are we designing for a single data center or multi-region availability?" (針對單一機房還是跨區？)
*   "What is the acceptable latency for the diagnostic data? Is it real-time alerting or batch reporting?" (診斷數據的延遲容忍度？)
*   "What is the resource constraint on the host machine? The diagnostic agent should be non-intrusive." (Host 機器的資源限制為何？代理程式必須是低侵入性的。)
*   "Is the target hardware homogeneous (all same TPUs) or heterogeneous?" (硬體是同質還是異質的？這影響 NPI 測試的複雜度。)

### 2. Architecture Components (架構組件關鍵字)
Use these terms to sound like an Infra Engineer:
*   **Control Plane vs. Data Plane:** "The Control Plane schedules the diagnostic tests, while the Data Plane (Agents) executes them."
*   **Agent / DaemonSet:** "We need a lightweight agent running on every node to scrape metrics."
*   **Push vs. Pull:** "For large scale fleet monitoring, a Pull model (Prometheus style) might be better for flow control, but Push is faster for critical alerts."
*   **Heartbeat & Lease:** "Nodes must send heartbeats to the master. If a heartbeat is missed, we assume hardware failure."
*   **Aggregation Tier:** "Raw logs are too heavy; we need an aggregation tier to pre-process data before storing to DB."

### 3. "NPI" (New Product Introduction) Context
Since the JD mentions NPI:
*   "For NPI projects, the system needs to support **flexible schema** because new hardware metrics might change frequently."
*   "We need a **workflow engine** (DAG) to sequence the hardware validation steps (e.g., Power-on -> BIOS check -> Stress test)."

---

## Signals for interviewers｜要讓面試官看到的訊號

If you execute this strategy, the interviewer will see:

1.  **Scalability Awareness (規模意識):**
    *   You understand that "looping through a database" doesn't work for 1 million machines. You talk about **sharding**, **partitioning**, and **map-reduce** patterns.
2.  **System Programming Empathy (系統程式開發的同理心):**
    *   You care about the **cost of the agent**. You mention "We shouldn't use a heavy Java JVM for a simple metric collector; maybe Go or C++ is better here to save memory." (This aligns with the JD's C++/System programming preference).
3.  **Reliability Engineering (可靠性工程):**
    *   You proactively discuss **"Blast Radius"** (爆炸半徑). "If we push a bad config, we should only affect 1% of the fleet first (Canary Deployment)."
4.  **Hardware/OS Knowledge (硬體與作業系統知識):**
    *   You mention interacting with **kernel syscalls**, **procfs**, or **hardware sensors** (temperature, fan speed) when discussing data collection.

---

## Common pitfalls｜常見錯誤與避免方式

*   **Pitfall 1: Designing a 3-Tier Web App.** (錯誤：設計成三層式 Web App)
    *   *Avoid:* Drawing "User -> Load Balancer -> Web Server -> DB".
    *   *Do:* Draw "Fleet (Agents) -> Ingestion Gateway -> Message Queue -> Stream Processor -> TSDB".
*   **Pitfall 2: Ignoring the "Write-Heavy" Nature.** (錯誤：忽略寫入密集特性)
    *   *Context:* Diagnostic systems are usually Write-Heavy (millions of logs) and Read-Rarely (only read when debugging).
    *   *Avoid:* Optimizing for read caching (Redis) excessively.
    *   *Do:* Optimize for fast ingestion (LSM Trees, Cassandra, BigTable).
*   **Pitfall 3: Forgetting Network Topology.** (錯誤：忘記網路拓樸)
    *   *Avoid:* Assuming all servers can talk to the central DB directly.
    *   *Do:* Introduce "Regional Aggregators" to reduce cross-region bandwidth costs.

---

## Checklist｜檢查清單

- [ ] **Mindset:** Can I explain the difference between designing for "Users" vs. "Machines"?
- [ ] **Vocabulary:** Am I comfortable using terms like *Control Plane, Agent, Heartbeat, Time-series DB, Ingestion Pipeline*?
- [ ] **Pattern:** Have I practiced drawing a "Distributed Log Collection System" architecture?
- [ ] **Pattern:** Have I practiced drawing a "Distributed Task Scheduler" architecture?
- [ ] **Constraint:** Do I remember to check CPU/Memory constraints of the diagnostic agent itself?
- [ ] **Google Context:** Have I read the high-level concepts of *Borg* and *Monarch*?