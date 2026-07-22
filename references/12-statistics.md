# Statistics API — Статистика

> ## ⚠️ ВАЖНО: `reportDetailByPeriod` DEPRECATED
>
> Эндпоинт `GET /api/v5/supplier/reportDetailByPeriod` официально отключается **с 15 июля 2026** —
> эта дата уже прошла на момент последней проверки справочника (2026-07-21). Фактический live-статус
> метода (отдаёт ли он уже ошибку, и какую) не подтверждён напрямую — `dev.wildberries.ru` блокирует
> автоматическую проверку. Перед использованием проверь вживую с реальным токеном.
>
> **Замена:** Finance API — см. [12a-finance.md](12a-finance.md).
>
> Новый путь: `POST /api/finance/v1/sales-reports/list` → `POST /api/finance/v1/sales-reports/detailed/{reportId}` на хосте `finance-api.wildberries.ru`.
>
> Остальные эндпоинты Statistics API (stocks, orders, sales, incomes) — по независимой перепроверке
> одного аудита подтверждены актуальными; другой аудит (по инфраструктурным файлам скилла) нашёл
> сигнал, что именно `stocks` мог быть заменён 23.06.2026 на `POST /api/analytics/v1/stocks-report/wb-warehouses`
> (Analytics API). Источники противоречат друг другу и оба — вторичные (не сам dev.wildberries.ru).
> ⚠️ Проверь вручную, прежде чем полагаться на `stocks` в новой интеграции.

## Назначение

Продажи, заказы, остатки товаров **на складах WB**, поставки, ~~финансовый детализированный отчёт реализации~~ (deprecated → Finance API).

**Хост:** `statistics-api.wildberries.ru`  
**Scope токена:** Statistics  
**Версии:** /api/v1/, /api/v5/

## Rate limits

| Эндпоинт | Лимит |
|---|---|
| `/api/v5/supplier/reportDetailByPeriod` ⚠️ deprecated | 1 запр/мин |
| `/api/v1/supplier/stocks` | 3 запр / 30 сек |
| `/api/v1/supplier/orders` | 1 запр/мин |
| `/api/v1/supplier/sales` | 1 запр/мин |
| `/api/v1/supplier/incomes` | 1 запр/мин |

## Эндпоинты

<!-- AUTO:BEGIN spec=12-reports section=endpoints -->
| Метод | Путь | Назначение |
|---|---|---|
| GET | `/api/v1/supplier/orders` | Заказы |
| GET | `/api/v1/supplier/sales` | Продажи |
<!-- AUTO:END -->

> **Примечание (эндпоинты вне авто-таблицы — их НЕТ в снапшоте спеки, сохранено из прежнего справочника):**
> В официальной спеке `12-reports` под хостом `statistics-api.wildberries.ru` есть только
> `supplier/orders` и `supplier/sales`. Остальные исторические эндпоинты этого хоста в спеку не
> попали и остаются здесь вручную:
> - `GET /api/v5/supplier/reportDetailByPeriod` — ⚠️ **DEPRECATED, отключение 15.07.2026**
>   (параметры `dateFrom`, `dateTo`, `rrdid`, `limit`; пагинация по `rrdid`; лимит 1 запр/мин).
>   Замена — Finance API (`12a-finance.md`). Подробный разбор — в разделе ниже.
> - `GET /api/v1/supplier/stocks` — остатки на складах WB (пагинация `offset`, лимит ответа 60000
>   строк, лимит 3 запр/30 сек). ⚠️ По вторичному сигналу мог быть заменён 23.06.2026 на
>   `POST /api/analytics/v1/stocks-report/wb-warehouses` (Analytics API) — проверь вживую. Разбор ниже.
> - `GET /api/v1/supplier/incomes` — поставки товара на склады WB (параметры `dateFrom`, `dateTo`;
>   лимит 1 запр/мин).
> - `supplier/orders` и `supplier/sales` дополнительно разобраны в разделах ниже (лимит 1 запр/мин каждый).

---

## reportDetailByPeriod — Финансовый отчёт (⚠️ DEPRECATED)

> **ВНИМАНИЕ:** Этот эндпоинт будет отключён **15 июля 2026**.
> Для новых интеграций использовать **Finance API** — см. [12a-finance.md](12a-finance.md).
>
> Описание ниже оставлено для поддержки существующего кода и понимания старых данных.

Эндпоинт раньше использовался как замена ручной выгрузки «Еженедельный детализированный отчет*.xlsx».

### Запрос

```
GET /api/v5/supplier/reportDetailByPeriod
    ?dateFrom=2024-06-01
    &dateTo=2024-06-07
    &rrdid=0
    &limit=100000
```

| Параметр | Обязателен | Описание |
|---|---|---|
| `dateFrom` | да | Начало периода (RFC3339, напр. `2024-06-01`) |
| `dateTo` | да | Конец периода (YYYY-MM-DD) |
| `rrdid` | нет | ID строки для пагинации (0 для первого запроса) |
| `limit` | нет | Макс. строк в ответе (рекомендуется 100000) |

### Пагинация через rrdid

См. подробно `03-pagination.md`, раздел «rrdid».

Коротко:
1. Первый запрос: `rrdid=0`
2. Из ответа берём последний `rrd_id`
3. Следующий запрос: `rrdid=<последний_rrd_id>`
4. Повторять, пока записей < `limit`
5. **Пауза 60 сек** между запросами (лимит 1/мин)

### Поля ответа

```json
{
  "data": [
    {
      "rrd_id": 1001,
      "date": "2024-06-20",
      "last_change_date": "2024-06-21T10:30:00Z",
      "supplier_oper_name": "Продажа",
      "supplier_oper_id": 1,
      "order_date": "2024-06-20T08:00:00Z",
      "nm_id": 123456,
      "brand": "Бренд",
      "brand_id": 789,
      "subject": "Категория",
      "subject_id": 100,
      "name": "Название товара",
      "quantity": 1,
      "retail_price": 4999.00,
      "retail_amount": 4999.00,
      "sales": 4999.00,
      "commission_percent": 20,
      "commission_amount": 999.80,
      "delivery_charge": 50.00,
      "delivery_rub": 150.00,
      "return_amount": 0,
      "penalty": 0.00,
      "fine": 0.00,
      "nds": 806.10,
      "nds_amount": 806.10,
      "acquiring": 100.00,
      "acquiring_percent": 2.5,
      "acquiring_fee": 100.00,
      "warehouse_name": "Тверь",
      "warehouse_id": 12321,
      "ppvz_spp_prc": 0,
      "ppvz_kvw_prc_u": 0,
      "ppvz_vat_prc": 18,
      "ppvz_vat_amount": 806.10,
      "ppvz_office_id": 1,
      "ppvz_supplier_id": 12345,
      "ppvz_inn": "7701234567",
      "spp_fix": 0,
      "super_com": null,
      "logistic_discount": 0.00,
      "stornos_count": 0,
      "bonuses_buy": 0.00,
      "bonuses_fact": 0.00,
      "return_date": null,
      "claim_status": 0
    }
  ]
}
```

### Ключевые поля ответа

| Поле | Тип | Описание |
|---|---|---|
| `nm_id` | int | Артикул WB |
| `supplier_oper_name` | string | Тип операции: «Продажа» / «Возврат» |
| `quantity` | int | Количество, шт |
| `retail_amount` | float | Сумма продажи по розничной цене, ₽ |
| `commission_amount` | float | Комиссия WB, ₽ |
| `delivery_rub` | float | Логистика, ₽ |
| `penalty` + `fine` | float | Штрафы, ₽ |
| `brand` | string | Бренд |
| `subject` | string | Предмет (категория) |
| `name` | string | Название товара |

### Типичная агрегация

Для сводного отчёта по товарам — группировка по `nm_id`, разделение по `supplier_oper_name`:
- «Продажа» → qty_sales, rev_sales
- «Возврат» → qty_ret, rev_ret
- Суммирование: commission_amount → commission, delivery_rub → logistics, penalty+fine → fines

### Подводные камни

- **rrd_id может быть не монотонным** — при пересчёте появляются дыры
- **Данные пересчитываются** — значения за прошлые даты могут измениться (не финальны < 7 дней)
- **Данные доступны с 29 января 2024**
- **Лимит: строго 1 запрос в минуту** — самый жёсткий во всём API
- Используй `limit=100000` чтобы минимизировать число запросов
- Для одной недели (~30-50 товаров) обычно хватает 1 запроса

---

## stocks — Остатки на складах WB

Заменяет ручную выгрузку `report_*.xlsx`.

### Запрос

```bash
curl -X GET "https://statistics-api.wildberries.ru/api/v1/supplier/stocks" \
  -H "Authorization: Bearer TOKEN"
```

### Ключевые поля ответа

| Поле | Маппинг в Юнит-листе |
|---|---|
| `nmId` | A (Артикул WB) |
| `inWayToClient` | E (В пути до клиента) |
| `inWayFromClient` | F (В пути от клиента) |
| `quantityFull` | G (Итого по складам ВБ) |
| `warehouseName` | Название склада |

### Подводные камни

- **Только текущие остатки** — история не хранится. Для исторических данных нужно сохранять самостоятельно.
- **Обновляются каждые 30 минут** — частые запросы дадут те же данные
- **Лимит ответа: 60000 строк** — если товаров больше, нужна пагинация через offset
- Лимит запросов: 3 за 30 сек

---

## orders — Заказы покупателей

```bash
curl -X GET "https://statistics-api.wildberries.ru/api/v1/supplier/orders?dateFrom=2024-06-01&dateTo=2024-06-07" \
  -H "Authorization: Bearer TOKEN"
```

Возвращает все заказы за период (все статусы). Лимит: 1 запр/мин.

## sales — Продажи и возвраты

```bash
curl -X GET "https://statistics-api.wildberries.ru/api/v1/supplier/sales?dateFrom=2024-06-01&dateTo=2024-06-07" \
  -H "Authorization: Bearer TOKEN"
```

Возвращает продажи и возвраты за период. Лимит: 1 запр/мин.

## Ссылка на оригинал

https://dev.wildberries.ru/openapi/statistics
