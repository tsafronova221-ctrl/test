from flask import Blueprint, jsonify, request, url_for
from app import db
from app.models import Game, IndieGame, AAAGame, MobileGame
from sqlalchemy.exc import IntegrityError
import json

api_bp = Blueprint('api', __name__, url_prefix='/api')

# ==================== ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ ====================

def game_to_dict(game):
    """Преобразует объект игры в словарь для JSON"""
    if isinstance(game, IndieGame):
        return {
            'id': game.id,
            'type': 'indie',
            'title': game.title,
            'developer': game.developer,
            'year': game.year,
            'price': game.price,
            'team_size': game.team_size,
            'engine': game.engine,
            'created_at': game.created_at.isoformat() if game.created_at else None,
            'updated_at': game.updated_at.isoformat() if game.updated_at else None
        }
    elif isinstance(game, AAAGame):
        return {
            'id': game.id,
            'type': 'aaa',
            'title': game.title,
            'developer': game.developer,
            'year': game.year,
            'price': game.price,
            'budget': game.budget,
            'platforms': game.platforms,
            'created_at': game.created_at.isoformat() if game.created_at else None,
            'updated_at': game.updated_at.isoformat() if game.updated_at else None
        }
    elif isinstance(game, MobileGame):
        return {
            'id': game.id,
            'type': 'mobile',
            'title': game.title,
            'developer': game.developer,
            'year': game.year,
            'price': game.effective_price,  # Используем effective_price
            'is_free': game.is_free,
            'microtransactions': game.microtransactions,
            'created_at': game.created_at.isoformat() if game.created_at else None,
            'updated_at': game.updated_at.isoformat() if game.updated_at else None
        }
    return None

def validate_game_data(data):
    """Проверяет корректность данных для создания/обновления игры"""
    errors = []
    
    # Проверка обязательных полей
    if not data.get('title'):
        errors.append("Поле 'title' обязательно")
    if not data.get('developer'):
        errors.append("Поле 'developer' обязательно")
    if not data.get('year'):
        errors.append("Поле 'year' обязательно")
    
    # Проверка типа
    game_type = data.get('type')
    if game_type not in ['indie', 'aaa', 'mobile']:
        errors.append("Поле 'type' должно быть 'indie', 'aaa' или 'mobile'")
    
    # Проверка цены для мобильных игр
    if game_type == 'mobile':
        is_free = data.get('is_free', False)
        if is_free:
            # Для бесплатных игр цена должна быть 0
            data['price'] = 0.0
        else:
            # Для платных игр цена обязательна
            if data.get('price') is None:
                errors.append("Для платной мобильной игры поле 'price' обязательно")
            elif float(data.get('price', 0)) <= 0:
                errors.append("Для платной мобильной игры цена должна быть > 0")
    else:
        # Для остальных игр цена обязательна
        if data.get('price') is None:
            errors.append("Поле 'price' обязательно")
    
    # Проверка специфичных полей
    if game_type == 'indie':
        if not data.get('team_size'):
            errors.append("Для indie игры поле 'team_size' обязательно")
        if not data.get('engine'):
            errors.append("Для indie игры поле 'engine' обязательно")
    elif game_type == 'aaa':
        if not data.get('budget'):
            errors.append("Для aaa игры поле 'budget' обязательно")
    elif game_type == 'mobile':
        if 'is_free' not in data:
            errors.append("Для mobile игры поле 'is_free' обязательно")
        if 'microtransactions' not in data:
            errors.append("Для mobile игры поле 'microtransactions' обязательно")
    
    return errors

# ==================== REST API МАРШРУТЫ ====================

@api_bp.route('/games', methods=['GET'])
def get_games():
    """Получить все игры"""
    games = Game.query.order_by(Game.created_at.desc()).all()
    return jsonify({
        'success': True,
        'count': len(games),
        'games': [game_to_dict(g) for g in games]
    })

@api_bp.route('/games/<int:game_id>', methods=['GET'])
def get_game(game_id):
    """Получить игру по ID"""
    game = Game.query.get(game_id)
    if not game:
        return jsonify({
            'success': False,
            'error': f'Игра с ID {game_id} не найдена'
        }), 404
    
    return jsonify({
        'success': True,
        'game': game_to_dict(game)
    })

@api_bp.route('/games', methods=['POST'])
def create_game():
    """Создать новую игру"""
    data = request.get_json()
    
    if not data:
        return jsonify({
            'success': False,
            'error': 'Нет данных в запросе'
        }), 400
    
    # Валидация
    errors = validate_game_data(data)
    if errors:
        return jsonify({
            'success': False,
            'errors': errors
        }), 400
    
    try:
        game_type = data.get('type')
        
        if game_type == 'indie':
            game = IndieGame(
                title=data['title'],
                developer=data['developer'],
                year=int(data['year']),
                price=float(data['price']),
                team_size=int(data['team_size']),
                engine=data['engine']
            )
        elif game_type == 'aaa':
            platforms = data.get('platforms', [])
            if isinstance(platforms, str):
                platforms = [p.strip() for p in platforms.split(',')]
            game = AAAGame(
                title=data['title'],
                developer=data['developer'],
                year=int(data['year']),
                price=float(data['price']),
                budget=float(data['budget']),
                platforms=platforms
            )
        elif game_type == 'mobile':
            is_free = bool(data.get('is_free', False))
            # Для бесплатных игр цена принудительно 0
            price = 0.0 if is_free else float(data.get('price', 0))
            
            game = MobileGame(
                title=data['title'],
                developer=data['developer'],
                year=int(data['year']),
                price=price,
                is_free=is_free,
                microtransactions=bool(data.get('microtransactions', False))
            )
        else:
            return jsonify({
                'success': False,
                'error': 'Неверный тип игры'
            }), 400
        
        db.session.add(game)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': f'Игра "{game.title}" создана',
            'game': game_to_dict(game)
        }), 201
        
    except IntegrityError as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': 'Ошибка целостности данных',
            'details': str(e)
        }), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@api_bp.route('/games/<int:game_id>', methods=['PUT'])
def update_game(game_id):
    """Обновить игру полностью"""
    game = Game.query.get(game_id)
    if not game:
        return jsonify({
            'success': False,
            'error': f'Игра с ID {game_id} не найдена'
        }), 404
    
    data = request.get_json()
    if not data:
        return jsonify({
            'success': False,
            'error': 'Нет данных в запросе'
        }), 400
    if 'type' in data and data['type'] != game.game_type:
        return jsonify({
            'success': False, 
            'error': 'Нельзя изменить тип существующей игры'
        }), 400
    
    try:
        # Обновляем базовые поля
        game.title = data.get('title', game.title)
        game.developer = data.get('developer', game.developer)
        game.year = data.get('year', game.year)
        
        # Для мобильных игр особая обработка цены
        if isinstance(game, MobileGame):
            is_free = data.get('is_free', game.is_free)
            game.is_free = is_free
            
            if is_free:
                game.price = 0.0
            else:
                game.price = data.get('price', game.price)
        else:
            game.price = data.get('price', game.price)
        
        # Обновляем специфичные поля
        if isinstance(game, IndieGame):
            game.team_size = data.get('team_size', game.team_size)
            game.engine = data.get('engine', game.engine)
        elif isinstance(game, AAAGame):
            game.budget = data.get('budget', game.budget)
            platforms = data.get('platforms', game.platforms)
            if isinstance(platforms, str):
                platforms = [p.strip() for p in platforms.split(',')]
            game.platforms = platforms
        elif isinstance(game, MobileGame):
            game.microtransactions = data.get('microtransactions', game.microtransactions)
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': f'Игра "{game.title}" обновлена',
            'game': game_to_dict(game)
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@api_bp.route('/games/<int:game_id>', methods=['PATCH'])
def patch_game(game_id):
    """Частичное обновление игры"""
    game = Game.query.get(game_id)
    if not game:
        return jsonify({
            'success': False,
            'error': f'Игра с ID {game_id} не найдена'
        }), 404
    
    data = request.get_json()
    if not data:
        return jsonify({
            'success': False,
            'error': 'Нет данных в запросе'
        }), 400
    
    try:
        # Обновляем только переданные поля
        if 'title' in data:
            game.title = data['title']
        if 'developer' in data:
            game.developer = data['developer']
        if 'year' in data:
            game.year = data['year']
        
        # Для мобильных игр особая обработка цены
        if isinstance(game, MobileGame):
            if 'is_free' in data:
                game.is_free = data['is_free']
            
            # Если игра стала бесплатной, цена 0
            if game.is_free:
                game.price = 0.0
            elif 'price' in data:
                game.price = data['price']
        elif 'price' in data:
            game.price = data['price']
        
        # Обновляем специфичные поля
        if isinstance(game, IndieGame):
            if 'team_size' in data:
                game.team_size = data['team_size']
            if 'engine' in data:
                game.engine = data['engine']
        elif isinstance(game, AAAGame):
            if 'budget' in data:
                game.budget = data['budget']
            if 'platforms' in data:
                platforms = data['platforms']
                if isinstance(platforms, str):
                    platforms = [p.strip() for p in platforms.split(',')]
                game.platforms = platforms
        elif isinstance(game, MobileGame):
            if 'microtransactions' in data:
                game.microtransactions = data['microtransactions']
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': f'Игра "{game.title}" обновлена',
            'game': game_to_dict(game)
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@api_bp.route('/games/<int:game_id>', methods=['DELETE'])
def delete_game(game_id):
    """Удалить игру"""
    game = Game.query.get(game_id)
    if not game:
        return jsonify({
            'success': False,
            'error': f'Игра с ID {game_id} не найдена'
        }), 404
    
    try:
        title = game.title
        db.session.delete(game)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': f'Игра "{title}" удалена'
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@api_bp.route('/games/type/<string:game_type>', methods=['GET'])
def get_games_by_type(game_type):
    """Получить игры по типу"""
    if game_type == 'indie':
        games = IndieGame.query.all()
    elif game_type == 'aaa':
        games = AAAGame.query.all()
    elif game_type == 'mobile':
        games = MobileGame.query.all()
    else:
        return jsonify({
            'success': False,
            'error': 'Неверный тип игры. Допустимые: indie, aaa, mobile'
        }), 400
    
    return jsonify({
        'success': True,
        'count': len(games),
        'type': game_type,
        'games': [game_to_dict(g) for g in games]
    })

@api_bp.route('/statistics', methods=['GET'])
def get_statistics_api():
    """Получить статистику"""
    from app.utils import get_statistics
    stats = get_statistics()
    return jsonify({
        'success': True,
        'statistics': stats
    })

@api_bp.route('/search', methods=['GET'])
def search_games():
    """Поиск игр по названию"""
    query = request.args.get('q', '')
    if not query:
        return jsonify({
            'success': False,
            'error': 'Параметр q обязателен'
        }), 400
    
    games = Game.query.filter(Game.title.ilike(f'%{query}%')).all()
    
    return jsonify({
        'success': True,
        'query': query,
        'count': len(games),
        'games': [game_to_dict(g) for g in games]
    })