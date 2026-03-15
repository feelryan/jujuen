# 前言與學習目標
# Introduction and Learning Objectives

作為資深工程師，選擇分支策略（Branching Strategy）不再只是個人習慣問題，而是影響整個工程團隊交付速度（Delivery Velocity）與系統穩定性（Stability）的關鍵架構決策。本章將超越基礎指令，從 CI/CD 與團隊協作的角度深入探討。

As a Senior Engineer, choosing a Branching Strategy is no longer just a matter of personal preference; it is a critical architectural decision that impacts the entire engineering team's Delivery Velocity and System Stability. This chapter moves beyond basic commands to explore these concepts from the perspective of CI/CD and team collaboration.

完成本章後，你應該能夠：
By the end of this chapter, you should be able to:

1.  **評估與選擇策略**：根據團隊規模、部署頻率與產品型態（SaaS vs. On-premise），在 Gitflow、GitHub Flow 與 Trunk-based Development (TBD) 之間做出最佳選擇。
    **Evaluate and Select Strategies**: Make the optimal choice between Gitflow, GitHub Flow, and Trunk-based Development (TBD) based on team size, deployment frequency, and product type (SaaS vs. On-premise).
2.  **設計發布流程**：結合 Feature Flags 與 CI/CD Pipeline，設計出能支援「每日多次部署」的高效流程。
    **Design Release Workflows**: Integrate Feature Flags and CI/CD Pipelines to design efficient workflows that support "multiple deployments per day."
3.  **解決擴張瓶頸**：識別並解決隨著團隊人數增長而產生的「合併地獄（Merge Hell）」與分支管理混亂。
    **Resolve Scaling Bottlenecks**: Identify and resolve "Merge Hell" and branch management chaos that arise as the team grows.

---

# 核心觀念與心智模型
# Core Concepts & Mental Model

分支策略的核心在於權衡**隔離性（Isolation）**與**整合頻率（Integration Frequency）**。隔離越久，衝突風險越高；整合越快，對自動化測試的要求越高。

The core of any branching strategy lies in balancing **Isolation** and **Integration Frequency**. The longer the isolation, the higher the risk of conflict; the faster the integration, the higher the demand for automated testing.

### 1. Gitflow：嚴謹的瀑布流 (The Strict Waterfall)
這是一個經典但稍顯過時的模型，強調嚴格的角色分離（Feature, Develop, Release, Master, Hotfix）。
This is a classic but somewhat dated model that emphasizes strict role separation (Feature, Develop, Release, Master, Hotfix).

*   **適用場景 (Use Case)**：發布週期長（數週/數月）、需要維護多個舊版本、傳統套裝軟體（Boxed Software）。
    **Use Case**: Long release cycles (weeks/months), need to maintain multiple legacy versions, traditional Boxed Software.
*   **缺點 (Drawback)**：流程繁瑣，容易導致長期分支（Long-lived branches），不利於 CI/CD。
    **Drawback**: Cumbersome process, prone to long-lived branches, hinders CI/CD.

### 2. GitHub Flow：輕量級持續交付 (Lightweight Continuous Delivery)
這是目前大多數中小型 SaaS 團隊的標準配置。只有一個長期分支（Main/Master），所有新功能透過 Pull Request (PR) 合併。
This is the standard setup for most small to medium SaaS teams today. There is only one long-lived branch (Main/Master), and all new features are merged via Pull Request (PR).

*   **適用場景 (Use Case)**：持續部署（Continuous Deployment）、Web 應用、團隊規模中等。
    **Use Case**: Continuous Deployment, Web applications, medium-sized teams.
*   **核心規則 (Core Rule)**：`main` 分支隨時可部署（Deployable at all times）。
    **Core Rule**: The `main` branch is deployable at all times.

### 3. Trunk-based Development (TBD)：Big Tech 的標準 (The Big Tech Standard)
Google、Meta 等巨頭的首選。所有開發者直接向主幹（Trunk）提交程式碼，或使用極短壽命的分支（Short-lived branches）。
The preferred choice of giants like Google and Meta. All developers commit code directly to the trunk or use extremely short-lived branches.

*   **心智模型 (Mental Model)**：主幹是唯一的真理來源。透過 **Feature Flags** 來隱藏未完成的功能，而不是透過分支來隔離。
    **Mental Model**: The trunk is the single source of truth. Unfinished features are hidden via **Feature Flags** rather than isolated by branches.
*   **先決條件 (Prerequisite)**：極高的測試覆蓋率、成熟的 CI/CD、Feature Toggles 基礎設施。
    **Prerequisite**: Extremely high test coverage, mature CI/CD, and Feature Toggles infrastructure.

---

# 實務場景與系統設計視角
# Real-World & System Design View

在系統設計與 DevOps 架構中，分支策略直接決定了 **DORA 指標**（DevOps Research and Assessment metrics）的表現，特別是「部署頻率（Deployment Frequency）」與「變更前置時間（Lead Time for Changes）」。

In system design and DevOps architecture, the branching strategy directly dictates performance on **DORA metrics**, specifically "Deployment Frequency" and "Lead Time for Changes."

### 1. CI/CD Pipeline 的觸發設計 (Trigger Design for CI/CD Pipeline)
分支策略決定了 Pipeline 何時以及如何運行：
The branching strategy determines when and how the pipeline runs:

*   **Gitflow**: 需要針對 `develop`, `release/*`, `master` 配置不同的 Pipeline 行為（如：只有 Release 分支會產生 Artifacts）。
    **Gitflow**: Requires different pipeline behaviors for `develop`, `release/*`, and `master` (e.g., only Release branches generate Artifacts).
*   **TBD**: 只有一條主要的 Pipeline。每次 Commit 都觸發完整的測試與建置。這簡化了 CI 配置，但要求 Pipeline 速度極快。
    **TBD**: Only one main pipeline. Every commit triggers full testing and building. This simplifies CI configuration but demands an extremely fast pipeline.

### 2. 微服務架構下的挑戰 (Challenges in Microservices)
在單體（Monolith）架構中，Gitflow 可能勉強可行；但在微服務架構下，如果每個服務都走複雜的 Gitflow，版本相依性管理（Dependency Management）會變成惡夢。
In a Monolith architecture, Gitflow might be manageable; however, in a microservices architecture, if every service follows a complex Gitflow, version dependency management becomes a nightmare.

*   **最佳實踐 (Best Practice)**：微服務傾向於 **TBD** 或 **GitHub Flow**。服務間透過 API 契約（Contract）解耦，而不是透過協調發布分支來管理。
    **Best Practice**: Microservices lean towards **TBD** or **GitHub Flow**. Services decouple via API Contracts rather than managing coordinated release branches.

### 3. 資料庫遷移與分支 (Database Migrations and Branching)
資深工程師必須考慮 DB Schema Change 如何配合分支策略。
Senior Engineers must consider how DB Schema Changes align with branching strategies.

*   **向後相容 (Backward Compatibility)**：無論使用何種策略，DB 變更必須與程式碼解耦。通常原則是「先擴充 DB，再部署程式碼，最後清理 DB」。這在 TBD 中尤為重要，因為沒有「發布窗口」來停機維護。
    **Backward Compatibility**: Regardless of the strategy, DB changes must be decoupled from code. The general rule is "Expand DB first, deploy code, then contract DB." This is especially critical in TBD as there is no "release window" for downtime maintenance.

---

# 逐步示例：從 Feature Branch 到 Trunk-based Development
# Walkthrough: From Feature Branch to Trunk-based Development

假設你帶領一個團隊，正在從傳統的 Gitflow 轉型為 Trunk-based Development，以加快迭代速度。

Suppose you are leading a team transitioning from traditional Gitflow to Trunk-based Development to accelerate iteration speed.

### 階段 1：引入 Feature Flags (Phase 1: Introducing Feature Flags)
在 TBD 中，你不能因為功能沒寫完就不 Merge。你需要一個機制來「關閉」生產環境中的未完成代碼。

In TBD, you cannot hold off merging just because a feature is incomplete. You need a mechanism to "turn off" unfinished code in production.

```typescript
// Config/FeatureFlag.ts
// 一個簡單的 Feature Flag 實作示意
// A simple Feature Flag implementation example

const flags = {
  NEW_CHECKOUT_FLOW: process.env.ENABLE_NEW_CHECKOUT === 'true',
  DARK_MODE: false, // Hardcoded off for now
};

export const isFeatureEnabled = (featureName: keyof typeof flags): boolean => {
  // 在真實系統中，這裡可能會查詢 Redis 或 LaunchDarkly 等服務
  // In a real system, this might query Redis or services like LaunchDarkly
  return flags[featureName];
};
```

### 階段 2：抽象化分支邏輯 (Phase 2: Abstracting Branching Logic)
開發新功能時，使用 Flag 包裹入口點，允許程式碼隨時合併進 Main 分支。

When developing new features, wrap entry points with Flags, allowing code to be merged into the Main branch at any time.

```typescript
// Services/CheckoutService.ts

import { isFeatureEnabled } from '../Config/FeatureFlag';

export class CheckoutService {
  public processPayment(order: Order) {
    if (isFeatureEnabled('NEW_CHECKOUT_FLOW')) {
      return this.processPaymentV2(order);
    }
    return this.processPaymentV1(order);
  }

  private processPaymentV1(order: Order) {
    // 舊的穩定邏輯 (Old stable logic)
    console.log("Processing with V1 legacy flow...");
  }

  private processPaymentV2(order: Order) {
    // 新的開發中邏輯 (New logic under development)
    // 即使這裡有 Bug，只要 Flag 關閉，就不會影響 Production
    // Even if there are bugs here, as long as the Flag is off, Production is safe
    console.log("Processing with V2 optimized flow...");
  }
}
```

### 階段 3：改變開發流程 (Phase 3: Changing the Workflow)

1.  **舊流程 (Old Way)**：開發者開一個 `feature/checkout-v2` 分支，開發 2 週，解決 50 個衝突，然後合併。
    **Old Way**: Developer opens a `feature/checkout-v2` branch, develops for 2 weeks, resolves 50 conflicts, then merges.
2.  **新流程 (New Way - TBD)**：
    **New Way - TBD**:
    *   Day 1: 建立 `processPaymentV2` 空殼函數，加上 Feature Flag。Commit & Push to Main.
        Day 1: Create `processPaymentV2` skeleton function, add Feature Flag. Commit & Push to Main.
    *   Day 2: 實作 V2 的驗證邏輯。寫單元測試。Commit & Push to Main.
        Day 2: Implement validation logic for V2. Write unit tests. Commit & Push to Main.
    *   Day 3: 實作 V2 的金流串接。Commit & Push to Main.
        Day 3: Implement payment gateway integration for V2. Commit & Push to Main.
    *   Day 4: 在 Staging 開啟 Flag 進行測試。
        Day 4: Enable Flag in Staging for testing.
    *   Day 5: 在 Production 對 1% 用戶開啟 Flag (Canary Release)。
        Day 5: Enable Flag for 1% of users in Production (Canary Release).

**分析 (Analysis)**：
這種做法消除了「Merge Hell」。代碼持續整合，衝突在發生當下就被解決（因為每天都在 Merge）。

This approach eliminates "Merge Hell." Code is continuously integrated, and conflicts are resolved the moment they occur (since merging happens daily).

---

# 常見錯誤與反模式
# Common Pitfalls & Anti-patterns

### 1. 長壽命的功能分支 (Long-lived Feature Branches)
*   **描述**：分支存在超過 2-3 天未合併。
    **Description**: Branches existing for more than 2-3 days without merging.
*   **為何不好**：這是軟體工程中的「庫存（Inventory）」。未合併的代碼會貶值，且隨著主幹演進，合併成本呈指數級上升。
    **Why it's bad**: This is "Inventory" in software engineering. Unmerged code depreciates, and merge costs increase exponentially as the trunk evolves.
*   **解法**：強制拆分任務（Task Decomposition），使用 Feature Flags。
    **Solution**: Enforce Task Decomposition and use Feature Flags.

### 2. 依賴 Cherry-pick 進行發布 (Dependence on Cherry-pick for Releases)
*   **描述**：主幹不穩定，導致發布時必須從主幹挑選特定的 Commit 到 Release 分支。
    **Description**: The trunk is unstable, so specific commits must be hand-picked from the trunk to the Release branch for deployment.
*   **為何不好**：這破壞了 Git 的 DAG（有向無環圖）完整性，容易遺漏依賴的 Commit，且難以追蹤 Bug 的修復狀態。
    **Why it's bad**: This breaks the integrity of Git's DAG (Directed Acyclic Graph), makes it easy to miss dependent commits, and makes tracking bug fix status difficult.
*   **解法**：確保主幹隨時處於「綠燈」狀態。若需 Hotfix，應在主幹修復後 Backport（如果維護舊版），或直接 Roll-forward。
    **Solution**: Ensure the trunk is always "Green." If a Hotfix is needed, fix on trunk and Backport (if maintaining legacy versions), or simply Roll-forward.

### 3. 環境特定的分支 (Environment-specific Branches)
*   **描述**：建立 `dev`, `test`, `uat`, `prod` 分支，並透過將代碼從一個分支 Merge 到另一個分支來部署。
    **Description**: Creating `dev`, `test`, `uat`, `prod` branches and deploying by merging code from one branch to another.
*   **為何不好**：代碼在不同環境應該是同一個 Artifact（Build once, deploy anywhere），只是配置不同。重新 Merge/Build 可能導致 `prod` 運行的代碼與 `test` 不同。
    **Why it's bad**: Code should be the same Artifact across environments (Build once, deploy anywhere), only configurations differ. Re-merging/Building can result in `prod` running different code than `test`.
*   **解法**：基於 Tag 或 Commit Hash 部署 Artifact，而不是基於分支名稱。
    **Solution**: Deploy Artifacts based on Tags or Commit Hashes, not branch names.

---

# 面試與實務問答切入點
# Interview & Discussion Hooks

### Q1: 請比較 Gitflow 與 Trunk-based Development，並說明你會如何選擇？
**Compare Gitflow and Trunk-based Development, and explain how you would choose between them.**

*   **高分回答要點 (Key Points for High Score)**：
    *   **Gitflow**：適合版本發布週期固定、需要同時維護多個舊版本的軟體（如手機 App、嵌入式系統）。優點是控制力強，缺點是整合延遲高。
    *   **TBD**：適合 SaaS、Web App。優點是極致的交付速度與 CI/CD 整合。
    *   **決策關鍵**：團隊的自動化測試成熟度。沒有高覆蓋率的測試，TBD 會導致主幹頻繁損壞。
    *   **Gitflow**: Suitable for software with fixed release cycles and the need to maintain multiple legacy versions simultaneously (e.g., Mobile Apps, Embedded Systems). Pro: Strong control; Con: High integration latency.
    *   **TBD**: Suitable for SaaS, Web Apps. Pro: Extreme delivery velocity and CI/CD integration.
    *   **Decision Key**: The maturity of the team's automated testing. Without high test coverage, TBD will lead to a frequently broken trunk.

### Q2: 在 Trunk-based Development 中，如何處理一個需要開發兩週的大型功能？
**In Trunk-based Development, how do you handle a large feature that takes two weeks to develop?**

*   **高分回答要點 (Key Points for High Score)**：
    *   **Feature Flags**：核心技術。代碼合併進主幹，但對用戶隱藏。
    *   **Branch by Abstraction**：如果涉及重構，先建立抽象層，讓新舊實作共存，逐步替換。
    *   **Dark Launching**：在背景運行新代碼但不顯示結果，驗證效能與正確性。
    *   **Feature Flags**: The core technique. Code is merged into the trunk but hidden from users.
    *   **Branch by Abstraction**: If refactoring is involved, create an abstraction layer first, allowing old and new implementations to coexist, and replace gradually.
    *   **Dark Launching**: Run new code in the background without showing results to verify performance and correctness.

### Q3: 團隊目前面臨嚴重的 Merge Conflict 問題，你會如何改善？
**The team is currently facing severe Merge Conflict issues. How would you improve this?**

*   **高分回答要點 (Key Points for High Score)**：
    *   **Root Cause**：通常是因為分支壽命過長（Long-lived branches）或模組耦合度過高（High Coupling）。
    *   **Process**：推動「每日合併」文化，即使功能未完成。
    *   **Architecture**：檢查是否多個團隊頻繁修改同一個「上帝類別（God Class）」或設定檔，考慮拆分代碼庫或模組化。
    *   **Root Cause**: Usually due to long-lived branches or high coupling between modules.
    *   **Process**: Promote a "Merge Daily" culture, even if features are incomplete.
    *   **Architecture**: Check if multiple teams frequently modify the same "God Class" or configuration file; consider splitting the codebase or modularizing.

---

# 小結與後續延伸
# Summary & Next Steps

### 記憶錨點 (Key Takeaways)
1.  **分支策略即權衡**：在隔離安全性（Gitflow）與交付速度（TBD）之間做選擇。
    **Branching Strategy is a Trade-off**: Choose between isolation safety (Gitflow) and delivery speed (TBD).
2.  **TBD 是高效能團隊的目標**：它能顯著提升 DORA 指標，但需要強大的測試與 Feature Flag 基礎設施。
    **TBD is the Goal for High Performers**: It significantly improves DORA metrics but requires robust testing and Feature Flag infrastructure.
3.  **避免長壽命分支**：分支壽命越短，合併痛苦越小。
    **Avoid Long-lived Branches**: The shorter the branch life, the less painful the merge.
4.  **Feature Flags 是關鍵**：它是解耦「部署（Deployment）」與「發布（Release）」的神器。
    **Feature Flags are Key**: They are the magic wand for decoupling "Deployment" from "Release."
5.  **不要依賴 Cherry-pick**：這通常是流程設計不良的信號。
    **Don't Rely on Cherry-pick**: This is usually a sign of poor process design.

### 後續延伸 (Next Steps)
*   **下一章 (Chapter 05)**：深入探討 **Git Hooks 與自動化流程**，學習如何在 Commit 與 Push 階段自動執行檢查，為 TBD 打下基礎。
    **Next Chapter (Chapter 05)**: Dive deep into **Git Hooks and Automation**, learning how to automatically enforce checks at the Commit and Push stages, laying the foundation for TBD.
*   **延伸閱讀**：研究 "Monorepo vs. Polyrepo" 的分支策略差異（如 Google/Meta 的單一倉庫策略）。
    **Further Reading**: Research the branching strategy differences in "Monorepo vs. Polyrepo" (e.g., Google/Meta's single repository strategy).