#!/bin/bash
# Настройка PM Copilot Exoskeleton
# Запустите один раз после клонирования: ./setup.sh

set -e

echo ""
echo "=== PM Copilot — настройка ==="
echo ""

# --- Сбор данных ---

read -p "Ваше имя (как в Staff, напр. Иван Петров): " DISPLAY_NAME
read -p "Логин (напр. ivpetrov): " LOGIN
read -p "Рабочий email (напр. ivpetrov@yandex-team.ru): " EMAIL
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
