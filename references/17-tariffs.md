# Tariffs API — Тарифы

> ⚠️ **Требует ручной проверки** (аудит от 2026-07-21, вторичные источники): версия путей ниже может
> быть `/api/v1/`, а не `/api/v2/`, для commission/box/pallet/return. Путь `warehouse-coefficients`
> тоже под вопросом — возможный аналог `/api/tariffs/v1/acceptance/coefficients` с лимитом, сниженным
> до 6 запр/мин (было 60) с 27.06.2026. Не подтверждено по первоисточнику — проверь вживую.

## Назначение

Текущие тарифы WB: комиссии по категориям, коэффициенты складов, стоимость коробов, паллет, возвратов.

**Хост:** `common-api.wildberries.ru`  
**Scope токена:** Tariffs  
**Версия:** /api/v2/

## Rate limits

| Эндпоинт | Лимит |
|---|---|
| /api/v2/tariffs/commission | **1 запр/мин** |
| /api/v2/tariffs/warehouse-coefficients | 60 запр/мин |
| /api/v2/tariffs/box | 60 запр/мин |
| /api/v2/tariffs/pallet | 60 запр/мин |
| /api/v2/tariffs/return | 60 запр/мин |

## Эндпоинты

| Метод | Путь | Назначение | Лимит |
|---|---|---|---|
| GET | /api/v2/tariffs/commission | Комиссии по категориям | 1/мин |
| GET | /api/v2/tariffs/warehouse-coefficients | Коэффициенты складов | 60/мин |
| GET | /api/v2/tariffs/box | Тариф на коробки | 60/мин |
| GET | /api/v2/tariffs/pallet | Тариф на паллеты | 60/мин |
| GET | /api/v2/tariffs/return | Тариф на возвраты | 60/мин |

## Пример: получить комиссии

```bash
curl -X GET "https://common-api.wildberries.ru/api/v2/tariffs/commission" \
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
