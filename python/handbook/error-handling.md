# 異常處理與日誌最佳實踐 / Exception Handling & Logging Best Practices

## Mental model｜心智模型

在 Python 開發中，異常處理（Exception Handling）與日誌（Logging）不應被視為「發生錯誤後的補救措施」，而應視為系統的 **控制流（Control Flow）** 與 **可觀測性（Observability）** 的核心組成部分。

### 1. The "Bubble Up" Strategy & Boundary Defense (氣泡上浮與邊界防禦)
異常就像氣泡，會從底層函數一路向上浮動（Propagate）。
- **Library/Low-level code**: 應專注於拋出具體的、語意化的異常（Signal），而不是吞掉錯誤。
- **Application/Entry-point code**: 應在邊界（如 API Handler, CLI Command）攔截異常，並將其轉換為用戶可讀的錯誤訊息或 HTTP Response。

### 2. Logs as Event Streams (日誌即事件流)
不要將 Log 視為寫入文字檔的字串，而應視為 **結構化的事件流（Structured Event Stream）**。每一條 Log 都應該包含 context（如 `user_id`, `request_id`），以便在 ELK stack 或 Datadog 等工具中進行聚合與追蹤。

---

## Patterns & best practices｜常見模式與最佳實務

### 1. Define Domain-Specific Exception Hierarchy (定義領域特定的異常階層)
不要只拋出 `ValueError` 或 `RuntimeError`。建立專屬於你的模組或應用程式的異常基類，這讓上層呼叫者能精準地捕捉特定錯誤。

```python
class PaymentError(Exception):
    """Base class for exceptions in this module."""
    pass

class InsufficientFundsError(PaymentError):
    """Raised when the account balance is too low."""
    def __init__(self, balance: float, amount: float):
        self.balance = balance
        self.amount = amount
        super().__init__(f"Attempt to pay {amount} with balance {balance}")

class GatewayTimeoutError(PaymentError):
    """Raised when the payment gateway times out."""
    pass
```

### 2. Explicit Exception Chaining (明確的異常鏈)
當你捕捉一個底層異常並拋出一個新的高層異常時，務必使用 `from e`。這能保留原始的 Traceback，對除錯至關重要。

```python
try:
    db.connect()
except ConnectionError as e:
    # 保留原始錯誤堆疊 (Original traceback is preserved)
    raise ServiceUnavailableError("Database is down") from e
```

### 3. Structured Logging (結構化日誌)
現代化應用不應使用 `f-string` 拼接 Log 訊息。使用 `structlog` 或標準庫的 `extra` 參數輸出 JSON 格式日誌，以便機器解析。

```python
import logging

logger = logging.getLogger(__name__)

# Bad: 難以索引與搜尋
logger.error(f"User {user_id} failed to pay order {order_id}")

# Good: 結構化，可被 Log 系統解析
logger.error("payment_failed", extra={"user_id": user_id, "order_id": order_id})
```

### 4. The `try-except-else` Block (善用 else 區塊)
將「可能出錯的程式碼」與「成功後才執行的程式碼」分開，可以避免意外捕捉到不該捕捉的異常。

```python
try:
    data = read_file(filename)
except FileNotFoundError:
    logger.error("file_missing", extra={"filename": filename})
else:
    # 只有在 read_file 成功時才會執行
    # 若 process_data 拋出異常，不會被上方的 except 捕捉 (這是好事)
    process_data(data)
```

---

## Anti-patterns & pitfalls｜反模式與踩雷點

### 1. The "Pokemon" Exception Handling (寶可夢式異常處理)
`except Exception:` 或更糟的 bare `except:` (Gotta catch 'em all!)。
- **後果**：這會隱藏 `NameError`、`SyntaxError` 甚至 `KeyboardInterrupt`（如果是 bare except），導致程式行為不可預測且難以除錯。
- **修正**：只捕捉你預期會發生的異常。

### 2. Log and Re-raise (記錄並重新拋出)
```python
except ValueError as e:
    logger.error("Something went wrong")  # Anti-pattern
    raise e
```
- **後果**：當異常層層上拋時，同樣的錯誤會被記錄多次，汙染 Log 系統。
- **修正**：要嘛處理掉異常並 Log，要嘛直接拋出（讓上層去 Log）。通常只在最上層（Boundary）做 Log。

### 3. Swallowing Exceptions (吞噬異常)
```python
except ValueError:
    pass
```
- **後果**：這是軟體工程中的「靜音殺手」。錯誤發生了但沒人知道，直到系統在遠處崩潰。
- **修正**：永遠不要寫 `pass`，除非你明確知道為什麼可以忽略，並且加上註解說明原因。

### 4. Using Exceptions for Flow Control (濫用異常做流程控制)
雖然 Python 講究 EAFP，但對於頻繁發生的業務邏輯（如檢查使用者是否存在），使用 `if user is None` 通常比 `try...except UserNotFoundError` 效能更好且語意更清晰。異常應保留給「非預期」或「例外」狀況。

---

## Checklists & workflows｜檢查清單與流程

在 Code Review 或提交程式碼前，請使用此清單自我檢核：

### Exception Design
- [ ] 我是否定義了自定義異常（Custom Exceptions），而不是直接拋出 `Exception` 或 `Error`？
- [ ] 異常類別名稱是否清晰表達了錯誤原因（例如 `UserNotFoundError` vs `UserError`）？
- [ ] 當我轉換異常時（Rethrowing），是否使用了 `raise ... from e`？

### Handling Logic
- [ ] `try` 區塊內的程式碼是否盡可能少？（避免將整個函數包在 try 中）
- [ ] 我是否避免了 bare `except:`？
- [ ] 資源釋放（如關閉檔案、連線）是否放在 `finally` 區塊或使用了 Context Manager (`with`)？

### Logging Strategy
- [ ] Log 訊息是否為靜態字串（Static String），變數是否放入了 Context/Extra 中？
- [ ] 是否避免了「Log 且 Rethrow」的雙重記錄行為？
- [ ] Log 等級（Info, Warning, Error）的使用是否正確？
    - **Info**: 正常運作的里程碑。
    - **Warning**: 發生了非預期狀況，但程式可繼續執行。
    - **Error**: 操作失敗，需要人工介入或影響功能。

---

## Real-world examples｜實戰案例

### Scenario: External API Client with Resilience
一個呼叫外部天氣服務的客戶端，展示如何結合自定義異常、結構化日誌與重試機制。

```python
import logging
import time
import requests
from typing import Optional, Dict, Any

# 1. Setup Structured Logger (Pseudo-setup)
logger = logging.getLogger("weather_service")

# 2. Custom Exception Hierarchy
class WeatherServiceError(Exception):
    """Base exception for weather service issues."""
    pass

class CityNotFoundError(WeatherServiceError):
    pass

class ServiceUnreachableError(WeatherServiceError):
    pass

def get_weather(city_id: str) -> Dict[str, Any]:
    url = f"https://api.weather.com/v1/{city_id}"
    
    # 3. Narrow try block
    try:
        response = requests.get(url, timeout=5)
        response.raise_for_status()
        
    except requests.exceptions.HTTPError as e:
        if response.status_code == 404:
            # 4. Semantic Exception Mapping
            logger.warning("city_not_found", extra={"city_id": city_id})
            raise CityNotFoundError(f"City {city_id} does not exist") from e
        
        # Log unexpected HTTP errors as critical context
        logger.error("upstream_api_error", extra={
            "city_id": city_id, 
            "status_code": response.status_code
        })
        raise WeatherServiceError("Upstream API failed") from e

    except requests.exceptions.RequestException as e:
        # 5. Handling Network/Connection issues
        logger.error("network_failure", extra={"city_id": city_id, "error": str(e)})
        raise ServiceUnreachableError("Could not connect to weather service") from e

    # 6. Success Path
    logger.info("weather_fetched", extra={"city_id": city_id})
    return response.json()

# Usage Example
def main():
    try:
        data = get_weather("taipei")
        print(f"Temperature: {data['temp']}")
    except CityNotFoundError:
        print("Please check the city ID.")
    except ServiceUnreachableError:
        print("Weather service is currently down, try again later.")
    except Exception:
        # Catch-all only at the very top level (Entry Point)
        logger.exception("unhandled_crash")
        print("An internal error occurred.")
```