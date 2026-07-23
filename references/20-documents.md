# Documents API — Документы

> ⚠️ **Пути подтверждены официальной спекой** (снапшот в `specs/`, авто-таблица ниже): актуальные —
> `GET /api/v1/documents/categories`, `GET /api/v1/documents/list`, `GET /api/v1/documents/download`
> (один документ), `POST /api/v1/documents/download/all` (массово, до 50). Прежние плоские
> `GET /api/v1/documents` и `GET /api/v1/documents/{id}` в спеке отсутствуют — заменены. Непроверенным
> по первоисточнику остаётся **rate limit** — он противоречив в источниках (см. шапку и примечание
> ниже). Аудит от 2026-07-21.

## Назначение

Получение счетов-фактур, актов выполнения, финансовых документов от WB.

**Хост:** `documents-api.wildberries.ru`  
**Scope токена:** Documents  
**Rate limit:** ⚠️ противоречив в источниках (3 запр/30 сек либо 1 запр/10 сек), вживую не проверен — см. примечание  
**Версия:** /api/v1/

## Эндпоинты

<!-- AUTO:BEGIN spec=13-finances section=endpoints -->
| Метод | Путь | Назначение |
|---|---|---|
| GET | `/api/v1/documents/categories` | Категории документов |
| GET | `/api/v1/documents/download` | Получить документ |
| POST | `/api/v1/documents/download/all` | Получить документы |
| GET | `/api/v1/documents/list` | Список документов |
<!-- AUTO:END -->

> **Примечание (сохранено из прежнего справочника):**
> - Эндпоинты документов приходят из спеки `13-finances` (тот же портальный раздел, что и Finance),
>   но хост — `documents-api.wildberries.ru`.
> - Спека (снапшот 2026-07-22) подтвердила актуальные пути: `GET /api/v1/documents/categories`,
>   `GET /api/v1/documents/list`, `GET /api/v1/documents/download` (один документ),
>   `POST /api/v1/documents/download/all` (массово, до 50). Прежний справочник описывал
>   `GET /api/v1/documents` и `GET /api/v1/documents/{id}` — они **заменены** путями выше.
> - Rate limit по вторичному источнику: 1 запр/10 сек (burst 5) для Personal/Service/Basic+Secret,
>   1 запр/24ч для Basic (прежняя запись «3 запр/30 сек» не подтверждена — проверь вживую).

## Пример

```bash
curl -X GET "https://documents-api.wildberries.ru/api/v1/documents/list?limit=50&offset=0" \
  -H "Authorization: Bearer TOKEN"
```

## Практическое применение

Полезен для автоматической загрузки актов и счетов в бухгалтерию/учётную систему.

## Ссылка на оригинал

https://dev.wildberries.ru/openapi/documents
