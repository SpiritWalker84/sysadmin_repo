# Telegram-бот для мониторинга проектов Kwork

Бот автоматически отслеживает новые задания на Kwork.ru в категориях Telegram-ботов и парсинга/скрапинга и отправляет уведомления о подходящих проектах.

## Установка

### Для Ubuntu/Linux

1. Клонируйте репозиторий:
```bash
git clone https://github.com/SpiritWalker84/sysadmin_repo.git
cd sysadmin_repo
```

2. **Установите python3-venv (обязательно!):**
```bash
sudo apt update
sudo apt install python3-venv python3-pip
```

3. Создайте виртуальное окружение (обязательно для Ubuntu 23.04+):
```bash
python3 -m venv venv
source venv/bin/activate
```

3. Установите зависимости:
```bash
pip install -r requirements.txt
```

4. Установите системные зависимости для Playwright (для Ubuntu):
```bash
sudo apt install -y libnss3 libnspr4 libatk1.0-0 libatk-bridge2.0-0 libcups2 libdrm2 libxkbcommon0 libxcomposite1 libxdamage1 libxfixes3 libxrandr2 libgbm1 libasound2 libpango-1.0-0 libatk-1.0-0 libcairo2 libgdk-pixbuf2.0-0 libgtk-3-0
```

5. Установите браузеры для Playwright:
```bash
python -m playwright install chromium
```

5. Создайте файл `.env` из примера:
```bash
cp .env.example .env
```

6. Отредактируйте `.env` и укажите ваш токен бота:
```bash
nano .env  # или используйте любой текстовый редактор
```

7. Запустите бота:
```bash
# Вариант 1: Используя скрипт (автоматически активирует venv)
chmod +x start.sh
./start.sh

# Вариант 2: Напрямую (убедитесь, что venv активирован)
source venv/bin/activate
python bot.py
```

### Для Windows

1. Клонируйте репозиторий или скачайте файлы проекта.

2. Установите зависимости:
```bash
pip install -r requirements.txt
```

3. Установите браузеры для Playwright:
```bash
py -m playwright install chromium
```

4. Создайте файл `.env` в корне проекта (скопируйте `.env.example` и заполните):
```
BOT_TOKEN=ваш_токен_бота_от_BotFather
POLL_INTERVAL=180
KEYWORDS=tg бот,тг бот,телеграм бот,telegram bot,telegram-бот,бот для telegram,парсинг,парсер,parser,parsing,скрапинг,scraping,скрапер,scraper,парс,parse,сбор данных,data extraction
```

5. Запустите бота:
```bash
py bot.py
```

**Примечание:** Бот автоматически ищет проекты по ключевым словам из `.env`, а также использует встроенную логику для поиска ботов и парсеров (даже если слова написаны по-разному).

## Получение токена бота

1. Откройте Telegram и найдите [@BotFather](https://t.me/BotFather)
2. Отправьте команду `/newbot`
3. Следуйте инструкциям для создания бота
4. Скопируйте полученный токен и вставьте в файл `.env`

## Запуск

### Linux/Ubuntu
```bash
python3 bot.py
# или используйте скрипт:
./start.sh
```

### Windows
```bash
py bot.py
# или
python bot.py
```

### Запуск в фоне (Linux)

Для запуска в фоне на сервере используйте `screen` или `tmux`:

```bash
# С screen (убедитесь, что venv активирован)
screen -S kwork_bot
source venv/bin/activate
python bot.py
# Нажмите Ctrl+A, затем D для отсоединения

# С tmux (убедитесь, что venv активирован)
tmux new -s kwork_bot
source venv/bin/activate
python bot.py
# Нажмите Ctrl+B, затем D для отсоединения
```

Или используйте systemd service (см. раздел ниже).

## Использование

1. Найдите вашего бота в Telegram по имени, которое вы указали при создании
2. Отправьте команду `/start` - бот сохранит ваш chat_id и начнёт мониторинг
3. Бот будет автоматически проверять новые проекты каждые N секунд (указано в `POLL_INTERVAL`)
4. При обнаружении новых подходящих проектов бот отправит вам уведомление

## Команды

- `/start` - Начать работу с ботом (сохраняет ваш chat_id)
- `/check` - Вручную проверить новые проекты

## Структура проекта

- `bot.py` - Основной файл с логикой бота
- `kwork_parser.py` - Модуль для парсинга страниц Kwork
- `storage.py` - Модуль для работы с локальным хранилищем (JSON)
- `.env` - Файл с конфигурацией (токен, интервал, ключевые слова)
- `requirements.txt` - Зависимости проекта

## Хранение данных

Бот сохраняет данные в JSON-файлах:
- `seen_projects.json` - ID уже обработанных проектов (чтобы не дублировать уведомления)
- `chat_id.json` - ID чата пользователя

## Настройка

Вы можете изменить следующие параметры в файле `.env`:

- `BOT_TOKEN` - Токен вашего Telegram-бота
- `POLL_INTERVAL` - Интервал проверки новых проектов в секундах (рекомендуется 120-300)
- `KEYWORDS` - Список ключевых слов для фильтрации проектов (через запятую)

## Запуск как служба (systemd) на Ubuntu

Создайте файл `/etc/systemd/system/kwork-bot.service`:

```ini
[Unit]
Description=Kwork Telegram Bot
After=network.target

[Service]
Type=simple
User=your_username
WorkingDirectory=/path/to/sysadmin_repo
ExecStart=/path/to/sysadmin_repo/venv/bin/python /path/to/sysadmin_repo/bot.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Затем:
```bash
sudo systemctl daemon-reload
sudo systemctl enable kwork-bot
sudo systemctl start kwork-bot
sudo systemctl status kwork-bot
```

## Требования

- Python 3.10 или выше
- Playwright с установленным Chromium браузером
- Доступ к интернету

## Примечания

- Бот работает асинхронно и не блокирует выполнение
- При изменении разметки сайта Kwork может потребоваться корректировка селекторов в `kwork_parser.py`
- Селекторы вынесены в константы и прокомментированы для удобства правки
- Playwright требует установки браузеров отдельно: `python3 -m playwright install chromium`

