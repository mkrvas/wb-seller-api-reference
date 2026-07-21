# Обзор: хосты, авторизация, scopes, форматы

## Базовые хосты

| Семейство | Хост | Версия API |
|---|---|---|
| Content (Контент) | `content-api.wildberries.ru` (до 30.01.2025 — `suppliers-api.wildberries.ru`, отключён) | /content/v1/, /content/v2/, /content/v3/ |
| Marketplace (Маркетплейс) | `marketplace-api.wildberries.ru` | /api/v3/ |
| Statistics (Статистика) | `statistics-api.wildberries.ru` | /api/v1/, /api/v5/ |
| **Finance (Финансы)** ⭐ | `finance-api.wildberries.ru` | /api/finance/v1/ |
| Analytics (Аналитика) | `seller-analytics-api.wildberries.ru` | /api/v1/, /api/v2/, /api/v3/ |
| Prices & Discounts | `discounts-prices-api.wildberries.ru` | /api/v1/, /api/v2/ |
| Advertising (Реклама) | `advert-api.wildberries.ru` | /adv/v1/, /adv/v2/ |
| Feedbacks & Questions | `feedbacks-api.wildberries.ru` | /api/v1/ |
| Tariffs (Тарифы) | `common-api.wildberries.ru` | /api/v2/ |
| Common (Общее) | `common-api.wildberries.ru` | /api/v1/ |
| Buyer Chat | `buyer-chat-api.wildberries.ru` | /api/v1/ |
| Returns (Возвраты) | `returns-api.wildberries.ru` | /api/v1/ |
| Documents (Документы) | `documents-api.wildberries.ru` | /api/v1/ |
| Promotion Calendar | `dp-calendar-api.wildberries.ru` | /api/v1/ |
| Supplies (Поставки) | `supplies-api.wildberries.ru` | /api/v1/ |
| Recommendations | `recommend-api.wildberries.ru` | /api/v1/ |

Все хосты работают по HTTPS.

## Авторизация

### Получение токена

1. ЛК продавца WB Partners → имя профиля → Settings (Параметры) → Access to API (Доступ к API)
2. «Создать токен» → выбрать категории доступа (scopes) → выбрать уровень (чтение / чтение+запись)
3. Скопировать токен и сохранить — показывается только один раз

### Использование

```
Authorization: Bearer <ваш_токен>
```

Токен — JWT (RFC 7519). Можно декодировать локально для проверки срока, scopes, ID продавца.

### Типы токенов

| Тип | Срок жизни | Особенности |
|---|---|---|
| Personal | 180 дней | Полный доступ к выбранным категориям |
| Service | 180 дней | Для внешних интеграций |
| Basic | 180 дней | Ограниченный набор категорий |
| Sandbox | 180 дней | Только sandbox-окружение, все категории автоматически |
| OAuth2 | Access: 12ч, Refresh: 30д | Для партнёрских сервисов |

**Важно:** После создания токена категории (scopes) изменить нельзя — нужно создавать новый.

С 30 марта 2026 WB дифференцировал rate limits по типам токенов: у Personal/Service лимиты не изменились, у Basic/Test — ниже.

## Категории токенов (Scopes)

При создании токена выбираешь, к каким API он даёт доступ:

| Категория | Что открывает | Доступ |
|---|---|---|
| Content | Карточки, медиа, характеристики, категории, теги | чтение/запись |
| Marketplace | FBS заказы, поставки, склады, остатки товара | чтение/запись |
| Statistics | Продажи, заказы, остатки WB, финансовый отчёт | только чтение |
| Analytics | NM-отчёты, воронка, платное хранение, удержания, штрафы | только чтение |
| Prices & Discounts | Цены, скидки, клубные скидки | чтение/запись |
| Promotion | Рекламные кампании, ставки, статистика рекламы, бюджеты | чтение/запись |
| Feedbacks & Questions | Отзывы, вопросы, ответы | чтение/запись |
| Recommendations | Рекомендуемые ставки | только чтение |
| Buyer Chat | Переписка с покупателями | чтение/запись |
| Supplies | Управление FBS поставками | чтение/запись |
| Returns | Возвраты товаров | чтение/запись |
| Finance | Финансовые отчёты, платежи | только чтение |
| Documents | Счета-фактуры, акты | только чтение |
| Tariffs | Тарифы, комиссии | только чтение |

**Для read-only отчётности/аналитики** обычно достаточно scopes (все — только чтение): **Finance** ⭐, Statistics, Analytics, Promotion, Content.

## Форматы данных

| Параметр | Значение |
|---|---|
| Формат | JSON (`Content-Type: application/json`) |
| Кодировка | UTF-8 |
| Формат дат | RFC3339 / ISO8601 |
| Часовой пояс | MSK (UTC+3) по умолчанию; `Z` в конце = UTC |
| HTTP методы | GET, POST, PUT, PATCH, DELETE |

### Допустимые форматы дат

```
2024-06-20T09:59              (без Z — MSK)
2024-06-20T00:00:00.123Z      (с Z — UTC)
2024-06-20T00:00:00.123       (без Z — MSK)
2024-06-20                    (только дата)
```

## Хранение токена в проекте

```env
# .env
WB_API_TOKEN=ваш_токен_здесь
```

Никогда не коммитить в git. Добавить `.env` в `.gitignore`.
