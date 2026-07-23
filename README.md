# wb-seller-api-reference

Неофициальный справочник по [Wildberries Seller API](https://dev.wildberries.ru/) в формате [Claude Code Skill](https://docs.claude.com/en/docs/claude-code/skills) — 5 файлов с общей инфраструктурой (авторизация, rate limits, ошибки, пагинация, асинхронные отчёты) + 18 файлов по семействам API (Content, Marketplace, Statistics, Finance, Analytics, Prices & Discounts, Advertising, Feedbacks, Tariffs, Chat, Returns, Documents, Calendar, Orders DBW, Orders DBS, Самовывоз, WBD, Supplies FBW) с эндпоинтами, параметрами, лимитами и типичными граблями.

## Что это такое

Это не код и не SDK — это структурированная markdown-документация, которую [Claude Code](https://claude.com/claude-code) подгружает себе в контекст по запросу, чтобы отвечать на вопросы про WB API или помогать проектировать интеграцию, не выдумывая пути и параметры эндпоинтов.

Формат "Skill" — папка с файлом `SKILL.md` (описание + триггеры + навигация) и подпапкой `references/` с детальными файлами, которые подгружаются по необходимости, а не все разом.

## Установка

Скопируйте эту папку в `~/.claude/skills/`:

```bash
git clone https://github.com/mkrvas/wb-seller-api-reference.git ~/.claude/skills/wb-api
```

Claude Code подхватит скилл автоматически — он сработает, когда вы спросите про путь/параметры/лимит конкретного эндпоинта WB API или попросите спроектировать интеграцию с Wildberries.

## Структура

| Файл | Содержание |
|---|---|
| [SKILL.md](SKILL.md) | Точка входа: когда использовать, навигация, быстрый справочник |
| [00-overview.md](references/00-overview.md) | Хосты, авторизация, scopes токена, форматы дат |
| [01-rate-limits-retry.md](references/01-rate-limits-retry.md) | Rate limits по семействам, exponential backoff |
| [02-errors.md](references/02-errors.md) | HTTP коды, формат ошибок, типичные проблемы |
| [03-pagination.md](references/03-pagination.md) | Cursor / offset / rrdid / date-based пагинация |
| [04-async-tasks.md](references/04-async-tasks.md) | Асинхронные отчёты через task_id |
| [10-content.md](references/10-content.md) | Content — карточки, медиа, справочники |
| [11-marketplace.md](references/11-marketplace.md) | Marketplace — FBS заказы, поставки, остатки |
| [12-statistics.md](references/12-statistics.md) | Statistics — остатки WB, продажи, заказы |
| [12a-finance.md](references/12a-finance.md) | Finance — финотчёты daily/weekly, баланс, эквайринг |
| [13-analytics.md](references/13-analytics.md) | Analytics — воронка продаж, платное хранение, NM-отчёты |
| [14-prices-discounts.md](references/14-prices-discounts.md) | Prices & Discounts — цены, скидки |
| [15-advertising.md](references/15-advertising.md) | Advertising — рекламные кампании |
| [16-feedbacks.md](references/16-feedbacks.md) | Feedbacks & Questions — отзывы, вопросы |
| [17-tariffs.md](references/17-tariffs.md) | Tariffs — комиссии, склады, короба |
| [18-chat.md](references/18-chat.md) | Buyer Chat — чат с покупателями |
| [19-returns.md](references/19-returns.md) | Returns — возвраты |
| [20-documents.md](references/20-documents.md) | Documents — счета, акты |
| [21-calendar.md](references/21-calendar.md) | Promotion Calendar — акции |
| [22-orders-dbw.md](references/22-orders-dbw.md) | Orders DBW — заказы с доставкой силами WB |
| [23-orders-dbs.md](references/23-orders-dbs.md) | Orders DBS — заказы с доставкой продавцом |
| [24-in-store-pickup.md](references/24-in-store-pickup.md) | In-Store Pickup — самовывоз из магазина |
| [25-wbd.md](references/25-wbd.md) | WBD (Wildberries Digital) — спека не скачана, зона пустая |
| [26-supplies-fbw.md](references/26-supplies-fbw.md) | Supplies FBW — поставки на склады WB |

## Автообновление

Таблицы эндпоинтов между маркерами `<!-- AUTO:BEGIN ... -->` / `<!-- AUTO:END -->`
генерируются из официальных OpenAPI-спек `dev.wildberries.ru` (снапшот — в
[specs/](specs/)). GitHub Actions ежедневно скачивает свежие спеки и, если WB
что-то поменял, открывает PR с перегенерированными таблицами и списком
изменений — мерж делает человек. Рукописные заметки (лимиты, грабли, даты
отключений) живут вне маркеров, генератор их не касается.

Обновить локальную копию скилла: `git pull` в папке скилла.

## Уровень детализации

Файлы неравномерны по глубине, и это осознанно:

- **Боевые** (Finance, Advertising, Statistics, Analytics) — содержат факты, проверенные живыми запросами с реальным токеном: реальные ответы API, эндпоинты, которые официальная документация не описывает или описывает неточно, конкретные даты изменений и deprecation.
- **Справочные** (Chat, Returns, Documents, Calendar, Feedbacks, Tariffs, Prices, Content, Marketplace, Orders DBW, Orders DBS, Самовывоз, WBD, Supplies FBW) — конспект официальной документации: пути, методы, параметры, без live-тестирования каждой мелочи. WBD — особый случай: спека не скачана (см. «Автообновление»), файл пока пуст.

Ориентируйтесь на это при выборе, насколько слепо доверять конкретному файлу.

**Аудит от 2026-07-21:** перед публикацией все файлы прогнаны через сверку со сторонними источниками (официальный `dev.wildberries.ru` на момент проверки блокировал автоматический доступ). Места с неподтверждённой или противоречивой информацией помечены прямо в тексте блоком `⚠️ Требует ручной проверки` — особенно внимательно отнеситесь к `18-chat.md`, `19-returns.md`, `20-documents.md`, `21-calendar.md`: есть сигналы, что описанные там пути устарели.

## ⚠️ Дисклеймер

Это **неофициальный community-справочник**, не аффилированный с Wildberries. WB меняет API часто и без объявления — файлы могут отставать от реальности. Перед использованием в продакшене **всегда сверяйтесь с официальными источниками**:

- Портал разработчиков: https://dev.wildberries.ru/
- Swagger/OpenAPI: https://dev.wildberries.ru/openapi
- Release Notes: https://dev.wildberries.ru/release-notes

Баги и устаревшие данные — через Issues/PR.

## Лицензия

[MIT](LICENSE)
