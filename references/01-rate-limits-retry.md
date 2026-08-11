# Rate Limits и стратегия ретраев

## Лимиты по семействам API

| Семейство | Лимит | Примечания |
|---|---|---|
| **Content** | 100 запр/мин | ⚠️ источники расходятся: встречается и отдельный суб-лимит 10 запр/мин на `/cards/upload`, `/cards/update`, `/cards/upload/add`, и утверждение об общем лимите на все Content-методы; вживую не проверено (см. `10-content.md`) |
| **Marketplace** | 300 запр/мин | 409 = 5 запросов; 409 для DBS = 10 запросов |
| **Statistics** | **1 запр/мин** | `reportDetailByPeriod` — самый жёсткий лимит (⚠️ deprecated, отключается с 15.07.2026 — замена Finance API) |
| **Statistics (orders/sales)** | ⚠️ доке 1 запр/мин, фактически больше | live-проверка 2026-08-08: `/api/v1/supplier/orders` отдал `x-ratelimit-remaining: 7` и `8` на двух разных кабинетах → бакет заметно больше единицы. **Точный размер не замерен** |
| **Statistics (stocks)** | 3 запр / 30 сек | `/api/v1/supplier/stocks` ⚠️ эндпоинт отключён 14.07.2026, см. `12-statistics.md` |
| **Finance** ⭐ | **1 запр/мин** | Все эндпоинты семейства (sales-reports, acquiring, balance). Подтверждено live 2026-08-08: после одного запроса к `sales-reports/list` — `x-ratelimit-remaining: 0` (бакет = 1, всплеск 1) |
| **Analytics** | зависит от метода | NM-отчёты: 10 запр/10 мин; воронка `/api/analytics/v3/sales-funnel/...`: 3 запр/мин; остатки `/api/analytics/v1/stocks-report/wb-warehouses`: 1 запр/20 сек, **счётчик по IP, а не по токену** (live 2026-08-08) |
| **Prices & Discounts** | 10 запр / 6 сек | ~100 запр/мин, равномерно распределять |
| **Advertising** | до ~10 запр/сек (≈600/мин) | по наблюдениям; WB официально не публикует — см. `15-advertising.md` |
| **Feedbacks** | 100 запр/мин | |
| **Tariffs (commission)** | 1 запр/мин | `/api/v1/tariffs/commission` |
| **Tariffs (приёмка)** | 60 запр/мин | `/api/tariffs/v1/acceptance/coefficients` (по вторичному источнику мог снизиться до 6/мин с 27.06.2026 — см. `17-tariffs.md`) |
| **Calendar** | 10 запр / 6 сек | ~100 запр/мин |
| **Documents** | ⚠️ противоречиво | заявлено 3 запр/30 сек либо 1 запр/10 сек — не подтверждено (см. `20-documents.md`) |
| **Common** | 3 запр / 30 сек | ~6 запр/мин для некоторых методов |

## Заголовки Rate Limit в ответах

> ⚠️ **Live-проверка 2026-08-08** (прод AutoReport, реальные токены, 4 кабинета):
> в успешных ответах приходит **только `x-ratelimit-remaining`**. Заголовков
> `X-Ratelimit-Limit` и `X-Ratelimit-Reset` в ответе **нет** — ни на
> `statistics-api.wildberries.ru/api/v1/supplier/orders`, ни на
> `finance-api.wildberries.ru/api/finance/v1/sales-reports/list` (оба HTTP 200).
>
> Практический вывод: **логику нельзя строить на `Limit`/`Reset`** — размер бакета
> и скорость долива приходится выводить из наблюдений за `remaining`.

Что реально приходит в 200 OK:

```
x-ratelimit-remaining: 7        # Осталось запросов в текущем окне
```

Полный набор заголовков ответа `statistics-api` (live 2026-08-08): `server`, `date`,
`content-type`, `transfer-encoding`, `connection`, **`x-ratelimit-remaining`**,
`x-s2s-response-by`, `x-s2s-replicaid`, `x-s2s-selector-func-route`, `access-control-*`,
`x-s2s-server`, `x-request-id`, `x-s2s-request-id-mirrored`, `content-encoding`,
`strict-transport-security`, `x-content-type-options`.

**По доке WB** (live НЕ подтверждено) API должен возвращать во всех ответах кроме 429:

```
X-Ratelimit-Limit: 300          # Максимум запросов за период — live НЕ приходит
X-Ratelimit-Remaining: 298      # Осталось до лимита — приходит (в нижнем регистре)
X-Ratelimit-Reset: 60           # Секунд до сброса счётчика — live НЕ приходит
```

При ответе **429** дополнительно (по доке; в live-проверке 2026-08-08 заголовки
429-ответа не фиксировались):

```
X-Ratelimit-Retry: 5            # Секунд, через которые можно повторить
```

## Квота по токену + отдельный лимит по IP (live 2026-08-08)

Квота считается **по токену** — у каждого кабинета свой счётчик `x-ratelimit-remaining`.
Но у шлюза есть **отдельное ограничение на одновременные запросы с одного IP**, и оно
срабатывает раньше токенных квот:

- 4 запроса с 4 **разными** токенами, выпущенные в одну миллисекунду → четвёртый получает **429**.
- Те же 4 запроса с разносом **2 секунды** → проходят все.

Практика: при обслуживании нескольких кабинетов с одного сервера разносить старты
запросов во времени (глобальный на процесс семафор / джиттер), а не полагаться на
«у каждого кабинета свой лимит».

**Отдельно:** `POST /api/analytics/v1/stocks-report/wb-warehouses`
(`seller-analytics-api`) лимитируется **именно по IP**, а не по токену — доказано
отдельной проверкой: четыре разных токена всё равно упирались в общий лимит.
Параллелить его по кабинетам бесполезно, нужен один глобальный семафор.

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
- При `x-ratelimit-remaining: 0` — не делать запрос, ждать. **Сколько именно — из ответа
  не узнать**: `X-Ratelimit-Reset` живьём не приходит (live 2026-08-08), окно надо брать
  из таблицы лимитов выше (для Finance — 60 сек) или подбирать по наблюдениям
- Не запускать запросы к разным кабинетам одновременно — у шлюза есть лимит по IP
  поверх токенных квот (см. раздел «Квота по токену + отдельный лимит по IP»)
- **5xx ошибки** — ретраить с backoff (временная проблема на стороне WB)
- **4xx ошибки** (кроме 429) — **не ретраить** (ошибка в запросе, нужно исправить)

## Рекомендации для массовых операций

- Распределять запросы равномерно, а не burst'ами
- Для Statistics API (`reportDetailByPeriod`) — выдерживать **строго 60 сек** между запросами
- Для Prices API — не более 10 запросов за 6 секунд, лучше 1 запрос в секунду
- Использовать максимальный `limit` в параметрах (100000 для финотчёта) чтобы минимизировать число запросов
