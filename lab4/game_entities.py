from abc import ABC, abstractmethod

class Game(ABC):
    def __init__(self, title="", developer="", year=0, price=0.0, io_strategy=None):
        self.title = title
        self.developer = developer
        self.year = year
        self.price = price
        self.io_strategy = io_strategy
    
    @abstractmethod
    def get_type(self):
        pass
    
    def __str__(self):
        return f"{self.get_type()}: {self.title} ({self.year}) | {self.developer} | ${self.price:.2f}"
    
    def input(self):
        if self.io_strategy:
            self.title = self.io_strategy.input_field("title", required=True)
            self.developer = self.io_strategy.input_field("developer", required=True)
            self.year = self.io_strategy.input_field_int("year", 1970, 2025, required=True)
            self.price = self.io_strategy.input_field_float("price", 0, 1000, required=True)
    
    def output(self):
        return {
            'type': self.get_type(),
            'title': self.title,
            'developer': self.developer,
            'year': self.year,
            'price': self.price
        }
    
    def __reduce__(self):
        return (self.__class__, (self.title, self.developer, self.year, self.price, None))


class IndieGame(Game):
    def __init__(self, title="", developer="", year=0, price=0.0, team_size=1, engine="", io_strategy=None):
        super().__init__(title, developer, year, price, io_strategy)
        self.team_size = team_size
        self.engine = engine
    
    def get_type(self):
        return "🎨 Инди-игра"
    
    def __str__(self):
        base = super().__str__()
        return f"{base} | 👥 {self.team_size} чел. | 🛠️ {self.engine}"
    
    def input(self):
        super().input()
        if self.io_strategy:
            self.team_size = self.io_strategy.input_field_int("team_size", 1, 1000, required=True)
            self.engine = self.io_strategy.input_field("engine", required=True)
    
    def output(self):
        data = super().output()
        data.update({
            'team_size': self.team_size,
            'engine': self.engine
        })
        return data
    
    def __reduce__(self):
        return (self.__class__, (self.title, self.developer, self.year, self.price, 
                                self.team_size, self.engine, None))


class AAAGame(Game):
    def __init__(self, title="", developer="", year=0, price=0.0, budget=0.0, platforms=None, io_strategy=None):
        super().__init__(title, developer, year, price, io_strategy)
        self.budget = budget
        self.platforms = platforms if platforms else []
    
    def get_type(self):
        return "💰 AAA-игра"
    
    def __str__(self):
        platforms_str = ", ".join(self.platforms) if self.platforms else "❓ Не указаны"
        base = super().__str__()
        return f"{base} | 💸 ${self.budget:.2f}M | 🖥️ {platforms_str}"
    
    def input(self):
        super().input()
        if self.io_strategy:
            self.budget = self.io_strategy.input_field_float("budget", 1, 1000, required=True)
            platforms_input = self.io_strategy.input_field("platforms", required=False)
            if platforms_input:
                self.platforms = [p.strip() for p in platforms_input.split(",") if p.strip()]
    
    def output(self):
        data = super().output()
        data.update({
            'budget': self.budget,
            'platforms': self.platforms
        })
        return data
    
    def __reduce__(self):
        return (self.__class__, (self.title, self.developer, self.year, self.price,
                                self.budget, self.platforms, None))


class MobileGame(Game):
    def __init__(self, title="", developer="", year=0, price=0.0, 
                 is_free=False, microtransactions=False, io_strategy=None):
        super().__init__(title, developer, year, price, io_strategy)
        self.is_free = is_free
        self.microtransactions = microtransactions
    
    def get_type(self):
        return "📱 Мобильная игра"
    
    def __str__(self):
        base = super().__str__()
        free_status = "✅ Бесплатная" if self.is_free else "💰 Платная"
        micro_status = "💎 Есть микротранзакции" if self.microtransactions else "🚫 Нет микротранзакций"
        return f"{base} | {free_status} | {micro_status}"
    
    def input(self):
        super().input()
        if self.io_strategy:
            self.is_free = self.io_strategy.input_field_bool("is_free")
            self.microtransactions = self.io_strategy.input_field_bool("microtransactions")
    
    def output(self):
        data = super().output()
        data.update({
            'is_free': self.is_free,
            'microtransactions': self.microtransactions
        })
        return data
    
    def __reduce__(self):
        return (self.__class__, (self.title, self.developer, self.year, self.price,
                                self.is_free, self.microtransactions, None))