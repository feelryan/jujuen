# 語意化與無障礙實戰：建構可訪問的 UI 元件 / Semantics and Accessibility in Practice: Building Accessible UI Components

## Mental model｜心智模型

要掌握無障礙網頁設計（Accessibility, A11y），不能只看視覺呈現，必須理解瀏覽器如何將 HTML 轉換為輔助科技（Assistive Technology, AT）能理解的資訊。

### 1. DOM vs. AOM (Accessibility Object Model)
瀏覽器不僅會建立 DOM Tree 來渲染畫面，還會平行建立一棵 **Accessibility Tree**。螢幕閱讀器（Screen Reader）讀取的是 Accessibility Tree，而非視覺上的像素。
- **HTML 標籤** 是這棵樹的「預設建材」。
- **ARIA (Accessible Rich Internet Applications)** 是當預設建材不足時，用來修補或增強這棵樹的「API」。

### 2. The "Native First" Rule｜原生優先原則
**"No ARIA is better than bad ARIA."**
這是 A11y 的黃金法則。原生的 HTML 元素（如 `<button>`, `<input>`, `<select>`）內建了完整的鍵盤互動、焦點管理與語意宣告。
- 當你使用 `<div onClick={...}>` 來模擬按鈕時，你實際上是在「違約」。你必須手動補回所有原生按鈕的功能（Focus, Enter/Space 觸發, Role 宣告），這通常既困難又容易出錯。

### 3. The Interaction Contract｜互動契約
每個 UI 元件都與使用者有一份隱形的契約：
- **Role (角色)**：我是什麼？(Button, Tab, Dialog)
- **Name (名稱)**：我叫什麼？(Label, aria-label)
- **State (狀態)**：我現在的情況？(Expanded, Selected, Disabled)
- **Value (數值)**：我的內容是什麼？(Input value)

你的工作就是確保這四個維度在任何時刻都是準確且同步的。

---

## Patterns & best practices｜常見模式與最佳實務

在實作常見 UI 元件時，請遵循以下 WAI-ARIA Design Patterns。

### 1. The Modal / Dialog Pattern (模態對話框)
Modal 是最容易做錯的元件。它必須攔截使用者的注意力與操作。
- **Container**: 使用 `role="dialog"` 或 `role="alertdialog"`。
- **Focus Trap (焦點鎖定)**：當 Modal 開啟時，`Tab` 鍵只能在 Modal 內部循環，不能跳回背景頁面。
- **Background Inertia**：背景內容應設為 `aria-hidden="true"` 或使用 `inert` 屬性，防止螢幕閱讀器讀到背景。
- **Escape to Close**：必須支援 `Esc` 鍵關閉。
- **Return Focus**：關閉後，焦點必須「歸還」給當初觸發 Modal 的按鈕。

### 2. The Disclosure Pattern (折疊/展開, Dropdown)
適用於 Accordion、Hamburger Menu 或簡單的 Show/Hide 區塊。
- **Trigger**: 必須是 `<button>`（不是 `<a>` 或 `<div>`）。
- **Relationship**: 按鈕上需有 `aria-expanded="true/false"` 與 `aria-controls="ID_of_content"`。
- **Content**: 內容區塊不需要特殊的 role，但需要對應的 ID。

### 3. The Tabs Pattern (分頁籤)
Tabs 不是單純的按鈕排列，它有嚴格的結構要求。
- **Wrapper**: `role="tablist"` 包裹所有標籤。
- **Trigger**: 每個標籤是 `role="tab"`，且需設定 `aria-selected="true/false"`。
- **Panel**: 內容區塊是 `role="tabpanel"`，需透過 `aria-labelledby` 關聯到對應的 tab。
- **Keyboard**: 應支援左右方向鍵（Arrow Keys）切換 Tab 焦點，`Tab` 鍵則進入 Panel 內容。

### 4. Visually Hidden (視覺隱藏但可讀)
設計上常有「只有 icon 的按鈕」，這對視障使用者是災難。
- **Do**: 使用 CSS class (如 `.sr-only` 或 `.visually-hidden`) 將文字移出視覺範圍，但保留在 DOM 中供螢幕閱讀器讀取。
- **Don't**: 使用 `display: none` 或 `visibility: hidden`，這會同時對螢幕閱讀器隱藏內容。

```css
/* Standard .sr-only class */
.sr-only {
  position: absolute;
  width: 1px;
  height: 1px;
  padding: 0;
  margin: -1px;
  overflow: hidden;
  clip: rect(0, 0, 0, 0);
  white-space: nowrap;
  border: 0;
}
```

---

## Anti-patterns & pitfalls｜反模式與踩雷點

### 1. The "Clickable Div" Syndrome
```html
<!-- ❌ BAD: 沒有語意，無法用鍵盤操作 -->
<div class="btn" onclick="submit()">Submit</div>

<!-- ✅ GOOD: 原生支援 Focus 與 Enter/Space -->
<button class="btn" onclick="submit()">Submit</button>
```
**後果**：鍵盤使用者無法 Tab 到此元素，也無法按 Enter 觸發。

### 2. Outline: None (Focus 樣式移除)
設計師常覺得瀏覽器預設的藍色外框很醜。
```css
/* ❌ VERY BAD: 鍵盤使用者會迷失方向 */
*:focus { outline: none; }
```
**修正**：如果移除了預設 outline，**必須** 提供自定義的 `:focus-visible` 樣式。

### 3. Button vs. Link Confusion
- **Link (`<a>`)**：導航到另一個頁面或錨點（URL 改變）。
- **Button (`<button>`)**：執行頁面內的動作（提交表單、打開 Modal、切換開關）。
**陷阱**：不要為了樣式把 `<a>` 當按鈕用，也不要給 `<a>` 加 `role="button"` 除非你完全接管了鍵盤事件（如空白鍵觸發）。

### 4. Redundant ARIA (冗餘的 ARIA)
HTML5 標籤大多已有隱含的 role。
```html
<!-- ❌ Redundant -->
<nav role="navigation">
<button role="button">
<h1 role="heading" aria-level="1">

<!-- ✅ Clean -->
<nav>
<button>
<h1>
```
過度使用 ARIA 會增加程式碼雜訊，甚至覆蓋原生的正確行為。

### 5. Placeholder as Label
```html
<!-- ❌ BAD: 輸入內容後 Label 消失，Screen Reader 支援度不一 -->
<input type="text" placeholder="Email">

<!-- ✅ GOOD: 視覺可見且程式關聯的 Label -->
<label for="email">Email</label>
<input id="email" type="text">
```

---

## Checklists & workflows｜檢查清單與流程

在開發 UI 元件或進行 Code Review 時，請使用此清單：

### Semantic Structure
- [ ] 是否優先使用了原生 HTML 元素（`<button>`, `<input>`, `<nav>` 等）？
- [ ] 標題結構（`h1` - `h6`）是否依層級順序排列，沒有跳級？
- [ ] 圖片是否有具意義的 `alt` 文字？（裝飾性圖片應設為 `alt=""`）。

### Keyboard Navigation
- [ ] **Tab Order**: 能否只用 `Tab` 鍵依序瀏覽所有互動元件？順序是否符合視覺邏輯？
- [ ] **Visual Focus**: 當元件獲得焦點時，是否有清晰可見的 Focus Ring？
- [ ] **Operation**: 按鈕能否用 `Enter` 和 `Space` 觸發？連結能否用 `Enter` 觸發？
- [ ] **Esc**: Modal 或 Popover 能否按 `Esc` 關閉？

### ARIA & States
- [ ] 動態元件（Dropdown, Modal）是否正確使用了 `aria-expanded`, `aria-hidden` 或 `aria-selected`？
- [ ] 狀態改變時，螢幕閱讀器是否會收到通知（例如使用 `aria-live` 於錯誤訊息）？
- [ ] 表單控制項是否有關聯的 `<label>` 或 `aria-label`？

### Automated Testing
- [ ] 是否通過了 Lighthouse 或 axe-core 的自動化檢測？（這能抓出約 30-50% 的基本錯誤）。

---

## Real-world examples｜實戰案例

### Case: Accessible Custom Dropdown (Disclosure Pattern)

這是一個常見的「使用者選單」實作，展示如何正確綁定 ARIA 屬性。

#### HTML Structure
```html
<div class="user-menu">
  <!-- 1. Trigger Button -->
  <!-- aria-expanded: 告知當前開合狀態 -->
  <!-- aria-controls: 告知此按鈕控制哪個區塊 -->
  <button
    type="button"
    id="user-menu-btn"
    aria-expanded="false"
    aria-controls="user-menu-content"
    aria-haspopup="true"
  >
    <span>John Doe</span>
    <!-- 視覺上的箭頭 icon，對 SR 隱藏 -->
    <svg aria-hidden="true" ... ></svg>
  </button>

  <!-- 2. Content Panel -->
  <!-- id: 對應 button 的 aria-controls -->
  <!-- hidden: 預設隱藏 -->
  <div id="user-menu-content" hidden>
    <ul>
      <li><a href="/profile">Profile</a></li>
      <li><a href="/settings">Settings</a></li>
      <li><button type="button">Logout</button></li>
    </ul>
  </div>
</div>
```

#### JavaScript Logic (Vanilla JS Example)
```javascript
const btn = document.getElementById('user-menu-btn');
const content = document.getElementById('user-menu-content');

btn.addEventListener('click', () => {
  // 1. Toggle visual state
  const isExpanded = btn.getAttribute('aria-expanded') === 'true';
  
  // 2. Update ARIA state (Crucial!)
  btn.setAttribute('aria-expanded', !isExpanded);
  
  // 3. Toggle visibility
  if (isExpanded) {
    content.hidden = true;
  } else {
    content.hidden = false;
  }
});

// Optional: Close on Esc key or click outside (Best Practice)
```

### Case: Form Error Handling
當表單驗證失敗時，如何讓使用者立即知道？

```html
<label for="email">Email</label>
<!-- aria-describedby: 連結錯誤訊息 -->
<!-- aria-invalid: 告知目前數值無效 -->
<input 
  type="email" 
  id="email" 
  aria-describedby="email-error" 
  aria-invalid="true"
>

<!-- aria-live="polite": 當內容出現時，SR 會在適當時機朗讀 -->
<div id="email-error" class="error-msg" aria-live="polite">
  Invalid email format.
</div>
```