# Быстрый старт

## Ubuntu/Linux

```bash
# 1. Клонируйте репозиторий
git clone <repository-url>
cd Bot_kwork

# 2. Установите зависимости
pip3 install -r requirements.txt

# 3. Установите браузеры Playwright
python3 -m playwright install chromium

# 4. Создайте .env файл
cp .env.example .env
nano .env  # Укажите BOT_TOKEN

# 5. Запустите бота
python3 bot.py
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

