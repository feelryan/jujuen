# Chapter 09: Refactoring Legacy Systems & Migration Patterns
# 第 09 章：遺留系統重構與遷移實戰

## 1. Introduction & Learning Objectives
## 1. 前言與學習目標

Migrating a monolithic legacy system to a microservices architecture is one of the most challenging tasks for a Senior Software Engineer. It is not merely a code reorganization; it is a complex operation involving data consistency, traffic routing, and organizational decoupling. This chapter focuses on risk control and architectural patterns to ensure zero downtime during migration.

將單體遺留系統遷移至微服務架構，是資深軟體工程師面臨最具挑戰性的任務之一。這不僅僅是程式碼的重組，更是一場涉及資料一致性、流量路由與組織解耦的複雜手術。本章專注於風險控制與架構模式，確保遷移過程中的零停機（Zero Downtime）。

By the end of this chapter, you should be able to:
完成本章後，你應該能夠：

1.  **Master the Strangler Fig Pattern**: Understand how to incrementally replace functionality in a monolith without a "Big Bang" rewrite.
    **掌握絞殺榕模式（Strangler Fig Pattern）**：理解如何在不進行「大爆炸」式重寫的情況下，逐步替換單體系統的功能。
2.  **Implement Anti-Corruption Layers (ACL)**: Design translation layers to prevent legacy technical debt from polluting new service models.
    **實作防腐層（Anti-Corruption Layer, ACL）**：設計轉譯層，防止遺留系統的技術債污染新服務的模型。
3.  **Execute Safe Data Migration**: Explain strategies for decoupling databases, such as Dual Write and Change Data Capture (CDC).
    **執行安全的資料遷移**：解釋資料庫解耦的策略，例如雙寫（Dual Write）與變更資料擷取（CDC）。
4.  **Design for Rollback**: Architect the migration path so that reverting changes is always an option in case of failure.
    **設計回滾機制**：架構遷移路徑，確保在失敗時隨時可以退回舊版。

---

## 2. Core Concepts & Mental Model
## 2. 核心觀念與心智模型

### 2.1 The Strangler Fig Pattern
### 2.1 絞殺榕模式

**Analogy**: Imagine a giant, old tree (the Monolith). A Strangler Fig (the new Microservices) starts growing around it. Initially, the fig relies on the tree for support. Over time, the fig grows stronger and takes over more sunlight (traffic), until the old tree dies and rots away, leaving only the new structure.

**類比**：想像一棵巨大的老樹（單體系統）。一株絞殺榕（新的微服務）開始圍繞著它生長。最初，榕樹依賴老樹支撐。隨著時間推移，榕樹變得更強壯並佔據更多陽光（流量），直到老樹枯死腐爛，只留下新的結構。

**Formal Definition**: A migration pattern where you incrementally replace specific functionality with new applications and services. A facade (usually an API Gateway or Load Balancer) intercepts requests and routes them to either the legacy system or the new service.

**正規定義**：一種逐步以新應用程式與服務替換特定功能的遷移模式。透過一個外觀介面（通常是 API Gateway 或負載平衡器）攔截請求，並將其路由至遺留系統或新服務。

### 2.2 Anti-Corruption Layer (ACL)
### 2.2 防腐層

**Concept**: When a new microservice needs to communicate with the legacy monolith (or vice versa), their data models often differ significantly. The monolith might use obscure column names or tight coupling. The ACL acts as a translator / adapter.

**觀念**：當新微服務需要與遺留單體（或反之）通訊時，它們的資料模型通常差異巨大。單體可能使用晦澀的欄位名稱或緊密耦合的結構。ACL 充當翻譯器或轉接器。

**Key Difference**:
*   **Adapter Pattern**: Typically transforms one interface to another.
*   **ACL**: Specifically used in Domain-Driven Design (DDD) to protect the integrity of a domain model from an external, messy model. It often involves semantic translation, not just syntactic adaptation.

**關鍵差異**：
*   **Adapter Pattern**：通常將一個介面轉換為另一個介面。
*   **ACL**：特指在領域驅動設計（DDD）中，用於保護領域模型的完整性，免受外部混亂模型的影響。它通常涉及語意上的翻譯，而不僅僅是語法上的適配。

---

## 3. Real-World & System Design View
## 3. 實務場景與系統設計視角

In a production environment, migration is rarely a clean cut. You will run a "Hybrid Architecture" for months or years.
在正式環境中，遷移很少是一刀切的。你將會運行數月甚至數年的「混合架構」。

### System Components in Transition
### 過渡期的系統元件

1.  **The Router (API Gateway / Load Balancer)**:
    *   **Role**: The traffic cop. It decides if a request for `/api/orders` goes to the Monolith or the new `OrderService`.
    *   **Criticality**: This is the single point of failure for the migration. Configuration must be dynamic (e.g., capable of canary routing).
    *   **角色**：交通警察。決定 `/api/orders` 的請求是進入單體還是新的 `OrderService`。
    *   **關鍵性**：這是遷移過程中的單點故障風險所在。配置必須是動態的（例如支援金絲雀路由）。

2.  **The Glue Code (ACL)**:
    *   **Role**: Code inside the Monolith that calls the new service, or code in the new service that calls the Monolith's database (temporarily).
    *   **Maintenance**: This code is destined to be deleted. Don't over-engineer it, but test it thoroughly.
    *   **角色**：單體內呼叫新服務的程式碼，或是新服務呼叫單體資料庫（暫時性）的程式碼。
    *   **維護**：這些程式碼註定要被刪除。不要過度設計，但必須徹底測試。

3.  **Data Synchronization Pipeline**:
    *   **Role**: Ensures that if a user writes to the new service, the old monolith (which might still handle reporting) sees the data.
    *   **Tech Stack**: Kafka Connect, Debezium (CDC), or simple Dual Write logic.
    *   **角色**：確保如果使用者寫入新服務，舊單體（可能仍負責報表功能）能看到該資料。
    *   **技術堆疊**：Kafka Connect, Debezium (CDC)，或簡單的雙寫邏輯。

### Impact on Quality Attributes
### 對品質屬性的影響

*   **Latency (延遲)**: Will likely increase initially due to extra hops (Gateway -> ACL -> Service).
    **延遲**：初期可能會因為額外的跳轉（Gateway -> ACL -> Service）而增加。
*   **Observability (可觀測性)**: Becomes critical. You need distributed tracing (e.g., OpenTelemetry) to see a request jump from Monolith to Microservice.
    **可觀測性**：變得至關重要。你需要分散式追蹤（如 OpenTelemetry）來觀察請求從單體跳轉到微服務的過程。
*   **Complexity (複雜度)**: Temporarily spikes. You are maintaining two systems plus the glue code.
    **複雜度**：暫時性激增。你需要維護兩套系統加上膠水程式碼。

---

## 4. Walkthrough: Extracting "User Service"
## 4. 逐步示例：提取「使用者服務」

### Scenario
### 情境
You have a 10-year-old PHP Monolith using a single MySQL database. You want to extract `User Management` (Auth, Profile) into a Go microservice.
你擁有一個 10 年歷史、使用單一 MySQL 資料庫的 PHP 單體系統。你想將 `User Management`（認證、個人檔案）提取為一個 Go 微服務。

### Step 1: Identify the Seams & Implement ACL
### 步驟 1：識別接縫並實作 ACL

First, stop the bleeding. Identify where the Monolith accesses user data. Wrap these direct DB calls into an Interface (ACL) within the Monolith.
首先，止血。找出單體在哪裡存取使用者資料。將這些直接的資料庫呼叫封裝在單體內部的介面（ACL）中。

**Before (PHP Monolith):**
```php
// Direct DB access scattered everywhere
$user = $db->query("SELECT * FROM users WHERE id = 1");
```

**After (PHP Monolith with Internal ACL):**
```php
interface UserRepository {
    public function getUser($id);
}

class SqlUserRepository implements UserRepository {
    public function getUser($id) {
        // Still pointing to old DB for now
        return $db->query("SELECT * FROM users WHERE id = ?", $id);
    }
}
```
*Why?* This prepares the code to be swapped later without changing business logic.
*為什麼？* 這為稍後的替換做準備，而無需更改業務邏輯。

### Step 2: Build the New Service & Shadow Traffic
### 步驟 2：建置新服務與影子流量（Shadow Traffic）

Deploy the new Go `UserService`. Do not switch user traffic yet. Use **Shadowing**.
部署新的 Go `UserService`。尚未切換使用者流量。使用 **Shadowing（影子模式）**。

The Monolith's ACL now calls *both* the old DB and the new Service (asynchronously), logging any discrepancies.
單體的 ACL 現在同時呼叫舊資料庫與新服務（非同步），並記錄任何不一致之處。

```php
class DualRunUserRepository implements UserRepository {
    public function getUser($id) {
        $oldResult = $this->sqlRepo->getUser($id);
        
        // Fire and forget / Async check
        dispatch(new CompareResultJob($id, $oldResult)); 
        
        return $oldResult; // Always return the trusted source
    }
}
```

### Step 3: Synchronize Data (The Hard Part)
### 步驟 3：同步資料（最困難的部分）

You cannot just copy the table once. The Monolith is still writing to it.
你不能只複製一次資料表。單體系統仍在寫入它。

**Strategy**:
1.  **Bulk Copy**: Dump `users` table to the new DB.
    **批次複製**：將 `users` 表倒出至新資料庫。
2.  **CDC (Change Data Capture)**: Listen to the Monolith's MySQL binlog (using Debezium) and stream updates to the new Service's DB.
    **CDC（變更資料擷取）**：監聽單體 MySQL 的 binlog（使用 Debezium），並將更新串流至新服務的資料庫。

### Step 4: Canary Release & Strangler Switch
### 步驟 4：金絲雀發布與絞殺切換

Configure the API Gateway.
設定 API Gateway。

1.  **Canary**: Route 1% of `GET /users/*` traffic to the new Service.
    **金絲雀**：將 1% 的 `GET /users/*` 流量路由至新服務。
2.  **Monitor**: Check error rates and latency.
    **監控**：檢查錯誤率與延遲。
3.  **Expand**: Increase to 10%, 50%, 100%.
    **擴展**：增加至 10%, 50%, 100%。
4.  **Write Traffic**: Switching *writes* is riskier. Usually done by flipping a feature flag in the Monolith to stop writing to its local table and start calling the Microservice API for updates.
    **寫入流量**：切換「寫入」風險較高。通常透過在單體中切換 Feature Flag，停止寫入本地資料表，改為呼叫微服務 API 進行更新。

### Step 5: Cleanup
### 步驟 5：清理

Once 100% traffic is on the new service and stable:
1.  Remove the `users` table from the Monolith DB.
2.  Delete the ACL code in the Monolith.
當 100% 流量都在新服務且穩定後：
1.  從單體資料庫移除 `users` 表。
2.  刪除單體中的 ACL 程式碼。

---

## 5. Common Pitfalls & Anti-patterns
## 5. 常見錯誤與反模式

### 5.1 The Distributed Monolith (分散式單體)
*   **Description**: You split the code but kept the database shared, or services are so chatty that one failure cascades everywhere.
*   **Why it's bad**: You get the complexity of microservices with none of the isolation benefits.
*   **Correction**: Ensure "Database per Service". Use asynchronous messaging (Events) to decouple services.
*   **描述**：你拆分了程式碼但保留了共享資料庫，或者服務間通訊過於頻繁導致連鎖故障。
*   **壞處**：你承受了微服務的複雜度，卻沒享受到隔離的好處。
*   **修正**：確保「每個服務有獨立資料庫」。使用非同步訊息（Events）來解耦服務。

### 5.2 Big Bang Migration (大爆炸式遷移)
*   **Description**: Rewriting the entire system from scratch and planning to switch over on a specific "Launch Day".
*   **Why it's bad**: High risk of failure. Business logic in the legacy system is often undocumented and lost in the rewrite.
*   **Correction**: Always use Strangler Fig. Deliver value incrementally.
*   **描述**：從頭重寫整個系統，並計劃在特定的「發布日」進行切換。
*   **壞處**：失敗風險極高。遺留系統中的業務邏輯通常缺乏文件，容易在重寫中遺失。
*   **修正**：始終使用絞殺榕模式。逐步交付價值。

### 5.3 Neglecting the Anti-Corruption Layer (忽視防腐層)
*   **Description**: Allowing the legacy database schema (e.g., `TBL_USR_01`) to leak into the new Microservice's domain objects.
*   **Why it's bad**: The new service becomes tightly coupled to the legacy debt.
*   **Correction**: Strictly map data at the boundary. The new service should have clean, semantic naming (e.g., `User`, `Profile`).
*   **描述**：允許遺留資料庫的 Schema（如 `TBL_USR_01`）滲透到新微服務的領域物件中。
*   **壞處**：新服務與遺留技術債緊密耦合。
*   **修正**：在邊界處嚴格映射資料。新服務應具有乾淨、語意化的命名（如 `User`, `Profile`）。

---

## 6. Interview & Discussion Hooks
## 6. 面試與實務問答切入點

### Q1: How do you handle data consistency during the migration of a write-heavy service?
### Q1: 在遷移高寫入量的服務時，你如何處理資料一致性？

*   **Key Points for High Score**:
    *   **Dual Write (Double Write)**: Application writes to both old and new DBs. Mention the complexity of handling partial failures (what if one write fails?).
    *   **CDC (Change Data Capture)**: Using database logs (binlog/WAL) to replicate data asynchronously. This is more robust than dual write.
    *   **Source of Truth**: Clearly define which DB is the authority at each phase.
    *   **Reconciliation**: Mention running background scripts to compare and fix data discrepancies.
*   **高分回答要點**：
    *   **雙寫（Dual Write）**：應用程式同時寫入舊與新資料庫。需提及處理部分失敗的複雜性（若其中一個寫入失敗怎麼辦？）。
    *   **CDC（變更資料擷取）**：利用資料庫日誌（binlog/WAL）非同步複製資料。這比雙寫更穩健。
    *   **單一真理來源（Source of Truth）**：明確定義每個階段哪個資料庫是權威。
    *   **對帳（Reconciliation）**：提及執行背景腳本來比對並修復資料差異。

### Q2: What if the new service fails after we switch 100% traffic? How do we rollback?
### Q2: 如果切換 100% 流量後新服務崩潰了怎麼辦？如何回滾？

*   **Key Points for High Score**:
    *   **Backfill Strategy**: Even after switching reads to the new service, continue writing data back to the old legacy DB (Reverse Sync) for a safety period.
    *   **Toggle Switch**: The ability to revert traffic instantly via API Gateway / Feature Flags.
    *   **Data Compatibility**: If the new service altered the data structure, how do we ensure the old system can still read it upon rollback? (Backward compatibility).
*   **高分回答要點**：
    *   **回填策略（Backfill）**：即使讀取已切換至新服務，仍持續將資料寫回舊的遺留資料庫（反向同步）作為安全期。
    *   **切換開關**：透過 API Gateway / Feature Flags 瞬間切回流量的能力。
    *   **資料相容性**：如果新服務改變了資料結構，如何確保回滾後舊系統仍能讀取？（向後相容性）。

### Q3: When should you *STOP* migrating and keep the Monolith?
### Q3: 什麼時候你應該「停止」遷移並保留單體？

*   **Key Points for High Score**:
    *   **Cost/Benefit Analysis**: When the domain is stable, rarely changes, and scales adequately vertically.
    *   **Complexity Tax**: If the team is too small to handle the operational overhead of distributed systems.
    *   **Performance**: If network latency between microservices is unacceptable for the specific use case.
*   **高分回答要點**：
    *   **成本效益分析**：當該領域穩定、鮮少變更，且垂直擴展已足夠時。
    *   **複雜度稅**：如果團隊太小，無法負擔分散式系統的維運開銷。
    *   **效能**：如果微服務間的網路延遲對特定使用案例來說無法接受。

---

## 7. Summary & Next Steps
## 7. 小結與後續延伸

### Summary (重點摘要)
1.  **Strangler Fig Pattern** is the standard for risk-averse migration. Never do a Big Bang rewrite.
    **絞殺榕模式**是規避風險的遷移標準。絕對不要進行大爆炸式重寫。
2.  **ACL (Anti-Corruption Layer)** allows you to build clean new models while interoperating with dirty legacy data.
    **ACL（防腐層）**讓你在與髒亂的遺留資料互動時，仍能建構乾淨的新模型。
3.  **Data Migration** is harder than code migration. Use CDC or Dual Write patterns.
    **資料遷移**比程式碼遷移更難。使用 CDC 或雙寫模式。
4.  **Observability** must span across the monolith and microservices to debug the hybrid state.
    **可觀測性**必須跨越單體與微服務，以便除錯混合狀態。
5.  **Rollback Plan** relies on keeping the old data in sync until the point of no return.
    **回滾計畫**仰賴保持舊資料同步，直到過了「不歸點」。

### Next Steps (後續延伸)
*   **Distributed Transactions**: Now that you have split the services, how do you handle transactions that span across them? Study the **Saga Pattern**.
    **分散式交易**：既然拆分了服務，如何處理跨服務的交易？請研讀 **Saga 模式**。
*   **Service Mesh**: As the number of services grows, managing mTLS, retries, and observability becomes a burden. Look into **Istio or Linkerd**.
    **Service Mesh**：隨著服務數量增加，管理 mTLS、重試與可觀測性成為負擔。研究 **Istio 或 Linkerd**。