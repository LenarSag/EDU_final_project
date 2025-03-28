# Проект с микросервисами

## Описание

Этот проект представляет собой систему с микросервисной архитектурой, включающую несколько сервисов, таких как **auth_service**, **calendar_service**, **meeting_service**, **task_service**, и **team_service**. Также используется **PostgreSQL** для хранения данных и **Redis** для кэширования. Для управления инфраструктурой используется **Docker**.

Проект включает в себя API для управления пользователями, календарем, встречами, задачами и командами. Все сервисы написаны с использованием **FastAPI** и работают в контейнерах Docker.

## Стек технологий

- **FastAPI** – для создания API.
- **Redis** – для кэширования данных.
- **PostgreSQL** – для хранения данных.
- **Alembic** – для миграций базы данных.
- **Docker** – для контейнеризации сервисов.
- **Nginx** – для проксирования запросов к микросервисам.
  
## Структура проекта

Проект состоит из нескольких сервисов:

1. **auth_service** — сервис для аутентификации и управления пользователями.
2. **calendar_service** — сервис для управления календарем.
3. **meeting_service** — сервис для управления встречами.
4. **task_service** — сервис для управления задачами.
5. **team_service** — сервис для управления командами.
6. **nginx** — обратный прокси-сервер для маршрутизации запросов к соответствующим сервисам.

## Установка и запуск

### Требования

- **Docker** — для запуска контейнеров.
- **Docker Compose** — для управления многоконтейнерными приложениями.

### Шаги для запуска

1. Клонируйте репозиторий:
   ```bash
   git clone https://github.com/LenarSag/EDU_final_project.git
   cd EDU_final_project

2. Создайте файл .env с переменными окружения для каждого сервиса (если они не включены в проект).

3. Запустите проект с помощью Docker Compose:
   ```bash
   docker-compose up --build

Это создаст и запустит все необходимые контейнеры.

### Сервисы

Сервисы будут доступны по следующим адресам, используется проксирование Nginx:

```
localhost/admin/
localhost/users/
localhost/auth/
localhost/calendar/
localhost/meetings/ 
localhost/tasks/
localhost/evaluations/
localhost/teams/
```

Также, все сервисы будут доступны по следующим портам:

```
auth_service: 8001
calendar_service: 8002
meeting_service: 8003
task_service: 8004
team_service: 8005
nginx: 80 (для проксирования запросов)
```

auth_service:
Ответственен за аутентификацию и управление пользователями.
Порты: 8001

calendar_service:
Ответственен за управление календарем и событиями.
Порты: 8002

meeting_service:
Ответственен за управление встречами.
Порты: 8003

task_service:
Ответственен за управление задачами и оценками.
Порты: 8004

team_service:
Ответственен за управление командами.
Порты: 8005

nginx:
Используется для проксирования запросов между сервисами.
Порты: 80

### Миграции
Для применения миграций:

   ```bash
   docker-compose exec auth_service alembic upgrade head