# Feedbacks & Questions API — Отзывы и вопросы

> ⚠️ **Требует ручной проверки** (аудит от 2026-07-21, вторичные источники): rate limit, похоже,
> устроен сложнее, чем плоские "100 запр/мин" — по спеке стороннего SDK это 3 запр/сек (burst 6) для
> Personal/Service/Basic+Secret и 5 запр/час для Basic. Пути ответа на отзыв/вопрос могли поменять
> структуру — возможно `id` передаётся в теле запроса (`POST/PATCH /api/v1/feedbacks/answer`,
> `PATCH /api/v1/questions`), а не в URL, как ниже. Правило редактирования ответа возможно строже —
> не только "60 дней", но и "только один раз". Также могла появиться отдельная платная фича
> "закреплённые отзывы" (`/api/feedbacks/v1/pins/*`), не описанная здесь. Не подтверждено по
> первоисточнику — проверь вживую.

## Назначение

Получение и управление отзывами и вопросами покупателей, ответы на них.

**Хост:** `feedbacks-api.wildberries.ru`  
**Scope токена:** Feedbacks & Questions  
**Rate limit:** 100 запр/мин  
**Версия:** /api/v1/

## Эндпоинты

<!-- AUTO:BEGIN spec=09-communications section=endpoints -->
| Метод | Путь | Назначение |
|---|---|---|
| GET | `/api/v1/new-feedbacks-questions` | Непросмотренные отзывы и вопросы |
| GET | `/api/v1/question` | Получить вопрос по ID |
| GET | `/api/v1/questions` | Список вопросов |
| PATCH | `/api/v1/questions` | Работа с вопросами |
| GET | `/api/v1/questions/count` | Количество вопросов |
| GET | `/api/v1/questions/count-unanswered` | Неотвеченные вопросы |
<!-- AUTO:END -->

**Примечание:** авто-таблица выше — из спеки `09-communications`, которая покрывает только
**вопросы** (`/api/v1/question*`) и общий счётчик новых (`new-feedbacks-questions`). Эндпоинты
**отзывов** (`/api/v1/feedbacks/*`) в спеку НЕ входят и сохранены ниже вручную из прежнего
справочника (проверь вживую — пути и структура ответа могли измениться, см. предупреждение вверху файла).

Прежний справочник описывал ответ на вопрос как `POST /api/v1/questions/{id}/answer`; в спеке —
`PATCH /api/v1/questions` (ID вопроса и текст ответа передаются **в теле**). Параметры списка
вопросов (`GET /api/v1/questions`): `isAnswered`, `nmId`, `dateFrom`, `dateTo`, `limit`, `offset`.

### Отзывы (вне спеки — ручной справочник)

| Метод | Путь | Назначение | Параметры |
|---|---|---|---|
| GET | /api/v1/feedbacks/count | Количество отзывов | hasFoto |
| GET | /api/v1/feedbacks/count-unanswered | Неотвеченные отзывы | — |
| GET | /api/v1/feedbacks | Список отзывов | isAnswered, nmId, dateFrom, dateTo, limit, offset |
| POST | /api/v1/feedbacks/{id}/answer | Ответить на отзыв | feedbackId, text |
| PATCH | /api/v1/feedbacks/{id}/answer | Редактировать ответ (макс 60 дней) | feedbackId, text |
| POST | /api/v1/feedbacks/order/return | Запросить возврат по отзыву | feedbackId |

## Пример: получить неотвеченные отзывы

```bash
curl -X GET "https://feedbacks-api.wildberries.ru/api/v1/feedbacks?isAnswered=false&limit=50&offset=0" \
  -H "Authorization: Bearer TOKEN"
```

Ответ:
```json
{
  "data": [
    {
      "id": 567890,
      "nmID": 123456,
      "userName": "Покупатель",
      "text": "Отличный товар!",
      "rating": 5,
      "isAnswered": false,
      "createdAt": "2024-06-20T10:30:00Z",
      "hasFoto": false
    }
  ]
}
```

## Подводные камни

- Ответ на отзыв можно редактировать только в течение 60 дней
- Пагинация: offset/limit

## Ссылка на оригинал

https://dev.wildberries.ru/openapi/user-communication
