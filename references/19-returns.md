# Returns API — Возвраты

> ⚠️ **Критично устарело — требует ручной проверки** (аудит от 2026-07-21, не подтверждено по
> первоисточнику, но три независимых сторонних источника сходятся): пути ниже, похоже, не
> соответствуют текущей модели API. Вероятная актуальная модель — заявки на возврат вместо
> "аналитики возвратов": `GET /api/v1/claims` (список заявок за 14 дней, ~20 запр/мин) и
> `PATCH /api/v1/claim` (решение по заявке: `approve`/`reject`/`rejectcustom` с комментарием).
> Путь `POST /api/v1/feedbacks/order/return`, указанный ниже под хостом returns-api, на самом деле
> может принадлежать хосту `feedbacks-api.wildberries.ru` (см. `16-feedbacks.md`). Не бери пути ниже
> на веру — сверь вживую перед интеграцией.

## Назначение

Управление возвратами от покупателей, отслеживание статусов возвратов.

**Хост:** `returns-api.wildberries.ru`  
**Scope токена:** Returns  
**Версия:** /api/v1/

## Эндпоинты

| Метод | Путь | Назначение | Параметры |
|---|---|---|---|
| GET | /api/v1/analytics/goods-return | Информация о возвратах | dateFrom, dateTo |
| GET | /api/v1/feedbacks/return-applications | Заявки на возврат (14 дней) | — |
| POST | /api/v1/feedbacks/order/return | Инициировать возврат из отзыва | feedbackId |

## Пример

```bash
curl -X GET "https://returns-api.wildberries.ru/api/v1/analytics/goods-return?dateFrom=2024-06-01&dateTo=2024-06-07" \
  -H "Authorization: Bearer TOKEN"
```

## Примечание

Базовые данные о возвратах уже есть в финансовом отчёте (Finance API, записи с `supplier_oper_name: "Возврат"`) — этот API нужен только для деталей самого процесса возврата (статусы, инициирование).

## Ссылка на оригинал

https://dev.wildberries.ru/openapi/returns
