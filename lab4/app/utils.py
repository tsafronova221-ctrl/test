import pickle
import os
from app import db
from app.models import Game, IndieGame, AAAGame, MobileGame
from sqlalchemy import func
from datetime import datetime

def get_statistics():
    total_games = Game.query.count()
    
    stats = {
        '🎨 Инди-игры': IndieGame.query.count(),
        '💰 AAA-игры': AAAGame.query.count(),
        '📱 Мобильные игры': MobileGame.query.count()
    }
    
    total_price = db.session.query(func.sum(Game.price)).scalar() or 0
    avg_price = total_price / total_games if total_games > 0 else 0
    
    year_min = db.session.query(func.min(Game.year)).scalar() or 0
    year_max = db.session.query(func.max(Game.year)).scalar() or 0
    
    return {
        'stats': stats,
        'total_games': total_games,
        'total_price': total_price,
        'avg_price': avg_price,
        'year_min': year_min,
        'year_max': year_max
    }

def list_saved_files(data_dir):
    files = []
    if os.path.exists(data_dir):
        for f in os.listdir(data_dir):
            if f.endswith('.pkl') or f.endswith('.txt'):
                filepath = os.path.join(data_dir, f)
                files.append({
                    'name': f,
                    'size': os.path.getsize(filepath),
                    'modified': datetime.fromtimestamp(os.path.getmtime(filepath))
                })
    return sorted(files, key=lambda x: x['name'], reverse=True)