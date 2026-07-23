# Content API — Контент

## Назначение

Управление карточками товаров: создание, редактирование, загрузка медиа, работа с характеристиками, категориями, тегами, справочниками (бренды, цвета, размеры).

**Хост:** `content-api.wildberries.ru` (до 30.01.2025 использовался `suppliers-api.wildberries.ru` —
отключён WB, не использовать)
**Scope токена:** Content
**Rate limit:** 100 запр/мин для Personal/Service/Basic-with-secret токенов (интервал 600мс, burst 5);
для токена уровня Basic — ниже (⚠️ точная цифра "2 запр/час" не подтверждена независимо при аудите
2026-07-21 — направление верно, число проверь вручную). ⚠️ Источники расходятся: встречается и утверждение об общем лимите на все Content-методы, и отдельный суб-лимит 10 запр/мин на upload/update — вживую не проверено (см. `01-rate-limits-retry.md`).
**Версии:** /content/v1/, /content/v2/, /content/v3/

## Эндпоинты

<!-- AUTO:BEGIN spec=02-items section=endpoints -->
| Метод | Путь | Назначение |
|---|---|---|
| GET | `/api/content/v1/brands` | Бренды |
| POST | `/api/content/v1/recommendations/list` | Список рекомендаций в карточках товаров |
| POST | `/api/content/v1/recommendations/set` | Установить рекомендации для товаров |
| POST | `/content/v2/barcodes` | Генерация баркодов |
| POST | `/content/v2/cards/delete/trash` | Перенос карточек товаров в корзину |
| POST | `/content/v2/cards/error/list` | Список несозданных карточек товаров с ошибками |
| GET | `/content/v2/cards/limits` | Лимиты карточек товаров |
| POST | `/content/v2/cards/moveNm` | Объединение и разъединение карточек товаров |
| POST | `/content/v2/cards/recover` | Восстановление карточек товаров из корзины |
| POST | `/content/v2/cards/update` | Редактирование карточек товаров |
| POST | `/content/v2/cards/upload` | Создание карточек товаров |
| POST | `/content/v2/cards/upload/add` | Создание карточек товаров с присоединением |
| GET | `/content/v2/directory/colors` | Цвет |
| GET | `/content/v2/directory/countries` | Страна производства |
| GET | `/content/v2/directory/kinds` | Пол |
| GET | `/content/v2/directory/seasons` | Сезон |
| GET | `/content/v2/directory/tnved` | ТНВЭД-код |
| GET | `/content/v2/directory/vat` | Ставка НДС |
| POST | `/content/v2/get/cards/list` | Список карточек товаров |
| POST | `/content/v2/get/cards/trash` | Список карточек товаров в корзине |
| GET | `/content/v2/object/all` | Список предметов |
| GET | `/content/v2/object/charcs/{subjectId}` | Характеристики предмета |
| GET | `/content/v2/object/parent/all` | Родительские категории товаров |
| POST | `/content/v2/tag` | Создание ярлыка |
| POST | `/content/v2/tag/nomenclature/link` | Управление ярлыками в карточке товара |
| DELETE | `/content/v2/tag/{id}` | Удаление ярлыка |
| PATCH | `/content/v2/tag/{id}` | Изменение ярлыка |
| GET | `/content/v2/tags` | Список ярлыков |
| POST | `/content/v3/media/file` | Загрузить медиафайл |
| POST | `/content/v3/media/save` | Загрузить медиафайлы по ссылкам |
<!-- AUTO:END -->

> **Примечание — карточки: чтение и запись (сверка с обновлённым снапшотом спеки `02-items`):**
> Обновлённый снапшот покрывает и операции записи карточек — они теперь в авто-таблице выше:
> `POST /content/v2/cards/upload` (загрузить товар), `POST /content/v2/cards/upload/add`
> (добавить товар к карточке), `POST /content/v2/cards/update` (обновить),
> `POST /content/v2/cards/delete/trash` / `POST /content/v2/cards/recover` (корзина: убрать/вернуть),
> `POST /content/v2/get/cards/trash` (список корзины), `POST /content/v2/cards/moveNm` (перенос
> номенклатур между карточками), `GET /content/v2/cards/limits` (лимиты карточек).
> **Вне спеки** остаётся только `POST /content/v2/cards/cursor/list` — чтение списка карточек с
> cursor-пагинацией (`limit`, `cursor`, `sort`); используется в примере ниже.

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

Источник: официальная OpenAPI-спека WB — снапшот в
[specs/02-items.yaml](../specs/02-items.yaml) этого репозитория
(не перепроверено live-токеном — перепроверить при первой реальной интеграции).

> **Примечание — штрих-коды, теги и справочники (сохранено из прежнего справочника):**
> - **Теги** (`GET /content/v2/tags`, `POST /content/v2/tag`, `PATCH`/`DELETE /content/v2/tag/{id}`,
>   `POST /content/v2/tag/nomenclature/link`) — уже в авто-таблице выше (спека их содержит).
> - `POST /content/v2/barcodes` — генерация штрих-кодов (`nmID`, `quantity`) — теперь в авто-таблице выше.
> - Справочники, отсутствующие в авто-таблице: `GET /content/v1/directory/sizes` (размеры),
>   `GET /content/v1/directory/collections` (коллекции), `GET /content/v2/catalog` (структура каталога).
>   В спеке справочники — версии v2 (`/content/v2/directory/{colors,countries,kinds,seasons,tnved,vat}`),
>   а бренды — на `/api/content/v1/brands`; прежний справочник указывал бренды/цвета на
>   `/content/v1/directory/*` (устаревшая нотация).

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
