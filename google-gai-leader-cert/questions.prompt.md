請從上傳的generative_ai_leader_exam_guide_english.pdf和generative_ai_leader_study_guide_english.pdf, 根據其文件說明產生120~150題目或題組, 要盡可能夠涵蓋考試範圍及內容並且實際考題越像越好，最後依照下列嚴格定義的 JSON 格式產出。如無法一次完成產出, 則說明需要如何指示來讓你分次產出.

**產出格式規則：**

1. **分句原則**：題目與解釋須以句號或段落為界進行分句。
2. **多語支援**：每句需包含繁體 (t)及英文 (en)。
3. **字詞分組 (wg)**：針對每個分句，識別出具備特別意義的中文字詞群組其英文翻譯相對困難的。提供該字詞在該分句字中的繁體中文 (t)、英文翻譯 (en) 及詞性 (ps)。
4. **解釋邏輯 (why)**：解釋答案以及為什麼其他選項是錯誤的，並同步提供英文版。

5. **選項隨機分佈** ：禁止將正確答案固定放在第一個選項 (A)。正確答案必須在 (A), (B), (C), (D), ... 之間隨機分佈。例如在每一批次的 5 題中，答案的分佈應盡可能平衡（例如：A, C, B, D, A），避免出現連續兩題答案相同或過度集中於某一字母的情況。

6. **複選題比例** : 複選題比例應佔每批次產出的10%, 

7. **禁止符號:** **嚴格禁止**產出任何引用標記如 `[cite]` 或 ``。

**JSON 欄位縮寫定義：**

* `t`: 繁體中文, `en`: 英文
* `wg`: 字詞群組, `ps`: 詞性

**產出格式：**

```json
{
  "no": "<題號>",
  "level": "<難易度>",
  "keywords": "<英文關鍵字(可多個,以逗號區隔)>",
  "parentNo": "<如果此為子題,則有母題的題號, 若無則為null>",
  "images": "<如果有圖片的話,則產生圖檔連結>",
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

```

---

### sample：

```json
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
```
