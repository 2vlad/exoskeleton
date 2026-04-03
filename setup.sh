#!/bin/bash
# Настройка Exoskeleton
# Запустите один раз после клонирования: ./setup.sh

set -e

echo ""
echo "=== Exoskeleton — настройка ==="
echo ""

# --- Проверяем arc-токен ---

ARC_TOKEN_FILE="$HOME/.arc/token"
if [ ! -f "$ARC_TOKEN_FILE" ]; then
  echo "Ошибка: нет токена $ARC_TOKEN_FILE"
  echo "Выполните: arc auth"
  exit 1
fi
ARC_TOKEN=$(cat "$ARC_TOKEN_FILE")

# --- Логин ---

read -p "Логин (напр. ivpetrov): " LOGIN

# --- Подтягиваем данные из Staff API ---

echo "Запрашиваю данные из Staff..."
STAFF_RESPONSE=$(curl -s -H "Authorization: OAuth $ARC_TOKEN" \
  "https://staff-api.yandex-team.ru/v3/persons?login=${LOGIN}&_fields=login,name,department_group.name,official.position")

# Проверяем, что пользователь найден
STAFF_TOTAL=$(echo "$STAFF_RESPONSE" | python3 -c "import sys,json; print(json.load(sys.stdin).get('total',0))")
if [ "$STAFF_TOTAL" = "0" ]; then
  echo "Ошибка: логин '$LOGIN' не найден в Staff"
  exit 1
fi

# Извлекаем имя и департамент
DISPLAY_NAME=$(echo "$STAFF_RESPONSE" | python3 -c "
import sys, json
p = json.load(sys.stdin)['result'][0]
first = p['name']['first'].get('ru', p['name']['first'].get('en', ''))
last = p['name']['last'].get('ru', p['name']['last'].get('en', ''))
print(f'{first} {last}')
")
DEPARTMENT=$(echo "$STAFF_RESPONSE" | python3 -c "
import sys, json
p = json.load(sys.stdin)['result'][0]
print(p.get('department_group', {}).get('name', ''))
")
POSITION=$(echo "$STAFF_RESPONSE" | python3 -c "
import sys, json
p = json.load(sys.stdin)['result'][0]
print(p.get('official', {}).get('position', {}).get('ru', ''))
")

echo "  Имя: $DISPLAY_NAME"
echo "  Должность: $POSITION"
echo "  Департамент: $DEPARTMENT"
echo ""

EMAIL="${LOGIN}@yandex-team.ru"

# --- Команда и очереди (не в Staff) ---

read -p "Команда (напр. practicum): " TEAM
read -p "Очереди трекера через запятую (напр. PRACT,LUMI): " QUEUES_RAW

# --- Формируем YAML-списки ---

IFS=',' read -ra QUEUE_ARRAY <<< "$QUEUES_RAW"
TEAMS_YAML="[\"$TEAM\"]"
QUEUES_YAML="["
for i in "${!QUEUE_ARRAY[@]}"; do
  Q=$(echo "${QUEUE_ARRAY[$i]}" | xargs)  # trim
  if [ $i -gt 0 ]; then QUEUES_YAML+=", "; fi
  QUEUES_YAML+="\"$Q\""
done
QUEUES_YAML+="]"

# --- Записываем identities.yaml ---

cat > brain/system/identities.yaml << YAML
user:
  display_name: "$DISPLAY_NAME"
  tracker_login: "$LOGIN"
  email: "$EMAIL"
  staff_login: "$LOGIN"
  position: "$POSITION"
  department: "$DEPARTMENT"
  teams: $TEAMS_YAML
  default_queues: $QUEUES_YAML
YAML

echo ""
echo "Готово! Записано в brain/system/identities.yaml"
echo ""
echo "Следующие шаги:"
echo "  1. Откройте эту папку в VS Code с Yandex Code Assistant"
echo "  2. Заполните brain/control/role.md — ваша роль"
echo "  3. Заполните brain/control/week.md — фокус недели"
echo "  4. Запустите /tool-calibrate в агенте"
echo "  5. Попробуйте /my-work"
echo ""
