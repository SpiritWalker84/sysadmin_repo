# Быстрый старт

## Ubuntu/Linux

```bash
# 1. Клонируйте репозиторий
git clone https://github.com/SpiritWalker84/sysadmin_repo.git
cd sysadmin_repo

# 2. Установите python3-venv (ОБЯЗАТЕЛЬНО!)
sudo apt update
sudo apt install python3-venv python3-pip
# Для Python 3.12: sudo apt install python3.12-venv

# 3. Создайте виртуальное окружение (обязательно для Ubuntu 23.04+)
python3 -m venv venv
source venv/bin/activate

# 4. Установите зависимости
pip install -r requirements.txt

# 5. Установите системные зависимости для Playwright (ОБЯЗАТЕЛЬНО!)
python -m playwright install-deps chromium

# 6. Установите браузеры Playwright
python -m playwright install chromium

# 7. Создайте .env файл
cp .env.example .env
nano .env  # Укажите BOT_TOKEN

# 8. Запустите бота
# Вариант 1: Используя скрипт (автоматически создаст и активирует venv)
chmod +x start.sh
./start.sh

# Вариант 2: Напрямую (убедитесь, что venv активирован)
source venv/bin/activate
python bot.py
```

## Windows

```bash
# 1. Клонируйте репозиторий
git clone <repository-url>
cd Bot_kwork

# 2. Установите зависимости
pip install -r requirements.txt

# 3. Установите браузеры Playwright
py -m playwright install chromium

# 4. Создайте .env файл (скопируйте .env.example)

# 5. Запустите бота
py bot.py
```

## Первый запуск

1. Запустите бота
2. Найдите вашего бота в Telegram
3. Отправьте команду `/start`
4. Бот начнёт мониторинг проектов автоматически

## Проверка работы

После запуска в консоли вы увидите:
- "Бот запущен..."
- "Интервал опроса: 180 секунд"
- "Следующая проверка в HH:MM:SS"

Если всё работает, бот будет проверять новые проекты каждые 3 минуты.

