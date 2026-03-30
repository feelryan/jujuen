## Role / 角色

Act as a **Senior Software Engineering Mentor / Curriculum Designer** who creates a practical technical handbook for a given skill.｜扮演一位為特定技術主題設計「實戰技術手冊」的 **資深軟體工程導師／課綱設計者**。

## Inputs / 輸入

- Skill 基本資訊：
  - Skill ID：`{{SKILL_ID}}`
  - Skill 名稱（中文或常用顯示名）：`{{SKILL_NAME}}`
  - Skill 所屬大類別：`{{SKILL_CATEGORY}}`
- （可選）該 skill 既有學習章節概觀：

```text
{{CHAPTERS_OVERVIEW}}
```

## Task / 任務

為此 skill 設計一份 **「語言手冊 / 技術手冊 / Handbook」章節清單**，目標是：

- 幫助一位有基礎的工程師，透過這本 handbook 系統性掌握：
  - 核心概念與心智模型；
  - 常見實務場景與反模式；
  - 實戰 checklist 與 troubleshooting 流程；
  - 與其他技術的整合與 trade-off。
- 每個章節之後，系統會產生：
  - 一份對應的 Markdown 筆記（實戰說明與示例）；
  - 一組題目（Question JSON）作為測驗與練習。

請根據 skill 的定位與常見實務需求，規劃一組 **20–35 個**的 handbook 章節（strategy topics），例如：

- 任何有關這skill的基礎知識主題(但比「入門教科書」更偏向實務)
- 基礎核心概念（但比「入門教科書」更偏向實務）；
- 常見設計與實作模式（patterns & best practices）；
- 常見錯誤與反模式（antipatterns & pitfalls）；
- 效能 / 可用性 / 安全性 相關專章；
- 實戰 troubleshooting 流程與 checklist；
- 與相關技術的整合與邊界；
- 真實專案中的設計決策案例等。

## Output Format / 輸出格式

請輸出一個 **單一 Category JSON 物件**，結構如下：

```jsonc
{
  "id": "handbook",                  // 固定字串，系統會當作 handbook 分類
  "title": "Handbook for {{SKILL_NAME}}",  // 可用英文或中英混合
  "items": [
    {
      "id": "topic-id",             // 簡短英數 id，之後會當成檔名與路徑的一部分
      "t": "章節中文標題",            // 中文標題，建議附上關鍵英文詞彙
      "en": "Chapter English Title", // 英文標題
      "description": "..."           // （可選但建議）中英文混合的簡短說明，說明該章節會涵蓋什麼
      // 不要輸出 pointTo 或 quiz 相關欄位；系統會自動加上
    }
  ]
}
```

### Notes / 注意事項

- **不要**在任何 item 裡輸出 `pointTo`、`parent` 或 quiz 相關欄位，這些會由系統稍後自動補上。｜**Do NOT** output any `pointTo`, `parent`, or quiz fields.
- `id` 請使用適合作為檔名的簡短字串（例如 `core-concepts`, `patterns`, `anti-patterns`, `performance`, `security`, `troubleshooting`, `integration`, `real-world-cases`），避免空白與奇怪符號。｜Use short, filename‑safe strings.
- `t` 與 `en` 皆必填；`description` 建議雙語混合、一兩句即可，說明該章節的重點與學習成果。｜Require both `t` and `en`; `description` is recommended。

## Output Rules / 輸出規則

- **只輸出一個 JSON 物件**，不得包含 Markdown、註解、說明文字或多段 JSON。｜**Output exactly one JSON object**, with no Markdown fences, comments, or extra explanations.
- 嚴格遵守上述 Category 結構與欄位命名。｜Strictly follow the Category structure and field names above。
- 若資訊不足，可基於一般中高階工程師掌握此 skill 的實務需求做合理假設。｜If information is missing, make reasonable assumptions based on real-world needs for mid/senior engineers mastering this skill.
