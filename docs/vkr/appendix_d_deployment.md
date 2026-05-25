# ПРИЛОЖЕНИЕ Г. ДОКУМЕНТАЦИЯ REST API

## Г.1 Общие сведения

**Base URL:** `https://ecogame.fullfocus.dev/api/v1`

**Аутентификация:** JWT Bearer Token
```
Authorization: Bearer <access_token>
```

**Формат ответа при ошибке:**
```json
{
  "detail": "Описание ошибки",
  "code": "error_code"
}
```

---

## Г.2 Аутентификация

### POST /accounts/token/
Получить пару JWT токенов.

**Request:**
```json
{ "username": "string", "password": "string" }
```
**Response 200:**
```json
{ "access": "eyJ...", "refresh": "eyJ..." }
```

### POST /accounts/token/refresh/
Обновить access token.

**Request:**
```json
{ "refresh": "eyJ..." }
```
**Response 200:**
```json
{ "access": "eyJ..." }
```

### POST /accounts/register/
Регистрация нового пользователя.

**Request:**
```json
{
  "username": "jakha",
  "email": "jakha@example.com",
  "password": "securepass123"
}
```
**Response 201:**
```json
{
  "access": "eyJ...",
  "refresh": "eyJ...",
  "user": { "id": 1, "username": "jakha" }
}
```

### POST /accounts/anonymous/
Создать анонимного пользователя.

**Request:**
```json
{ "session_key": "unique-device-session-id" }
```
**Response 201:**
```json
{ "access": "eyJ...", "refresh": "eyJ...", "username": "anon_abc123" }
```

### POST /accounts/claim/
Конвертировать анонимного в полноценного пользователя. Auth required.

**Request:**
```json
{ "username": "newname", "email": "user@example.com", "password": "pass123" }
```
**Response 200:**
```json
{ "detail": "Muvaffaqiyatli ro'yxatdan o'tdingiz!" }
```

---

## Г.3 Квиз

### POST /game/quiz/sessions/
Начать новую квиз-сессию. Auth required.

**Request:**
```json
{ "mode": "QUICK" }
```
или
```json
{ "mode": "CATEGORY", "category": "AIR" }
```

**Response 201:**
```json
{
  "id": 42,
  "mode": "QUICK",
  "started_at": "2026-05-25T10:00:00Z",
  "questions": [
    {
      "id": 1,
      "text_uz": "...",
      "category": "AIR",
      "difficulty": 1,
      "question_type": "MCQ",
      "time_limit": 30,
      "answers": [
        { "id": 101, "text_uz": "..." },
        { "id": 102, "text_uz": "..." },
        { "id": 103, "text_uz": "..." },
        { "id": 104, "text_uz": "..." }
      ]
    }
  ]
}
```
*Примечание: `is_correct` намеренно отсутствует в ответах (anti-cheat).*

### POST /game/quiz/sessions/{session_id}/answer/
Ответить на вопрос. Auth required.

**Request:**
```json
{
  "question_id": 1,
  "answer_id": 101,
  "time_spent_ms": 5432
}
```

**Response 200:**
```json
{
  "is_correct": true,
  "correct_answer_id": 101,
  "explanation_uz": "...",
  "points_earned": 185,
  "streak": 3,
  "streak_multiplier": 2.0,
  "time_bonus": 85,
  "total_score": 650,
  "is_game_over": false
}
```

### POST /game/quiz/sessions/{session_id}/end/
Завершить квиз-сессию. Auth required.

**Response 200:**
```json
{
  "session": { "id": 42, "score": 850, "correct_count": 8, ... },
  "accuracy": 0.8,
  "rank_title": "Tabiat do'sti",
  "achievements_unlocked": [
    { "key": "first_quiz", "title_uz": "Birinchi qadam", "icon": "🌱" }
  ]
}
```

### GET /game/quiz/questions/
Получить список вопросов (публичный). Параметры: `?category=AIR&difficulty=1`.

**Response 200:**
```json
{
  "count": 150,
  "results": [ { "id": 1, "text_uz": "...", ... } ]
}
```

### GET /game/quiz/daily/
Получить ежедневное задание. Auth required.

**Response 200:**
```json
{
  "id": 5,
  "date": "2026-05-25",
  "bonus_score": 50,
  "is_completed": false,
  "questions": [ ... ]
}
```

### GET /game/quiz/stats/
Статистика текущего пользователя. Auth required.

**Response 200:**
```json
{
  "total_quizzes": 12,
  "accuracy_pct": 73.5,
  "best_streak": 8,
  "rank_title": "Tabiat do'sti",
  "per_category": {
    "AIR": { "total": 30, "correct": 24, "accuracy": 0.8 }
  }
}
```

---

## Г.4 Мини-игра

### POST /game/mini-game/score/
Сохранить результат мини-игры. Auth required.

**Request:**
```json
{ "score": 180, "correct_count": 18, "total_items": 20 }
```
**Response 201:** `{}`

---

## Г.5 Образование

### GET /education/articles/
Список образовательных статей. Публичный. Параметры: `?category=AIR&search=chiqindi`.

**Response 200:**
```json
{
  "count": 12,
  "results": [
    { "id": 1, "title_uz": "...", "summary_uz": "...", "category": "WATER", "read_time_minutes": 5 }
  ]
}
```

### GET /education/articles/{id}/
Полный текст статьи. Публичный.

**Response 200:**
```json
{ "id": 1, "title_uz": "...", "content_uz": "...", "category": "WATER" }
```

### GET /education/facts/random/
Три случайных экологических факта. Публичный.

**Response 200:**
```json
[ { "text_uz": "...", "category": "AIR" } ]
```

---

## Г.6 Лидерборд

### GET /leaderboard/
Топ-50 игроков. Публичный.

**Response 200:**
```json
{
  "results": [
    { "rank": 1, "player": "jakha", "score": 5000, "rank_title": "Eko-ustoz" }
  ],
  "my_rank": 12,
  "my_score": 1340
}
```

---

## Г.7 Достижения

### GET /game/achievements/
Все достижения (публичный).

**Response 200:**
```json
[ { "key": "first_quiz", "title_uz": "...", "icon": "🌱", "points_reward": 50 } ]
```

### GET /game/achievements/my/
Полученные достижения текущего пользователя. Auth required.

**Response 200:**
```json
[ { "id": 1, "achievement": { "key": "first_quiz", ... }, "unlocked_at": "..." } ]
```
