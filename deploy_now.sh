#!/bin/bash
# Деплой фронтенда - выполнить с sudo
# sudo bash /home/temrjan/znai-cloud/deploy_now.sh

set -e

echo "Копирую новый билд..."
rm -rf /var/www/znai-cloud/*
cp -r /home/temrjan/znai-cloud/frontend/dist/* /var/www/znai-cloud/

echo "Устанавливаю права..."
chown -R www-data:www-data /var/www/znai-cloud
chmod -R 755 /var/www/znai-cloud

echo "Перезагружаю nginx..."
nginx -t && systemctl reload nginx

echo "Готово! Очистите кэш браузера (Ctrl+Shift+R)"
