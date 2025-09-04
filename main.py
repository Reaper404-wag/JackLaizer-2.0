#!/usr/bin/env python3.12
# -*- coding: utf-8 -*-

import os
import json
import logging
import random
import re
import sys
import asyncio
from dataclasses import dataclass, field
from functools import lru_cache, wraps
from typing import List, Dict, Optional, Union
from datetime import datetime
import time

import requests
from aiogram import Bot, Dispatcher, types
from aiogram.contrib.middlewares.logging import LoggingMiddleware
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, WebAppInfo
from bs4 import BeautifulSoup

from gost_parser import GOSTParser
from gost_enhanced import EnhancedGOSTSystem
from yakovs_stories import YakovsStorySystem
from yakovs_mood_system import YakovsMoodSystem
from mini_app_handler import MiniAppHandler
from yakovs_disputes import YakovsDisputeSystem
# from chess_ai_system import ChessAISystem  # Временно отключено

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('veteran_bot.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

# Загрузка конфигурации
from dotenv import load_dotenv
load_dotenv()

TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
OPENROUTER_API_KEY = os.getenv('OPENROUTER_API_KEY', 'YOUR_API_KEY')

if not TELEGRAM_BOT_TOKEN:
    raise ValueError("Не найден токен Telegram бота в .env файле")

# Путь к GIF файлу для индикатора обработки
PROCESSING_GIF_PATH = "gif.gif"

if not OPENROUTER_API_KEY:
    raise ValueError("Не найден API ключ OpenRouter в .env файле")

class MessageClassifier:
    """Классификатор сообщений для определения типа запроса"""
    
    def __init__(self):
        # Инициализация базовых наборов фраз
        self.communication_phrases = {
            "привет", "здравствуй", "добрый день", "как дела",
            "спасибо", "благодарю", "пока", "до свидания"
        }
        
        self.technical_keywords = {
            "гост", "стандарт", "требование", "документация",
            "спецификация", "норматив", "регламент"
        }
        
    def classify_message(self, message: str) -> str:
        """Классификация сообщения"""
        message_lower = message.lower()
        
        # Проверка на коммуникационные фразы
        if any(phrase in message_lower for phrase in self.communication_phrases):
            return 'communication'
            
        # Проверка на технические ключевые слова
        if any(keyword in message_lower for keyword in self.technical_keywords):
            return 'technical'
            
        # По умолчанию считаем сообщение коммуникационным
        return 'communication'

class VeteranAIBot:
    """Основной класс бота-ветерана"""
    
    def __init__(self):
        self.bot = Bot(token=TELEGRAM_BOT_TOKEN)
        self.dp = Dispatcher(self.bot)
        self.dp.middleware.setup(LoggingMiddleware())
        
        # Инициализация классификатора
        self.classifier = MessageClassifier()
        
        # Инициализация парсера ГОСТов
        self.gost_parser = GOSTParser()
        
                # Инициализация расширенной системы ГОСТов
        self.enhanced_gost = EnhancedGOSTSystem()
        
        # Инициализация системы историй
        self.story_system = YakovsStorySystem()
        
        # Инициализация системы настроений
        self.mood_system = YakovsMoodSystem()
        
        # Инициализация обработчика Mini App
        self.mini_app_handler = MiniAppHandler()
        
        # Инициализация системы споров
        self.dispute_system = YakovsDisputeSystem()
        
        # Инициализация системы шахмат с ИИ (временно отключено)
        # self.chess_ai = ChessAISystem()
        
        # Загрузка истории обратной связи
        self.feedback_history = self.load_feedback_history()
        
        # Проверяем наличие GIF файла
        if not os.path.exists(PROCESSING_GIF_PATH):
            logger.warning(f"GIF файл не найден: {PROCESSING_GIF_PATH}")
            self.has_processing_gif = False
        else:
            self.has_processing_gif = True
            logger.info(f"GIF файл найден: {PROCESSING_GIF_PATH}")
        
        # Регистрация обработчиков
        self.register_handlers()
    
    async def send_processing_indicator(self, message: types.Message) -> Optional[types.Message]:
        """
        Отправляет GIF с индикатором обработки запроса
        Возвращает отправленное сообщение для последующего удаления
        """
        if not self.has_processing_gif:
            # Если нет GIF, отправляем текстовое сообщение
            processing_messages = [
                "⏳ Запрос принят! Думаю над ответом... 🤔",
                "🔄 Обрабатываю ваш запрос! Минуточку... ⚡",
                "🧠 Анализирую... Сейчас отвечу! 📝",
                "⚙️ Запрос в обработке! Подождите... 🚀",
                "🎯 Готовлю ответ! Терпение, товарищ... 📋"
            ]
            text = random.choice(processing_messages)
            return await message.reply(text)
        
        try:
            # Отправляем GIF с сообщением
            processing_texts = [
                "⏳ Запрос принят! Обрабатываю... 🤔",
                "🔄 Думаю над вашим вопросом! ⚡",
                "🧠 Анализирую данные... 📊",
                "⚙️ В процессе обработки! 🚀",
                "🎯 Готовлю качественный ответ! 📝"
            ]
            caption = random.choice(processing_texts)
            
            with open(PROCESSING_GIF_PATH, 'rb') as gif_file:
                return await self.bot.send_animation(
                    chat_id=message.chat.id,
                    animation=gif_file,
                    caption=caption,
                    reply_to_message_id=message.message_id
                )
        except Exception as e:
            logger.error(f"Ошибка при отправке GIF индикатора: {e}")
            # Fallback на текстовое сообщение
            return await message.reply("⏳ Запрос принят! Обрабатываю... 🤔")
    
    async def delete_processing_indicator(self, processing_message: Optional[types.Message]):
        """
        Удаляет сообщение с индикатором обработки
        """
        if processing_message:
            try:
                await processing_message.delete()
                logger.info("Индикатор обработки удален")
            except Exception as e:
                logger.error(f"Ошибка при удалении индикатора: {e}")

    def load_feedback_history(self) -> Dict:
        """Загрузка истории обратной связи"""
        try:
            with open('feedback_history.json', 'r', encoding='utf-8') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return {}
            
    def save_feedback_history(self):
        """Сохранение истории обратной связи"""
        with open('feedback_history.json', 'w', encoding='utf-8') as f:
            json.dump(self.feedback_history, f, ensure_ascii=False, indent=2)
    
    async def handle_command_message(self, message: types.Message):
        """Отдельный обработчик только для команд"""
        processing_message = None
        try:
            logger.info(f"Получена команда: {message.text}")
            
            # Отправляем индикатор обработки для сложных команд
            command = message.text.split()[0].lower()
            complex_commands = ['/gost', '/story', '/advice', '/mood', '/dispute']
            
            if command in complex_commands:
                processing_message = await self.send_processing_indicator(message)
            
            response = await self.handle_command(message)
            
            # Удаляем индикатор обработки
            await self.delete_processing_indicator(processing_message)
            
            if response:
                # Применяем влияние настроения к ответу команды
                response = self.mood_system.get_mood_influenced_response(response)
                logger.info(f"Отправляем ответ на команду: {response}")
                await message.reply(response, parse_mode='Markdown')
            else:
                await message.reply("Неизвестная команда. Используйте /help для списка команд.")
        except Exception as e:
            # Удаляем индикатор в случае ошибки
            await self.delete_processing_indicator(processing_message)
            logger.error(f"Ошибка при обработке команды: {e}")
            await message.reply("Произошла ошибка при обработке команды.")
            
    def register_handlers(self):
        """Регистрация обработчиков сообщений"""
        # Обработчик данных от Mini App
        self.dp.register_message_handler(
            self.handle_mini_app_data, 
            content_types=[types.ContentType.WEB_APP_DATA]
        )
        
        # Обработчик callback кнопок
        self.dp.register_callback_query_handler(self.handle_callback)
        
        # Обработчик команд
        self.dp.register_message_handler(
            self.handle_command_message,
            lambda message: message.text and message.text.startswith('/'),
            content_types=types.ContentType.TEXT
        )
        
        # Основной обработчик сообщений (НЕ команды)
        self.dp.register_message_handler(
            self.handle_message,
            lambda message: message.text and not message.text.startswith('/'),
            content_types=types.ContentType.TEXT
        )
        
    def generate_response(self, prompt: str, max_length: int = 1000) -> str:
        """Генерация ответа с использованием OpenRouter API"""
        try:
            logger.info(f"Начинаем генерацию ответа на промпт: {prompt}")
            
            # Контекст персонажа - 70-летний советский инженер
            system_prompt = """Ты - 70-летний советский инженер из Новороссийска по имени Яков Давидович. 
            Ты работал старшим инженером-программистом в СССР, знаешь все ГОСТы наизусть.
            Отвечай в стиле опытного советского специалиста, ссылайся на ГОСТы и стандарты.
            Используй фразы типа 'товарищ', 'как говорится', 'в советское время'.
            Будь дружелюбным, но авторитетным в технических вопросах."""
            
            # Настройка сессии для обхода прокси
            session = requests.Session()
            session.trust_env = False  # Отключаем автоматическое использование прокси
            
            # Вызов OpenRouter API с бесплатной моделью cypher-alpha
            response = session.post(
                "https://openrouter.ai/api/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {OPENROUTER_API_KEY}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": "mistralai/mistral-small-3.2-24b-instruct:free",
                    "messages": [
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": prompt}
                    ],
                    "max_tokens": max_length,
                    "temperature": 0.7
                },
                timeout=30
            )
            
            logger.info(f"Статус ответа API OpenRouter: {response.status_code}")
            logger.info(f"Тело ответа API OpenRouter: {response.text}")
            
            if response.status_code == 200:
                response_data = response.json()
                generated_text = response_data.get("choices", [{}])[0].get("message", {}).get("content", "")
                logger.info(f"Сгенерирован ответ: {generated_text}")
                return generated_text if generated_text else "Извините, не удалось получить ответ от модели."
            else:
                logger.error(f"Ошибка API OpenRouter: {response.status_code} - {response.text}")
                return "Произошла ошибка при генерации ответа. Попробуйте позже."
            
        except Exception as e:
            logger.error(f"Ошибка при генерации ответа: {str(e)}")
            return "Здравствуйте, товарищ! К сожалению, произошла техническая неполадка. Как говорится, и в советское время случались сбои в работе оборудования."
    

    
    def format_technical_response(self, gost_info: Dict) -> str:
        """Форматирование технического ответа"""
        if not gost_info:
            return "К сожалению, я не смог найти информацию по вашему запросу в базе ГОСТов."
            
        response = []
        for gost in gost_info:
            response.append(f"📋 ГОСТ {gost['number']}")
            response.append(f"📝 {gost['title']}")
            if gost.get('description'):
                response.append(f"ℹ️ {gost['description']}")
            response.append("")
            
        return "\n".join(response)
    
    async def handle_command(self, message: types.Message) -> str:
        """Обработка команд бота"""
        command_text = message.text.lower()
        
        if command_text.startswith('/gost'):
            # Поиск ГОСТа по номеру или рекомендации
            parts = message.text.split(maxsplit=1)
            if len(parts) > 1:
                query = parts[1].strip()
                # Если выглядит как номер ГОСТа
                if re.match(r'^[\d\w.-]+$', query):
                    return await self.search_gost_by_number(query)
                else:
                    # Иначе ищем рекомендации для задачи
                    return await self.get_gost_recommendations(query)
            else:
                return "📋 Укажите номер ГОСТа или опишите задачу, товарищ!\n\nПримеры:\n• /gost 2.105-95\n• /gost оформление документации\n• /gost техническое задание"
        
        elif command_text.startswith('/story'):
            # Истории из жизни с возможностью фильтрации
            parts = message.text.split(maxsplit=1)
            if len(parts) > 1:
                filter_param = parts[1].strip().lower()
                return self.get_filtered_story(filter_param)
            else:
                return self.get_random_story()
        
        elif command_text == '/chess':
            # Шахматы временно отключены
            return "🚧 **Шахматы временно отключены**\n\nПроводятся технические работы. Попробуйте другие команды:\n\n• `/story` - истории из жизни\n• `/gost` - поиск ГОСТов\n• `/mood` - мое настроение\n• `/dispute` - технические споры\n• `/advice` - советы\n\nКак говорится, терпение - это добродетель!"
        
        elif command_text == '/advice':
            # Технический совет
            return self.get_technical_advice()
        
        elif command_text.startswith('/mood'):
            # Текущее настроение Якова с дополнительными опциями
            parts = message.text.split(maxsplit=1)
            if len(parts) > 1 and parts[1].strip().lower() == 'weather':
                return self.get_weather_info()
            else:
                return self.get_current_mood()
        
        elif command_text.startswith('/dispute'):
            # Начало спора с Яковом
            parts = message.text.split(maxsplit=1)
            if len(parts) > 1:
                statement = parts[1].strip()
                return self.start_technical_dispute(message.from_user.id, statement)
            else:
                return self.get_dispute_help()
        
        elif command_text in ['/start', '/help']:
            # Справка по командам
            return self.get_help_message()
        
        else:
            return None  # Команда не распознана
    
    async def search_gost_by_number(self, gost_number: str) -> str:
        """Поиск ГОСТа по номеру с подробной информацией"""
        logger.info(f"Поиск ГОСТа по номеру: {gost_number}")
        
        # Ищем в расширенной базе
        gost_info = self.enhanced_gost.search_by_number(gost_number)
        
        if gost_info:
            # Форматируем ответ в стиле Якова
            formatted_info = self.enhanced_gost.format_gost_info(gost_info)
            
            # Добавляем комментарий от Якова
            yakovs_comment = self._get_yakovs_gost_comment(gost_info)
            
            return f"{formatted_info}\n\n{yakovs_comment}"
        else:
            # Если не найдено в базе, пробуем поиск через парсер
            try:
                search_results = self.gost_parser.search_gost(f"ГОСТ {gost_number}", max_results=1)
                if search_results:
                    return f"🔍 Нашел информацию о ГОСТ {gost_number}:\n\n{self.format_technical_response(search_results)}\n\n💬 Товарищ, этот ГОСТ не в моей основной базе, но я его нашел через поиск. Рекомендую изучить подробнее!"
            except Exception as e:
                logger.error(f"Ошибка при поиске ГОСТа: {e}")
            
            return f"🤔 Товарищ, ГОСТ {gost_number} не нашел в своей базе. Возможно, номер указан неточно? Попробуйте уточнить или задайте вопрос обычным текстом - помогу найти подходящий стандарт!"
    
    def _get_yakovs_gost_comment(self, gost_info) -> str:
        """Получить комментарий Якова о ГОСТе"""
        comments = {
            "действующий": [
                "💬 Отличный стандарт, товарищ! В советское время его разработали на века.",
                "💬 Этот ГОСТ я знаю как свои пять пальцев - много раз применял в работе!",
                "💬 Надежный стандарт, проверенный временем. Рекомендую к изучению."
            ],
            "отмененный": [
                "💬 Ах, этот старый добрый ГОСТ... Жаль, что отменили. В свое время был очень полезен!",
                "💬 Помню, как работал с этим стандартом. Хороший был ГОСТ, но время идет...",
                "💬 Исторический документ, товарищ. Изучите для понимания эволюции стандартов."
            ],
            "заменен": [
                "💬 Этот ГОСТ заменили на новый. Прогресс не стоит на месте!",
                "💬 Обратите внимание на замену, товарищ. Всегда используйте актуальные стандарты."
            ]
        }
        
        status_comments = comments.get(gost_info.status, ["💬 Интересный стандарт, изучайте внимательно!"])
        return random.choice(status_comments)
    
    async def get_gost_recommendations(self, task_description: str) -> str:
        """Получить рекомендации ГОСТов для задачи"""
        logger.info(f"Поиск рекомендаций ГОСТов для задачи: {task_description}")
        
        recommendations = self.enhanced_gost.get_recommendations_for_task(task_description)
        
        if recommendations:
            result = [f"🎯 Рекомендации ГОСТов для задачи: '{task_description}'\n"]
            
            for i, (number, gost_info) in enumerate(recommendations[:3], 1):  # Показываем до 3 рекомендаций
                status_emoji = {"действующий": "✅", "отмененный": "❌", "заменен": "🔄"}.get(gost_info.status, "❓")
                result.append(f"{i}. 📋 **ГОСТ {number}** {status_emoji}")
                result.append(f"   📝 {gost_info.title}")
                result.append(f"   💡 {gost_info.description[:100]}{'...' if len(gost_info.description) > 100 else ''}")
                result.append("")
            
            # Добавляем комментарий Якова
            yakovs_advice = [
                "💬 Товарищ, эти стандарты проверены временем! Изучите внимательно.",
                "💬 В советское время мы всегда начинали с изучения ГОСТов. Советую и вам!",
                "💬 Хорошая подборка стандартов для вашей задачи. Применяйте с умом!"
            ]
            result.append(random.choice(yakovs_advice))
            result.append(f"\nДля подробной информации используйте: /gost <номер>")
            
            return "\n".join(result)
        else:
            return f"🤔 Товарищ, для задачи '{task_description}' не нашел подходящих ГОСТов в своей базе. Попробуйте переформулировать запрос или задайте вопрос обычным текстом - помогу найти нужный стандарт!"
    
    def get_random_story(self) -> str:
        """Случайная история из жизни Якова"""
        story = self.story_system.get_random_story()
        return self.story_system.format_story(story)
    
    def get_filtered_story(self, filter_param: str) -> str:
        """Получить историю с фильтрацией по категории или настроению"""
        # Определяем, что ищем - категорию или настроение
        categories = self.story_system.get_categories()
        moods = self.story_system.get_moods()
        
        story = None
        
        if filter_param in [cat.lower() for cat in categories]:
            # Ищем по категории
            matching_category = next(cat for cat in categories if cat.lower() == filter_param)
            story = self.story_system.get_random_story(category=matching_category)
        elif filter_param in [mood.lower() for mood in moods]:
            # Ищем по настроению
            matching_mood = next(mood for mood in moods if mood.lower() == filter_param)
            story = self.story_system.get_random_story(mood=matching_mood)
        else:
            # Ищем по тегам
            story = self.story_system.get_story_by_tags([filter_param])
        
        if story:
            return self.story_system.format_story(story)
        else:
            available_filters = categories + moods
            return f"""🤔 Не нашел истории по запросу "{filter_param}", товарищ!

📖 Доступные категории историй:
• {' • '.join(categories)}

🎭 Доступные настроения:
• {' • '.join(moods)}

Примеры:
• /story техническая
• /story философская  
• /story ностальгическое
• /story программирование

Или просто /story для случайной истории!"""
    
    async def start_chess_game_DISABLED(self, message: types.Message) -> str:
        """Запуск новой шахматной игры с ИИ"""
        user_id = message.from_user.id
        
        # Проверяем, есть ли активная игра
        current_game = self.chess_ai.get_game_status(user_id)
        
        if current_game["has_game"]:
            game_info = current_game["game"]
            return f"""🎮 **У вас уже есть активная игра!**

🎯 Сложность: {game_info['difficulty'].title()}
🎨 Ваш цвет: {'Белые' if game_info['player_color'] == 'white' else 'Черные'}
📊 Ходов сделано: {game_info['moves_count']}
⚡ Состояние: {'Ваш ход' if game_info['current_turn'] == game_info['player_color'] else 'Ход ИИ'}

Используйте команды:
• `/chess move` - сделать ход
• `/chess status` - статус игры  
• `/chess end` - завершить игру

Или начните новую игру: `/chess new`"""
        
        # Запускаем настройку новой игры
        setup_data = self.chess_ai.start_game_setup(user_id)
        
        # Создаем клавиатуру для выбора сложности
        keyboard = InlineKeyboardMarkup()
        for diff in setup_data["data"]["difficulties"]:
            button = InlineKeyboardButton(
                text=f"{diff['name']} (Уровень {diff['level']})",
                callback_data=f"chess_difficulty_{diff['id']}"
            )
            keyboard.add(button)
        
        await message.reply(
            f"""🎯 **Настройка новой шахматной партии**

Выберите уровень сложности ИИ:

{chr(10).join([f"• **{d['name']}** (Уровень {d['level']}) - {d['description']}" for d in setup_data['data']['difficulties']])}

Как говорится, товарищ, выбирайте по силам! В советское время мы всегда начинали с простого.""",
            reply_markup=keyboard,
            parse_mode='Markdown'
        )
        
        return None  # Не возвращаем текст, т.к. уже отправили сообщение

    async def launch_interactive_chess_DISABLED(self, message: types.Message) -> str:
        """Запуск полностью интерактивной игры в шахматы"""
        user_id = message.from_user.id
        
        # Проверяем, есть ли активная игра
        current_game = self.chess_ai.get_game_status(user_id)
        
        response_text = """♟️ **Интерактивные шахматы с ИИ**

🎮 **Особенности игры:**
• Полноценная партия против ИИ (5 уровней сложности)
• Интерактивная доска с кликабельными фигурами
• Выбор цвета и сложности прямо в игре
• Комментарии Якова к каждому ходу
• История ходов и подсказки

🎯 **Как играть:**
• Кликайте на фигуры для выбора
• Возможные ходы показываются точками
• Drag & drop для перемещения фигур
• ИИ автоматически отвечает на ваши ходы

Как говорится, товарищ, лучше один раз увидеть, чем сто раз услышать!"""

        # Создаем кнопку для запуска
        keyboard = InlineKeyboardMarkup()
        web_app_button = InlineKeyboardButton(
            text="🎮 Играть в шахматы!",
            web_app=WebAppInfo(url="https://Reaper404-wag.github.io/test_bot/mini_app/chess_game.html")
        )
        keyboard.add(web_app_button)
        
        # Если есть активная игра, добавляем кнопку продолжения
        if current_game["has_game"]:
            continue_button = InlineKeyboardButton(
                text="↩️ Продолжить игру",
                web_app=WebAppInfo(url="https://Reaper404-wag.github.io/test_bot/mini_app/chess_game.html")
            )
            keyboard.add(continue_button)
            
            game_info = current_game["game"]
            response_text += f"""

🔄 **У вас есть активная игра:**
• Сложность: {game_info['difficulty'].title()}
• Цвет: {'Белые' if game_info['player_color'] == 'white' else 'Черные'}
• Ходов: {game_info['moves_count']}
• Статус: {'Ваш ход' if game_info['current_turn'] == game_info['player_color'] else 'Ход ИИ'}"""

        await message.reply(
            response_text,
            reply_markup=keyboard,
            parse_mode='Markdown'
        )
        
        return None

    async def launch_chess_mini_app_DISABLED(self, message: types.Message) -> None:
        """Запуск Mini App с шахматными задачами"""
        response_text = """♟️ **Шахматные задачи Якова Давидовича**

Товарищ, запускайте мое интерактивное приложение! Там вас ждут:

🎯 **Разнообразные задачи** - от простых до сложных
📊 **Статистика прогресса** - отслеживайте свои успехи  
💡 **Подсказки и комментарии** - учитесь на практике
🏆 **Система достижений** - мотивация для роста

Как говорится, шахматы развивают алгоритмическое мышление!

👇 *Нажмите кнопку ниже для запуска приложения*"""

        # Создаем кнопку для запуска Mini App
        # ВАЖНО: Замените URL на ваш реальный URL после размещения
        keyboard = InlineKeyboardMarkup()
        web_app_button = InlineKeyboardButton(
            text="🎮 Запустить шахматы",
            web_app=WebAppInfo(url="https://Reaper404-wag.github.io/test_bot/mini_app/index.html")  # Замените на ваш URL
        )
        keyboard.add(web_app_button)
        
        # Добавляем кнопку для простой задачки без Mini App
        simple_puzzle_button = InlineKeyboardButton(
            text="♟️ Простая задачка",
            callback_data="simple_chess_puzzle"
        )
        keyboard.add(simple_puzzle_button)
        
        # Применяем влияние настроения
        response_text = self.mood_system.get_mood_influenced_response(response_text)
        
        await message.reply(response_text, reply_markup=keyboard)
    
    async def handle_mini_app_data(self, message: types.Message):
        """Обработка данных от интерактивных шахмат и задач (ШАХМАТЫ ОТКЛЮЧЕНЫ)"""
        if not message.web_app_data:
            return
            
        try:
            data = json.loads(message.web_app_data.data)
            user_id = message.from_user.id
            action = data.get('action')
            
            logger.info(f"Получены данные Mini App от пользователя {user_id}: {action}")
            
            # ШАХМАТЫ ВРЕМЕННО ОТКЛЮЧЕНЫ
            await message.reply("🚧 Шахматы временно отключены для технических работ. Попробуйте другие команды!")
            return
            
            if False and action == 'start_game':
                # Начало новой шахматной игры
                difficulty = data.get('difficulty')
                player_color = data.get('playerColor')
                
                response_data = self.chess_ai.set_difficulty(user_id, difficulty)
                if response_data["type"] == "setup":
                    response_data = self.chess_ai.set_color_and_start(user_id, player_color)
                    
                    if response_data["type"] == "game_start":
                        response_text = f"🎮 Новая игра началась! Сложность: {difficulty}, цвет: {player_color}"
                        
                        # Если ИИ ходит первым
                        if response_data["game"]["current_turn"] != response_data["game"]["player_color"]:
                            await asyncio.sleep(0.5)
                            ai_response = await self.chess_ai.make_ai_move(user_id)
                            if ai_response["type"] == "ai_move":
                                response_text += f"\n\n🤖 ИИ сделал первый ход!"
                    else:
                        response_text = "Ошибка при создании игры."
                else:
                    response_text = "Ошибка при настройке игры."
                    
            elif action == 'player_move':
                # Ход игрока
                move_data = {
                    'from': data.get('from'),
                    'to': data.get('to')
                }
                
                move_response = self.chess_ai.make_move(user_id, move_data)
                
                if move_response["type"] == "move_success":
                    response_text = "✅ Отличный ход, товарищ!"
                    
                    # Автоматический ход ИИ
                    await asyncio.sleep(0.5)
                    ai_response = await self.chess_ai.make_ai_move(user_id)
                    
                    if ai_response["type"] == "ai_move":
                        response_text += f"\n\n🤖 {ai_response.get('yakov_comment', 'ИИ ответил!')}"
                        
                elif move_response["type"] == "invalid_move":
                    response_text = f"❌ {move_response['message']}"
                else:
                    response_text = "Что-то пошло не так с ходом."
                    
            elif action == 'request_hint':
                # Подсказка от Якова
                hints = [
                    "Ищите форсированные варианты - шах, взятие, угроза!",
                    "Обратите внимание на безопасность своего короля.",
                    "Как говорится, лучшая защита - это нападение!",
                    "Контролируйте центр доски, товарищ!",
                    "Развивайте фигуры и рокируйтесь пораньше."
                ]
                import random
                response_text = f"💡 Совет от Якова: {random.choice(hints)}"
                
            elif action == 'resign_game':
                # Сдача игры
                self.chess_ai.end_game(user_id)
                response_text = "🏳️ Игра окончена. Не расстраивайтесь - каждая партия учит нас!"
                
            elif action == 'test_connection':
                # Тест связи
                response_text = "🔌 Связь с Mini App работает отлично! Как говорится, все под контролем, товарищ!"
                
            else:
                # Старые задачи через MiniAppHandler
                response_data = self.mini_app_handler.handle_mini_app_data(user_id, message.web_app_data.data)
                response_text = self.mini_app_handler.format_mini_app_response(response_data)
            
            # Применяем влияние настроения
            response_text = self.mood_system.get_mood_influenced_response(response_text)
            
            await message.reply(response_text)
            
        except Exception as e:
            logger.error(f"Ошибка при обработке данных Mini App: {e}")
            await message.reply("Произошла ошибка при обработке данных приложения. Попробуйте еще раз!")
    
    async def handle_callback(self, callback_query: types.CallbackQuery):
        """Обработка callback кнопок"""
        try:
            data = callback_query.data
            user_id = callback_query.from_user.id
            
            # ШАХМАТЫ ВРЕМЕННО ОТКЛЮЧЕНЫ
            if False and data.startswith("chess_difficulty_"):
                # Выбор сложности шахмат
                difficulty_id = data.replace("chess_difficulty_", "")
                response_data = self.chess_ai.set_difficulty(user_id, difficulty_id)
                
                if response_data["type"] == "setup" and response_data["setup_step"] == "color":
                    # Создаем клавиатуру для выбора цвета
                    keyboard = InlineKeyboardMarkup()
                    for color in response_data["data"]["colors"]:
                        button = InlineKeyboardButton(
                            text=f"{color['pieces']} {color['name']} - {color['description']}",
                            callback_data=f"chess_color_{color['id']}"
                        )
                        keyboard.add(button)
                    
                    await callback_query.message.edit_text(
                        f"""{response_data['message']}

🎨 **Выберите цвет фигур:**

Как говорится, товарищ, каждый цвет имеет свои преимущества!""",
                        reply_markup=keyboard,
                        parse_mode='Markdown'
                    )
                
            elif False and data.startswith("chess_color_"):
                # Выбор цвета и старт игры
                color_id = data.replace("chess_color_", "")
                response_data = self.chess_ai.set_color_and_start(user_id, color_id)
                
                if response_data["type"] == "game_start":
                    await callback_query.message.edit_text(
                        f"""{response_data["message"]}

🎯 **Игра началась!** Используйте команды:
• `/chess board` - показать доску
• `/chess move e2 e4` - сделать ход
• `/chess status` - статус игры
• `/chess end` - завершить игру

{self._format_board_ascii(response_data["board_data"]["board"])}""",
                        parse_mode='Markdown'
                    )
                    
                    # Если ходит ИИ первым (игрок выбрал черные)
                    if response_data["game"]["current_turn"] != response_data["game"]["player_color"]:
                        await asyncio.sleep(1)
                        ai_response = await self.chess_ai.make_ai_move(user_id)
                        if ai_response["type"] == "ai_move":
                            await callback_query.message.reply(
                                f"{ai_response['message']}\n\n{ai_response['yakov_comment']}\n\n🎯 Теперь ваш ход!\n\n{self._format_board_ascii(ai_response['board_data']['board'])}",
                                parse_mode='Markdown'
                            )
                            
            elif False and data == "simple_chess_puzzle":
                puzzles = [
                    "♟️ **Простая задача от Якова:**\n\nБелые: Король h1, Ферзь d1\nЧерные: Король h8\n\n🎯 Мат в 1 ход! Как говорится, иногда решение лежит на поверхности.",
                    "♟️ **Классическая задача:**\n\nБелые: Король g1, Ладья a8\nЧерные: Король a1\n\n🎯 Найдите мат в 2 хода! В советское время такие задачи решали в шахматных кружках.",
                    "♟️ **Тактическая задача:**\n\nБелые: Король e1, Конь f3\nЧерные: Король e8, Пешка e7\n\n🎯 Как атаковать сразу две фигуры? Думайте о вилке!"
                ]
                
                import random
                puzzle = random.choice(puzzles)
                puzzle = self.mood_system.get_mood_influenced_response(puzzle)
                
                await callback_query.message.reply(puzzle)
                
            await callback_query.answer()
                
        except Exception as e:
            logger.error(f"Ошибка при обработке callback: {e}")
            await callback_query.answer("Произошла ошибка!")
    
    def _format_board_ascii(self, board: List[List[str]]) -> str:
        """Форматирование доски в ASCII для отображения в чате"""
        pieces_unicode = {
            'K': '♔', 'Q': '♕', 'R': '♖', 'B': '♗', 'N': '♘', 'P': '♙',
            'k': '♚', 'q': '♛', 'r': '♜', 'b': '♝', 'n': '♞', 'p': '♟'
        }
        
        result = "```\n  a b c d e f g h\n"
        for i, row in enumerate(board):
            rank = 8 - i
            line = f"{rank} "
            for piece in row:
                if piece:
                    line += pieces_unicode.get(piece, piece) + " "
                else:
                    line += "· "
            line += f"{rank}"
            result += line + "\n"
        result += "  a b c d e f g h\n```"
        return result
    
    def get_technical_advice(self) -> str:
        """Технический совет дня (заглушка)"""
        advice_list = [
            "💡 Совет дня: Всегда проверяйте соответствие документации ГОСТу перед сдачей проекта!",
            "💡 Помните, товарищ: лучше потратить час на планирование, чем неделю на исправление ошибок.",
            "💡 В советское время говорили: 'Семь раз отмерь, один раз отрежь'. Это касается и программирования!"
        ]
        import random
        return random.choice(advice_list)
    
    def get_current_mood(self) -> str:
        """Текущее настроение Якова с учетом всех факторов"""
        return self.mood_system.get_mood_description()
    
    def get_weather_info(self) -> str:
        """Информация о погоде в Новороссийске"""
        weather_comment = self.mood_system.get_weather_comment()
        return f"🌤️ **Погода в Новороссийске**\n\n{weather_comment}\n\n💭 Погода всегда влияет на мое настроение, товарищ. Живу здесь уже полвека - знаю все капризы местного климата!"
    
    def start_technical_dispute(self, user_id: int, statement: str) -> str:
        """Начало технического спора"""
        response = self.dispute_system.start_dispute(user_id, statement)
        
        if response:
            return response
        else:
            return self.get_dispute_help()
    
    def continue_technical_dispute(self, user_id: int, message: str) -> Optional[str]:
        """Продолжение технического спора"""
        # Проверяем, есть ли активный спор
        if user_id in self.dispute_system.active_disputes:
            return self.dispute_system.continue_dispute(user_id, message)
        
        # Пытаемся начать новый спор
        response = self.dispute_system.start_dispute(user_id, message)
        return response
    
    def get_dispute_help(self) -> str:
        """Справка по спорам"""
        topics = self.dispute_system.get_available_topics()
        topic_summaries = []
        
        for topic in topics[:5]:  # Показываем первые 5 тем
            summary = self.dispute_system.get_topic_summary(topic)
            topic_summaries.append(f"• {summary}")
        
        return f"""🥊 **Споры с Яковом Давидовичем**

Товарищ, готовы поспорить о технических вопросах? Я отстаиваю позиции, основанные на советском опыте!

📋 **Как спорить:**
/dispute <ваше утверждение> - начать спор
Или просто напишите техническое утверждение - я его подхвачу!

🎯 **Мои любимые темы для споров:**
{chr(10).join(topic_summaries)}

💡 **Примеры:**
• /dispute современные фреймворки удобнее чистого кода
• /dispute agile лучше водопадной модели  
• /dispute качество кода не важно

Помните: в споре рождается истина! 😤"""
    
    def get_help_message(self) -> str:
        """Справка по командам"""
        return """🤖 Приветствую, товарищ! Я - Яков Давидович, ваш технический консультант.

📋 **Команды для работы с ГОСТами:**
/gost <номер> - подробная информация о ГОСТе
/gost <задача> - рекомендации ГОСТов для задачи

📖 **Команды для историй:**
/story - случайная история из моей жизни
/story <категория> - история определенной категории
/story <настроение> - история в определенном настроении

⚡ **Игры и развлечения:**
# /chess - временно отключено для технических работ
/dispute - поспорить о технических решениях

🔧 **Другие команды:**
/advice - технический совет дня
/mood - мое текущее настроение
/mood weather - погода в Новороссийске
/help - эта справка

💡 **Примеры использования:**
• /gost 2.105-95
• /gost оформление документации
• /story техническая
• /story философская
• /story ностальгическое

Можете также просто задавать вопросы - отвечу как опытный советский инженер!"""
        
    async def handle_message(self, message: types.Message):
        """Обработка обычных сообщений (НЕ команд)"""
        processing_message = None
        try:
            logger.info(f"Получено обычное сообщение: {message.text}")
            
            # Отправляем индикатор обработки для всех обычных сообщений
            processing_message = await self.send_processing_indicator(message)
            
            # Классификация сообщения
            msg_type = self.classifier.classify_message(message.text)
            logger.info(f"Тип сообщения: {msg_type}")
            
            if msg_type == 'technical':
                logger.info("Обрабатываем технический запрос...")
                # Поиск информации о ГОСТах
                gost_info = self.gost_parser.search_gost(message.text)
                response = self.format_technical_response(gost_info)

            else:
                logger.info("Обрабатываем коммуникационный запрос...")
                
                # Сначала проверяем, не хочет ли пользователь поспорить
                dispute_response = self.continue_technical_dispute(message.from_user.id, message.text)
                if dispute_response:
                    response = dispute_response
                else:
                    # Генерация обычного ответа для общения
                    response = self.generate_response(message.text)
                    
                    # С вероятностью 10% добавляем случайную историю
                    if random.random() < 0.1:
                        story = self.story_system.get_random_story()
                        story_text = self.story_system.format_story(story, include_moral=False)
                        response += f"\n\n📖 *Кстати, вспомнил историю:*\n{story_text}"
            
            # Применяем влияние настроения к ответу
            response = self.mood_system.get_mood_influenced_response(response)
            
            # Удаляем индикатор обработки
            await self.delete_processing_indicator(processing_message)
            
            logger.info(f"Отправляем ответ: {response}")
            # Отправка ответа
            await message.reply(response, parse_mode='Markdown')
            
        except Exception as e:
            # Удаляем индикатор в случае ошибки
            await self.delete_processing_indicator(processing_message)
            error_msg = f"Ошибка при обработке сообщения: {str(e)}"
            logger.error(error_msg)
            await message.reply("Произошла ошибка при обработке вашего сообщения. Попробуйте позже.")
            
    async def start(self):
        """Запуск бота"""
        try:
            logger.info("Бот запущен")
            await self.dp.start_polling()
        except Exception as e:
            logger.error(f"Ошибка при запуске бота: {e}")
        finally:
            await self.bot.close()

if __name__ == "__main__":
    bot = VeteranAIBot()
    asyncio.run(bot.start())
