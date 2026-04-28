from flask import render_template, redirect, url_for, flash, request
from app import db
from app.models import Game, IndieGame, AAAGame, MobileGame
from app.forms import IndieGameForm, AAAGameForm, MobileGameForm
from app.utils import get_statistics, list_saved_files
import os
import pickle
from datetime import datetime
from sqlalchemy import text

def init_app(app):
    
    @app.route('/')
    def index():
        return render_template('index.html')
    
    @app.route('/games')
    def games_list():
        games = Game.query.order_by(Game.created_at.desc()).all()
        return render_template('games.html', games=games, count=len(games))
    
    @app.route('/game/add')
    def add_game_select():
        return render_template('select_game_type.html')
    
    @app.route('/game/add/<game_type>', methods=['GET', 'POST'])
    def add_game(game_type):
        form = None
        
        if game_type == 'indie':
            form = IndieGameForm()
        elif game_type == 'aaa':
            form = AAAGameForm()
        elif game_type == 'mobile':
            form = MobileGameForm()
        else:
            flash('❌ Неверный тип игры!', 'error')
            return redirect(url_for('add_game_select'))
        
        if form.validate_on_submit():
            try:
                if game_type == 'indie':
                    game = IndieGame(
                        title=form.title.data,
                        developer=form.developer.data,
                        year=form.year.data,
                        price=form.price.data,
                        team_size=form.team_size.data,
                        engine=form.engine.data
                    )
                elif game_type == 'aaa':
                    platforms = [p.strip() for p in form.platforms.data.split(',')] if form.platforms.data else []
                    game = AAAGame(
                        title=form.title.data,
                        developer=form.developer.data,
                        year=form.year.data,
                        price=form.price.data,
                        budget=form.budget.data,
                        platforms=platforms
                    )
                elif game_type == 'mobile':
                    # Для мобильных игр: если is_free=True, цена принудительно 0
                    if form.is_free.data:
                        price = 0.0
                    else:
                        # Для платных игр цена обязательна
                        if not form.price.data or form.price.data <= 0:
                            flash('❌ Для платной игры необходимо указать цену!', 'error')
                            return render_template('game_form.html', form=form, game_type=game_type, action='add')
                        price = form.price.data
                    
                    game = MobileGame(
                        title=form.title.data,
                        developer=form.developer.data,
                        year=form.year.data,
                        price=price,
                        is_free=form.is_free.data,
                        microtransactions=form.microtransactions.data
                    )
                
                db.session.add(game)
                db.session.commit()
                flash(f'✅ Игра "{game.title}" успешно добавлена!', 'success')
                return redirect(url_for('games_list'))
                
            except Exception as e:
                db.session.rollback()
                flash(f'❌ Ошибка при добавлении игры: {str(e)}', 'error')
        
        return render_template('game_form.html', form=form, game_type=game_type, action='add')
    
    @app.route('/game/edit/<int:game_id>', methods=['GET', 'POST'])
    def edit_game(game_id):
        game = Game.query.get_or_404(game_id)
        
        if isinstance(game, IndieGame):
            form = IndieGameForm(obj=game)
            game_type = 'indie'
        elif isinstance(game, AAAGame):
            form = AAAGameForm(obj=game)
            if game.platforms:
                form.platforms.data = ', '.join(game.platforms)
            game_type = 'aaa'
        elif isinstance(game, MobileGame):
            form = MobileGameForm(obj=game)
            game_type = 'mobile'
        else:
            flash('❌ Неизвестный тип игры!', 'error')
            return redirect(url_for('games_list'))
        
        if form.validate_on_submit():
            try:
                game.title = form.title.data
                game.developer = form.developer.data
                game.year = form.year.data
                
                # Для мобильных игр обрабатываем цену особым образом
                if isinstance(game, MobileGame):
                    game.is_free = form.is_free.data
                    # Если игра бесплатная, цена 0
                    if game.is_free:
                        game.price = 0.0
                    else:
                        # Для платных игр цена обязательна
                        if not form.price.data or form.price.data <= 0:
                            flash('❌ Для платной игры необходимо указать цену!', 'error')
                            return render_template('game_form.html', form=form, game_type=game_type, action='edit', game=game)
                        game.price = form.price.data
                else:
                    game.price = form.price.data
                
                if isinstance(game, IndieGame):
                    game.team_size = form.team_size.data
                    game.engine = form.engine.data
                elif isinstance(game, AAAGame):
                    game.budget = form.budget.data
                    platforms = [p.strip() for p in form.platforms.data.split(',')] if form.platforms.data else []
                    game.platforms = platforms
                elif isinstance(game, MobileGame):
                    game.microtransactions = form.microtransactions.data
                
                db.session.commit()
                flash(f'✅ Игра "{game.title}" успешно обновлена!', 'success')
                return redirect(url_for('games_list'))
                
            except Exception as e:
                db.session.rollback()
                flash(f'❌ Ошибка при редактировании: {str(e)}', 'error')
        
        return render_template('game_form.html', form=form, game_type=game_type, action='edit', game=game)
    
    @app.route('/game/delete/<int:game_id>')
    def delete_game(game_id):
        game = Game.query.get_or_404(game_id)
        try:
            title = game.title
            db.session.delete(game)
            db.session.commit()
            flash(f'🗑️ Игра "{title}" удалена!', 'success')
        except Exception as e:
            db.session.rollback()
            flash(f'❌ Ошибка при удалении: {str(e)}', 'error')
        
        return redirect(url_for('games_list'))
    
    @app.route('/statistics')
    def statistics():
        stats = get_statistics()
        return render_template('statistics.html', **stats)
    
    @app.route('/files')
    def files_list():
        files = list_saved_files(app.config['DATA_DIR'])
        return render_template('files.html', files=files)
    
    @app.route('/files/save', methods=['POST'])
    def save_file():
        if Game.query.count() == 0:
            flash('❌ НЕТ ДАННЫХ ДЛЯ СОХРАНЕНИЯ!', 'error')
            return redirect(url_for('files_list'))
        
        format_choice = request.form.get('format', '1')
        custom_filename = request.form.get('filename', '').strip()
        
        if format_choice == '1':
            default_name = 'games.pkl'
        else:
            default_name = 'games.txt'
        
        filename = custom_filename if custom_filename else default_name
        
        if format_choice == '1' and not filename.endswith('.pkl'):
            filename += '.pkl'
        elif format_choice == '2' and not filename.endswith('.txt'):
            filename += '.txt'
        
        filepath = os.path.join(app.config['DATA_DIR'], filename)
        
        games = Game.query.all()
        
        games_data = []
        for game in games:
            if isinstance(game, IndieGame):
                games_data.append({
                    'type': 'indie',
                    'title': game.title,
                    'developer': game.developer,
                    'year': game.year,
                    'price': game.price,
                    'team_size': game.team_size,
                    'engine': game.engine
                })
            elif isinstance(game, AAAGame):
                games_data.append({
                    'type': 'aaa',
                    'title': game.title,
                    'developer': game.developer,
                    'year': game.year,
                    'price': game.price,
                    'budget': game.budget,
                    'platforms': game.platforms
                })
            elif isinstance(game, MobileGame):
                games_data.append({
                    'type': 'mobile',
                    'title': game.title,
                    'developer': game.developer,
                    'year': game.year,
                    'price': game.price,
                    'is_free': game.is_free,
                    'microtransactions': game.microtransactions
                })
        
        try:
            if format_choice == '1':
                with open(filepath, 'wb') as f:
                    pickle.dump(games_data, f)
                flash(f'✅ Данные сохранены в {filename} (папка data)', 'success')
            else:
                with open(filepath, 'w', encoding='utf-8') as f:
                    f.write("=" * 60 + "\n")
                    f.write("БИБЛИОТЕКА ВИДЕОИГР - ЭКСПОРТ\n")
                    f.write("=" * 60 + "\n")
                    f.write(f"Дата: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                    f.write(f"Всего игр: {len(games_data)}\n")
                    f.write("=" * 60 + "\n\n")
                    
                    for i, game in enumerate(games_data, 1):
                        f.write(f"ИГРА #{i}\n")
                        f.write("-" * 40 + "\n")
                        f.write(f"Тип: {game['type']}\n")
                        f.write(f"Название: {game['title']}\n")
                        f.write(f"Разработчик: {game['developer']}\n")
                        f.write(f"Год: {game['year']}\n")
                        f.write(f"Цена: ${game['price']}\n")
                        
                        if game['type'] == 'indie':
                            f.write(f"Команда: {game['team_size']} чел.\n")
                            f.write(f"Движок: {game['engine']}\n")
                        elif game['type'] == 'aaa':
                            f.write(f"Бюджет: ${game['budget']}M\n")
                            f.write(f"Платформы: {', '.join(game['platforms'])}\n")
                        elif game['type'] == 'mobile':
                            f.write(f"Бесплатная: {'Да' if game['is_free'] else 'Нет'}\n")
                            f.write(f"Микротранзакции: {'Да' if game['microtransactions'] else 'Нет'}\n")
                        
                        f.write("\n" + "=" * 40 + "\n\n")
                
                flash(f'✅ Данные экспортированы в {filename} (папка data)', 'success')
        except Exception as e:
            flash(f'❌ Ошибка сохранения: {str(e)}', 'error')
        
        return redirect(url_for('files_list'))
    
    @app.route('/files/load', methods=['POST'])
    def load_file():
        """Загрузка библиотеки из файла (поддерживает объекты и словари)"""
        format_choice = request.form.get('format', '1')
        filename = request.form.get('filename', '').strip()
        confirm = request.form.get('confirm')  # Получаем значение чекбокса
        
        if not filename:
            flash('❌ Введите имя файла!', 'error')
            return redirect(url_for('files_list'))
        
        filepath = os.path.join(app.config['DATA_DIR'], filename)
        
        if not os.path.exists(filepath):
            flash(f'❌ Файл {filename} не найден в папке data!', 'error')
            return redirect(url_for('files_list'))
        
        # Проверка подтверждения для pickle файлов, если в библиотеке есть данные
        if format_choice == '1' and Game.query.count() > 0:
            if not confirm or confirm != 'yes':
                flash('⚠️ Загрузка отменена. Необходимо подтвердить потерю текущих данных!', 'warning')
                return redirect(url_for('files_list'))
        
        if format_choice == '1':
            # Если есть подтверждение и есть данные, очищаем таблицы
            if Game.query.count() > 0:
                try:
                    db.session.execute(text("DELETE FROM indie_games"))
                    db.session.execute(text("DELETE FROM aaa_games"))
                    db.session.execute(text("DELETE FROM mobile_games"))
                    db.session.execute(text("DELETE FROM games"))
                    db.session.commit()
                except Exception as e:
                    db.session.rollback()
                    flash(f'❌ Ошибка при очистке: {str(e)}', 'error')
                    return redirect(url_for('files_list'))
            
            try:
                with open(filepath, 'rb') as f:
                    data = pickle.load(f)
                
                games_data = []
                
                # Универсальная обработка - определяем тип данных
                for item in data:
                    # Если это объект игры (из 1-й или 2-й лабы)
                    if hasattr(item, 'get_type'):
                        game_type = item.get_type()
                        if 'Инди' in game_type:
                            games_data.append({
                                'type': 'indie',
                                'title': item.title,
                                'developer': item.developer,
                                'year': item.year,
                                'price': item.price,
                                'team_size': item.team_size,
                                'engine': item.engine
                            })
                        elif 'AAA' in game_type:
                            games_data.append({
                                'type': 'aaa',
                                'title': item.title,
                                'developer': item.developer,
                                'year': item.year,
                                'price': item.price,
                                'budget': item.budget,
                                'platforms': item.platforms if hasattr(item, 'platforms') else []
                            })
                        elif 'Мобильная' in game_type:
                            games_data.append({
                                'type': 'mobile',
                                'title': item.title,
                                'developer': item.developer,
                                'year': item.year,
                                'price': item.price,
                                'is_free': item.is_free if hasattr(item, 'is_free') else False,
                                'microtransactions': item.microtransactions if hasattr(item, 'microtransactions') else False
                            })
                    
                    # Если это словарь (из сохранения в этой лабе)
                    elif isinstance(item, dict):
                        games_data.append(item)
                    
                    # Если что-то другое
                    else:
                        print(f"⚠️ Неизвестный тип данных: {type(item)}")
                        continue
                
                # Загружаем данные в базу
                for game_data in games_data:
                    if 'id' in game_data:
                        del game_data['id']
                    
                    if game_data['type'] == 'indie':
                        game = IndieGame(
                            title=game_data['title'],
                            developer=game_data['developer'],
                            year=game_data['year'],
                            price=game_data['price'],
                            team_size=game_data['team_size'],
                            engine=game_data['engine']
                        )
                    elif game_data['type'] == 'aaa':
                        game = AAAGame(
                            title=game_data['title'],
                            developer=game_data['developer'],
                            year=game_data['year'],
                            price=game_data['price'],
                            budget=game_data['budget'],
                            platforms=game_data['platforms']
                        )
                    elif game_data['type'] == 'mobile':
                        game = MobileGame(
                            title=game_data['title'],
                            developer=game_data['developer'],
                            year=game_data['year'],
                            price=game_data['price'],
                            is_free=game_data['is_free'],
                            microtransactions=game_data['microtransactions']
                        )
                    else:
                        continue
                    
                    db.session.add(game)
                
                db.session.commit()
                flash(f'✅ Загружено {len(games_data)} игр из {filename}', 'success')
                
            except Exception as e:
                db.session.rollback()
                flash(f'❌ Ошибка загрузки: {str(e)}', 'error')
        
        else:
            # Текстовый файл - только просмотр
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                preview = content[:500] + "..." if len(content) > 500 else content
                flash(f'📄 Содержимое {filename}:\n{preview}', 'info')
                
            except Exception as e:
                flash(f'❌ Ошибка чтения файла: {str(e)}', 'error')
        
        return redirect(url_for('files_list'))
    
    @app.route('/files/delete/<filename>')
    def delete_file(filename):
        filepath = os.path.join(app.config['DATA_DIR'], filename)
        
        try:
            if os.path.exists(filepath):
                os.remove(filepath)
                flash(f'🗑️ Файл {filename} удален из папки data', 'success')
            else:
                flash(f'❌ Файл {filename} не найден в папке data', 'error')
        except Exception as e:
            flash(f'❌ Ошибка удаления: {str(e)}', 'error')
        
        return redirect(url_for('files_list'))
    
    @app.route('/clear')
    def clear_library():
        try:
            count = Game.query.count()
            if count == 0:
                flash('📭 Библиотека уже пуста', 'warning')
            else:
                db.session.execute(text("DELETE FROM indie_games"))
                db.session.execute(text("DELETE FROM aaa_games"))
                db.session.execute(text("DELETE FROM mobile_games"))
                db.session.execute(text("DELETE FROM games"))
                db.session.commit()
                flash(f'🧹 Библиотека очищена. Удалено {count} игр.', 'success')
        except Exception as e:
            db.session.rollback()
            flash(f'❌ Ошибка при очистке: {str(e)}', 'error')
        
        return redirect(url_for('games_list'))
    
    @app.route('/help')
    def help_page():
        return render_template('help.html')