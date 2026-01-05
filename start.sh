#!/bin/bash
# Скрипт запуска бота на Linux/Ubuntu

echo "Запуск Telegram-бота для мониторинга Kwork..."

# Проверяем наличие Python
if ! command -v python3 &> /dev/null; then
    echo "Ошибка: Python3 не установлен"
    exit 1
fi

# Проверяем наличие .env файла
if [ ! -f .env ]; then
    echo "Ошибка: файл .env не найден"
    echo "Скопируйте .env.example в .env и заполните его"
    exit 1
fi

# Проверяем установку зависимостей
if ! python3 -c "import aiogram" 2>/dev/null; then
    echo "Установка зависимостей..."
    pip3 install -r requirements.txt
fi

# Проверяем установку браузеров Playwright
if ! python3 -c "from playwright.sync_api import sync_playwright; p = sync_playwright().start(); p.chromium.executable_path" 2>/dev/null; then
    echo "Установка браузеров Playwright..."
    python3 -m playwright install chromium
fi

# Запускаем бота
echo "Запуск бота..."
python3 bot.py

