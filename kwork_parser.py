"""
Модуль для парсинга проектов с сайта Kwork.ru
"""
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
    
    Returns:
        str: HTML содержимое страницы после выполнения JavaScript или None в случае ошибки
    """
    try:
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            page = await browser.new_page()
            
            # Устанавливаем заголовки
            await page.set_extra_http_headers({
                "Accept-Language": "ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7",
            })
            
            # Переходим на страницу и ждём загрузки контента
            await page.goto(KWORK_URL, wait_until="networkidle", timeout=30000)
            
            # Ждём немного, чтобы JavaScript успел загрузить проекты
            await page.wait_for_timeout(3000)
            
            # Получаем HTML после выполнения JavaScript
            html = await page.content()
            await browser.close()
            
            return html
    except Exception as e:
        print(f"Ошибка при загрузке страницы Kwork через Playwright: {e}")
        import traceback
        traceback.print_exc()
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
                
                # Извлекаем цену из родительского элемента
                price_elem = None
                if parent_element:
                    price_elem = parent_element.css_first('.price, .project-price, .budget, [class*="price"], [class*="Price"], .amount')
                
                if price_elem:
                    price_text = price_elem.text(strip=True)
                    project_data['price'] = price_text if price_text else None
                else:
                    project_data['price'] = None
                
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

