# Быстрый старт

## Минимальная настройка за 5 минут

### 1. Клонирование и настройка

```bash
# Клонируйте репозиторий
git clone https://github.com/SpiritWalker84/sysadmin_repo.git
cd sysadmin_repo/wb_full

# Создайте виртуальное окружение
python3 -m venv venv
source venv/bin/activate

# Установите зависимости
pip install -r requirements.txt
```

### 2. Создание конфигурации

```bash
# Скопируйте пример
cp .env.example .env

# Отредактируйте .env (замените значения на реальные)
nano .env
```

**Минимально необходимые переменные:**
- `IMAP_LOGIN` - ваш email
- `IMAP_PASSWORD` - пароль от почты
- `WB_API_TOKEN` - токен API Wildberries

### 3. Проверка

```bash
python3 check_setup_price.py
```

### 4. Запуск

```bash
python3 run_full_update.py
```

## Что дальше?

- 📖 Полная документация: [README.md](README.md)
- 🚀 Развертывание: [DEPLOYMENT.md](DEPLOYMENT.md)
- 📝 Инструкции по Git: [GIT_DEPLOY_INSTRUCTIONS.md](GIT_DEPLOY_INSTRUCTIONS.md)

## Нужна помощь?

Проверьте:
- ✅ Все переменные в `.env` заполнены
- ✅ Файлы соответствия (`*Артикулы*.xlsx`, `*Баркоды*.xlsx`) в директории
- ✅ Интернет соединение активно
- ✅ API токен Wildberries валиден

