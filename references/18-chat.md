# Buyer Chat API — Чат с покупателями

> ⚠️ **Критично устарело — требует ручной проверки** (аудит от 2026-07-21, не подтверждено по
> первоисточнику, но независимые сторонние источники сходятся): API мог быть переработан. Вероятная
> актуальная модель: единая лента событий `GET /api/v1/seller/events` вместо
> `GET /api/v1/seller/chats/{id}/messages`; отправка — `POST /api/v1/seller/message`, а не
> `.../chats/send-message`; скачивание файла — `GET /api/v1/seller/download/{id}`, а не
> `.../chats/{id}/file/{fileId}`. Rate limit тоже не указан ниже — по стороннему источнику
> ~10 запр/10 сек. Файл ниже описывает, вероятно, устаревшую 4-эндпоинтную структуру — не доверяй
> путям без проверки живым токеном.

## Назначение

Переписка с покупателями: отправка сообщений, получение истории, файлы.

**Хост:** `buyer-chat-api.wildberries.ru`  
**Scope токена:** Buyer Chat  
**Версия:** /api/v1/

## Эндпоинты

| Метод | Путь | Назначение | Параметры |
|---|---|---|---|
| POST | /api/v1/seller/chats/send-message | Отправить сообщение | chatId, text, fileId |
| GET | /api/v1/seller/chats | Список чатов | offset, limit |
| GET | /api/v1/seller/chats/{id}/messages | История сообщений | chatId, offset, limit |
| GET | /api/v1/seller/chats/{id}/file/{fileId} | Скачать файл | chatId, fileId |

## Пример: получить список чатов

```bash
curl -X GET "https://buyer-chat-api.wildberries.ru/api/v1/seller/chats?limit=20&offset=0" \
  -H "Authorization: Bearer TOKEN"
```

## Ссылка на оригинал

https://dev.wildberries.ru/openapi/user-communication
