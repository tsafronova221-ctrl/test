"""
Клиент для работы с REST API библиотеки видеоигр
"""

import requests
import json
from typing import List, Dict, Optional, Any

class GameAPIClient:
    """Клиент для REST API библиотеки видеоигр"""
    
    def __init__(self, base_url: str = "http://localhost:5000/api"):
        self.base_url = base_url.rstrip('/')
        self.session = requests.Session()
    
    def _handle_response(self, response: requests.Response) -> Dict[str, Any]:
        """Обработка ответа от API"""
        try:
            data = response.json()
        except:
            data = {'success': False, 'error': 'Неверный формат ответа'}
        
        if not response.ok:
            error_msg = data.get('error', data.get('message', 'Неизвестная ошибка'))
            raise Exception(f"API Error ({response.status_code}): {error_msg}")
        
        return data
    
    # ==================== GET запросы ====================
    
    def get_all_games(self) -> List[Dict[str, Any]]:
        """Получить все игры"""
        response = self.session.get(f"{self.base_url}/games")
        data = self._handle_response(response)
        return data.get('games', [])
    
    def get_game(self, game_id: int) -> Dict[str, Any]:
        """Получить игру по ID"""
        response = self.session.get(f"{self.base_url}/games/{game_id}")
        data = self._handle_response(response)
        return data.get('game', {})
    
    def get_games_by_type(self, game_type: str) -> List[Dict[str, Any]]:
        """Получить игры по типу"""
        response = self.session.get(f"{self.base_url}/games/type/{game_type}")
        data = self._handle_response(response)
        return data.get('games', [])
    
    def search_games(self, query: str) -> List[Dict[str, Any]]:
        """Поиск игр по названию"""
        response = self.session.get(f"{self.base_url}/search", params={'q': query})
        data = self._handle_response(response)
        return data.get('games', [])
    
    def get_statistics(self) -> Dict[str, Any]:
        """Получить статистику"""
        response = self.session.get(f"{self.base_url}/statistics")
        data = self._handle_response(response)
        return data.get('statistics', {})
    
    # ==================== POST запросы ====================
    
    def create_indie_game(self, title: str, developer: str, year: int, 
                          price: float, team_size: int, engine: str) -> Dict[str, Any]:
        """Создать инди-игру"""
        data = {
            'type': 'indie',
            'title': title,
            'developer': developer,
            'year': year,
            'price': price,
            'team_size': team_size,
            'engine': engine
        }
        response = self.session.post(f"{self.base_url}/games", json=data)
        return self._handle_response(response)
    
    def create_aaa_game(self, title: str, developer: str, year: int,
                        price: float, budget: float, platforms: List[str] = None) -> Dict[str, Any]:
        """Создать AAA-игру"""
        data = {
            'type': 'aaa',
            'title': title,
            'developer': developer,
            'year': year,
            'price': price,
            'budget': budget,
            'platforms': platforms or []
        }
        response = self.session.post(f"{self.base_url}/games", json=data)
        return self._handle_response(response)
    
    def create_mobile_game(self, title: str, developer: str, year: int,
                          price: float, is_free: bool, microtransactions: bool) -> Dict[str, Any]:
        """Создать мобильную игру"""
        # Для бесплатных игр цена должна быть 0
        if is_free:
            price = 0.0
        
        data = {
            'type': 'mobile',
            'title': title,
            'developer': developer,
            'year': year,
            'price': price,
            'is_free': is_free,
            'microtransactions': microtransactions
        }
        response = self.session.post(f"{self.base_url}/games", json=data)
        return self._handle_response(response)
    
    # ==================== PUT/PATCH запросы ====================
    
    def update_game(self, game_id: int, **kwargs) -> Dict[str, Any]:
        """Полное обновление игры"""
        response = self.session.put(f"{self.base_url}/games/{game_id}", json=kwargs)
        return self._handle_response(response)
    
    def patch_game(self, game_id: int, **kwargs) -> Dict[str, Any]:
        """Частичное обновление игры"""
        response = self.session.patch(f"{self.base_url}/games/{game_id}", json=kwargs)
        return self._handle_response(response)
    
    # ==================== DELETE запросы ====================
    
    def delete_game(self, game_id: int) -> Dict[str, Any]:
        """Удалить игру"""
        response = self.session.delete(f"{self.base_url}/games/{game_id}")
        return self._handle_response(response)
    
    # ==================== Вспомогательные методы ====================
    
    def game_to_string(self, game: Dict[str, Any]) -> str:
        """Преобразовать игру в строку для отображения"""
        game_type = game.get('type', 'unknown')
        
        if game_type == 'indie':
            return (f"[{game['id']}] 🎨 Инди-игра: {game['title']} ({game['year']})\n"
                   f"    Разработчик: {game['developer']}, Цена: ${game['price']:.2f}\n"
                   f"    Команда: {game['team_size']} чел., Движок: {game['engine']}")
        elif game_type == 'aaa':
            platforms = ', '.join(game.get('platforms', []))
            return (f"[{game['id']}] 💰 AAA-игра: {game['title']} ({game['year']})\n"
                   f"    Разработчик: {game['developer']}, Цена: ${game['price']:.2f}\n"
                   f"    Бюджет: ${game['budget']:.2f}M, Платформы: {platforms}")
        elif game_type == 'mobile':
            status = "БЕСПЛАТНАЯ" if game.get('is_free') else "ПЛАТНАЯ"
            price_str = "" if game.get('is_free') else f", Цена: ${game['price']:.2f}"
            micro = "✅ есть микротранзакции" if game.get('microtransactions') else "❌ нет микротранзакций"
            return (f"[{game['id']}] 📱 Мобильная игра: {game['title']} ({game['year']})\n"
                   f"    Разработчик: {game['developer']}, Статус: {status}{price_str}\n"
                   f"    {micro}")
        else:
            return f"[{game['id']}] {game.get('title', 'Unknown')}"
    
    def print_game(self, game: Dict[str, Any]) -> None:
        """Вывести игру в консоль"""
        print(self.game_to_string(game))
        print("-" * 50)