# 1. 前言與學習目標 (Introduction & Learning Objectives)

作為資深工程師，你可能已經習慣撰寫功能性的 React 組件。然而，當你的任務轉變為「建立跨團隊共用的 Component Library」或「設計高度可擴充的 UI 系統」時，單純的 Props 傳遞往往會導致 "Prop Drilling" 或 "God Components"（接受數十個 Props 的巨大組件）。本章的目標是透過 **Inversion of Control (IoC)** 的設計哲學，提升你的組件設計能力。

As a Senior Engineer, you are likely accustomed to writing functional React components. However, when your task shifts to "building a cross-team Component Library" or "designing a highly scalable UI system," simple prop passing often leads to "Prop Drilling" or "God Components" (massive components accepting dozens of props). The goal of this chapter is to elevate your component design skills through the philosophy of **Inversion of Control (IoC)**.

完成本章後，你將能夠：
By the end of this chapter, you will be able to:

1.  **實作 Compound Components**：讓使用者能自由安排子組件佈局，同時隱式共用狀態。
    **Implement Compound Components**: Allow consumers to arrange child component layouts freely while implicitly sharing state.
2.  **運用 Control Props 模式**：設計出既能「自我管理狀態」又能「受外部控制」的靈活組件（類似 HTML `<input>`）。
    **Apply the Control Props Pattern**: Design flexible components that can both "manage their own state" and be "controlled externally" (similar to HTML `<input>`).
3.  **理解 Headless UI 架構**：將邏輯與渲染完全分離，打造極致的可重用性與無障礙（Accessibility）支援。
    **Understand Headless UI Architecture**: Completely separate logic from rendering to achieve maximum reusability and accessibility support.
4.  **優化組件 API 設計**：從 Library 作者的角度思考，減少 Breaking Changes 並提升開發者體驗（DX）。
    **Optimize Component API Design**: Think from a library author's perspective to reduce breaking changes and improve Developer Experience (DX).

---

# 2. 核心觀念與心智模型 (Core Concepts & Mental Model)

## 2.1 控制反轉 (Inversion of Control - IoC)

在初階 React 開發中，父組件往往控制了「做什麼」以及「怎麼呈現」。進階模式的核心在於 **IoC**：父組件提供邏輯與狀態，但將「渲染細節」與「控制權」交還給使用者（Consumer）。

In junior React development, the parent component often dictates both "what to do" and "how to render." The core of advanced patterns lies in **IoC**: the parent provides logic and state but hands back the "rendering details" and "control" to the consumer.

### 類比 (Analogy)

-   **傳統組件 (Traditional Component)**：就像去餐廳點套餐。你只能選 A 餐或 B 餐，無法單獨更換配菜或擺盤方式。
    **Traditional Component**: Like ordering a set meal at a restaurant. You can only choose Set A or Set B; you cannot swap specific sides or change the plating.
-   **進階模式 (Advanced Patterns)**：就像自助餐（Buffet）或 IKEA 家具。圖書館提供所有零件（邏輯與基本樣式），使用者決定如何組裝、擺放以及何時觸發改變。
    **Advanced Patterns**: Like a buffet or IKEA furniture. The library provides all the parts (logic and base styles), and the user decides how to assemble them, place them, and when to trigger changes.

## 2.2 關鍵模式定義 (Key Pattern Definitions)

1.  **Compound Components**: 利用 `Context` 在父子組件間隱式傳遞狀態，讓使用者可以透過 JSX 巢狀結構定義 UI。
    **Compound Components**: Uses `Context` to implicitly pass state between parent and child components, allowing users to define UI via JSX nesting.
2.  **Control Props**: 允許使用者透過傳入 `value` 和 `onChange` 來接管組件狀態，若不傳入則組件退回內部自我管理模式。
    **Control Props**: Allows users to take over component state by passing `value` and `onChange`; if not passed, the component falls back to internal self-management.
3.  **Render Props / Function as Child**: 將渲染邏輯作為一個函數傳入，讓父組件決定「邏輯」，子函數決定「UI」。(雖然 Hooks 出現後較少用，但在某些 Library 中仍是強大的模式)。
    **Render Props / Function as Child**: Passes rendering logic as a function, letting the parent decide the "logic" and the child function decide the "UI". (Though less common after Hooks, it remains a powerful pattern in some libraries).
4.  **Headless UI**: 僅提供 Hooks（如 `useSelect`, `useToggle`）處理狀態、ARIA 屬性與互動邏輯，完全不提供 CSS 或 HTML 標籤。
    **Headless UI**: Provides only Hooks (e.g., `useSelect`, `useToggle`) to handle state, ARIA attributes, and interaction logic, providing zero CSS or HTML tags.

---

# 3. 實務場景與系統設計視角 (Real-World & System Design View)

在大型系統設計或 Design System 的建置中，這些模式決定了前端架構的**可維護性**與**一致性**。

In large-scale system design or Design System construction, these patterns determine the **maintainability** and **consistency** of the frontend architecture.

## 3.1 Design System 的分層架構 (Layered Architecture of Design Systems)

在 Production 環境中，我們通常會這樣分層：

In a production environment, we typically layer the architecture as follows:

1.  **Layer 1: Headless / Logic Layer (e.g., Radix UI Primitives, React Aria)**
    -   負責：State Machine, Accessibility (a11y), Keyboard Navigation.
    -   優勢：解決最困難的瀏覽器相容性與無障礙問題。
    -   **Responsibility**: State Machine, Accessibility (a11y), Keyboard Navigation.
    -   **Advantage**: Solves the hardest browser compatibility and accessibility issues.

2.  **Layer 2: Styled Component Layer (Your Company's UI Lib)**
    -   負責：將公司的 Brand Design (CSS/Tailwind) 綁定到 Layer 1 的邏輯上。
    -   使用模式：Compound Components, Control Props.
    -   **Responsibility**: Binds the company's Brand Design (CSS/Tailwind) to the logic of Layer 1.
    -   **Usage Patterns**: Compound Components, Control Props.

3.  **Layer 3: Application Layer (Product Features)**
    -   負責：組合 Layer 2 的組件來實現業務邏輯。
    -   **Responsibility**: Composes components from Layer 2 to implement business logic.

## 3.2 對系統品質的影響 (Impact on System Quality)

-   **可擴充性 (Extensibility)**: 當業務需求變更（例如：Dropdown 選單裡需要加一個 Search Bar），Compound Components 允許直接插入 `<SearchBar />` 而不需修改 Dropdown 的原始碼。
    **Extensibility**: When business requirements change (e.g., adding a Search Bar inside a Dropdown menu), Compound Components allow inserting a `<SearchBar />` directly without modifying the Dropdown's source code.
-   **關注點分離 (Separation of Concerns)**: 邏輯開發者專注於 `useSelect` 的狀態機測試；UI 設計師專注於樣式實作。
    **Separation of Concerns**: Logic developers focus on testing the state machine of `useSelect`; UI designers focus on style implementation.

---

# 4. 逐步示例 (Walkthrough / Example)

我們將以設計一個 **Accordion (手風琴)** 組件為例，展示從 Naive 到 Advanced 的演進。

We will use the design of an **Accordion** component to demonstrate the evolution from Naive to Advanced.

## Phase 1: The Naive Approach (Configuration Props)

最直覺的做法是透過一個巨大的 `items` 陣列來設定。

The most intuitive approach is configuring it via a massive `items` array.

```tsx
// ❌ Hard to customize content, rigid structure
const Accordion = ({ items, onChange }) => {
  return (
    <div>
      {items.map((item, index) => (
        <div key={index}>
          <button onClick={() => onChange(index)}>{item.title}</button>
          {item.isOpen && <div className="content">{item.content}</div>}
        </div>
      ))}
    </div>
  );
};
```

**問題 (Issues)**:
- 如果 `content` 裡面需要包含複雜的互動元件（如 Form）怎麼辦？
- 如果想要把 `button` 換到 `content` 下方怎麼辦？
- **What if** the `content` needs to contain complex interactive elements (like a Form)?
- **What if** we want to move the `button` below the `content`?

## Phase 2: Compound Components (Flexible Layout)

我們使用 React Context 來共享狀態，並拆分組件。

We use React Context to share state and split the components.

```tsx
import React, { createContext, useContext, useState, useMemo } from 'react';

// 1. Create Context
interface AccordionContextType {
  openIndex: number | null;
  setOpenIndex: (index: number) => void;
}
const AccordionContext = createContext<AccordionContextType | undefined>(undefined);

// 2. Parent Component
export const Accordion = ({ children }: { children: React.ReactNode }) => {
  const [openIndex, setOpenIndex] = useState<number | null>(null);
  
  // Memoize context value to prevent unnecessary re-renders
  const value = useMemo(() => ({ openIndex, setOpenIndex }), [openIndex]);

  return (
    <AccordionContext.Provider value={value}>
      <div className="accordion-root">{children}</div>
    </AccordionContext.Provider>
  );
};

// 3. Child Components
// Hook to consume context safely
const useAccordionContext = () => {
  const context = useContext(AccordionContext);
  if (!context) throw new Error("Accordion components must be used within <Accordion />");
  return context;
};

export const AccordionItem = ({ index, children }: { index: number, children: React.ReactNode }) => {
    // Usually, we might use React.Children.map to inject index automatically, 
    // but explicit index or ID is clearer for this demo.
    return <div className="accordion-item">{children}</div>;
};

export const AccordionHeader = ({ index, children }: { index: number, children: React.ReactNode }) => {
  const { openIndex, setOpenIndex } = useAccordionContext();
  const isOpen = openIndex === index;

  return (
    <button onClick={() => setOpenIndex(isOpen ? -1 : index)} aria-expanded={isOpen}>
      {children}
      {isOpen ? '🔼' : '🔽'}
    </button>
  );
};

export const AccordionPanel = ({ index, children }: { index: number, children: React.ReactNode }) => {
  const { openIndex } = useAccordionContext();
  if (openIndex !== index) return null;
  return <div className="accordion-panel">{children}</div>;
};

// Usage
// <Accordion>
//   <AccordionItem index={0}>
//     <AccordionHeader index={0}>Section 1</AccordionHeader>
//     <AccordionPanel index={0}>Content 1</AccordionPanel>
//   </AccordionItem>
// </Accordion>
```

## Phase 3: Control Props (Hybrid State)

現在，使用者希望能夠從外部控制 Accordion（例如：點擊外部按鈕時關閉所有 Panel）。我們需要支援 **Control Props**。

Now, the user wants to control the Accordion from the outside (e.g., close all panels when clicking an external button). We need to support **Control Props**.

這是一個常見的 Pattern，通常我們會封裝一個 `useControllableState` hook。

This is a common pattern, and we typically encapsulate it in a `useControllableState` hook.

```tsx
function useControllableState<T>({
  value: valueProp,
  defaultValue,
  onChange,
}: {
  value?: T;
  defaultValue?: T;
  onChange?: (value: T) => void;
}) {
  const [internalValue, setInternalValue] = useState(defaultValue);
  
  // Determine if it is controlled
  const isControlled = valueProp !== undefined;
  
  const value = isControlled ? valueProp : internalValue;

  const setValue = (newValue: T) => {
    if (!isControlled) {
      setInternalValue(newValue);
    }
    onChange?.(newValue);
  };

  return [value, setValue] as const;
}

// Refactored Parent Component
export const Accordion = ({ 
  index,         // Controlled prop
  defaultIndex,  // Uncontrolled prop
  onIndexChange, // Callback
  children 
}: any) => {
  const [openIndex, setOpenIndex] = useControllableState({
    value: index,
    defaultValue: defaultIndex,
    onChange: onIndexChange
  });

  const value = useMemo(() => ({ openIndex, setOpenIndex }), [openIndex, setOpenIndex]);

  return (
    <AccordionContext.Provider value={value}>
      <div className="accordion-root">{children}</div>
    </AccordionContext.Provider>
  );
};
```

**為何這在實務中可行？**
這讓你的組件既能像 `<input defaultValue="..." />` 一樣簡單易用（Uncontrolled），也能像 `<input value="..." onChange="..." />` 一樣完全受控（Controlled）。這是高品質 Library 的標配。

**Why is this practical?**
This makes your component as simple to use as `<input defaultValue="..." />` (Uncontrolled), while also being fully controllable like `<input value="..." onChange="..." />` (Controlled). This is a standard for high-quality libraries.

---

# 5. 常見錯誤與反模式 (Common Pitfalls & Anti-patterns)

## 5.1 過度封裝 (Over-Abstraction)
**錯誤**：試圖將所有 Compound Components 再次包裝成一個 Config-based 的組件，只為了「少寫幾行 code」。
**Pitfall**: Trying to wrap all Compound Components back into a Config-based component just to "save a few lines of code."

**為何不好**：你失去了 Compound Components 的靈活性（例如無法在 Header 和 Panel 之間插入一個 `<hr />`），重新引入了 Phase 1 的問題。
**Why it's bad**: You lose the flexibility of Compound Components (e.g., unable to insert an `<hr />` between Header and Panel), reintroducing the problems from Phase 1.

## 5.2 Context Value 沒有 Memoization
**錯誤**：在 Provider 中直接傳遞物件字面量 `value={{ state, setState }}`。
**Pitfall**: Passing an object literal directly in the Provider `value={{ state, setState }}`.

**為何不好**：每次父組件 render 時，`value` 都會是一個新的 reference，導致所有 Consumer 強制 re-render，即使狀態根本沒變。這在大型列表中是效能殺手。
**Why it's bad**: Every time the parent renders, `value` becomes a new reference, forcing all Consumers to re-render, even if the state hasn't changed. This is a performance killer in large lists.

## 5.3 忽略 `ref` 轉發 (Ignoring Ref Forwarding)
**錯誤**：封裝組件時沒有使用 `React.forwardRef`。
**Pitfall**: Not using `React.forwardRef` when wrapping components.

**為何不好**：使用者無法獲取 DOM 節點來處理 Focus Management 或動畫整合。對於 Headless UI 來說，能夠存取底層 DOM 是至關重要的。
**Why it's bad**: Consumers cannot access the DOM node for Focus Management or animation integration. For Headless UI, accessing the underlying DOM is crucial.

---

# 6. 面試與實務問答切入點 (Interview & Discussion Hooks)

這些問題可用於評估候選人對 React 架構的理解深度。

These questions can be used to assess a candidate's depth of understanding of React architecture.

## Q1: 你會如何設計一個供全公司使用的 Modal 組件？
**How would you design a Modal component for company-wide use?**

*   **高分回答要點 (Key Points)**:
    *   提到 **Portal**：避免 `z-index` 戰爭。
    *   提到 **Compound Components**：`<Modal.Header>`, `<Modal.Body>`, `<Modal.Footer>` 以支援不同內容佈局。
    *   提到 **Context**：管理 `isOpen` 狀態與關閉函數。
    *   提到 **Accessibility**：Focus trap（焦點鎖定）、ESC 鍵關閉、ARIA roles。
    *   提到 **Control Props**：支援外部控制顯示/隱藏。

## Q2: 解釋 Controlled 與 Uncontrolled 組件的差異，以及如何在同一個組件中支援兩者？
**Explain the difference between Controlled and Uncontrolled components, and how to support both in a single component?**

*   **高分回答要點 (Key Points)**:
    *   定義：Controlled 依賴 Props (`value`), Uncontrolled 依賴內部 State (`ref` 或 `useState`).
    *   實作：描述類似 `useControllableState` 的邏輯——檢查 `value` prop 是否存在來決定 Source of Truth。
    *   場景：Form libraries (React Hook Form) 通常偏好 Uncontrolled 以優化效能；複雜的業務邏輯連動通常需要 Controlled。

## Q3: 什麼時候該用 Render Props，什麼時候該用 Custom Hooks？
**When should you use Render Props versus Custom Hooks?**

*   **高分回答要點 (Key Points)**:
    *   **Hooks**：是邏輯重用的首選（Headless UI）。它們不產生 DOM，更乾淨。
    *   **Render Props**：當你需要將「渲染權」交給使用者，但「資料來源」在組件內部時（例如 `VirtualList` 渲染每一列，或某些動畫庫）。
    *   趨勢：大部分 Render Props 場景已被 Hooks 取代，但在處理 JSX 結構動態注入時，Render Props 仍有其語意上的優勢。

---

# 7. 小結與後續延伸 (Summary & Next Steps)

## 記憶錨點 (Key Takeaways)

1.  **Inversion of Control (IoC)** 是進階組件設計的核心，將控制權交還給開發者。
2.  **Compound Components** 解決了佈局彈性與 Prop Drilling 問題。
3.  **Control Props** 讓組件同時支援受控（Controlled）與非受控（Uncontrolled）模式。
4.  **Headless UI** 是打造 Design System 的最佳實踐，分離了邏輯與樣式。
5.  永遠記得對 Context Value 進行 **Memoization** 以避免效能陷阱。

## 後續延伸 (Next Steps)

*   **實作練習**：嘗試使用 `createContext` 和 `useControllableState` 重構你現有的 Dropdown 或 Modal 組件。
*   **閱讀原始碼**：閱讀 [Radix UI](https://www.radix-ui.com/) 或 [Reach UI](https://reach.tech/) 的原始碼，看看它們如何實作 Headless Pattern。
*   **下一章預告**：掌握了組件設計模式後，下一章我們將探討 **React Performance Optimization**（效能優化），深入了解 Re-render 機制與 Concurrency Mode。