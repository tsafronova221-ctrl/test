#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Запуск консольного клиента для библиотеки видеоигр
"""

import sys
import os

# Добавляем путь к клиенту
sys.path.append(os.path.join(os.path.dirname(__file__), 'client'))

from console_client import ConsoleClient

def main():
    """Запуск клиента"""
    # Можно передать URL API как аргумент
    api_url = "http://localhost:5090/api"
    if len(sys.argv) > 1:
        api_url = sys.argv[1]
    
    print(f"🔌 Подключение к API: {api_url}")
    print("⚠️ Убедитесь, что сервер запущен!")
    
    try:
        client = ConsoleClient(api_url)
        client.run()
    except KeyboardInterrupt:
        print("\n\n👋 Программа завершена")
    except Exception as e:
        print(f"❌ Ошибка: {e}")

if __name__ == "__main__":
    main()