"""
Основной модуль Telegram-бота для мониторинга проектов Kwork.
"""
import asyncio
import os
import datetime
from typing import List, Set
from dotenv import load_dotenv
from aiogram import Bot, Dispatcher
from aiogram.filters import Command
from aiogram.types import Message
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties

from kwork_parser import fetch_projects_page, parse_projects
from storage import load_seen_ids, save_seen_ids, load_chat_id, save_chat_id


# Загружаем переменные окружения
load_dotenv()

# Конфигурация из .env
BOT_TOKEN = os.getenv("BOT_TOKEN")
POLL_INTERVAL = int(os.getenv("POLL_INTERVAL", "180"))  # По умолчанию 3 минуты
KEYWORDS_STR = os.getenv("KEYWORDS", "")

# Парсим ключевые слова
KEYWORDS = [kw.strip().lower() for kw in KEYWORDS_STR.split(",") if kw.strip()]

# Инициализация бота и диспетчера (будет создан в main после проверки токена)
bot = None
dp = Dispatcher()

# Флаг для остановки фоновой задачи
background_task_running = False


def matches_keywords(text: str) -> bool:
    """
    Проверяет, содержит ли текст одно из ключевых слов.
    Использует более гибкую проверку: ищет слова отдельно и комбинации.
    
    Args:
        text: Текст для проверки
    
    Returns:
        bool: True, если найдено совпадение
    """
    if not text:
        return False
    
    text_lower = text.lower()
    
    # Сначала проверяем точные вхождения ключевых слов
    for keyword in KEYWORDS:
        if keyword in text_lower:
            return True
    
    # Дополнительная проверка: ищем слова "telegram" или "телеграм" + "бот"
    # Это покрывает случаи типа "Telegram Бот", "TG-бот" и т.д.
    telegram_words = ['telegram', 'телеграм', 'тг', 'tg']
    bot_words = ['бот', 'bot']
    
    has_telegram = any(word in text_lower for word in telegram_words)
    has_bot = any(word in text_lower for word in bot_words)
    
    if has_telegram and has_bot:
        return True
    
    # Проверка на парсинг/парсеры
    parsing_words = ['парсинг', 'парсер', 'parser', 'parsing', 'скрапинг', 'scraping', 
                     'скрапер', 'scraper', 'парс', 'parse', 'сбор данных', 'data extraction']
    
    if any(word in text_lower for word in parsing_words):
        return True
    
    return False


def filter_projects(projects: List[dict]) -> List[dict]:
    """
    Фильтрует проекты по ключевым словам.
    
    Args:
        projects: Список проектов
    
    Returns:
        List[dict]: Отфильтрованный список проектов
    """
    filtered = []
    for project in projects:
        title = project.get("title", "")
        description = project.get("description", "") or ""
        
        # Проверяем заголовок и описание
        if matches_keywords(title) or matches_keywords(description):
            filtered.append(project)
    
    return filtered


def format_project_message(project: dict) -> str:
    """
    Форматирует сообщение о проекте для отправки в Telegram.
    
    Args:
        project: Словарь с данными проекта
    
    Returns:
        str: Отформатированное сообщение
    """
    title = project.get("title", "Без названия")
    price = project.get("price") or "не указана"
    description = project.get("description") or ""
    url = project.get("url", "")
    
    message = f"🧾 <b>Новое задание Kwork</b>\n\n"
    message += f"<b>Заголовок:</b> {title}\n"
    message += f"<b>Цена:</b> {price}\n"
    
    if description:
        message += f"<b>Описание:</b> {description}\n"
    
    message += f"\n<b>Ссылка:</b> {url}"
    
    return message


async def check_new_projects(chat_id: int) -> None:
    """
    Проверяет новые проекты на Kwork и отправляет их пользователю.
    
    Args:
        chat_id: ID чата для отправки сообщений
    """
    try:
        # Загружаем уже обработанные ID
        seen_ids = load_seen_ids()
        
        # Получаем и парсим страницу
        html = await fetch_projects_page()
        if not html:
            print("Не удалось загрузить страницу Kwork")
            return
        
        projects = parse_projects(html)
        if not projects:
            print("Не найдено проектов на странице")
            return
        
        print(f"Всего проектов на странице: {len(projects)}")
        
        # Фильтруем по ключевым словам
        filtered_projects = filter_projects(projects)
        print(f"Проектов после фильтрации по ключевым словам: {len(filtered_projects)}")
        
        # Отладочная информация (только для первых запусков)
        if len(seen_ids) == 0 and len(filtered_projects) > 0:
            print(f"\nНайдено подходящих проектов: {len(filtered_projects)}")
        
        # Находим новые проекты
        new_projects = [p for p in filtered_projects if p.get("id") not in seen_ids]
        print(f"Уже обработанных проектов: {len(seen_ids)}")
        print(f"Новых проектов: {len(new_projects)}")
        
        if new_projects:
            print(f"Найдено {len(new_projects)} новых проектов")
            
            # Отправляем каждое новое задание
            for project in new_projects:
                try:
                    message = format_project_message(project)
                    await bot.send_message(chat_id=chat_id, text=message)
                    
                    # Добавляем ID в множество обработанных
                    project_id = project.get("id")
                    if project_id:
                        seen_ids.add(project_id)
                    
                    # Небольшая задержка между сообщениями
                    await asyncio.sleep(1)
                    
                except Exception as e:
                    print(f"Ошибка при отправке сообщения: {e}")
            
            # Сохраняем обновлённый список seen_ids
            save_seen_ids(seen_ids)
        else:
            if len(filtered_projects) > 0:
                print(f"Новых проектов не найдено (все {len(filtered_projects)} проектов уже были отправлены ранее)")
            else:
                print("Новых проектов не найдено (после фильтрации подходящих проектов нет)")
            
    except Exception as e:
        print(f"Ошибка при проверке проектов: {e}")


async def background_task() -> None:
    """
    Фоновая задача для периодической проверки новых проектов.
    """
    global background_task_running
    
    while background_task_running:
        try:
            chat_id = load_chat_id()
            if chat_id:
                await check_new_projects(chat_id)
            else:
                print("Chat ID не сохранён, пропускаем проверку")
            
            # Вычисляем время следующей проверки
            next_check = datetime.datetime.now() + datetime.timedelta(seconds=POLL_INTERVAL)
            next_check_str = next_check.strftime("%H:%M:%S")
            print(f"Следующая проверка в {next_check_str} (через {POLL_INTERVAL} секунд)")
            print("-" * 50)
            
            # Ждём указанный интервал
            await asyncio.sleep(POLL_INTERVAL)
            
        except Exception as e:
            print(f"Ошибка в фоновой задаче: {e}")
            import traceback
            traceback.print_exc()
            next_check = datetime.datetime.now() + datetime.timedelta(seconds=60)
            next_check_str = next_check.strftime("%H:%M:%S")
            print(f"Следующая проверка после ошибки в {next_check_str} (через 60 секунд)")
            await asyncio.sleep(60)  # При ошибке ждём минуту перед повтором


@dp.message(Command("start"))
async def cmd_start(message: Message) -> None:
    """
    Обработчик команды /start.
    Сохраняет chat_id пользователя и запускает фоновую задачу.
    """
    chat_id = message.chat.id
    
    # Сохраняем chat_id
    save_chat_id(chat_id)
    
    welcome_text = (
        "👋 <b>Привет!</b>\n\n"
        "Я буду отслеживать новые задания на Kwork по категории Telegram-ботов "
        "и присылать тебе уведомления о подходящих проектах.\n\n"
        "Проверка происходит автоматически каждые несколько минут."
    )
    
    await message.answer(welcome_text)
    
    # Запускаем фоновую задачу, если она ещё не запущена
    global background_task_running
    if not background_task_running:
        background_task_running = True
        asyncio.create_task(background_task())
        print("Фоновая задача запущена")


@dp.message(Command("check"))
async def cmd_check(message: Message) -> None:
    """
    Обработчик команды /check для ручной проверки проектов.
    """
    chat_id = message.chat.id
    await message.answer("🔍 Проверяю новые проекты...")
    await check_new_projects(chat_id)


async def main() -> None:
    """
    Главная функция для запуска бота.
    """
    global bot
    
    # Проверяем наличие токена
    if not BOT_TOKEN:
        print("Ошибка: BOT_TOKEN не указан в .env файле")
        print("Убедитесь, что в файле .env есть строка: BOT_TOKEN=ваш_токен")
        return
    
    # Инициализируем бота после проверки токена
    bot = Bot(
        token=BOT_TOKEN,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML)
    )
    
    if not KEYWORDS:
        print("Предупреждение: KEYWORDS не указаны в .env файле")
    
    print("Бот запущен...")
    print(f"Интервал опроса: {POLL_INTERVAL} секунд")
    print(f"Ключевые слова: {', '.join(KEYWORDS) if KEYWORDS else 'не указаны'}")
    
    # Проверяем подключение к Telegram API
    print("Проверка подключения к Telegram API...")
    try:
        bot_info = await bot.get_me()
        print(f"✓ Бот подключен: @{bot_info.username}")
    except Exception as e:
        print(f"✗ Ошибка подключения к Telegram API: {e}")
        print("Проверьте BOT_TOKEN в файле .env")
        return
    
    # Запускаем фоновую задачу, если есть сохранённый chat_id
    global background_task_running
    saved_chat_id = load_chat_id()
    if saved_chat_id:
        print(f"Найден сохранённый chat_id: {saved_chat_id}")
        background_task_running = True
        asyncio.create_task(background_task())
        print("Фоновая задача запущена")
    else:
        print("Chat ID не сохранён. Отправьте /start боту в Telegram для начала работы.")
    
    # Запускаем бота
    print("Ожидание команд от пользователя...")
    print("Отправьте /start боту в Telegram для начала работы.")
    try:
        await dp.start_polling(bot)
    except KeyboardInterrupt:
        print("\nОстановка бота...")
    finally:
        background_task_running = False
        await bot.session.close()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nБот остановлен")

