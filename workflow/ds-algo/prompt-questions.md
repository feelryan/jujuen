請為下面的「{topic}」這個資料結構與演算法主題，設計一組高品質的題庫。

本次呼叫中，你「最多」可以產生 {remaining_questions} 題問題，整體目標總題數為 {total_questions} 題。
系統會附上一份 JSON 物件 {questions_meta}，其中包含目前已經產生的題目摘要與總題數設定，請務必避免重複或太過相似的題目。

產生的題目須貼切實際面試考題並且可讓觀念更加釐清。

**重要規則：**

**產出格式規則：**

1.  **分句原則**：題目與解釋須以句號或段落為界進行分句。
2.  **多語支援**：每句需包含繁體 (t)及英文 (en)。
3.  **字詞分組 (wg)**：針對每個分句，識別出具備特別意義的中文字詞群組其英文翻譯相對困難的。提供該字詞在該分句字中的繁體中文 (t)、英文翻譯 (en) 及詞性 (ps)。
4.  **解釋邏輯 (why)**：解釋答案以及為什麼其他選項是錯誤的，並同步提供英文版。
5.  **選項標號 (options)**：`options` 為一個陣列，依照陣列順序對第 1、2、3、4 個選項依序加上 `(A) `、`(B) `、`(C) `、`(D) `⋯ 作為前綴。此前綴必須同時加在該選項的 `t` 與 `en` 字串開頭；若原本文字已有其它標號（例如 `A.`、`(1)` 等），請先移除再改用標準的 `(A) `、`(B) `⋯。不得出現重複或遺漏的標號，且除了加入標號外，請不要改變選項原本的語意。
6.  **答案格式 (answer)**：
  - 若為單選題（Single Choice / 單選題），`"answer"` 必須是一個單一大寫英文字母，例如 `"A"`、`"B"`，對應正確選項的標號。
  - 若為複選題（Multiple Choice / 複選題），`"answer"` 必須是一個由一個或多個大寫英文字母組成的字串，使用半形逗號分隔且不含空白，例如 `"A,B"` 或 `"B,D"`。
  - 禁止使用數字索引（例如 0,1,2 或 1,2,3⋯）或完整文字敘述來表示答案，必須只用選項標號字母。

**JSON 欄位縮寫定義：**

*   `t`: 繁體中文, `en`: 英文
*   `wg`: 字詞群組, `ps`: 詞性

**產出格式（單一物件範例）：**

```json
[
  {
    "no": "<題號>",
    "level": "<難易度>",
    "keywords": "<英文關鍵字(可多個,以逗號區隔)>",
    "parentNo": "<如果此為子題,則有母題的題號, 若無則為null>",
    "images": "<如果有圖片的話,則產生圖檔連結>",
    "codeSnippet": "<如果該題目需要用程式碼來輔助或描述>",
    "question": [
      {
        "t": "...", "en": "...",
        "wg": [ {"t": "...", "en": "...", "ps": "..."} ]
      }
    ],
    "type": "<單選題/複選題>",
    "options": [
      {
        "t": "...", "en": "...",
        "wg": [ ... ]
      }
    ],
    "answer": "<答案>",
    "why": {
      "t": "...", "en": "...",
      "wg": [ ... ]
    }
  }
]
```


### sample：

```json
[
  {
    "no": "1",
    "level": "medium",
    "keywords": "Compute, Cost Optimization, Serverless, Cloud Run",
    "parentNo": null,
    "figure": null,
    "question": [
      {
        "t": "您的新創公司正在開發一個無狀態的微服務應用程式，",
        "en": "Your startup is developing a stateless microservices application,",
        "wg": [
          {"t": "新創", "en": "startup", "ps": "N"},
          {"t": "無狀態", "en": "stateless", "ps": "Adj"},
          {"t": "微服務", "en": "microservice", "ps": "N"}
        ]
      },
      {
        "t": "該應用程式的流量無法預測，且偶爾會長時間沒有請求。",
        "en": "The application traffic is unpredictable, and occasionally there are long periods with no requests.",
        "wg": [
          {"t": "偶爾", "en": "occasionally", "ps": "Adv"}
        ]
      },
      {
        "t": "您需要選擇一個最具成本效益的運算平台，同時將維運負擔降至最低。",
        "en": "You need to choose the most cost-effective compute platform while minimizing operational overhead.",
        "wg": [
          {"t": "維運負擔", "en": "operational overhead", "ps": "N"}
        ]
      }
    ],
    "type": "單選題",
    "options": [
      {
        "t": "(A) 使用 Compute Engine 並設定託管執行個體群組 (MIG) 的自動擴充。",
        "en": "(A) Use Compute Engine and configure autoscaling for Managed Instance Groups (MIG).",
        "wg": [
          {"t": "自動擴充", "en": "autoscaling", "ps": "N"}
        ]
      },
      {
        "t": "(B) 使用 Google Kubernetes Engine (GKE) Standard 叢集。",
        "en": "(B) Use Google Kubernetes Engine (GKE) Standard clusters.",
        "wg": [
        ]
      },
      {
        "t": "(C) 使用 Cloud Run 部署容器化服務。",
        "en": "(C) Deploy containerized services using Cloud Run.",
        "wg": [
        ]
      },
      {
        "t": "(D) 使用配備高效能 SSD 的專用機器類型。",
        "en": "(D) Use dedicated machine types equipped with high-performance SSDs.",
        "wg": [
        ]
      }
    ],
    "answer": "(C)",
    "why": {
      "t": "Cloud Run 支援將執行個體縮減為零，這對於流量無法預測且有閒置期的應用程式來說是最具成本效益的選擇，且屬於全託管服務 (Serverless)。",
      "en": "Cloud Run supports scaling instances to zero, which is the most cost-effective choice for applications with unpredictable traffic and idle periods, and it is a fully managed (Serverless) service.",
      "wg": [
        {"t": "成本效益", "en": "cost-effective", "ps": "Adj"},
        {"t": "全託管" , "en": "fully managed", "ps": "Adj"}
      ]
    }
  }
]
```
