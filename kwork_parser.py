"""
Модуль для парсинга проектов с сайта Kwork.ru
"""
import asyncio
import re
from typing import List, Dict, Optional
from selectolax.parser import HTMLParser
from playwright.async_api import async_playwright


# URL страницы с проектами (общая категория разработки и IT)
# c=41 - категория "Разработка и IT"
KWORK_URL = "https://kwork.ru/projects?c=41"

# Селекторы для парсинга (могут потребоваться корректировки при изменении разметки Kwork)
# Основной контейнер с проектами
PROJECTS_CONTAINER_SELECTOR = ".project-card, .card-project, [data-project-id]"

# Селекторы для отдельных элементов проекта
TITLE_SELECTOR = "h2 a, .project-title a, a.project-title"
PRICE_SELECTOR = ".price, .project-price, .budget"
DESCRIPTION_SELECTOR = ".description, .project-description, .text"


async def fetch_projects_page() -> Optional[str]:
    """
    Получает HTML страницы с проектами Kwork через Playwright (выполняет JS).
    Использует retry логику для повышения устойчивости к сетевых ошибкам.
    
    Returns:
        str: HTML содержимое страницы после выполнения JavaScript или None в случае ошибки
    """
    max_retries = 3
    retry_delay = 5  # секунд
    
    for attempt in range(max_retries):
        try:
            async with async_playwright() as p:
                browser = await p.chromium.launch(headless=True)
                page = await browser.new_page()
                
                # Устанавливаем заголовки
                await page.set_extra_http_headers({
                    "Accept-Language": "ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7",
                })
                
                # Используем "load" вместо "networkidle" для более быстрой и надежной загрузки
                # "networkidle" может не наступить при постоянных фоновых запросах
                try:
                    await page.goto(KWORK_URL, wait_until="load", timeout=45000)
                except Exception as goto_error:
                    # Если "load" не сработал, пробуем "domcontentloaded" как запасной вариант
                    print(f"Предупреждение: 'load' не сработал, пробую 'domcontentloaded': {goto_error}")
                    try:
                        await page.goto(KWORK_URL, wait_until="domcontentloaded", timeout=45000)
                    except Exception:
                        raise goto_error
                
                # Ждём немного, чтобы JavaScript успел загрузить проекты
                await page.wait_for_timeout(3000)
                
                # Получаем HTML после выполнения JavaScript
                html = await page.content()
                await browser.close()
                
                return html
        except Exception as e:
            print(f"Ошибка при загрузке страницы Kwork через Playwright (попытка {attempt + 1}/{max_retries}): {e}")
            if attempt < max_retries - 1:
                print(f"Повторная попытка через {retry_delay} секунд...")
                await asyncio.sleep(retry_delay)
            else:
                import traceback
                traceback.print_exc()
                return None
    
    return None


def extract_project_id(url: str) -> Optional[int]:
    """
    Извлекает ID проекта из URL.
    
    Args:
        url: URL проекта вида /projects/123456/... или https://kwork.ru/projects/123456/...
    
    Returns:
        int: ID проекта или None, если не удалось извлечь
    """
    # Ищем паттерн /projects/число/
    match = re.search(r'/projects/(\d+)', url)
    if match:
        try:
            return int(match.group(1))
        except ValueError:
            return None
    return None


def parse_projects(html: str) -> List[Dict]:
    """
    Парсит HTML страницы и извлекает информацию о проектах.
    
    Args:
        html: HTML содержимое страницы
    
    Returns:
        List[Dict]: Список словарей с информацией о проектах:
            [
                {
                    "id": int,
                    "title": str,
                    "price": str | None,
                    "description": str | None,
                    "url": str,
                },
                ...
            ]
    """
    if not html:
        return []
    
    projects = []
    
    try:
        parser = HTMLParser(html)
        
        # Ищем все ссылки на проекты (самый надёжный способ)
        project_links = parser.css('a[href*="/projects/"]')
        
        if not project_links:
            return []
        
        # Группируем ссылки по уникальным ID проектов
        seen_ids = set()
        project_elements_data = []
        
        for link in project_links:
            href = link.attributes.get('href', '')
            if not href:
                continue
                
            # Извлекаем ID из URL
            project_id = extract_project_id(href)
            if not project_id or project_id in seen_ids:
                continue
            
            seen_ids.add(project_id)
            
            # Формируем полный URL
            if not href.startswith('http'):
                href = f"https://kwork.ru{href}"
            
            # Ищем родительский контейнер проекта (обычно это элемент с классом проекта)
            parent = link.parent
            while parent and parent.tag != 'html':
                # Пробуем найти контейнер проекта
                if parent.attributes and ('class' in str(parent.attributes) or parent.tag in ['div', 'article', 'li']):
                    break
                parent = parent.parent
            
            project_elements_data.append({
                'link': link,
                'href': href,
                'id': project_id,
                'parent': parent or link
            })
        
        
        for elem_data in project_elements_data:
            try:
                link_element = elem_data['link']
                href = elem_data['href']
                project_id = elem_data['id']
                parent_element = elem_data['parent']
                
                project_data = {}
                project_data['id'] = project_id
                project_data['url'] = href
                
                # Извлекаем заголовок из ссылки
                title = link_element.text(strip=True)
                if not title:
                    # Пробуем найти заголовок в дочерних элементах ссылки
                    title_elem = link_element.css_first('span, strong, b, .title')
                    if title_elem:
                        title = title_elem.text(strip=True)
                    # Если не нашли, пробуем в родительском элементе
                    if not title and parent_element:
                        title_elem = parent_element.css_first('h2, h3, .title, [class*="title"]')
                        if title_elem:
                            title = title_elem.text(strip=True)
                
                project_data['title'] = title or "Без названия"
                
                # Извлекаем цену - расширенный поиск
                price_text = None
                
                # Список возможных селекторов для цены на Kwork
                price_selectors = [
                    '.price', '.project-price', '.budget', '.amount',
                    '[class*="price"]', '[class*="Price"]', '[class*="budget"]', 
                    '[class*="Budget"]', '[class*="amount"]', '[class*="Amount"]',
                    '.wants-card__price', '.wants-card__price-value',  # Kwork селекторы
                    '[data-price]', '[data-budget]',  # Атрибуты данных
                ]
                
                # Ищем цену в родительском элементе
                if parent_element:
                    # Сначала проверяем атрибуты data-price и data-budget
                    if parent_element.attributes:
                        attrs = parent_element.attributes
                        if 'data-price' in attrs:
                            price_text = attrs['data-price']
                        elif 'data-budget' in attrs:
                            price_text = attrs['data-budget']
                    
                    # Если не нашли в атрибутах, ищем через селекторы
                    if not price_text:
                        for selector in price_selectors:
                            try:
                                price_elem = parent_element.css_first(selector)
                                if price_elem:
                                    # Проверяем атрибуты элемента с ценой
                                    if price_elem.attributes:
                                        elem_attrs = price_elem.attributes
                                        if 'data-price' in elem_attrs:
                                            price_text = elem_attrs['data-price']
                                            break
                                        elif 'data-budget' in elem_attrs:
                                            price_text = elem_attrs['data-budget']
                                            break
                                    
                                    # Берем текст элемента
                                    text = price_elem.text(strip=True)
                                    if text:
                                        price_text = text
                                        break
                            except:
                                continue
                
                # Если не нашли в parent, ищем в более широком контексте (вверх по DOM)
                if not price_text and parent_element:
                    current = parent_element.parent
                    max_levels = 3  # Ограничиваем глубину поиска
                    level = 0
                    while current and level < max_levels:
                        # Проверяем атрибуты текущего элемента
                        if current.attributes:
                            attrs = current.attributes
                            if 'data-price' in attrs:
                                price_text = attrs['data-price']
                                break
                            elif 'data-budget' in attrs:
                                price_text = attrs['data-budget']
                                break
                        
                        # Ищем через селекторы
                        for selector in price_selectors:
                            try:
                                price_elem = current.css_first(selector)
                                if price_elem:
                                    # Проверяем атрибуты
                                    if price_elem.attributes:
                                        elem_attrs = price_elem.attributes
                                        if 'data-price' in elem_attrs:
                                            price_text = elem_attrs['data-price']
                                            break
                                        elif 'data-budget' in elem_attrs:
                                            price_text = elem_attrs['data-budget']
                                            break
                                    
                                    text = price_elem.text(strip=True)
                                    if text:
                                        price_text = text
                                        break
                            except:
                                continue
                        if price_text:
                            break
                        current = current.parent
                        level += 1
                
                # Если всё ещё не нашли, ищем по текстовым паттернам (рубли, доллары, евро)
                if not price_text and parent_element:
                    try:
                        # Получаем весь текст родительского элемента
                        all_text = parent_element.text()
                        
                        # Сначала ищем "Желаемый бюджет" или "бюджет:" - это приоритетная цена
                        # Паттерны для формата "Желаемый бюджет: до 5 000 ₽" или "бюджет: до 15 000 ₽"
                        # Поддержка чисел с пробелами: 5 000, 15 000, 100 000 и т.д.
                        # Паттерн числа: \d{1,3}(?:\s+\d{3})* - это 1-3 цифры, затем группы по 3 цифры
                        # Также поддерживаем варианты без пробелов: "до5", ":12"
                        budget_patterns = [
                            # Сначала ищем "Желаемый бюджет" - приоритет
                            r'желаемый\s+бюджет[:\s]+до\s?\d{1,3}(?:\s+\d{3})*\s*[₽₴€$]',  # Желаемый бюджет: до 5 000 ₽ или до5 000₽
                            r'желаемый\s+бюджет[:\s]+до\s?\d{1,3}(?:\s+\d{3})*\s*(?:руб|рублей|руб\.)',  # Желаемый бюджет: до 5 000 руб
                            r'желаемый\s+бюджет[:\s]+\d{1,3}(?:\s+\d{3})*\s*[₽₴€$]',  # Желаемый бюджет: 5 000 ₽
                            r'желаемый\s+бюджет[:\s]+\d{1,3}(?:\s+\d{3})*\s*(?:руб|рублей|руб\.)',  # Желаемый бюджет: 5 000 руб
                            # Затем "Допустимый" - если нет желаемого
                            r'допустимый[:\s]+до\s?\d{1,3}(?:\s+\d{3})*\s*[₽₴€$]',  # Допустимый: до 15 000 ₽
                            r'допустимый[:\s]+до\s?\d{1,3}(?:\s+\d{3})*\s*(?:руб|рублей|руб\.)',  # Допустимый: до 15 000 руб
                            # "Цена до:" формат
                            r'цена\s+до[:\s]+\d{1,3}(?:\s+\d{3})*\s*[₽₴€$]',  # Цена до: 12 000 ₽
                            r'цена\s+до[:\s]+\d{1,3}(?:\s+\d{3})*\s*(?:руб|рублей|руб\.)',  # Цена до: 12 000 руб
                            # Общие паттерны бюджета
                            r'бюджет[:\s]+до\s?\d{1,3}(?:\s+\d{3})*\s*[₽₴€$]',  # бюджет: до 5 000 ₽
                            r'бюджет[:\s]+до\s?\d{1,3}(?:\s+\d{3})*\s*(?:руб|рублей|руб\.)',  # бюджет: до 5 000 руб
                            r'до\s?\d{1,3}(?:\s+\d{3})*\s*[₽₴€$]',  # до 5 000 ₽ или до5 000₽
                            r'до\s?\d{1,3}(?:\s+\d{3})*\s*(?:руб|рублей|руб\.)',  # до 5 000 руб
                        ]
                        
                        for pattern in budget_patterns:
                            match = re.search(pattern, all_text, re.IGNORECASE)
                            if match:
                                raw_text = match.group(0).strip()
                                
                                # Используем множественные замены для надежной нормализации
                                # Заменяем "до5" на "до 5" (все возможные варианты)
                                raw_text = re.sub(r'(?i)(до)(\d)', r'\1 \2', raw_text)
                                # Заменяем ":12" на ": 12"
                                raw_text = re.sub(r'(:)(\d)', r'\1 \2', raw_text)
                                # Заменяем "000₽" на "000 ₽"
                                raw_text = re.sub(r'(\d)([₽₴€$])', r'\1 \2', raw_text)
                                # Заменяем "000руб" на "000 руб"
                                raw_text = re.sub(r'(\d)(руб)', r'\1 \2', raw_text, flags=re.IGNORECASE)
                                
                                # Нормализуем все пробелы
                                raw_text = re.sub(r'\s+', ' ', raw_text)
                                price_text = raw_text.strip()
                                
                                if price_text:
                                    break
                        
                        # Если не нашли через "бюджет", ищем общие паттерны цены
                        if not price_text:
                            general_patterns = [
                                r'\d{1,3}(?:\s+\d{3})*\s*[₽₴€$]',  # 5 000 ₽, 50 $, 100 €
                                r'\d{1,3}(?:\s+\d{3})*\s*(?:руб|рублей|руб\.)',  # 5 000 руб
                                r'\d+(?:[\s,]\d+)*\s*[₽₴€$]',  # 5000 ₽, 50,000 $ (с запятыми)
                                r'\d+(?:[\s,]\d+)*\s*(?:руб|рублей|руб\.)',  # 5000 руб
                                r'[₽$€]\s*\d{1,3}(?:\s+\d{3})*',  # ₽ 5 000, $ 50
                                r'\d+(?:[\s,]\d+)*\s*(?:USD|EUR|RUB|usd|eur|rub)',  # 100 USD
                            ]
                            
                            for pattern in general_patterns:
                                match = re.search(pattern, all_text, re.IGNORECASE)
                                if match:
                                    price_text = match.group(0).strip()
                                    # Нормализуем пробелы и добавляем пробелы там, где их нет
                                    price_text = re.sub(r'\s+', ' ', price_text)
                                    # Добавляем пробел между числом и валютой если его нет: "000₽" -> "000 ₽"
                                    price_text = re.sub(r'(\d)([₽₴€$])', r'\1 \2', price_text)
                                    # Убираем лишние пробелы снова после нормализации
                                    price_text = re.sub(r'\s+', ' ', price_text).strip()
                                    break
                    except Exception as e:
                        print(f"Ошибка при поиске цены по паттернам: {e}")
                        pass
                
                # Финальная нормализация цены (применяем к любой найденной цене)
                if price_text:
                    # Добавляем пробелы там, где их явно нет
                    price_text = re.sub(r'(?i)(до)(\d)', r'\1 \2', price_text)  # "до5" -> "до 5"
                    price_text = re.sub(r'(:)(\d)', r'\1 \2', price_text)  # ":12" -> ": 12"
                    price_text = re.sub(r'(\d)([₽₴€$])', r'\1 \2', price_text)  # "000₽" -> "000 ₽"
                    price_text = re.sub(r'(\d)(руб)', r'\1 \2', price_text, flags=re.IGNORECASE)  # "000руб" -> "000 руб"
                    price_text = re.sub(r'\s+', ' ', price_text).strip()  # Нормализуем пробелы
                
                project_data['price'] = price_text if price_text else None
                
                # Извлекаем описание из родительского элемента
                desc_elem = None
                if parent_element:
                    desc_elem = parent_element.css_first('.description, .project-description, .text, [class*="description"], [class*="Description"], p')
                
                if desc_elem:
                    desc_text = desc_elem.text(strip=True)
                    # Ограничиваем длину описания
                    if desc_text and len(desc_text) > 300:
                        desc_text = desc_text[:300] + "..."
                    project_data['description'] = desc_text if desc_text else None
                else:
                    project_data['description'] = None
                
                projects.append(project_data)
                
            except Exception as e:
                print(f"Ошибка при парсинге проекта: {e}")
                continue
        
    except Exception as e:
        print(f"Ошибка при парсинге HTML: {e}")
    
    return projects

