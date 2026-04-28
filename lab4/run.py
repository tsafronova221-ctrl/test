#!/usr/bin/env python3

from app import create_app, db
from app.models import Game, IndieGame, AAAGame, MobileGame
import os

app = create_app()

@app.shell_context_processor
def make_shell_context():
    return {
        'db': db,
        'Game': Game,
        'IndieGame': IndieGame,
        'AAAGame': AAAGame,
        'MobileGame': MobileGame
    }

if __name__ == '__main__':
    print("=" * 60)
    print("🎮 БИБЛИОТЕКА ВИДЕОИГР С SQLite")
    print("=" * 60)
    print(f"📁 База данных: {app.config['DATA_DIR']}\\games.db")
    print(f"📁 Папка для сохранений: {app.config['DATA_DIR']}")
    print(f"🌐 Сервер: http://localhost:5090")
    print("=" * 60)
    
    with app.app_context():
        db.create_all()
        print("✅ Таблицы созданы")
    
    app.run(debug=True, host='127.0.0.1', port=5090)