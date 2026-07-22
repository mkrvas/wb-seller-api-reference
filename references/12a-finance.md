# Finance API — Финансы (ОСНОВНОЕ)

## Назначение

Отчёты реализации (еженедельные и **ежедневные**), детализация по `reportId` или за период, отчёты эквайринга (издержки приёма платежей), баланс продавца.

**С 15 июля 2026 это единственный источник финансовых данных.** Старый `GET /api/v5/supplier/reportDetailByPeriod` на `statistics-api.wildberries.ru` будет отключён.

**Хост:** `finance-api.wildberries.ru`  
**Scope токена:** Finance  
**Типы токенов:** Персональный, Сервисный (Basic и Sandbox — не поддерживаются)  
**Rate limit:** **1 запрос / мин** на весь Finance API (всплеск 1)  
**Версия:** /api/v1/ и /api/finance/v1/

## Дата запуска и миграция

- **Запущен:** 15 апреля 2026
- **Старый эндпоинт** `GET /api/v5/supplier/reportDetailByPeriod` — **deprecated**, удаление **15 июля 2026**

## Эндпоинты

<!-- AUTO:BEGIN spec=13-finances section=endpoints -->
| Метод | Путь | Назначение |
|---|---|---|
| POST | `/api/finance/v1/acquiring/detailed` | Детализации к отчётам об издержках на приём платежей за период |
| POST | `/api/finance/v1/acquiring/detailed/{reportId}` | Детализации к отчётам об издержках на приём платежей по ID отчётов |
| POST | `/api/finance/v1/acquiring/list` | Список отчётов об издержках на приём платежей |
| POST | `/api/finance/v1/sales-reports/detailed` | Детализации к отчётам реализации за период |
| POST | `/api/finance/v1/sales-reports/detailed/{reportId}` | Детализации к отчётам реализации по ID отчётов |
| POST | `/api/finance/v1/sales-reports/list` | Список отчётов реализации |
| GET | `/api/v1/account/balance` | Получить баланс продавца |
<!-- AUTO:END -->

> **Примечание (факты вне авто-таблицы, сохранено из прежнего справочника):**
> - `sales-reports/list` возвращает список отчётов (тип `daily` / `weekly` задаётся телом),
>   `sales-reports/detailed/{reportId}` — детализация по ID (основной способ),
>   `sales-reports/detailed` — за произвольный период. Подробно — в разделах ниже.
> - Эквайринг (`acquiring/*`) — **только по операциям в России**.
> - Спека `13-finances` также содержит документы (`/api/v1/documents/*`) — они вынесены в
>   `20-documents.md` (хост `documents-api.wildberries.ru`), сюда не попадают по фильтру.
> - Лимит на всё семейство — **1 запрос/мин** (всплеск 1). Параметры тел, поля ответов (~80 полей),
>   BigInt для ежедневных `reportId`, пагинация по `rrdId` (стоп — `204`) — в разделах ниже.

## Типы отчётов реализации

| Тип | Параметр `period` | Когда формируется |
|---|---|---|
| **Ежедневный** | `"daily"` | Каждый день (точное время в доке не указано) |
| **Еженедельный** | `"weekly"` (default) | **Понедельник, 8:00–11:00 МСК** (по итогам прошедшей недели Пн–Вс) |

**Важно:** Тип отчёта выбирается **параметром запроса** `period`, а не различается эндпоинтом. Поле `reportType` в ответе `/list` всегда `= 1` — его семантика в доке не раскрыта.

## Глубина истории

| Эндпоинт | Данные с |
|---|---|
| `/sales-reports/detailed/{reportId}` (по ID) | **1 января 2025** |
| `/sales-reports/detailed` (за период) | 29 января 2024 |
| `/acquiring/*` | не указано в доке |

---

## POST /api/finance/v1/sales-reports/list — Список отчётов

Получить список доступных отчётов (чтобы потом брать детализацию по `reportId`).

### Запрос

```bash
curl -X POST https://finance-api.wildberries.ru/api/finance/v1/sales-reports/list \
  -H "Authorization: Bearer TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "dateFrom": "2025-01-01T00:00:00Z",
    "dateTo":   "2025-01-31T23:59:59Z",
    "period":   "daily",
    "limit":    1000,
    "offset":   0
  }'
```

### Параметры

| Поле | Тип | Обязат. | Описание |
|---|---|---|---|
| `dateFrom` | string (RFC3339) | да | Начало периода |
| `dateTo` | string (RFC3339) | да | Конец периода |
| `period` | `"daily"` \| `"weekly"` | нет | Тип отчётов (default: `"weekly"`) |
| `limit` | int ≤ 1000 | нет | Default: 1000 |
| `offset` | int | нет | Default: 0 |

### Пример ответа

```json
{
  "data": [
    {
      "reportId": 123456789,
      "sellerFinanceName": "ООО «Ромашка»",
      "dateFrom": "2025-06-01T00:00:00Z",
      "dateTo": "2025-06-07T23:59:59Z",
      "createDate": "2025-06-09T08:30:00Z",
      "currency": "RUB",
      "reportType": 1,
      "retailAmountSum": 150000.00,
      "forPaySum": 110000.00,
      "deliveryServiceSum": 5000.00,
      "paidStorageSum": 1200.00,
      "paidAcceptanceSum": 500.00,
      "deductionSum": 0.00,
      "penaltySum": 300.00,
      "additionalPaymentSum": 0.00,
      "cashbackAmountSum": 250.00,
      "paymentSchedule": -1,
      "bankPaymentSum": 108000.00
    }
  ]
}
```

### ⚠️ BigInt для ежедневных reportId

Для **ежедневных** отчётов `reportId` может быть очень большим числом (int64, близко к границе). Стандартный JSON-парсер в некоторых языках теряет точность.

**Решение:**
- JavaScript: `JSON.parse` с `reviver` или библиотеки типа `json-bigint`
- Python: `json.loads(..., parse_int=int)` обычно справляется, но при сериализации обратно — внимание к точности
- Go: использовать `json.Number` или `*big.Int`
- При запросе `/sales-reports/detailed/{reportId}` — передавать **строку**, а не число

---

## POST /api/finance/v1/sales-reports/detailed/{reportId} — Детализация по ID

Это **основной способ** получать финотчёт — сначала из `/list` узнаёшь `reportId`, потом тянешь детализацию.

### Запрос

```bash
curl -X POST "https://finance-api.wildberries.ru/api/finance/v1/sales-reports/detailed/123456789" \
  -H "Authorization: Bearer TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "limit":  100000,
    "rrdId":  0,
    "fields": []
  }'
```

### Параметры

| Path | Описание |
|---|---|
| `reportId` | int64 — ID отчёта из `/list`. Для ежедневных — передавать строкой |

| Body | Тип | Описание |
|---|---|---|
| `limit` | int ≤ 100000 | Макс. строк в ответе (default: 100000) |
| `rrdId` | int | Пагинация — передать последний `rrdId` из предыдущего ответа (default: 0) |
| `fields` | array of string | Фильтр полей (если пусто — возвращаются все) |

### Пагинация через rrdId

1. Первый запрос: `rrdId = 0`
2. Из ответа берём последний `rrdId`
3. Следующий запрос: `rrdId = <последний>`
4. **Стоп-условие:** ответ `204 No Content` (не как раньше — меньше лимита)
5. **Пауза 60 сек** между запросами (лимит 1/мин на всё API)

### Ключевые поля ответа (~80 полей)

```
Идентификация
  rrdId, giId, nmId, brandName, vendorCode, title, techSize, sku, subjectName, shkId

Операция
  docTypeName, sellerOperName, orderDt, saleDt, rrDate, officeName, quantity

Цены и суммы
  retailPrice, retailAmount, retailPriceWithDisc, salePercent, commissionPercent
  forPay, deliveryAmount, returnAmount, deliveryService
  ppvzSalesCommission, ppvzReward, rebillLogisticCost

Эквайринг
  acquiringFee, acquiringPercent, acquiringBank

Хранение/приёмка/штрафы
  paidStorage, paidAcceptance, penalty, deduction, additionalPayment

НДС и юрлицо
  vw, vwNds, ppvzOfficeName, ppvzOfficeId, ppvzSupplierName, ppvzSupplierInn
  declarationNumber, agencyVat

Прочее
  bonusTypeName, kiz, isB2b, trbxId, srid, orderUid, orderId

Новые поля (только Finance API, НЕТ в старом Statistics)
  wibesDiscountPercent        -- скидка WB-клуба
  cashbackAmount              -- кешбек
  cashbackDiscount            -- скидка от кешбека
  cashbackCommissionChange    -- корректировка комиссии из-за кешбека
  paymentSchedule             -- график платежей (-1 в примерах, семантика не раскрыта)
  deliveryMethod              -- способ доставки
  sellerPromoId               -- ID промо-акции продавца
  sellerPromoDiscount         -- скидка по промо
  loyaltyId                   -- ID программы лояльности
  loyaltyDiscount             -- скидка по лояльности
  uuidPromocode               -- промокод
  salePricePromocodeDiscountPrc
  salePriceAffiliatedDiscountPrc
  salePriceWholesaleDiscountPrc
  articleSubstitution         -- подмена артикула
  installmentCofinancingAmount -- рассрочка
  dlvPrc                      -- логистика в процентах
  fixTariffDateFrom, fixTariffDateTo  -- период фиксированного тарифа
  srvDbs                      -- сервисный сбор DBS
```

---

## POST /api/finance/v1/sales-reports/detailed — Детализация за период

Альтернатива — без получения `reportId`, сразу по датам. Полезно если не нужна привязка к конкретному отчёту.

### Запрос

```bash
curl -X POST https://finance-api.wildberries.ru/api/finance/v1/sales-reports/detailed \
  -H "Authorization: Bearer TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "dateFrom": "2025-06-01T00:00:00Z",
    "dateTo":   "2025-06-07T23:59:59Z",
    "period":   "weekly",
    "limit":    100000,
    "rrdId":    0,
    "fields":   []
  }'
```

Параметры тела — те же, что у `/detailed/{reportId}`, плюс `dateFrom`, `dateTo`, `period`.

---

## GET /api/v1/account/balance — Баланс

### Запрос

```bash
curl -X GET "https://finance-api.wildberries.ru/api/v1/account/balance" \
  -H "Authorization: Bearer TOKEN"
```

### Ответ

```json
{
  "currency": "RUB",
  "current": 10196.21,
  "for_withdraw": 6395.80
}
```

- `current` — текущий баланс
- `for_withdraw` — доступно к выводу

---

## Эквайринг — структура

Эндпоинты `/acquiring/*` работают аналогично `/sales-reports/*`:
- `/list` — список отчётов эквайринга
- `/detailed/{reportId}` — детализация по ID
- `/detailed` — за период

### Ключевые поля ответа эквайринга

```
rrdId, reportId, acqDate, acquiringBank, tin (ИНН), taxRegistrationReasonCode (КПП)
saleDate, srid, docTypeName, nmId, retailAmount
acquiringFee, acquiringFeeVat, acquiringPercent
invoiceNumber, invoiceDate, shkId, currency
```

**Ограничение:** только по операциям в России.

---

## Типичный workflow для еженедельной отчётности

```
1. GET /api/finance/v1/sales-reports/list
     body: { dateFrom, dateTo, period: "weekly" }
   → получить reportId последнего еженедельного отчёта

2. sleep 60 сек (лимит 1/мин)

3. POST /api/finance/v1/sales-reports/detailed/{reportId}
     body: { limit: 100000, rrdId: 0 }
   → получить детализацию

4. Если ответ не 204 — взять последний rrdId, sleep 60, повторить с ним

5. Агрегация по nmId, разделение по sellerOperName ("Продажа" / "Возврат")
```

## Workflow для дашборда на ежедневных

```
1. GET /api/finance/v1/sales-reports/list  
     body: { dateFrom: вчера, dateTo: вчера, period: "daily" }
   → получить reportId вчерашнего отчёта

2. sleep 60 сек

3. POST /api/finance/v1/sales-reports/detailed/{reportId}
     body: { limit: 100000, rrdId: 0 }
   → детализация за день

4. Повторять каждый день по расписанию
```

## Подводные камни

- **Лимит 1 запрос/мин** на всё семейство — не только на один эндпоинт. Выдерживать паузу между `/list` и `/detailed`.
- **BigInt для ежедневных reportId** — см. выше
- **Признак конца пагинации** — `204 No Content`, а не «меньше лимита» как в старом API
- **reportType в ответе `/list`** — всегда `1`, не использовать для определения типа. Тип задаёт параметр `period` запроса.
- **`paymentSchedule`** со значением `-1` — семантика в доке не раскрыта
- **Еженедельный отчёт** формируется понедельник 8-11 МСК — запрашивать позже этого времени
- **Данные по reportId доступны только с 01.01.2025** — для исторических данных до этой даты использовать `/detailed` за период (где глубина до 29.01.2024)
- **Эквайринг только Россия** — для зарубежных операций этих данных нет

## Ссылки

- Документация: https://dev.wildberries.ru/docs/openapi/financial-reports-and-accounting
- Swagger: https://dev.wildberries.ru/swagger/finances
- Release notes о запуске: https://dev.wildberries.ru/release-notes?id=293
