---
name: wb-api
description: >
  Справочник по Wildberries Seller API — базовые хосты, авторизация, rate limits, эндпоинты
  по 18 семействам (Content, Marketplace, Statistics, Finance, Analytics, Prices, Advertising,
  Feedbacks, Tariffs, Chat, Returns, Documents, Calendar, Orders DBW, Orders DBS,
  Самовывоз, WBD, Supplies FBW). Используй когда нужно
  узнать путь/параметры/лимит WB API или спроектировать интеграцию с WB.
---

# Wildberries Seller API — Справочник

Глобальный скилл-энциклопедия по WB Seller API для Claude Code.
Содержит описание всех семейств API, эндпоинты, параметры, лимиты, стратегии ретраев,
примеры запросов/ответов и подводные камни по каждому семейству.

## Когда использовать

- Нужно узнать путь, параметры или лимит конкретного эндпоинта WB API
- Проектируешь интеграцию с WB (замена ручных выгрузок из ЛК на API)
- Нужно разобраться с ошибкой 429 / retry / rate limits
- Нужно понять как работает асинхронный отчёт через task_id

## Навигация

### Общие разделы

| Файл | Содержание |
|---|---|
| [00-overview.md](references/00-overview.md) | Хосты, авторизация, scopes токена, форматы дат |
| [01-rate-limits-retry.md](references/01-rate-limits-retry.md) | Rate limits по семействам, заголовки, exponential backoff |
| [02-errors.md](references/02-errors.md) | HTTP коды, формат ошибок, типичные проблемы |
| [03-pagination.md](references/03-pagination.md) | Cursor / offset / rrdid / date-based пагинация |
| [04-async-tasks.md](references/04-async-tasks.md) | Асинхронные отчёты через task_id (create → status → download) |

### Семейства API

| Файл | Семейство | Хост |
|---|---|---|
| [10-content.md](references/10-content.md) | Content (карточки, медиа, справочники) | content-api.wildberries.ru |
| [11-marketplace.md](references/11-marketplace.md) | Marketplace (FBS заказы, поставки, остатки) | marketplace-api.wildberries.ru |
| [12-statistics.md](references/12-statistics.md) | Statistics (остатки WB, продажи, заказы; ⚠️ финотчёт deprecated) | statistics-api.wildberries.ru |
| [12a-finance.md](references/12a-finance.md) | **Finance (⭐ финотчёт daily/weekly, баланс, эквайринг) — ЗАМЕНА старого финотчёта** | finance-api.wildberries.ru |
| [13-analytics.md](references/13-analytics.md) | **Analytics (воронка, платное хранение, NM-отчёты)** | seller-analytics-api.wildberries.ru |
| [14-prices-discounts.md](references/14-prices-discounts.md) | Prices & Discounts (цены, скидки) | discounts-prices-api.wildberries.ru |
| [15-advertising.md](references/15-advertising.md) | **Advertising (кампании, история затрат)** | advert-api.wildberries.ru |
| [16-feedbacks.md](references/16-feedbacks.md) | Feedbacks & Questions (отзывы, вопросы) | feedbacks-api.wildberries.ru |
| [17-tariffs.md](references/17-tariffs.md) | Tariffs (комиссии, склады, короба) | common-api.wildberries.ru |
| [18-chat.md](references/18-chat.md) | Buyer Chat (чат с покупателями) | buyer-chat-api.wildberries.ru |
| [19-returns.md](references/19-returns.md) | Returns (возвраты) | returns-api.wildberries.ru |
| [20-documents.md](references/20-documents.md) | Documents (счета, акты) | documents-api.wildberries.ru |
| [21-calendar.md](references/21-calendar.md) | Promotion Calendar (акции) | dp-calendar-api.wildberries.ru |
| [22-orders-dbw.md](references/22-orders-dbw.md) | Orders DBW (доставка силами WB) | marketplace-api.wildberries.ru |
| [23-orders-dbs.md](references/23-orders-dbs.md) | Orders DBS (доставка продавцом) | marketplace-api.wildberries.ru |
| [24-in-store-pickup.md](references/24-in-store-pickup.md) | Самовывоз из магазина | marketplace-api.wildberries.ru |
| [25-wbd.md](references/25-wbd.md) | WBD (Wildberries Digital) — спека не скачана, зона пустая | не подтверждён |
| [26-supplies-fbw.md](references/26-supplies-fbw.md) | Supplies FBW (поставки на склады WB) | supplies-api.wildberries.ru |

## Быстрый справочник

**Авторизация:** `Authorization: Bearer <token>`

**Токен:** ЛК продавца → Настройки → Доступ к API → Создать токен (выбрать категории). Срок — 180 дней. Хранить в `.env` как `WB_API_TOKEN`.

**Форматы дат:** RFC3339 / ISO8601. Без `Z` — московское время (UTC+3). С `Z` — UTC.

**Формат данных:** JSON (application/json), UTF-8.

## Критичные правила

**Не выдумывать.** Если эндпоинта нет в reference-файле — говорить: «не найдено в справочнике, проверь https://dev.wildberries.ru».

**Для любой интеграции** обязательно читать:
- `01-rate-limits-retry.md` — лимиты и стратегия ретраев
- `02-errors.md` — обработка ошибок

**Для асинхронных отчётов** (платное хранение, NM-отчёты, приёмка) — `04-async-tasks.md`.

## Ссылки

- Портал разработчиков: https://dev.wildberries.ru/
- Swagger: https://dev.wildberries.ru/openapi
- FAQ: https://dev.wildberries.ru/faq
- Release Notes: https://dev.wildberries.ru/release-notes
- Поддержка: dev-info@rwb.ru
