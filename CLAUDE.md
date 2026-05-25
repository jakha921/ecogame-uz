# EcoGame — Project-specific Claude Instructions

## Описание проекта
Экологическая викторина на узбекском языке. Дипломный проект.
- Backend: Django REST API (port 8000)
- Frontend: React 19 + TypeScript + Vite (port 3000)
- Deploy: ecogame.fullfocus.dev via Coolify

## Команды проверки
```bash
# Backend
cd backend && uv run python manage.py check
cd backend && uv run pytest -v
cd backend && uv run ruff check --fix .

# Frontend
cd frontend && npm run build
cd frontend && npm run lint

# Docker (dev)
docker compose -f docker-compose.dev.yml config
docker compose -f docker-compose.dev.yml up --build
```

## Язык контента
- ВСЕ пользовательские тексты в игре — на узбекском языке (латиница)
- Поля с узбекским контентом именуются с суффиксом `_uz`
- Текст ВКР — на русском языке
- Комментарии в коде — на русском или английском

## Структура
```
backend/apps/
  accounts/    — Аутентификация, модель Player
  game/        — Quiz модели, QuizService, scoring, достижения
  education/   — Образовательный контент, EcoFact
  leaderboard/ — Таблица лидеров (сигналы QuizSession)

frontend/src/
  components/quiz/ — Timer, QuestionCard, ExplanationPanel, StreakCounter, ...
  pages/           — MainMenu, QuizPlayPage, QuizResultsPage, ProfilePage, ...
  stores/          — authStore, quizStore (Zustand)
  api/             — quiz.ts, education.ts, types.ts, client.ts
```

## Quiz API endpoints (основные)
```
POST /api/v1/game/quiz/sessions/              — start session
POST /api/v1/game/quiz/sessions/{id}/answer/  — submit answer
POST /api/v1/game/quiz/sessions/{id}/end/     — end session
GET  /api/v1/game/quiz/stats/                 — player stats
GET  /api/v1/game/quiz/daily/                 — daily challenge
GET  /api/v1/game/quiz/questions/             — question list
GET  /api/v1/game/achievements/my/            — my achievements
```

## Правила кода
- Python: type hints обязательны, ruff форматирование
- TypeScript: strict mode, БЕЗ `any`
- Нет N+1 запросов: select_related/prefetch_related
- Секреты только в .env (не в коде)
