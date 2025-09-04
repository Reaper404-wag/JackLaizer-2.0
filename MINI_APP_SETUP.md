# 🎮 Настройка Mini App в BotFather

## 📋 Пошаговая инструкция

### Шаг 1: Подготовка файлов
1. ✅ HTML файл готов: `mini_app/index.html`
2. ✅ Обработчик готов: `mini_app_handler.py`
3. ✅ Интеграция с ботом завершена

### Шаг 2: Размещение Mini App
Вам нужно разместить файл `mini_app/index.html` на веб-сервере с HTTPS.

**Варианты размещения:**
- GitHub Pages (бесплатно)
- Netlify (бесплатно)
- Vercel (бесплатно)
- Ваш собственный сервер

**Пример для GitHub Pages:**
1. Создайте репозиторий на GitHub
2. Загрузите файл `index.html` в папку `docs/`
3. Включите GitHub Pages в настройках репозитория
4. Получите URL вида: `https://username.github.io/repository-name/index.html`

### Шаг 3: Настройка в BotFather

Отправьте следующие команды в @BotFather:

```
/mybots
[Выберите своего бота]
Bot Settings
Menu Button
Configure Menu Button
```

**Введите данные:**
- **Text**: `🎮 Шахматы`
- **URL**: `https://ваш-домен.com/mini_app/index.html`

### Шаг 4: Настройка Web App

```
/mybots
[Выберите своего бота]
Bot Settings
Web App
Configure Web App
```

**Введите данные:**
- **Name**: `Шахматы с Яковом`
- **URL**: `https://ваш-домен.com/mini_app/index.html`
- **Short Name**: `chess_yakov`

### Шаг 5: Создание кнопки для команды /chess

Добавьте в код бота кнопку с Web App при отправке команды `/chess`:

```python
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, WebAppInfo

# В методе launch_chess_mini_app:
keyboard = InlineKeyboardMarkup()
web_app_button = InlineKeyboardButton(
    text="🎮 Запустить игру",
    web_app=WebAppInfo(url="https://ваш-домен.com/mini_app/index.html")
)
keyboard.add(web_app_button)

await message.reply(response_text, reply_markup=keyboard)
```

## 🔧 Технические детали

### Функции Mini App:
- ♟️ **Интерактивная шахматная доска**
- 🎯 **3 уровня сложности задач**
- 📊 **Статистика прогресса**
- 💬 **Комментарии Якова Давидовича**
- 🎨 **Адаптивный дизайн**

### Обмен данными:
- Mini App → Bot: через `Telegram.WebApp.sendData()`
- Bot → User: обычные сообщения с результатами

### Безопасность:
- Все данные проверяются на стороне бота
- Используется Telegram Web App API
- HTTPS обязателен

## 🚀 После настройки

1. Команда `/chess` будет показывать кнопку запуска Mini App
2. Пользователи смогут решать шахматные задачи
3. Результаты будут отправляться в чат с комментариями Якова
4. Статистика будет сохраняться

## 📞 Нужна помощь?

Если возникнут проблемы с настройкой:
1. Проверьте, что URL доступен по HTTPS
2. Убедитесь, что файл `index.html` открывается в браузере
3. Проверьте логи бота на предмет ошибок
