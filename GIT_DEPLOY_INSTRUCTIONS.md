# Инструкция по выгрузке на GitHub

## Репозиторий: https://github.com/SpiritWalker84/sysadmin_repo

### Вариант 1: Если Git установлен, но не в PATH

1. Найдите путь к Git (обычно):
   - `C:\Program Files\Git\bin\git.exe`
   - `C:\Program Files (x86)\Git\bin\git.exe`
   - `%LOCALAPPDATA%\Programs\Git\bin\git.exe`

2. Используйте полный путь к git или добавьте в PATH

### Вариант 2: Выполните команды вручную

Откройте командную строку или PowerShell в папке проекта и выполните:

```bash
# 1. Инициализация (если еще не сделано)
git init

# 2. Добавление всех файлов
git add .

# 3. Проверка что будет закоммичено (ВАЖНО!)
git status

# Убедитесь, что НЕТ в списке:
#   - .env (реальный файл)
#   - seen_projects.json
#   - chat_id.json
# 
# Должны быть:
#   - .env.example
#   - Все .py файлы
#   - README.md, requirements.txt и т.д.

# 4. Коммит
git commit -m "Add Kwork monitoring Telegram bot

- Telegram bot for monitoring Kwork projects
- Supports bots and parsing/scraping projects
- Uses Playwright for JavaScript rendering
- Ready for Ubuntu deployment"

# 5. Настройка remote
git remote add origin https://github.com/SpiritWalker84/sysadmin_repo.git
# Или если remote уже существует:
git remote set-url origin https://github.com/SpiritWalker84/sysadmin_repo.git

# 6. Создание ветки main (если нужно)
git branch -M main

# 7. Выгрузка на GitHub
git push -u origin main
```

### Вариант 3: Использование GitHub Desktop

1. Установите GitHub Desktop: https://desktop.github.com/
2. Откройте GitHub Desktop
3. File → Add Local Repository
4. Выберите папку `C:\projects\Bot_kwork`
5. Нажмите "Publish repository"
6. Выберите репозиторий `sysadmin_repo`

### Вариант 4: Через веб-интерфейс GitHub

1. Откройте https://github.com/SpiritWalker84/sysadmin_repo
2. Нажмите "uploading an existing file"
3. Перетащите файлы (кроме .env, seen_projects.json, chat_id.json)
4. Добавьте commit message
5. Commit changes

## Важные файлы для выгрузки:

✅ **Должны быть:**
- bot.py
- kwork_parser.py
- storage.py
- requirements.txt
- README.md
- QUICKSTART.md
- LICENSE
- .env.example
- .gitignore
- .gitattributes
- start.sh
- DEPLOYMENT_CHECKLIST.md
- FILES_TO_COMMIT.md

❌ **НЕ должны быть:**
- .env (реальный файл с токеном)
- seen_projects.json
- chat_id.json
- __pycache__/
- .ms-playwright/

## После выгрузки на Ubuntu:

```bash
git clone https://github.com/SpiritWalker84/sysadmin_repo.git
cd sysadmin_repo
cp .env.example .env
nano .env  # Указать BOT_TOKEN
pip3 install -r requirements.txt
python3 -m playwright install chromium
chmod +x start.sh
./start.sh
```

