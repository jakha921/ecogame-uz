# ПРИЛОЖЕНИЕ В. ER-ДИАГРАММА БАЗЫ ДАННЫХ

## В.1 ER-диаграмма в нотации Mermaid

```mermaid
erDiagram
    Player {
        int id PK
        string username
        string email
        string password_hash
        int total_score
        bool is_anonymous_player
        string avatar
        datetime created_at
    }

    Question {
        int id PK
        string text_uz
        string category
        int difficulty
        string question_type
        int time_limit
        string explanation_uz
        string source
        bool is_active
    }

    Answer {
        int id PK
        int question_id FK
        string text_uz
        bool is_correct
        int order
    }

    QuizSession {
        int id PK
        int player_id FK
        string mode
        string category
        int score
        int correct_count
        int total_questions
        int current_streak
        int max_streak
        datetime started_at
        datetime finished_at
    }

    QuizAnswer {
        int id PK
        int session_id FK
        int question_id FK
        int selected_answer_id FK
        bool is_correct
        int time_spent_ms
    }

    DailyChallenge {
        int id PK
        date date
        int bonus_score
        int completed_count
        datetime created_at
    }

    Achievement {
        int id PK
        string key
        string title_uz
        string description_uz
        string condition_type
        json condition_value
        string icon
        int points_reward
    }

    PlayerAchievement {
        int id PK
        int player_id FK
        int achievement_id FK
        datetime unlocked_at
    }

    LeaderboardEntry {
        int id PK
        int player_id FK
        int score
        string rank_title
        int quizzes_completed
        datetime updated_at
    }

    EducationalContent {
        int id PK
        string title_uz
        text content_uz
        string summary_uz
        string category
        int difficulty_level
        int read_time_minutes
        string slug
        bool is_published
    }

    EcoFact {
        int id PK
        string text_uz
        string category
        string source
        bool is_active
    }

    MiniGameScore {
        int id PK
        int player_id FK
        int score
        int correct_count
        int total_items
        datetime played_at
    }

    %% Связи
    Player ||--o{ QuizSession : "проводит"
    Player ||--o| LeaderboardEntry : "имеет"
    Player ||--o{ PlayerAchievement : "получает"
    Player ||--o{ MiniGameScore : "набирает"

    Question ||--o{ Answer : "содержит"
    Question }o--o{ DailyChallenge : "входит в"

    QuizSession ||--o{ QuizAnswer : "содержит"
    QuizAnswer }o--|| Question : "на"
    QuizAnswer }o--o| Answer : "выбран"

    Achievement ||--o{ PlayerAchievement : "выдаётся"
```

## В.2 Описание связей

| Связь | Кратность | Описание |
|-------|-----------|---------|
| Player → QuizSession | 1:N | Один игрок может иметь много сессий |
| Player → LeaderboardEntry | 1:1 | У каждого игрока одна запись в лидерборде |
| Player → PlayerAchievement | 1:N | Игрок может иметь много достижений |
| Question → Answer | 1:N | Вопрос имеет 2 или 4 варианта ответа |
| Question ↔ DailyChallenge | N:M | Вопросы могут входить в несколько ежедневных заданий |
| QuizSession → QuizAnswer | 1:N | Сессия содержит ответы на все вопросы |
| QuizAnswer → Answer | N:1 | Каждый ответ ссылается на выбранный вариант |
| Achievement → PlayerAchievement | 1:N | Достижение может быть выдано многим игрокам |

## В.3 Ключевые ограничения целостности

- `LeaderboardEntry.player` — UNIQUE (OneToOneField)
- `PlayerAchievement(player, achievement)` — UNIQUE TOGETHER
- `DailyChallenge.date` — UNIQUE
- `Answer.is_correct=True` — ровно один для MCQ вопросов (NOT ENFORCED на DB уровне, проверяется в QuizService)
- `QuizAnswer(session, question)` — UNIQUE TOGETHER (защита от повторного ответа)
