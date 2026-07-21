# Асинхронные отчёты через task_id

Некоторые эндпоинты WB работают асинхронно: создаёшь задачу → опрашиваешь статус → скачиваешь готовый файл.

## Какие эндпоинты асинхронные

| Отчёт | Create | Status | Download |
|---|---|---|---|
| **Платное хранение** | `POST /api/v1/paid_storage` | `GET /api/v1/paid_storage/tasks/{taskId}/status` | `GET /api/v1/paid_storage/tasks/{taskId}/download` |
| **Приёмка** | `POST /api/v1/acceptance_report` | `GET /api/v1/acceptance_report/tasks/{taskId}/status` | `GET /api/v1/acceptance_report/tasks/{taskId}/download` |
| **NM-отчёты** | `POST /api/v2/nm-report/downloads` | `GET /api/v2/nm-report/downloads/{taskId}` ⚠️ | `GET /api/v2/nm-report/downloads/{taskId}/file` ⚠️ |
| **Доля бренда** | `POST /api/v2/brands/report-downloads` ⚠️ | `GET /api/v2/brands/report-downloads/{taskId}` ⚠️ | `GET /api/v2/brands/report-downloads/{taskId}/file` ⚠️ |
| **Заблокированные товары** | `POST /api/v1/banned-products` ⚠️ | `GET /api/v1/banned-products/tasks/{taskId}/status` ⚠️ | `GET /api/v1/banned-products/tasks/{taskId}/download` ⚠️ |

Все на хосте `seller-analytics-api.wildberries.ru`.

> ⚠️ **Требует ручной проверки** (аудит от 2026-07-21, не подтверждено по первоисточнику):
> - **Доля бренда** и **Заблокированные товары** — по двум независимым сторонним источникам это,
>   похоже, на самом деле **синхронные `GET`-эндпоинты**, а не async task-flow: доля бренда —
>   `GET /api/v1/analytics/brand-share`, `/brand-share/brands`, `/brand-share/parent-subjects`;
>   заблокированные товары — `GET /api/v1/analytics/banned-products/blocked` и `/shadowed`.
> - **NM-отчёты** — пути статуса/скачивания могли измениться: возможно статус проверяется через
>   `GET /api/v2/nm-report/downloads` (список, без `{taskId}`), а скачивание — через
>   `GET /api/v2/nm-report/downloads/file/{downloadId}`; статусы могут быть `SUCCESS`/`FAILED`, а не
>   `done`/`failed`; retention — возможно 48 часов, а не 2. Есть также вероятный неупомянутый метод
>   `POST /api/v2/nm-report/downloads/retry`.
> - Отдельно есть сигнал о существовании **ещё одного async-отчёта — "Остатки на складах"**
>   (`warehouse_remains`): `POST /api/v1/warehouse_remains` → `GET .../tasks/{taskId}/status` →
>   `GET .../tasks/{taskId}/download`, не упомянутого в таблице выше (это не то же самое, что
>   синхронный `stocks-report/wb-warehouses` из `03-pagination.md`).

## Workflow: 3 шага

### Шаг 1. Создать задачу

```bash
curl -X POST https://seller-analytics-api.wildberries.ru/api/v1/paid_storage \
  -H "Authorization: Bearer TOKEN" \
  -H "Content-Type: application/json" \
  -d '{ "dateFrom": "2024-06-01", "dateTo": "2024-06-30" }'
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
