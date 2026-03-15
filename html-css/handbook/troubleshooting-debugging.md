# 疑難排解與除錯流程：DevTools 深度應用 / Troubleshooting and Debugging Workflows: Deep Dive into DevTools

CSS 的除錯往往比邏輯程式碼更具挑戰性，因為 CSS 失敗時通常是「靜默」的（failing silently）——沒有錯誤訊息，只有看起來不對勁的畫面。本章節將建立一套系統化的除錯心法，並深入瀏覽器開發者工具（DevTools）中鮮為人知但極具威力的功能。

## Mental model｜心智模型

### 1. 渲染是「計算」的結果，而非僅是「樣式」的堆疊
**Rendering is a computation result, not just a stack of styles.**
很多開發者只看 DevTools 的 `Styles` 面板，試圖找出哪一行 CSS 生效。但真正的心智模型應該是關注 **Computed（計算後樣式）**。
- **Styles Panel**: 這是輸入（Input）。它顯示了所有競爭的規則、繼承關係與優先權（Specificity）。
- **Computed Panel**: 這是真理（Truth）。它是瀏覽器經過 Cascade（層疊）、Inheritance（繼承）與 Defaulting（預設值）計算後的最終數值。
- **Mental Shift**: 當畫面不如預期，先問「瀏覽器最終算出了什麼數值？」（Computed），再回頭找「是哪條規則導致這個計算結果？」（Styles）。

### 2. 佈局是「合約」關係
**Layout is a contract relationship.**
元素不會孤立存在。除錯時，必須理解該元素處於哪種 **Formatting Context（格式化上下文）** 中。
- 如果 `z-index` 不生效，是因為它沒有建立 Stacking Context。
- 如果 `width` 不生效，可能是因為它在 Flex container 中被壓縮（shrink）了。
- **Mental Shift**: 不要只盯著出問題的元素（The Child），要往上看它的容器（The Parent）簽訂了什麼佈局合約（Flex, Grid, Block, Position）。

---

## Patterns & best practices｜常見模式與最佳實務

### 1. 善用 Computed 面板追蹤來源 (Trace back via Computed)
不要在 `Styles` 面板大海撈針。
- **Pattern**: 點擊 `Computed` tab -> 勾選 `Show all` -> 搜尋屬性（如 `height`）。
- **Action**: 點擊數值旁的小箭頭，DevTools 會直接跳轉到定義該數值的具體 CSS 規則。這對於解決繼承問題（Inheritance issues）特別有效。

### 2. 視覺化佈局除錯 (Visual Layout Debugging)
現代 DevTools 提供了強大的視覺輔助，不要只靠猜測。
- **Flex/Grid Badges**: 在 DOM tree 中點擊 `flex` 或 `grid` 標籤。這會開啟 Overlay，顯示軌道（tracks）、間隙（gaps）與區域名稱。
- **Flexbox Inspector**: 在 Styles 面板中，點擊 `display: flex` 旁的小圖示，可以視覺化調整 `align-items` 或 `justify-content`，直接觀察變化。

### 3. 隔離變因演算法 (Isolation Algorithm / Wolf Fence)
當頁面佈局徹底崩壞（例如出現不明的橫向捲軸）時，使用二分法或刪除法。
- **Delete Node**: 在 Elements 面板直接按 `Delete` 刪除懷疑的 DOM 節點。如果問題消失，則兇手就在該節點或其子節點中。
- **Ghost Outline**: 使用全域 outline 找出溢出元素。
  ```css
  /* 在 Console 中輸入或暫時加入 CSS */
  * { outline: 1px solid red !important; }
  ```
  *Pro Tip: 使用 `outline` 而非 `border`，因為 `outline` 不佔據空間，不會改變 Box Model 導致佈局變動。*

### 4. 模擬狀態與內容 (Simulating States & Content)
- **Force State**: 在 Elements 面板右鍵 -> `Force state` -> 鎖定 `:hover`, `:focus`, `:active` 狀態，方便調整互動樣式。
- **Design Mode**: 直接在頁面上編輯文字以測試溢出（Overflow）狀況。
  ```javascript
  // 在 Console 輸入
  document.designMode = 'on'
  ```

---

## Anti-patterns & pitfalls｜反模式與踩雷點

### 1. 盲目嘗試與 Magic Numbers (Shotgun Debugging)
- **Anti-pattern**: 為了修復對齊問題，隨意添加 `margin-top: -3px` 或 `width: 99%`，直到看起來「差不多」對了。
- **Consequence**: 這些 Magic Numbers 在不同螢幕尺寸或字體渲染下必定破版，且極難維護。
- **Correction**: 找出導致對齊問題的根源（例如 `line-height`、`vertical-align` 或 Flexbox 的 `align-items`）。

### 2. 濫用 `!important` 解決衝突 (Specificity Wars)
- **Anti-pattern**: 樣式蓋不過去，就加上 `!important`。
- **Consequence**: 破壞了 CSS 的層疊機制，導致日後維護必須使用更強的 `!important`，陷入惡性循環。
- **Correction**: 檢查 Specificity（權重），利用 CSS Layers (`@layer`) 或增加選擇器特異性來解決，或者重構 HTML 結構。

### 3. 忽略 User Agent Styles (Default Styles Trap)
- **Anti-pattern**: 困惑為什麼有一個消不掉的間距，卻沒在自己的 CSS 裡找到設定。
- **Consequence**: 浪費時間除錯。
- **Correction**: 在 Computed 面板中，留意那些非粗體的數值，或是 Styles 面板中的 `user agent stylesheet`。常見於 `ul`, `p`, `body` 的預設 margin/padding。

### 4. 忽視 Stacking Context 的 `z-index` 陷阱
- **Anti-pattern**: 瘋狂增加 `z-index` 到 `99999`，但元素依然被蓋住。
- **Consequence**: 無效的修復。
- **Correction**: 檢查父層是否有 `transform`, `opacity`, `filter` 或 `isolation: isolate` 屬性，這些都會建立新的 Stacking Context，導致子元素的 `z-index` 無法與外部元素比較。

---

## Checklists & workflows｜檢查清單與流程

### The "Why is it broken?" Decision Tree
當遇到樣式問題時，請依照此順序檢查：

- [ ] **Syntax Check**: Console 有沒有 CSS 解析錯誤？（雖然 CSS 不會報錯，但 DevTools 會在無效屬性旁顯示黃色驚嘆號）。
- [ ] **Selector Match**: 選擇器真的有選到元素嗎？（在 Elements 面板確認該元素是否有吃到規則）。
- [ ] **Specificity Check**: 是否被其他權重更高的選擇器覆蓋？（看 Styles 面板是否有被劃掉的樣式）。
- [ ] **Computed Value**: 瀏覽器最終計算出的 Box Model（Margin/Border/Padding/Content）是多少？
- [ ] **Layout Context**:
    - 父層是 Flex/Grid 嗎？
    - 元素是否有 `width` 但被 `flex-shrink` 壓縮了？
    - 元素是否脫離了文檔流（Float/Absolute/Fixed）？
- [ ] **Stacking Context**: 如果是層級問題，檢查 **Layers Panel** 或父層是否建立了新的堆疊上下文。

### The "Overflow / Scrollbar" Checklist
當出現不預期的捲軸時：

- [ ] 檢查是否有固定寬度（Fixed Width）元素超過視窗寬度。
- [ ] 檢查是否有長單字或 URL 沒有設定 `word-break: break-all` 或 `overflow-wrap: break-word`。
- [ ] 檢查是否有元素使用了 `width: 100vw`，但忽略了捲軸本身的寬度（導致 100vw + scrollbar width > window width）。
- [ ] 使用 DevTools 的 **Layers** 面板查看是否有元素意外飛出視窗外。

---

## Real-world examples｜實戰案例

### Case 1: The `z-index` War (Modal 被 Header 蓋住)

**情境**: 你設定了 Modal 的 `z-index: 1000`，但它仍然被 `z-index: 10` 的 Header 蓋住。

**Debug 流程**:
1. **Inspect**: 選中 Modal，確認 `z-index` 有生效。
2. **Trace Up**: 往上檢查 Modal 的父容器。
3. **Discovery**: 發現 Modal 被包在一個 `opacity: 0.9` 的容器內（或是使用了 `transform` 做動畫）。
4. **Root Cause**: `opacity` 小於 1 會建立一個新的 **Stacking Context**。在這個 Context 內，`z-index: 1000` 只是「區域性」的最高，無法與外部的 Header 比較。
5. **Fix**: 將 Modal 移出該容器（移至 `<body>` 直屬），或移除父容器建立 Context 的屬性。

### Case 2: The Mysterious Horizontal Scroll (手機版破版)

**情境**: 手機版頁面出現橫向捲軸，且可以左右晃動，但看不出是哪個元素凸出去。

**Debug 流程**:
1. **Tool**: 開啟 DevTools 的 Device Toolbar 模擬手機。
2. **Script**: 在 Console 執行一段簡單的腳本找出溢出者：
   ```javascript
   document.querySelectorAll('*').forEach(el => {
     if (el.offsetWidth > document.documentElement.offsetWidth) {
       console.log('Overflowing element:', el);
       el.style.border = '5px solid red'; // 標記出來
     }
   });
   ```
3. **Visual Check**: 或者使用 `* { outline: 1px solid red }` 大法。
4. **Fix**: 發現是一個 `width: 600px` 的圖片沒有設定 `max-width: 100%`，或是某個 `padding` 撐大了 Box（忘記設定 `box-sizing: border-box`）。

### Case 3: Grid Layout Gaps (Grid 項目沒對齊)

**情境**: 使用 CSS Grid，但項目之間的位置很奇怪，不像預期的網格。

**Debug 流程**:
1. **Tool**: 在 Elements 面板，點擊 Grid 容器旁的 `grid` badge。
2. **Observation**: 畫面出現網格線（Grid Lines）和軌道（Tracks）。
3. **Discovery**: 發現多出了一個隱形的 "Implicit Track"（隱式軌道），或者某個項目意外跨了兩行。
4. **Fix**: 調整 `grid-template-columns` 或檢查子項目的 `grid-column` 設定，確保它們落在正確的 Line Number 之間。