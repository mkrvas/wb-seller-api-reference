# Returns API — Возвраты

> ⚠️ **Файл непроверенный — актуальная модель возвратов описана в [16-feedbacks.md](16-feedbacks.md).**
> Гипотеза аудита от 2026-07-21 подтвердилась официальной спекой (снапшот в `specs/`): заявки
> покупателей на возврат — это **claims на хосте `feedbacks-api.wildberries.ru`**, а не «аналитика
> возвратов» на returns-api. Подтверждённые спекой пути — `GET /api/v1/claims` (список заявок) и
> `PATCH /api/v1/claim` (решение по заявке) — задокументированы в
> [16-feedbacks.md](16-feedbacks.md) (там же — авто-таблица из спеки). За возвратами обращайся туда.
> Остальное содержимое ЭТОГО файла (пути под хостом `returns-api.wildberries.ru`) официально не
> подтверждено, вероятно устарело — оставлено как есть, но вживую не проверялось.

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
