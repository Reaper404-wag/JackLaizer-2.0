#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Расширенная система работы с ГОСТами для бота Якова Давидовича
"""

import json
import re
from typing import Dict, List, Optional, Tuple
from datetime import datetime
import requests
from dataclasses import dataclass

@dataclass
class GOSTInfo:
    """Информация о ГОСТе"""
    number: str
    title: str
    status: str  # "действующий", "отмененный", "заменен"
    description: str
    application_areas: List[str]
    replaced_by: Optional[str] = None
    effective_date: Optional[str] = None
    cancellation_date: Optional[str] = None
    recommendations: List[str] = None

class EnhancedGOSTSystem:
    """Расширенная система работы с ГОСТами"""
    
    def __init__(self, db_file='gost_enhanced_db.json'):
        self.db_file = db_file
        self.gost_database = self._load_database()
        
    def _load_database(self) -> Dict[str, GOSTInfo]:
        """Загрузка базы ГОСТов"""
        try:
            with open(self.db_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return {k: GOSTInfo(**v) for k, v in data.items()}
        except FileNotFoundError:
            return self._create_initial_database()
    
    def _create_initial_database(self) -> Dict[str, GOSTInfo]:
        """Создание начальной базы популярных ГОСТов"""
        initial_gosts = {
            "2.105-95": GOSTInfo(
                number="2.105-95",
                title="ЕСКД. Общие требования к текстовым документам",
                status="действующий",
                description="Устанавливает общие требования к выполнению текстовых документов, входящих в состав конструкторской документации изделий всех отраслей промышленности.",
                application_areas=["конструкторская документация", "техническая документация", "оформление документов"],
                recommendations=[
                    "Используйте для оформления технических заданий",
                    "Обязателен при создании конструкторской документации",
                    "Определяет требования к шрифтам, полям, нумерации"
                ],
                effective_date="1996-07-01"
            ),
            "7.32-2017": GOSTInfo(
                number="7.32-2017",
                title="Отчет о научно-исследовательской работе. Структура и правила оформления",
                status="действующий", 
                description="Устанавливает общие требования к структуре и правилам оформления отчета о НИР.",
                application_areas=["научные отчеты", "исследовательская работа", "диссертации"],
                recommendations=[
                    "Обязателен для научно-исследовательских отчетов",
                    "Используется в академических работах",
                    "Определяет структуру и библиографию"
                ],
                effective_date="2018-07-01"
            ),
            "19.301-94": GOSTInfo(
                number="19.301-94",
                title="ЕСД. Программа и методика испытаний. Требования к содержанию и оформлению",
                status="действующий",
                description="Устанавливает требования к содержанию и оформлению программ и методик испытаний.",
                application_areas=["программное обеспечение", "тестирование", "испытания"],
                recommendations=[
                    "Используйте при создании программ испытаний ПО",
                    "Обязателен для методик тестирования",
                    "Определяет структуру документов испытаний"
                ],
                effective_date="1995-01-01"
            ),
            "34.602-89": GOSTInfo(
                number="34.602-89",
                title="Техническое задание на создание автоматизированной системы",
                status="отмененный",
                description="Устанавливал требования к содержанию и оформлению технического задания на создание автоматизированной системы.",
                application_areas=["автоматизированные системы", "техническое задание", "разработка ПО"],
                replaced_by="ГОСТ Р 51904-2002",
                cancellation_date="2002-07-01",
                recommendations=[
                    "Заменен на ГОСТ Р 51904-2002",
                    "Использовался для ТЗ на АС",
                    "Историческое значение для понимания эволюции стандартов"
                ]
            ),
            "2.004-88": GOSTInfo(
                number="2.004-88", 
                title="ЕСКД. Общие требования к выполнению конструкторских и технологических документов на печатающих и графических устройствах вывода ЭВМ",
                status="действующий",
                description="Устанавливает общие требования к выполнению конструкторских и технологических документов на печатающих и графических устройствах вывода ЭВМ.",
                application_areas=["САПР", "автоматизированное проектирование", "компьютерная графика"],
                recommendations=[
                    "Актуален для современных САПР систем",
                    "Используйте при выводе чертежей на плоттер",
                    "Определяет требования к электронным документам"
                ],
                effective_date="1989-01-01"
            )
        }
        
        # Сохраняем в файл
        self._save_database(initial_gosts)
        return initial_gosts
    
    def _save_database(self, database: Dict[str, GOSTInfo]):
        """Сохранение базы ГОСТов"""
        data = {k: v.__dict__ for k, v in database.items()}
        with open(self.db_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    
    def search_by_number(self, gost_number: str) -> Optional[GOSTInfo]:
        """Поиск ГОСТа по номеру"""
        # Нормализуем номер (убираем лишние пробелы, приводим к стандартному виду)
        normalized_number = self._normalize_gost_number(gost_number)
        
        # Ищем точное совпадение
        if normalized_number in self.gost_database:
            return self.gost_database[normalized_number]
        
        # Ищем частичные совпадения
        for number, gost_info in self.gost_database.items():
            if normalized_number in number or number in normalized_number:
                return gost_info
        
        return None
    
    def _normalize_gost_number(self, number: str) -> str:
        """Нормализация номера ГОСТа"""
        # Убираем "ГОСТ", лишние пробелы
        clean_number = re.sub(r'^ГОСТ\s*', '', number.strip(), flags=re.IGNORECASE)
        return clean_number
    
    def get_recommendations_for_task(self, task_description: str) -> List[Tuple[str, GOSTInfo]]:
        """Получение рекомендаций ГОСТов для конкретной задачи"""
        recommendations = []
        task_lower = task_description.lower()
        
        for number, gost_info in self.gost_database.items():
            # Проверяем совпадения в областях применения
            for area in gost_info.application_areas:
                if any(keyword in task_lower for keyword in area.lower().split()):
                    recommendations.append((number, gost_info))
                    break
        
        return recommendations
    
    def format_gost_info(self, gost_info: GOSTInfo, include_recommendations: bool = True) -> str:
        """Форматирование информации о ГОСТе для вывода"""
        status_emoji = {
            "действующий": "✅",
            "отмененный": "❌", 
            "заменен": "🔄"
        }
        
        result = []
        result.append(f"📋 **ГОСТ {gost_info.number}**")
        result.append(f"📝 {gost_info.title}")
        result.append(f"{status_emoji.get(gost_info.status, '❓')} Статус: {gost_info.status}")
        result.append("")
        result.append(f"ℹ️ **Описание:**")
        result.append(gost_info.description)
        result.append("")
        
        if gost_info.application_areas:
            result.append("🎯 **Области применения:**")
            for area in gost_info.application_areas:
                result.append(f"  • {area}")
            result.append("")
        
        if gost_info.effective_date:
            result.append(f"📅 Дата введения: {gost_info.effective_date}")
        
        if gost_info.status == "отмененный" and gost_info.cancellation_date:
            result.append(f"🗓️ Дата отмены: {gost_info.cancellation_date}")
        
        if gost_info.replaced_by:
            result.append(f"🔄 Заменен на: {gost_info.replaced_by}")
        
        if include_recommendations and gost_info.recommendations:
            result.append("")
            result.append("💡 **Рекомендации по применению:**")
            for rec in gost_info.recommendations:
                result.append(f"  • {rec}")
        
        return "\n".join(result)

def main():
    """Тестирование системы"""
    system = EnhancedGOSTSystem()
    
    # Тест поиска по номеру
    print("🔍 Тест поиска ГОСТа по номеру:")
    gost = system.search_by_number("2.105-95")
    if gost:
        print(system.format_gost_info(gost))
    
    print("\n" + "="*50 + "\n")
    
    # Тест рекомендаций
    print("🎯 Тест рекомендаций для задачи:")
    recommendations = system.get_recommendations_for_task("нужно оформить техническую документацию")
    for number, gost_info in recommendations:
        print(f"📋 {number}: {gost_info.title}")

if __name__ == "__main__":
    main()
