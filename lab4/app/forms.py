from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, FloatField, BooleanField
from wtforms.validators import DataRequired, NumberRange, Optional, Length, ValidationError
from wtforms.widgets import CheckboxInput

class BaseGameForm(FlaskForm):
    title = StringField('НАЗВАНИЕ ИГРЫ', validators=[
        DataRequired(message='Название игры обязательно'),
        Length(min=1, max=200, message='Название должно быть от 1 до 200 символов')
    ])
    
    developer = StringField('РАЗРАБОТЧИК', validators=[
        DataRequired(message='Разработчик обязателен'),
        Length(min=1, max=200, message='Название разработчика должно быть от 1 до 200 символов')
    ])
    
    year = IntegerField('ГОД ВЫПУСКА', validators=[
        DataRequired(message='Год выпуска обязателен'),
        NumberRange(min=1970, max=2026, message='Год должен быть от 1970 до 2026')
    ])
    
    price = FloatField('ЦЕНА ($)', validators=[
        Optional(),
        NumberRange(min=0, max=1000, message='Цена должна быть от 0 до 1000')
    ])


class IndieGameForm(BaseGameForm):
    team_size = IntegerField('РАЗМЕР КОМАНДЫ', validators=[
        DataRequired(message='Размер команды обязателен'),
        NumberRange(min=1, max=1000, message='Размер команды должен быть от 1 до 1000')
    ])
    
    engine = StringField('ИГРОВОЙ ДВИЖОК', validators=[
        DataRequired(message='Игровой движок обязателен'),
        Length(min=1, max=100, message='Название движка должно быть от 1 до 100 символов')
    ])


class AAAGameForm(BaseGameForm):
    budget = FloatField('БЮДЖЕТ (МЛН $)', validators=[
        DataRequired(message='Бюджет обязателен'),
        NumberRange(min=1, max=1000, message='Бюджет должен быть от 1 до 1000 млн $')
    ])
    
    platforms = StringField('ПЛАТФОРМЫ', validators=[Optional()])


class MobileGameForm(BaseGameForm):
    is_free = BooleanField('БЕСПЛАТНАЯ ИГРА', widget=CheckboxInput())
    microtransactions = BooleanField('ЕСТЬ МИКРОТРАНЗАКЦИИ', widget=CheckboxInput())
    
    def validate_price(self, field):
        """Валидация цены для мобильных игр"""
        if self.is_free.data:
            if field.data and field.data != 0:
                field.data = 0.0
        else:
            if not field.data or field.data <= 0:
                raise ValidationError('Для платной игры необходимо указать цену (> 0)')


class ImportForm(FlaskForm):
    """Форма для загрузки файлов"""
    format = StringField('ФОРМАТ')  # Скрытое поле
    filename = StringField('ИМЯ ФАЙЛА', validators=[DataRequired()])
    confirm = BooleanField('ПОДТВЕРЖДЕНИЕ', validators=[DataRequired()])