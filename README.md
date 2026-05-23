# EcoGame — Экологическая игра-симулятор

**Тема дипломной работы:** Разработка экологической игры по охране окружающей среды (на узбекском языке)

**Автор:** Рузибаев Жахонгир Дилмуратович (036-21 SMMr)  
**Научные руководители:** Узакова М.А., Абидова Ш.Б.  
**Кафедра:** Multimedia texnologiyalari

---

## Описание проекта

EcoGame — браузерная игра-симулятор экосистемы, обучающая игроков основам охраны окружающей среды на узбекском языке. Игрок управляет виртуальной территорией, выполняя экологические действия: посадка деревьев, очистка водоёмов, сортировка мусора, установка солнечных панелей, защита животных.

**Игра доступна по адресу:** https://ecogame.fullfocus.dev

---

## Стек технологий

| Компонент | Технология |
|-----------|------------|
| Backend | Django 5 + Django REST Framework + Unfold Admin |
| Аутентификация | JWT (djangorestframework-simplejwt) |
| Frontend | React 19 + TypeScript + Vite |
| Game Engine | Phaser.js 3.80+ |
| Состояние | Zustand |
| Стили | Tailwind CSS v4 |
| База данных (dev) | SQLite |
| База данных (prod) | PostgreSQL 16 |
| Контейнеризация | Docker + Docker Compose |
| Обратный прокси | Nginx |
| Деплой | Coolify |

---

## Запуск для разработки

### Предварительные требования
- Python 3.12+
- Node.js 20+
- [uv](https://docs.astral.sh/uv/) (Python package manager)
- Docker + Docker Compose (опционально)

### Через Docker Compose (рекомендуется)

```bash
# Скопировать переменные окружения
cp .env.example .env
# Отредактировать .env при необходимости

# Запустить
docker compose -f docker-compose.dev.yml up --build
```

Приложение будет доступно:
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000/api/v1/
- Admin: http://localhost:8000/admin/

### Ручной запуск

**Backend:**
```bash
cd backend
uv sync
uv run python manage.py migrate
uv run python manage.py loaddata fixtures/levels.json fixtures/eco_actions.json fixtures/achievements.json fixtures/educational_content.json fixtures/eco_facts.json
uv run python manage.py runserver
```

**Frontend:**
```bash
cd frontend
npm install
npm run dev
```

---

## Запуск в production

```bash
cp .env.example .env
# Заполнить .env production значениями (SECRET_KEY, DATABASE_URL, и т.д.)

docker compose up --build -d
docker compose exec backend uv run python manage.py migrate
docker compose exec backend uv run python manage.py loaddata fixtures/levels.json fixtures/eco_actions.json
```

---

## Структура проекта

```
.
├── backend/          # Django REST API
│   ├── apps/
│   │   ├── accounts/ # Аутентификация, модель Player
│   │   ├── game/     # Игровая логика, уровни, действия
│   │   ├── education/ # Образовательный контент
│   │   └── leaderboard/ # Таблица лидеров
│   ├── config/       # Django настройки
│   └── fixtures/     # Начальные данные
├── frontend/         # React + Phaser.js приложение
│   └── src/
│       ├── game/     # Phaser сцены и объекты
│       ├── pages/    # React страницы
│       └── stores/   # Zustand хранилища
├── nginx/            # Nginx конфигурация
└── docs/
    ├── vkr/          # Текст дипломной работы
    └── presentation/ # Презентация для защиты
```

---

## Тестирование

```bash
# Backend
cd backend
uv run pytest -v
uv run pytest --cov=apps --cov-report=html

# Frontend
cd frontend
npm run lint
npm run build
```

---

## Лицензия

Дипломный проект. Все права защищены.
