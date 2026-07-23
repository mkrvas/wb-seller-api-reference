# Feedbacks & Questions API — Отзывы и вопросы

> ⚠️ **Пути подтверждены официальной спекой** (снапшот в `specs/`); непроверенными по первоисточнику
> остаются лимиты и поля тел запросов (аудит от 2026-07-21, вторичные источники). Конкретно:
> - **Rate limit** может быть сложнее плоских «100 запр/мин» — по вторичным источникам это 3 запр/сек
>   (burst 6) для Personal/Service/Basic+Secret и 5 запр/час для Basic; вживую не проверено.
> - **Ответ на отзыв/вопрос:** `id` и текст передаются **в теле** запроса
>   (`POST/PATCH /api/v1/feedbacks/answer`, `PATCH /api/v1/questions`), а не в URL — это подтверждено
>   спекой и примечанием ниже.
> - **Срок редактирования ответа** возможно строже «60 дней»: не только срок, но и «только один раз» —
>   не подтверждено, проверь вживую.
> - **Закреплённые отзывы** (`/api/feedbacks/v1/pins/*`) — подтверждены спекой, см. авто-таблицу и
>   примечание ниже.

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
| DELETE | `/api/feedbacks/v1/pins` | Открепить отзывы |
| GET | `/api/feedbacks/v1/pins` | Список закреплённых и откреплённых отзывов |
| POST | `/api/feedbacks/v1/pins` | Закрепить отзывы |
| GET | `/api/feedbacks/v1/pins/count` | Количество закреплённых и откреплённых отзывов |
| GET | `/api/feedbacks/v1/pins/limits` | Лимиты закреплённых отзывов |
| PATCH | `/api/v1/claim` | Ответ на заявку покупателя |
| GET | `/api/v1/claims` | Заявки покупателей на возврат |
| GET | `/api/v1/feedback` | Получить отзыв по ID |
| GET | `/api/v1/feedbacks` | Список отзывов |
| PATCH | `/api/v1/feedbacks/answer` | Отредактировать ответ на отзыв |
| POST | `/api/v1/feedbacks/answer` | Ответить на отзыв |
| GET | `/api/v1/feedbacks/archive` | Список архивных отзывов |
| GET | `/api/v1/feedbacks/count` | Количество отзывов |
| GET | `/api/v1/feedbacks/count-unanswered` | Необработанные отзывы |
| POST | `/api/v1/feedbacks/order/return` | Возврат товара по ID отзыва |
| GET | `/api/v1/new-feedbacks-questions` | Непросмотренные отзывы и вопросы |
| GET | `/api/v1/question` | Получить вопрос по ID |
| GET | `/api/v1/questions` | Список вопросов |
| PATCH | `/api/v1/questions` | Работа с вопросами |
| GET | `/api/v1/questions/count` | Количество вопросов |
| GET | `/api/v1/questions/count-unanswered` | Неотвеченные вопросы |
<!-- AUTO:END -->

**Примечание:** авто-таблица выше — из спеки `09-communications`. Портал отдал полную версию
(5 → 21 путь), поэтому зона теперь покрывает **вопросы** (`/api/v1/question*`,
`new-feedbacks-questions`), **отзывы** (`/api/v1/feedback*`, включая закреплённые
`/api/feedbacks/v1/pins*`) и **заявки покупателей на возврат** (`/api/v1/claim`, `/api/v1/claims`).
**Чат с покупателями** (`/api/v1/seller/*`) — отдельное семейство, вынесен в `18-chat.md`.
См. также `19-returns.md` (старая, непроверенная модель возвратов на returns-api — вытеснена claims выше).

Уточнения из прежнего ручного справочника (спека даёт пути, но не параметры/грабли):
- Ответ на вопрос — `PATCH /api/v1/questions`, на отзыв — `POST /api/v1/feedbacks/answer`
  (редактирование ответа — `PATCH /api/v1/feedbacks/answer`). ID и текст передаются **в теле**;
  прежний справочник ошибочно указывал ID в URL (`/api/v1/questions/{id}/answer`,
  `/api/v1/feedbacks/{id}/answer`).
- Параметры списков (`GET /api/v1/questions`, `GET /api/v1/feedbacks`): `isAnswered`, `nmId`,
  `dateFrom`, `dateTo`, `limit`, `offset`; для отзывов также `hasFoto` (в `count`).
- Редактировать ответ на отзыв можно только в течение 60 дней (см. «Подводные камни»).

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
