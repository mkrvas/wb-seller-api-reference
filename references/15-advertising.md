# Advertising API — Реклама

## Назначение

Получение и (частично) управление рекламными кампаниями WB. **Критично:** на 2026-05 WB Promotion API сильно урезан — большинство «классических» эндпоинтов отдают 404 (`path not found`). Это подтверждено live-проверкой 2026-05-28 в проде с реальным токеном.

**Хост:** `advert-api.wildberries.ru`
**Scope токена:** Promotion
**Rate limit:** глобальный лимит на seller (`Limited by global limiter, per seller`). Точное число WB не публикует — на практике безопасно ≤10 запросов в секунду; на 50+ можно ловить 429. С 30.03.2026 WB также дифференцирует лимиты по типу токена (Personal/Service — без изменений, Basic/Test — ниже) — это могло затронуть и Advertising, отдельно не проверялось.
**Версии:** `/adv/v1/`, `/adv/v3/`. Старая `/adv/v0/` мёртвая, `/adv/v2/` — только для `save-ad` и `fullstats`.

## Полный список эндпоинтов Promotion (авто из официальной спеки)

Канонический перечень путей из спеки `08-promotion` (без раздела «Календарь акций» — он вынесен в
[21-calendar.md](21-calendar.md)). Это **номенклатура портала**, а не гарантия работоспособности:
фактический live-статус каждого метода (что реально отвечает 200, а что 404) разобран вручную в
разделах ниже — для практики они важнее.

<!-- AUTO:BEGIN spec=08-promotion section=endpoints -->
| Метод | Путь | Назначение |
|---|---|---|
| PATCH | `/adv/v0/auction/nms` | Изменение списка карточек товаров в кампаниях |
| PUT | `/adv/v0/auction/placements` | Изменение мест размещения в кампаниях с ручной ставкой |
| GET | `/adv/v0/delete` | Удаление кампании |
| DELETE | `/adv/v0/normquery/bids` | Удалить ставки поисковых кластеров |
| POST | `/adv/v0/normquery/bids` | Установить ставки для поисковых кластеров |
| POST | `/adv/v0/normquery/get-bids` | Список ставок поисковых кластеров |
| POST | `/adv/v0/normquery/get-minus` | Список минус-фраз кампаний |
| POST | `/adv/v0/normquery/list` | Списки активных и неактивных поисковых кластеров |
| POST | `/adv/v0/normquery/set-minus` | Установка и удаление минус-фраз |
| POST | `/adv/v0/normquery/stats` | Статистика поисковых кластеров |
| GET | `/adv/v0/pause` | Пауза кампании |
| POST | `/adv/v0/rename` | Переименование кампании |
| GET | `/adv/v0/start` | Запуск кампании |
| GET | `/adv/v0/stop` | Завершение кампании |
| GET | `/adv/v1/advert` | Информация о медиакампании |
| GET | `/adv/v1/adverts` | Список медиакампаний |
| GET | `/adv/v1/balance` | Баланс |
| GET | `/adv/v1/budget` | Бюджет кампании |
| POST | `/adv/v1/budget/deposit` | Пополнение бюджета кампании |
| GET | `/adv/v1/count` | Количество медиакампаний |
| POST | `/adv/v1/normquery/stats` | Статистика по поисковым кластерам с детализацией по дням |
| GET | `/adv/v1/payments` | Получение истории пополнений счёта |
| GET | `/adv/v1/promotion/count` | Списки кампаний |
| POST | `/adv/v1/stats` | Статистика медиакампаний |
| GET | `/adv/v1/supplier/subjects` | Предметы для кампаний |
| GET | `/adv/v1/upd` | Получение истории затрат |
| POST | `/adv/v2/seacat/save-ad` | Создать кампанию |
| POST | `/adv/v2/supplier/nms` | Карточки товаров для кампаний |
| GET | `/adv/v3/fullstats` | Статистика кампаний |
| GET | `/api/advert/v0/bids/recommendations` | Рекомендуемые ставки для карточек товаров и поисковых кластеров |
| PATCH | `/api/advert/v1/bids` | Изменение ставок в кампаниях |
| POST | `/api/advert/v1/bids/min` | Минимальные ставки для карточек товаров |
| GET | `/api/advert/v1/config` | Конфигурационные значения продвижения |
| POST | `/api/advert/v1/normquery/bids` | Установить ставки для поисковых кластеров в валюте аккаунта продавца |
| GET | `/api/advert/v2/adverts` | Информация о кампаниях |
<!-- AUTO:END -->

> **Важно:** таблица выше — из спеки, НЕ проверка живости. WB держит в спеке методы, которые в проде
> отдают 404 (см. «❌ Мёртвые эндпоинты»), а рабочие управляющие методы (ставки — `PATCH /api/advert/v1/bids`,
> конфиг — `GET /api/advert/v2/adverts`) живут в новом неймспейсе `/api/advert/*`. Перед использованием
> сверяйся с live-разделами ниже.

## ✅ Живые эндпоинты (проверено live 2026-05-28)

### `GET /adv/v1/promotion/count` — список всех кампаний

Единственный источник, который даёт **полный список кампаний** юзера.

**Запрос:** `GET https://advert-api.wildberries.ru/adv/v1/promotion/count`

**Ответ:**
```json
{
  "adverts": [
    {
      "type": 9,          // тип кампании (см. ниже)
      "status": 9,        // статус (см. ниже)
      "count": 5,
      "advert_list": [
        { "advertId": 34680458, "changeTime": "2026-04-15T11:28:10+03:00" },
        ...
      ]
    },
    { "type": 8, "status": 7, "count": 286, "advert_list": [...] }
  ]
}
```

**НЕ отдаёт:** name, dailyBudget, paymentType, состав товаров.

### `GET /adv/v3/fullstats?ids=&beginDate=&endDate=` — статистика расходов

ВНИМАНИЕ: метод **GET**, а не POST. POST → 405 `method not allowed`.

**Запрос:**
```bash
curl -X GET "https://advert-api.wildberries.ru/adv/v3/fullstats?ids=27967938&beginDate=2026-02-18&endDate=2026-02-18" \
  -H "Authorization: Bearer TOKEN"
```

`ids` — до 50 advert_id через запятую.

**Ответ (важные поля):**
```json
[{
  "advertId": 27967938,
  "name": null,           // ← всегда null, WB не отдаёт имя кампании
  "type": null,
  "views": 4, "sum": 1.11,
  "days": [{
    "date": "2026-02-18T00:00:00Z",
    "views": 4, "clicks": 1, "sum": 1.11,
    "apps": [{
      "appType": 32,
      "nms": [{
        "nmId": 312118064,
        "name": "Кеды на высокой подошве бежевые",  // ← имя товара ЕСТЬ
        "views": 3, "clicks": 1, "sum": 0.81,
        "sum_price": 0, "orders": 0, "atbs": 0,
        "ctr": 33.33, "cpc": 0.81, "cr": 0
      }]
    }]
  }]
}]
```

**Ключевое:**
- `days[].date` приходит как ISO с `T00:00:00Z` — парсить `date.fromisoformat(s[:10])`.
- `nms[].sum_price` — НЕ `sum_orders` или `sumOrders` (WB переименовали ~2026-05).
- Названия **товаров** есть в `nms[].name`. Названия **кампании** — нет (null).

### Ассоциированные заказы (основной товар vs ассоциированные)

WB **НЕ** отдаёт отдельного поля «ассоциированные заказы» и отдельного
эндпоинта под эту разбивку нет. Но в `nms[]` одной кампании ассоциированные
товары (заказанные после клика по рекламе, но сами НЕ рекламируемые) приходят
**отдельными строками** и отличаются по признаку `views`:

| Строка `nm` | Что это |
|---|---|
| `views > 0` | рекламируемый (основной) товар — прямые заказы |
| `views == 0`, `orders > 0` | ассоциированный товар (другой SKU «того же кластера», заказан после клика; деньги за показ не списывались) |

Итого по кампании: основные заказы = Σ `orders` где `views>0`; ассоциированные
= Σ `orders` где `views==0`. Сумма обоих = общие `orders` кампании.

**Live-подтверждено 2026-05-29** на реальных данных (окно 90 дней): 1789 строк с
`views=0 AND orders>0`, **2547 ассоциированных заказов против 6260 основных**,
в 35 кампаниях. Признак реально работает.

⚠️ Семантика `views==0` официально WB не задокументирована (выведена из форума
dev.wildberries.ru #1474), но подтверждена на живых данных. Возможна
историческая нестабильность: в марте 2024 WB временно вообще перестал отдавать
ассоциированные через API.

## ✅ Управление и доп-методы (live-проверено 2026-06-03, personal-токен)

Дополнительная live-перепроверка расширила список живых методов:

| Метод | Путь | Назначение | Проверка |
|---|---|---|---|
| GET | `/adv/v0/pause?id=` | Пауза кампании | ✅ боевой (200, обратимо) |
| GET | `/adv/v0/start?id=` | Запуск кампании | ✅ боевой (200, статус вернулся в 9) |
| GET | `/adv/v0/stop?id=` | Остановка | по аналогии, live не дёргался |
| GET | `/adv/v1/balance` | Баланс счёта `{balance, net, currency}` | ✅ |
| GET | `/adv/v1/budget?id=` | Остаток бюджета кампании `{cash, netting, total}` | ✅ |
| POST | `/adv/v1/budget/deposit` | Пополнение бюджета (битое тело→400; GET→405 allowed POST) | ✅ путь жив, деньги не тратил |
| POST | `/adv/v0/normquery/stats` | **Статистика по ключевым фразам/кластерам.** См. отдельный раздел ниже — тело и схема пересняты live 2026-06-13 | ✅ отдаёт реальные фразы |
| POST | `/adv/v1/normquery/stats` | То же, **с разбивкой по дням** (`dailyStats`) | ✅ |
| POST | `/adv/v0/normquery/set-minus` | Минус-фразы (битое тело→400 "invalid advert id") | ✅ путь жив |
| POST | `/adv/v2/seacat/save-ad` | Создать/редактировать кампанию (нужен `nms`) | ✅ (пустое тело→400 "must provide at least one nm id") |

**`fullstats` бонус:** на активной кампании отдаёт `boosterStats:[{avg_position, date, nm}]` — средняя позиция товара в выдаче по дням.

### ✅ Статистика по ключевым фразам — `normquery/stats` (live-переснято 2026-06-13)

**КРИТИЧНО:** прежняя запись в этом скилле («тело `{advertId, from, to}`, `{stats:null}`
= нет трафика ≥100 показов») была **НЕВЕРНА**. Реальная схема снята живым токеном
на 5 активных CPC-кампаниях.

**Ключ к данным:** в `items` нужна **пара `(advertId × nmId)`** — кампания × артикул.
С телом `{"items":[{"id": advertId}], ...}` (без nmId) сервер отдаёт 200, но `null`.
Именно из-за этого раньше казалось, что метод пустой. Период **≤30 дней**
(больше → 400 `date range must not exceed 30 days`).

**v0 — агрегат за период** (ключи ответа `snake_case`):
```bash
curl -X POST "https://advert-api.wildberries.ru/adv/v0/normquery/stats" \
  -H "Authorization: Bearer TOKEN" -H "Content-Type: application/json" \
  -d '{"from":"2026-05-14","to":"2026-06-12","items":[{"advert_id":34680458,"nm_id":311586380}]}'
```
```json
{"stats":[{"advert_id":34680458,"nm_id":311586380,"stats":[
  {"norm_query":"кроссовки женские на платформе","clicks":248,"cpc":4,
   "spend":992.4,"orders":4,"shks":4,"atbs":22,"avg_pos":95.4,"currency":"RUB"}
]}]}
```

**v1 — разбивка по дням** (ключи ответа `camelCase`, для графиков динамики):
```bash
-d '{"from":"2026-06-10","to":"2026-06-12","items":[{"advertId":34680458,"nmId":311586380}]}'
```
```json
{"items":[{"advertId":34680458,"nmId":311586380,"dailyStats":[
  {"date":"2026-06-10","stat":{"normQuery":"белые кроссовки для женщин","clicks":15,
   "cpc":4,"spend":60,"orders":1,"shks":1,"atbs":1,"avgPos":183.74,"currency":"RUB"}}
]}]}
```

**Поля фразы (live):** `norm_query/normQuery`, `clicks`, `cpc` (₽, **не копейки**),
`spend` (₽), `orders`, `shks` (заказов в штуках), `atbs` (в корзину),
`avg_pos/avgPos` (средняя позиция в выдаче), `currency`.
**Полей `views`, `cpm`, `ctr` НЕТ** — CTR через этот метод невычислим.

**Подводные камни:**
- v0 принимает ключи `advert_id`/`nm_id`, v1 — `advertId`/`nmId`. Período `from`/`to` —
  на верхнем уровне тела, НЕ внутри item (иначе 400 `missing from: 0001-01-01`).
- Метод для CPC-кампаний с поисковым размещением (`placements.search=true`).
- `/adv/v0/stats/keywords` и `/adv/v1/stat/words` (старые методы из форумов 2024) —
  **404, удалены WB.** `fullstats` даёт агрегат по кампании БЕЗ разбивки по фразам.

### ✅ Управление СТАВКОЙ — `PATCH /api/advert/v1/bids` (НОВЫЙ неймспейс!)

**ВАЖНО: ставки живут в новом неймспейсе `/api/advert/v1/`, НЕ в старом `/adv/*`.**
Все `/adv/*/cpm*` пути — 404 (это тупик, не ищи там). Живой метод (live-проверено 2026-06-03,
схема выявлена эмпирически по ошибкам валидатора, реальная ставка НЕ применялась):

```
PATCH https://advert-api.wildberries.ru/api/advert/v1/bids
Content-Type: application/json
{
  "bids": [                          // массив 1..50 объектов (gt-валидация: непустой)
    {
      "advert_id": 34680458,         // ID кампании, snake_case
      "placement": "combined",       // combined (единая ставка) | search | recommendations (ручная)
      "nm_bids": [
        { "nm_id": 311586380, "bid_kopecks": 15000 }   // ставка по артикулу В КОПЕЙКАХ (>0)
      ]
    }
  ]
}
```

- Меняет ставки **по артикулам WB (nm_id)** в кампаниях: единая ставка / ручная ставка / CPC.
- Работает для статусов **4, 9, 11**.
- `GET /api/advert/v1/bids` → 405 (allowed PATCH) — чтения текущих ставок через этот путь нет.
- Прочие `/api/advert/v1/*` (count/balance/adverts/budget/fullstats) — 404, эти методы остались на
  `/adv/v1/`, `/adv/v3/`. Но неймспейс `/api/advert/*` **не ограничен только `bids`** — по независимой
  проверке (аудит 2026-07-21) там также существуют минимум `POST /api/advert/v1/bids/min` (мин. ставки),
  `POST /api/advert/v1/normquery/bids` (ставки по кластерам), `GET /api/advert/v1/config`,
  `GET /api/advert/v0/bids/recommendations` — не проверены live-токеном, но стоит попробовать.
- Rate limit неймспейса `/api/advert/*` не проверен отдельно — см. общее замечание про лимиты по типу токена ниже.
- Док: https://dev.wildberries.ru/docs/openapi/promotion/#tag/Upravlenie-kampaniyami (раздел bids).

**Урок:** WB держит ДВА неймспейса параллельно (`/adv/*` legacy + `/api/advert/v1/*` новый).
Угадывать пути нельзя — смотри актуальный Swagger dev.wildberries.ru. (Старая ошибка в этом
скилле: было написано «ставку менять нельзя» — неверно, метод просто в новом неймспейсе.)

### Запуск/стоп по времени и бюджету — в API НЕТ

Только ручные `start`/`pause`/`stop`. Расписания и автостопа по бюджету в WB API не существует —
реализуется своей обвязкой (обычно периодическая задача/scheduler: дёргает start/pause по расписанию,
бюджет мониторится через `fullstats`/`budget` + ручной `pause`).

## ❌ Мёртвые эндпоинты (404 path not found)

Проверены live 2026-05-28 — все 404. Не пытайся их дёргать.

| Эндпоинт | Метод | Статус |
|---|---|---|
| `/adv/v2/adverts` | POST (массив id / `{ids:[]}`) | 404 *(перепроверено 2026-06-03; research по форумам ошибочно считал живым — name/budget/состав НЕ достать)* |
| `/adv/v1/promotion/adverts` | GET, POST | 404 |
| `/adv/v1/promotion/adverts?status=&type=&order=&direction=` | GET, POST | 404 |
| `/adv/v1/promotion/{advertId}` | GET | 404 |
| `/adv/v1/promotion?status=&type=` | GET | 404 |
| `/adv/v2/promotion/adverts` | GET | 404 |
| `/adv/v2/promotion/{id}` | GET | 404 |
| `/adv/v2/auto/config` | GET | 404 |
| `/adv/v2/search/config` | GET | 404 |
| `/adv/v2/seacat/config` | GET | 404 |
| `/adv/v0/advert?id=` | GET | 404 |
| `/adv/v0/adverts` | GET | 404 |
| `/adv/v1/auto/config` | GET | 404 |
| `/adv/v1/search/config` | GET | 404 |
| `/adv/v1/cpm/config` | GET | 404 |
| `/adv/v1/info` | GET | 404 |
| `/adv/v1/advertiser/budget` | GET | 404 |

Сторонние библиотеки (WBSeller PHP/Python, GitHub gist'ы 2024–2025) и старые гайды описывают часть этих как живые — **это устарело**. Перед использованием подтверди live-запросом.

## ✅ Конфиг кампании — `GET /api/advert/v2/adverts` (НОВЫЙ неймспейс, live 2026-06-03)

**ВАЖНО: это `/api/advert/v2/adverts`, а НЕ старый `/adv/v2/adverts` (тот 404).** Отдаёт
имя/тип оплаты/ставки/состав — всё то, что старое API не давало. Опровергает прежнее
«название кампании получить нельзя».

**Query:** `ids=` (до 50, через запятую), `statuses=` (`-1,4,7,8,9,11`), `payment_type=` (`cpm`|`cpc`).

```json
GET https://advert-api.wildberries.ru/api/advert/v2/adverts?ids=34680458
{
  "adverts": [{
    "id": 34680458,
    "bid_type": "manual",                 // manual | unified
    "currency": "RUB",
    "status": 9,
    "settings": {
      "name": "482-2 CPC",                // ✅ ИМЯ КАМПАНИИ (раньше считалось недоступным!)
      "payment_type": "cpc",              // ✅ cpm (за показы) | cpc (за клик)
      "placements": { "search": true, "recommendations": false }
    },
    "nm_settings": [{
      "nm_id": 311586380,                 // ✅ состав кампании (артикулы)
      "bids_kopecks": { "search": 400, "recommendations": 0 },  // ✅ текущие ставки в копейках по placement
      "subject": { "id": 105, "name": "Кеды" }                  // предмет товара
    }],
    "restrictions": { "can_change_nms": true },
    "timestamps": { "created": "...", "started": "...", "updated": "...", "deleted": "..." }
  }]
}
```

**Что ТЕПЕРЬ доступно (через `/api/advert/v2/adverts`):** имя кампании, тип оплаты (cpm/cpc),
тип ставки (manual/unified), площадки (search/recommendations), состав (`nm_id`),
**текущие ставки** (`bids_kopecks` по placement), предмет, статус, таймстемпы.

**Чего по-прежнему НЕТ:** дневного бюджета (`dailyBudget`) как лимита — только остаток через
`GET /adv/v1/budget`; расписания/автостопа.

**Практическая ценность:** раньше имя кампании приходилось хранить вручную (алиас) — с этим
методом оно доступно напрямую через `settings.name`, отдельный костыль для него не нужен.
Тип оплаты cpm/cpc — тоже отсюда. Старый метод `/adv/v1/promotion/count` (только id+тип+статус)
имеет смысл дополнять этим для обогащения данных.

## Типы и статусы кампаний

| `type` | Описание |
|---|---|
| 4 | Каталог |
| 5 | Карточка товара |
| 6 | Поиск |
| 7 | Рекомендации |
| 8 | Авто *(отключён 23.10.2025, объединён в 9)* |
| 9 | Поиск+Каталог |

| `status` | Описание |
|---|---|
| -1 | Удалена |
| 4 | Готова |
| 7 | Завершена |
| 8 | Отменена |
| 9 | Активна |
| 11 | Приостановлена |

## Создание / редактирование кампании

| Метод | Путь | Назначение |
|---|---|---|
| POST | `/adv/v2/seacat/save-ad` | Создать/обновить кампанию (тип 9) |

`POST /adv/v1/save-ad` отключён 23.10.2025.

## Подводные камни

- `429 "global limiter, per seller"` ловится при бурстах. Батчить по 50 `ids` в fullstats, делать пакетные запросы с интервалом ≥100ms.
- Статистика отстаёт от реального времени на 1–2 часа.
- В `nms[].sum_price` лежит сумма заказов (а не `sum_orders`/`sumOrders` — те null). Это переименование 2026-05.
- `days[].date` всегда `T00:00:00Z` — парсить по первым 10 символам.

## Источники

- WB Release notes: https://dev.wildberries.ru/release-notes
- WB OpenAPI (требует логин): https://dev.wildberries.ru/openapi/promotion
