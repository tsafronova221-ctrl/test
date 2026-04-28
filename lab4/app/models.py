from app import db
from datetime import datetime

class Game(db.Model):
    __tablename__ = 'games'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    developer = db.Column(db.String(200), nullable=False)
    year = db.Column(db.Integer, nullable=False)
    price = db.Column(db.Float, nullable=False)
    game_type = db.Column(db.String(50), nullable=False)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    __mapper_args__ = {
        'polymorphic_on': game_type,
        'polymorphic_identity': 'game'
    }

class IndieGame(Game):
    __tablename__ = 'indie_games'
    
    id = db.Column(db.Integer, db.ForeignKey('games.id'), primary_key=True)
    team_size = db.Column(db.Integer, nullable=False)
    engine = db.Column(db.String(100), nullable=False)
    
    __mapper_args__ = {
        'polymorphic_identity': 'indie',
    }

class AAAGame(Game):
    __tablename__ = 'aaa_games'
    
    id = db.Column(db.Integer, db.ForeignKey('games.id'), primary_key=True)
    budget = db.Column(db.Float, nullable=False)
    platforms = db.Column(db.JSON, nullable=False, default=[])
    
    __mapper_args__ = {
        'polymorphic_identity': 'aaa',
    }

class MobileGame(Game):
    __tablename__ = 'mobile_games'
    
    id = db.Column(db.Integer, db.ForeignKey('games.id'), primary_key=True)
    is_free = db.Column(db.Boolean, nullable=False, default=False)
    microtransactions = db.Column(db.Boolean, nullable=False, default=False)
    
    __mapper_args__ = {
        'polymorphic_identity': 'mobile',
    }
    
    @property
    def effective_price(self):
        """Возвращает эффективную цену (0 для бесплатных игр)"""
        return 0.0 if self.is_free else self.price
    
    @effective_price.setter
    def effective_price(self, value):
        """Устанавливает цену с учетом бесплатности"""
        if self.is_free:
            self.price = 0.0
        else:
            self.price = value