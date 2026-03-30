你是一位專精 **{skill}** 的大師，為這個技能規劃「章節目錄（Category 清單）」。

## 任務說明

目標對象：
- 具 7–12 年經驗的 Senior Software Engineer
- 主要需求：面試表現與實務能力雙提升（system design、DS&A、production readiness）

我會提供：
- 技能名稱：`{skill}`

你的任務：
- 幫這個技能設計一份「學習與練功路線圖」，拆成多個章節（chapters），每個章節都是 Category 的一個 item。
- 這些章節會被用來生成對應的教材與練習題，因此需要：
  - 有清楚的章節標題（中英文）
  - 按照學習順序由淺入深排列
  - 對應 Senior Engineer 的實戰場景（系統設計、效能、維運、團隊協作、最佳實務等）。

建議章節數量：
- 5–12 個章節皆可，重點是「完整覆蓋該技能的核心能力模型」，而非僅列 keyword。

## 輸出格式（非常重要）

請務必輸出「純 JSON 陣列」，不能有 Markdown 語法、註解或多餘文字。

JSON 陣列中的每個物件代表一個章節（對應 Category 的 item），格式如下示意：

```json
[
  {
    "id": "chapter01",              // 章節代號：全英文+數字、不含空白，建議 chapter01, chapter02, ...
    "t": "核心觀念與心智模型",   // 章節標題（繁體）
    "en": "Core concepts and mental model", // 章節標題或簡短英文說明
    "description": "說明此技能的定位、典型使用場景，以及對 Senior Engineer 的影響。"
  }
]
```

規則：
- 一定要回傳 **JSON 陣列**，最外層不可是物件。
- 陣列中的每一個物件，代表一個依序排列的章節（chapter01, chapter02, ...）。
- 不要在 JSON 之外加入任何文字說明或註解。
- 每個物件 **至少** 要有欄位：`id`, `t`, `en`。
- 建議額外加入：`description`，用 1–3 句說明該章節聚焦的能力與常見實戰場景。
- `id` 必須是穩定的英文代號：
  - 僅能使用英文字母、數字與短橫線（-）。
  - 不可包含空白或中文。
  - 建議形式：`"chapter01"`, `"chapter02"`, ... 依實際章節順序遞增。
- `t` 應為清楚的中文章節名稱，讓工程師一看就知道本章重點。
- `en` 為英文名稱或簡短英文描述，可在面試或英文筆記情境中直接使用。

## 範例：以「TypeScript」為例（僅示意，實際請依指定 {skill} 產生）

> 下方僅是**格式示例**，不是要你照抄的內容。

```json
[
  {
    "id": "chapter01",
    "t": "TypeScript 核心型別系統",
    "en": "Core type system",
    "description": "從基本型別到 union/intersection、type narrowing，建立正確的型別心智模型。"
  },
  {
    "id": "chapter02",
    "t": "實戰中的型別設計",
    "en": "Type design in real projects",
    "description": "如何為 API、domain model、錯誤處理設計可維護的型別結構，避免 over-typing 與 under-typing。"
  }
]
```

## 請根據以下資訊產生章節 JSON 陣列

- 技能名稱：`{skill}`

請直接輸出 **JSON 陣列**，不要加上任何說明文字或額外註解。