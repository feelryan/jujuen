# 1. 前言與學習目標 (Introduction & Learning Objectives)

對於資深工程師而言，測試不僅僅是驗證程式碼的正確性，更是系統設計的一部分。測試程式碼的品質直接決定了系統的可維護性（Maintainability）與重構的信心（Refactoring Confidence）。在本章中，我們將超越基礎的 `unittest` 與簡單斷言，深入探討現代 Python 測試生態系中最強大的工具與思維。

For senior engineers, testing is not just about verifying correctness; it is an integral part of system design. The quality of test code directly dictates the maintainability of the system and the confidence to refactor. In this chapter, we move beyond basic `unittest` and simple assertions to explore the most powerful tools and paradigms in the modern Python testing ecosystem.

完成本章後，你將能夠：
By the end of this chapter, you will be able to:

1.  **精通 Pytest Fixtures 的依賴注入機制 (Master Pytest Fixtures as Dependency Injection)**：理解 Scope（作用域）、Yield fixtures 與 `conftest.py` 的階層結構，寫出模組化且可重用的測試設置。
    Understand Scopes, Yield fixtures, and the hierarchy of `conftest.py` to write modular and reusable test setups.
2.  **掌握進階 Mocking 策略 (Master Advanced Mocking Strategies)**：清楚分辨何時該 Mock、何時該用 Fake，並解決 "Where to patch" 的常見陷阱，避免測試與實作細節過度耦合。
    Distinguish when to Mock versus when to use Fakes, resolve the common "Where to patch" pitfalls, and avoid coupling tests too tightly with implementation details.
3.  **運用 Property-based Testing 發現邊界案例 (Apply Property-based Testing to Find Edge Cases)**：使用 `Hypothesis` 函式庫自動生成測試資料，找出人類思維難以覆蓋的邊界條件（Edge Cases）。
    Use the `Hypothesis` library to automatically generate test data, uncovering edge cases that human intuition often misses.
4.  **設計適合 CI/CD 的測試架構 (Design CI/CD-friendly Test Architectures)**：了解如何優化測試執行速度、處理 Flaky Tests，並在微服務架構中進行有效的整合測試。
    Learn how to optimize test execution speed, handle Flaky Tests, and perform effective integration testing within a microservices architecture.

---

# 2. 核心觀念與心智模型 (Core Concepts & Mental Model)

## 2.1 Fixtures 作為依賴注入 (Fixtures as Dependency Injection)

在傳統的 `unittest` 中，我們依賴 `setUp` 和 `tearDown` 來管理狀態，這往往導致一個巨大的 setup 函式包含了所有測試案例不一定都需要資源。
In traditional `unittest`, we rely on `setUp` and `tearDown` to manage state, which often leads to a monolithic setup function containing resources that not all test cases require.

**心智模型 (Mental Model)**：將 Pytest Fixtures 視為**依賴注入容器 (Dependency Injection Container)**。
**Mental Model**: Treat Pytest Fixtures as a **Dependency Injection Container**.

測試函式宣告它需要的參數（fixtures），Pytest 負責實例化並注入這些資源。這形成了一個資源依賴圖（Dependency Graph），只有被請求的資源才會被建立。
The test function declares the arguments (fixtures) it needs, and Pytest is responsible for instantiating and injecting these resources. This forms a resource dependency graph where only requested resources are created.

## 2.2 Mocking：行為驗證 vs. 狀態驗證 (Mocking: Behavior vs. State Verification)

資深工程師應區分 **Stub** (提供預設回傳值) 與 **Mock** (驗證行為交互)。過度使用 Mock 會導致測試變脆（Brittle Tests），因為測試鎖定了實作細節而非行為契約。
Senior engineers should distinguish between **Stubs** (providing canned answers) and **Mocks** (verifying interactions). Overusing Mocks leads to Brittle Tests because the tests lock onto implementation details rather than behavioral contracts.

**關鍵原則 (Key Principle)**：Mock Roles, not Objects.
**Key Principle**: Mock Roles, not Objects.
不要 Mock 整個資料庫物件，而是 Mock 資料庫在該業務邏輯中扮演的「角色」（例如 `UserRepository` 介面）。
Don't mock the entire database object; mock the "role" the database plays in that specific business logic (e.g., a `UserRepository` interface).

## 2.3 Property-based Testing (PBT)

傳統測試是 Example-based（基於範例的）：`assert add(1, 2) == 3`。
PBT 是 Generative（生成式的）：`assert add(x, y) == x + y` for all integers `x, y`。
Traditional testing is Example-based: `assert add(1, 2) == 3`.
PBT is Generative: `assert add(x, y) == x + y` for all integers `x, y`.

**心智模型 (Mental Model)**：PBT 是一種**模糊測試 (Fuzzing)** 的結構化形式。你定義資料的「形狀」與「不變量 (Invariants)」，讓引擎去尋找破壞這些不變量的反例。
**Mental Model**: PBT is a structured form of **Fuzzing**. You define the "shape" of the data and the "Invariants," letting the engine hunt for counter-examples that break these invariants.

---

# 3. 實務場景與系統設計視角 (Real-World & System Design View)

在大型分散式系統或微服務架構中，測試策略直接影響交付速度與穩定性。
In large-scale distributed systems or microservices architectures, testing strategy directly impacts delivery speed and stability.

## 3.1 測試金字塔的實務調整 (Practical Adjustments to the Testing Pyramid)

在 Big Tech 環境中，單純的單元測試（Unit Tests）往往不足以捕捉跨服務的錯誤。
In Big Tech environments, pure Unit Tests are often insufficient to catch cross-service errors.

-   **Unit Tests (Pytest + Mocking)**: 針對複雜的業務邏輯（Business Logic），執行速度極快（毫秒級）。
    Focus on complex Business Logic; execution speed is extremely fast (milliseconds).
-   **Integration Tests (Pytest + Docker/Testcontainers)**: 針對資料庫查詢、快取存取。這裡通常使用真實的 DB（如透過 Docker 啟動的 ephemeral DB）而非 Mock，以避免 "Mocking the truth" 的風險。
    Focus on database queries, cache access. Here, real DBs (e.g., ephemeral DBs via Docker) are often used instead of Mocks to avoid the risk of "Mocking the truth."
-   **Contract Tests**: 確保微服務之間的 API 協議未被破壞。
    Ensure API agreements between microservices remain unbroken.

## 3.2 可維護性與 Flaky Tests (Maintainability & Flaky Tests)

Flaky Tests（不穩定的測試）是 CI/CD 的惡夢。常見原因包括：
Flaky Tests are the nightmare of CI/CD. Common causes include:

1.  **時間依賴 (Time Dependency)**：直接使用 `datetime.now()`。解法：使用 `freezegun` 或 Mock 時間。
    Direct use of `datetime.now()`. Solution: Use `freezegun` or mock time.
2.  **資源競爭 (Resource Contention)**：多個測試共用同一個 DB 狀態且未清理。解法：使用 Pytest fixtures 的 `yield` 機制確保 Teardown。
    Multiple tests sharing the same DB state without cleanup. Solution: Use Pytest fixtures' `yield` mechanism to ensure Teardown.
3.  **網路依賴 (Network Dependency)**：測試中呼叫外部 API。解法：使用 `vcrpy` 錄製回應或 `responses` 進行 Mock。
    Calling external APIs during tests. Solution: Use `vcrpy` to record responses or `responses` to mock.

---

# 4. 逐步示例 (Walkthrough / Example)

我們將模擬一個電商系統中的「訂單處理服務」。該服務需要計算總價（包含折扣），並呼叫外部支付閘道。
We will simulate an "Order Processing Service" in an e-commerce system. This service needs to calculate the total price (including discounts) and call an external payment gateway.

## 4.1 原始程式碼 (Source Code)

```python
# payment_service.py
import requests
from datetime import datetime

class PaymentGateway:
    def charge(self, amount: int, currency: str) -> bool:
        # 模擬外部 API 呼叫 / Simulate external API call
        resp = requests.post("https://api.stripe.com/charge", json={"amount": amount})
        return resp.status_code == 200

def calculate_total(price: int, discount_rate: float) -> int:
    if discount_rate < 0 or discount_rate > 1:
        raise ValueError("Invalid discount rate")
    return int(price * (1 - discount_rate))

def process_order(price: int, discount: float, gateway: PaymentGateway) -> str:
    final_price = calculate_total(price, discount)
    if gateway.charge(final_price, "USD"):
        return "SUCCESS"
    return "FAILED"
```

## 4.2 Level 1: 基礎測試與常見錯誤 (Basic Test & Common Mistakes)

初階工程師可能會這樣寫，這有兩個問題：依賴真實網路、測試邏輯分散。
A junior engineer might write this, which has two problems: dependency on real network, and scattered test logic.

```python
# test_bad.py
import unittest
from payment_service import process_order, PaymentGateway

class TestPayment(unittest.TestCase):
    def test_process_order(self):
        # 錯誤：這會真的打 API，導致測試變慢且不穩定
        # Mistake: This hits the real API, causing slow and flaky tests
        gw = PaymentGateway() 
        result = process_order(100, 0.1, gw)
        self.assertEqual(result, "SUCCESS")
```

## 4.3 Level 2: 使用 Pytest Fixtures 與 Mocking (Using Pytest Fixtures & Mocking)

我們將改進測試：
1.  使用 `fixture` 注入 Gateway。
2.  使用 `unittest.mock` 隔離網路呼叫。

We will improve the test:
1.  Use `fixture` to inject the Gateway.
2.  Use `unittest.mock` to isolate network calls.

```python
# test_better.py
import pytest
from unittest.mock import Mock
from payment_service import process_order, PaymentGateway

@pytest.fixture
def mock_gateway():
    # 建立一個 Mock 物件，模擬 charge 方法回傳 True
    # Create a Mock object, simulating charge method returning True
    gw = Mock(spec=PaymentGateway)
    gw.charge.return_value = True
    return gw

def test_process_order_success(mock_gateway):
    # Arrange
    price = 100
    discount = 0.1
    
    # Act
    result = process_order(price, discount, mock_gateway)
    
    # Assert
    assert result == "SUCCESS"
    # 驗證行為：確保 charge 被呼叫了一次，且參數正確
    # Verify behavior: Ensure charge was called once with correct args
    mock_gateway.charge.assert_called_once_with(90, "USD")

def test_process_order_failure(mock_gateway):
    # 修改 Mock 行為 / Modify Mock behavior
    mock_gateway.charge.return_value = False
    
    result = process_order(100, 0.1, mock_gateway)
    assert result == "FAILED"
```

## 4.4 Level 3: Property-based Testing (Hypothesis)

對於 `calculate_total` 函式，我們不僅想測試 `100 * 0.9 = 90`，我們想確保「打折後的價格永遠小於等於原價」且「價格不會變成負數」。
For the `calculate_total` function, we don't just want to test `100 * 0.9 = 90`. We want to ensure "discounted price is always <= original price" and "price never becomes negative".

```python
# test_advanced.py
from hypothesis import given, strategies as st
from payment_service import calculate_total

# 定義策略：價格是正整數，折扣是 0.0 到 1.0 之間的浮點數
# Define strategies: Price is a positive integer, discount is float between 0.0 and 1.0
@given(
    price=st.integers(min_value=0, max_value=1_000_000),
    discount=st.floats(min_value=0.0, max_value=1.0)
)
def test_calculate_total_properties(price, discount):
    final_price = calculate_total(price, discount)
    
    # Invariant 1: 折後價格不應超過原價
    # Invariant 1: Discounted price should not exceed original price
    assert final_price <= price
    
    # Invariant 2: 折後價格不應為負
    # Invariant 2: Discounted price should not be negative
    assert final_price >= 0

# Hypothesis 會自動嘗試邊界值，例如 price=0, discount=0.0, discount=1.0
# Hypothesis automatically tries edge cases, e.g., price=0, discount=0.0, discount=1.0
```

---

# 5. 常見錯誤與反模式 (Common Pitfalls & Anti-patterns)

## 5.1 錯誤的 Patch 位置 (Wrong Patch Location)

這是資深工程師面試中最常問的陷阱。
This is the most common trap asked in senior engineer interviews.

-   **錯誤 (Bad)**: `patch('library.SomeClass')` —— Patch 了定義的地方。
    Patching where it is defined.
-   **正確 (Good)**: `patch('my_module.SomeClass')` —— Patch 了使用的地方。
    Patching where it is used.

**原因**：Python 在 import 時會建立名稱綁定。如果你 patch 了原始定義，但你的模組已經 import 了該類別，你的 patch 就不會生效。
**Reason**: Python creates name bindings at import time. If you patch the original definition but your module has already imported the class, your patch will not take effect.

## 5.2 過度 Mocking (Over-Mocking)

**反模式**：測試程式碼中充滿了 `mock_obj.method.return_value = ...`，幾乎重寫了整個業務邏輯。
**Anti-pattern**: Test code is littered with `mock_obj.method.return_value = ...`, essentially rewriting the entire business logic.

**後果**：重構程式碼內部實作時，測試會失敗，即使外部行為沒有改變。這降低了重構的意願。
**Consequence**: When refactoring internal implementation, tests fail even if external behavior hasn't changed. This reduces the willingness to refactor.

**解法**：盡量使用 **Fakes**（輕量級的記憶體實作，如 `sqlite:///:memory:` 替代 Postgres）而非 Mock 所有 DB 操作。
**Solution**: Prefer using **Fakes** (lightweight in-memory implementations, e.g., `sqlite:///:memory:` instead of Postgres) rather than mocking all DB operations.

## 5.3 測試依賴順序 (Test Order Dependency)

**反模式**：Test B 依賴 Test A 在資料庫中留下的資料。
**Anti-pattern**: Test B relies on data left in the database by Test A.

**後果**：當並行執行測試（如 `pytest-xdist`）或單獨執行 Test B 時，測試會失敗。
**Consequence**: Tests fail when run in parallel (e.g., `pytest-xdist`) or when Test B is run in isolation.

**解法**：每個測試都應該是原子的（Atomic）。使用 Fixture 的 `yield` 語法在測試後進行清理（Teardown）。
**Solution**: Every test should be atomic. Use Fixture's `yield` syntax to clean up (Teardown) after the test.

---

# 6. 面試與實務問答切入點 (Interview & Discussion Hooks)

## 6.1 如何處理遺留代碼（Legacy Code）的測試？
**How do you approach testing Legacy Code?**

*   **高分回答要點 (Key Points)**：
    *   提及 **Characterization Tests**（特性測試）：先寫測試來鎖定當前行為（即使是 Bug 也不修），確保重構不破壞現有功能。
    *   使用 **Golden Master** 模式：擷取大量輸入與輸出的快照，作為基準比對。
    *   逐步重構：只在需要修改功能的地方補測試，而不是盲目追求 100% 覆蓋率。

## 6.2 請解釋 `pytest` fixture 的 `scope` 機制及其在優化測試速度中的應用。
**Explain the `scope` mechanism in `pytest` fixtures and its application in optimizing test speed.**

*   **高分回答要點 (Key Points)**：
    *   解釋 `function` (預設), `class`, `module`, `session` 的差異。
    *   舉例：昂貴的資源（如 DB 連線、Docker 容器啟動）應設為 `session` scope，在所有測試間共用。
    *   強調共用資源的副作用管理：如果共用 DB，需要在每個 `function` 級別的 fixture 中使用 Transaction Rollback 來重置狀態，而非重建 DB。

## 6.3 什麼是 Property-based Testing？它解決了什麼 Example-based Testing 無法解決的問題？
**What is Property-based Testing? What problems does it solve that Example-based Testing cannot?**

*   **高分回答要點 (Key Points)**：
    *   PBT 驗證的是**不變量 (Invariants)** 而非特定值。
    *   它能發現**未知的未知 (Unknown Unknowns)**：開發者沒想到的邊界值（如 unicode 字元、極大整數、空集合）。
    *   提及 **Shrinking** 機制：當 Hypothesis 找到錯誤時，會自動簡化範例（例如將一個導致錯誤的長 List 縮減為最小的重現範例）。

---

# 7. 小結與後續延伸 (Summary & Next Steps)

## 重點回顧 (Key Takeaways)

1.  **Fixtures Power**: 使用 Pytest Fixtures 建立模組化、可組合的測試環境，善用 `conftest.py` 管理全域配置。
2.  **Mocking Precision**: 記住 "Mock Roles, not Objects" 以及 "Patch where used, not where defined"。
3.  **Generative Testing**: 引入 Hypothesis 進行 Property-based Testing，提升對邊界條件的防禦力。
4.  **Test Isolation**: 確保測試原子性，避免共享可變狀態導致 Flaky tests。
5.  **Pyramid Strategy**: 合理分配 Unit (Mock heavy) 與 Integration (Docker/Fake heavy) 測試的比例。

## 後續延伸 (Next Steps)

*   **Performance Profiling**: 學習使用 `cProfile` 或 `py-spy` 分析 Python 程式碼效能（Chapter 09 預告）。
*   **AsyncIO Testing**: 深入研究如何測試非同步程式碼（`pytest-asyncio`），這是現代 Python 後端開發的必備技能。
*   **Mutation Testing**: 嘗試 `mutmut` 等工具，透過故意修改程式碼來驗證測試是否真的有效（Test the tests）。