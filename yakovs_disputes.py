#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Система споров Якова Давидовича о технических решениях
"""

import json
import random
import re
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from enum import Enum

class DisputePosition(Enum):
    """Позиция Якова в споре"""
    STRONGLY_AGREE = "полностью согласен"
    AGREE = "согласен"
    NEUTRAL = "нейтрален"
    DISAGREE = "не согласен"
    STRONGLY_DISAGREE = "категорически не согласен"

@dataclass
class TechnicalOpinion:
    """Техническое мнение Якова"""
    topic: str
    position: DisputePosition
    arguments: List[str]
    soviet_examples: List[str]
    counter_arguments: List[str]
    yakovs_emotion: str  # "спокойный", "возмущенный", "ностальгический", "поучающий"

@dataclass
class DisputeContext:
    """Контекст спора"""
    user_statement: str
    topic_detected: str
    yakovs_position: DisputePosition
    argument_strength: int  # 1-5
    personal_experience: bool

class YakovsDisputeSystem:
    """Система споров Якова Давидовича"""
    
    def __init__(self):
        self.technical_opinions = self._load_technical_opinions()
        self.dispute_keywords = self._load_dispute_keywords()
        self.active_disputes = {}  # user_id -> DisputeContext
    
    def _load_technical_opinions(self) -> Dict[str, TechnicalOpinion]:
        """Загрузка технических мнений Якова"""
        opinions = {
            "modern_frameworks": TechnicalOpinion(
                topic="современные фреймворки",
                position=DisputePosition.DISAGREE,
                arguments=[
                    "Современные фреймворки слишком раздуты и медленны",
                    "В советское время писали на чистом C и программы летали",
                    "Молодежь разучилась понимать, что происходит под капотом",
                    "Зависимости от тысяч библиотек - это ненадежно"
                ],
                soviet_examples=[
                    "Наша система управления заводом работала 20 лет без единого сбоя",
                    "Программы на Фортране были компактными и быстрыми",
                    "Мы каждую строчку кода проверяли вручную"
                ],
                counter_arguments=[
                    "Но ведь фреймворки ускоряют разработку!",
                    "Современные требования к интерфейсам сложнее",
                    "Безопасность сейчас важнее производительности"
                ],
                yakovs_emotion="возмущенный"
            ),
            
            "code_quality": TechnicalOpinion(
                topic="качество кода",
                position=DisputePosition.STRONGLY_AGREE,
                arguments=[
                    "Качество кода - основа всего!",
                    "Лучше написать медленно, но правильно",
                    "Каждую функцию нужно тестировать до мелочей",
                    "Документация должна быть как техпаспорт"
                ],
                soviet_examples=[
                    "В КБ мы по три раза проверяли каждый алгоритм",
                    "Программы для космоса писались с тройным контролем",
                    "ГОСТ требовал полной документации к каждому модулю"
                ],
                counter_arguments=[
                    "Но сейчас нужно выпускать быстрее",
                    "Рынок не ждет идеального кода"
                ],
                yakovs_emotion="поучающий"
            ),
            
            "artificial_intelligence": TechnicalOpinion(
                topic="искусственный интеллект",
                position=DisputePosition.NEUTRAL,
                arguments=[
                    "ИИ - это интересная технология, но не панацея",
                    "Человеческий опыт и интуиция незаменимы",
                    "ИИ хорош для рутинных задач",
                    "Но творческое мышление - прерогатива человека"
                ],
                soviet_examples=[
                    "Мы в 70-х тоже мечтали о думающих машинах",
                    "Экспертные системы были первыми попытками ИИ",
                    "Но лучший 'искусственный интеллект' - это опытный инженер"
                ],
                counter_arguments=[
                    "ИИ уже превзошел людей в шахматах",
                    "Машинное обучение решает сложные задачи"
                ],
                yakovs_emotion="философский"
            ),
            
            "agile_methodology": TechnicalOpinion(
                topic="agile методологии",
                position=DisputePosition.DISAGREE,
                arguments=[
                    "Agile - это хаос под красивым названием",
                    "Без четкого плана проект обречен на провал",
                    "Постоянные изменения требований вредят качеству",
                    "Водопадная модель надежнее и предсказуемее"
                ],
                soviet_examples=[
                    "Мы всегда планировали проекты на годы вперед",
                    "Техническое задание было священным документом",
                    "Изменения вносились только через комиссию"
                ],
                counter_arguments=[
                    "Но мир изменился, требования меняются быстро",
                    "Гибкость помогает адаптироваться к рынку"
                ],
                yakovs_emotion="возмущенный"
            ),
            
            "open_source": TechnicalOpinion(
                topic="открытый код",
                position=DisputePosition.AGREE,
                arguments=[
                    "Открытый код - это честно и правильно",
                    "Коллективный разум сильнее одиночки",
                    "Прозрачность повышает качество",
                    "Знания должны быть доступны всем"
                ],
                soviet_examples=[
                    "В СССР мы делились опытом между предприятиями",
                    "Научные статьи публиковались открыто",
                    "Коллективный труд всегда был в почете"
                ],
                counter_arguments=[
                    "Но как зарабатывать на бесплатном коде?",
                    "Коммерческие решения надежнее"
                ],
                yakovs_emotion="спокойный"
            ),
            
            "cloud_computing": TechnicalOpinion(
                topic="облачные технологии",
                position=DisputePosition.DISAGREE,
                arguments=[
                    "Облака - это чужие компьютеры, не более",
                    "Зависимость от интернета критична",
                    "Безопасность данных под угрозой",
                    "Локальные решения надежнее"
                ],
                soviet_examples=[
                    "Наши системы работали автономно",
                    "Критически важные данные хранились локально",
                    "Отказоустойчивость закладывалась в архитектуру"
                ],
                counter_arguments=[
                    "Облака дают масштабируемость",
                    "Не нужно содержать свои серверы"
                ],
                yakovs_emotion="недоверчивый"
            )
        }
        return opinions
    
    def _load_dispute_keywords(self) -> Dict[str, List[str]]:
        """Загрузка ключевых слов для определения тем споров"""
        return {
            "modern_frameworks": ["фреймворк", "react", "angular", "vue", "библиотек", "зависимост"],
            "code_quality": ["качество", "код", "тест", "документация", "стандарт", "гост"],
            "artificial_intelligence": ["ии", "искусственный интеллект", "нейрон", "машинное обучение", "chatgpt"],
            "agile_methodology": ["agile", "scrum", "спринт", "итерация", "гибк"],
            "open_source": ["открытый код", "open source", "github", "свободное по"],
            "cloud_computing": ["облак", "cloud", "aws", "azure", "сервер"]
        }
    
    def detect_dispute_topic(self, user_message: str) -> Optional[str]:
        """Определение темы спора по сообщению пользователя"""
        message_lower = user_message.lower()
        
        for topic, keywords in self.dispute_keywords.items():
            for keyword in keywords:
                if keyword in message_lower:
                    return topic
        
        return None
    
    def analyze_user_statement(self, user_message: str) -> Optional[DisputeContext]:
        """Анализ утверждения пользователя"""
        topic = self.detect_dispute_topic(user_message)
        
        if not topic or topic not in self.technical_opinions:
            return None
        
        opinion = self.technical_opinions[topic]
        
        # Определяем силу аргумента пользователя
        argument_indicators = {
            5: ["доказано", "очевидно", "факт", "научно"],
            4: ["считаю", "уверен", "точно"],
            3: ["думаю", "полагаю", "возможно"],
            2: ["может быть", "наверное"],
            1: ["не знаю", "сомневаюсь"]
        }
        
        strength = 3  # По умолчанию
        for level, indicators in argument_indicators.items():
            if any(indicator in user_message.lower() for indicator in indicators):
                strength = level
                break
        
        # Проверяем личный опыт
        personal_indicators = ["опыт", "работал", "использовал", "применял", "видел"]
        has_personal_experience = any(indicator in user_message.lower() for indicator in personal_indicators)
        
        return DisputeContext(
            user_statement=user_message,
            topic_detected=topic,
            yakovs_position=opinion.position,
            argument_strength=strength,
            personal_experience=has_personal_experience
        )
    
    def generate_dispute_response(self, context: DisputeContext) -> str:
        """Генерация ответа Якова в споре"""
        if context.topic_detected not in self.technical_opinions:
            return "Интересная тема, товарищ, но я предпочитаю спорить о том, в чем разбираюсь!"
        
        opinion = self.technical_opinions[context.topic_detected]
        
        # Выбираем стиль ответа в зависимости от эмоции
        emotion_prefixes = {
            "возмущенный": ["😤", "Что за чепуха, товарищ!", "Ну это уже слишком!"],
            "поучающий": ["🤔", "Позвольте объяснить, молодой человек...", "Как говорится..."],
            "спокойный": ["😌", "Понимаю вашу точку зрения, но...", "Давайте разберемся..."],
            "философский": ["💭", "Это глубокий вопрос...", "Жизнь показывает..."],
            "недоверчивый": ["🤨", "Сомневаюсь я в этом...", "Не все так просто..."]
        }
        
        # Формируем ответ
        response_parts = []
        
        # Эмоциональная реакция
        prefixes = emotion_prefixes.get(opinion.yakovs_emotion, ["🤔"])
        response_parts.append(f"{random.choice(prefixes)} ")
        
        # Позиция Якова
        if opinion.position in [DisputePosition.DISAGREE, DisputePosition.STRONGLY_DISAGREE]:
            response_parts.append(f"Я {opinion.position.value} с вашим мнением о {opinion.topic}!")
        else:
            response_parts.append(f"Я {opinion.position.value} по поводу {opinion.topic}.")
        
        response_parts.append("\n\n")
        
        # Основной аргумент
        main_argument = random.choice(opinion.arguments)
        response_parts.append(f"💬 {main_argument}")
        response_parts.append("\n\n")
        
        # Пример из советского опыта
        soviet_example = random.choice(opinion.soviet_examples)
        response_parts.append(f"📖 {soviet_example}.")
        
        # Если у пользователя есть личный опыт, Яков это учитывает
        if context.personal_experience:
            response_parts.append(f"\n\n🤝 Понимаю, что у вас есть практический опыт, товарищ. Но позвольте поделиться своими наблюдениями...")
        
        # Дополнительный аргумент в зависимости от силы утверждения пользователя
        if context.argument_strength >= 4:
            response_parts.append(f"\n\n🎯 Вы говорите очень уверенно! Но {random.choice(opinion.arguments).lower()}")
        elif context.argument_strength <= 2:
            response_parts.append(f"\n\n💡 Раз сомневаетесь, то объясню подробнее: {random.choice(opinion.arguments).lower()}")
        
        return "".join(response_parts)
    
    def get_counter_argument(self, topic: str, user_argument: str) -> str:
        """Получение контраргумента от Якова"""
        if topic not in self.technical_opinions:
            return "Хороший аргумент, товарищ! Но давайте посмотрим с другой стороны..."
        
        opinion = self.technical_opinions[topic]
        
        # Яков признает хорошие аргументы, но отстаивает свою позицию
        responses = [
            f"Справедливое замечание, но {random.choice(opinion.arguments).lower()}",
            f"Да, это так, однако {random.choice(opinion.soviet_examples).lower()}",
            f"Согласен частично, но опыт показывает: {random.choice(opinion.arguments).lower()}",
            f"Вы правы в этом моменте, но не забывайте: {random.choice(opinion.arguments).lower()}"
        ]
        
        return f"🤔 {random.choice(responses)}!"
    
    def start_dispute(self, user_id: int, user_message: str) -> Optional[str]:
        """Начало спора с пользователем"""
        context = self.analyze_user_statement(user_message)
        
        if not context:
            return None
        
        # Сохраняем контекст спора
        self.active_disputes[user_id] = context
        
        # Генерируем первый ответ
        response = self.generate_dispute_response(context)
        
        # Добавляем предложение продолжить спор
        response += f"\n\n❓ А что вы скажете на это, товарищ? Готовы продолжить обсуждение?"
        
        return response
    
    def continue_dispute(self, user_id: int, user_message: str) -> str:
        """Продолжение спора"""
        if user_id not in self.active_disputes:
            return "О чем спорим, товарищ? Начните с технического утверждения!"
        
        context = self.active_disputes[user_id]
        
        # Проверяем, хочет ли пользователь закончить спор
        end_keywords = ["согласен", "убедил", "прав", "закончим", "хватит"]
        if any(keyword in user_message.lower() for keyword in end_keywords):
            del self.active_disputes[user_id]
            return "😊 Вот и славно! Как говорится, в споре рождается истина. Приятно было подискутировать с вами, товарищ!"
        
        # Генерируем контраргумент
        counter_response = self.get_counter_argument(context.topic_detected, user_message)
        
        # Добавляем вопрос для продолжения
        follow_ups = [
            "Что скажете на это?",
            "Какие будут возражения?",
            "Убедил или есть что добавить?",
            "Согласны или будете спорить дальше?"
        ]
        
        return f"{counter_response}\n\n❓ {random.choice(follow_ups)}"
    
    def get_available_topics(self) -> List[str]:
        """Получение списка тем для споров"""
        return list(self.technical_opinions.keys())
    
    def get_topic_summary(self, topic: str) -> str:
        """Получение краткого описания позиции Якова по теме"""
        if topic not in self.technical_opinions:
            return "Неизвестная тема"
        
        opinion = self.technical_opinions[topic]
        main_arg = opinion.arguments[0] if opinion.arguments else "Сложная тема"
        
        return f"{opinion.topic}: {opinion.position.value} - {main_arg}"

def main():
    """Тестирование системы споров"""
    dispute_system = YakovsDisputeSystem()
    
    test_statements = [
        "Современные фреймворки очень удобны для разработки",
        "React делает разработку намного быстрее",
        "Качество кода не так важно, главное скорость",
        "ИИ скоро заменит программистов",
        "Agile лучше водопадной модели"
    ]
    
    print("🥊 Тест системы споров Якова Давидовича")
    print("="*50)
    
    for statement in test_statements:
        print(f"\n👤 Пользователь: {statement}")
        response = dispute_system.start_dispute(123, statement)
        if response:
            print(f"👴 Яков: {response[:200]}...")
        else:
            print("👴 Яков: (тема не распознана)")
        print("-"*50)

if __name__ == "__main__":
    main()
