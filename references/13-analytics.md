# Analytics API — Аналитика

## Назначение

NM-отчёты по товарам, **воронка продаж** (заказы, средняя цена, % выкупа), **платное хранение**, удержания, штрафы, доля бренда.

**Хост:** `seller-analytics-api.wildberries.ru`  
**Scope токена:** Analytics  
**Версии:** /api/v1/, /api/v2/, /api/v3/

## Rate limits

| Эндпоинт | Лимит |
|---|---|
| NM-отчёты | 10 запр / 10 мин |
| Воронка v3 (`/api/analytics/v3/sales-funnel/...`) | **3 запр/мин** (burst 3 за 20 сек) |
| Платное хранение (async) | ограничено по задачам |
| Отчёт приёмки (async) | ограничено по задачам |

## Эндпоинты

### Воронка продаж

| Метод | Путь | Назначение | Тело запроса | Тип |
|---|---|---|---|---|
| **POST** | **/api/analytics/v3/sales-funnel/products** | **Воронка по товарам (АКТУАЛЬНАЯ)** | JSON: selectedPeriod, nmIds, limit, offset, orderBy | синхронный |
| POST | /api/analytics/v3/sales-funnel/products/history | Поденная/понедельная динамика | JSON | синхронный |
| POST | /api/analytics/v3/sales-funnel/grouped/history | Динамика, сгруппировано по subject/brand/tag | JSON | синхронный |
| ~~GET~~ | ~~/api/v2/sales-funnel/products~~ | **Отключён 09.12.2025** | — | — |
| ~~GET~~ | ~~/api/v3/sales-funnel/products~~ | **Старый путь до миграции — заменён на `/api/analytics/v3/...`** | — | — |

**Что изменилось в актуальной v3:**
- Префикс пути: `/api/v3/...` → `/api/analytics/v3/...`
- Метод: GET → **POST**, параметры переехали в JSON-body
- Период задаётся объектом `selectedPeriod {start, end}` (не плоскими `dateFrom/dateTo`)
- Пагинация — **offset/limit** (`limit` до 1000, дефолт 50; `offset` сдвигает страницу)
- Ошибки больше не приходят в теле успешного ответа — проверять HTTP-статус

### NM-отчёты (аналитика товаров)

| Метод | Путь | Назначение | Параметры | Тип |
|---|---|---|---|---|
| GET | /api/v1/nm-report/detail | Детальный отчёт по товарам | nmID, period | синхронный |
| POST | /api/v2/nm-report/downloads | Создать отчёт NM за период | dateFrom, dateTo, fields | **асинхронный** |
| GET | /api/v2/nm-report/downloads | Список созданных отчётов | — | — |
| GET | /api/v2/nm-report/downloads/{taskId} | Статус отчёта | taskId | — |
| GET | /api/v2/nm-report/downloads/{taskId}/file | Скачать отчёт | taskId | — |

### Платное хранение (АСИНХРОННЫЙ)

| Метод | Путь | Назначение | Параметры | Тип |
|---|---|---|---|---|
| POST | /api/v1/paid_storage | **Создать отчёт хранения** | dateFrom, dateTo | **асинхронный** |
| GET | /api/v1/paid_storage/tasks/{taskId}/status | Статус отчёта | taskId | — |
| GET | /api/v1/paid_storage/tasks/{taskId}/download | Скачать отчёт (CSV в ZIP) | taskId | — |

Подробно workflow task_id — см. `04-async-tasks.md`.

### Приёмка (АСИНХРОННЫЙ)

| Метод | Путь | Назначение | Параметры | Тип |
|---|---|---|---|---|
| POST | /api/v1/acceptance_report | Создать отчёт приёмки | dateFrom, dateTo | **асинхронный** |
| GET | /api/v1/acceptance_report/tasks/{taskId}/status | Статус | taskId | — |
| GET | /api/v1/acceptance_report/tasks/{taskId}/download | Скачать | taskId | — |

### Доля бренда (АСИНХРОННЫЙ)

| Метод | Путь | Назначение | Параметры | Тип |
|---|---|---|---|---|
| POST | /api/v2/brands/report-downloads | Создать отчёт по бренду | dateFrom, dateTo | **асинхронный** |
| GET | /api/v2/brands/report-downloads/{taskId} | Статус | taskId | — |
| GET | /api/v2/brands/report-downloads/{taskId}/file | Скачать | taskId | — |

### Прочее

| Метод | Путь | Назначение | Параметры |
|---|---|---|---|
| GET | /api/v1/analytics/goods-return | Возвраты товаров | dateFrom, dateTo |
| GET | /api/v1/analytics/excise | Отчёт по акцизам | nmID |

---

## Воронка продаж — подробно

Заменяет ручную выгрузку «*Воронка продаж*.xlsx».

### Запрос

```bash
curl -X POST "https://seller-analytics-api.wildberries.ru/api/analytics/v3/sales-funnel/products" \
  -H "Authorization: Bearer TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "selectedPeriod": { "start": "2026-04-07", "end": "2026-04-13" },
    "nmIds": [],
    "limit": 1000
  }'
```

### Тело запроса (JSON)

| Поле | Тип | Обязателен | Описание |
|---|---|---|---|
| `selectedPeriod.start` | string (YYYY-MM-DD) | да | Начало периода |
| `selectedPeriod.end`   | string (YYYY-MM-DD) | да | Конец периода |
| `pastPeriod`           | object              | нет | Период для сравнения (та же схема) |
| `nmIds`                | array<int>          | нет | Если пусто `[]` — все карточки продавца |
| `brandNames`           | array<string>       | нет | Фильтр по бренду |
| `subjectIds`           | array<int>          | нет | Фильтр по предмету |
| `tagIds`               | array<int>          | нет | Фильтр по тегам |
| `skipDeletedNm`        | bool                | нет | Скрыть удалённые карточки |
| `limit`                | int                 | нет | Макс. записей в ответе (1..1000, дефолт 50) |
| `offset`               | int                 | нет | Сдвиг для постраничного перебора (0 для первой страницы) |
| `orderBy`              | object              | нет | `{ "field": "orderCount", "mode": "desc" }` — сортировка |

### Структура ответа (проверено зондом 2026-04-19, токен Personal)

```json
{
  "data": {
    "currency": "RUB",
    "products": [
      {
        "product": {
          "nmId": 196832890,
          "title": "Кроссовки на высокой подошве белые",
          "vendorCode": "4800-2",
          "brandName": "OVVO",
          "subjectId": 105,
          "subjectName": "Кроссовки",
          "tags": [],
          "productRating": 10,
          "feedbackRating": 4.8,
          "stocks": { "wb": 355, "mp": 0, "balanceSum": 1310277 }
        },
        "statistic": {
          "selected": {
            "period": { "start": "2026-04-06", "end": "2026-04-12" },
            "openCount":              7503,
            "cartCount":              735,
            "orderCount":             204,
            "orderSum":               750517,
            "buyoutCount":            87,
            "buyoutSum":              318853,
            "cancelCount":            90,
            "cancelSum":              332900,
            "avgPrice":               3679,
            "avgOrdersCountPerDay":   29.1,
            "shareOrderPercent":      41.4,
            "addToWishlist":          189,
            "timeToReady":            { "days": 1, "hours": 19, "mins": 0 },
            "localizationPercent":    50,
            "wbClub":                 { "orderCount": 15, "orderSum": 54845, "buyoutSum": 29222, "buyoutCount": 8, "cancelSum": 18595, "cancelCount": 5, "avgPrice": 3656, "buyoutPercent": 62, "avgOrderCountPerDay": 2.1 },
            "conversions":            { "addToCartPercent": 10, "cartToOrderPercent": 28, "buyoutPercent": 49 }
          },
          "past":       { /* те же поля, если передан pastPeriod (или дефолтный) */ },
          "comparison": { "openCountDynamic": -27, "orderCountDynamic": -33, /* ... */ }
        }
      }
    ]
  }
}
```

### ⚠️ Особенности именования полей

- Поля называются **`orderCount`/`orderSum`/`buyoutCount`/`buyoutSum`** (без `s` на конце, без суффикса `Rub`). Не `ordersCount`/`ordersSumRub`.
- **`buyoutPercent` лежит внутри `statistic.selected.conversions`**, а **не** на уровне `selected`. На уровне `selected` поля `buyoutPercent` нет — только в `conversions` (общий) и в `wbClub` (для WB Клуба).
- `nmId` — внутри обёртки `product` (camelCase, маленькая `d`). На верхнем уровне продукта `nmId`/`nmID` нет.
- `avgPrice` — есть, поле так и называется. Расчёт `orderSum/orderCount` не нужен.

### Ключевые поля ответа

| Поле API | Описание |
|---|---|
| `product.nmId` | Артикул WB |
| `statistic.selected.orderCount` | Заказы за период, шт |
| `statistic.selected.avgPrice` | Средняя цена, ₽ |
| `statistic.selected.conversions.buyoutPercent` | % выкупа — **внутри `conversions`** |
| `statistic.selected.avgOrdersCountPerDay` или `orderCount / 7` | Скорость заказов, шт/день |

### Подводные камни

- **Имена полей не совпадают с тем, что часто пишут на форумах** (`ordersCount`/`ordersSumRub` — старая или ошибочная номенклатура). Проверяй по живому ответу.
- **`buyoutPercent` — не на уровне `selected`**, а в `conversions`. Очень легко промахнуться и получить 0.
- **Метод POST с body** — параметры через querystring не пройдут.
- **`limit` до 1000**, дефолт ниже. Для большого ассортимента ставь `limit=1000` плюс `offset` для следующих страниц.
- **Лимит 3 запр/мин** (по `X-Ratelimit-Remaining` в ответе видно).
- ⚠️ Найден непроверенный сигнал (аудит 2026-07-21) про отключение 29.04.2026 некоего метода
  "группировки статистики карточек товаров за период" — не удалось установить, относится ли это
  к `grouped/history` из этого файла или к другому методу. Проверь вживую, если используешь `grouped/history`.
- **Период — объект `selectedPeriod`**, не плоские `dateFrom/dateTo`. Эндпоинт сам подставляет `pastPeriod` (предыдущий период такой же длины) для блока `past`/`comparison`, если не указан.

---

## Платное хранение — подробно

Заменяет ручную выгрузку «*платному хранению*.xlsx».

### Создание задачи

```bash
curl -X POST https://seller-analytics-api.wildberries.ru/api/v1/paid_storage \
  -H "Authorization: Bearer TOKEN" \
  -H "Content-Type: application/json" \
  -d '{ "dateFrom": "2024-06-01", "dateTo": "2024-06-07" }'
```

### Скачанный отчёт (CSV)

Ключевые поля:

| Поле CSV | Маппинг в Юнит-листе |
|---|---|
| `nmId` (Артикул WB) | A |
| `date` (Дата начисления) | фильтр по неделе |
| `storageCost` (Сумма хранения, руб) | AB (Хранение, ₽) |

**Обработка:** Фильтр по дате недели → группировка по nmId → сумма storageCost.

### Подводные камни

- Генерация занимает 5-30 минут (асинхронный отчёт)
- Готовый отчёт хранится 2 часа
- Данные за последние 90 дней
- Формат: CSV в ZIP-архиве

---

## Оборачиваемость

В WB API **нет прямого эндпоинта для оборачиваемости** — вручную её обычно берут из «Шаблон обновления цен и скидок*.xlsx» в ЛК.

Можно рассчитать: `оборачиваемость = остатки / скорость_продаж` из данных Finance `sales-reports/detailed` (см. [12a-finance.md](12a-finance.md)) + `stocks`.

## Ссылка на оригинал

https://dev.wildberries.ru/openapi/analytics
