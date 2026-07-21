# Rate Limits и стратегия ретраев

## Лимиты по семействам API

| Семейство | Лимит | Примечания |
|---|---|---|
| **Content** | 100 запр/мин | `/cards/upload`, `/cards/update`, `/cards/upload/add`: 10 запр/мин |
| **Marketplace** | 300 запр/мин | 409 = 5 запросов; 409 для DBS = 10 запросов |
| **Statistics** | **1 запр/мин** | `reportDetailByPeriod` — самый жёсткий лимит (⚠️ deprecated, отключается с 15.07.2026 — замена Finance API) |
| **Statistics (stocks)** | 3 запр / 30 сек | `/api/v1/supplier/stocks` |
| **Finance** ⭐ | **1 запр/мин** | Все эндпоинты семейства (sales-reports, acquiring, balance) |
| **Analytics** | зависит от метода | NM-отчёты: 10 запр/10 мин; воронка `/api/analytics/v3/sales-funnel/...`: 3 запр/мин |
| **Prices & Discounts** | 10 запр / 6 сек | ~100 запр/мин, равномерно распределять |
| **Advertising** | 10-100 запр/мин | зависит от конкретного метода |
| **Feedbacks** | 100 запр/мин | |
| **Tariffs (commission)** | 1 запр/мин | `/api/v2/tariffs/commission` |
| **Tariffs (warehouse)** | 60 запр/мин | `/api/v2/tariffs/warehouse-coefficients` |
| **Calendar** | 10 запр / 6 сек | ~100 запр/мин |
| **Common** | 3 запр / 30 сек | ~6 запр/мин для некоторых методов |

## Заголовки Rate Limit в ответах

API возвращает эти заголовки во **всех** ответах (кроме 429):

```
X-Ratelimit-Limit: 300          # Максимум запросов за период
X-Ratelimit-Remaining: 298      # Осталось до лимита
X-Ratelimit-Reset: 60           # Секунд до сброса счётчика
```

При ответе **429** дополнительно:

```
X-Ratelimit-Retry: 5            # Секунд, через которые можно повторить
```

## Ответ при 429

```json
{
  "title": "too many requests",
  "detail": "Request limit exceeded",
  "status": 429
}
```

## Стратегия Exponential Backoff с Jitter

### Приоритет определения задержки

1. Заголовок `Retry-After` (если есть) — использовать его
2. Заголовок `X-Ratelimit-Retry` — использовать его
3. Exponential backoff — формула ниже

### Формула

```
wait_time = min(2^attempt + random(0, 0.1), max_backoff)
```

| Попытка | Базовая задержка | С jitter (пример) |
|---|---|---|
| 1 | 1 сек | 1.05 сек |
| 2 | 2 сек | 2.08 сек |
| 3 | 4 сек | 4.03 сек |
| 4 | 8 сек | 8.07 сек |
| 5 | 16 сек | 16.02 сек |
| 6 | 32 сек (макс) | 32.09 сек |

### Псевдокод retry-обёртки

```
function wb_request(method, url, params, max_retries=5):
    for attempt in 1..max_retries:
        response = http_request(method, url, params)
        
        if response.status == 200:
            return response
        
        if response.status == 429:
            retry_after = response.headers.get("Retry-After")
                       or response.headers.get("X-Ratelimit-Retry")
            if retry_after:
                sleep(int(retry_after))
            else:
                sleep(min(2^attempt + random(0, 0.1), 32))
            continue
        
        if response.status >= 500:
            sleep(min(2^attempt + random(0, 0.1), 32))
            continue
        
        // 4xx кроме 429 — не ретраить, вернуть ошибку
        raise ApiError(response.status, response.body)
    
    raise MaxRetriesExceeded()
```

### Правила

- Максимум **5-7 попыток** — потом отдавать ошибку
- **Jitter обязателен** — случайная добавка 0-100мс для избежания "thundering herd"
- **Логировать все 429** — для анализа и подстройки частоты
- При `X-Ratelimit-Remaining: 0` — не делать запрос, ждать `X-Ratelimit-Reset` секунд
- **5xx ошибки** — ретраить с backoff (временная проблема на стороне WB)
- **4xx ошибки** (кроме 429) — **не ретраить** (ошибка в запросе, нужно исправить)

## Рекомендации для массовых операций

- Распределять запросы равномерно, а не burst'ами
- Для Statistics API (`reportDetailByPeriod`) — выдерживать **строго 60 сек** между запросами
- Для Prices API — не более 10 запросов за 6 секунд, лучше 1 запрос в секунду
- Использовать максимальный `limit` в параметрах (100000 для финотчёта) чтобы минимизировать число запросов
