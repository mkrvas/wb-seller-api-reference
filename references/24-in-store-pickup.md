# In-Store Pickup — самовывоз из магазина

## Назначение

Раздел добавлен автоконвейером: таблица ниже генерируется из официальной
спеки. Рукописные заметки (лимиты, грабли) наполняются по мере боевого
использования — пока считать файл справочным, не боевым.

Модель «Самовывоз» (click-and-collect): покупатель оформляет заказ и забирает
его сам из точки продавца (магазина), минуя стандартную логистику WB. Раздел
покрывает сборочные задания и идентификаторы маркировки этой модели —
`/api/v3/click-collect/...` и `/api/marketplace/v3/click-collect/...`.
Методы можно протестировать в песочнице (`/sandbox`).

**Хост:** `marketplace-api.wildberries.ru`  
**Scope токена:** Marketplace  
**Rate limit:** 300 запр/мин (общий лимит хоста Marketplace API; стоимость 409 Conflict для этой модели в справочнике не уточнена, см. `01-rate-limits-retry.md`)  
**Версия:** /api/v3/

Хост подтверждён напрямую в спеке `06-in-store-pickup` (`servers: [{url: https://marketplace-api.wildberries.ru}]`) — совпадает с `00-overview.md`.

## Эндпоинты

<!-- AUTO:BEGIN spec=06-in-store-pickup section=endpoints -->
| Метод | Путь | Назначение |
|---|---|---|
| POST | `/api/marketplace/v3/click-collect/orders/meta/customs-declaration` | Закрепить номера ДТ за сборочными заданиями |
| POST | `/api/marketplace/v3/click-collect/orders/meta/delete` | Удалить идентификаторы маркировки сборочных заданий |
| POST | `/api/marketplace/v3/click-collect/orders/meta/details` | Получить идентификаторы маркировки сборочных заданий |
| POST | `/api/marketplace/v3/click-collect/orders/meta/gtin` | Закрепить GTIN за сборочными заданиями |
| POST | `/api/marketplace/v3/click-collect/orders/meta/imei` | Закрепить IMEI за сборочными заданиями |
| POST | `/api/marketplace/v3/click-collect/orders/meta/info` | Получить идентификаторы маркировки сборочных заданий ⚠️ deprecated |
| POST | `/api/marketplace/v3/click-collect/orders/meta/sgtin` | Закрепить коды маркировки Честного знака за сборочными заданиями |
| POST | `/api/marketplace/v3/click-collect/orders/meta/uin` | Закрепить УИН за сборочными заданиями |
| POST | `/api/marketplace/v3/click-collect/orders/status/cancel` | Отменить сборочные задания |
| POST | `/api/marketplace/v3/click-collect/orders/status/confirm` | Перевести сборочные задания на сборку |
| POST | `/api/marketplace/v3/click-collect/orders/status/info` | Получить статусы сборочных заданий |
| POST | `/api/marketplace/v3/click-collect/orders/status/prepare` | Сообщить, что сборочные задания готовы к выдаче |
| POST | `/api/marketplace/v3/click-collect/orders/status/receive` | Сообщить, что заказы приняты покупателями |
| POST | `/api/marketplace/v3/click-collect/orders/status/reject` | Сообщить об отказе от заказов |
| GET | `/api/v3/click-collect/orders` | Получить информацию о завершённых сборочных заданиях |
| POST | `/api/v3/click-collect/orders/client` | Информация о покупателе |
| POST | `/api/v3/click-collect/orders/client/identity` | Проверить, что заказ принадлежит покупателю |
| GET | `/api/v3/click-collect/orders/new` | Получить список новых сборочных заданий |
<!-- AUTO:END -->

## Ссылка на оригинал

https://dev.wildberries.ru/openapi/in-store-pickup
