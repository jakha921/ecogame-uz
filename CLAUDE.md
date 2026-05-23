# EcoGame — Project-specific Claude Instructions

## Описание проекта
Экологическая игра-симулятор на узбекском языке. Дипломный проект.
- Backend: Django REST API (port 8000)
- Frontend: React 19 + Phaser.js (port 3000)
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
  accounts/   — Аутентификация, модель Player
  game/       — Игровая логика, уровни, действия
  education/  — Образовательный контент
  leaderboard/ — Таблица лидеров

frontend/src/
  game/       — Phaser сцены и объекты
  pages/      — React страницы
  stores/     — Zustand хранилища
  api/        — HTTP клиент и типы
```

## Правила кода
- Python: type hints обязательны, ruff форматирование
- TypeScript: strict mode, БЕЗ `any`
- Нет N+1 запросов: select_related/prefetch_related
- Секреты только в .env (не в коде)
