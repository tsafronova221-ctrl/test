#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Qt6 клиент для библиотеки видеоигр
Взаимодействует с REST API из лабораторной работы 4
"""

import sys
import json
from typing import List, Dict, Optional, Any
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QLineEdit, QTextEdit, QTableWidget, QTableWidgetItem,
    QComboBox, QSpinBox, QDoubleSpinBox, QCheckBox, QDialog, QDialogButtonBox,
    QFormLayout, QGroupBox, QMessageBox, QTabWidget, QHeaderView, QFrame,
    QScrollArea, QSplitter, QToolBar, QStatusBar, QSystemTrayIcon
)
from PyQt6.QtCore import Qt, QUrl, pyqtSignal, QThread
from PyQt6.QtGui import QFont, QIcon, QColor, QPalette, QAction, QActionGroup
from PyQt6.QtNetwork import QNetworkAccessManager, QNetworkRequest, QNetworkReply
import urllib.request
import urllib.error


class GameAPIClient:
    """Клиент для REST API библиотеки видеоигр"""
    
    def __init__(self, base_url: str = "http://localhost:5090/api"):
        self.base_url = base_url.rstrip('/')
    
    def _make_request(self, endpoint: str, method: str = "GET", data: dict = None) -> dict:
        """Выполнение HTTP запроса"""
        url = f"{self.base_url}{endpoint}"
        headers = {"Content-Type": "application/json"}
        
        try:
            if data is not None:
                req_data = json.dumps(data).encode('utf-8')
                req = urllib.request.Request(url, data=req_data, headers=headers, method=method)
            else:
                req = urllib.request.Request(url, headers=headers, method=method)
            
            with urllib.request.urlopen(req, timeout=10) as response:
                return json.loads(response.read().decode('utf-8'))
        except urllib.error.HTTPError as e:
            try:
                error_data = json.loads(e.read().decode('utf-8'))
                raise Exception(f"API Error ({e.code}): {error_data.get('error', 'Неизвестная ошибка')}")
            except:
                raise Exception(f"API Error ({e.code}): {e.reason}")
        except urllib.error.URLError as e:
            raise Exception(f"Ошибка соединения: {e.reason}")
        except Exception as e:
            raise Exception(f"Ошибка: {str(e)}")
    
    # ==================== GET запросы ====================
    
    def get_all_games(self) -> List[Dict[str, Any]]:
        """Получить все игры"""
        data = self._make_request("/games")
        return data.get('games', [])
    
    def get_game(self, game_id: int) -> Dict[str, Any]:
        """Получить игру по ID"""
        data = self._make_request(f"/games/{game_id}")
        return data.get('game', {})
    
    def get_games_by_type(self, game_type: str) -> List[Dict[str, Any]]:
        """Получить игры по типу"""
        data = self._make_request(f"/games/type/{game_type}")
        return data.get('games', [])
    
    def search_games(self, query: str) -> List[Dict[str, Any]]:
        """Поиск игр по названию"""
        data = self._make_request(f"/search?q={query}")
        return data.get('games', [])
    
    def get_statistics(self) -> Dict[str, Any]:
        """Получить статистику"""
        data = self._make_request("/statistics")
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
        return self._make_request("/games", "POST", data)
    
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
        return self._make_request("/games", "POST", data)
    
    def create_mobile_game(self, title: str, developer: str, year: int,
                          price: float, is_free: bool, microtransactions: bool) -> Dict[str, Any]:
        """Создать мобильную игру"""
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
        return self._make_request("/games", "POST", data)
    
    # ==================== PUT/PATCH запросы ====================
    
    def update_game(self, game_id: int, **kwargs) -> Dict[str, Any]:
        """Полное обновление игры"""
        return self._make_request(f"/games/{game_id}", "PUT", kwargs)
    
    def patch_game(self, game_id: int, **kwargs) -> Dict[str, Any]:
        """Частичное обновление игры"""
        return self._make_request(f"/games/{game_id}", "PATCH", kwargs)
    
    # ==================== DELETE запросы ====================
    
    def delete_game(self, game_id: int) -> Dict[str, Any]:
        """Удалить игру"""
        return self._make_request(f"/games/{game_id}", "DELETE")


class GameDialog(QDialog):
    """Диалог для добавления/редактирования игры"""
    
    def __init__(self, parent=None, game: dict = None, mode: str = "add"):
        super().__init__(parent)
        self.game = game
        self.mode = mode  # "add" или "edit"
        self.is_full_edit = mode == "full_edit"
        self.setup_ui()
    
    def setup_ui(self):
        self.setWindowTitle("Добавление игры" if self.mode == "add" else "Редактирование игры")
        self.setMinimumWidth(500)
        
        layout = QVBoxLayout(self)
        
        # Тип игры
        type_group = QGroupBox("Тип игры")
        type_layout = QFormLayout(type_group)
        self.type_combo = QComboBox()
        self.type_combo.addItems(["Инди-игра", "AAA-игра", "Мобильная игра"])
        type_layout.addRow("Тип:", self.type_combo)
        layout.addWidget(type_group)
        
        # Основные поля
        main_group = QGroupBox("Основная информация")
        main_layout = QFormLayout(main_group)
        
        self.title_edit = QLineEdit()
        self.developer_edit = QLineEdit()
        self.year_spin = QSpinBox()
        self.year_spin.setRange(1970, 2026)
        self.price_spin = QDoubleSpinBox()
        self.price_spin.setRange(0, 1000)
        self.price_spin.setDecimals(2)
        self.price_spin.setSuffix(" $")
        
        main_layout.addRow("Название:", self.title_edit)
        main_layout.addRow("Разработчик:", self.developer_edit)
        main_layout.addRow("Год выпуска:", self.year_spin)
        main_layout.addRow("Цена:", self.price_spin)
        
        layout.addWidget(main_group)
        
        # Специфичные поля для разных типов
        self.indie_group = QGroupBox("Параметры инди-игры")
        indie_layout = QFormLayout(self.indie_group)
        self.team_size_spin = QSpinBox()
        self.team_size_spin.setRange(1, 1000)
        self.engine_edit = QLineEdit()
        indie_layout.addRow("Размер команды:", self.team_size_spin)
        indie_layout.addRow("Игровой движок:", self.engine_edit)
        layout.addWidget(self.indie_group)
        
        self.aaa_group = QGroupBox("Параметры AAA-игры")
        aaa_layout = QFormLayout(self.aaa_group)
        self.budget_spin = QDoubleSpinBox()
        self.budget_spin.setRange(1, 10000)
        self.budget_spin.setValue(1)
        self.budget_spin.setDecimals(2)
        self.budget_spin.setSuffix(" млн $")
        self.platforms_edit = QLineEdit()
        self.platforms_edit.setPlaceholderText("PC, PlayStation 5, Xbox Series X (необязательно)")
        aaa_layout.addRow("Бюджет:", self.budget_spin)
        aaa_layout.addRow("Платформы:", self.platforms_edit)
        layout.addWidget(self.aaa_group)
        
        self.mobile_group = QGroupBox("Параметры мобильной игры")
        mobile_layout = QFormLayout(self.mobile_group)
        self.is_free_check = QCheckBox("Бесплатная игра")
        self.microtrans_check = QCheckBox("Есть микротранзакции")
        mobile_layout.addRow(self.is_free_check)
        mobile_layout.addRow(self.microtrans_check)
        layout.addWidget(self.mobile_group)
        
        # Кнопки
        button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        button_box.accepted.connect(self.validate_and_accept)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)
        
        # Подключение сигналов
        self.type_combo.currentIndexChanged.connect(self.on_type_changed)
        self.is_free_check.stateChanged.connect(self.on_free_changed)
        
        # Заполнение данными если редактируем
        if self.game:
            self.populate_data()
        
        # Показать нужную группу
        self.on_type_changed()
    
    def on_type_changed(self):
        """Показать поля для выбранного типа игры"""
        game_type = self.type_combo.currentIndex()
        self.indie_group.setVisible(game_type == 0)
        self.aaa_group.setVisible(game_type == 1)
        self.mobile_group.setVisible(game_type == 2)
        
        # Показывать/скрывать цену для мобильных игр
        if game_type == 2:
            self.price_spin.setEnabled(not self.is_free_check.isChecked())
    
    def on_free_changed(self):
        """Обработка изменения статуса бесплатности"""
        self.price_spin.setEnabled(not self.is_free_check.isChecked())
        if self.is_free_check.isChecked():
            self.price_spin.setValue(0)
    
    def validate_and_accept(self):
        """Валидация данных перед закрытием диалога"""
        game_type = ['indie', 'aaa', 'mobile'][self.type_combo.currentIndex()]
        
        # Проверка обязательных полей
        if not self.title_edit.text().strip():
            QMessageBox.warning(self, "Ошибка", "Название игры обязательно!")
            return
        if not self.developer_edit.text().strip():
            QMessageBox.warning(self, "Ошибка", "Разработчик обязателен!")
            return
        
        # Проверка специфичных полей для каждого типа
        if game_type == 'indie':
            if not self.engine_edit.text().strip():
                QMessageBox.warning(self, "Ошибка", "Игровой движок обязателен для инди-игры!")
                return
        elif game_type == 'aaa':
            # Платформы теперь необязательны, проверяем только бюджет
            if self.budget_spin.value() < 1:
                QMessageBox.warning(self, "Ошибка", "Бюджет должен быть не менее 1 млн $!")
                return
        
        self.accept()
    
    def populate_data(self):
        """Заполнить форму данными игры"""
        self.title_edit.setText(self.game.get('title', ''))
        self.developer_edit.setText(self.game.get('developer', ''))
        self.year_spin.setValue(self.game.get('year', 2020))
        self.price_spin.setValue(self.game.get('price', 0))
        
        game_type = self.game.get('type', 'indie')
        if game_type == 'indie':
            self.type_combo.setCurrentIndex(0)
            self.team_size_spin.setValue(self.game.get('team_size', 1))
            self.engine_edit.setText(self.game.get('engine', ''))
        elif game_type == 'aaa':
            self.type_combo.setCurrentIndex(1)
            self.budget_spin.setValue(self.game.get('budget', 0))
            platforms = self.game.get('platforms', [])
            self.platforms_edit.setText(', '.join(platforms) if isinstance(platforms, list) else platforms)
        elif game_type == 'mobile':
            self.type_combo.setCurrentIndex(2)
            self.is_free_check.setChecked(self.game.get('is_free', False))
            self.microtrans_check.setChecked(self.game.get('microtransactions', False))
    
    def get_data(self) -> dict:
        """Получить данные из формы"""
        game_type = ['indie', 'aaa', 'mobile'][self.type_combo.currentIndex()]
        
        data = {
            'type': game_type,
            'title': self.title_edit.text().strip(),
            'developer': self.developer_edit.text().strip(),
            'year': self.year_spin.value(),
            'price': self.price_spin.value()
        }
        
        if game_type == 'indie':
            data['team_size'] = self.team_size_spin.value()
            engine = self.engine_edit.text().strip()
            if engine:
                data['engine'] = engine
            else:
                data['engine'] = 'Unknown'
        elif game_type == 'aaa':
            data['budget'] = self.budget_spin.value()
            platforms_text = self.platforms_edit.text().strip()
            if platforms_text:
                data['platforms'] = [p.strip() for p in platforms_text.split(',')]
            else:
                data['platforms'] = []  # Платформы необязательны
        elif game_type == 'mobile':
            data['is_free'] = self.is_free_check.isChecked()
            data['microtransactions'] = self.microtrans_check.isChecked()
            # Если игра не бесплатная, цена должна быть > 0
            if not data['is_free'] and data['price'] <= 0:
                data['price'] = 0.99  # Цена по умолчанию для платной мобильной игры
        
        return data


class StatisticsDialog(QDialog):
    """Диалог отображения статистики"""
    
    def __init__(self, parent=None, stats: dict = None):
        super().__init__(parent)
        self.stats = stats or {}
        self.setup_ui()
    
    def setup_ui(self):
        self.setWindowTitle("Статистика библиотеки")
        self.setMinimumWidth(400)
        
        layout = QVBoxLayout(self)
        
        # Общая статистика
        total_group = QGroupBox("Общая статистика")
        total_layout = QFormLayout(total_group)
        
        total_games = self.stats.get('total_games', 0)
        total_price = self.stats.get('total_price', 0)
        avg_price = self.stats.get('avg_price', 0)
        year_min = self.stats.get('year_min', 0)
        year_max = self.stats.get('year_max', 0)
        
        total_layout.addRow("Всего игр:", QLabel(str(total_games)))
        total_layout.addRow("Общая стоимость:", QLabel(f"${total_price:.2f}"))
        total_layout.addRow("Средняя цена:", QLabel(f"${avg_price:.2f}"))
        total_layout.addRow("Диапазон годов:", QLabel(f"{year_min} - {year_max}"))
        
        layout.addWidget(total_group)
        
        # Распределение по типам
        type_group = QGroupBox("Распределение по типам")
        type_layout = QVBoxLayout(type_group)
        
        stats_dict = self.stats.get('stats', {})
        for type_name, count in stats_dict.items():
            if count > 0 and total_games > 0:
                percent = (count / total_games) * 100
                bar_length = int(percent / 5)
                bar = "█" * bar_length
                label = QLabel(f"{type_name}: {count} ({percent:.1f}%)")
                bar_label = QLabel(bar)
                bar_label.setStyleSheet("color: #4CAF50; font-weight: bold;")
                type_layout.addWidget(label)
                type_layout.addWidget(bar_label)
        
        layout.addWidget(type_group)
        
        # Кнопка закрытия
        close_btn = QPushButton("Закрыть")
        close_btn.clicked.connect(self.accept)
        layout.addWidget(close_btn)


class MainWindow(QMainWindow):
    """Главное окно приложения"""
    
    def __init__(self):
        super().__init__()
        self.api = GameAPIClient("http://localhost:5090/api")
        self.current_games: List[Dict] = []
        self.selected_game_id: Optional[int] = None
        self.setup_ui()
        self.load_games()
    
    def setup_ui(self):
        self.setWindowTitle("🎮 Картотека видеоигр")
        self.setMinimumSize(1200, 800)
        self.setStyleSheet(self.get_stylesheet())
        
        # Центральная виджет
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        main_layout.setSpacing(10)
        main_layout.setContentsMargins(15, 15, 15, 15)
        
        # Заголовок
        header_frame = QFrame()
        header_frame.setObjectName("headerFrame")
        header_layout = QHBoxLayout(header_frame)
        
        title_label = QLabel("🎮 Картотека видеоигр")
        title_label.setObjectName("mainTitle")
        header_layout.addWidget(title_label)
        
        header_layout.addStretch()
        
        # Поиск
        search_layout = QHBoxLayout()
        self.search_edit = QLineEdit()
        self.search_edit.setPlaceholderText("🔍 Поиск по названию...")
        self.search_edit.setObjectName("searchEdit")
        self.search_edit.returnPressed.connect(self.search_games)
        
        search_btn = QPushButton("🔍")
        search_btn.setObjectName("searchButton")
        search_btn.clicked.connect(self.search_games)
        
        search_layout.addWidget(self.search_edit)
        search_layout.addWidget(search_btn)
        header_layout.addLayout(search_layout)
        
        main_layout.addWidget(header_frame)
        
        # Панель инструментов
        toolbar_frame = QFrame()
        toolbar_frame.setObjectName("toolbarFrame")
        toolbar_layout = QHBoxLayout(toolbar_frame)
        
        # Кнопки основных действий
        self.btn_all = QPushButton("📋 Все игры")
        self.btn_all.setObjectName("primaryButton")
        self.btn_all.clicked.connect(self.load_games)
        
        self.btn_add = QPushButton("➕ Добавить")
        self.btn_add.setObjectName("successButton")
        self.btn_add.clicked.connect(self.add_game)
        
        self.btn_edit = QPushButton("✏️ Редактировать")
        self.btn_edit.setObjectName("warningButton")
        self.btn_edit.clicked.connect(self.edit_game)
        
        self.btn_delete = QPushButton("🗑️ Удалить")
        self.btn_delete.setObjectName("dangerButton")
        self.btn_delete.clicked.connect(self.delete_game)
        
        self.btn_stats = QPushButton("📊 Статистика")
        self.btn_stats.setObjectName("infoButton")
        self.btn_stats.clicked.connect(self.show_statistics)
        
        # Кнопка обновить
        self.btn_refresh = QPushButton("🔄 Обновить")
        self.btn_refresh.setObjectName("primaryButton")
        self.btn_refresh.clicked.connect(self.load_games)
        
        toolbar_layout.addWidget(self.btn_all)
        toolbar_layout.addWidget(self.btn_add)
        toolbar_layout.addWidget(self.btn_edit)
        toolbar_layout.addWidget(self.btn_delete)
        toolbar_layout.addWidget(self.btn_stats)
        toolbar_layout.addWidget(self.btn_refresh)
        
        toolbar_layout.addStretch()
        
        # Фильтр по типу
        filter_label = QLabel("Фильтр:")
        self.filter_combo = QComboBox()
        self.filter_combo.addItems(["Все типы", "Инди-игры", "AAA-игры", "Мобильные игры"])
        self.filter_combo.setObjectName("filterCombo")
        self.filter_combo.currentIndexChanged.connect(self.filter_games)
        
        toolbar_layout.addWidget(filter_label)
        toolbar_layout.addWidget(self.filter_combo)
        
        main_layout.addWidget(toolbar_frame)
        
        # Таблица игр
        self.table = QTableWidget()
        self.table.setObjectName("gamesTable")
        self.table.setColumnCount(7)
        self.table.setHorizontalHeaderLabels(["ID", "Тип", "Название", "Разработчик", "Год", "Цена", "Детали"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table.verticalHeader().setVisible(False)  # Скрываем заголовок строк (слева)
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.setSelectionMode(QTableWidget.SelectionMode.SingleSelection)
        self.table.itemSelectionChanged.connect(self.on_selection_changed)
        self.table.setAlternatingRowColors(False)  # Отключаем встроенные чередующиеся цвета, используем CSS
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.table.mousePressEvent = self.on_table_click
        
        main_layout.addWidget(self.table)
        
        # Строка состояния
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("Готово")
    
    def get_stylesheet(self) -> str:
        """Возвращает таблицу стилей для приложения"""
        return """
            QMainWindow {
                background-color: #1a1a2e;
            }
            
            QWidget {
                font-family: 'Segoe UI', Arial, sans-serif;
                font-size: 14px;
                color: #eee;
            }
            
            #headerFrame {
                background-color: #16213e;
                padding: 15px;
                border-radius: 10px;
            }
            
            #mainTitle {
                font-size: 28px;
                font-weight: bold;
                color: #00d9ff;
                padding: 5px;
            }
            
            #searchEdit {
                background-color: #0f3460;
                border: 2px solid #00d9ff;
                border-radius: 8px;
                padding: 8px 15px;
                min-width: 250px;
                color: #fff;
                selection-background-color: #00d9ff;
                selection-color: #000;
            }
            
            #searchEdit:focus {
                border-color: #e94560;
            }
            
            #searchButton {
                background-color: #00d9ff;
                border: none;
                border-radius: 8px;
                padding: 8px 15px;
                font-weight: bold;
                min-width: 50px;
            }
            
            #searchButton:hover {
                background-color: #00b8d9;
            }
            
            #toolbarFrame {
                background-color: #16213e;
                padding: 10px;
                border-radius: 10px;
            }
            
            QPushButton {
                background-color: #0f3460;
                border: 2px solid #00d9ff;
                border-radius: 8px;
                padding: 10px 20px;
                font-weight: bold;
                min-width: 120px;
            }
            
            QPushButton:hover {
                background-color: #00d9ff;
                color: #000;
            }
            
            QPushButton:pressed {
                background-color: #00b8d9;
            }
            
            #primaryButton {
                background-color: #00d9ff;
                color: #000;
            }
            
            #successButton {
                background-color: #4CAF50;
                border-color: #4CAF50;
                color: #fff;
            }
            
            #successButton:hover {
                background-color: #45a049;
            }
            
            #warningButton {
                background-color: #ff9800;
                border-color: #ff9800;
                color: #fff;
            }
            
            #warningButton:hover {
                background-color: #f57c00;
            }
            
            #dangerButton {
                background-color: #e94560;
                border-color: #e94560;
                color: #fff;
            }
            
            #dangerButton:hover {
                background-color: #c73e54;
            }
            
            #infoButton {
                background-color: #2196F3;
                border-color: #2196F3;
                color: #fff;
            }
            
            #infoButton:hover {
                background-color: #1976D2;
            }
            
            #filterCombo {
                background-color: #0f3460;
                border: 2px solid #00d9ff;
                border-radius: 8px;
                padding: 8px 15px;
                min-width: 150px;
            }
            
            #filterCombo::drop-down {
                width: 30px;
            }
            
            #filterCombo QAbstractItemView {
                background-color: #16213e;
                border: 2px solid #00d9ff;
                selection-background-color: #00d9ff;
                selection-color: #000;
            }
            
            #filterCombo QAbstractItemView::item {
                padding: 8px;
                background-color: #16213e;
                color: #eee;
            }
            
            #filterCombo QAbstractItemView::item:hover {
                background-color: #0f3460;
            }
            
            #filterCombo QAbstractItemView::item:selected {
                background-color: #00d9ff;
                color: #000;
            }
            
            #gamesTable {
                background-color: #0f3460;
                border: 2px solid #16213e;
                border-radius: 10px;
                gridline-color: #16213e;
                selection-background-color: transparent;
            }
            
            #gamesTable::item {
                padding: 8px;
                border-bottom: 1px solid #16213e;
                background-color: transparent;
            }
            
            #gamesTable::item:selected {
                background-color: #00d9ff;
                color: #000;
            }
            
            #gamesTable::item:hover {
                background-color: #16213e;
            }
            
            #gamesTable::item:nth-child(odd) {
                background-color: #0a2a4a;
            }
            
            #gamesTable::item:nth-child(even) {
                background-color: #0f3460;
            }
            
            #gamesTable QHeaderView::section {
                background-color: #16213e;
                color: #00d9ff;
                padding: 10px;
                border: none;
                font-weight: bold;
                font-size: 14px;
            }
            
            QGroupBox {
                font-weight: bold;
                border: 2px solid #00d9ff;
                border-radius: 8px;
                margin-top: 15px;
                padding-top: 15px;
                background-color: #16213e;
            }
            
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 15px;
                padding: 0 10px;
                color: #00d9ff;
            }
            
            QLabel {
                color: #eee;
            }
            
            QLineEdit, QSpinBox, QDoubleSpinBox {
                background-color: #0f3460;
                border: 2px solid #00d9ff;
                border-radius: 6px;
                padding: 8px;
                color: #fff;
                selection-background-color: #00d9ff;
                selection-color: #000;
            }
            
            QLineEdit:focus, QSpinBox:focus, QDoubleSpinBox:focus {
                border-color: #e94560;
            }
            
            QComboBox {
                background-color: #0f3460;
                border: 2px solid #00d9ff;
                border-radius: 6px;
                padding: 8px;
                color: #fff;
                min-width: 120px;
            }
            
            QComboBox::drop-down {
                width: 30px;
                border: none;
            }
            
            QComboBox::down-arrow {
                image: none;
                border-left: 5px solid transparent;
                border-right: 5px solid transparent;
                border-top: 8px solid #00d9ff;
                margin-right: 10px;
            }
            
            QComboBox QAbstractItemView {
                background-color: #16213e;
                border: 2px solid #00d9ff;
                selection-background-color: #00d9ff;
                selection-color: #000;
                outline: none;
                padding: 0px;
            }
            
            QComboBox QAbstractItemView::item {
                padding: 8px;
                background-color: #16213e;
                color: #eee;
                border: none;
            }
            
            QComboBox QAbstractItemView::item:hover {
                background-color: #0f3460;
            }
            
            QComboBox QAbstractItemView::item:selected {
                background-color: #00d9ff;
                color: #000;
            }
            
            QCheckBox {
                spacing: 10px;
                color: #eee;
            }
            
            QCheckBox::indicator {
                width: 20px;
                height: 20px;
                border-radius: 4px;
                border: 2px solid #00d9ff;
                background-color: #0f3460;
            }
            
            QCheckBox::indicator:checked {
                background-color: #4CAF50;
                border-color: #4CAF50;
            }
            
            QDialog {
                background-color: #1a1a2e;
            }
            
            QDialogButtonBox QPushButton {
                min-width: 80px;
            }
            
            QMessageBox {
                background-color: #1a1a2e;
            }
            
            QMessageBox QLabel {
                color: #eee;
            }
            
            QMessageBox QPushButton {
                min-width: 80px;
                padding: 8px 20px;
            }
            
            QScrollBar:vertical {
                background-color: #16213e;
                width: 12px;
                border-radius: 6px;
            }
            
            QScrollBar::handle:vertical {
                background-color: #00d9ff;
                border-radius: 6px;
                min-height: 30px;
            }
            
            QScrollBar::handle:vertical:hover {
                background-color: #00b8d9;
            }
            
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                height: 0px;
            }
            
            QStatusBar {
                background-color: #16213e;
                color: #00d9ff;
                padding: 5px;
            }
        """
    
    def load_games(self):
        """Загрузить все игры"""
        self.status_bar.showMessage("Загрузка игр...")
        try:
            self.current_games = self.api.get_all_games()
            self.populate_table()
            self.status_bar.showMessage(f"Загружено игр: {len(self.current_games)}")
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", str(e))
            self.status_bar.showMessage("Ошибка загрузки")
    
    def populate_table(self, games: List[Dict] = None):
        """Заполнить таблицу играми"""
        if games is None:
            games = self.current_games
        
        self.table.setRowCount(len(games))
        
        type_icons = {'indie': '🎨', 'aaa': '💰', 'mobile': '📱'}
        type_names = {'indie': 'Инди', 'aaa': 'AAA', 'mobile': 'Мобильная'}
        
        for row, game in enumerate(games):
            game_id = game.get('id', 0)
            game_type = game.get('type', 'unknown')
            
            self.table.setItem(row, 0, QTableWidgetItem(str(game_id)))
            self.table.setItem(row, 1, QTableWidgetItem(f"{type_icons.get(game_type, '')} {type_names.get(game_type, game_type)}"))
            self.table.setItem(row, 2, QTableWidgetItem(game.get('title', '')))
            self.table.setItem(row, 3, QTableWidgetItem(game.get('developer', '')))
            self.table.setItem(row, 4, QTableWidgetItem(str(game.get('year', ''))))
            
            price = game.get('price', 0)
            if game_type == 'mobile' and game.get('is_free'):
                price_str = "Бесплатно"
            else:
                price_str = f"${price:.2f}"
            self.table.setItem(row, 5, QTableWidgetItem(price_str))
            
            # Детали в зависимости от типа
            details = ""
            if game_type == 'indie':
                details = f"Команда: {game.get('team_size', '')}, Движок: {game.get('engine', '')}"
            elif game_type == 'aaa':
                platforms = ', '.join(game.get('platforms', []))
                details = f"Бюджет: ${game.get('budget', 0):.1f}M, Платформы: {platforms}"
            elif game_type == 'mobile':
                micro = "✅ Микротранзакции" if game.get('microtransactions') else "❌ Без микротранзакций"
                details = micro
            
            self.table.setItem(row, 6, QTableWidgetItem(details))
    
    def on_selection_changed(self):
        """Обработка выбора строки в таблице"""
        selected_rows = self.table.selectedItems()
        if selected_rows:
            row = selected_rows[0].row()
            if row < len(self.current_games):
                self.selected_game_id = self.current_games[row].get('id')
        else:
            self.selected_game_id = None
    
    def on_table_click(self, event):
        """Обработка клика по таблице - снятие выделения при клике на пустую область"""
        item = self.table.itemAt(event.pos())
        if item is None:
            self.table.clearSelection()
            self.selected_game_id = None
        else:
            # Вызываем оригинальный обработчик
            QTableWidget.mousePressEvent(self.table, event)
    
    def filter_games(self):
        """Фильтрация игр по типу"""
        filter_index = self.filter_combo.currentIndex()
        
        if filter_index == 0:  # Все типы
            self.populate_table()
        else:
            type_map = {1: 'indie', 2: 'aaa', 3: 'mobile'}
            game_type = type_map.get(filter_index)
            if game_type:
                try:
                    filtered_games = self.api.get_games_by_type(game_type)
                    self.populate_table(filtered_games)
                    self.status_bar.showMessage(f"Найдено игр: {len(filtered_games)}")
                except Exception as e:
                    QMessageBox.critical(self, "Ошибка", str(e))
    
    def search_games(self):
        """Поиск игр по названию"""
        query = self.search_edit.text().strip()
        if not query:
            self.load_games()
            return
        
        try:
            results = self.api.search_games(query)
            self.populate_table(results)
            self.status_bar.showMessage(f"Найдено игр: {len(results)}")
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", str(e))
    
    def add_game(self):
        """Добавить новую игру"""
        dialog = GameDialog(self, mode="add")
        if dialog.exec() == QDialog.DialogCode.Accepted:
            data = dialog.get_data()
            
            # Проверка обязательных полей
            if not data['title'] or not data['developer']:
                QMessageBox.warning(self, "Ошибка", "Название и разработчик обязательны!")
                return
            
            try:
                if data['type'] == 'indie':
                    result = self.api.create_indie_game(
                        data['title'], data['developer'], data['year'],
                        data['price'], data['team_size'], data['engine']
                    )
                elif data['type'] == 'aaa':
                    result = self.api.create_aaa_game(
                        data['title'], data['developer'], data['year'],
                        data['price'], data['budget'], data.get('platforms', [])
                    )
                elif data['type'] == 'mobile':
                    result = self.api.create_mobile_game(
                        data['title'], data['developer'], data['year'],
                        data['price'], data['is_free'], data['microtransactions']
                    )
                
                QMessageBox.information(self, "Успех", result.get('message', 'Игра добавлена!'))
                self.load_games()
            except Exception as e:
                QMessageBox.critical(self, "Ошибка", str(e))
    
    def edit_game(self):
        """Редактировать выбранную игру"""
        if self.selected_game_id is None:
            QMessageBox.warning(self, "Предупреждение", "Выберите игру для редактирования!")
            return
        
        try:
            game = self.api.get_game(self.selected_game_id)
            if not game:
                QMessageBox.warning(self, "Ошибка", "Игра не найдена!")
                return
            
            dialog = GameDialog(self, game=game, mode="full_edit")
            if dialog.exec() == QDialog.DialogCode.Accepted:
                data = dialog.get_data()
                del data['type']  # Нельзя изменить тип
                
                result = self.api.update_game(self.selected_game_id, **data)
                QMessageBox.information(self, "Успех", result.get('message', 'Игра обновлена!'))
                self.load_games()
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", str(e))
    
    def delete_game(self):
        """Удалить выбранную игру"""
        if self.selected_game_id is None:
            QMessageBox.warning(self, "Предупреждение", "Выберите игру для удаления!")
            return
        
        try:
            game = self.api.get_game(self.selected_game_id)
            if not game:
                QMessageBox.warning(self, "Ошибка", "Игра не найдена!")
                return
            
            reply = QMessageBox.question(
                self, "Подтверждение",
                f"Вы уверены, что хотите удалить игру \"{game.get('title', '')}\"?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            
            if reply == QMessageBox.StandardButton.Yes:
                result = self.api.delete_game(self.selected_game_id)
                QMessageBox.information(self, "Успех", result.get('message', 'Игра удалена!'))
                self.load_games()
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", str(e))
    
    def show_statistics(self):
        """Показать статистику"""
        try:
            stats = self.api.get_statistics()
            dialog = StatisticsDialog(self, stats)
            dialog.exec()
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", str(e))


def main():
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    
    window = MainWindow()
    window.show()
    
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
