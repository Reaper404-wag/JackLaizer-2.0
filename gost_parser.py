import requests
from bs4 import BeautifulSoup
import json
import logging
from typing import Dict, List, Optional
import re
import time
import random
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry

class GOSTParser:
    def __init__(self, cache_file='gost_cache.json'):
        self.base_url = "https://docs.cntd.ru"
        self.search_url = f"{self.base_url}/search"
        self.cache_file = cache_file
        self.cache = self._load_cache()
        
        # Настройка логирования
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s: %(message)s',
            handlers=[
                logging.FileHandler('gost_parser.log', encoding='utf-8'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)

        # Создание сессии с повторными попытками
        self.session = requests.Session()
        retries = Retry(
            total=3,
            backoff_factor=0.5,
            status_forcelist=[500, 502, 503, 504]
        )
        self.session.mount('https://', HTTPAdapter(max_retries=retries))

    def _load_cache(self) -> Dict:
        try:
            with open(self.cache_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            return {}

    def _save_cache(self):
        with open(self.cache_file, 'w', encoding='utf-8') as f:
            json.dump(self.cache, f, ensure_ascii=False, indent=2)

    def _get_headers(self) -> Dict:
        """Генерация случайных заголовков для обхода блокировок"""
        user_agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15',
            'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36'
        ]
        return {
            'User-Agent': random.choice(user_agents),
            'Accept-Language': 'ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Referer': 'https://www.google.com/'
        }

    def search_gost(self, query: str, max_results: int = 5) -> List[Dict]:
        """Поиск ГОСТов по запросу с расширенной обработкой"""
        self.logger.info(f"Начало поиска ГОСТов по запросу: {query}")

        # Проверка кэша
        if query in self.cache:
            self.logger.info("Возврат результатов из кэша")
            return self.cache[query]

        try:
            # Случайная задержка для имитации человеческого поведения
            time.sleep(random.uniform(1, 3))

            params = {
                'query': query,
                'type': 'normative_document'
            }
            
            response = self.session.get(
                self.search_url, 
                params=params, 
                headers=self._get_headers(),
                timeout=10
            )
            
            # Расширенная обработка ошибок
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            results = []

            for item in soup.select('.search-result')[:max_results]:
                try:
                    title = item.select_one('.search-result__title').text.strip()
                    link = self.base_url + item.select_one('a')['href']
                    
                    # Детальный парсинг страницы ГОСТа
                    gost_details = self._parse_gost_details(link)
                    
                    result = {
                        'title': title,
                        'link': link,
                        **gost_details
                    }
                    results.append(result)
                except Exception as item_error:
                    self.logger.warning(f"Ошибка при обработке элемента: {item_error}")

            # Кэширование результатов
            self.cache[query] = results
            self._save_cache()

            self.logger.info(f"Найдено {len(results)} результатов")
            return results

        except requests.RequestException as e:
            self.logger.error(f"Ошибка при поиске ГОСТа: {e}")
            return []

    def _parse_gost_details(self, url: str) -> Dict:
        """Парсинг детальной информации о ГОСТе с расширенной обработкой"""
        try:
            response = self.session.get(
                url, 
                headers=self._get_headers(),
                timeout=10
            )
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Извлечение кода ГОСТа
            code_match = re.search(r'ГОСТ\s+[\w.-]+', soup.text)
            gost_code = code_match.group(0) if code_match else "Не определен"
            
            # Поиск описания
            description_elem = soup.select_one('.document-description')
            description = description_elem.text.strip() if description_elem else "Описание отсутствует"
            
            return {
                'code': gost_code,
                'description': description[:500]  # Ограничение длины описания
            }

        except requests.RequestException as e:
            self.logger.error(f"Ошибка при парсинге деталей ГОСТа: {e}")
            return {}

def main():
    parser = GOSTParser()
    
    # Примеры поиска
    test_queries = [
        "схемы алгоритмов",
        "библиографическая ссылка",
        "программная документация"
    ]

    for query in test_queries:
        print(f"\n🔍 Результаты поиска для '{query}':")
        results = parser.search_gost(query)
        
        for result in results:
            print(f"Название: {result.get('title', 'Н/Д')}")
            print(f"Код: {result.get('code', 'Н/Д')}")
            print(f"Ссылка: {result.get('link', 'Н/Д')}")
            print(f"Описание: {result.get('description', 'Н/Д')[:200]}...\n")
        
        time.sleep(1)  # Задержка между запросами

if __name__ == "__main__":
    main()
