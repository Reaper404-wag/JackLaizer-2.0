# 🚀 Руководство по развертыванию

## 📋 Предварительные требования

### Системные требования
- **Python**: 3.8 или выше
- **RAM**: Минимум 512MB, рекомендуется 1GB+
- **Диск**: 2GB свободного места
- **ОС**: Linux (Ubuntu 20.04+), Windows 10+, macOS 10.15+

### Внешние сервисы
- **Telegram Bot Token**: Получить у [@BotFather](https://t.me/botfather)
- **OpenRouter API** (опционально): Для ИИ функций
- **Веб-сервер** (опционально): Для Mini App

## 🐧 Развертывание на Linux (Ubuntu)

### 1. Подготовка системы
```bash
# Обновление системы
sudo apt update && sudo apt upgrade -y

# Установка Python и зависимостей
sudo apt install python3 python3-pip python3-venv git -y

# Установка дополнительных пакетов
sudo apt install build-essential libssl-dev libffi-dev -y
```

### 2. Клонирование и настройка
```bash
# Клонирование репозитория
git clone https://github.com/ваш-username/yakov-davydovich-bot.git
cd yakov-davydovich-bot

# Создание виртуального окружения
python3 -m venv venv
source venv/bin/activate

# Установка зависимостей
pip install --upgrade pip
pip install -r requirements.txt
```

### 3. Конфигурация
```bash
# Копирование конфигурации
cp .env.example .env

# Редактирование конфигурации
nano .env
```

### 4. Создание systemd сервиса
```bash
# Создание файла сервиса
sudo nano /etc/systemd/system/yakov-bot.service
```

Содержимое файла:
```ini
[Unit]
Description=Yakov Davydovich Telegram Bot
After=network.target

[Service]
Type=simple
User=ubuntu
WorkingDirectory=/home/ubuntu/yakov-davydovich-bot
Environment=PATH=/home/ubuntu/yakov-davydovich-bot/venv/bin
ExecStart=/home/ubuntu/yakov-davydovich-bot/venv/bin/python main.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

### 5. Запуск сервиса
```bash
# Перезагрузка systemd
sudo systemctl daemon-reload

# Включение автозапуска
sudo systemctl enable yakov-bot

# Запуск сервиса
sudo systemctl start yakov-bot

# Проверка статуса
sudo systemctl status yakov-bot
```

## 🐳 Развертывание с Docker

### 1. Создание Dockerfile
```dockerfile
FROM python:3.9-slim

WORKDIR /app

# Установка системных зависимостей
RUN apt-get update && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Копирование файлов
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Создание пользователя
RUN useradd -m -u 1000 botuser && chown -R botuser:botuser /app
USER botuser

# Запуск
CMD ["python", "main.py"]
```

### 2. Docker Compose
```yaml
version: '3.8'

services:
  yakov-bot:
    build: .
    container_name: yakov-bot
    restart: unless-stopped
    environment:
      - TELEGRAM_BOT_TOKEN=${TELEGRAM_BOT_TOKEN}
      - OPENROUTER_API_KEY=${OPENROUTER_API_KEY}
    volumes:
      - ./data:/app/data
      - ./logs:/app/logs
    networks:
      - bot-network

networks:
  bot-network:
    driver: bridge
```

### 3. Запуск
```bash
# Сборка и запуск
docker-compose up -d

# Просмотр логов
docker-compose logs -f yakov-bot

# Остановка
docker-compose down
```

## ☁️ Развертывание в облаке

### Heroku
```bash
# Установка Heroku CLI
# Создание приложения
heroku create yakov-bot-app

# Настройка переменных окружения
heroku config:set TELEGRAM_BOT_TOKEN=your_token
heroku config:set OPENROUTER_API_KEY=your_key

# Деплой
git push heroku main
```

### DigitalOcean Droplet
```bash
# Создание дроплета (Ubuntu 20.04)
# Подключение по SSH
ssh root@your_droplet_ip

# Следуйте инструкциям для Linux выше
```

### AWS EC2
```bash
# Запуск EC2 инстанса (t2.micro для начала)
# Настройка Security Groups (порт 22 для SSH)
# Подключение и установка как на Linux
```

## 🌐 Настройка Mini App

### 1. Статический хостинг
```bash
# Загрузка файлов на веб-сервер
scp -r mini_app/ user@your-server:/var/www/html/

# Настройка Nginx
sudo nano /etc/nginx/sites-available/yakov-miniapp
```

Конфигурация Nginx:
```nginx
server {
    listen 80;
    server_name your-domain.com;
    
    location /mini_app/ {
        root /var/www/html;
        index index.html;
        try_files $uri $uri/ =404;
    }
    
    # SSL настройки (рекомендуется)
    # ...
}
```

### 2. GitHub Pages
```bash
# Создание отдельного репозитория для Mini App
# Загрузка файлов в gh-pages ветку
# Настройка в Settings -> Pages
```

## 📊 Мониторинг и логирование

### 1. Настройка логов
```bash
# Создание директории для логов
mkdir -p /var/log/yakov-bot

# Настройка ротации логов
sudo nano /etc/logrotate.d/yakov-bot
```

Конфигурация logrotate:
```
/var/log/yakov-bot/*.log {
    daily
    missingok
    rotate 30
    compress
    delaycompress
    notifempty
    create 644 ubuntu ubuntu
}
```

### 2. Мониторинг с помощью systemd
```bash
# Просмотр логов
journalctl -u yakov-bot -f

# Статус сервиса
systemctl status yakov-bot

# Перезапуск при необходимости
sudo systemctl restart yakov-bot
```

## 🔧 Обслуживание

### Обновление бота
```bash
# Остановка сервиса
sudo systemctl stop yakov-bot

# Обновление кода
git pull origin main

# Обновление зависимостей
source venv/bin/activate
pip install -r requirements.txt

# Запуск сервиса
sudo systemctl start yakov-bot
```

### Бэкапы
```bash
# Создание скрипта бэкапа
nano backup.sh
```

Содержимое скрипта:
```bash
#!/bin/bash
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="/home/ubuntu/backups"
BOT_DIR="/home/ubuntu/yakov-davydovich-bot"

mkdir -p $BACKUP_DIR

# Бэкап данных
tar -czf $BACKUP_DIR/yakov-bot-data-$DATE.tar.gz \
    $BOT_DIR/*.json \
    $BOT_DIR/*.log \
    $BOT_DIR/.env

# Удаление старых бэкапов (старше 30 дней)
find $BACKUP_DIR -name "yakov-bot-data-*.tar.gz" -mtime +30 -delete
```

### Автоматизация с cron
```bash
# Редактирование crontab
crontab -e

# Добавление задач
# Бэкап каждый день в 2:00
0 2 * * * /home/ubuntu/backup.sh

# Перезапуск бота каждую неделю в воскресенье в 3:00
0 3 * * 0 sudo systemctl restart yakov-bot
```

## 🚨 Устранение неполадок

### Частые проблемы

#### Бот не отвечает
```bash
# Проверка статуса
systemctl status yakov-bot

# Просмотр логов
journalctl -u yakov-bot --since "1 hour ago"

# Проверка сетевого соединения
curl -I https://api.telegram.org
```

#### Ошибки ИИ модели
```bash
# Проверка API ключей
grep OPENROUTER_API_KEY .env

# Тест соединения с OpenRouter
curl -H "Authorization: Bearer your_key" https://openrouter.ai/api/v1/models
```

#### Проблемы с Mini App
```bash
# Проверка доступности файлов
curl -I https://your-domain.com/mini_app/index.html

# Проверка HTTPS сертификата
openssl s_client -connect your-domain.com:443
```

### Полезные команды
```bash
# Мониторинг ресурсов
htop
df -h
free -h

# Проверка портов
netstat -tlnp | grep python

# Анализ логов
tail -f /var/log/yakov-bot/veteran_bot.log
grep ERROR /var/log/yakov-bot/veteran_bot.log
```

## 📈 Масштабирование

### Горизонтальное масштабирование
- Использование webhook вместо polling
- Балансировка нагрузки между несколькими инстансами
- Кэширование с Redis

### Вертикальное масштабирование
- Увеличение RAM и CPU
- Оптимизация базы данных
- Использование SSD дисков

---

**Удачного развертывания!** 🚀

*"Как говорится, товарищ, хорошо настроенная система работает как швейцарские часы!"* — Яков Давидович