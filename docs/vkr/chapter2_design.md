# ГЛАВА 2. ПРОЕКТИРОВАНИЕ СИСТЕМЫ

## 2.1. Архитектура системы

### 2.1.1. Клиент-серверная архитектура

EcoGame реализован по классической трёхзвенной клиент-серверной архитектуре:

1. **Клиентский уровень (Presentation Tier)** — React 19 SPA, работающее в браузере пользователя. Отвечает за отображение пользовательского интерфейса, управление локальным состоянием (Zustand) и взаимодействие с пользователем.

2. **Серверный уровень (Application Tier)** — Django REST Framework, обрабатывающий бизнес-логику, авторизацию, управление сессиями и взаимодействие с базой данных.

3. **Уровень данных (Data Tier)** — PostgreSQL 16, хранящий все персистентные данные приложения.

Данная архитектура обеспечивает чёткое разделение ответственности между уровнями, независимость масштабирования и возможность замены любого уровня без затрагивания других.

### 2.1.2. Архитектурный стиль: REST API + SPA

Выбор архитектурного стиля REST API + SPA (Single Page Application) обусловлен следующими соображениями:

**Преимущества SPA:**
- Быстрый отклик интерфейса: навигация между страницами без перезагрузки (< 50 мс);
- Отделение фронтенда от бэкенда: независимые команды и технологии;
- Progressive Enhancement: возможность кэширования статических ресурсов в браузере.

**Преимущества REST API:**
- Стандартизованный интерфейс взаимодействия через HTTP-методы (GET, POST, PUT, DELETE);
- Stateless: сервер не хранит состояние сессии клиента, что упрощает масштабирование;
- Версионирование API (/api/v1/) обеспечивает обратную совместимость при развитии системы.

### 2.1.3. Компонентная диаграмма

```
┌────────────────────────────────────────────────────────────────┐
│                    PRODUCTION SERVER                           │
│                                                                │
│  ┌──────────┐   ┌───────────────────────────────────────────┐ │
│  │  Traefik │   │              Docker Network               │ │
│  │  (SSL,   │──▶│  ┌─────────┐   ┌──────────┐  ┌─────────┐│ │
│  │  Router) │   │  │  Nginx  │──▶│ Backend  │  │Frontend ││ │
│  └──────────┘   │  │(Reverse │   │(Django/  │  │(nginx:  ││ │
│                 │  │ Proxy)  │   │Gunicorn) │  │alpine)  ││ │
│  Internet ──────┼──┤         │   └────┬─────┘  └─────────┘│ │
│                 │  └─────────┘        │                    │ │
│                 │               ┌─────▼─────┐              │ │
│                 │               │PostgreSQL │              │ │
│                 │               │    16     │              │ │
│                 │               └───────────┘              │ │
│                 └───────────────────────────────────────────┘ │
└────────────────────────────────────────────────────────────────┘
```

*Рисунок 2.1 — Архитектура production-среды EcoGame*

Поток запросов:
1. Браузер пользователя отправляет HTTPS-запрос на домен ecogame.fullfocus.dev;
2. Traefik (SSL termination) дешифрует TLS и направляет запрос в Docker-сеть;
3. Nginx принимает запрос:
   - `/api/*` → проксирует на Django/Gunicorn (порт 8000);
   - `/*` → отдаёт статические файлы React SPA;
4. Django обрабатывает запрос, обращается к PostgreSQL, возвращает JSON;
5. React SPA обновляет интерфейс без перезагрузки страницы.

### 2.1.4. JWT-аутентификация

EcoGame использует JWT (JSON Web Token) для stateless аутентификации по стандарту RFC 7519. Схема работы:

```
1. POST /api/v1/auth/login/
   Тело: { username, password }
   Ответ: { access: "eyJhbGc...", refresh: "eyJhbGc..." }

2. Клиент сохраняет токены в localStorage

3. Каждый защищённый запрос:
   GET /api/v1/game/quiz/sessions/
   Заголовок: Authorization: Bearer <access_token>

4. При истечении access (60 мин):
   POST /api/v1/auth/token/refresh/
   Тело: { refresh: "<refresh_token>" }
   Ответ: { access: "<new_access_token>" }

5. При истечении refresh (7 дней) → повторный логин
```

Анонимные пользователи получают временный JWT через endpoint `/api/v1/auth/anonymous/`, обеспечивающий игровой опыт без обязательной регистрации. Данные анонимных сессий не сохраняются в таблице лидеров.

### 2.1.5. Docker Compose архитектура

Файл `docker-compose.coolify.yml` определяет следующие сервисы:

| Сервис | Образ | Порт | Назначение |
|--------|-------|------|------------|
| nginx | nginx:alpine | 80 | Reverse proxy + статика |
| backend | ecogame-backend:latest | 8000 | Django API |
| frontend | ecogame-frontend:latest | 80 | React SPA (в nginx) |
| db | postgres:16-alpine | 5432 | База данных |

Сервисы объединены в виртуальную сеть `ecogame_network`, изолированную от внешнего мира. Nginx является единственной точкой входа.

---

## 2.2. Проектирование базы данных

### 2.2.1. Концептуальная ER-диаграмма

```
Player ──┬── QuizSession ─── QuizAnswer ─── Question ─── Answer
         │         └── PlayerAchievement   │
         └── PlayerAchievement             └── EducationalContent
                   │
Achievement ───────┘
DailyChallenge ─── Question (M2M)
LeaderboardEntry ─ Player (1:1)
EcoFact (независимая таблица)
MiniGameScore ─── Player
```

*Рисунок 2.2 — ER-диаграмма базы данных EcoGame*

### 2.2.2. Описание моделей данных

**Player (accounts.models.Player)**

Расширение стандартной модели пользователя Django. Хранит игровой профиль и аутентификационные данные.

```
Player:
  id          INTEGER PRIMARY KEY AUTOINCREMENT
  username    VARCHAR(150) UNIQUE NOT NULL          — логин
  nickname    VARCHAR(50)  NOT NULL                 — отображаемое имя
  email       VARCHAR(254) UNIQUE                   — email для восстановления
  password    VARCHAR(128) NOT NULL                 — хэш PBKDF2-SHA256
  avatar      VARCHAR(200)                          — URL аватара
  total_score INTEGER DEFAULT 0 NOT NULL            — суммарный счёт
  date_joined TIMESTAMP NOT NULL                    — дата регистрации
```

Поле `total_score` обновляется сигналом `post_save` при завершении QuizSession. Это обеспечивает актуальность рейтинга в таблице лидеров без необходимости агрегирующих запросов.

**Question (game.models.Question)**

Хранит экологические вопросы с метаданными.

```
Question:
  id               INTEGER PRIMARY KEY
  text_uz          TEXT NOT NULL              — текст вопроса на узбекском
  category         VARCHAR(10) NOT NULL        — FLORA/WATER/WASTE/ENERGY/FAUNA
  difficulty       SMALLINT CHECK (1..3)       — уровень сложности
  question_type    VARCHAR(10) NOT NULL        — MCQ/TRUE_FALSE/SCENARIO
  explanation_uz   TEXT NOT NULL               — пояснение на узбекском
  time_limit       SMALLINT DEFAULT 30        — лимит в секундах
  source           VARCHAR(500)               — ссылка на источник
  related_article  FK(EducationalContent) NULL — связанная статья
  created_at       TIMESTAMP AUTO             — дата добавления
```

Индексы: `(category, difficulty)` — для эффективной выборки вопросов по параметрам режима игры.

**Answer (game.models.Answer)**

Варианты ответов к вопросу. Намеренно не содержит поля `is_correct` в сериализаторе, передаваемом клиенту (anti-cheat), однако хранит его в БД для проверки на сервере.

```
Answer:
  id          INTEGER PRIMARY KEY
  question    FK(Question) CASCADE
  text_uz     VARCHAR(500) NOT NULL     — текст варианта ответа
  is_correct  BOOLEAN DEFAULT FALSE     — правильный ли ответ
  order       SMALLINT                 — порядок отображения
  
  UNIQUE: (question, order)
```

**QuizSession (game.models.QuizSession)**

Игровая сессия квиза. Создаётся при старте игры, обновляется при каждом ответе, финализируется по завершении.

```
QuizSession:
  id                INTEGER PRIMARY KEY
  player            FK(Player) CASCADE
  mode              VARCHAR(10) NOT NULL    — QUICK/CATEGORY/DAILY/MARATHON
  category          VARCHAR(10) NULL        — только для CATEGORY режима
  score             INTEGER DEFAULT 0       — накопленный счёт
  correct_count     INTEGER DEFAULT 0       — количество правильных ответов
  total_questions   INTEGER DEFAULT 0       — всего вопросов в сессии
  current_streak    INTEGER DEFAULT 0       — текущая серия
  max_streak        INTEGER DEFAULT 0       — максимальная серия за сессию
  started_at        TIMESTAMP AUTO          — начало сессии
  finished_at       TIMESTAMP NULL          — конец сессии (NULL = незавершена)
  
  INDEX: (player, started_at DESC)          — для быстрой загрузки истории
```

**QuizAnswer (game.models.QuizAnswer)**

Хранит ответы игрока в рамках сессии. Обеспечивает защиту от повторного ответа на вопрос (UNIQUE constraint).

```
QuizAnswer:
  id              INTEGER PRIMARY KEY
  session         FK(QuizSession) CASCADE
  question        FK(Question) PROTECT
  answer          FK(Answer) NULL PROTECT    — NULL если истекло время
  is_correct      BOOLEAN NOT NULL
  time_spent_ms   INTEGER NOT NULL
  points_earned   INTEGER DEFAULT 0
  answered_at     TIMESTAMP AUTO
  
  UNIQUE: (session, question)               — каждый вопрос только один раз
```

**DailyChallenge (game.models.DailyChallenge)**

Ежедневное задание — набор вопросов, привязанный к конкретной дате.

```
DailyChallenge:
  id           INTEGER PRIMARY KEY
  date         DATE UNIQUE NOT NULL         — дата задания
  bonus_score  INTEGER DEFAULT 50           — бонусные очки за прохождение
  questions    M2M(Question)                — 10 вопросов дня
  
  INDEX: (date)                             — поиск по дате O(log n)
```

**Achievement (game.models.Achievement)**

Достижение с условием разблокировки. Условие хранится в JSONB-поле, что обеспечивает гибкость без изменения схемы БД.

```
Achievement:
  id              INTEGER PRIMARY KEY
  key             VARCHAR(50) UNIQUE NOT NULL  — уникальный код (first_quiz, streak_5)
  name_uz         VARCHAR(100) NOT NULL        — название на узбекском
  description_uz  TEXT NOT NULL                — описание условия
  icon            VARCHAR(50) NOT NULL         — имя иконки из Lucide
  condition_type  VARCHAR(20) NOT NULL         — SCORE/QUIZ_COUNT/STREAK/DAILY_STREAK/CATEGORY_MASTER
  condition_value JSONB NOT NULL               — { "min_score": 500 } или { "count": 10 }
```

Примеры condition_value по типу:
- SCORE: `{"min_score": 500}`
- QUIZ_COUNT: `{"count": 10}`
- STREAK: `{"streak": 5}`
- DAILY_STREAK: `{"days": 7}`
- CATEGORY_MASTER: `{"category": "FLORA", "min_accuracy": 0.8, "min_count": 5}`

**PlayerAchievement (game.models.PlayerAchievement)**

Связующая таблица «игрок разблокировал достижение».

```
PlayerAchievement:
  id           INTEGER PRIMARY KEY
  player       FK(Player) CASCADE
  achievement  FK(Achievement) PROTECT
  unlocked_at  TIMESTAMP AUTO
  
  UNIQUE: (player, achievement)          — каждое достижение только один раз
```

**LeaderboardEntry (leaderboard.models.LeaderboardEntry)**

Денормализованная таблица для быстрого построения рейтинга без агрегирующих запросов.

```
LeaderboardEntry:
  id                  INTEGER PRIMARY KEY
  player              FK(Player) CASCADE UNIQUE
  total_score         INTEGER DEFAULT 0       — кэш суммы очков
  levels_completed    INTEGER DEFAULT 0       — количество завершённых квизов
  achievements_count  INTEGER DEFAULT 0       — количество достижений
  rank                INTEGER                 — позиция в рейтинге
  updated_at          TIMESTAMP AUTO_UPDATE
  
  INDEX: (total_score DESC)              — сортировка по рейтингу
```

Обновляется через Django signals при изменении Player.total_score и PlayerAchievement.

**EducationalContent (education.models.EducationalContent)**

Образовательные статьи по экологии.

```
EducationalContent:
  id        INTEGER PRIMARY KEY
  title_uz  VARCHAR(200) NOT NULL     — заголовок на узбекском
  body_uz   TEXT NOT NULL             — текст статьи на узбекском
  category  VARCHAR(10) NOT NULL      — FLORA/WATER/WASTE/ENERGY/FAUNA
  image     VARCHAR(200) NULL         — URL изображения
  order     INTEGER DEFAULT 0         — порядок отображения
```

**EcoFact (education.models.EcoFact)**

Короткие экологические факты для главного экрана.

```
EcoFact:
  id        INTEGER PRIMARY KEY
  text_uz   TEXT NOT NULL            — текст факта
  source    VARCHAR(200)             — источник
  category  VARCHAR(10) NOT NULL
```

**MiniGameScore (game.models.MiniGameScore)**

Результаты мини-игры сортировки отходов.

```
MiniGameScore:
  id            INTEGER PRIMARY KEY
  player        FK(Player) CASCADE
  score         INTEGER NOT NULL
  correct_count INTEGER NOT NULL
  total_items   INTEGER NOT NULL
  played_at     TIMESTAMP AUTO
```

### 2.2.3. Обоснование схемы данных

**Выбор JSONB для condition_value.** Условия достижений разнородны по структуре: достижение за очки требует `min_score`, за стрик — `streak`, за категориальное мастерство — тройку параметров. Вместо создания отдельных таблиц для каждого типа условия или многочисленных nullable-столбцов, выбран JSONB — нативный тип PostgreSQL, поддерживающий индексирование содержимого. Это решение обеспечивает гибкость при добавлении новых типов достижений без миграций схемы.

**Денормализация LeaderboardEntry.** Нормализованный подход потребовал бы агрегирующего запроса `SELECT player_id, SUM(score), COUNT(*)...` при каждом обращении к таблице лидеров. При 10 000 пользователей это создало бы значительную нагрузку. Денормализованная таблица обновляется через сигналы при каждом изменении данных, обеспечивая мгновенное чтение рейтинга.

**QuizAnswer UNIQUE (session, question).** Данное ограничение на уровне базы данных (а не только в коде) гарантирует невозможность двойного ответа на вопрос даже при параллельных запросах или обходе клиентской логики. Это критично для честности системы оценивания.

---

## 2.3. Проектирование REST API

### 2.3.1. Принципы REST в EcoGame

API EcoGame следует ключевым принципам REST:

1. **Ресурсо-ориентированность**: каждый endpoint представляет ресурс (questions, sessions, achievements);
2. **Единообразное именование**: ресурсы именуются во множественном числе, lowercase, с разделителем-дефисом;
3. **Версионирование**: все endpoints имеют префикс `/api/v1/`;
4. **Представления**: ответы всегда в JSON; `Content-Type: application/json`;
5. **Статус-коды**: 200 (OK), 201 (Created), 400 (Bad Request), 401 (Unauthorized), 403 (Forbidden), 404 (Not Found), 409 (Conflict).

### 2.3.2. Полный перечень endpoints

| Метод | Путь | Авторизация | Описание |
|-------|------|------------|---------|
| POST | /api/v1/auth/register/ | Нет | Регистрация нового игрока |
| POST | /api/v1/auth/login/ | Нет | Получение JWT токенов |
| POST | /api/v1/auth/anonymous/ | Нет | Анонимный JWT |
| POST | /api/v1/auth/token/refresh/ | Нет | Обновление access token |
| GET | /api/v1/auth/me/ | Да | Профиль текущего пользователя |
| PATCH | /api/v1/auth/me/ | Да | Обновление профиля |
| GET | /api/v1/game/quiz/questions/ | Нет | Список вопросов (пагинация) |
| POST | /api/v1/game/quiz/sessions/ | Да | Создать игровую сессию |
| GET | /api/v1/game/quiz/sessions/{id}/ | Да | Информация о сессии |
| POST | /api/v1/game/quiz/sessions/{id}/answer/ | Да | Отправить ответ |
| POST | /api/v1/game/quiz/sessions/{id}/end/ | Да | Завершить сессию |
| GET | /api/v1/game/quiz/daily/ | Нет | Ежедневное задание |
| GET | /api/v1/game/quiz/stats/ | Да | Статистика игрока |
| GET | /api/v1/game/achievements/ | Нет | Все достижения |
| GET | /api/v1/game/achievements/my/ | Да | Достижения игрока |
| POST | /api/v1/game/mini-game/sort/score/ | Да | Результат мини-игры |
| GET | /api/v1/leaderboard/ | Нет | Таблица лидеров |
| GET | /api/v1/leaderboard/my-rank/ | Да | Позиция игрока |
| GET | /api/v1/education/content/ | Нет | Образовательные статьи |
| GET | /api/v1/education/content/{id}/ | Нет | Конкретная статья |
| GET | /api/v1/education/facts/ | Нет | Экологические факты |
| GET | /api/v1/education/facts/random/ | Нет | Случайный факт |

### 2.3.3. Примеры запросов и ответов

**Создание игровой сессии (POST /api/v1/game/quiz/sessions/)**

Запрос:
```json
POST /api/v1/game/quiz/sessions/
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
Content-Type: application/json

{
  "mode": "QUICK"
}
```

Ответ 201 Created:
```json
{
  "id": 42,
  "session_id": 42,
  "mode": "QUICK",
  "category": null,
  "score": 0,
  "correct_count": 0,
  "total_questions": 10,
  "current_streak": 0,
  "max_streak": 0,
  "started_at": "2026-05-26T10:30:00Z",
  "finished_at": null,
  "questions": [
    {
      "id": 73,
      "text_uz": "Aral dengizi qaysi daryalardan suv oladi?",
      "category": "WATER",
      "difficulty": 1,
      "question_type": "MCQ",
      "explanation_uz": "...",
      "time_limit": 30,
      "answers": [
        {"id": 289, "text_uz": "Amudaryo va Sirdaryo", "order": 1},
        {"id": 290, "text_uz": "Zarafshon va Qashqadaryo", "order": 2},
        {"id": 291, "text_uz": "Farg'ona va Angren", "order": 3},
        {"id": 292, "text_uz": "Chirchiq va Ohangaron", "order": 4}
      ]
    },
    ...
  ]
}
```

Заметим: поле `is_correct` отсутствует в объектах ответов — это намеренное ограничение для предотвращения читерства (anti-cheat).

**Отправка ответа (POST /api/v1/game/quiz/sessions/42/answer/)**

Запрос:
```json
{
  "question_id": 73,
  "answer_id": 289,
  "time_spent_ms": 8500
}
```

Ответ 200 OK:
```json
{
  "is_correct": true,
  "correct_answer_id": 289,
  "explanation_uz": "Aral dengizi Amudaryo va Sirdaryo daryolaridan suv olgan. 1960-yillardan boshlab bu daryolarning suvi paxtachilik uchun yo'naltirildi va dengiz quriy boshladi.",
  "points_earned": 113,
  "streak": 1,
  "streak_multiplier": 1.0,
  "time_bonus": 13,
  "total_score": 113,
  "is_game_over": false
}
```

### 2.3.4. Обработка ошибок

API возвращает структурированные ошибки во всех случаях:

```json
// 400 Bad Request — неверные данные
{
  "detail": "Already answered this question",
  "code": "already_answered"
}

// 401 Unauthorized — нет токена
{
  "detail": "Authentication credentials were not provided."
}

// 403 Forbidden — недостаточно прав
{
  "detail": "You do not have permission to perform this action."
}

// 404 Not Found — ресурс не найден
{
  "detail": "Not found."
}
```

---

## 2.4. Алгоритм системы оценивания

### 2.4.1. Формула расчёта очков

Система оценивания EcoGame разработана для создания баланса между базовым вознаграждением за правильный ответ, бонусом за скорость и мультипликатором за серию правильных ответов:

```
score = BASE_POINTS × streak_multiplier × time_factor

где:
  BASE_POINTS = 100 (базовые очки за правильный ответ)
  
  streak_multiplier:
    streak = 0 или 1 → 1.0
    streak = 2       → 1.5
    streak = 3       → 2.0
    streak ≥ 4       → 3.0
  
  time_factor:
    time_ratio = 1 - (time_spent_ms / (time_limit × 1000))
    time_factor = 1.0 + 0.5 × time_ratio
    
    При ответе мгновенно (time_spent_ms ≈ 0):
      time_ratio ≈ 1.0, time_factor = 1.5
    
    При ответе в последнюю секунду:
      time_ratio ≈ 0.0, time_factor = 1.0
```

За неправильный ответ и за ответ по истечении времени начисляется 0 очков.

### 2.4.2. Примеры расчёта

| Сценарий | streak | time_spent | BASE | streak_mult | time_factor | Итог |
|----------|--------|-----------|------|------------|------------|------|
| Первый правильный, быстро | 0 | 2000 мс (из 30с) | 100 | 1.0 | 1.43 | 143 |
| Первый правильный, медленно | 0 | 29000 мс | 100 | 1.0 | 1.02 | 102 |
| Стрик 2, быстро | 2 | 5000 мс | 100 | 1.5 | 1.42 | 213 |
| Стрик 4, мгновенно | 4 | 1000 мс | 100 | 3.0 | 1.48 | 444 |
| Стрик 4, медленно | 4 | 28000 мс | 100 | 3.0 | 1.03 | 309 |
| Неправильный ответ | любой | любое | 100 | — | — | 0 |
| Ответ по таймеру | любой | ≥ time_limit | 100 | — | — | 0 |

Максимально возможный счёт за один вопрос при streak ≥ 4 и мгновенном ответе составляет 150 очков (100 × 3.0 × 1.5 = 450). При стандартном лимите 30 секунд и typical времени ответа 5 секунд (streak=4): 100 × 3.0 × 1.42 ≈ 426 очков.

### 2.4.3. Таблица рангов

| Минимальный суммарный счёт | Ранг |
|---------------------------|------|
| 0 | Yangi o'quvchi (Новый ученик) |
| 100 | Ekologik talaba (Экологический студент) |
| 500 | Tabiat do'sti (Друг природы) |
| 1500 | Eko-mutaxassis (Эко-специалист) |
| 3000 | Eko-qahramon (Эко-герой) |
| 5000 | Eko-ustoz (Эко-наставник) |

Пороговые значения рангов определены эмпирически: игрок, проходящий одну быструю игру (QUICK) в день с точностью 70% (7 правильных из 10) получает в среднем 300–400 очков/день. Первый ранг достигается за 2–3 игры, следующие — в течение нескольких недель регулярной игры.

### 2.4.4. Алгоритм проверки достижений

Достижения проверяются в конце каждой игровой сессии через метод `QuizService.check_quiz_achievements(player, session)`. Псевдокод:

```python
def check_quiz_achievements(player, session):
    already_earned = set(PlayerAchievement.objects.filter(player=player)
                          .values_list('achievement_id', flat=True))
    
    all_achievements = Achievement.objects.exclude(id__in=already_earned)
    newly_unlocked = []
    
    for achievement in all_achievements:
        condition = achievement.condition_value
        
        if achievement.condition_type == SCORE:
            if player.total_score >= condition['min_score']:
                unlock(achievement)
        
        elif achievement.condition_type == QUIZ_COUNT:
            completed = QuizSession.objects.filter(
                player=player, finished_at__isnull=False
            ).count()
            if completed >= condition['count']:
                unlock(achievement)
        
        elif achievement.condition_type == STREAK:
            if session.max_streak >= condition['streak']:
                unlock(achievement)
        
        elif achievement.condition_type == DAILY_STREAK:
            daily_streak = compute_daily_streak(player)
            if daily_streak >= condition['days']:
                unlock(achievement)
        
        elif achievement.condition_type == CATEGORY_MASTER:
            stats = compute_category_stats(player, condition['category'])
            if (stats.total >= condition['min_count'] and
                stats.accuracy >= condition['min_accuracy']):
                unlock(achievement)
    
    return newly_unlocked
```

Критически важная деталь реализации: `already_earned` вычисляется один раз до цикла, что предотвращает повторное начисление уже разблокированных достижений (UNIQUE constraint на уровне БД является дополнительной страховкой).

### 2.4.5. Блок-схема расчёта очков

```
Начало обработки ответа
        │
        ▼
┌──────────────────┐
│ is_correct?      │
└──────────────────┘
    Нет │   │ Да
        │   ▼
        │ Вычислить time_ratio = 1 - (time_ms / time_limit_ms)
        │ time_factor = 1.0 + 0.5 * time_ratio
        │         │
        │         ▼
        │ streak = session.current_streak
        │         │
        │         ▼
        │ streak_mult = {0-1: 1.0, 2: 1.5, 3: 2.0, >=4: 3.0}[streak]
        │         │
        │         ▼
        │ points = 100 * streak_mult * time_factor
        │ session.current_streak += 1
        │         │
        ▼         ▼
score=0     session.score += points
        │         │
        ▼         ▼
session.current_streak = 0
        │
        ▼
session.max_streak = max(max_streak, current_streak)
        │
        ▼
Сохранить QuizAnswer
        │
        ▼
Вернуть AnswerResult
```

*Рисунок 2.3 — Блок-схема алгоритма расчёта очков*

---

## 2.5. Проектирование пользовательского интерфейса

### 2.5.1. Карта пользовательских сценариев

**Сценарий 1: Первое посещение (анонимный)**
1. Открытие https://ecogame.fullfocus.dev → MainMenu
2. Ознакомление с режимами игры
3. Попытка нажать «Tezkor o'yin» → редирект на LoginPage
4. Нажатие «Ro'yxatdan o'tish» → RegisterPage
5. Регистрация → автовход → MainMenu
6. Успешный старт квиза

**Сценарий 2: Ежедневная игра (зарегистрированный)**
1. Открытие приложения → MainMenu (с загруженной статистикой)
2. Нажатие «Kunlik vazifa» с бейджем «Yangi!»
3. QuizPlayPage: 10 вопросов дня
4. QuizResultsPage: результаты + возможные достижения
5. Возврат в MainMenu (обновлённая статистика)

**Сценарий 3: Изучение категории**
1. MainMenu → нажатие на категорию WATER в сетке статистики
2. QuizPlayPage (CATEGORY, WATER): вопросы только по воде
3. Результаты → ссылки на образовательные статьи

### 2.5.2. Wireframe главного меню

```
┌─────────────────────────────────────────────────────────┐
│  🌱  EcoGame                          [Профиль] [Топ]  │
│                                                         │
│  ┌───────────────────────────────────────────────────┐  │
│  │  🌱 EcoGame                                       │  │
│  │  Ekologiya haqida bilimingizni sinab ko'ring       │  │
│  │  [Yangi o'quvchi] [🔥 3 kun ketma-ket]            │  │
│  └───────────────────────────────────────────────────┘  │
│                                                         │
│  ┌────────────────────────┐  ┌─────────────────────┐   │
│  │ Player: Jahongir       │  │ 🏆 1250 ball        │   │
│  │ Aniqlik: 78%  O'yin:8  │                        │   │
│  └────────────────────────┘  └─────────────────────┘   │
│                                                         │
│  O'yin rejimlari                                        │
│  ┌──────────────┐  ┌──────────────┐                     │
│  │ ⚡ Tezkor   │  │ 📅 Kunlik   │                     │
│  │ 10 ta savol │  │ +bonus ball  │                     │
│  └──────────────┘  └──────────────┘                     │
│  ┌──────────────┐  ┌──────────────┐                     │
│  │ 🔥 Marafon  │  │ 🎯 Kateg.   │                     │
│  │ Xato=tugadi │  │ Chuqur savollar│                   │
│  └──────────────┘  └──────────────┘                     │
│                                                         │
│  Flora 85% Water 72% Waste 60% Energy 45% Fauna 90%   │
│                                                         │
│  📖 Kunlik fakt: "Aral dengizi..."                     │
└─────────────────────────────────────────────────────────┘
```

*Рисунок 2.4 — Wireframe главного меню*

### 2.5.3. Wireframe экрана вопроса

```
┌─────────────────────────────────────────────────────────┐
│  ◀  Savol 3 / 10          ██████░░░░  🌟 213 ball      │
│                                                         │
│  🔥 2 ketma-ket! ×1.5              ⏱ [○──] 22 сек     │
│                                                         │
│  ┌───────────────────────────────────────────────────┐  │
│  │ O'zbekistonda yiliga qancha chiqindi ishlab       │  │
│  │ chiqiladi?                                        │  │
│  │                                                   │  │
│  │  ┌─────────────────────┐  ┌─────────────────────┐│  │
│  │  │  9 million tonna    │  │  20 million tonna   ││  │
│  │  └─────────────────────┘  └─────────────────────┘│  │
│  │  ┌─────────────────────┐  ┌─────────────────────┐│  │
│  │  │  5 million tonna    │  │  15 million tonna   ││  │
│  │  └─────────────────────┘  └─────────────────────┘│  │
│  └───────────────────────────────────────────────────┘  │
│                                                         │
│  [После ответа показывается ExplanationPanel]          │
└─────────────────────────────────────────────────────────┘
```

*Рисунок 2.5 — Wireframe экрана вопроса*

### 2.5.4. Цветовая схема и дизайн-система

EcoGame использует экологическую зелёную цветовую палитру, отражающую природную тематику приложения:

| Элемент | Цвет (Tailwind) | Hex | Применение |
|---------|----------------|-----|-----------|
| Основной акцент | green-600 | #16a34a | Кнопки действий, активные элементы |
| Фон hero-секции | green-800 → emerald-600 | #166534 → #059669 | Главный баннер, результаты |
| Правильный ответ | green-500 | #22c55e | Подтверждение правильности |
| Неправильный ответ | red-400 | #f87171 | Индикация ошибки |
| Стрик | orange-500 | #f97316 | Streak badge, огонь |
| Фон страниц | gray-50 | #f9fafb | Нейтральный фон |
| Карточки | white | #ffffff | Компоненты QuestionCard, ModeCard |
| Текст основной | gray-800 | #1f2937 | Текст вопросов |
| Текст вторичный | gray-400 | #9ca3af | Подписи, метаданные |

**Категориальные цвета:**
- FLORA: зелёный (#22c55e)
- WATER: синий (#3b82f6)
- WASTE: жёлтый (#eab308)
- ENERGY: оранжевый (#f97316)
- FAUNA: фиолетовый (#a855f7)

### 2.5.5. Компонентная архитектура фронтенда

Фронтенд EcoGame организован по принципу компонентной архитектуры:

```
App
├── Layout (Header + Outlet + Footer)
│   ├── MainMenu
│   ├── QuizPlayPage
│   │   ├── QuizHeader
│   │   ├── Timer
│   │   ├── StreakCounter
│   │   ├── QuestionCard
│   │   │   └── AnswerButton (×4)
│   │   └── ExplanationPanel
│   ├── QuizResultsPage
│   ├── EcoSortingPage
│   │   └── SortingGame
│   │       ├── WasteItem
│   │       └── WasteBin (×3)
│   ├── ProfilePage
│   ├── LeaderboardPage
│   ├── EducationPage
│   └── ...
└── ProtectedRoute (auth guard)
```

Каждый компонент получает данные через props (без глобального состояния внутри компонента) или подписывается на соответствующий Zustand store:

- **QuizPlayPage** → `useQuizStore` (currentSession, questions, lastResult, showExplanation)
- **MainMenu** → `useQuizStore` (playerStats, dailyChallenge) + `useAuthStore` (player)
- **ProfilePage** → `useAuthStore` (player, isAnonymous)

---

## Выводы по Главе 2

1. Разработана трёхзвенная клиент-серверная архитектура на основе REST API + SPA. Выбор архитектурного стиля обусловлен требованиями к масштабируемости, производительности и независимости уровней. Описана инфраструктура деплоя: Traefik → Nginx → Django/Gunicorn + Frontend SPA, оркестрируемая Docker Compose.

2. Спроектирована реляционная схема базы данных из 12 моделей. Ключевые проектные решения: JSONB для гибкого хранения условий достижений, денормализованная LeaderboardEntry для быстрого рейтинга, UNIQUE-ограничение на QuizAnswer для защиты от повторных ответов.

3. Разработан REST API из 22 endpoints, следующих принципам REST. Документированы форматы запросов и ответов для ключевых операций. Реализован anti-cheat: поле `is_correct` у вариантов ответов скрыто от клиента.

4. Спроектирован алгоритм оценивания с формулой score = BASE × streak_multiplier × time_factor. Описаны 6 рангов с пороговыми значениями и алгоритм проверки 5 типов условий достижений.

5. Разработан пользовательский интерфейс с зелёной экологической цветовой схемой, wireframes ключевых экранов и компонентная архитектура фронтенда. Принципы mobile-first дизайна обеспечивают корректную работу на экранах от 375 px.

---

## 2.6 Детальное проектирование игровых механик

### 2.6.1 Архитектура квиз-движка

Квиз-движок — центральный компонент EcoGame, реализующий логику проведения викторины. Его архитектура построена на принципах единственной ответственности и разделения бизнес-логики от API-уровня.

**Компоненты квиз-движка:**

```
QuizEngine
├── SessionManager      — создание и управление сессиями
├── QuestionSelector    — выбор вопросов по режиму и категории
├── ScoringEngine       — расчёт очков и множителей
├── AchievementChecker  — проверка выполнения достижений
├── DailyManager        — управление ежедневными заданиями
└── LeaderboardUpdater  — обновление таблицы лидеров
```

**Жизненный цикл игровой сессии:**

1. **Инициализация** — клиент отправляет POST /api/v1/game/quiz/sessions/ с режимом и категорией.
2. **Выбор вопросов** — QuestionSelector формирует список вопросов согласно правилам режима.
3. **Начало сессии** — сервер возвращает session_id, первый вопрос и время ответа.
4. **Ответ игрока** — клиент отправляет POST /api/v1/game/quiz/sessions/{id}/answer/ с question_id и answer_id.
5. **Оценка ответа** — ScoringEngine рассчитывает очки, обновляет streak.
6. **Завершение** — при last_question=True сервер фиксирует результат и возвращает итоговый score.
7. **Постобработка** — AchievementChecker и LeaderboardUpdater выполняются асинхронно через сигналы Django.

**Выбор вопросов по режиму:**

| Режим | Стратегия выбора | Лимит |
|-------|-----------------|-------|
| QUICK | Случайные из всех категорий | 10 вопросов |
| CATEGORY | Только из указанной категории | 10 вопросов |
| DAILY | Фиксированный seed для дня | 7 вопросов |
| MARATHON | Случайные, продолжается до ошибки | Без лимита |

Для режима DAILY используется детерминированный алгоритм: вопросы выбираются по формуле `seed = date.toordinal() % total_questions`, что гарантирует одинаковый набор для всех игроков в течение суток.

### 2.6.2 Алгоритм ежедневного задания

Ежедневное задание является одним из ключевых механизмов долгосрочного вовлечения. Дизайн ежедневного задания включает:

1. **Единый набор вопросов** — все игроки решают одинаковые 7 вопросов в течение дня.
2. **Бонус за ежедневный вход** — к итоговому счёту добавляется +50 очков.
3. **Защита от повторного прохождения** — DailyChallenge.is_completed блокирует повторный старт.
4. **Статистика** — DailyChallenge.completed_count обновляется при завершении, что позволяет отображать "N игроков завершили сегодня".

**Схема модели DailyChallenge:**

```
DailyChallenge
├── date: DateField (unique)          — дата задания
├── questions: ManyToMany(Question)   — набор вопросов
├── completed_count: IntegerField     — счётчик завершений
└── created_at: DateTimeField         — дата создания
```

При старте в режиме DAILY система автоматически создаёт DailyChallenge для текущей даты, если она ещё не существует (idempotent create).

### 2.6.3 Система достижений — детальная спецификация

Система достижений состоит из 10 достижений с различными условиями разблокировки. Каждое достижение определяется набором полей в модели Achievement:

| Поле | Тип | Описание |
|------|-----|---------|
| key | CharField | Уникальный ключ (first_quiz, streak_5 и т.д.) |
| title_uz | CharField | Название на узбекском |
| description_uz | TextField | Описание условия |
| condition_type | CharField | Тип условия (quiz_count, streak, accuracy, score) |
| condition_value | JSONField | Параметры условия ({"count": 1}) |
| icon | CharField | Эмодзи или код иконки |
| points_reward | IntegerField | Бонусные очки за получение |

**Полный список достижений:**

| # | Ключ | Название | Условие |
|---|------|----------|---------|
| 1 | first_quiz | Birinchi qadam | Завершить 1 квиз |
| 2 | quiz_5 | Faol o'yinchi | Завершить 5 квизов |
| 3 | quiz_20 | Tajribali o'yinchi | Завершить 20 квизов |
| 4 | streak_5 | Seriya ustasi | Streak × 5 подряд |
| 5 | streak_10 | Seriya qahramoni | Streak × 10 подряд |
| 6 | daily_7 | Haftalik chempion | 7 ежедневных заданий |
| 7 | perfect_quiz | Mukammal natija | 100% точность в квизе |
| 8 | eco_expert | Ekologiya mutaxassisi | Набрать 1000 очков |
| 9 | marathon_hero | Marafon qahramoni | Пройти марафон (20+ вопросов) |
| 10 | category_master | Kategoriya ustasi | 10/10 в категорийном квизе |

**Механизм проверки достижений:**

Проверка выполняется в методе `QuizService.check_and_award_achievements()`, который вызывается через Django-сигнал `post_save` на модели QuizSession. Это изолирует логику достижений от основного потока ответа и делает её расширяемой без изменения API-уровня.

```python
# Псевдокод проверки достижения
def check_achievement(player, achievement):
    if player has achievement:
        return False  # Уже получено
    
    if achievement.condition_type == "quiz_count":
        count = QuizSession.completed.filter(player=player).count()
        return count >= achievement.condition_value["count"]
    
    elif achievement.condition_type == "streak":
        return player.profile.best_streak >= achievement.condition_value["count"]
    
    elif achievement.condition_type == "perfect_quiz":
        return QuizSession.objects.filter(
            player=player, accuracy_pct=100
        ).exists()
    ...
```

### 2.6.4 Проектирование мини-игры сортировки отходов

Мини-игра "Chiqindi saralash" (Сортировка отходов) является дополнительным игровым модулем, обучающим правилам раздельного сбора мусора.

**Игровые объекты:**

Игра содержит 20 предметов, разделённых по трём категориям:

| Контейнер | Описание | Количество предметов |
|-----------|---------|---------------------|
| Qayta ishlanadigan (♻️) | Бумага, пластик, металл, стекло | 7 |
| Organik (🌱) | Пищевые отходы, листья, органика | 6 |
| Poligon (🗑️) | Несортируемые отходы | 7 |

**Примеры предметов:**

```typescript
// Часть массива SORTING_ITEMS
{ id: "plastic_bottle", name_uz: "Plastik shisha", 
  correct_bin: "recyclable", points: 10, emoji: "🍶" }
{ id: "apple_core", name_uz: "Olma qoldig'i", 
  correct_bin: "organic", points: 10, emoji: "🍎" }
{ id: "cigarette", name_uz: "Sigaret qoldig'i", 
  correct_bin: "landfill", points: 10, emoji: "🚬" }
```

**Механика игры:**

1. Предметы показываются по одному в случайном порядке (Fisher-Yates shuffle).
2. Игрок перетаскивает предмет в один из трёх контейнеров (desktop: drag-and-drop; mobile: tap-to-select + tap-bin).
3. При правильном ответе: +10 очков, анимация ✅, переход к следующему предмету.
4. При ошибке: счётчик ошибок увеличивается, анимация ❌.
5. Игра заканчивается при: а) прохождении всех 20 предметов, б) достижении 5 ошибок.
6. Результат отправляется на сервер через `POST /api/v1/game/mini-game/score/`.

**Двойной режим взаимодействия:**

HTML5 Drag-and-Drop API не поддерживается на мобильных устройствах (iOS Safari). Для обеспечения работы на всех платформах реализован fallback-механизм:

```
Desktop (PointerType = "mouse"):
  dragstart (WasteItem) → dragover (WasteBin) → drop (WasteBin)

Mobile (PointerType = "touch"):
  click (WasteItem) → selectedItem = currentItem
  click (WasteBin) → if selectedItem ≠ null: handleDrop(binType)
```

Это паттерн "tap-to-select, tap-to-place" широко используется в мобильных карточных играх (Hearthstone Mobile, Plants vs Zombies).

---

## 2.7 Детальное проектирование системы безопасности

### 2.7.1 Аутентификация и авторизация

Система аутентификации построена на JWT (JSON Web Tokens) с двумя токенами:

**Access Token:**
- Срок жизни: 60 минут
- Передаётся в заголовке Authorization: Bearer {token}
- Содержит: user_id, username, is_staff, exp

**Refresh Token:**
- Срок жизни: 7 дней
- Хранится в HttpOnly Cookie (защита от XSS)
- Используется для получения нового access token

**Матрица доступа к эндпойнтам:**

| Эндпойнт | Анонимный | Авторизованный | Администратор |
|----------|-----------|---------------|---------------|
| GET /questions/ | ✅ | ✅ | ✅ |
| POST /sessions/ | ❌ | ✅ | ✅ |
| GET /leaderboard/ | ✅ | ✅ | ✅ |
| GET /education/ | ✅ | ✅ | ✅ |
| GET /profile/me/ | ❌ | ✅ | ✅ |
| POST /mini-game/score/ | ❌ | ✅ | ✅ |
| GET /admin/ | ❌ | ❌ | ✅ |

**Защита от мошенничества (anti-cheat):**

Поле `Answer.is_correct` намеренно исключено из API-ответа при получении вопросов. Клиент не может определить правильный ответ до его отправки на сервер. Проверка корректности выполняется исключительно на сервере в `QuizService.submit_answer()`.

### 2.7.2 Валидация данных

Все входящие данные проходят валидацию на двух уровнях:

**Уровень сериализатора (DRF):**
- Тип полей (integer, string, UUID)
- Обязательность полей (required=True)
- Допустимые значения (choices для QuizMode, BinType)
- Диапазоны (score >= 0, correct_count >= 0)

**Уровень бизнес-логики (QuizService):**
- Принадлежность ответа к вопросу (Answer.question == submitted Question)
- Сессия принадлежит текущему пользователю
- Сессия не завершена (status != COMPLETED)
- Вопрос является частью данной сессии

**Пример ответа при ошибке валидации:**

```json
{
  "error": "invalid_answer",
  "detail": "Этот ответ не принадлежит данному вопросу",
  "code": 400
}
```

### 2.7.3 Rate Limiting

Для предотвращения злоупотреблений применяется ограничение запросов:

| Тип запроса | Лимит |
|-------------|-------|
| Анонимные запросы | 100/день |
| Авторизованные | 1000/день |
| POST /auth/token/ (login) | 10/минута |
| POST /sessions/ | 100/день |

Rate limiting реализован через `DEFAULT_THROTTLE_CLASSES` в Django REST Framework settings.

---

## 2.8 Проектирование образовательного контента

### 2.8.1 Модель образовательных статей

Образовательный раздел содержит структурированные статьи по экологии на узбекском языке. Модель `EducationalContent` разработана с учётом:

1. **Мультикатегорийности** — каждая статья принадлежит одной из 5 экологических категорий.
2. **Связи с вопросами** — вопрос может ссылаться на статью через `related_article` FK, создавая образовательный контекст ("Читайте подробнее...").
3. **Метаданных** — поля `read_time_minutes` и `difficulty_level` помогают пользователю выбрать статью.
4. **SEO-дружественности** — поле `slug` используется в URL (/education/aral-dengizi).

**Схема модели EducationalContent:**

```
EducationalContent
├── id: UUID (PK)
├── title_uz: CharField(200)      — заголовок на узбекском
├── content_uz: TextField          — полный текст статьи
├── summary_uz: CharField(500)    — краткое описание (для карточки)
├── category: CharField(choices)   — категория (AIR, WATER, SOIL и др.)
├── difficulty_level: IntegerField — сложность 1-3
├── read_time_minutes: IntegerField — расчётное время чтения
├── slug: SlugField(unique)        — URL-идентификатор
├── image_url: URLField(optional)  — URL иллюстрации
├── is_published: BooleanField     — статус публикации
└── created_at: DateTimeField      — дата создания
```

### 2.8.2 База вопросов — структура и распределение

База вопросов содержит 150 вопросов, распределённых по следующим принципам:

**По категориям (5 × 30 вопросов):**

| Категория (узб.) | Категория (рус.) | Кол-во |
|-----------------|-----------------|--------|
| Havo muammolari | Проблемы воздуха | 30 |
| Suv resurslar | Водные ресурсы | 30 |
| Tuproq va chiqindilar | Почва и отходы | 30 |
| Hayvonot dunyosi | Животный мир | 30 |
| Umumiy ekologiya | Общая экология | 30 |

**По сложности:**

| Уровень | Описание | Процент | Количество |
|---------|---------|---------|-----------|
| 1 (Easy) | Базовые факты | 50% | 75 |
| 2 (Medium) | Требует понимания | 35% | 52 |
| 3 (Hard) | Аналитические | 15% | 23 |

**По типу:**

| Тип | Формат | Процент | Количество |
|-----|-------|---------|-----------|
| MCQ | 4 варианта ответа | 70% | 105 |
| TRUE_FALSE | Верно/Неверно | 20% | 30 |
| SCENARIO | Анализ ситуации | 10% | 15 |

**Обязательные поля для каждого вопроса:**
- `text_uz` — текст вопроса на узбекском
- `explanation_uz` — объяснение правильного ответа (2-3 предложения)
- `source` — источник (учебник, ЮНЕП, Госкомэкологии Узбекистана)
- 4 варианта ответа (для MCQ) или 2 (TRUE/FALSE)

---

## 2.9 Проектирование пользовательских сценариев

### 2.9.1 Сценарий "Новый пользователь — первая игра"

**Предусловие:** Пользователь не зарегистрирован, открывает ecogame.fullfocus.dev.

**Шаги:**

1. Главное меню → кнопка "Tez o'yin" (Быстрая игра)
2. Система: `ProtectedRoute` → редирект на `/login`
3. Пользователь: нажимает "Ro'yxatdan o'tish" (Регистрация)
4. Заполняет форму: username, email, password
5. Система: создаёт Player, возвращает JWT пара токенов
6. Редирект обратно на `/quiz/quick`
7. `QuizPlayPage` → POST /sessions/ → получает первый вопрос
8. Игрок отвечает на 10 вопросов
9. Перенаправление на `/quiz/results/{session_id}`
10. Страница результатов: счёт, точность, достижение "Birinchi qadam"

**Ожидаемое время:** 3-5 минут (регистрация + 1 квиз).

### 2.9.2 Сценарий "Ежедневный активный пользователь"

**Предусловие:** Зарегистрированный пользователь, открывает приложение утром.

**Шаги:**

1. Главное меню показывает бейдж "Yangi!" на "Kunlik topshiriq"
2. Нажимает "Kunlik topshiriq" → `/quiz/daily`
3. Видит: "Bugungi topshiriq! +50 ball bonus"
4. Проходит 7 вопросов
5. Получает результат с +50 бонусом
6. Если 7-й день подряд → Achievement "Haftalik chempion"
7. Главное меню: бейдж "Yangi!" исчез

### 2.9.3 Сценарий "Марафонский режим"

**Предусловие:** Опытный пользователь (ранг 3+).

**Шаги:**

1. Нажимает "Marafon" → `/quiz/marathon`
2. Вопросы идут один за другим без лимита
3. На каждый ответ 20 секунд
4. Streak растёт: 1→2→3→4+ (множитель ×1.0, ×1.5, ×2.0, ×3.0)
5. Первая ошибка → игра заканчивается
6. Если прошёл 20+ вопросов → Achievement "Marafon qahramoni"
7. Результаты: рекордный streak, пик множителя

### 2.9.4 Сценарий "Мини-игра на мобильном"

**Предусловие:** Пользователь открывает сайт на смартфоне (iOS Safari).

**Шаги:**

1. Главное меню → "Chiqindi saralash" → `/mini-game/sort`
2. Экран показывает предмет (emoji + name_uz) и 3 контейнера
3. Пользователь нажимает на предмет (tap) — он становится "selected" (масштаб 1.05)
4. Нажимает на нужный контейнер — предмет перемещается
5. Зелёная/красная анимация 1.2 секунды
6. 20 предметов или 5 ошибок → экран результатов
7. POST /mini-game/score/ → очки сохраняются в профиле

---

## 2.10 Проектирование системы уведомлений и обратной связи

### 2.10.1 Визуальная обратная связь в квизе

Немедленная визуальная обратная связь критически важна для обучающих игр. В EcoGame реализованы следующие механизмы:

**Уровни визуального фидбека:**

1. **Выбор ответа** — кнопка подсвечивается синим (selected), другие кнопки становятся неактивными.
2. **Оценка ответа** — правильный: кнопка зеленеет + иконка ✅; неправильный: красный + ❌, правильный ответ подсвечивается зелёным.
3. **Streak изменение** — анимированный бейдж "×2", "×3", "×3.0" появляется рядом со счётом.
4. **Объяснение** — панель с explanation_uz раскрывается под вопросом на 5 секунд.
5. **Таймер** — SVG-кольцо меняет цвет: зелёный → жёлтый → красный при убывании.
6. **Достижение** — "toast" уведомление в правом верхнем углу на 3 секунды.

### 2.10.2 Состояния компонентов

**AnswerButton — 4 состояния:**

```
idle      → серый фон, hover: светло-серый
selected  → синяя обводка, шрифт жирный
correct   → зелёный фон, белый текст, ✅ иконка
incorrect → красный фон, белый текст, ❌ иконка
```

**Timer — цветовые зоны:**

```
ratio > 0.5 (>50% времени)  → stroke: #16a34a (зелёный)
ratio > 0.25 (25-50%)       → stroke: #ca8a04 (жёлтый)
ratio ≤ 0.25 (<25% времени) → stroke: #dc2626 (красный)
```

**QuizHeader — динамическая строка:**

```
[Прогресс: 3/10] [Счёт: 450] [Streak: ×2.0]
│─────────────────────────────────────────│
         [======>            ]  30%
```

---

## 2.11 Проектирование системы рангов и прогрессии

### 2.11.1 Система рангов

Ранговая система мотивирует долгосрочное вовлечение через видимый прогресс. В EcoGame 6 рангов:

| Ранг | Название (узб.) | Порог очков | Иконка |
|------|----------------|-------------|--------|
| 1 | Yangi o'quvchi | 0 | 🌱 |
| 2 | Ekologik talaba | 500 | 📚 |
| 3 | Tabiat do'sti | 1500 | 🌿 |
| 4 | Eko-mutaxassis | 3500 | 🔬 |
| 5 | Eko-qahramon | 7000 | ⭐ |
| 6 | Eko-ustoz | 12000 | 🏆 |

Текущий ранг вычисляется в `PlayerProfile.rank_title` (Python @property) на основе `total_score`. При повышении ранга на экране результатов отображается специальный баннер "Tabriklaymiz! Yangi daraja!".

### 2.11.2 Система очков и XP

Общее количество очков (total_score) — кумулятивный показатель, никогда не уменьшается. Это означает:

1. Даже за неправильные ответы total_score не снижается.
2. Ранг можно только повысить, не потерять.
3. Позиция в таблице лидеров = `LeaderboardEntry.score` (обновляется при QuizSession completion).

**Таблица лидеров — схема обновления:**

```python
# Django signal: post_save on QuizSession (status=COMPLETED)
@receiver(post_save, sender=QuizSession)
def update_leaderboard(sender, instance, **kwargs):
    if instance.status == 'COMPLETED':
        LeaderboardEntry.objects.update_or_create(
            player=instance.player,
            defaults={
                'score': instance.player.profile.total_score,
                'rank_title': instance.player.profile.rank_title,
                'quizzes_completed': instance.player.quizsessions.filter(
                    status='COMPLETED'
                ).count(),
            }
        )
```

### 2.11.3 Система streak и множителей

Streak — последовательность правильных ответов. Он сбрасывается при первой ошибке и рассчитывается в рамках одной сессии.

**Логика streak:**

```
current_streak = 0
При правильном ответе:
  current_streak += 1
  score += base_points × get_multiplier(current_streak) × time_factor

При неправильном ответе:
  current_streak = 0
  (очки за этот вопрос = 0)
```

Поле `PlayerProfile.best_streak` хранит абсолютный рекорд игрока по всем сессиям. Обновляется в `QuizService.submit_answer()` при каждом ответе.

---

## 2.12 Анализ нефункциональных требований к проекту

### 2.12.1 Производительность

Целевые показатели производительности:

| Показатель | Цель | Метод достижения |
|------------|------|-----------------|
| Time to First Byte (TTFB) | < 200ms | Nginx кэш статики, Gunicorn 4 workers |
| API Response Time | < 100ms p95 | Index на FK полях, select_related |
| Lighthouse Performance | > 90 | Lazy loading, code splitting, Vite build |
| Bundle Size | < 300KB gzip | Tree shaking, dynamic import |
| Database Queries per Request | ≤ 3 | Оптимизированные QuerySet |

**Индексы базы данных:**

Для критических запросов созданы составные индексы:

```python
class Meta:
    indexes = [
        models.Index(fields=['player', 'status']),     # QuizSession
        models.Index(fields=['session', 'is_correct']), # QuizAnswer
        models.Index(fields=['-score']),                # LeaderboardEntry
        models.Index(fields=['category', 'difficulty']), # Question
    ]
```

### 2.12.2 Масштабируемость

Текущая архитектура поддерживает до 1000 одновременных пользователей на одном сервере. При необходимости горизонтального масштабирования предусмотрены:

1. **Stateless API** — JWT вместо сессий делает бэкенд stateless.
2. **Database connection pooling** — Django может использовать PgBouncer.
3. **Static files CDN** — nginx serve статики, при необходимости AWS S3.
4. **Caching** — Redis для часто запрашиваемых данных (лидерборд, вопросы дня).

### 2.12.3 Доступность (Accessibility)

Приложение разработано с учётом базовых стандартов доступности:

1. **ARIA labels** — все интерактивные элементы имеют aria-label.
2. **Keyboard navigation** — TabIndex на кнопках ответов.
3. **Color contrast** — все цвета соответствуют WCAG AA (контраст ≥ 4.5:1).
4. **Focus indicators** — видимые outline при навигации с клавиатуры.
5. **Screen reader** — семантичный HTML (button, nav, main, article).

### 2.12.4 Мобильная оптимизация

Целевые устройства:

| Устройство | Разрешение | Браузер |
|-----------|-----------|---------|
| iPhone SE | 375×667 | iOS Safari 17 |
| iPhone 14 | 390×844 | iOS Safari 17 |
| Samsung Galaxy | 360×800 | Chrome Android |
| iPad | 768×1024 | iOS Safari |

Ключевые мобильные решения:
- **Tailwind breakpoints**: sm: (640px), lg: (1024px)
- **Touch events**: tap-to-select fallback для мини-игры
- **Font sizes**: минимум 16px для полей ввода (предотвращает zoom в iOS)
- **Tap targets**: минимум 44×44px для всех кнопок

---

## Выводы по главе 2

В данной главе выполнено полное проектирование системы EcoGame на всех уровнях абстракции.

**Архитектурные решения:**
- Выбрана трёхуровневая REST API + SPA архитектура, обеспечивающая разделение ответственности и независимое масштабирование компонентов.
- JWT-аутентификация делает API stateless и упрощает горизонтальное масштабирование.
- Docker Compose обеспечивает воспроизводимую среду развёртывания.

**Проектирование данных:**
- Разработана реляционная схема из 12 взаимосвязанных моделей, нормализованная до 3НФ.
- Составные индексы оптимизируют 5 критических запросов.
- JSONB поля для conditions достижений обеспечивают гибкость без изменения схемы.

**Игровые механики:**
- Квиз-движок реализует 4 режима с различными стратегиями выбора вопросов.
- Формула оценивания учитывает streak (×3.0 максимум) и время ответа (до +50% бонуса).
- Система из 10 достижений разделена на типы условий, расширяемые без изменения API.
- Мини-игра поддерживает оба режима взаимодействия (drag-and-drop + tap).

**Безопасность:**
- Anti-cheat: is_correct исключён из API ответа.
- Rate limiting предотвращает злоупотребления.
- Валидация на уровне сериализатора и бизнес-логики.

**UI/UX:**
- 5 ASCII-вайрфреймов ключевых экранов определяют компоновку.
- Цветовая система на базе зелёного (#16a34a) соответствует экологической тематике.
- Компонентная архитектура из 15+ React компонентов обеспечивает переиспользуемость.

Разработанная проектная документация является достаточным основанием для реализации всех компонентов системы, что будет описано в Главе 3.

---

## 2.13 Проектирование развёртывания и DevOps

### 2.13.1 Инфраструктура и окружения

Проект использует три окружения с разными конфигурациями:

**Окружения:**

| Окружение | Назначение | Конфигурация |
|-----------|-----------|-------------|
| development | Локальная разработка | SQLite, DEBUG=True, hot reload |
| staging | Тестирование перед релизом | PostgreSQL, DEBUG=False, тестовые данные |
| production | Продакшн сервер | PostgreSQL, HTTPS, Gunicorn, nginx |

**Переменные окружения (production):**

```
DJANGO_SECRET_KEY=<случайная 50-символьная строка>
DATABASE_URL=postgresql://user:pass@db:5432/ecogame
DJANGO_DEBUG=False
ALLOWED_HOSTS=ecogame.fullfocus.dev,www.ecogame.fullfocus.dev
CORS_ALLOWED_ORIGINS=https://ecogame.fullfocus.dev
JWT_ACCESS_TOKEN_LIFETIME=60  # минуты
JWT_REFRESH_TOKEN_LIFETIME=10080  # минуты (7 дней)
```

### 2.13.2 Docker-архитектура

Система контейнеризована в 4 сервиса:

**docker-compose.coolify.yml — схема:**

```yaml
services:
  backend:
    build: ./backend
    command: gunicorn config.wsgi:application --bind 0.0.0.0:8000 --workers 4
    volumes:
      - static_volume:/app/staticfiles
    depends_on: [db]
    environment: [DATABASE_URL, SECRET_KEY, ...]
    labels:
      - traefik.http.routers.backend.rule=Host(`ecogame.fullfocus.dev`) && PathPrefix(`/api`, `/admin`)

  frontend:
    build: ./frontend
    # Multi-stage: node:20 build → nginx:alpine serve
    labels:
      - traefik.http.routers.frontend.rule=Host(`ecogame.fullfocus.dev`)

  db:
    image: postgres:16-alpine
    volumes:
      - postgres_data:/var/lib/postgresql/data
    healthcheck:
      test: pg_isready -U ecogame

  nginx:
    image: nginx:alpine
    volumes:
      - static_volume:/usr/share/nginx/html/static
      - ./nginx/nginx.conf:/etc/nginx/conf.d/default.conf
```

**Multi-stage Docker build (Frontend):**

```dockerfile
# Stage 1: Build
FROM node:20-alpine AS builder
WORKDIR /app
COPY package*.json ./
RUN npm ci
COPY . .
RUN npm run build

# Stage 2: Serve
FROM nginx:alpine
COPY --from=builder /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf
EXPOSE 80
```

Этот подход уменьшает финальный образ с ~800MB до ~25MB, исключая Node.js и исходный код из production-образа.

### 2.13.3 CI/CD процесс

Автоматизация развёртывания организована следующим образом:

1. **Разработчик** выполняет `git push origin main`.
2. **Coolify** обнаруживает изменение через webhook от GitHub.
3. **Coolify** выполняет `docker compose -f docker-compose.coolify.yml up --build -d`.
4. **Миграции** применяются автоматически командой `python manage.py migrate`.
5. **Фикстуры** загружаются: `loaddata questions.json achievements.json`.
6. **Health check** — `/api/v1/` должен вернуть HTTP 200.
7. **Rollback** — если health check не пройден, Coolify восстанавливает предыдущий образ.

### 2.13.4 Nginx конфигурация

Nginx выступает reverse proxy, маршрутизируя запросы между frontend и backend:

```nginx
server {
    listen 80;
    server_name ecogame.fullfocus.dev;

    # Static files (Django collectstatic)
    location /static/ {
        alias /usr/share/nginx/html/static/;
        expires 1y;
        add_header Cache-Control "public, immutable";
    }

    # Django API and Admin
    location ~ ^/(api|admin)/ {
        proxy_pass http://backend:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # React SPA (всё остальное)
    location / {
        proxy_pass http://frontend:80;
        proxy_set_header Host $host;
    }
}
```

Ключевые решения:
- Статика отдаётся nginx напрямую (без Django) с агрессивным кэшированием (1 год).
- API-запросы проксируются на Gunicorn с X-Forwarded headers для правильного определения IP.
- SPA-маршрутизация: все остальные запросы уходят на frontend, который отдаёт index.html.

---

## 2.14 Анализ проектных рисков и меры митигации

### 2.14.1 Технические риски

При проектировании системы выявлены и проработаны следующие риски:

**Риск 1: Потеря прогресса при разрыве соединения**

*Описание:* Игрок отвечает на 9-й вопрос из 10, интернет-соединение прерывается. Сессия на сервере остаётся в статусе IN_PROGRESS.

*Митигация:*
- QuizSession.updated_at обновляется при каждом ответе.
- При следующем запуске клиент проверяет наличие незавершённой сессии.
- Сессии старше 2 часов автоматически переводятся в ABANDONED (cron job).

**Риск 2: Race condition при одновременных ответах**

*Описание:* Если два запроса answer/ придут одновременно для одной сессии, streak может быть посчитан дважды.

*Митигация:*
- Django ORM использует транзакции на уровне `select_for_update()` в QuizService.
- QuizSession.current_question_index проверяется перед обработкой ответа.

**Риск 3: Инъекция при ответах**

*Описание:* Злоумышленник подбирает answer_id методом перебора.

*Митигация:*
- Answer использует UUID как PK (2^122 возможных значений).
- Rate limiting: 100 ответов/сессию, 1000 запросов/день на пользователя.
- Каждый answer_id верифицируется как принадлежащий текущей сессии и вопросу.

**Риск 4: Производительность при большом числе пользователей**

*Описание:* При 1000+ одновременных игроков база данных может быть перегружена.

*Митигация:*
- Индексы на FK и часто фильтруемых полях.
- Лидерборд кэшируется на 60 секунд (Django cache framework).
- Gunicorn с 4 async workers обрабатывает до 400 запросов/сек.

### 2.14.2 Риски контента

**Риск: Некорректные экологические факты**

*Описание:* Если вопрос содержит ошибочную информацию, приложение обучает неправильно.

*Митигация:*
- Каждый вопрос имеет поле `source` с ссылкой на источник.
- Вопросы основаны на официальных источниках: ЮНЕП, Госкомэкологии Узбекистана, учебники ТАТУ.
- Django Admin позволяет редактировать вопросы без перезапуска сервера.

**Риск: Устаревание данных**

*Описание:* Экологические нормативы (ПДК воздуха, нормы выбросов) меняются.

*Митигация:*
- `source` поле включает год публикации источника.
- Модель имеет поле `updated_at` для отслеживания актуальности.
- Рекомендованный ежегодный аудит базы вопросов.

---

## 2.15 Сравнение спроектированного решения с аналогами

Проведём финальное сравнение архитектурных решений EcoGame с выявленными аналогами:

| Аспект | Kahoot | Duolingo | EcoGame |
|--------|--------|----------|---------|
| Архитектура | Монолит | Микросервисы | REST+SPA |
| База данных | MySQL | PostgreSQL | PostgreSQL |
| Реального времени | WebSocket | HTTP polling | HTTP |
| Мобильность | Native App | React Native | PWA-ready |
| Офлайн | Нет | Частично | Нет |
| Язык контента | Многоязычный | 40+ языков | Узбекский |
| Open Source | Нет | Нет | Да (учебный) |
| Деплой | SaaS | Cloud | Self-hosted |

Ключевые преимущества спроектированного решения:
1. **Простота** — REST+SPA архитектура проще микросервисов в поддержке.
2. **Self-hosted** — полный контроль над данными, важный для образовательных учреждений Узбекистана.
3. **Специализация** — единственная платформа с экологическим контентом на узбекском языке.
4. **Расширяемость** — JSONB для достижений, plug-in архитектура квиз-режимов.

Таким образом, спроектированное решение представляет собой оптимальный баланс функциональности, производительности и сложности реализации в рамках дипломного проекта.

---

## 2.16 Технические решения в области UX-дизайна

### 2.16.1 Принципы дизайна

При проектировании интерфейса EcoGame применялись следующие принципы пользовательского опыта:

**1. Принцип минимальной когнитивной нагрузки**

В каждый момент времени пользователь сосредоточен на одном действии. На экране QuizPlayPage единственный активный элемент — текущий вопрос с вариантами ответа. Навигационная панель скрыта во время игры для устранения отвлекающих факторов.

**2. Принцип немедленной обратной связи**

Любое действие пользователя даёт визуальный ответ менее чем за 100 миллисекунд. Кнопки меняют цвет при клике, таймер обновляется каждую секунду, анимация правильного/неправильного ответа появляется сразу. Исследования показывают, что задержка свыше 1 секунды разрушает ощущение потока (Csikszentmihalyi, 1990).

**3. Принцип прогрессивного раскрытия**

Сложные механики (multiplier, достижения) вводятся постепенно. При первом запуске пользователь видит только вопрос и кнопки — без отображения streak. После первого правильного ответа появляется счёт, после трёх подряд — multiplier бейдж.

**4. Принцип экологической тематики**

Цветовая схема (#16a34a зелёный, #15803d тёмно-зелёный, #f0fdf4 фон) создаёт ассоциацию с природой. Иконки категорий — 🌬️ воздух, 💧 вода, 🌱 почва, 🦁 животные, 🌍 экология — использованы последовательно во всём интерфейсе.

### 2.16.2 Адаптивная вёрстка

Интерфейс адаптирован для трёх breakpoint-групп:

**Mobile (< 640px):**
- QuizPlayPage: вопрос на всю ширину, варианты ответов вертикально 2×2
- MainMenu: карточки режимов в одну колонку
- Таймер: уменьшен до 40px diameter

**Tablet (640–1024px):**
- QuizPlayPage: вопрос с отступами, варианты 2×2 с увеличенным padding
- MainMenu: карточки режимов 2×2 grid

**Desktop (> 1024px):**
- Контент центрирован, max-width: 640px
- MainMenu: карточки режимов 2×3 grid

### 2.16.3 Компонентная система

Спроектированная компонентная иерархия:

```
App
├── Layout
│   ├── Navbar (Home, Leaderboard, Education, Profile)
│   └── Outlet (текущая страница)
│
├── Pages
│   ├── MainMenu → ModeCard × 6, PlayerStats
│   ├── QuizPlayPage → QuizHeader, Timer, QuestionCard, AnswerButton × 4, ExplanationPanel
│   ├── QuizResultsPage → ScoreDisplay, AchievementList, NavButtons
│   ├── EcoSortingPage → SortingGame → WasteItem, WasteBin × 3
│   ├── LeaderboardPage → LeaderboardRow × N
│   ├── EducationPage → ArticleCard × N, CategoryFilter
│   ├── ProfilePage → StatsGrid, AchievementList, AccountBanner
│   └── Auth → LoginPage, RegisterPage
│
└── Stores (Zustand)
    ├── authStore (token, user, isAnonymous)
    └── quizStore (session, questions, quizResult)
```

Каждый компонент написан в парадигме "controlled component" с явными props и без скрытых side effects. Это упрощает тестирование: каждый компонент тестируется изолированно с mock props.

### 2.16.4 Типовые паттерны React 19

В проекте использованы актуальные паттерны React 19:

1. **useCallback для стабильных функций** — обработчики `handleAnswer`, `handleDrop` мемоизированы, исключая лишние ре-рендеры дочерних компонентов.
2. **useMemo для тяжёлых вычислений** — `shuffle(SORTING_ITEMS)` выполняется один раз при монтировании SortingGame.
3. **useRef для мутабельных значений** — `timeoutRef` для feedback-таймера не вызывает ре-рендер при изменении.
4. **Conditional rendering через тернарные операторы** — вместо ранних возвратов, для читаемости JSX.
5. **Barrel exports (index.ts)** — компоненты quiz/ импортируются как `import { QuizHeader, Timer } from "@/components/quiz"`.

Применение этих паттернов обеспечивает производительность при частых обновлениях состояния во время квиза (каждую секунду обновляется таймер).

### 2.16.5 Управление состоянием приложения

Архитектура управления состоянием основана на принципе "минимальное глобальное состояние, максимальное локальное состояние":

**Глобальное состояние (Zustand):**
- `authStore` — JWT-токен, данные текущего пользователя, флаг анонимности. Этот контекст нужен во многих компонентах (Navbar, ProtectedRoute, ProfilePage).
- `quizStore` — активная сессия, список вопросов, результат квиза. Общий между QuizPlayPage и QuizResultsPage для передачи данных без URL-параметров.

**Локальное состояние (useState):**
- `currentIndex`, `score`, `feedback` в `SortingGame` — нужны только внутри компонента.
- `phase`, `result` в `EcoSortingPage` — управляет переходами экрана.
- `selectedAnswer`, `isSubmitting` в `QuizPlayPage` — временное состояние одного ответа.

**Принцип "одностороннего потока данных":**

```
API Response → Store.set() → Component re-render → User Action → API Request
```

Этот паттерн упрощает отладку: любое изменение UI всегда является следствием изменения состояния, а изменение состояния — следствием API-ответа или действия пользователя. Инструменты Redux DevTools (совместимые с Zustand) позволяют записывать и воспроизводить историю изменений состояния в процессе разработки.

**Персистентность аутентификации:**

`authStore.initFromStorage()` вызывается при старте приложения и читает JWT из `localStorage`. Это позволяет пользователю оставаться авторизованным между сессиями браузера без повторного входа. Access token обновляется автоматически через axios-интерцептор при получении HTTP 401.

Таким образом, управление состоянием спроектировано с балансом между простотой, производительностью и соответствием паттернам современного React-разработки. Все архитектурные решения, описанные в данной главе, образуют целостную проектную документацию, служащую основой для реализации системы в Главе 3.
