#!/bin/bash
# Установка Playwright с зависимостями
# sudo bash /home/temrjan/ai-avangard/install_playwright.sh

set -e

echo "=== Установка зависимостей Playwright ==="

# Установка системных зависимостей
apt-get update
apt-get install -y \
    libnss3 \
    libnspr4 \
    libatk1.0-0 \
    libatk-bridge2.0-0 \
    libcups2 \
    libdrm2 \
    libxkbcommon0 \
    libxcomposite1 \
    libxdamage1 \
    libxfixes3 \
    libxrandr2 \
    libgbm1 \
    libasound2t64 \
    libpango-1.0-0 \
    libcairo2

echo "=== Установка браузера Chromium ==="
npx playwright install chromium

echo "=== Готово! ==="
echo "Перезапустите Claude Code: /exit и запустите снова"
