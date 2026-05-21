🐍 KostylЯ (Project Management System)

[![CI](https://github.com/SergoTrafimov/ProgramSystemZuparova/actions/workflows/ci.yml/badge.svg)](https://github.com/SergoTrafimov/ProgramSystemZuparova/actions/workflows/ci.yml)

[![Build](https://github.com/SergoTrafimov/ProgramSystemZuparova/actions/workflows/build.yml/badge.svg)](https://github.com/SergoTrafimov/ProgramSystemZuparova/actions/workflows/build.yml)


Система управления проектами и задачами для IT-компании с ролевой моделью (аналитик, куратор, разработчик, тестировщик, бухгалтер, клиент).

📋 Основные возможности
🔐 Регистрация и аутентификация с выбором роли и организации

📊 Ролевые дашборды (аналитик, куратор, разработчик, тестировщик, бухгалтер)

🗂️ Управление проектами и задачами с дедлайнами

🔄 Автоматическая передача задач по статусам (новая → в работе → на тестировании → готова)

📝 Обратная связь клиентов и переписка с аналитиком

📈 Расчёт зарплаты с учётом налогов

🔔 Уведомления о дедлайнах

🚀 Быстрый старт
1. Настройка виртуального окружения

 WINDOWS
    
      python -m venv venv
      
      venv\Scripts\activate
    
 LINUX
    
      python3 -m venv venv
      
      source venv/bin/activate
  
2.Установка зависимостей
   pip install -r requirements.txt


4. Применение миграций и создание суперпользователя

python manage.py migrate

python manage.py createsuperuser

4. Запуск сервера

python manage.py runserver 8080

Приложение будет доступно по адресу: http://localhost:8080

5. Вход в систему
   
  Пользовательский интерфейс: http://localhost:8080

  Админ-панель Django: http://localhost:8080/admin

  Кастомная админ-панель: http://localhost:8080/admin-panel

🧪 Тестирование и автоматизация
Тесты написаны с использованием pytest и pytest-django. GitHub Actions настроен на автоматический запуск тестов при каждом пуше в main и создании pull request.

Запуск тестов локально

pytest -v
Запуск с покрытием

pytest --cov=. --cov-report=term

Покрытие кода
Проект интегрирован с Codecov. Текущее покрытие можно увидеть по бейджу вверху README. Минимальное покрытие для ключевых модулей — 70%.

Тестовые данные
Для проверки работы можно использовать:

Админ-панель: создайте организацию с кодом приглашения (например, 123)

Регистрация: зарегистрируйте пользователей с ролями analyst, curator, dev, tester, accountant, client

Для ролей, отличных от client, потребуется код приглашения

Учётные записи по умолчанию (если заданы в fixtures): admin / admin

🛠️ Используемые технологии
Python 3.10+

Django 6.0

SQLite (по умолчанию) / PostgreSQL (для production)

pytest-django (тестирование)

GitHub Actions (CI/CD)

Codecov (покрытие)


📄 Лицензия
Этот проект создан в учебных целях и не предназначен для коммерческого использования.

💡 Примечание: При первом запуске убедитесь, что у вас создана хотя бы одна организация, иначе регистрация пользователей с ролями, отличными от client, будет невозможна.


## ⚙️ Автоматизация (CI/CD)

В проекте настроены **GitHub Actions** для непрерывной интеграции и развёртывания. Все workflows находятся в папке `.github/workflows/` и запускаются автоматически при пушах в ветку `main` и создании pull request.

### 🔄 Доступные workflows

| Workflow | Файл | Триггер | Что делает |
|----------|------|---------|-------------|
| **CI – тестирование** | `ci.yml` | push / PR в `main` | Устанавливает Python 3.12, зависимости, запускает `pytest` с покрытием, загружает отчёт в Codecov. |
| **Build – проверка целостности** | `build.yml` | push / PR в `main` | Проверяет, что все миграции созданы (`makemigrations --check`). |
| **Deploy – развёртывание** | `deploy.yml` | push в `main` | Автоматически деплоит приложение на **Render** (бесплатный хостинг). |


