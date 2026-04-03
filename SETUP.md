# Настройка Exoskeleton

## Что нужно заранее

- VS Code с расширением Yandex Code Assistant
- Токен `~/.arc/token` (стандартный Arc OAuth; если нет — выполните `arc auth`)
- Доступ через IDM к MCP-серверам: `tracker_mcp`, `intrasearch`, `deepagent`

## Установка

```bash
git clone https://github.com/2vlad/exoskeleton.git
cd exoskeleton
./setup.sh
```

Скрипт спросит:
- Логин (имя, должность и департамент подтянутся из Staff API автоматически)
- Команду
- Очереди трекера, за которыми следите

И запишет всё в `brain/system/identities.yaml`.

## После установки

1. Откройте папку `exoskeleton` в VS Code
2. Убедитесь, что в настройках YCA подключены MCP-серверы: tracker, intrasearch, deepagent
3. Запустите в агенте: `/tool-calibrate` — проверит подключение к инструментам
4. Попробуйте: `/my-work` — покажет ваши тикеты

## Опционально: заполнить контекст

Чтобы `/brief` давал полезные сводки, заполните:

- `brain/control/role.md` — ваша роль (одно предложение)
- `brain/control/week.md` — фокус текущей недели
- `brain/control/quarter.md` — цели на квартал

## Доступные команды

| Команда | Что делает |
|---------|-----------|
| `/brief` | Утренний брифинг: фокус, задачи, риски |
| `/my-work` | Синхронизировать тикеты из Трекера |
| `/issue PM-123` | Досье на тикет: статус, контекст, связанные доки |
| `/remember <факт>` | Записать решение или договорённость |
| `/tool-calibrate` | Проверить подключение к инструментам |

## Если что-то не работает

**`/my-work` пустой:** проверьте логин в `brain/system/identities.yaml` и доступ к tracker_mcp через IDM.

**MCP не подключается:** проверьте настройки MCP в Yandex Code Assistant (боковая панель → MCP).

**Незнакомое имя/проект:** добавьте алиас в `brain/system/aliases.yaml`.
