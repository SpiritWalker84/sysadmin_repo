# Чеклист для развертывания на Ubuntu

## Файлы, которые попадут в GitHub:

✅ **Исходный код:**
- `bot.py` - основной файл бота
- `kwork_parser.py` - парсер страниц Kwork
- `storage.py` - работа с хранилищем данных

✅ **Конфигурация:**
- `.env.example` - пример конфигурации (БЕЗ реальных данных)
- `requirements.txt` - зависимости Python
- `.gitignore` - исключения для Git
- `.gitattributes` - настройки Git

✅ **Документация:**
- `README.md` - основная документация
- `QUICKSTART.md` - быстрый старт
- `LICENSE` - лицензия MIT

✅ **Скрипты:**
- `start.sh` - скрипт запуска для Linux

## Файлы, которые НЕ попадут в GitHub (в .gitignore):

❌ `.env` - реальная конфигурация с токеном
❌ `seen_projects.json` - данные о обработанных проектах
❌ `chat_id.json` - ID чата пользователя
❌ `__pycache__/` - кэш Python
❌ `.ms-playwright/` - кэш Playwright

## Проверка перед коммитом:

1. ✅ Нет хардкода токенов/паролей в коде
2. ✅ `.env` исключен из Git
3. ✅ `.env.example` включен в Git (с !.env.example)
4. ✅ Все зависимости в requirements.txt
5. ✅ README содержит инструкции для Ubuntu
6. ✅ start.sh имеет права на выполнение (chmod +x)

## Команды для первого коммита:

```bash
# Инициализация репозитория
git init

# Добавление всех файлов (с учетом .gitignore)
git add .

# Проверка что будет закоммичено
git status

# Коммит
git commit -m "Initial commit: Kwork monitoring bot"

# Добавление remote
git remote add origin <your-repo-url>

# Push
git push -u origin main
```

## После клонирования на Ubuntu:

```bash
# 1. Клонировать
git clone <repository-url>
cd Bot_kwork

# 2. Создать .env
cp .env.example .env
nano .env  # Указать BOT_TOKEN

# 3. Установить зависимости
pip3 install -r requirements.txt

# 4. Установить браузеры Playwright
python3 -m playwright install chromium

# 5. Запустить
chmod +x start.sh
./start.sh
```

