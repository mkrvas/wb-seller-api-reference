# Marketplace API — Маркетплейс

## Назначение

FBS заказы (сборочные задания), поставки, управление складами продавца, остатки товара продавца на собственных складах.

**Хост:** `marketplace-api.wildberries.ru`  
**Scope токена:** Marketplace  
**Rate limit:** 300 запр/мин (409 = 5 запросов; 409 для DBS = 10)  
**Версия:** /api/v3/

## Эндпоинты

### Заказы (сборочные задания)

| Метод | Путь | Назначение | Параметры |
|---|---|---|---|
| GET | /api/v3/orders | Получить новые FBS заказы | limit, offset, status |
| GET | /api/v3/orders/{id} | Детали заказа | orderId |
| PATCH | /api/v3/orders/{id} | Обновить статус заказа | orderId, status |
| PATCH | /api/v3/orders/{orderId}/meta | Обновить комментарии | orderId |
| GET | /api/v3/orders/dbs | Заказы DBS | — |
| POST | /api/v3/orders/stickers | Этикетки для FBS заказов | orderIDs |
| POST | /api/v3/orders/stickers/cross-border | Этикетки трансграничная доставка | orderIDs |

### Поставки

| Метод | Путь | Назначение | Параметры |
|---|---|---|---|
| POST | /api/v3/supplies | Создать поставку | warehouseID |
| GET | /api/v3/supplies | Список поставок | limit, offset |
| GET | /api/v3/supplies/{id} | Детали поставки | supplyID |
| PUT | /api/v3/supplies/{id} | Изменить поставку | supplyID |
| DELETE | /api/v3/supplies/{id} | Удалить поставку | supplyID |
| PATCH | /api/v3/supplies/{id}/close | Закрыть поставку | supplyID |
| POST | /api/v3/supplies/{id}/orders | Добавить заказы в поставку | supplyID, orderIDs |
| GET | /api/v3/supplies/{id}/orders | Заказы в поставке | supplyID |
| GET | /api/v3/supplies/{id}/barcode | Штрих-код поставки | supplyID |

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
