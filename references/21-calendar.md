# Promotion Calendar API — Календарь акций

> ⚠️ **Пути подтверждены официальной спекой** (снапшот в `specs/`, авто-таблица ниже): актуальные — все
> под префиксом `/api/v1/calendar/promotions/*` (`promotions` — список акций, `/details` — детали,
> `/nomenclatures` — товары для участия, `POST /api/v1/calendar/promotions/upload` — добавить товар).
> Прежние плоские `GET /api/v1/calendar`, `GET /api/v1/calendar/{id}`,
> `POST /api/v1/calendar/{id}/actions` в спеке отсутствуют — заменены. Непроверенными по первоисточнику
> остаются поля тел запросов и лимиты (аудит от 2026-07-21).

## Назначение

Информация о предстоящих акциях WB, добавление товаров в акции.

**Хост:** `dp-calendar-api.wildberries.ru`  
**Scope токена:** Prices & Discounts (или Promotion)  
**Rate limit:** 10 запр / 6 сек (~100 запр/мин)  
**Версия:** /api/v1/

## Эндпоинты

<!-- AUTO:BEGIN spec=08-promotion section=endpoints -->
| Метод | Путь | Назначение |
|---|---|---|
| GET | `/api/v1/calendar/promotions` | Список акций |
| GET | `/api/v1/calendar/promotions/details` | Детальная информация об акциях |
| GET | `/api/v1/calendar/promotions/nomenclatures` | Список товаров для участия в акции |
| POST | `/api/v1/calendar/promotions/upload` | Добавить товар в акцию |
<!-- AUTO:END -->

> **Примечание (сохранено из прежнего справочника):**
> - Спека (снапшот 2026-07-22) подтвердила: актуальные пути — под префиксом
>   `/api/v1/calendar/promotions/*` (список акций, детали, номенклатуры для участия, добавление
>   товара). Прежний справочник описывал плоские `GET /api/v1/calendar`, `GET /api/v1/calendar/{id}`,
>   `POST /api/v1/calendar/{id}/actions` — они **заменены** новыми путями выше, не использовать.
> - Хост — `dp-calendar-api.wildberries.ru`, версия `/api/v1/`, лимит 10 запр / 6 сек (~100/мин).

## Пример

```bash
curl -X GET "https://dp-calendar-api.wildberries.ru/api/v1/calendar/promotions?startDateTime=2026-07-01T00:00:00Z&endDateTime=2026-07-31T23:59:59Z&allPromo=false" \
  -H "Authorization: Bearer TOKEN"
```

Параметры `startDateTime`, `endDateTime`, `allPromo` — обязательные (по спеке);
`allPromo=false` — только акции с товарами продавца.

## Практическое применение

Полезен для планирования участия в акциях и анализа их влияния на продажи.

## Ссылка на оригинал

https://dev.wildberries.ru/openapi/promotion-calendar
