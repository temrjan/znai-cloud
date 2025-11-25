#!/bin/bash
# Деплой фронтенда - выполнить с sudo
# sudo bash /home/temrjan/ai-avangard/deploy_now.sh

set -e

echo "Копирую новый билд..."
rm -rf /var/www/ai-avangard/*
cp -r /home/temrjan/ai-avangard/frontend/dist/* /var/www/ai-avangard/

echo "Устанавливаю права..."
chown -R www-data:www-data /var/www/ai-avangard
chmod -R 755 /var/www/ai-avangard

echo "Перезагружаю nginx..."
nginx -t && systemctl reload nginx

echo "Готово! Очистите кэш браузера (Ctrl+Shift+R)"
