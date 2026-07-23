# Tariffs API — Тарифы

> ⚠️ **Пути подтверждены официальной спекой** (снапшот в `specs/`, авто-таблица ниже): актуальная
> версия — `/api/v1/tariffs/*` (commission/box/pallet/return) и
> `/api/tariffs/v1/acceptance/coefficients`, а не `/api/v2/`. Прежний путь `warehouse-coefficients` в
> спеке отсутствует (вероятный аналог — `acceptance/coefficients`). Непроверенными по первоисточнику
> остаются лимиты: по вторичному источнику лимит коэффициентов приёмки мог быть снижен до 6 запр/мин
> (было 60) с 27.06.2026 — проверь вживую (аудит от 2026-07-21).

## Назначение

Текущие тарифы WB: комиссии по категориям, коэффициенты складов, стоимость коробов, паллет, возвратов.

**Хост:** `common-api.wildberries.ru`  
**Scope токена:** Tariffs  
**Версия:** /api/v1/ (+ /api/tariffs/v1/acceptance/coefficients)

## Rate limits

| Эндпоинт | Лимит |
|---|---|
| /api/v1/tariffs/commission | **1 запр/мин** |
| /api/tariffs/v1/acceptance/coefficients | 60 запр/мин (по вторичному источнику мог быть снижен до 6 запр/мин с 27.06.2026 — см. примечание) |
| /api/v1/tariffs/box | 60 запр/мин |
| /api/v1/tariffs/pallet | 60 запр/мин |
| /api/v1/tariffs/return | 60 запр/мин |
| /api/v2/tariffs/warehouse-coefficients | путь из старой документации, в спеке отсутствует (вероятно заменён на acceptance/coefficients) |

## Эндпоинты

<!-- AUTO:BEGIN spec=10-rates section=endpoints -->
| Метод | Путь | Назначение |
|---|---|---|
| GET | `/api/tariffs/v1/acceptance/coefficients` | Тарифы на поставку |
| GET | `/api/v1/tariffs/box` | Тарифы для коробов |
| GET | `/api/v1/tariffs/commission` | Комиссия по категориям товаров |
| GET | `/api/v1/tariffs/pallet` | Тарифы для монопаллет |
| GET | `/api/v1/tariffs/return` | Тарифы на возврат |
<!-- AUTO:END -->

> **Примечание (факты вне авто-таблицы, сохранено из прежнего справочника):**
> - Актуальный префикс путей — `/api/v1/tariffs/*` и `/api/tariffs/v1/acceptance/coefficients`
>   (по спеке, снапшот 2026-07-22). Прежний справочник описывал их как `/api/v2/tariffs/*`, а
>   коэффициенты складов — как `/api/v2/tariffs/warehouse-coefficients`; актуальный аналог —
>   `/api/tariffs/v1/acceptance/coefficients` (тарифы на поставку/приёмку).
> - Лимиты по эндпоинтам: `tariffs/commission` — **1 запр/мин**, остальные (`box`, `pallet`,
>   `return`, коэффициенты) — 60 запр/мин (см. раздел «Rate limits» выше; по вторичному источнику
>   лимит коэффициентов приёмки мог быть снижен до 6 запр/мин с 27.06.2026 — проверь вживую).

## Пример: получить комиссии

```bash
curl -X GET "https://common-api.wildberries.ru/api/v1/tariffs/commission" \
  -H "Authorization: Bearer TOKEN"
```

Ответ:
```json
{
  "data": [
    {
      "subjectID": 1,
      "subjectName": "Электроника",
      "commission": 15,
      "commissionPercent": 15
    }
  ]
}
```

## Примечание

Комиссии дублируются в финансовом отчёте (Finance API sales-reports), так что для сверки факта Tariffs API не обязателен. Основная ценность — прогнозирование и расчёт юнит-экономики до старта продаж.

## Ссылка на оригинал

https://dev.wildberries.ru/openapi/wb-tariffs
