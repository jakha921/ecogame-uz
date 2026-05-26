# EcoGame — Экологическая викторина

**Тема дипломной работы:** Разработка экологической игры по охране окружающей среды (на узбекском языке)

**Автор:** Рузибаев Жахонгир Дилмуратович (036-21 SMMr)  
**Научные руководители:** Узакова М.А., Абидова Ш.Б.  
**Кафедра:** Multimedia texnologiyalari

---

## Описание проекта

EcoGame — браузерная экологическая викторина на узбекском языке. Игроки отвечают на вопросы об экологии, зарабатывают очки за правильные ответы и быстрые ответы, поднимаются по рейтингу.

**4 режима игры:**
- **Tezkor o'yin** — 10 случайных вопросов
- **Kunlik vazifa** — ежедневные вопросы с бонусом
- **Marafon** — до первой ошибки
- **Kategoriya bo'yicha** — вопросы по одной теме (Flora, Water, Waste, Energy, Fauna)

**Геймификация:** scoring formula, streak multiplier (×1→×3), ранги (6 уровней), 10 достижений

**Мини-игра:** drag-and-drop сортировка мусора

**Игра доступна по адресу:** https://ecogame.fullfocus.dev

---

## Стек технологий

| Компонент | Технология |
|-----------|------------|
| Backend | Django 5 + Django REST Framework + Unfold Admin |
| Аутентификация | JWT (djangorestframework-simplejwt) |
| Frontend | React 19 + TypeScript + Vite |
| Quiz Engine | 4 режима, scoring, streaks, achievements |
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
cp .env.example .env
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
uv run python manage.py loaddata \
  fixtures/levels.json \
  fixtures/quiz_achievements.json \
  fixtures/educational_content.json \
  fixtures/eco_facts.json \
  fixtures/questions.json
uv run python manage.py runserver
```

**Frontend:**
```bash
cd frontend
npm install
npm run dev
```

---

## Структура проекта

```
.
├── backend/           # Django REST API
│   ├── apps/
│   │   ├── accounts/  # Аутентификация, модель Player
│   │   ├── game/      # Quiz модели, QuizService, достижения
│   │   ├── education/ # Образовательный контент, факты
│   │   └── leaderboard/ # Таблица лидеров
│   ├── config/        # Django настройки
│   └── fixtures/      # Начальные данные (150 вопросов, достижения)
├── frontend/          # React приложение
│   └── src/
│       ├── components/
│       │   └── quiz/  # Timer, QuestionCard, ExplanationPanel, ...
│       ├── pages/     # MainMenu, QuizPlayPage, QuizResultsPage, ...
│       ├── stores/    # authStore, quizStore
│       └── api/       # quiz.ts, education.ts, types.ts
├── nginx/             # Nginx конфигурация
└── docs/
    ├── vkr/           # Текст дипломной работы
    └── presentation/  # Презентация для защиты
```

---

## Тестирование

```bash
# Backend (136+ тестов)
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
