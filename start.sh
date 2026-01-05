#!/bin/bash
# Скрипт запуска бота на Linux/Ubuntu

echo "Запуск Telegram-бота для мониторинга Kwork..."

# Проверяем наличие Python
if ! command -v python3 &> /dev/null; then
    echo "Ошибка: Python3 не установлен"
    echo "Установите: sudo apt install python3 python3-venv python3-pip"
    exit 1
fi

# Проверяем наличие .env файла
if [ ! -f .env ]; then
    echo "Ошибка: файл .env не найден"
    echo "Скопируйте .env.example в .env и заполните его:"
    echo "  cp .env.example .env"
    echo "  nano .env"
    exit 1
fi

# Создаём виртуальное окружение, если его нет
if [ ! -d "venv" ]; then
    echo "Создание виртуального окружения..."
    python3 -m venv venv
    if [ $? -ne 0 ]; then
        echo "Ошибка: не удалось создать виртуальное окружение"
        echo "Установите python3-venv: sudo apt install python3-venv"
        exit 1
    fi
fi

# Активируем виртуальное окружение
echo "Активация виртуального окружения..."
source venv/bin/activate

# Проверяем установку зависимостей
if ! python -c "import aiogram" 2>/dev/null; then
    echo "Установка зависимостей..."
    pip install --upgrade pip
    pip install -r requirements.txt
    if [ $? -ne 0 ]; then
        echo "Ошибка при установке зависимостей"
        exit 1
    fi
fi

# Проверяем установку браузеров Playwright
if ! python -c "from playwright.sync_api import sync_playwright; p = sync_playwright().start(); p.chromium.executable_path" 2>/dev/null; then
    echo "Установка браузеров Playwright..."
    python -m playwright install chromium
    if [ $? -ne 0 ]; then
        echo "Ошибка при установке браузеров Playwright"
        exit 1
    fi
fi

# Запускаем бота
echo "Запуск бота..."
python bot.py


