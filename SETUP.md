# Настройка PM Copilot Exoskeleton

Инструкция для запуска в SourceCraft Code Assistant (VS Code).

## Что понадобится

- VS Code с расширением SourceCraft Code Assistant
- Доступ к корпоративной сети Яндекса
- Файл `~/.arc/token` (стандартный Arc OAuth-токен)
- Доступ через IDM к MCP-серверам: `tracker_mcp`, `intrasearch`, `deepagent`

## Шаг 1. Клонировать репозиторий

```bash
git clone <repo-url> pm-copilot
cd pm-copilot
```

## Шаг 2. Создать виртуальное окружение

Python нужен для `mcp_proxy.py` (мост к MCP-серверам) и скриптов обработки данных.

```bash
python3 -m venv .venv
.venv/bin/pip install websockets pyyaml pydantic jsonschema
```

## Шаг 3. Получить `mcp_proxy.py`

Прокси-скрипт, который подключается к `mcp.yandex.net` по WebSocket. Попросите у владельца проекта или скопируйте из существующей настройки.

```bash
# Положить в корень проекта
cp /path/to/mcp_proxy.py ./mcp_proxy.py
```

## Шаг 4. Проверить Arc-токен

```bash
cat ~/.arc/token
# Должен вернуть OAuth-токен. Если файла нет — выполните arc auth.
```

## Шаг 5. Настроить MCP-серверы

```bash
cp .mcp.json.example .mcp.json
```

В файле прописаны три сервера Phase 1:
- **tracker_mcp** — тикеты, статусы, проекты, цели
- **intrasearch** — поиск по вики, трекеру, SO
- **deepagent** — широкий поиск внутри компании (только как кандидат, не как источник истины)

Если путь к python другой — поправьте `command` в `.mcp.json`.

## Шаг 6. Заполнить свои данные

Откройте `brain/system/identities.yaml` и впишите:

```yaml
user:
  display_name: "Имя Фамилия"
  tracker_login: "your-login"       # ваш логин в Трекере
  email: "your-login@yandex-team.ru"
  staff_login: "your-login"         # логин в Staff
  teams: ["your-team"]              # название команды
  default_queues: ["QUEUE1"]        # очереди трекера, за которыми следите
```

## Шаг 7. Заполнить контекст работы

Эти файлы читаются командой `/brief` — заполните их под себя:

- `brain/control/role.md` — ваша текущая роль
- `brain/control/quarter.md` — цели на квартал
- `brain/control/week.md` — фокус текущей недели
- `brain/control/constraints.md` — ограничения (фриз, зависимости)

## Шаг 8. Откалибровать рецепты

Откройте проект в VS Code с SourceCraft Code Assistant и выполните:

```
/tool-calibrate
```

Это протестирует MCP-инструменты с вашими данными и запишет рабочие паттерны вызовов в `brain/system/query-recipes/`. Без калибровки система работает вслепую.

## Шаг 9. Проверить

```
/my-work
```

Должен показать ваши открытые тикеты из Трекера. Если всё ок — система готова.

## Доступные команды

| Команда | Что делает |
|---------|-----------|
| `/brief` | Дневной брифинг: фокус, тикеты, риски, свежесть данных |
| `/my-work` | Синхронизировать и показать текущие задачи из Трекера |
| `/issue PM-123` | Досье на конкретный тикет (трекер + связанные доки) |
| `/remember <факт>` | Записать факт, решение или обязательство в мозг |
| `/tool-calibrate` | Проверить и откалибровать MCP-рецепты |

## Устранение проблем

**`/my-work` возвращает пустой результат:**
1. Проверьте `tracker_login` в `brain/system/identities.yaml`
2. Проверьте доступ к `tracker_mcp` через IDM
3. Перезапустите `/tool-calibrate`
4. Смотрите `brain/system/runbooks/empty-tracker-response.md`

**MCP не подключается:**
1. Проверьте `~/.arc/token` — не истёк ли
2. Проверьте что `.venv/bin/python3` существует и в нём есть `websockets`
3. Проверьте сетевое подключение к `mcp.yandex.net`

**Неизвестный человек/проект:**
1. Добавьте алиас в `brain/system/aliases.yaml`
2. Смотрите `brain/system/runbooks/entity-collision.md`
