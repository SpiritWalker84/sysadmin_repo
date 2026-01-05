# Скрипт для выгрузки проекта на GitHub
# https://github.com/SpiritWalker84/sysadmin_repo

Write-Host "=== Подготовка к выгрузке на GitHub ===" -ForegroundColor Green

# Проверяем наличие git
if (-not (Get-Command git -ErrorAction SilentlyContinue)) {
    Write-Host "Ошибка: Git не установлен!" -ForegroundColor Red
    Write-Host "Установите Git с https://git-scm.com/download/win" -ForegroundColor Yellow
    exit 1
}

# Инициализация git репозитория (если еще не инициализирован)
if (-not (Test-Path .git)) {
    Write-Host "Инициализация git репозитория..." -ForegroundColor Yellow
    git init
    if ($LASTEXITCODE -ne 0) {
        Write-Host "Ошибка при инициализации git!" -ForegroundColor Red
        exit 1
    }
}

# Проверяем, что .env не будет закоммичен
Write-Host "`nПроверка .gitignore..." -ForegroundColor Yellow
if (Test-Path .env) {
    $gitStatus = git check-ignore .env 2>&1
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✓ .env правильно исключен из Git" -ForegroundColor Green
    } else {
        Write-Host "⚠ ВНИМАНИЕ: .env может попасть в репозиторий!" -ForegroundColor Red
        Write-Host "Проверьте .gitignore" -ForegroundColor Yellow
    }
}

# Добавляем все файлы
Write-Host "`nДобавление файлов в git..." -ForegroundColor Yellow
git add .

# Показываем статус
Write-Host "`nСтатус файлов для коммита:" -ForegroundColor Yellow
git status --short

# Спрашиваем подтверждение
Write-Host "`n=== ВНИМАНИЕ ===" -ForegroundColor Yellow
Write-Host "Убедитесь, что в списке выше НЕТ:" -ForegroundColor Yellow
Write-Host "  - .env (реальный файл с токеном)" -ForegroundColor Red
Write-Host "  - seen_projects.json" -ForegroundColor Red
Write-Host "  - chat_id.json" -ForegroundColor Red
Write-Host "`nДолжны быть:" -ForegroundColor Yellow
Write-Host "  - .env.example" -ForegroundColor Green
Write-Host "  - Все .py файлы" -ForegroundColor Green
Write-Host "  - README.md, requirements.txt и т.д." -ForegroundColor Green

$confirm = Read-Host "`nПродолжить коммит? (y/n)"
if ($confirm -ne "y" -and $confirm -ne "Y") {
    Write-Host "Отменено пользователем" -ForegroundColor Yellow
    exit 0
}

# Коммит
Write-Host "`nСоздание коммита..." -ForegroundColor Yellow
git commit -m "Add Kwork monitoring Telegram bot

- Telegram bot for monitoring Kwork projects
- Supports bots and parsing/scraping projects
- Uses Playwright for JavaScript rendering
- Ready for Ubuntu deployment"

if ($LASTEXITCODE -ne 0) {
    Write-Host "Ошибка при создании коммита!" -ForegroundColor Red
    exit 1
}

# Настройка remote
Write-Host "`nНастройка remote репозитория..." -ForegroundColor Yellow
$remoteUrl = "https://github.com/SpiritWalker84/sysadmin_repo.git"

# Проверяем существующий remote
$existingRemote = git remote get-url origin 2>&1
if ($LASTEXITCODE -eq 0) {
    if ($existingRemote -ne $remoteUrl) {
        Write-Host "Обновление remote URL..." -ForegroundColor Yellow
        git remote set-url origin $remoteUrl
    } else {
        Write-Host "✓ Remote уже настроен правильно" -ForegroundColor Green
    }
} else {
    Write-Host "Добавление remote..." -ForegroundColor Yellow
    git remote add origin $remoteUrl
}

# Проверяем текущую ветку
$currentBranch = git branch --show-current 2>&1
if (-not $currentBranch) {
    Write-Host "Создание ветки main..." -ForegroundColor Yellow
    git branch -M main
}

# Push
Write-Host "`n=== Выгрузка на GitHub ===" -ForegroundColor Green
Write-Host "URL: $remoteUrl" -ForegroundColor Cyan
Write-Host "`nВыполните команду вручную:" -ForegroundColor Yellow
Write-Host "  git push -u origin main" -ForegroundColor Cyan
Write-Host "`nИли если репозиторий уже существует и нужно перезаписать:" -ForegroundColor Yellow
Write-Host "  git push -u origin main --force" -ForegroundColor Cyan
Write-Host "`nПри необходимости введите логин и пароль (или токен)" -ForegroundColor Yellow

