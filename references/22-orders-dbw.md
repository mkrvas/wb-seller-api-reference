# Orders DBW — заказы с доставкой силами WB

## Назначение

Раздел добавлен автоконвейером: таблица ниже генерируется из официальной
спеки. Рукописные заметки (лимиты, грабли) наполняются по мере боевого
использования — пока считать файл справочным, не боевым.

DBW (Доставка курьером WB) — модель, при которой курьер WB забирает заказ у
продавца и доставляет его покупателю сам (в отличие от FBS, где WB забирает
товар со своего склада/ПВЗ по расписанию поставок, и от DBS, где доставку до
покупателя организует продавец). Управление сборочными заданиями и
идентификаторами маркировки — как у FBS/DBS, просто другой набор путей.

**Хост:** `marketplace-api.wildberries.ru`  
**Scope токена:** Marketplace  
**Rate limit:** 300 запр/мин (общий лимит хоста Marketplace API; 409 Conflict — 5 запросов, см. `01-rate-limits-retry.md`)  
**Версия:** /api/v3/

> В спеке `04-orders-dbw` поле `servers` пустое (`[]`). Хост взят из `00-overview.md`
> (там `Marketplace → marketplace-api.wildberries.ru` — уже задокументированный факт,
> не предположение) — пути спеки (`/api/v3/dbw/...`, `/api/marketplace/v3/dbw/...`)
> лежат в тех же префиксах, что и семейство FBS (`11-marketplace.md`) и подтверждённое
> семейство Самовывоз (`06-in-store-pickup`, там `servers` указан явно).

## Эндпоинты

<!-- AUTO:BEGIN spec=04-orders-dbw section=endpoints -->
| Метод | Путь | Назначение |
|---|---|---|
| POST | `/api/marketplace/v3/dbw/orders/client` | Информация о покупателе |
| POST | `/api/marketplace/v3/dbw/orders/status/deliver` | Перевести сборочные задания в доставку |
| GET | `/api/v3/dbw/orders` | Получить информацию о завершенных сборочных заданиях |
| POST | `/api/v3/dbw/orders/courier` | Информация о курьере |
| POST | `/api/v3/dbw/orders/delivery-date` | Получить дату и время доставки |
| GET | `/api/v3/dbw/orders/new` | Получить список новых сборочных заданий |
| POST | `/api/v3/dbw/orders/status` | Получить статусы сборочных заданий |
| POST | `/api/v3/dbw/orders/stickers` | Получить стикеры сборочных заданий |
| PATCH | `/api/v3/dbw/orders/{orderId}/confirm` | Перевести на сборку |
<!-- AUTO:END -->

## Ссылка на оригинал

https://dev.wildberries.ru/openapi/orders-dbw
