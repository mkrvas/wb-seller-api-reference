# Buyer Chat API — Чат с покупателями

> ⚠️ **Пути подтверждены официальной спекой** (снапшот в `specs/`): модель чата действительно
> обновлена — вместо старой 4-эндпоинтной структуры теперь единая лента событий
> `GET /api/v1/seller/events`, отправка `POST /api/v1/seller/message`, скачивание файла
> `GET /api/v1/seller/download/{id}` (соответствие старых путей новым — в таблице ниже). Непроверенным
> по первоисточнику остаётся **rate limit**: по вторичным источникам ~10 запр/10 сек, в спеке не
> указан — проверь вживую (аудит от 2026-07-21).

## Назначение

Переписка с покупателями: отправка сообщений, получение истории, файлы.

**Хост:** `buyer-chat-api.wildberries.ru`  
**Scope токена:** Buyer Chat  
**Версия:** /api/v1/

## Эндпоинты

Актуальные пути — из официальной спеки `09-communications` (снапшот с портала; проверь вживую):

<!-- AUTO:BEGIN spec=09-communications section=endpoints -->
| Метод | Путь | Назначение |
|---|---|---|
| GET | `/api/v1/seller/chats` | Список чатов |
| GET | `/api/v1/seller/download/{id}` | Получить файл из сообщения |
| GET | `/api/v1/seller/events` | События чатов |
| POST | `/api/v1/seller/message` | Отправить сообщение |
<!-- AUTO:END -->

### Ранее документированные вручную пути (аудит 2026-07-21)

Официальная спека подтвердила обновление модели чата (см. бокс вверху файла).
Соответствие старых путей новым:

| Было (ручной справочник) | Стало (спека 09-communications) |
|---|---|
| `POST /api/v1/seller/chats/send-message` (chatId, text, fileId) | `POST /api/v1/seller/message` |
| `GET /api/v1/seller/chats/{id}/messages` (chatId, offset, limit) | `GET /api/v1/seller/events` (единая лента событий) |
| `GET /api/v1/seller/chats/{id}/file/{fileId}` (chatId, fileId) | `GET /api/v1/seller/download/{id}` |
| `GET /api/v1/seller/chats` (offset, limit) | `GET /api/v1/seller/chats` (без изменений) |

## Пример: получить список чатов

```bash
curl -X GET "https://buyer-chat-api.wildberries.ru/api/v1/seller/chats?limit=20&offset=0" \
  -H "Authorization: Bearer TOKEN"
```

## Ссылка на оригинал

https://dev.wildberries.ru/openapi/user-communication
