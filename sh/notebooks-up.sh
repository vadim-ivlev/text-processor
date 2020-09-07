#!/bin/bash



echo "Стартуем Jupyter notebooks..."

docker-compose up -d

# Если предыдущая команда выполнилась удачно печатаем приглашение.
if [ $? -eq 0 ]; then
    sh/greetings.sh
else
    echo "НЕ удалость стартовать Jupyter notebooks."
fi
