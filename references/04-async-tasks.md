# Асинхронные отчёты через task_id

Некоторые эндпоинты WB работают асинхронно: создаёшь задачу → опрашиваешь статус → скачиваешь готовый файл.

## Какие эндпоинты асинхронные

| Отчёт | Create | Status | Download |
|---|---|---|---|
| **Платное хранение** | `GET /api/v1/paid_storage` *(в старой документации был POST)* | `GET /api/v1/paid_storage/tasks/{taskId}/status` | `GET /api/v1/paid_storage/tasks/{taskId}/download` |
| **Приёмка** | `GET /api/v1/acceptance_report` *(в старой документации был POST)* | `GET /api/v1/acceptance_report/tasks/{taskId}/status` | `GET /api/v1/acceptance_report/tasks/{taskId}/download` |
| **NM-отчёты** | `POST /api/v2/nm-report/downloads` | `GET /api/v2/nm-report/downloads` (список/статус) | `GET /api/v2/nm-report/downloads/file/{downloadId}` |
| **Остатки на складах** | `GET /api/v1/warehouse_remains` | `GET /api/v1/warehouse_remains/tasks/{taskId}/status` | `GET /api/v1/warehouse_remains/tasks/{taskId}/download` |

Все на хосте `seller-analytics-api.wildberries.ru`.

> **Доля бренда** и **заблокированные товары** — это **НЕ** async task-flow, а **синхронные `GET`**:
> доля бренда — `GET /api/v1/analytics/brand-share` (+ `/brands`, `/parent-subjects`); заблокированные
> товары — `GET /api/v1/analytics/banned-products/blocked` (и `/shadowed`). Прежний справочник ошибочно
> описывал их как async — см. `13-analytics.md`.
>
> **Обновлено по спеке** (снапшот в `specs/`): пути NM-отчётов и async-семейства приведены к спеке;
> create-запросы платного хранения/приёмки/остатков — **GET** (в старой документации был POST). Прежние
> формы (async `brands/report-downloads`, `banned-products` как task-flow, статус NM по `{taskId}`) —
> см. git-историю. По NM-отчётам детали статусов/retry — в `13-analytics.md`.

## Workflow: 3 шага

### Шаг 1. Создать задачу

```bash
curl -X GET "https://seller-analytics-api.wildberries.ru/api/v1/paid_storage?dateFrom=2024-06-01&dateTo=2024-06-30" \
  -H "Authorization: Bearer TOKEN"
```

Ответ:
```json
{ "data": { "taskId": "a1b2c3d4-e5f6-7890-abcd-ef1234567890" } }
```

### Шаг 2. Опрашивать статус (polling)

```bash
curl -X GET "https://seller-analytics-api.wildberries.ru/api/v1/paid_storage/tasks/{taskId}/status" \
  -H "Authorization: Bearer TOKEN"
```

Возможные статусы:

| Статус | Значение |
|---|---|
| `queued` | В очереди, ещё не начат |
| `in_progress` | Генерируется, поле `percent` показывает прогресс |
| `done` | Готов к скачиванию |
| `failed` | Ошибка — нужно создать задачу заново |

Ответ (в процессе):
```json
{ "data": { "taskId": "...", "status": "in_progress", "percent": 45 } }
```

Ответ (готово):
```json
{ "data": { "taskId": "...", "status": "done", "percent": 100, "fileName": "paid_storage_2024-06-30.csv" } }
```

### Шаг 3. Скачать результат

```bash
curl -X GET "https://seller-analytics-api.wildberries.ru/api/v1/paid_storage/tasks/{taskId}/download" \
  -H "Authorization: Bearer TOKEN" \
  -o report.zip
```

Формат: обычно CSV в ZIP-архиве.

## Стратегия polling

```
poll_interval = 5 сек (начальный)
max_wait = 3600 сек (1 час)
elapsed = 0

while elapsed < max_wait:
    status = check_status(task_id)
    
    if status == "done":    → скачать и вернуть
    if status == "failed":  → выбросить ошибку
    
    sleep(poll_interval)
    elapsed += poll_interval
    poll_interval = min(poll_interval + 5, 60)  // постепенно увеличивать до 60 сек
```

## Ограничения

- **Готовые отчёты хранятся 2 часа** — после этого нужна новая задача
- **Данные доступны за последние 90 дней** — для старых дат отчёт может быть пустым
- **Генерация занимает 5-30 минут** — не ждать мгновенного результата
- **Задачу можно запросить в течение 48 часов** после создания
- Нельзя создать две одинаковые задачи параллельно — подождать завершения предыдущей

## Практический пример

Раньше данные по платному хранению брались из ручной Excel-выгрузки (фильтр по дате недели, группировка по nmId → сумма). API-эндпоинт (`paid_storage`) отдаёт те же данные, но нужно дождаться генерации через task_id.
