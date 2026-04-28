#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Консольный клиент для библиотеки видеоигр
Использует REST API как источник данных (вместо локального хранилища)
"""

import os
import sys
from typing import Optional
from api_client import GameAPIClient

class ConsoleClient:
    """Консольный интерфейс для работы с библиотекой через API"""
    
    def __init__(self, api_url: str = "http://localhost:5090/api"):
        self.api = GameAPIClient(api_url)
        self.current_game_id: Optional[int] = None
    
    def clear_screen(self):
        """Очистка экрана"""
        os.system('cls' if os.name == 'nt' else 'clear')
    
    def print_header(self, title: str):
        """Печать заголовка"""
        print("\n" + "=" * 60)
        print(f"🎮 {title}")
        print("=" * 60)
    
    def print_menu(self):
        """Печать главного меню"""
        self.print_header("КОНСОЛЬНЫЙ КЛИЕНТ БИБЛИОТЕКИ ВИДЕОИГР")
        print("\n📋 ОСНОВНЫЕ КОМАНДЫ:")
        print("  1. Показать все игры")
        print("  2. Показать игру по ID")
        print("  3. Показать игры по типу")
        print("  4. Поиск игр по названию")
        print("  5. Показать статистику")
        print("\n➕ ДОБАВЛЕНИЕ ИГР:")
        print("  6. Добавить инди-игру")
        print("  7. Добавить AAA-игру")
        print("  8. Добавить мобильную игру")
        print("\n✏️ РЕДАКТИРОВАНИЕ:")
        print("  9. Редактировать игру")
        print(" 10. Частичное обновление игры")
        print("\n🗑️ УДАЛЕНИЕ:")
        print(" 11. Удалить игру")
        print("\n🚪 ВЫХОД:")
        print("  0. Выход")
        print("-" * 60)
    
    def get_input(self, prompt: str, required: bool = True) -> str:
        """Получение ввода от пользователя"""
        while True:
            value = input(prompt).strip()
            if not required or value:
                return value
            print("❌ Поле не может быть пустым!")
    
    def get_int_input(self, prompt: str, min_val: int = None, max_val: int = None) -> Optional[int]:
        """Получение целочисленного ввода"""
        while True:
            try:
                value = input(prompt).strip()
                if not value:
                    return None
                num = int(value)
                if min_val is not None and num < min_val:
                    print(f"❌ Число должно быть >= {min_val}")
                    continue
                if max_val is not None and num > max_val:
                    print(f"❌ Число должно быть <= {max_val}")
                    continue
                return num
            except ValueError:
                print("❌ Введите целое число!")
    
    def get_float_input(self, prompt: str, min_val: float = None, max_val: float = None) -> Optional[float]:
        """Получение числа с плавающей точкой"""
        while True:
            try:
                value = input(prompt).strip()
                if not value:
                    return None
                num = float(value)
                if min_val is not None and num < min_val:
                    print(f"❌ Число должно быть >= {min_val}")
                    continue
                if max_val is not None and num > max_val:
                    print(f"❌ Число должно быть <= {max_val}")
                    continue
                return num
            except ValueError:
                print("❌ Введите число!")
    
    def get_bool_input(self, prompt: str) -> bool:
        """Получение булевого значения"""
        value = input(prompt).strip().lower()
        return value in ['да', 'д', 'yes', 'y', '1', '+']
    
    # ==================== ОТОБРАЖЕНИЕ ====================
    
    def show_all_games(self):
        """Показать все игры"""
        self.print_header("ВСЕ ИГРЫ")
        try:
            games = self.api.get_all_games()
            if not games:
                print("📭 Библиотека пуста")
                return
            
            print(f"📊 Всего игр: {len(games)}\n")
            for game in games:
                self.api.print_game(game)
        except Exception as e:
            print(f"❌ Ошибка: {e}")
    
    def show_game_by_id(self):
        """Показать игру по ID"""
        game_id = self.get_int_input("Введите ID игры: ")
        if not game_id:
            return
        
        try:
            game = self.api.get_game(game_id)
            self.print_header(f"ИГРА #{game_id}")
            self.api.print_game(game)
        except Exception as e:
            print(f"❌ Ошибка: {e}")
    
    def show_games_by_type(self):
        """Показать игры по типу"""
        print("\nТипы игр:")
        print("  1. Инди-игры")
        print("  2. AAA-игры")
        print("  3. Мобильные игры")
        
        choice = self.get_int_input("Выберите тип (1-3): ", 1, 3)
        if not choice:
            return
        
        type_map = {1: 'indie', 2: 'aaa', 3: 'mobile'}
        type_name = {1: "ИНДИ-ИГРЫ", 2: "AAA-ИГРЫ", 3: "МОБИЛЬНЫЕ ИГРЫ"}
        
        try:
            games = self.api.get_games_by_type(type_map[choice])
            self.print_header(type_name[choice])
            
            if not games:
                print(f"📭 Нет игр этого типа")
                return
            
            print(f"📊 Найдено: {len(games)}\n")
            for game in games:
                self.api.print_game(game)
        except Exception as e:
            print(f"❌ Ошибка: {e}")
    
    def search_games(self):
        """Поиск игр по названию"""
        query = self.get_input("Введите название для поиска: ")
        
        try:
            games = self.api.search_games(query)
            self.print_header(f"РЕЗУЛЬТАТЫ ПОИСКА: '{query}'")
            
            if not games:
                print(f"📭 Ничего не найдено")
                return
            
            print(f"📊 Найдено: {len(games)}\n")
            for game in games:
                self.api.print_game(game)
        except Exception as e:
            print(f"❌ Ошибка: {e}")
    
    def show_statistics(self):
        """Показать статистику"""
        try:
            stats = self.api.get_statistics()
            self.print_header("СТАТИСТИКА БИБЛИОТЕКИ")
            
            total = stats.get('total_games', 0)
            print(f"📊 Всего игр: {total}")
            print(f"💰 Общая стоимость: ${stats.get('total_price', 0):.2f}")
            print(f"📊 Средняя цена: ${stats.get('avg_price', 0):.2f}")
            print(f"📅 Диапазон годов: {stats.get('year_min', 0)} - {stats.get('year_max', 0)}")
            
            print("\n📈 Распределение по типам:")
            for type_name, count in stats.get('stats', {}).items():
                if count > 0 and total > 0:
                    percent = (count / total) * 100
                    bar = "█" * int(percent / 5)
                    print(f"  {type_name}: {count} ({percent:.1f}%)")
                    print(f"    {bar}")
                    
        except Exception as e:
            print(f"❌ Ошибка: {e}")
    
    # ==================== ДОБАВЛЕНИЕ ====================
    
    def add_indie_game(self):
        """Добавить инди-игру"""
        self.print_header("ДОБАВЛЕНИЕ ИНДИ-ИГРЫ")
        
        title = self.get_input("Название игры: ")
        developer = self.get_input("Разработчик: ")
        year = self.get_int_input("Год выпуска (1970-2026): ", 1970, 2026)
        price = self.get_float_input("Цена ($): ", 0, 1000)
        team_size = self.get_int_input("Размер команды: ", 1)
        engine = self.get_input("Игровой движок: ")
        
        try:
            result = self.api.create_indie_game(
                title=title,
                developer=developer,
                year=year,
                price=price,
                team_size=team_size,
                engine=engine
            )
            print(f"\n✅ {result.get('message', 'Игра добавлена!')}")
            if 'game' in result:
                self.api.print_game(result['game'])
        except Exception as e:
            print(f"❌ Ошибка: {e}")
    
    def add_aaa_game(self):
        """Добавить AAA-игру"""
        self.print_header("ДОБАВЛЕНИЕ AAA-ИГРЫ")
        
        title = self.get_input("Название игры: ")
        developer = self.get_input("Разработчик: ")
        year = self.get_int_input("Год выпуска (1970-2026): ", 1970, 2026)
        price = self.get_float_input("Цена ($): ", 0, 1000)
        budget = self.get_float_input("Бюджет (млн $): ", 1, 1000)
        
        platforms_input = self.get_input("Платформы (через запятую, необязательно): ", required=False)
        platforms = [p.strip() for p in platforms_input.split(',')] if platforms_input else []
        
        try:
            result = self.api.create_aaa_game(
                title=title,
                developer=developer,
                year=year,
                price=price,
                budget=budget,
                platforms=platforms
            )
            print(f"\n✅ {result.get('message', 'Игра добавлена!')}")
            if 'game' in result:
                self.api.print_game(result['game'])
        except Exception as e:
            print(f"❌ Ошибка: {e}")
    
    def add_mobile_game(self):
        """Добавить мобильную игру"""
        self.print_header("ДОБАВЛЕНИЕ МОБИЛЬНОЙ ИГРЫ")
        
        title = self.get_input("Название игры: ")
        developer = self.get_input("Разработчик: ")
        year = self.get_int_input("Год выпуска (1970-2026): ", 1970, 2026)
        
        is_free = self.get_bool_input("Бесплатная игра? (да/нет): ")
        
        # Если игра бесплатная, цену не запрашиваем
        if is_free:
            price = 0.0
            print("✅ Бесплатная игра - цена установлена в 0")
        else:
            price = self.get_float_input("Цена ($): ", 0, 1000)
            if price <= 0:
                print("❌ Для платной игры цена должна быть больше 0")
                return
        
        microtransactions = self.get_bool_input("Есть микротранзакции? (да/нет): ")
        
        try:
            result = self.api.create_mobile_game(
                title=title,
                developer=developer,
                year=year,
                price=price,
                is_free=is_free,
                microtransactions=microtransactions
            )
            print(f"\n✅ {result.get('message', 'Игра добавлена!')}")
            if 'game' in result:
                self.api.print_game(result['game'])
        except Exception as e:
            print(f"❌ Ошибка: {e}")
    
    # ==================== РЕДАКТИРОВАНИЕ ====================
    
    def edit_game(self):
        """Полное редактирование игры"""
        game_id = self.get_int_input("Введите ID игры для редактирования: ")
        if not game_id:
            return
        
        try:
            # Получаем текущие данные
            game = self.api.get_game(game_id)
            self.print_header(f"РЕДАКТИРОВАНИЕ ИГРЫ #{game_id}")
            print("Текущие данные:")
            self.api.print_game(game)
            print("\nВведите новые данные (Enter - оставить без изменений):")
            
            # Собираем новые данные
            data = {}
            
            title = self.get_input(f"Название [{game['title']}]: ", required=False)
            if title:
                data['title'] = title
            
            developer = self.get_input(f"Разработчик [{game['developer']}]: ", required=False)
            if developer:
                data['developer'] = developer
            
            year = self.get_int_input(f"Год [{game['year']}]: ")
            if year:
                data['year'] = year
            
            # Для мобильных игр особая обработка
            if game['type'] == 'mobile':
                is_free_str = "да" if game.get('is_free') else "нет"
                is_free = self.get_bool_input(f"Бесплатная игра? [{is_free_str}]: ")
                if is_free != game.get('is_free'):
                    data['is_free'] = is_free
                
                # Если игра становится бесплатной, цена будет 0
                if is_free:
                    data['price'] = 0.0
                else:
                    price = self.get_float_input(f"Цена [{game['price']}]: ")
                    if price and price > 0:
                        data['price'] = price
                
                micro = self.get_bool_input(f"Микротранзакции? [{'да' if game.get('microtransactions') else 'нет'}]: ")
                if micro != game.get('microtransactions'):
                    data['microtransactions'] = micro
            else:
                # Для остальных типов
                price = self.get_float_input(f"Цена [{game['price']}]: ")
                if price:
                    data['price'] = price
                
                if game['type'] == 'indie':
                    team_size = self.get_int_input(f"Размер команды [{game['team_size']}]: ")
                    if team_size:
                        data['team_size'] = team_size
                    
                    engine = self.get_input(f"Движок [{game['engine']}]: ", required=False)
                    if engine:
                        data['engine'] = engine
                
                elif game['type'] == 'aaa':
                    budget = self.get_float_input(f"Бюджет [{game['budget']}]: ")
                    if budget:
                        data['budget'] = budget
                    
                    platforms_input = self.get_input(f"Платформы [{', '.join(game.get('platforms', []))}]: ", required=False)
                    if platforms_input:
                        data['platforms'] = [p.strip() for p in platforms_input.split(',')]
            
            if not data:
                print("⚠️ Нет изменений")
                return
            
            result = self.api.update_game(game_id, **data)
            print(f"\n✅ {result.get('message', 'Игра обновлена!')}")
            
        except Exception as e:
            print(f"❌ Ошибка: {e}")
    
    def patch_game(self):
        """Частичное обновление игры"""
        game_id = self.get_int_input("Введите ID игры для обновления: ")
        if not game_id:
            return
        
        try:
            game = self.api.get_game(game_id)
            self.print_header(f"ЧАСТИЧНОЕ ОБНОВЛЕНИЕ ИГРЫ #{game_id}")
            print("Текущие данные:")
            self.api.print_game(game)
            print("\nВведите поля для обновления (Enter - пропустить):")
            
            data = {}
            
            title = self.get_input("Новое название (Enter - пропустить): ", required=False)
            if title:
                data['title'] = title
            
            developer = self.get_input("Новый разработчик (Enter - пропустить): ", required=False)
            if developer:
                data['developer'] = developer
            
            year = self.get_int_input("Новый год (Enter - пропустить): ")
            if year:
                data['year'] = year
            
            # Для мобильных игр особая обработка
            if game['type'] == 'mobile':
                is_free = self.get_bool_input("Бесплатная? (Enter - пропустить): ")
                if is_free != game.get('is_free'):
                    data['is_free'] = is_free
                    # Если игра становится бесплатной, цена будет 0
                    if is_free:
                        data['price'] = 0.0
                
                # Если игра остается платной или становится платной
                if not is_free and not game.get('is_free'):
                    price = self.get_float_input("Новая цена (Enter - пропустить): ")
                    if price and price > 0:
                        data['price'] = price
                
                micro = self.get_bool_input("Микротранзакции? (Enter - пропустить): ")
                if micro != game.get('microtransactions'):
                    data['microtransactions'] = micro
            else:
                price = self.get_float_input("Новая цена (Enter - пропустить): ")
                if price:
                    data['price'] = price
                
                if game['type'] == 'indie':
                    team_size = self.get_int_input("Новый размер команды (Enter - пропустить): ")
                    if team_size:
                        data['team_size'] = team_size
                    
                    engine = self.get_input("Новый движок (Enter - пропустить): ", required=False)
                    if engine:
                        data['engine'] = engine
                
                elif game['type'] == 'aaa':
                    budget = self.get_float_input("Новый бюджет (Enter - пропустить): ")
                    if budget:
                        data['budget'] = budget
                    
                    platforms_input = self.get_input("Новые платформы (Enter - пропустить): ", required=False)
                    if platforms_input:
                        data['platforms'] = [p.strip() for p in platforms_input.split(',')]
            
            if not data:
                print("⚠️ Нет изменений")
                return
            
            result = self.api.patch_game(game_id, **data)
            print(f"\n✅ {result.get('message', 'Игра обновлена!')}")
            
        except Exception as e:
            print(f"❌ Ошибка: {e}")
    
    # ==================== УДАЛЕНИЕ ====================
    
    def delete_game(self):
        """Удалить игру"""
        game_id = self.get_int_input("Введите ID игры для удаления: ")
        if not game_id:
            return
        
        try:
            # Показываем игру перед удалением
            game = self.api.get_game(game_id)
            self.print_header("ПОДТВЕРЖДЕНИЕ УДАЛЕНИЯ")
            self.api.print_game(game)
            
            confirm = input("\nВы уверены? (да/нет): ").strip().lower()
            if confirm not in ['да', 'д', 'yes', 'y']:
                print("❌ Удаление отменено")
                return
            
            result = self.api.delete_game(game_id)
            print(f"\n✅ {result.get('message', 'Игра удалена!')}")
            
        except Exception as e:
            print(f"❌ Ошибка: {e}")
    
    # ==================== ЗАПУСК ====================
    
    def run(self):
        """Запуск консольного клиента"""
        while True:
            self.clear_screen()
            self.print_menu()
            
            choice = self.get_int_input("\n👉 Выберите действие: ", 0, 11)
            
            if choice == 0:
                self.print_header("ДО СВИДАНИЯ!")
                print("👋 Спасибо за использование библиотеки!")
                break
            elif choice == 1:
                self.show_all_games()
            elif choice == 2:
                self.show_game_by_id()
            elif choice == 3:
                self.show_games_by_type()
            elif choice == 4:
                self.search_games()
            elif choice == 5:
                self.show_statistics()
            elif choice == 6:
                self.add_indie_game()
            elif choice == 7:
                self.add_aaa_game()
            elif choice == 8:
                self.add_mobile_game()
            elif choice == 9:
                self.edit_game()
            elif choice == 10:
                self.patch_game()
            elif choice == 11:
                self.delete_game()
            
            input("\n⏎ Нажмите Enter для продолжения...")

if __name__ == "__main__":
    client = ConsoleClient()
    client.run()