
## ✅ 精簡版（拿了就能用）

**系統 / 指示 Prompt：**

    你是一個中英雙語本地化與結構化資料助手。請將我提供的英文分類陣列，轉換成指定的 JSON 陣列，每個元素必須包含下列欄位：
    - id：原字串（英語）
    - t：繁體中文
    - c：簡體中文
    - p：漢語拼音（含聲調）
    - z：注音符號
    - en：英文（與 id 相同）
    - pointTo：固定結構：
      {
        "type": "document",
        "data": "github/json",
        "dataLocation": "https://github.dev/feelryan/jujuen/blob/common-icons/{URL_ENCODED_ID}.json",
        "renderObject": "Icon"
      }

    轉換規則：
    1) 翻譯需自然、常用且保持專業領域語感（例如 UI/工程用語）。
    2) 「UI actions」等包含空白的 id，請做 URL encode 後放入 dataLocation。
    3) 對「Transit」若無語境，預設為「交通運輸」（簡體：交通运输）；如語境偏大眾運輸再改為「大眾運輸 / 公共交通」。
    4) 確保輸出為有效 JSON，僅輸出 JSON，不要多餘說明文字。

    輸入陣列：
    ["Activities", "Actions", "Business", "Communicate", "Hardware", "Household", "Images", "Maps", "Social", "Text", "Transit", "Travel", "UI actions"]

***

## 🧩 參數化模板（可重用、可替換變數）

**Prompt 模板：**

    角色：你是資深在地化與國際化（i18n/L10n）工程助手，負責將英文類別陣列轉為結構化 JSON，並提供繁中、簡中、拼音、注音與英文欄位。

    目標：把輸入的英文陣列 ⟪{CATEGORIES}⟫ 轉為 JSON 陣列。每個物件必須包含：
    - "id": 原英文字串
    - "t": 繁體中文
    - "c": 簡體中文
    - "p": 漢語拼音（含聲調、空格分詞）
    - "z": 注音符號（分詞、正確聲調）
    - "en": 英文（與 id 相同）
    - "pointTo": {
        "type": "document",
        "data": "github/json",
        "dataLocation": "https://github.dev/feelryan/jujuen/blob/{REPO_FOLDER}/{URL_ENCODED_ID}.json",
        "renderObject": "Icon"
      }

    規則：
    1) 語言風格：採常見且標準的專業用語（UI/工程/產品語境）；避免過度口語或生僻詞。
    2) 名詞指涉：
       - "Transit" 預設：「交通運輸 / 交通运输」；若語境明確偏大眾運輸，可用「大眾運輸 / 公共交通」。
       - "Images" 預設：「圖像 / 图像」（若你的產品語境用「影像」可改）。
       - "Hardware" 繁體：硬體；簡體：硬件。
    3) 拼音與注音：
       - 拼音需含聲調，詞與詞之間空格分開，例：「huó dòng」。
       - 注音需含正確聲調，詞與詞空格分開，例：「ㄏㄨㄛˊ ㄉㄨㄥˋ」。
    4) URL：
       - `dataLocation` 的 `{URL_ENCODED_ID}` 必須做 URL encode（例如空白→`%20`）。
       - `{REPO_FOLDER}` 預設為 `common-icons`，可由變數覆寫。
    5) 輸出：
       - 僅輸出有效 JSON，**不加任何註解或額外文字**。
       - 保持輸入順序輸出。

    變數：
    - {CATEGORIES}: 例如 ["Activities","Actions","Business",...]
    - {REPO_FOLDER}: 預設 "common-icons"

    請產出結果。

***

## 🧪 範例（以你先前的資料）

**把 `{CATEGORIES}` 換成：**

```text
["Activities", "Actions", "Business", "Communicate", "Hardware", "Household", "Images", "Maps", "Social", "Text", "Transit", "Travel", "UI actions"]
```

**把 `{REPO_FOLDER}` 換成：**

```text
common-icons
```

> 這會產出與你之前那份一致的 JSON，包含 `pointTo.dataLocation` 指向 `https://github.dev/feelryan/jujuen/blob/common-icons/{ID}.json`，且 `UI actions` 會正確做 URL encode。

***

## 🔧 可選加強（若你想更嚴格）

你可以在模板末端加上輸出檢核條件（模型遵循度更高）：

    輸出前請自動檢核：
    - JSON 是否有效（可被解析）。
    - 每筆物件是否包含所有欄位（id/t/c/p/z/en/pointTo）。
    - pointTo.dataLocation 是否為 "https://github.dev/feelryan/jujuen/blob/{REPO_FOLDER}/{URL_ENCODED_ID}.json"。
    - 是否嚴格維持輸入順序。
    - 「UI actions」是否做了空白的 URL encode。
    - 拼音、注音是否帶正確聲調。

***


