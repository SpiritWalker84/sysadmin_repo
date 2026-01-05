"""
Модуль для работы с локальным хранилищем данных (JSON).
"""
import json
import os
from typing import Set, Optional


# Файлы для хранения данных
SEEN_IDS_FILE = "seen_projects.json"
CHAT_ID_FILE = "chat_id.json"


def load_seen_ids() -> Set[int]:
    """
    Загружает множество уже обработанных ID проектов.
    
    Returns:
        Set[int]: Множество ID проектов
    """
    if not os.path.exists(SEEN_IDS_FILE):
        return set()
    
    try:
        with open(SEEN_IDS_FILE, 'r', encoding='utf-8') as f:
            data = json.load(f)
            # Преобразуем список в множество
            if isinstance(data, list):
                return set(data)
            elif isinstance(data, dict) and 'ids' in data:
                return set(data['ids'])
            else:
                return set()
    except (json.JSONDecodeError, IOError) as e:
        print(f"Ошибка при загрузке seen_ids: {e}")
        return set()


def save_seen_ids(ids: Set[int]) -> None:
    """
    Сохраняет множество обработанных ID проектов.
    
    Args:
        ids: Множество ID проектов для сохранения
    """
    try:
        # Преобразуем множество в список для JSON
        data = list(ids)
        with open(SEEN_IDS_FILE, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    except IOError as e:
        print(f"Ошибка при сохранении seen_ids: {e}")


def load_chat_id() -> Optional[int]:
    """
    Загружает сохранённый chat_id пользователя.
    
    Returns:
        int: chat_id или None, если не сохранён
    """
    if not os.path.exists(CHAT_ID_FILE):
        return None
    
    try:
        with open(CHAT_ID_FILE, 'r', encoding='utf-8') as f:
            data = json.load(f)
            if isinstance(data, dict):
                return data.get('chat_id')
            elif isinstance(data, (int, str)):
                return int(data)
            else:
                return None
    except (json.JSONDecodeError, IOError, ValueError) as e:
        print(f"Ошибка при загрузке chat_id: {e}")
        return None


def save_chat_id(chat_id: int) -> None:
    """
    Сохраняет chat_id пользователя.
    
    Args:
        chat_id: ID чата пользователя
    """
    try:
        data = {'chat_id': chat_id}
        with open(CHAT_ID_FILE, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    except IOError as e:
        print(f"Ошибка при сохранении chat_id: {e}")

