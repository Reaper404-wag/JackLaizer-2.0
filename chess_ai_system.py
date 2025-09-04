#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Система шахмат с ИИ для бота Якова Давидовича
Полноценная игра против искусственного интеллекта
"""

import json
import random
import logging
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass
from enum import Enum
import asyncio
import aiohttp

logger = logging.getLogger(__name__)

class Difficulty(Enum):
    """Уровни сложности ИИ"""
    BEGINNER = ("Новичок", 1, "Для тех, кто только учится")
    EASY = ("Легкий", 3, "Простые комбинации")
    MEDIUM = ("Средний", 5, "Тактические задачи")
    HARD = ("Сложный", 7, "Стратегическое мышление")
    EXPERT = ("Эксперт", 9, "Как Яков в молодости!")

class Color(Enum):
    """Цвета фигур"""
    WHITE = ("white", "Белые", "♔♕♖♗♘♙")
    BLACK = ("black", "Черные", "♚♛♜♝♞♟")

class GameState(Enum):
    """Состояния игры"""
    SETUP = "setup"
    PLAYING = "playing"
    PAUSED = "paused"
    FINISHED = "finished"

@dataclass
class ChessGame:
    """Объект шахматной партии"""
    user_id: int
    player_color: Color
    difficulty: Difficulty
    state: GameState
    board: List[List[str]]
    moves_history: List[Dict]
    current_turn: Color
    game_id: str
    ai_thinking: bool = False
    last_move: Optional[Dict] = None
    captured_pieces: Dict[str, List[str]] = None
    
    def __post_init__(self):
        if self.captured_pieces is None:
            self.captured_pieces = {"white": [], "black": []}

class ChessAISystem:
    """Система шахмат с ИИ"""
    
    def __init__(self):
        self.active_games: Dict[int, ChessGame] = {}
        self.chess_api_url = "https://chess-api.com/v1"  # Placeholder API
        
        # Начальная позиция шахматной доски
        self.initial_board = [
            ['r', 'n', 'b', 'q', 'k', 'b', 'n', 'r'],
            ['p', 'p', 'p', 'p', 'p', 'p', 'p', 'p'],
            ['', '', '', '', '', '', '', ''],
            ['', '', '', '', '', '', '', ''],
            ['', '', '', '', '', '', '', ''],
            ['', '', '', '', '', '', '', ''],
            ['P', 'P', 'P', 'P', 'P', 'P', 'P', 'P'],
            ['R', 'N', 'B', 'Q', 'K', 'B', 'N', 'R']
        ]
        
        # Unicode фигуры
        self.pieces_unicode = {
            'K': '♔', 'Q': '♕', 'R': '♖', 'B': '♗', 'N': '♘', 'P': '♙',
            'k': '♚', 'q': '♛', 'r': '♜', 'b': '♝', 'n': '♞', 'p': '♟'
        }
    
    def start_game_setup(self, user_id: int) -> Dict[str, Any]:
        """Начать настройку новой игры"""
        return {
            "type": "setup",
            "message": "🎯 Настройка новой партии",
            "setup_step": "difficulty",
            "data": {
                "difficulties": [
                    {
                        "id": diff.name.lower(),
                        "name": diff.value[0],
                        "level": diff.value[1],
                        "description": diff.value[2]
                    }
                    for diff in Difficulty
                ]
            }
        }
    
    def set_difficulty(self, user_id: int, difficulty_id: str) -> Dict[str, Any]:
        """Установить сложность игры"""
        try:
            difficulty = Difficulty[difficulty_id.upper()]
            
            # Сохраняем выбор в временном хранилище
            if not hasattr(self, '_temp_setups'):
                self._temp_setups = {}
            
            self._temp_setups[user_id] = {"difficulty": difficulty}
            
            return {
                "type": "setup",
                "message": f"🎯 Выбрана сложность: {difficulty.value[0]}",
                "setup_step": "color",
                "data": {
                    "colors": [
                        {
                            "id": "white",
                            "name": "Белые",
                            "description": "Первый ход - ваш!",
                            "pieces": "♔♕♖♗♘♙"
                        },
                        {
                            "id": "black", 
                            "name": "Черные",
                            "description": "Классический выбор",
                            "pieces": "♚♛♜♝♞♟"
                        }
                    ]
                }
            }
        except KeyError:
            return {"type": "error", "message": "Неверная сложность!"}
    
    def set_color_and_start(self, user_id: int, color_id: str) -> Dict[str, Any]:
        """Установить цвет и начать игру"""
        try:
            color = Color.WHITE if color_id == "white" else Color.BLACK
            
            if not hasattr(self, '_temp_setups') or user_id not in self._temp_setups:
                return {"type": "error", "message": "Сначала выберите сложность!"}
            
            difficulty = self._temp_setups[user_id]["difficulty"]
            
            # Создаем новую игру
            game_id = f"game_{user_id}_{random.randint(1000, 9999)}"
            
            game = ChessGame(
                user_id=user_id,
                player_color=color,
                difficulty=difficulty,
                state=GameState.PLAYING,
                board=[row[:] for row in self.initial_board],  # Копия доски
                moves_history=[],
                current_turn=Color.WHITE,  # Белые всегда ходят первыми
                game_id=game_id
            )
            
            self.active_games[user_id] = game
            
            # Очищаем временные настройки
            del self._temp_setups[user_id]
            
            return {
                "type": "game_start",
                "message": f"🎮 Игра началась!\n\n"
                          f"🎯 Сложность: {difficulty.value[0]}\n"
                          f"🎨 Вы играете: {color.value[1]}\n"
                          f"⭐ {'Ваш ход!' if color == Color.WHITE else 'Ходит ИИ...'}",
                "game": self._game_to_dict(game),
                "board_data": self._get_board_data(game)
            }
            
        except Exception as e:
            logger.error(f"Ошибка при создании игры: {e}")
            return {"type": "error", "message": "Ошибка при создании игры"}
    
    def make_move(self, user_id: int, move_data: Dict) -> Dict[str, Any]:
        """Сделать ход игрока"""
        if user_id not in self.active_games:
            return {"type": "error", "message": "Игра не найдена"}
        
        game = self.active_games[user_id]
        
        if game.state != GameState.PLAYING:
            return {"type": "error", "message": "Игра не активна"}
        
        if game.current_turn != game.player_color:
            return {"type": "error", "message": "Не ваш ход!"}
        
        # Валидация и выполнение хода
        move_result = self._validate_and_make_move(game, move_data)
        
        if not move_result["valid"]:
            return {
                "type": "invalid_move",
                "message": f"❌ {move_result['reason']}",
                "board_data": self._get_board_data(game)
            }
        
        # Ход успешен, переключаем на ИИ
        game.current_turn = Color.BLACK if game.player_color == Color.WHITE else Color.WHITE
        game.moves_history.append(move_result["move"])
        
        response = {
            "type": "move_success",
            "message": "✅ Ход принят! ИИ думает...",
            "game": self._game_to_dict(game),
            "board_data": self._get_board_data(game),
            "last_move": move_result["move"]
        }
        
        # Проверяем на мат/пат
        game_status = self._check_game_status(game)
        if game_status["finished"]:
            game.state = GameState.FINISHED
            response["game_finished"] = game_status
            return response
        
        # Запускаем ход ИИ асинхронно
        game.ai_thinking = True
        
        return response
    
    async def make_ai_move(self, user_id: int) -> Dict[str, Any]:
        """Сделать ход ИИ"""
        if user_id not in self.active_games:
            return {"type": "error", "message": "Игра не найдена"}
        
        game = self.active_games[user_id]
        game.ai_thinking = False
        
        # Генерируем ход ИИ
        ai_move = await self._generate_ai_move(game)
        
        if not ai_move:
            return {"type": "error", "message": "ИИ не может сделать ход"}
        
        # Выполняем ход ИИ
        self._execute_move(game, ai_move)
        game.current_turn = game.player_color
        game.moves_history.append(ai_move)
        
        # Проверяем статус игры
        game_status = self._check_game_status(game)
        
        response = {
            "type": "ai_move",
            "message": f"🤖 ИИ сделал ход: {self._move_to_notation(ai_move)}",
            "game": self._game_to_dict(game),
            "board_data": self._get_board_data(game),
            "ai_move": ai_move,
            "yakov_comment": self._get_yakov_chess_comment(ai_move, game)
        }
        
        if game_status["finished"]:
            game.state = GameState.FINISHED
            response["game_finished"] = game_status
        
        return response
    
    def get_possible_moves(self, user_id: int, from_pos: Dict) -> Dict[str, Any]:
        """Получить возможные ходы для фигуры"""
        if user_id not in self.active_games:
            return {"type": "error", "message": "Игра не найдена"}
        
        game = self.active_games[user_id]
        row, col = from_pos["row"], from_pos["col"]
        
        if not (0 <= row < 8 and 0 <= col < 8):
            return {"possible_moves": []}
        
        piece = game.board[row][col]
        if not piece:
            return {"possible_moves": []}
        
        # Проверяем, что это фигура игрока
        piece_color = Color.WHITE if piece.isupper() else Color.BLACK
        if piece_color != game.player_color:
            return {"possible_moves": []}
        
        moves = self._calculate_possible_moves(game, row, col, piece)
        
        return {
            "type": "possible_moves",
            "possible_moves": moves,
            "piece": piece,
            "from": {"row": row, "col": col}
        }
    
    def _validate_and_make_move(self, game: ChessGame, move_data: Dict) -> Dict[str, Any]:
        """Валидация и выполнение хода"""
        from_pos = move_data["from"]
        to_pos = move_data["to"]
        
        from_row, from_col = from_pos["row"], from_pos["col"]
        to_row, to_col = to_pos["row"], to_pos["col"]
        
        # Проверки валидности
        if not (0 <= from_row < 8 and 0 <= from_col < 8 and 0 <= to_row < 8 and 0 <= to_col < 8):
            return {"valid": False, "reason": "Ход за пределы доски"}
        
        piece = game.board[from_row][from_col]
        if not piece:
            return {"valid": False, "reason": "Нет фигуры на исходной клетке"}
        
        # Проверяем цвет фигуры
        piece_color = Color.WHITE if piece.isupper() else Color.BLACK
        if piece_color != game.player_color:
            return {"valid": False, "reason": "Это не ваша фигура"}
        
        # Проверяем возможность хода
        possible_moves = self._calculate_possible_moves(game, from_row, from_col, piece)
        target_move = next((m for m in possible_moves if m["row"] == to_row and m["col"] == to_col), None)
        
        if not target_move:
            return {"valid": False, "reason": "Недопустимый ход для этой фигуры"}
        
        # Выполняем ход
        captured_piece = game.board[to_row][to_col]
        move = {
            "from": {"row": from_row, "col": from_col},
            "to": {"row": to_row, "col": to_col},
            "piece": piece,
            "captured": captured_piece,
            "notation": self._move_to_notation({"from": from_pos, "to": to_pos, "piece": piece}),
            "move_type": target_move.get("move_type", "normal")
        }
        
        # Делаем ход на доске
        game.board[to_row][to_col] = piece
        game.board[from_row][from_col] = ""
        
        # Добавляем взятую фигуру
        if captured_piece:
            color_key = "white" if captured_piece.isupper() else "black"
            game.captured_pieces[color_key].append(captured_piece)
        
        return {"valid": True, "move": move}
    
    def _calculate_possible_moves(self, game: ChessGame, row: int, col: int, piece: str) -> List[Dict]:
        """Вычисление возможных ходов для фигуры"""
        moves = []
        piece_type = piece.lower()
        is_white = piece.isupper()
        
        if piece_type == 'p':  # Пешка
            direction = -1 if is_white else 1
            start_row = 6 if is_white else 1
            
            # Ход вперед
            new_row = row + direction
            if 0 <= new_row < 8 and not game.board[new_row][col]:
                moves.append({"row": new_row, "col": col, "move_type": "normal"})
                
                # Двойной ход с начальной позиции
                if row == start_row and not game.board[new_row + direction][col]:
                    moves.append({"row": new_row + direction, "col": col, "move_type": "double"})
            
            # Взятие по диагонали
            for dc in [-1, 1]:
                new_col = col + dc
                if 0 <= new_row < 8 and 0 <= new_col < 8:
                    target = game.board[new_row][new_col]
                    if target and (target.isupper() != is_white):
                        moves.append({"row": new_row, "col": new_col, "move_type": "capture"})
        
        elif piece_type == 'r':  # Ладья
            directions = [(0, 1), (0, -1), (1, 0), (-1, 0)]
            moves.extend(self._get_line_moves(game, row, col, directions, is_white))
        
        elif piece_type == 'b':  # Слон
            directions = [(1, 1), (1, -1), (-1, 1), (-1, -1)]
            moves.extend(self._get_line_moves(game, row, col, directions, is_white))
        
        elif piece_type == 'q':  # Ферзь
            directions = [(0, 1), (0, -1), (1, 0), (-1, 0), (1, 1), (1, -1), (-1, 1), (-1, -1)]
            moves.extend(self._get_line_moves(game, row, col, directions, is_white))
        
        elif piece_type == 'n':  # Конь
            knight_moves = [(-2, -1), (-2, 1), (-1, -2), (-1, 2), (1, -2), (1, 2), (2, -1), (2, 1)]
            for dr, dc in knight_moves:
                new_row, new_col = row + dr, col + dc
                if 0 <= new_row < 8 and 0 <= new_col < 8:
                    target = game.board[new_row][new_col]
                    if not target:
                        moves.append({"row": new_row, "col": new_col, "move_type": "normal"})
                    elif target.isupper() != is_white:
                        moves.append({"row": new_row, "col": new_col, "move_type": "capture"})
        
        elif piece_type == 'k':  # Король
            king_moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1)]
            for dr, dc in king_moves:
                new_row, new_col = row + dr, col + dc
                if 0 <= new_row < 8 and 0 <= new_col < 8:
                    target = game.board[new_row][new_col]
                    if not target:
                        moves.append({"row": new_row, "col": new_col, "move_type": "normal"})
                    elif target.isupper() != is_white:
                        moves.append({"row": new_row, "col": new_col, "move_type": "capture"})
        
        return moves
    
    def _get_line_moves(self, game: ChessGame, row: int, col: int, directions: List[Tuple], is_white: bool) -> List[Dict]:
        """Получить ходы по линиям (для ладьи, слона, ферзя)"""
        moves = []
        
        for dr, dc in directions:
            for i in range(1, 8):
                new_row, new_col = row + dr * i, col + dc * i
                
                if not (0 <= new_row < 8 and 0 <= new_col < 8):
                    break
                
                target = game.board[new_row][new_col]
                
                if not target:
                    moves.append({"row": new_row, "col": new_col, "move_type": "normal"})
                else:
                    if target.isupper() != is_white:
                        moves.append({"row": new_row, "col": new_col, "move_type": "capture"})
                    break
        
        return moves
    
    async def _generate_ai_move(self, game: ChessGame) -> Optional[Dict]:
        """Генерация хода ИИ"""
        # Простой ИИ для демонстрации
        ai_color = Color.BLACK if game.player_color == Color.WHITE else Color.WHITE
        is_white = ai_color == Color.WHITE
        
        all_moves = []
        
        # Собираем все возможные ходы ИИ
        for row in range(8):
            for col in range(8):
                piece = game.board[row][col]
                if piece and (piece.isupper() == is_white):
                    piece_moves = self._calculate_possible_moves(game, row, col, piece)
                    for move in piece_moves:
                        all_moves.append({
                            "from": {"row": row, "col": col},
                            "to": {"row": move["row"], "col": move["col"]},
                            "piece": piece,
                            "move_type": move.get("move_type", "normal")
                        })
        
        if not all_moves:
            return None
        
        # Простая стратегия: приоритет взятию, потом случайный ход
        capture_moves = [m for m in all_moves if game.board[m["to"]["row"]][m["to"]["col"]]]
        
        if capture_moves and game.difficulty.value[1] >= 3:
            return random.choice(capture_moves)
        
        return random.choice(all_moves)
    
    def _execute_move(self, game: ChessGame, move: Dict):
        """Выполнить ход на доске"""
        from_pos = move["from"]
        to_pos = move["to"]
        
        captured = game.board[to_pos["row"]][to_pos["col"]]
        
        game.board[to_pos["row"]][to_pos["col"]] = move["piece"]
        game.board[from_pos["row"]][from_pos["col"]] = ""
        
        if captured:
            color_key = "white" if captured.isupper() else "black"
            game.captured_pieces[color_key].append(captured)
        
        move["captured"] = captured
        move["notation"] = self._move_to_notation(move)
    
    def _check_game_status(self, game: ChessGame) -> Dict[str, Any]:
        """Проверка статуса игры (мат, пат, ничья)"""
        # Упрощенная проверка для демонстрации
        return {"finished": False, "result": None, "reason": None}
    
    def _move_to_notation(self, move: Dict) -> str:
        """Конвертация хода в шахматную нотацию"""
        piece = move["piece"].upper()
        from_pos = move["from"]
        to_pos = move["to"]
        
        files = "abcdefgh"
        from_square = f"{files[from_pos['col']]}{8 - from_pos['row']}"
        to_square = f"{files[to_pos['col']]}{8 - to_pos['row']}"
        
        capture = "x" if move.get("captured") else ""
        
        if piece == "P":
            return f"{from_square[0] if capture else ''}{capture}{to_square}"
        else:
            return f"{piece}{capture}{to_square}"
    
    def _get_board_data(self, game: ChessGame) -> Dict[str, Any]:
        """Получить данные доски для фронтенда"""
        return {
            "board": game.board,
            "current_turn": game.current_turn.value[0],
            "player_color": game.player_color.value[0],
            "last_move": game.last_move,
            "captured": game.captured_pieces
        }
    
    def _game_to_dict(self, game: ChessGame) -> Dict[str, Any]:
        """Конвертация игры в словарь"""
        return {
            "game_id": game.game_id,
            "player_color": game.player_color.value[0],
            "difficulty": game.difficulty.name.lower(),
            "state": game.state.value,
            "current_turn": game.current_turn.value[0],
            "moves_count": len(game.moves_history),
            "ai_thinking": game.ai_thinking
        }
    
    def _get_yakov_chess_comment(self, move: Dict, game: ChessGame) -> str:
        """Комментарий Якова о ходе"""
        comments = [
            "Интересный ход! Как говорится, каждая фигура имеет свою ценность.",
            "Хорошая тактика! В советское время мы так же обдумывали каждый шаг.",
            "Классический прием! Эту позицию я изучал еще в шахматном кружке.",
            "Неплохо, товарищ! Но помните - в шахматах важна не только атака.",
            "Как говорил мой учитель: 'Шахматы - это война на 64 клетках'.",
            "Вижу, что вы думаете стратегически. Это правильный подход!",
            "Такой ход мы называли 'инженерным' - точный и выверенный."
        ]
        
        return f'"{random.choice(comments)}"'
    
    def get_game_status(self, user_id: int) -> Optional[Dict[str, Any]]:
        """Получить статус текущей игры"""
        if user_id in self.active_games:
            game = self.active_games[user_id]
            return {
                "has_game": True,
                "game": self._game_to_dict(game),
                "board_data": self._get_board_data(game)
            }
        return {"has_game": False}
    
    def end_game(self, user_id: int) -> Dict[str, Any]:
        """Завершить игру"""
        if user_id in self.active_games:
            del self.active_games[user_id]
            return {"message": "Игра завершена. Было приятно сыграть!"}
        return {"message": "Активная игра не найдена"}
