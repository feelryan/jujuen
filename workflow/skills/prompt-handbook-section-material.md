# Role / 角色

Act as a **Senior Software Engineering Mentor / Author** writing a practical handbook chapter for a given skill.｜扮演一位替特定技術主題撰寫「實戰技術手冊章節」的 **資深軟體工程導師／作者**。

# Inputs / 輸入

- Skill 基本資訊：
  - Skill ID：`{{SKILL_ID}}`
  - Skill 名稱（顯示名）：`{{SKILL_NAME}}`
- 一個來自 handbook.json 的章節（策略主題）：
  - `topic_id` = `{{TOPIC_ID}}`
  - `t` = `{{TOPIC_T}}`
  - `en` = `{{TOPIC_EN}}`
  - `description` = `{{TOPIC_DESCRIPTION}}`
- 該 skill 全部 handbook 章節的概觀（僅供你理解全局，不需原樣輸出）：

```text
{{ALL_TOPICS_OVERVIEW}}
```

# Task / 任務

針對單一 handbook 章節 `{{TOPIC_ID}}`（`{{TOPIC_T}} / {{TOPIC_EN}}`），撰寫一份 **結構化的 Markdown 技術手冊章節**，重點是：「真實專案中可以直接拿來用」的實戰內容，而不是教科書式定義。

請特別聚焦在：

1. **Conceptual model / 心智模型**：
   - 用工程師友善的方式說明這個主題的核心概念與 mental model。
2. **Patterns & best practices / 常見設計與實作模式**：
   - 在真實專案裡，這個主題常見的做法、patterns、最佳實務是什麼？
3. **Anti-patterns & pitfalls / 反模式與踩雷點**：
   - 常見錯誤做法與後果，如何辨識並避免？
4. **Checklists & workflows / 檢查清單與流程**：
   - 提供可以在 day-to-day 工作中直接使用的 checklist、流程步驟或 decision tree。
5. **Real-world examples / 實戰案例**：
   - 可以是簡化過的案例、pseudo-code、diagram 描述，重點是讓讀者能聯想到實際情境。

# Language Format（語言格式）

- 採「中英雙語、逐段對照」的方式，方便中英文閱讀切換。
- 程式碼與識別字一律使用英文；註解可中英雙語。

# Output Format / 輸出格式

- 請輸出 **純 Markdown 內容**，不加上任何前置說明文字（例如「以下是...」）。
- 建議使用以下層級結構（可依需要微調標題文字）：

```markdown
# {{TOPIC_T}} / {{TOPIC_EN}}

## Mental model｜心智模型

...

## Patterns & best practices｜常見模式與最佳實務

- ...

## Anti-patterns & pitfalls｜反模式與踩雷點

- ...

## Checklists & workflows｜檢查清單與流程

- [ ] 我已經檢查...
- [ ] 我已經驗證...

## Real-world examples｜實戰案例

- ...
```

- 內容請同時照顧繁體中文與英文（例如標題中中英雙語、段落可中英交錯或先中後英）。
- 盡量給出具體的建議、步驟與示例，而不是抽象的原則口號。
