# Python 設計模式與架構原則
# Design Patterns & Architecture Principles

## 1. 前言與學習目標
## 1. Introduction & Learning Objectives

在資深工程師的職涯階段，寫出「能動的程式碼」已不再是挑戰，真正的挑戰在於如何設計出「可測試、可維護且易於擴充」的系統。Python 雖然靈活，但也容易因為缺乏結構約束而導致程式碼變成「義大利麵條（Spaghetti Code）」。本章將探討如何將經典的軟體工程原則應用於 Python 專案中。

At the Senior Engineer career stage, writing "working code" is no longer the challenge. The real challenge lies in designing systems that are "testable, maintainable, and extensible." While Python is flexible, this lack of structural constraint can easily lead to "Spaghetti Code." This chapter explores how to apply classic software engineering principles specifically to Python projects.

完成本章後，你將能夠：
By the end of this chapter, you will be able to:

1.  **運用 SOLID 原則重構 Python 程式碼**：特別是如何利用 Python 的 `Protocol` 與 `ABC` 來實現依賴反轉（DIP）。
    **Refactor Python code using SOLID principles**: Specifically, utilizing Python's `Protocol` and `ABC` to implement Dependency Inversion (DIP).
2.  **實作 Clean Architecture（整潔架構）**：將業務邏輯與框架（如 FastAPI, Django）解耦，提升系統的可移植性。
    **Implement Clean Architecture**: Decoupling business logic from frameworks (like FastAPI, Django) to enhance system portability.
3.  **掌握 Pythonic 的依賴注入（Dependency Injection）**：區分何時該使用簡單的參數傳遞，何時該引入 DI 容器（Dependency Injection Containers）。
    **Master Pythonic Dependency Injection**: Distinguish when to use simple argument passing versus when to introduce DI containers.
4.  **識別過度設計（Over-engineering）的陷阱**：避免將 Java/C# 的繁瑣模式生搬硬套到 Python 中。
    **Identify Over-engineering pitfalls**: Avoid blindly applying verbose Java/C# patterns to Python.

---

## 2. 核心觀念與心智模型
## 2. Core Concepts & Mental Model

### 2.1 Duck Typing vs. Structural Subtyping (Protocols)
### 2.1 Duck Typing vs. Structural Subtyping (Protocols)

傳統 Python 強調「鴨子型別（Duck Typing）」——「如果它走起來像鴨子，叫起來像鴨子，那它就是鴨子」。這賦予了極大的靈活性，但在大型系統中，缺乏明確合約（Contract）會導致重構困難。

Traditional Python emphasizes "Duck Typing"—"If it walks like a duck and quacks like a duck, then it must be a duck." This grants immense flexibility, but in large systems, the lack of explicit contracts makes refactoring difficult.

**現代 Python（Python 3.8+）的心智模型轉變：**
我們使用 `typing.Protocol` 來實現「結構化子型別（Structural Subtyping）」。這類似於 Go 的 interface 或 TypeScript 的 interface。它保留了鴨子型別的靈活性（不需要顯式繼承），但提供了靜態型別檢查的安全性。

**The Mental Model Shift in Modern Python (Python 3.8+):**
We use `typing.Protocol` to implement "Structural Subtyping." This is similar to Go's interfaces or TypeScript's interfaces. It retains the flexibility of duck typing (no explicit inheritance required) but provides the safety of static type checking.

### 2.2 依賴反轉原則 (DIP) 與依賴注入 (DI)
### 2.2 Dependency Inversion Principle (DIP) & Dependency Injection (DI)

*   **DIP (原則)**：高層模組（業務邏輯）不應依賴低層模組（資料庫驅動、API Client）；兩者都應依賴於抽象介面。
    **DIP (Principle)**: High-level modules (business logic) should not depend on low-level modules (DB drivers, API Clients); both should depend on abstractions.
*   **DI (手段)**：不要在類別內部 `import` 或 `new` 具體的依賴物件，而是透過建構式（Constructor）將其傳入。
    **DI (Technique)**: Do not `import` or `new` concrete dependency objects inside a class; instead, pass them in via the constructor.

### 2.3 整潔架構 (Clean Architecture) 的洋蔥模型
### 2.3 The Onion Model of Clean Architecture

想像系統是一個洋蔥，依賴關係只能**由外向內**指向。

Imagine the system as an onion, where dependencies can only point **inwards**.

1.  **Core (Entities & Use Cases)**: 純 Python 物件，不依賴任何外部庫（SQLAlchemy, Pandas, HTTP requests）。
    **Core (Entities & Use Cases)**: Pure Python objects, independent of external libraries (SQLAlchemy, Pandas, HTTP requests).
2.  **Adapters (Gateways/Repositories)**: 實作 Core 定義的介面，負責與外部世界溝通。
    **Adapters (Gateways/Repositories)**: Implement interfaces defined by the Core, responsible for communicating with the outside world.
3.  **Infrastructure (Frameworks/DBs)**: 最外層，如 Flask, FastAPI, Postgres。
    **Infrastructure (Frameworks/DBs)**: The outermost layer, such as Flask, FastAPI, Postgres.

---

## 3. 實務場景與系統設計視角
## 3. Real-World & System Design View

### 3.1 為什麼這對 Senior Engineer 很重要？
### 3.1 Why does this matter for Senior Engineers?

在 System Design 面試或實務架構決策中，你常會遇到以下需求：
In System Design interviews or practical architectural decisions, you often encounter the following requirements:

*   **可測試性 (Testability)**：你需要對核心業務邏輯進行單元測試，但不想真的連線到 AWS S3 或 Production Database。透過 DI 與 Protocol，你可以輕鬆注入 Mock 物件。
    **Testability**: You need to unit test core business logic without actually connecting to AWS S3 or the Production Database. Through DI and Protocols, you can easily inject Mock objects.
*   **技術債管理 (Tech Debt Management)**：今天用 MongoDB，明年可能要換成 PostgreSQL。若業務邏輯與 DB 驅動強耦合，重寫成本極高。Repository Pattern 解決了這個問題。
    **Tech Debt Management**: You use MongoDB today, but might switch to PostgreSQL next year. If business logic is tightly coupled with DB drivers, the rewrite cost is prohibitive. The Repository Pattern solves this.

### 3.2 架構圖示 (文字版)
### 3.2 Architectural Diagram (Text Version)

一個典型的 Python 微服務架構如下：

A typical Python microservice architecture looks like this:

```text
[ HTTP Layer (FastAPI/Flask) ]
       | calls
       v
[ Service Layer (Use Cases) ]  <-- 定義了 IRepository (Protocol)
       | depends on interface      (Defines IRepository)
       v
[ Repository Layer (Implementation) ]
       | uses
       v
[ Database Driver (SQLAlchemy/Motor) ]
```

關鍵點在於：**Service Layer 不知道 Database Driver 的存在，它只知道 IRepository。**
The key point is: **The Service Layer does not know the Database Driver exists; it only knows IRepository.**

---

## 4. 逐步示例：重構訂單處理系統
## 4. Walkthrough: Refactoring an Order Processing System

### 場景 (Scenario)
我們有一個簡單的訂單處理功能：驗證庫存、扣款、儲存訂單、發送 Email。

We have a simple order processing function: validate stock, charge payment, save order, send email.

### 階段 1：Naive Approach (緊密耦合)
### Phase 1: Naive Approach (Tightly Coupled)

這是初階工程師常見的寫法，所有邏輯混雜在一起，難以測試。
This is a common style for junior engineers; all logic is mixed, making it hard to test.

```python
# bad_example.py
import smtplib
from sqlalchemy.orm import Session
from my_db import OrderModel, engine

def process_order(user_id: int, item_id: int, quantity: int):
    # 1. Direct DB dependency
    session = Session(engine) 
    
    # 2. Business Logic mixed with DB calls
    stock = session.execute(f"SELECT stock FROM items WHERE id={item_id}").scalar()
    if stock < quantity:
        raise ValueError("Not enough stock")
    
    # 3. Create Order
    order = OrderModel(user_id=user_id, item_id=item_id, quantity=quantity)
    session.add(order)
    session.commit()
    
    # 4. Hardcoded Email Service
    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.sendmail("system@example.com", "user@example.com", "Order Confirmed")
    server.quit()
```

### 階段 2：引入 Protocol 與 Repository Pattern
### Phase 2: Introducing Protocols and Repository Pattern

我們將外部依賴（DB, Email）抽象化。

We abstract away external dependencies (DB, Email).

```python
# domain/interfaces.py
from typing import Protocol, List
from dataclasses import dataclass

@dataclass
class Order:
    id: str
    item_id: int
    quantity: int

# 定義介面 (Protocol) - 這是 Pythonic 的 Interface
# Define Interface (Protocol) - This is the Pythonic Interface
class OrderRepository(Protocol):
    def save(self, order: Order) -> None:
        ...
    
    def get_stock(self, item_id: int) -> int:
        ...

class NotificationService(Protocol):
    def send_confirmation(self, user_id: int, message: str) -> None:
        ...
```

### 階段 3：實作 Use Case 與依賴注入
### Phase 3: Implementing Use Case & Dependency Injection

現在，業務邏輯只依賴於 `Protocol`，完全不知道 SQL 或 SMTP 的存在。

Now, the business logic only depends on the `Protocol`, completely unaware of SQL or SMTP.

```python
# domain/services.py
from .interfaces import OrderRepository, NotificationService, Order
import uuid

class OrderService:
    # 透過建構式注入依賴 (Constructor Injection)
    def __init__(self, repo: OrderRepository, notifier: NotificationService):
        self.repo = repo
        self.notifier = notifier

    def place_order(self, user_id: int, item_id: int, quantity: int) -> Order:
        # Pure Business Logic
        current_stock = self.repo.get_stock(item_id)
        if current_stock < quantity:
            raise ValueError("Out of stock")
        
        new_order = Order(id=str(uuid.uuid4()), item_id=item_id, quantity=quantity)
        self.repo.save(new_order)
        
        self.notifier.send_confirmation(user_id, "Order Placed!")
        return new_order
```

### 階段 4：實作層 (Infrastructure Layer)
### Phase 4: Infrastructure Layer

最後，我們實作具體的類別。這些類別可以在 Runtime 時被替換。

Finally, we implement the concrete classes. These can be swapped at runtime.

```python
# infrastructure/db.py
class SqlAlchemyOrderRepository:
    def __init__(self, session):
        self.session = session
    
    def save(self, order: Order) -> None:
        # Convert domain model to ORM model
        orm_order = OrderModel(id=order.id, ...) 
        self.session.add(orm_order)
        self.session.commit()
    
    def get_stock(self, item_id: int) -> int:
        return 100 # Simplified

# infrastructure/email.py
class SmtpNotificationService:
    def send_confirmation(self, user_id: int, message: str) -> None:
        print(f"Sending email via SMTP to user {user_id}")

# main.py (Composition Root)
# 這是唯一知道所有具體類別的地方
# This is the only place that knows about all concrete classes
def main():
    db_session = get_db_session()
    repo = SqlAlchemyOrderRepository(db_session)
    notifier = SmtpNotificationService()
    
    # Inject dependencies
    service = OrderService(repo=repo, notifier=notifier)
    service.place_order(user_id=1, item_id=5, quantity=2)
```

---

## 5. 常見錯誤與反模式
## 5. Common Pitfalls & Anti-patterns

### 5.1 過度使用類別 (The "Java in Python" Syndrome)
### 5.1 Overusing Classes (The "Java in Python" Syndrome)

*   **錯誤 (Pitfall)**：為每個微小的功能都建立一個 Factory Class 或 Strategy Class。
    **Pitfall**: Creating a Factory Class or Strategy Class for every tiny function.
*   **修正 (Fix)**：Python 的函式是一等公民（First-class citizen）。如果你的 Strategy 只有一個方法，直接傳遞函式（Callable）即可，不需要定義完整的類別。
    **Fix**: Python functions are first-class citizens. If your Strategy has only one method, just pass the function (Callable) directly; you don't need a full class definition.

### 5.2 循環依賴 (Circular Imports)
### 5.2 Circular Imports

*   **錯誤 (Pitfall)**：`models.py` 引用 `services.py`，而 `services.py` 又引用 `models.py`。這是架構分層不清的典型徵兆。
    **Pitfall**: `models.py` imports `services.py`, and `services.py` imports `models.py`. This is a classic symptom of unclear architectural layering.
*   **修正 (Fix)**：嚴格遵守依賴方向（Dependency Rule）。定義一個獨立的 `interfaces` 或 `types` 模組，讓雙方都依賴它；或者使用 Python 的 `TYPE_CHECKING` 區塊來解決型別提示的循環引用。
    **Fix**: Strictly adhere to the Dependency Rule. Define a separate `interfaces` or `types` module that both depend on; or use Python's `TYPE_CHECKING` block to resolve circular references for type hinting.

### 5.3 全域狀態單例 (Global State Singletons)
### 5.3 Global State Singletons

*   **錯誤 (Pitfall)**：在模組層級直接初始化 DB 連線或 API Client (`db = Database()`)，並在其他地方直接 import 這個變數。這會讓單元測試時很難 Mock 掉該物件。
    **Pitfall**: Initializing DB connections or API clients directly at the module level (`db = Database()`) and importing this variable elsewhere. This makes it very hard to mock the object during unit tests.
*   **修正 (Fix)**：使用依賴注入。如果必須使用全域變數，請使用 `ContextVar` 或依賴注入框架（如 `Dependency Injector` 或 FastAPI 的 `Depends`）來管理生命週期。
    **Fix**: Use Dependency Injection. If global variables are necessary, use `ContextVar` or a DI framework (like `Dependency Injector` or FastAPI's `Depends`) to manage the lifecycle.

---

## 6. 面試與實務問答切入點
## 6. Interview & Discussion Hooks

### Q1: 在 Python 中實作 Singleton 模式最好的方法是什麼？
### Q1: What is the best way to implement the Singleton pattern in Python?

*   **高分回答要點 (Key Points)**：
    *   指出 Python 的模組（Module）本身就是天然的 Singleton（import 兩次會拿到同一個物件）。通常不需要寫複雜的 `__new__` 邏輯。
    *   提到在並發（Concurrency）環境下的安全性。
    *   **進階**：反問「為什麼我們需要 Singleton？」通常依賴注入（DI）且將生命週期設為 Singleton scope 是比硬編碼 Singleton 模式更好的選擇，因為更易於測試。

### Q2: 請解釋 Python 的 MRO (Method Resolution Order) 以及它如何影響多重繼承的設計？
### Q2: Explain Python's MRO (Method Resolution Order) and how it affects the design of multiple inheritance?

*   **高分回答要點 (Key Points)**：
    *   解釋 C3 Linearization 演算法。
    *   說明 `super()` 的行為不是呼叫父類，而是呼叫 MRO 鏈中的下一個類別。
    *   **架構觀點**：在系統設計中，應盡量使用 **Composition over Inheritance**（組合優於繼承）。如果必須使用多重繼承，應限制在 Mixin 模式（提供行為而非狀態），避免鑽石繼承問題（Diamond Problem）帶來的複雜度。

### Q3: 你如何在不使用大型框架（如 Django）的情況下，組織一個大型 Python 後端專案？
### Q3: How would you organize a large Python backend project without using a monolithic framework like Django?

*   **高分回答要點 (Key Points)**：
    *   描述 **Clean Architecture** 或 **Hexagonal Architecture**。
    *   強調將 `domain`（業務邏輯）、`adapters`（DB/API）、`entrypoints`（Web/CLI）分開。
    *   提到使用 `Dependency Injection` 來黏合這些層。
    *   提到使用 `Pydantic` 進行資料驗證與序列化，作為各層之間的資料傳輸物件（DTO）。

---

## 7. 小結與後續延伸
## 7. Summary & Next Steps

### 記憶錨點 (Key Takeaways)
1.  **Protocol over ABC**: 在現代 Python 中，優先使用 `typing.Protocol` 進行隱式介面定義，這更符合 Python 的 Duck Typing 哲學。
2.  **Dependency Injection**: 不要讓你的類別自己找依賴，而是讓別人給它。這解耦了配置與使用。
3.  **Layered Architecture**: 保護你的核心業務邏輯不受外部框架（FastAPI, SQLAlchemy）變更的影響。
4.  **Composition over Inheritance**: 多重繼承很強大，但組合（Composition）通常更易於維護與理解。
5.  **Testability First**: 好的架構副作用是「測試變得容易」。如果你發現測試很難寫，通常是架構出了問題。

### 後續延伸 (Next Steps)
*   **Next Chapter**: 進入 **Chapter 06: Advanced Testing & Performance Profiling**，學習如何針對上述架構編寫高效的 Pytest 測試與 Mock 策略。
*   **Action Item**: 挑選你目前專案中的一個複雜模組，嘗試定義一個 `Protocol` 來隔離資料庫存取，並為其撰寫單元測試。