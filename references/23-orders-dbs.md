# Orders DBS — заказы с доставкой продавцом

## Назначение

Раздел добавлен автоконвейером: таблица ниже генерируется из официальной
спеки. Рукописные заметки (лимиты, грабли) наполняются по мере боевого
использования — пока считать файл справочным, не боевым.

DBS (Delivery by Seller) — модель, при которой продавец сам доставляет заказ
покупателю (в отличие от FBS/DBW, где логистику от склада до двери берёт на
себя WB). Раздел покрывает сборочные задания DBS и их идентификаторы
маркировки (GTIN/IMEI/УИН/код Честного знака), а также B2B-заказы DBS.
Методы можно протестировать в песочнице (`/sandbox`), включая эмуляцию
действий покупателя.

**Хост:** `marketplace-api.wildberries.ru`  
**Scope токена:** Marketplace  
**Rate limit:** 300 запр/мин (общий лимит хоста Marketplace API; 409 Conflict — 10 запросов для DBS, см. `01-rate-limits-retry.md`)  
**Версия:** /api/v3/

> Хост подтверждён per-path записями `servers:` в спеке 05-orders-dbs; корневого
> поля `servers` в спеке нет, поэтому `--list` показывает пустой список. Совпадает
> с `00-overview.md` (`Marketplace → marketplace-api.wildberries.ru`) и с путями
> семейства FBS (`11-marketplace.md`) и Самовывоз (`06-in-store-pickup`).

## Эндпоинты

<!-- AUTO:BEGIN spec=05-orders-dbs section=endpoints -->
| Метод | Путь | Назначение |
|---|---|---|
| POST | `/api/marketplace/v3/dbs/orders/b2b/info` | Информация о покупателе B2B |
| POST | `/api/marketplace/v3/dbs/orders/meta/customs-declaration` | Закрепить номера ДТ за сборочными заданиями |
| POST | `/api/marketplace/v3/dbs/orders/meta/delete` | Удалить идентификаторы маркировки сборочных заданий |
| POST | `/api/marketplace/v3/dbs/orders/meta/details` | Получить идентификаторы маркировки сборочных заданий |
| POST | `/api/marketplace/v3/dbs/orders/meta/gtin` | Закрепить GTIN за сборочными заданиями |
| POST | `/api/marketplace/v3/dbs/orders/meta/imei` | Закрепить IMEI за сборочными заданиями |
| POST | `/api/marketplace/v3/dbs/orders/meta/info` | Получить идентификаторы маркировки сборочных заданий ⚠️ deprecated |
| POST | `/api/marketplace/v3/dbs/orders/meta/sgtin` | Закрепить коды маркировки Честного знака за сборочными заданиями |
| POST | `/api/marketplace/v3/dbs/orders/meta/uin` | Закрепить УИН за сборочными заданиями |
| POST | `/api/marketplace/v3/dbs/orders/status/cancel` | Отменить сборочные задания |
| POST | `/api/marketplace/v3/dbs/orders/status/confirm` | Перевести сборочные задания на сборку |
| POST | `/api/marketplace/v3/dbs/orders/status/deliver` | Перевести сборочные задания в доставку |
| POST | `/api/marketplace/v3/dbs/orders/status/info` | Получить статусы сборочных заданий |
| POST | `/api/marketplace/v3/dbs/orders/status/receive` | Сообщить о получении заказов |
| POST | `/api/marketplace/v3/dbs/orders/status/reject` | Сообщить об отказе от заказов |
| POST | `/api/marketplace/v3/dbs/orders/stickers` | Получить стикеры для сборочных заданий с доставкой в ПВЗ |
| POST | `/api/v3/dbs/groups/info` | Получить информацию о платной доставке |
| GET | `/api/v3/dbs/orders` | Получить информацию о завершенных сборочных заданиях |
| POST | `/api/v3/dbs/orders/client` | Информация о покупателе |
| POST | `/api/v3/dbs/orders/delivery-date` | Получить дату и время доставки |
| GET | `/api/v3/dbs/orders/new` | Получить список новых сборочных заданий |
<!-- AUTO:END -->

## Ссылка на оригинал

https://dev.wildberries.ru/openapi/orders-dbs
