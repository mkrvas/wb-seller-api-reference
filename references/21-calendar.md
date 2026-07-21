# Promotion Calendar API — Календарь акций

> ⚠️ **Критично устарело — требует ручной проверки** (аудит от 2026-07-21, не подтверждено по
> первоисточнику): пути `GET /api/v1/calendar`, `GET /api/v1/calendar/{id}`,
> `POST /api/v1/calendar/{id}/actions` ниже не нашлись в независимых источниках. Вероятные актуальные
> пути — все под префиксом `/api/v1/calendar/promotions/...`: `GET /api/v1/calendar/promotions`
> (список акций), `GET /api/v1/calendar/promotions/details` (детали),
> `GET /api/v1/calendar/promotions/nomenclatures` (товары для участия),
> `POST /api/v1/calendar/promotions/upload` (добавить товар в акцию). Не бери пути ниже на веру —
> сверь вживую перед интеграцией.

## Назначение

Информация о предстоящих акциях WB, добавление товаров в акции.

**Хост:** `dp-calendar-api.wildberries.ru`  
**Scope токена:** Prices & Discounts (или Promotion)  
**Rate limit:** 10 запр / 6 сек (~100 запр/мин)  
**Версия:** /api/v1/

## Эндпоинты

| Метод | Путь | Назначение | Параметры |
|---|---|---|---|
| GET | /api/v1/calendar | Календарь всех акций | — |
| GET | /api/v1/calendar/{id} | Детали акции | eventId |
| POST | /api/v1/calendar/{id}/actions | Добавить товары в акцию | eventId, товары |

## Пример

```bash
curl -X GET "https://dp-calendar-api.wildberries.ru/api/v1/calendar" \
  -H "Authorization: Bearer TOKEN"
```

## Практическое применение

Полезен для планирования участия в акциях и анализа их влияния на продажи.

## Ссылка на оригинал

https://dev.wildberries.ru/openapi/promotion-calendar
