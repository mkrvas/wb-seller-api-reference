# Documents API — Документы

> ⚠️ **Критично устарело — требует ручной проверки** (аудит от 2026-07-21, не подтверждено по
> первоисточнику): пути `GET /api/v1/documents` и `GET /api/v1/documents/{id}` ниже не нашлись в
> актуальной OpenAPI-спеке стороннего SDK. Вероятные актуальные пути: `GET /api/v1/documents/categories`
> (категории), `GET /api/v1/documents/list` (список), `GET /api/v1/documents/download` (скачать один),
> `POST /api/v1/documents/download/all` (массовое скачивание, до 50). Rate limit тоже, вероятно,
> другой — по спеке 1 запрос/10 сек (burst 5) для Personal/Service/Basic+Secret, 1 запрос/24ч для
> Basic, а не "3 запр/30 сек" ниже. Не бери пути на веру — сверь вживую перед интеграцией.

## Назначение

Получение счетов-фактур, актов выполнения, финансовых документов от WB.

**Хост:** `documents-api.wildberries.ru`  
**Scope токена:** Documents  
**Rate limit:** 3 запр / 30 сек (~6 запр/мин)  
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
curl -X GET "https://documents-api.wildberries.ru/api/v1/documents?limit=50&offset=0" \
  -H "Authorization: Bearer TOKEN"
```

## Практическое применение

Полезен для автоматической загрузки актов и счетов в бухгалтерию/учётную систему.

## Ссылка на оригинал

https://dev.wildberries.ru/openapi/documents
