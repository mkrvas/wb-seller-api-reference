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

Эндпоинты аналитики приходят из ДВУХ официальных спек на хосте `seller-analytics-api.wildberries.ru`:
`11-analytics` (воронка, NM-отчёты, рейтинг, отчёты по остаткам и поиску) и `12-reports` (платное
хранение, приёмка, доля бренда, возвраты, удержания, штрафы, маркировка, самовыкупы).

### Аналитика: воронка, NM-отчёты, остатки, поиск (спека 11-analytics)

<!-- AUTO:BEGIN spec=11-analytics section=endpoints -->
| Метод | Путь | Назначение |
|---|---|---|
| POST | `/api/analytics/v1/item-rating` | Получить отчёт ⚠️ deprecated |
| POST | `/api/analytics/v1/stocks-report/wb-warehouses` | Остатки на складах WB |
| POST | `/api/analytics/v2/item-rating` | Получить отчёт |
| POST | `/api/analytics/v3/sales-funnel/grouped/history` | Статистика групп карточек товаров по дням |
| POST | `/api/analytics/v3/sales-funnel/products` | Статистика карточек товаров за период |
| POST | `/api/analytics/v3/sales-funnel/products/history` | Статистика карточек товаров по дням |
| GET | `/api/v2/nm-report/downloads` | Получить список отчётов |
| POST | `/api/v2/nm-report/downloads` | Создать отчёт |
| GET | `/api/v2/nm-report/downloads/file/{downloadId}` | Получить отчёт |
| POST | `/api/v2/nm-report/downloads/retry` | Сгенерировать отчёт повторно |
| POST | `/api/v2/search-report/product/orders` | Заказы и позиции по поисковым запросам товара |
| POST | `/api/v2/search-report/product/search-texts` | Поисковые запросы по товару |
| POST | `/api/v2/search-report/report` | Основная страница |
| POST | `/api/v2/search-report/table/details` | Пагинация по товарам в группе |
| POST | `/api/v2/search-report/table/groups` | Пагинация по группам |
| POST | `/api/v2/stocks-report/offices` | Данные по складам |
| POST | `/api/v2/stocks-report/products/groups` | Данные по группам |
| POST | `/api/v2/stocks-report/products/products` | Данные по товарам |
| POST | `/api/v2/stocks-report/products/sizes` | Данные по размерам |
<!-- AUTO:END -->

### Отчёты: хранение, приёмка, доля бренда, возвраты, удержания, штрафы (спека 12-reports)

<!-- AUTO:BEGIN spec=12-reports section=endpoints -->
| Метод | Путь | Назначение |
|---|---|---|
| GET | `/api/analytics/v1/deductions` | Подмены и неверные вложения |
| GET | `/api/analytics/v1/measurement-penalties` | Удержания за занижение габаритов упаковки |
| GET | `/api/analytics/v1/warehouse-measurements` | Замеры склада |
| GET | `/api/v1/acceptance_report` | Создать отчёт |
| GET | `/api/v1/acceptance_report/tasks/{task_id}/download` | Получить отчёт |
| GET | `/api/v1/acceptance_report/tasks/{task_id}/status` | Проверить статус |
| GET | `/api/v1/analytics/antifraud-details` | Самовыкупы |
| GET | `/api/v1/analytics/banned-products/blocked` | Получить отчёт |
| GET | `/api/v1/analytics/banned-products/shadowed` | Скрытые из каталога ⚠️ deprecated |
| GET | `/api/v1/analytics/brand-share` | Получить отчёт |
| GET | `/api/v1/analytics/brand-share/brands` | Бренды продавца |
| GET | `/api/v1/analytics/brand-share/parent-subjects` | Родительские категории бренда |
| POST | `/api/v1/analytics/excise-report` | Получить отчёт |
| GET | `/api/v1/analytics/goods-labeling` | Маркировка товара |
| GET | `/api/v1/analytics/goods-return` | Получить отчёт |
| GET | `/api/v1/analytics/region-sale` | Получить отчёт |
| GET | `/api/v1/paid_storage` | Создать отчёт |
| GET | `/api/v1/paid_storage/tasks/{task_id}/download` | Получить отчёт |
| GET | `/api/v1/paid_storage/tasks/{task_id}/status` | Проверить статус |
| GET | `/api/v1/warehouse_remains` | Создать отчёт |
| GET | `/api/v1/warehouse_remains/tasks/{task_id}/download` | Получить отчёт |
| GET | `/api/v1/warehouse_remains/tasks/{task_id}/status` | Проверить статус |
<!-- AUTO:END -->

> **Примечание — фактура прежнего справочника вне авто-колонок (тела запросов, тип sync/async, отключённые методы):**
>
> **Воронка продаж:**
> - **`POST /api/analytics/v3/sales-funnel/products`** — **АКТУАЛЬНАЯ** воронка по товарам,
>   **синхронный**, тело JSON `{selectedPeriod, nmIds, limit, offset, orderBy, ...}` (подробно —
>   раздел «Воронка продаж — подробно» ниже).
> - `POST /api/analytics/v3/sales-funnel/products/history` и `.../grouped/history` —
>   поденная/понедельная динамика (синхронные; grouped — по subject/brand/tag).
> - ⚠️ Отключённые пути: `GET /api/v2/sales-funnel/products` — **отключён 09.12.2025**;
>   `GET /api/v3/sales-funnel/products` — старый путь до миграции, **заменён** на `/api/analytics/v3/...`.
>
> **NM-отчёты:** `POST /api/v2/nm-report/downloads` — **асинхронный** (создать отчёт), список/статус
> и скачивание — `GET /api/v2/nm-report/downloads` и `GET /api/v2/nm-report/downloads/file/{downloadId}`,
> повтор — `POST /api/v2/nm-report/downloads/retry`. Прежний синхронный `GET /api/v1/nm-report/detail`
> в спеке отсутствует — проверь вживую.
>
> **Асинхронные отчёты** (создать → статус → скачать по `task_id`, workflow — см. `04-async-tasks.md`):
> платное хранение (`GET /api/v1/paid_storage`), приёмка (`GET /api/v1/acceptance_report`), остатки на
> складах (`GET /api/v1/warehouse_remains`). Создающий запрос — **GET** (в старой документации был POST).
> Готовый отчёт хранения живёт 2 часа, данные — за последние 90 дней; формат — CSV в ZIP.
> Доля бренда и самовыкупы — **синхронные** `GET` (не async): `GET /api/v1/analytics/brand-share`,
> `GET /api/v1/analytics/antifraud-details`.
>
> **Доля бренда:** в спеке — `GET /api/v1/analytics/brand-share` (+ `/brands`, `/parent-subjects`).
> Прежний справочник указывал **асинхронный** `POST /api/v2/brands/report-downloads` — **заменён** на brand-share.
>
> **Прочее:** возвраты товаров — `GET /api/v1/analytics/goods-return`; акцизы —
> `POST /api/v1/analytics/excise-report` (прежде указывался как `GET /api/v1/analytics/excise`).

**Что изменилось в актуальной воронке v3:**
- Префикс пути: `/api/v3/...` → `/api/analytics/v3/...`
- Метод: GET → **POST**, параметры переехали в JSON-body
- Период задаётся объектом `selectedPeriod {start, end}` (не плоскими `dateFrom/dateTo`)
- Пагинация — **offset/limit** (`limit` до 1000, дефолт 50; `offset` сдвигает страницу)
- Ошибки больше не приходят в теле успешного ответа — проверять HTTP-статус

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
curl -X GET "https://seller-analytics-api.wildberries.ru/api/v1/paid_storage?dateFrom=2024-06-01&dateTo=2024-06-07" \
  -H "Authorization: Bearer TOKEN"
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
