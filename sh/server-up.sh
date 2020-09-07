#!/bin/bash



echo "Стартуем Text-processor server..."

docker-compose -f deploy/docker-compose.yml up -d

# Если предыдущая команда выполнилась удачно печатаем приглашение.
if [ $? -eq 0 ]; then
    sh/greetings.sh
else
    echo "НЕ удалость стартовать Text-processor server."
fi
