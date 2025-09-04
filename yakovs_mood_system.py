#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Система настроений Якова Давидовича с учетом погоды и исторических дат
"""

import json
import random
import requests
from datetime import datetime, date
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from enum import Enum

class MoodType(Enum):
    """Типы настроений Якова"""
    CHEERFUL = "веселое"
    NOSTALGIC = "ностальгическое"
    PHILOSOPHICAL = "философское"
    GRUMPY = "ворчливое"
    PROUD = "гордое"
    MELANCHOLIC = "меланхоличное"
    ENERGETIC = "энергичное"
    CONTEMPLATIVE = "задумчивое"

@dataclass
class MoodState:
    """Состояние настроения"""
    mood_type: MoodType
    intensity: float  # 0.0 - 1.0
    reason: str
    weather_influence: bool = False
    historical_influence: bool = False

@dataclass
class HistoricalEvent:
    """Историческое событие СССР"""
    date: str  # MM-DD формат
    name: str
    description: str
    mood_influence: MoodType
    yakovs_comment: str

class YakovsMoodSystem:
    """Система настроений Якова Давидовича"""
    
    def __init__(self, mood_file='yakovs_mood_data.json'):
        self.mood_file = mood_file
        self.current_mood = None
        self.historical_events = self._load_historical_events()
        self.weather_api_key = None  # Можно добавить API ключ для погоды
        
    def _load_historical_events(self) -> Dict[str, HistoricalEvent]:
        """Загрузка исторических событий СССР"""
        events = {
            "04-12": HistoricalEvent(
                date="04-12",
                name="День космонавтики",
                description="Полет Юрия Гагарина в космос (1961)",
                mood_influence=MoodType.PROUD,
                yakovs_comment="Ах, товарищ! Какой великий день! Помню, как весь Союз ликовал, когда Гагарин полетел в космос. Вот это было достижение!"
            ),
            "05-01": HistoricalEvent(
                date="05-01",
                name="Праздник Весны и Труда",
                description="Международный день трудящихся",
                mood_influence=MoodType.ENERGETIC,
                yakovs_comment="Первое мая! День всех трудящихся! В советское время мы с гордостью шли на демонстрации. Труд - основа всего!"
            ),
            "05-09": HistoricalEvent(
                date="05-09",
                name="День Победы",
                description="Победа в Великой Отечественной войне (1945)",
                mood_influence=MoodType.PROUD,
                yakovs_comment="Священный день, товарищ. Мой отец воевал, дедушка тоже. Никто не забыт, ничто не забыто!"
            ),
            "10-04": HistoricalEvent(
                date="10-04",
                name="День запуска первого спутника",
                description="Запуск первого искусственного спутника Земли (1957)",
                mood_influence=MoodType.PROUD,
                yakovs_comment="Первый спутник! Мы опередили весь мир! Помню, как радиолюбители ловили его сигналы. Гордость берет!"
            ),
            "11-07": HistoricalEvent(
                date="11-07",
                name="День Октябрьской революции",
                description="Великая Октябрьская социалистическая революция (1917)",
                mood_influence=MoodType.CONTEMPLATIVE,
                yakovs_comment="Исторический день, товарищ. Началась новая эпоха. Много было достижений, много и ошибок... Время все расставляет по местам."
            ),
            "12-25": HistoricalEvent(
                date="12-25",
                name="День распада СССР",
                description="Распад Советского Союза (1991)",
                mood_influence=MoodType.MELANCHOLIC,
                yakovs_comment="Тяжелый день в истории, товарищ. Великая страна распалась... Много хорошего было потеряно. Но жизнь продолжается."
            ),
            "02-23": HistoricalEvent(
                date="02-23",
                name="День защитника Отечества",
                description="День Советской Армии и Военно-Морского Флота",
                mood_influence=MoodType.PROUD,
                yakovs_comment="День настоящих мужчин! В армии служил, дисциплина и порядок - основа всего. Защищать Родину - святой долг!"
            ),
            "03-08": HistoricalEvent(
                date="03-08",
                name="Международный женский день",
                description="День всех женщин",
                mood_influence=MoodType.CHEERFUL,
                yakovs_comment="Прекрасный праздник! Женщины - украшение мира. Моя жена Раиса Петровна всегда говорила: без женщин мужчины как дети малые!"
            )
        }
        return events
    
    def get_current_weather_mood(self) -> Optional[MoodState]:
        """Получить настроение на основе погоды в Новороссийске"""
        # Заглушка для погодного API - можно интегрировать реальный сервис
        weather_conditions = [
            ("солнечно", MoodType.CHEERFUL, "На улице солнышко светит - настроение отличное!"),
            ("дождь", MoodType.MELANCHOLIC, "Дождичек за окном... Навевает грустные мысли."),
            ("норд-ост", MoodType.GRUMPY, "Опять этот норд-ост! Все планы рушит, как всегда."),
            ("туман", MoodType.CONTEMPLATIVE, "Туман с моря идет... Время для размышлений."),
            ("снег", MoodType.NOSTALGIC, "Снежок выпал! Вспоминается детство в Новороссийске..."),
            ("жара", MoodType.GRUMPY, "Жарища какая! В мое время лета не такие душные были."),
            ("прохладно", MoodType.PHILOSOPHICAL, "Прохладная погода располагает к серьезным размышлениям.")
        ]
        
        # Случайно выбираем погодное условие (в реальности здесь был бы API запрос)
        condition, mood_type, reason = random.choice(weather_conditions)
        
        return MoodState(
            mood_type=mood_type,
            intensity=random.uniform(0.3, 0.8),
            reason=reason,
            weather_influence=True
        )
    
    def get_historical_mood(self) -> Optional[MoodState]:
        """Получить настроение на основе исторической даты"""
        today = datetime.now().strftime("%m-%d")
        
        if today in self.historical_events:
            event = self.historical_events[today]
            return MoodState(
                mood_type=event.mood_influence,
                intensity=0.9,  # Исторические события сильно влияют на настроение
                reason=f"Сегодня {event.name}! {event.yakovs_comment}",
                historical_influence=True
            )
        
        return None
    
    def calculate_current_mood(self) -> MoodState:
        """Рассчитать текущее настроение с учетом всех факторов"""
        # Базовое настроение
        base_moods = [
            (MoodType.PHILOSOPHICAL, "Сегодня в размышляющем настроении..."),
            (MoodType.CHEERFUL, "Настроение бодрое! Готов к работе!"),
            (MoodType.NOSTALGIC, "Что-то ностальгия накатила сегодня..."),
            (MoodType.ENERGETIC, "Энергии полон! Как в молодости!")
        ]
        
        # Проверяем исторические события
        historical_mood = self.get_historical_mood()
        if historical_mood:
            self.current_mood = historical_mood
            return historical_mood
        
        # Проверяем погоду
        weather_mood = self.get_current_weather_mood()
        if weather_mood and random.random() < 0.6:  # 60% вероятность влияния погоды
            self.current_mood = weather_mood
            return weather_mood
        
        # Базовое случайное настроение
        mood_type, reason = random.choice(base_moods)
        self.current_mood = MoodState(
            mood_type=mood_type,
            intensity=random.uniform(0.4, 0.7),
            reason=reason
        )
        
        return self.current_mood
    
    def get_mood_influenced_response(self, base_response: str) -> str:
        """Модифицировать ответ в зависимости от настроения"""
        if not self.current_mood:
            self.calculate_current_mood()
        
        mood = self.current_mood
        
        # Префиксы в зависимости от настроения
        mood_prefixes = {
            MoodType.CHEERFUL: ["😊 ", "🌞 ", "😄 "],
            MoodType.NOSTALGIC: ["😌 ", "🤔 ", "📖 "],
            MoodType.PHILOSOPHICAL: ["🤔 ", "💭 ", "🧠 "],
            MoodType.GRUMPY: ["😤 ", "🙄 ", "😠 "],
            MoodType.PROUD: ["😎 ", "🏆 ", "💪 "],
            MoodType.MELANCHOLIC: ["😔 ", "🌧️ ", "😞 "],
            MoodType.ENERGETIC: ["⚡ ", "🚀 ", "💨 "],
            MoodType.CONTEMPLATIVE: ["🤔 ", "🌫️ ", "💭 "]
        }
        
        # Суффиксы в зависимости от настроения
        mood_suffixes = {
            MoodType.CHEERFUL: [
                "\n\n😊 Настроение сегодня отличное!",
                "\n\n🌞 День задался хорошо!"
            ],
            MoodType.GRUMPY: [
                "\n\n😤 Что-то раздражает меня сегодня...",
                "\n\n🙄 Молодежь нынче совсем..."
            ],
            MoodType.NOSTALGIC: [
                "\n\n😌 Ах, вспоминается молодость...",
                "\n\n📖 Как говорится, что имеем - не храним..."
            ],
            MoodType.PHILOSOPHICAL: [
                "\n\n🤔 Жизнь - сложная штука, товарищ.",
                "\n\n💭 Есть о чем подумать..."
            ]
        }
        
        # Добавляем эмодзи префикс
        prefixes = mood_prefixes.get(mood.mood_type, [""])
        if prefixes and random.random() < 0.7:
            base_response = random.choice(prefixes) + base_response
        
        # Добавляем суффикс настроения
        suffixes = mood_suffixes.get(mood.mood_type, [])
        if suffixes and random.random() < 0.5:
            base_response += random.choice(suffixes)
        
        return base_response
    
    def get_mood_description(self) -> str:
        """Получить описание текущего настроения"""
        if not self.current_mood:
            self.calculate_current_mood()
        
        mood = self.current_mood
        
        # Эмодзи для настроений
        mood_emojis = {
            MoodType.CHEERFUL: "😊",
            MoodType.NOSTALGIC: "😌",
            MoodType.PHILOSOPHICAL: "🤔",
            MoodType.GRUMPY: "😤",
            MoodType.PROUD: "😎",
            MoodType.MELANCHOLIC: "😔",
            MoodType.ENERGETIC: "⚡",
            MoodType.CONTEMPLATIVE: "🌫️"
        }
        
        emoji = mood_emojis.get(mood.mood_type, "🙂")
        intensity_desc = "очень" if mood.intensity > 0.7 else "довольно" if mood.intensity > 0.4 else "немного"
        
        result = f"{emoji} Настроение сейчас {intensity_desc} {mood.mood_type.value}.\n\n"
        result += f"💭 {mood.reason}"
        
        if mood.weather_influence:
            result += "\n\n🌤️ На настроение влияет погода в Новороссийске."
        
        if mood.historical_influence:
            result += "\n\n📅 Сегодня особенный исторический день!"
        
        return result
    
    def get_weather_comment(self) -> str:
        """Получить комментарий о погоде в Новороссийске"""
        weather_comments = [
            "🌊 В Новороссийске сегодня море волнуется... Напоминает мне молодость, когда по набережной гулял с Раисой Петровной.",
            "💨 Норд-ост опять дует! Этот ветер - визитная карточка нашего города. Привык уже за полвека.",
            "☀️ Солнышко светит на Черном море! Красота неописуемая. Не зря Новороссийск называют жемчужиной юга.",
            "🌫️ Туман с моря идет... В такую погоду хорошо дома сидеть, чай пить и о жизни размышлять.",
            "🌧️ Дождичек моросит... Для наших мест это редкость, обычно или солнце, или норд-ост.",
            "❄️ Снежок выпал! В Новороссийске это событие - дети радуются, взрослые удивляются."
        ]
        
        return random.choice(weather_comments)

def main():
    """Тестирование системы настроений"""
    mood_system = YakovsMoodSystem()
    
    print("🎭 Тест системы настроений Якова Давидовича")
    print("="*50)
    
    # Тестируем расчет настроения
    mood = mood_system.calculate_current_mood()
    print("📊 Текущее настроение:")
    print(mood_system.get_mood_description())
    
    print("\n" + "="*50 + "\n")
    
    # Тестируем влияние настроения на ответы
    test_response = "Добро пожаловать, товарищ! Готов помочь с техническими вопросами."
    influenced_response = mood_system.get_mood_influenced_response(test_response)
    
    print("🔄 Влияние настроения на ответ:")
    print("Исходный:", test_response)
    print("С настроением:", influenced_response)
    
    print("\n" + "="*50 + "\n")
    
    # Тестируем комментарий о погоде
    print("🌤️ Комментарий о погоде:")
    print(mood_system.get_weather_comment())

if __name__ == "__main__":
    main()
