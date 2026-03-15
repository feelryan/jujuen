# 進階組件設計模式 / Advanced Component Patterns

## Mental model｜心智模型

在 React 初學階段，我們習慣將 UI 視為「接收資料並顯示的樣板」；但在進階階段，你需要將組件視為 **API 設計**。核心的心智模型是 **Inversion of Control (IoC, 控制反轉)**。

### 1. Don't Configure, Compose (不要配置，要組合)
初階組件往往充滿了「配置型 Props」（例如 `hasIcon`, `isBlue`, `showFooter`）。隨著需求增加，這些 Props 會指數級爆炸。
進階模式的核心在於：**不再試圖預測所有可能的 UI 變體，而是將「渲染什麼」的控制權交還給使用者（開發者）。**

### 2. Separation of Logic and View (邏輯與視圖分離)
將「狀態機（State Machine）」與「DOM 結構」拆開。
- **Headless (無頭模式)**：負責處理狀態、事件監聽、Accessibility (A11y)。
- **Visual (視覺組件)**：負責 CSS、Layout、Theme。

### 3. Implicit State Sharing (隱式狀態共享)
當一組組件必須協同工作（如 `<Select>` 與 `<Option>`），不應強迫使用者手動傳遞 `selectedId` 或 `onSelect` 給每一個子組件。應透過 Context 建立隱形的通訊管道。

---

## Patterns & best practices｜常見模式與最佳實務

### 1. Compound Components (複合組件)
讓多個組件共享隱式狀態，提供靈活的 UI 排版能力。

*   **Use Case**: Menu, Tabs, Accordion, Select.
*   **How**: 使用 `React.createContext` 在父層提供狀態，子層消費狀態。
*   **Benefit**: 使用者可以自由調整子組件順序，或插入額外的 DOM 元素（如 `<div>` wrapper），而不破壞邏輯。

```jsx
// Usage Example
<Tabs>
  <div className="sidebar">
    <Tabs.List>
      <Tabs.Trigger value="a">Tab A</Tabs.Trigger>
    </Tabs.List>
  </div>
  <Tabs.Content value="a">Content A</Tabs.Content>
</Tabs>
```

### 2. Control Props (受控屬性模式)
允許組件既可以是「受控 (Controlled)」也可以是「非受控 (Uncontrolled)」。這是高品質 UI Library (如 MUI, AntD) 的標準實作。

*   **Pattern**: 同時接受 `value` (受控) 與 `defaultValue` (非受控)。
*   **Implementation**: 內部判斷 `value` 是否為 `undefined` 來決定使用內部 state 還是外部 props。

### 3. Render Props (渲染屬性)
雖然 Hooks 取代了 Render Props 在「邏輯復用」上的地位，但在 **「渲染客製化」** 上，Render Props 仍然強大。

*   **Use Case**: Virtual List (虛擬列表)、複雜的動畫組件、Layout 容器。
*   **Concept**: 將 `children` 定義為一個函數，將內部狀態暴露給 UI 層。

```jsx
// List component handles logic (iteration), User handles UI
<List data={items} renderItem={(item) => <CustomCard item={item} />} />
```

### 4. Headless Hooks & Prop Getters
這是目前最現代化的模式（參考 Radix UI, React Aria, TanStack Table）。

*   **Concept**: 組件完全不渲染 DOM，只回傳屬性集合 (Prop Collections) 和狀態。
*   **Prop Getters**: 使用函數來合併使用者的 props 與內部的 props (特別是 Event Handlers)。

```jsx
// Inside your custom hook
const useToggle = () => {
  const [on, setOn] = useState(false);
  const toggle = () => setOn(!on);
  
  // Prop Getter pattern
  const getTogglerProps = ({ onClick, ...props } = {}) => ({
    onClick: (e) => {
      onClick && onClick(e); // Call user's handler
      toggle(); // Call internal handler
    },
    'aria-pressed': on,
    ...props,
  });

  return { on, getTogglerProps };
};
```

---

## Anti-patterns & pitfalls｜反模式與踩雷點

### 1. The "God Component" (上帝組件)
*   **Symptom**: 一個組件擁有超過 10 個以上的 Props，且包含大量 `boolean` flags (e.g., `isPrimary`, `hasShadow`, `withIcon`, `renderFooterAsLink`)。
*   **Consequence**: 維護困難，任何小的 UI 變更都需要修改組件內部邏輯。
*   **Fix**: 使用 **Composition**。與其傳入 `title="Hello"` 和 `renderTitleIcon={true}`，不如直接讓使用者傳入 `<Header>Hello <Icon /></Header>`。

### 2. Over-using Context for Everything (濫用 Context)
*   **Symptom**: 為了避免 Prop Drilling，建立了一個巨大的 Context 包裹整個應用，導致任何小變動都觸發全域重繪。
*   **Fix**: Context 應該 **Colocate (就近配置)**。只在 Compound Components 的父層建立 Context，或者使用專門的狀態管理工具。

### 3. Mixing Logic and UI too tightly (邏輯與 UI 耦合過深)
*   **Symptom**: 在一個 Dropdown 組件內寫死了特定的 CSS class 或 HTML 結構，導致另一個專案無法復用該邏輯。
*   **Fix**: 抽離出 `useDropdown` hook，或是使用 Headless UI library。

### 4. Prop Drilling through Composition (透傳地獄)
*   **Symptom**: `Component A` 接收 props 只是為了傳給 `Component B`，B 又傳給 C。
*   **Fix**: 使用 **Component Composition (Slot pattern)**。
    *   *Bad*: `<Layout user={user} />` -> Layout 內部傳給 Header -> Header 傳給 Avatar。
    *   *Good*: `<Layout header={<Header user={user} />} />`。

---

## Checklists & workflows｜檢查清單與流程

在設計一個新的通用組件（Shared Component）時，請依序檢查：

### Decision Tree: Choosing the Right Pattern
1.  **這個組件是否包含複雜的互動邏輯（如鍵盤導航、焦點管理）？**
    *   Yes -> 考慮 **Headless Hook** 或 **Compound Components**。
    *   No -> 普通組件即可。
2.  **UI 是否需要高度客製化（例如 Select 的選項樣式）？**
    *   Yes -> 使用 **Compound Components** 或 **Render Props**。
    *   No -> 使用 Props 配置即可。
3.  **這個組件是否需要同時支援受控與非受控模式？**
    *   Yes -> 實作 **Control Props** 模式。

### Refactoring Checklist (重構檢查)
- [ ] **Prop Explosion Test**: 檢查是否有超過 3 個 boolean props 是用來控制顯示/隱藏某個區塊的？如果是，改用 `children` 或 `slots`。
- [ ] **HTML Flexibility**: 使用者是否能輕易地將內部的 `<h3>` 改為 `<h1>`？如果不能，考慮 Render Props 或 Compound Components。
- [ ] **A11y Check**: 互動邏輯是否包含了適當的 `aria-*` 屬性？如果是 Headless Hook，確保 `getProps` 回傳了這些屬性。
- [ ] **Ref Forwarding**: 通用組件是否使用了 `forwardRef`？這對於整合 Tooltip 或測量尺寸至關重要。

---

## Real-world examples｜實戰案例

### Case 1: The "Card" Refactor (Composition)

**Before (Configuration Hell):**
```jsx
// 難以擴充，如果我想在 title 旁加個按鈕怎麼辦？
<Card 
  title="My Project" 
  subtitle="Created 2 days ago"
  imageSrc="/img.png"
  onImageClick={...}
  hasShadow={true}
  footerText="Read more"
/>
```

**After (Composition & Compound):**
```jsx
// 靈活，結構一目了然，樣式易於客製
<Card elevation="high">
  <Card.Image src="/img.png" onClick={...} />
  <Card.Body>
    <div className="flex justify-between">
       <Card.Title>My Project</Card.Title>
       <Badge>New</Badge>
    </div>
    <Card.Subtitle>Created 2 days ago</Card.Subtitle>
  </Card.Body>
  <Card.Footer>
    <Button>Read more</Button>
  </Card.Footer>
</Card>
```

### Case 2: Headless Modal (Separation of Concerns)

我們不寫一個帶有樣式的 `<Modal>`，而是寫一個 `useModal` hook 處理邏輯（開關、ESC 關閉、鎖定 Scroll）。

```jsx
// 1. Logic (The Brain)
const { isOpen, open, close, getOverlayProps, getContentProps } = useModal();

// 2. UI (The Skin) - 可以是任何 CSS Framework
return (
  <>
    <button onClick={open}>Open Modal</button>
    
    {isOpen && (
      <div {...getOverlayProps()} className="fixed inset-0 bg-black/50">
        <div {...getContentProps()} className="bg-white p-4 rounded">
          <h2>Title</h2>
          <button onClick={close}>Close</button>
        </div>
      </div>
    )}
  </>
);
```

### Case 3: Polymorphic Components (多型組件)

建立一個可以變身為 `a` tag 或 `button` 的組件，常用于 Design System。

```tsx
type ButtonProps<T extends React.ElementType> = {
  as?: T;
  children: React.ReactNode;
} & React.ComponentPropsWithoutRef<T>;

const Button = <T extends React.ElementType = 'button'>({ 
  as, 
  children, 
  ...props 
}: ButtonProps<T>) => {
  const Component = as || 'button';
  return <Component className="btn" {...props}>{children}</Component>;
};

// Usage
<Button as="a" href="/link">I am a Link</Button>
<Button onClick={doSomething}>I am a Button</Button>
```