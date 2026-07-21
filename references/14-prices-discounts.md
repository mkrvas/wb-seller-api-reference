# Prices & Discounts API — Цены и скидки

> ⚠️ **Требует ручной проверки** (аудит от 2026-07-21): по двум независимым сторонним источникам
> (не первоисточник — dev.wildberries.ru блокирует автоматическую проверку) пути ниже могли устареть
> ещё в 2023-2024 годах. Возможные актуальные пути: `POST /api/v2/upload/task` (единая установка
> цены+скидки, тело `{"data": [{nmID, price, discount}]}` — обёртка `data`, а не `prices`),
> `POST /api/v2/upload/task/size` (цены по размерам), `POST /api/v2/upload/task/club-discount`
> (клубные скидки, отдельно от общего запроса), чтение — `GET /api/v2/list/goods/filter`.
> Проверь вживую перед использованием — расхождение может быть серьёзным, не мелкой правкой.

## Назначение

Управление ценами товаров, установка скидок, клубные скидки WB.

**Хост:** `discounts-prices-api.wildberries.ru`  
**Scope токена:** Prices & Discounts  
**Rate limit:** 10 запр / 6 сек (~100 запр/мин)  
**Версии:** /api/v1/, /api/v2/

## Эндпоинты

| Метод | Путь | Назначение | Параметры |
|---|---|---|---|
| POST | /api/v2/prices | Получить текущие цены | nmIds (массив) |
| POST | /api/v2/prices/update | Обновить цены | массив { nmID, price, discount } |
| POST | /api/v2/discounts | Получить текущие скидки | nmIds |
| POST | /api/v2/discounts/edit | Изменить скидки | nmID, discount_percent |
| POST | /api/v1/wildberries-discounts | Управление клубными скидками | nmID, clubDiscount |

## Пример: изменить цену

```bash
curl -X POST https://discounts-prices-api.wildberries.ru/api/v2/prices/update \
  -H "Authorization: Bearer TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "prices": [
      {
        "nmID": 123456,
        "price": 2999.00,
        "discount": 15
      }
    ]
  }'
```

### Поля

| Поле | Обязат. | Описание |
|---|---|---|
| `nmID` | да | ID товара |
| `price` | да | Цена без скидки |
| `discount` | нет | Процент скидки (0-99) |
| `discountedPrice` | нет | Цена со скидкой |
| `clubDiscount` | нет | Скидка для клуба WB |

**Важно:** Передавать либо `discount`, либо `discountedPrice` — не оба одновременно.

## Пример: получить текущие цены

```bash
curl -X POST https://discounts-prices-api.wildberries.ru/api/v2/prices \
  -H "Authorization: Bearer TOKEN" \
  -H "Content-Type: application/json" \
  -d '{ "nmIds": [123456, 789012] }'
```

## Примечание

В Prices API нет поля **«оборачиваемость»** — вручную её обычно берут из «Шаблон обновления цен и скидок*.xlsx» в ЛК; через API придётся считать самостоятельно из данных остатков (`stocks`) и отчёта о продажах (Finance API sales-reports).

## Ссылка на оригинал

https://dev.wildberries.ru/openapi/prices-discounts
