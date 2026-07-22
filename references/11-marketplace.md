# Marketplace API — Маркетплейс

## Назначение

FBS заказы (сборочные задания), поставки, управление складами продавца, остатки товара продавца на собственных складах.

**Хост:** `marketplace-api.wildberries.ru`  
**Scope токена:** Marketplace  
**Rate limit:** 300 запр/мин (409 = 5 запросов; 409 для DBS = 10)  
**Версия:** /api/v3/

## Эндпоинты

<!-- AUTO:BEGIN spec=03-orders-fbs section=endpoints -->
| Метод | Путь | Назначение |
|---|---|---|
| GET | `/api/marketplace/v3/fbs/orders/archive` | Получить список архивных сборочных заданий |
| POST | `/api/marketplace/v3/orders/meta` | Получить идентификаторы маркировки сборочных заданий |
| PUT | `/api/marketplace/v3/orders/{orderId}/meta/customs-declaration` | Закрепить за сборочным заданием номер ДТ |
| GET | `/api/marketplace/v3/supplies/{supplyId}/order-ids` | Получить ID сборочных заданий поставки |
| PATCH | `/api/marketplace/v3/supplies/{supplyId}/orders` | Добавить сборочные задания к поставке |
| GET | `/api/v3/orders` | Получить информацию о сборочных заданиях |
| POST | `/api/v3/orders/client` | Заказы с информацией по клиенту |
| GET | `/api/v3/orders/new` | Получить список новых сборочных заданий |
| POST | `/api/v3/orders/status` | Получить статусы сборочных заданий |
| POST | `/api/v3/orders/status/history` | История статусов для сборочных заданий трансграничных поставок |
| POST | `/api/v3/orders/stickers` | Получить стикеры сборочных заданий |
| POST | `/api/v3/orders/stickers/cross-border` | Получить стикеры сборочных заданий трансграничных поставок |
| PATCH | `/api/v3/orders/{orderId}/cancel` | Отменить сборочное задание |
| DELETE | `/api/v3/orders/{orderId}/meta` | Удалить идентификаторы маркировки сборочного задания |
| PUT | `/api/v3/orders/{orderId}/meta/expiration` | Закрепить за сборочным заданием срок годности товара |
| PUT | `/api/v3/orders/{orderId}/meta/gtin` | Закрепить за сборочным заданием GTIN |
| PUT | `/api/v3/orders/{orderId}/meta/imei` | Закрепить за сборочным заданием IMEI |
| PUT | `/api/v3/orders/{orderId}/meta/sgtin` | Закрепить за сборочным заданием код маркировки Честного знака |
| PUT | `/api/v3/orders/{orderId}/meta/uin` | Закрепить за сборочным заданием УИН |
| GET | `/api/v3/passes` | Получить список пропусков |
| POST | `/api/v3/passes` | Создать пропуск |
| GET | `/api/v3/passes/offices` | Получить список складов, для которых требуется пропуск |
| DELETE | `/api/v3/passes/{passId}` | Удалить пропуск |
| PUT | `/api/v3/passes/{passId}` | Обновить пропуск |
| GET | `/api/v3/supplies` | Получить список поставок |
| POST | `/api/v3/supplies` | Создать новую поставку |
| GET | `/api/v3/supplies/orders/reshipment` | Получить все сборочные задания для повторной отгрузки |
| DELETE | `/api/v3/supplies/{supplyId}` | Удалить поставку |
| GET | `/api/v3/supplies/{supplyId}` | Получить информацию о поставке |
| GET | `/api/v3/supplies/{supplyId}/barcode` | Получить QR-код поставки |
| PATCH | `/api/v3/supplies/{supplyId}/deliver` | Передать поставку в доставку |
| DELETE | `/api/v3/supplies/{supplyId}/trbx` | Удалить грузоместа из поставки |
| GET | `/api/v3/supplies/{supplyId}/trbx` | Получить список грузомест поставки |
| POST | `/api/v3/supplies/{supplyId}/trbx` | Добавить грузоместа к поставке |
| POST | `/api/v3/supplies/{supplyId}/trbx/stickers` | Получить стикеры грузомест поставки |
<!-- AUTO:END -->

> **Примечание (сохранено из прежнего справочника):**
> - Авто-таблица из спеки `03-orders-fbs` покрывает FBS: заказы (`/api/v3/orders*`), поставки
>   (`/api/v3/supplies*`), пропуска (`/api/v3/passes*`) и работу с маркировкой (`/api/marketplace/v3/*`).
>   Она уточняет прежние таблицы: «закрыть поставку» — это `PATCH /api/v3/supplies/{supplyId}/deliver`
>   (в старом справочнике было ошибочное `.../close`); статусы заказов запрашиваются/меняются через
>   `POST /api/v3/orders/status` (а не через `PATCH /api/v3/orders/{id}`). Отмена — `PATCH /api/v3/orders/{orderId}/cancel`.
>   См. также блок «Требует ручной проверки» ниже — часть отмеченных там сомнений спека разрешает.
> - Заказы **DBS** — отдельное семейство (`/api/v3/dbs/*`, будущий `23-orders-dbs.md`), в этой спеке их нет.

> **Склады и остатки продавца (`/api/v3/warehouses`, `/api/v3/stocks`) в спеке `03-orders-fbs`
> ОТСУТСТВУЮТ** — это отдельная категория API. Таблицы ниже сохранены вручную из прежнего справочника.

### Склады продавца

| Метод | Путь | Назначение | Параметры |
|---|---|---|---|
| GET | /api/v3/warehouses | Список складов | — |
| POST | /api/v3/warehouses | Создать склад | name, address |
| GET | /api/v3/warehouses/{id} | Детали склада | warehouseId |
| PATCH | /api/v3/warehouses/{id} | Обновить склад | warehouseId |
| DELETE | /api/v3/warehouses/{id} | Удалить склад | warehouseId |

### Остатки продавца (на своих складах)

| Метод | Путь | Назначение | Параметры |
|---|---|---|---|
| POST | /api/v3/stocks | Загрузить остатки | warehouseID, sku, quantity |
| GET | /api/v3/stocks/{warehouseId} | Остатки на складе | warehouseId, limit, offset |
| POST | /api/v3/stocks/{warehouseId} | Обновить остатки | warehouseId |
| PUT | /api/v3/stocks/{warehouseId} | Заменить остатки (полная) | warehouseId |
| DELETE | /api/v3/stocks/{warehouseId} | Удалить остатки | warehouseId, skus |

**Важно:** Это остатки **продавца** на его собственных FBS-складах. Остатки **на складах WB** — через Statistics API (`/api/v1/supplier/stocks`), см. `12-statistics.md`.

## Пример: получить заказы

```bash
curl -X GET "https://marketplace-api.wildberries.ru/api/v3/orders?limit=50&offset=0" \
  -H "Authorization: Bearer TOKEN"
```

Ответ:
```json
{
  "orders": [
    {
      "id": 987654,
      "number": "AB123456",
      "createdAt": "2024-06-20T10:30:00Z",
      "status": "new",
      "totalPrice": 4999.00
    }
  ],
  "pagination": { "offset": 0, "limit": 50, "total": 150 }
}
```

## Подводные камни

- FBS заказы нужно опрашивать регулярно (каждые 5-15 мин)
- 409 Conflict считается за 5 обычных запросов (DBS — за 10)
- Остатки Marketplace API ≠ остатки Statistics API (разные склады!)

> ⚠️ **Требует ручной проверки** (аудит от 2026-07-21, вторичные источники, не первоисточник):
> - `GET /api/v3/orders/{id}` и `PATCH /api/v3/orders/{id}` — существование именно в такой обобщённой
>   форме под вопросом; статус, похоже, меняется пакетно через `POST /api/v3/orders/status`
> - `GET /api/v3/orders/dbs` — вероятно должно быть `GET /api/v3/dbs/orders`
> - `PATCH /api/v3/supplies/{id}/close` — вероятно должно быть `POST /api/v3/supplies/{id}/deliver`
> - `PATCH /api/v3/warehouses/{id}` — HTTP-метод под вопросом (возможно `PUT` или `POST`)
> - `POST /api/v3/stocks` без `{warehouseId}` — вероятная ошибка/дубль в таблице
> - Точная стоимость 409 Conflict (5 vs 10) — источники противоречат друг другу
> - Не упомянута новая модель заказов **DBW**, появившаяся в 2025
>
> Проверь эти пункты вживую перед использованием в продакшене.

## Ссылка на оригинал

https://dev.wildberries.ru/openapi/marketplace
