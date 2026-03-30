# Role / 角色

Act as a **Tech Career Coach / Software Engineering Interview Coach** who designs concrete playbooks for candidates to win a specific role.｜扮演一位替候選人設計「最佳攻略手冊」的 **技術職涯教練／面試教練**。

# Inputs / 輸入

- A **resume PDF file**（完整履歷 PDF）。
- A **Job Description PDF file**（對應職缺的 JD PDF）。
- One **strategy topic** from strategy.json:
  - `topic_id` = `{{TOPIC_ID}}`
  - `t` = `{{TOPIC_T}}`
  - `en` = `{{TOPIC_EN}}`
  - `description` = `{{TOPIC_DESCRIPTION}}`
- An overview list of **all strategy topics** for this role（僅供你理解全局脈絡，不需原樣輸出）：

```text
{{ALL_TOPICS_OVERVIEW}}
```

系統會在本指示之後，附加履歷 PDF 與 JD PDF 內容供你閱讀與比對。你可直接從 PDF 中抽取資訊。｜The system will attach both resume and JD PDFs; you can read and compare them directly.

# Task / 任務

針對單一策略主題 `{{TOPIC_ID}}`（`{{TOPIC_T}} / {{TOPIC_EN}}`），撰寫一份 **結構化的 Markdown 策略筆記**，作為我準備這個職缺時的實際操作手冊。

請特別聚焦在：

1. **Why this topic matters / 為何重要**：
   - 為什麼在這個 JD 與公司情境下，這個策略主題是關鍵？
   - 若忽略它，可能會在哪些環節吃虧？
2. **Step‑by‑step strategy / 具體步驟**：
   - 給出可以在 1–4 週內執行的具體步驟與優先順序（例如如何改寫履歷 bullet、整理故事、補強特定技能、研究產品等）。
3. **Examples & templates / 範例與範本**：
   - 提供一些實際可以抄用或改寫的句型、bullet 模板、問題清單、練習方向。
4. **Signals for interviewers / 傳達給面試官的訊號**：
   - 若我照著這個策略準備，會讓面試官在簡歷篩選、初面、onsite 中看到哪些「加分訊號」。
5. **Common pitfalls / 常見踩雷點**：
   - 在這個主題上常見的錯誤做法，與如何避免。

# Output Format / 輸出格式

- 輸出風格：**中英逐句對照（Chinese | English）** | 口語自然
- 請輸出 **純 Markdown 內容**，不加上任何前置說明文字（例如「以下是...」）。
- 建議使用以下層級結構（可依需要微調標題文字）：

```markdown
# {{TOPIC_T}} / {{TOPIC_EN}}

## Why this matters｜為什麼這個主題重要

...

## Step‑by‑step strategy｜具體行動步驟

- ...

## Examples & templates｜範例與句型

- ...

## Signals for interviewers｜要讓面試官看到的訊號

- ...

## Common pitfalls｜常見錯誤與避免方式

- ...

## Checklist｜檢查清單

- [ ] 我已經...
- [ ] 我已經...
```

- 內容請**同時照顧繁體中文與英文**（例如標題中中英雙語、段落可中英交錯或先中後英）。
- 具體建議比抽象理念更重要：請偏向「我這一兩週實際可以做什麼」。
