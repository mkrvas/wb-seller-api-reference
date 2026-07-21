# Content API — Контент

## Назначение

Управление карточками товаров: создание, редактирование, загрузка медиа, работа с характеристиками, категориями, тегами, справочниками (бренды, цвета, размеры).

**Хост:** `content-api.wildberries.ru` (до 30.01.2025 использовался `suppliers-api.wildberries.ru` —
отключён WB, не использовать)
**Scope токена:** Content
**Rate limit:** 100 запр/мин для Personal/Service/Basic-with-secret токенов (интервал 600мс, burst 5);
для токена уровня Basic — ниже (⚠️ точная цифра "2 запр/час" не подтверждена независимо при аудите
2026-07-21 — направление верно, число проверь вручную). Общий лимит на все Content-методы, не отдельно на upload/update.
**Версии:** /content/v1/, /content/v2/, /content/v3/

## Эндпоинты

### Карточки товаров

| Метод | Путь | Назначение | Параметры | Пагинация |
|---|---|---|---|---|
| POST | /content/v2/cards/cursor/list | Список карточек | limit, cursor, sort | cursor |
| POST | /content/v2/get/cards/list | Список карточек (альт.) | limit, offset | offset |
| GET | /content/v2/cards/error/list | Карточки с ошибками | limit, offset, type | offset |
| POST | /content/v2/cards/update | Обновить карточку | объект с полями товара | — |
| POST | /content/v2/cards/upload/add | Добавить товар к карточке | объект товара с nmID/SKU | — |
| POST | /content/v2/cards/upload | Загрузить новый товар | объект товара | — |
| POST | /content/v2/cards/delete/trash | Переместить в корзину | nmID | — |
| POST | /content/v2/cards/recover | Восстановить из корзины | nmID | — |
| POST | /content/v2/get/cards/trash | Карточки из корзины | limit, offset | offset |

### Медиа

| Метод | Путь | Назначение | Параметры |
|---|---|---|---|
| POST | /content/v3/media/file | Добавить один медиафайл (multipart, заголовки X-Nm-Id/X-Photo-Number) | file |
| POST | /content/v3/media/save | Полностью заменить список медиа карточки | nmId, data |

**`media/save`** — тело `{"nmId": <int>, "data": ["<url1>", "<url2>", ...]}`. **Заменяет весь
список медиафайлов карточки** переданным массивом — чтобы сохранить старые фото, их URL нужно
включить в тот же массив. Порядок элементов = порядок отображения в карточке, первый элемент —
обложка. Ссылки должны вести напрямую на файл, доступ без авторизации, HTTPS.
Изображения: до 30 на карточку, мин. 700×900px, макс. 32 Мб, JPG/PNG/BMP/GIF(статичный)/WebP.
Если хотя бы один файл в запросе не проходит требования — весь запрос молча не применяется, даже
при HTTP 200.

**`media/file`** — наоборот, ДОБАВЛЯЕТ один файл в конец списка (заголовок `X-Photo-Number` должен
быть больше текущего числа медиафайлов) — не подходит для замены/перестановки конкретной позиции.

Источник: OpenAPI-спека WB, синхронизированная в SDK-референс
https://eslazarev.github.io/wildberries-sdk/reference/items/post_content_v3_media_save/
(dev.wildberries.ru отдаёт 498/требует логин при прямом обращении — не перепроверено live-токеном,
перепроверить при первой реальной интеграции).

### Штрих-коды

| Метод | Путь | Назначение | Параметры |
|---|---|---|---|
| GET | /content/v2/barcodes | Генерация штрих-кодов | nmID, quantity |

### Теги

| Метод | Путь | Назначение | Параметры |
|---|---|---|---|
| GET | /content/v2/tags | Список тегов | — |
| POST | /content/v2/tag | Создать тег | name, description |
| PATCH | /content/v2/tag/{id} | Изменить тег | name, description |
| DELETE | /content/v2/tag/{id} | Удалить тег | — |
| POST | /content/v2/tag/nomenclature/link | Привязать тег к товару | nmID, tagId |

### Справочники

| Метод | Путь | Назначение | Параметры |
|---|---|---|---|
| GET | /content/v1/directory/brands | Справочник брендов | query, limit, offset |
| GET | /content/v1/directory/colors | Справочник цветов | query, limit |
| GET | /content/v1/directory/sizes | Справочник размеров | query, limit |
| GET | /content/v1/directory/collections | Справочник коллекций | — |
| GET | /content/v2/catalog | Структура каталога | — |

## Пример: получить карточки товаров

```bash
curl -X POST https://content-api.wildberries.ru/content/v2/cards/cursor/list \
  -H "Authorization: Bearer TOKEN" \
  -H "Content-Type: application/json" \
  -d '{ "limit": 100, "cursor": "" }'
```

Ответ:
```json
{
  "data": {
    "listGoods": [
      {
        "nmID": 123456,
        "vendorCode": "SKU001",
        "title": "Название товара",
        "brand": "Бренд",
        "brandID": 789,
        "description": "Описание",
        "specs": [ { "name": "Материал", "value": "Хлопок" } ]
      }
    ],
    "cursor": "eyJkYXRhIjoibmV4dF9jdXJzb3IifQ=="
  }
}
```

## Практическое применение

Основной сценарий — получить **справочник товаров** (`Предмет`, `Бренд`, `Артикул поставщика`) по nmID вместо парсинга ручных Excel-выгрузок из ЛК. Эндпоинт: `POST /content/v2/get/cards/list` или `POST /content/v2/cards/cursor/list`.

## Ссылка на оригинал

https://dev.wildberries.ru/openapi/work-with-products
