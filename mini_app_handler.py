#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Обработчик Mini App для шахматных задач Якова Давидовича
"""

import json
import logging
from typing import Dict, Any, Optional
from dataclasses import dataclass
import random

@dataclass
class ChessMove:
    """Шахматный ход"""
    row: int
    col: int
    piece: Optional[str] = None

@dataclass
class ChessPuzzle:
    """Шахматная задача"""
    id: str
    title: str
    description: str
    position: list
    solution: list
    difficulty: int  # 1-5
    yakovs_comment: str

class MiniAppHandler:
    """Обработчик Mini App"""
    
    def __init__(self):
        self.chess_puzzles = self._load_chess_puzzles()
        self.user_progress = {}  # В реальности это была бы база данных
        
    def _load_chess_puzzles(self) -> Dict[str, ChessPuzzle]:
        """Загрузка шахматных задач"""
        puzzles = {
            "mate_in_2_easy": ChessPuzzle(
                id="mate_in_2_easy",
                title="Мат в 2 хода (легкая)",
                description="Белые начинают и дают мат в два хода. Классическая задача для начинающих.",
                position=[
                    ['r', '', 'b', 'q', 'k', 'b', 'n', 'r'],
                    ['p', 'p', 'p', 'p', '', 'p', 'p', 'p'],
                    ['', '', 'n', '', '', '', '', ''],
                    ['', '', '', '', 'p', '', '', ''],
                    ['', '', '', '', 'P', '', '', ''],
                    ['', '', '', '', '', 'N', '', ''],
                    ['P', 'P', 'P', 'P', '', 'P', 'P', 'P'],
                    ['R', 'N', 'B', 'Q', 'K', 'B', '', 'R']
                ],
                solution=[(6, 3, 7, 3), (7, 4, 6, 3)],  # Пример решения
                difficulty=2,
                yakovs_comment="Хорошая базовая задача! В советское время мы такие решали в шахматных кружках."
            ),
            "tactical_fork": ChessPuzzle(
                id="tactical_fork",
                title="Тактическая вилка",
                description="Найдите способ атаковать сразу две фигуры противника.",
                position=[
                    ['r', '', '', 'q', 'k', 'b', 'n', 'r'],
                    ['p', 'p', 'b', 'p', '', 'p', 'p', 'p'],
                    ['', '', 'p', '', '', 'n', '', ''],
                    ['', '', '', '', 'p', '', '', ''],
                    ['', '', '', 'P', 'P', '', '', ''],
                    ['', '', 'N', '', '', '', '', ''],
                    ['P', 'P', 'P', '', '', 'P', 'P', 'P'],
                    ['R', '', 'B', 'Q', 'K', 'B', 'N', 'R']
                ],
                solution=[(5, 2, 3, 1)],  # Конь делает вилку
                difficulty=3,
                yakovs_comment="Вилка - мощное тактическое оружие! Как алгоритм, который решает две задачи одновременно."
            ),
            "endgame_study": ChessPuzzle(
                id="endgame_study",
                title="Эндшпильный этюд",
                description="Сложная позиция из эндшпиля. Требует точного расчета.",
                position=[
                    ['', '', '', '', '', '', '', ''],
                    ['', '', '', '', '', '', '', 'k'],
                    ['', '', '', '', '', '', 'P', ''],
                    ['', '', '', '', '', '', '', ''],
                    ['', '', '', '', '', '', '', ''],
                    ['', '', '', '', '', 'K', '', ''],
                    ['', '', '', '', '', '', '', ''],
                    ['', '', '', '', '', '', '', '']
                ],
                solution=[(5, 5, 4, 6), (7, 1, 6, 1), (4, 6, 5, 7)],
                difficulty=5,
                yakovs_comment="Эндшпиль - это высшая математика шахмат! Каждый ход должен быть точным, как в программе."
            )
        }
        return puzzles
    
    def handle_mini_app_data(self, user_id: int, data: str) -> Dict[str, Any]:
        """Обработка данных от Mini App"""
        try:
            parsed_data = json.loads(data)
            action = parsed_data.get('action')
            
            if action == 'chess_move':
                return self._handle_chess_move(user_id, parsed_data)
            elif action == 'get_puzzle':
                return self._get_puzzle(user_id, parsed_data.get('difficulty', 2))
            elif action == 'ask_yakov':
                return self._handle_yakov_question(user_id)
            elif action == 'get_stats':
                return self._get_user_stats(user_id)
            else:
                return {'error': 'Unknown action'}
                
        except json.JSONDecodeError:
            return {'error': 'Invalid JSON data'}
        except Exception as e:
            logging.error(f"Error handling mini app data: {e}")
            return {'error': 'Internal error'}
    
    def _handle_chess_move(self, user_id: int, data: Dict) -> Dict[str, Any]:
        """Обработка шахматного хода"""
        row = data.get('row')
        col = data.get('col')
        
        # Получаем текущую задачу пользователя
        current_puzzle = self._get_user_current_puzzle(user_id)
        
        if not current_puzzle:
            return {
                'type': 'move_response',
                'message': 'Сначала выберите задачу для решения!',
                'yakovs_comment': 'Товарищ, без задачи ходы делать бессмысленно!'
            }
        
        # Проверяем правильность хода
        is_correct = self._check_move(current_puzzle, row, col)
        
        if is_correct:
            self._update_user_progress(user_id, current_puzzle.id, True)
            yakovs_responses = [
                "Отлично! Правильный ход, товарищ!",
                "Молодец! Как говорится, практика - критерий истины!",
                "Точно! В советское время мы так и учились - методом проб.",
                "Браво! Этот ход я бы и сам сделал!"
            ]
            return {
                'type': 'move_response',
                'correct': True,
                'message': 'Правильный ход!',
                'yakovs_comment': random.choice(yakovs_responses),
                'next_puzzle': self._get_next_puzzle_id(current_puzzle.difficulty)
            }
        else:
            yakovs_responses = [
                "Не совсем так, товарищ. Подумайте еще!",
                "Этот ход не ведет к цели. Попробуйте другой подход.",
                "Как говорится, поспешишь - людей насмешишь. Подумайте внимательнее!",
                "Не тот ход! В шахматах, как в программировании, важна логика."
            ]
            return {
                'type': 'move_response',
                'correct': False,
                'message': 'Попробуйте другой ход',
                'yakovs_comment': random.choice(yakovs_responses),
                'hint': self._get_move_hint(current_puzzle)
            }
    
    def _check_move(self, puzzle: ChessPuzzle, row: int, col: int) -> bool:
        """Проверка правильности хода"""
        # Упрощенная проверка - в реальности нужна полная шахматная логика
        solution_squares = []
        for move in puzzle.solution:
            if len(move) >= 2:
                solution_squares.extend([(move[0], move[1]), (move[2], move[3])])
        
        return (row, col) in solution_squares
    
    def _get_move_hint(self, puzzle: ChessPuzzle) -> str:
        """Получение подсказки для хода"""
        hints = {
            1: "Ищите шах королю противника!",
            2: "Обратите внимание на незащищенные фигуры.",
            3: "Попробуйте найти тактический удар.",
            4: "Думайте о контроле ключевых полей.",
            5: "В эндшпиле каждый темп на счету!"
        }
        return hints.get(puzzle.difficulty, "Подумайте о цели позиции!")
    
    def _get_puzzle(self, user_id: int, difficulty: int) -> Dict[str, Any]:
        """Получение задачи по сложности"""
        suitable_puzzles = [p for p in self.chess_puzzles.values() 
                          if p.difficulty == difficulty]
        
        if not suitable_puzzles:
            suitable_puzzles = list(self.chess_puzzles.values())
        
        puzzle = random.choice(suitable_puzzles)
        self._set_user_current_puzzle(user_id, puzzle.id)
        
        return {
            'type': 'puzzle',
            'puzzle': {
                'id': puzzle.id,
                'title': puzzle.title,
                'description': puzzle.description,
                'position': puzzle.position,
                'difficulty': puzzle.difficulty,
                'yakovs_comment': puzzle.yakovs_comment
            }
        }
    
    def _handle_yakov_question(self, user_id: int) -> Dict[str, Any]:
        """Обработка вопроса к Якову"""
        responses = [
            "Задавайте вопрос, товарищ! Всегда рад помочь с техническими вопросами.",
            "Слушаю внимательно! Какая проблема вас беспокоит?",
            "Говорите, не стесняйтесь! Опыт - лучший учитель.",
            "Я весь внимание! В советское время мы всегда помогали коллегам."
        ]
        
        return {
            'type': 'yakov_response',
            'message': random.choice(responses),
            'suggestion': 'Напишите свой вопрос в чат с ботом!'
        }
    
    def _get_user_stats(self, user_id: int) -> Dict[str, Any]:
        """Получение статистики пользователя"""
        progress = self.user_progress.get(user_id, {})
        
        solved_count = len([p for p in progress.values() if p.get('solved', False)])
        total_attempts = sum(p.get('attempts', 0) for p in progress.values())
        accuracy = (solved_count / max(total_attempts, 1)) * 100 if total_attempts > 0 else 0
        
        return {
            'type': 'stats',
            'stats': {
                'solved_puzzles': solved_count,
                'total_attempts': total_attempts,
                'accuracy': round(accuracy, 1),
                'current_streak': progress.get('current_streak', 0)
            },
            'yakovs_comment': f"{'Отличные' if accuracy > 80 else 'Неплохие' if accuracy > 60 else 'Есть куда расти'} результаты! Продолжайте тренироваться!"
        }
    
    def _get_user_current_puzzle(self, user_id: int) -> Optional[ChessPuzzle]:
        """Получение текущей задачи пользователя"""
        progress = self.user_progress.get(user_id, {})
        current_puzzle_id = progress.get('current_puzzle')
        
        if current_puzzle_id and current_puzzle_id in self.chess_puzzles:
            return self.chess_puzzles[current_puzzle_id]
        return None
    
    def _set_user_current_puzzle(self, user_id: int, puzzle_id: str):
        """Установка текущей задачи пользователя"""
        if user_id not in self.user_progress:
            self.user_progress[user_id] = {}
        
        self.user_progress[user_id]['current_puzzle'] = puzzle_id
    
    def _update_user_progress(self, user_id: int, puzzle_id: str, solved: bool):
        """Обновление прогресса пользователя"""
        if user_id not in self.user_progress:
            self.user_progress[user_id] = {}
        
        if puzzle_id not in self.user_progress[user_id]:
            self.user_progress[user_id][puzzle_id] = {'attempts': 0, 'solved': False}
        
        self.user_progress[user_id][puzzle_id]['attempts'] += 1
        if solved:
            self.user_progress[user_id][puzzle_id]['solved'] = True
    
    def _get_next_puzzle_id(self, current_difficulty: int) -> str:
        """Получение ID следующей задачи"""
        next_puzzles = [p for p in self.chess_puzzles.values() 
                       if p.difficulty == current_difficulty]
        
        if next_puzzles:
            return random.choice(next_puzzles).id
        return list(self.chess_puzzles.keys())[0]
    
    def format_mini_app_response(self, response_data: Dict[str, Any]) -> str:
        """Форматирование ответа для отправки в чат"""
        response_type = response_data.get('type')
        
        if response_type == 'move_response':
            if response_data.get('correct'):
                return f"✅ {response_data['message']}\n\n👴 {response_data['yakovs_comment']}"
            else:
                return f"❌ {response_data['message']}\n\n👴 {response_data['yakovs_comment']}\n\n💡 Подсказка: {response_data.get('hint', '')}"
        
        elif response_type == 'yakov_response':
            return f"👴 {response_data['message']}\n\n💬 {response_data.get('suggestion', '')}"
        
        elif response_type == 'stats':
            stats = response_data['stats']
            return f"""📊 **Ваша статистика:**
            
🎯 Решено задач: {stats['solved_puzzles']}
🎲 Всего попыток: {stats['total_attempts']} 
📈 Точность: {stats['accuracy']}%
🔥 Текущая серия: {stats.get('current_streak', 0)}

👴 {response_data['yakovs_comment']}"""
        
        else:
            return "Mini App обработано успешно!"

def main():
    """Тестирование обработчика Mini App"""
    handler = MiniAppHandler()
    
    # Тест получения задачи
    puzzle_response = handler.handle_mini_app_data(123, '{"action": "get_puzzle", "difficulty": 2}')
    print("Получение задачи:")
    print(json.dumps(puzzle_response, ensure_ascii=False, indent=2))
    
    # Тест хода
    move_response = handler.handle_mini_app_data(123, '{"action": "chess_move", "row": 6, "col": 3}')
    print("\nОбработка хода:")
    print(handler.format_mini_app_response(move_response))

if __name__ == "__main__":
    main()
