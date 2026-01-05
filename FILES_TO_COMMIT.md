# Файлы для коммита в GitHub

## ✅ Должны быть в репозитории:

### Исходный код:
- `bot.py`
- `kwork_parser.py`
- `storage.py`

### Конфигурация и зависимости:
- `requirements.txt`
- `.env.example` (пример, БЕЗ реальных данных)
- `.gitignore`
- `.gitattributes`

### Документация:
- `README.md`
- `QUICKSTART.md`
- `DEPLOYMENT_CHECKLIST.md`
- `LICENSE`

### Скрипты:
- `start.sh`

## ❌ НЕ должны быть в репозитории (уже в .gitignore):

- `.env` - реальная конфигурация с токеном
- `seen_projects.json` - данные
- `chat_id.json` - данные пользователя
- `__pycache__/` - кэш Python
- `.ms-playwright/` - кэш Playwright

## Проверка перед push:

1. Убедитесь, что `.env` НЕ закоммичен (проверьте `git status`)
2. Убедитесь, что `.env.example` закоммичен
3. Убедитесь, что нет реальных токенов в коде
4. Все зависимости указаны в `requirements.txt`

