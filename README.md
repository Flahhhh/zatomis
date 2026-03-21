<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <title>Zatomis README</title>
    <style>
        body {
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Helvetica, Arial, sans-serif;
            line-height: 1.6;
            color: #24292e;
            max-width: 900px;
            margin: 0 auto;
            padding: 20px;
        }
        h1, h2, h3 {
            border-bottom: 1px solid #eaecef;
            padding-bottom: 0.3em;
        }
        code {
            background-color: #f6f8fa;
            padding: 0.2em 0.4em;
            border-radius: 3px;
            font-family: "SFMono-Regular", Consolas, "Liberation Mono", Menlo, monospace;
        }
        pre {
            background-color: #f6f8fa;
            padding: 16px;
            overflow: auto;
            border-radius: 3px;
        }
        ul {
            padding-left: 2em;
        }
        blockquote {
            border-left: 4px solid #dfe2e5;
            color: #6a737d;
            padding: 0 1em;
        }
    </style>
</head>
<body>

    <h1>Zatomis</h1>
    <p>
        <strong>Zatomis</strong> — это open-source микрофреймворк, разработанный специально для проекта <a href="#">SKIJ.net</a>. 
        Он обеспечивает эффективную работу клиент-сервер ресурсов в <strong>LoRa-mesh сетях</strong>.
    </p>
    <p>
        На данный момент взаимодействие с аппаратной частью осуществляется через <strong>Meshtastic</strong>, 
        но в дальнейшем это может быть изменено. Слово «микро» означает стремление обеспечить лишь необходимый 
        для работы функционал с максимальной возможностью расширения.
    </p>

    <blockquote>
        <p>В данной конфигурации работа с БД, валидацией данных и другой функционал реализуется разработчиком конкретного ресурса, а не разработчиком фреймворка.</p>
    </blockquote>

    <h2>Возможности фреймворка</h2>
    <ul>
        <li>Асинхронность и фоновые воркеры.</li>
        <li>Двухсторонний механизм автоматической пагинации.</li>
        <li>Поддержка разных интерфейсов подключения (Serial, TCP, BLE).</li>
        <li>Обработка различных типов ответов.</li>
        <li>Гибкая маршрутизация запросов.</li>
    </ul>

    <h2>Требования</h2>
    <ul>
        <li>Python версии >= 3.8</li>
        <li>Библиотека <code>meshtastic</code> версии 2.7.7 (единственная обязательная зависимость ядра)</li>
    </ul>

    <h2>Установка и запуск</h2>
    <p>Репозиторий проекта хранится на GitHub. Для начала работы выполните следующие шаги:</p>

    <h3>1. Клонирование репозитория</h3>
    <pre><code>git clone flahhh/zatomis
cd zatomis</code></pre>
    <p><em>Для внесения изменений в ядро фреймворка рекомендуется создать форк репозитория.</em></p>

    <h3>2. Настройка виртуальной среды</h3>
    <p>Рекомендуется использовать <code>venv</code>:</p>
    <pre><code>python -m venv venv</code></pre>
    <p>Активация среды:</p>
    <ul>
        <li><strong>Windows:</strong> <code>venv\Scripts\activate</code></li>
        <li><strong>Linux:</strong> <code>sudo source venv/bin/activate</code></li>
    </ul>

    <h3>3. Установка зависимостей</h3>
    <pre><code>pip install -r requirements.txt</code></pre>

    <h3>4. Запуск проекта</h3>
    <pre><code>python app.py</code></pre>
    <p>Теперь фреймворк готов принимать и обрабатывать запросы из LoRa-сети. Для остановки нажмите <code>Ctrl+C</code>.</p>

    <h2>Настройка интерфейса</h2>
    <p>Zatomis поддерживает три способа подключения к радиомодему. При инициализации приложения необходимо передать кортеж, описывающий тип интерфейса и его параметры.</p>
    
    <p>Пример инициализации в <code>app.py</code>:</p>
    <pre><code>from zatomis import Zatomis

# 1. Serial (USB) – обычно используется devPath, например '/dev/ttyUSB0' или 'COM3'
app = Zatomis(receive_interface=("serial", "/dev/ttyUSB0"))

# 2. TCP – требуется указать IP-адрес и порт (например, 192.168.1.100:4403)
app = Zatomis(receive_interface=("tcp", "192.168.1.100:4403"))

# 3. BLE – Bluetooth-адрес устройства
app = Zatomis(receive_interface=("ble", "AA:BB:CC:DD:EE:FF"))</code></pre>
    
    <p>Если интерфейс для отправки сообщений должен отличаться от принимающего, можно указать второй аргумент <code>send_interface</code> (аналогично). По умолчанию используется тот же интерфейс, что и для приёма.</p>

    <h2>Архитектура проекта</h2>
    <p>Основные компоненты фреймворка:</p>
    <ul>
        <li><strong>Zatomis</strong> — основное приложение.</li>
        <li><strong>Router</strong> — маршрутизация запросов.</li>
        <li><strong>Request</strong> — класс входящего запроса и его данных.</li>
        <li><strong>Response</strong> — класс ответа сервера и его виды.</li>
    </ul>

    <h2>Минимальное приложение</h2>
    <p>Структура простейшего приложения включает:</p>
    <ul>
        <li><code>app.py</code> — точка входа.</li>
        <li><code>urls.py</code> — конфигурация маршрутов.</li>
        <li>Контроллер-функции — обработка запроса и формирование ответа.</li>
    </ul>

    <h2>Дополнительные возможности</h2>
    <ul>
        <li><strong>Интеграция с БД:</strong> Поддержка SQLAlchemy, сессии, генераторы.</li>
        <li><strong>Низкоуровневая работа:</strong> Обработка пакетов Meshtastic, парсинг, очереди отправки.</li>
        <li><strong>Расширение:</strong> Добавление аутентификации, валидация данных.</li>
        <li><strong>Логирование:</strong> Встроенные механизмы отладки.</li>
    </ul>

    <h2>Документация</h2>
    <p>Полная документация находится в разработке.</p>
    <p><em>Скоро...</em></p>

    <hr>
    <p><small>Zatomis Microframework &copy; 2023-2024. Open Source.</small></p>

</body>
</html>
