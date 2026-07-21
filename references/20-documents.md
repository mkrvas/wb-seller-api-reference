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

| Метод | Путь | Назначение | Параметры | Пагинация |
|---|---|---|---|---|
| GET | /api/v1/documents | Список документов | limit, offset, type | offset |
| GET | /api/v1/documents/{id} | Скачать документ | documentId | — |

## Пример

```bash
curl -X GET "https://documents-api.wildberries.ru/api/v1/documents?limit=50&offset=0" \
  -H "Authorization: Bearer TOKEN"
```

## Практическое применение

Полезен для автоматической загрузки актов и счетов в бухгалтерию/учётную систему.

## Ссылка на оригинал

https://dev.wildberries.ru/openapi/documents
