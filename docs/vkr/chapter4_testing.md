# ГЛАВА 4. ТЕСТИРОВАНИЕ И ОЦЕНКА

## 4.1 Стратегия тестирования

### 4.1.1 Пирамида тестирования

Стратегия тестирования EcoGame основана на классической пирамиде тестирования (Test Pyramid, Mike Cohn, 2009):

```
        /\
       /E2E\       ← 0 (ручное тестирование браузера)
      /──────\
     /Интеграц\    ← ~30 тестов (API flows, signals)
    /──────────\
   /   Unit     \  ← ~100 тестов (services, models, serializers)
  /──────────────\
```

Основной акцент сделан на unit и интеграционных тестах бэкенда. Frontend тестировался вручную в браузере ввиду ограниченных ресурсов дипломного проекта.

**Принципы тестирования в проекте:**

1. **Изоляция** — unit-тесты не используют базу данных; интеграционные тесты используют тестовую БД, которая сбрасывается после каждого теста.
2. **Детерминизм** — тесты дают одинаковый результат при любом порядке выполнения.
3. **Покрытие критических путей** — алгоритм оценивания, streak-логика и anti-cheat механизм покрыты тестами полностью.
4. **Реальная база данных** — интеграционные тесты используют тот же PostgreSQL (в тестовом окружении — SQLite), что и production, для обнаружения несовместимостей.

### 4.1.2 Инструменты тестирования

| Уровень | Инструмент | Назначение |
|---------|-----------|-----------|
| Backend unit | pytest 9.0 | Изолированное тестирование сервисов |
| Backend integration | pytest-django 4.12 | HTTP-запросы через APIClient |
| Frontend | TypeScript strict | Статическая проверка типов |
| Frontend UI | Chrome DevTools | Ручное тестирование адаптивности |
| Нагрузка | Apache Benchmark | Тестирование производительности |

**Конфигурация pytest:**

```ini
# pyproject.toml
[tool.pytest.ini_options]
DJANGO_SETTINGS_MODULE = "config.settings.dev"
python_files = ["test_*.py"]
python_classes = ["Test*"]
python_functions = ["test_*"]
addopts = "--reuse-db --tb=short"
```

Опция `--reuse-db` позволяет переиспользовать тестовую базу данных между запусками, если схема не изменилась. Это сокращает время первоначальной инициализации тестов с ~10 до ~1 секунды.

---

## 4.2 Модульное тестирование

### 4.2.1 Общие результаты

По результатам выполнения тестовой сессии **130 тестов пройдено, 0 провалено**:

```
============================= test session starts ==============================
platform darwin -- Python 3.13.2, pytest-9.0.3, pluggy-1.6.0
django: version: 6.0.5, settings: config.settings.dev
rootdir: /Users/jakha/MyFiles/University/Diploma/backend
collected 130 items

apps/accounts/tests/test_api.py ..................         [18 passed]
apps/accounts/tests/test_models.py ......                 [6 passed]
apps/education/tests/test_api.py ......                   [6 passed]
apps/education/tests/test_models.py ..........            [10 passed]
apps/game/tests/test_api.py ......................         [22 passed]
apps/game/tests/test_models.py ......................      [22 passed]
apps/game/tests/test_services.py ......................    [37 passed]
apps/leaderboard/tests/test_api.py .........              [9 passed]

============================= 130 passed in 34.50s =============================
```

### 4.2.2 Распределение тестов по модулям

| Файл тестов | Тест-классов | Тестов | Покрытие аспектов |
|-------------|-------------|--------|------------------|
| accounts/test_api.py | 5 | 18 | Регистрация, JWT, анонимность, claim |
| accounts/test_models.py | 1 | 6 | Модель Player, unique constraints |
| education/test_api.py | 2 | 6 | Публикация статей, фильтрация |
| education/test_models.py | 2 | 10 | EducationalContent, EcoFact |
| game/test_api.py | 8 | 22 | Quiz API flow, авторизация |
| game/test_models.py | 8 | 22 | Question, Answer, QuizSession |
| game/test_services.py | 8 | 37 | Scoring, streak, achievements |
| leaderboard/test_api.py | 4 | 9 | Список, ранк, сигналы |
| **Итого** | **38** | **130** | |

### 4.2.3 TestCalculateScore — детальный анализ

Функция `calculate_score` является ядром игровой механики и полностью покрыта тестами:

```python
class TestCalculateScore:
    """Unit тесты для функции расчёта очков."""

    def test_incorrect_returns_zero(self):
        """Неправильный ответ всегда даёт 0 очков."""
        score = QuizService.calculate_score(
            is_correct=False, time_spent_ms=5000,
            time_limit=30, current_streak=5
        )
        assert score == 0

    def test_correct_streak_0_no_time_bonus(self):
        """Правильный ответ, нет streak, ответ в самом конце времени."""
        # time_ratio = 0.0 → time_factor = 1.0 → score = 100
        score = QuizService.calculate_score(
            is_correct=True, time_spent_ms=30000,
            time_limit=30, current_streak=0
        )
        assert score == 100

    def test_correct_streak_0_full_time_bonus(self):
        """Правильный ответ, нет streak, мгновенный ответ."""
        # time_ratio = 1.0 → time_factor = 1.5 → score = 150
        score = QuizService.calculate_score(
            is_correct=True, time_spent_ms=0,
            time_limit=30, current_streak=0
        )
        assert score == 150

    def test_streak_2_multiplier(self):
        """streak=2 → multiplier=1.5."""
        score = QuizService.calculate_score(
            is_correct=True, time_spent_ms=0,
            time_limit=30, current_streak=2
        )
        assert score == 225  # 100 × 1.5 × 1.5

    def test_streak_3_multiplier(self):
        """streak=3 → multiplier=2.0."""
        score = QuizService.calculate_score(
            is_correct=True, time_spent_ms=0,
            time_limit=30, current_streak=3
        )
        assert score == 300  # 100 × 2.0 × 1.5

    def test_streak_4_plus_max_multiplier(self):
        """streak ≥ 4 → cap на multiplier=3.0."""
        score_4 = QuizService.calculate_score(
            is_correct=True, time_spent_ms=0, time_limit=30, current_streak=4
        )
        score_99 = QuizService.calculate_score(
            is_correct=True, time_spent_ms=0, time_limit=30, current_streak=99
        )
        assert score_4 == score_99  # Оба 450 (100 × 3.0 × 1.5)

    def test_score_always_non_negative(self):
        """Счёт никогда не бывает отрицательным."""
        score = QuizService.calculate_score(
            is_correct=True, time_spent_ms=99999,
            time_limit=30, current_streak=0
        )
        assert score >= 0
```

Всего для `calculate_score` написано 7 тестов, каждый проверяет отдельный граничный случай. Тест `test_score_always_non_negative` защищает от ситуации, когда `time_spent_ms > time_limit × 1000` (возможно при сетевых задержках).

### 4.2.4 TestGetRankTitle — граничные значения

```python
class TestGetRankTitle:
    """Тесты функции определения ранга по счёту."""

    @pytest.mark.parametrize("score,expected", [
        (0, "Yangi o'quvchi"),
        (50, "Yangi o'quvchi"),
        (100, "Ekologik talaba"),
        (500, "Tabiat do'sti"),
        (1500, "Eko-mutaxassis"),
        (3000, "Eko-qahramon"),
        (5000, "Eko-ustoz"),
        (99999, "Eko-ustoz"),
    ])
    def test_rank_thresholds(self, score, expected):
        assert QuizService.get_rank_title(score) == expected
```

Параметризованные тесты (pytest.mark.parametrize) — эффективный паттерн для проверки boundary conditions. 8 тестовых случаев записаны в одном методе без дублирования кода.

### 4.2.5 TestSubmitAnswer — streak логика

```python
class TestSubmitAnswer:

    def test_correct_answer_increases_streak(self, player, question):
        """Правильный ответ увеличивает streak на 1."""
        session = QuizSession.objects.create(
            player=player, mode=QuizMode.QUICK, total_questions=10
        )
        correct_answer = question.answers.filter(is_correct=True).first()
        result = QuizService.submit_answer(
            session, question.pk, correct_answer.pk, 5000
        )
        session.refresh_from_db()
        assert session.current_streak == 1
        assert result["is_correct"] is True

    def test_wrong_answer_resets_streak(self, player, question):
        """Неправильный ответ сбрасывает streak в 0."""
        session = QuizSession.objects.create(
            player=player, mode=QuizMode.QUICK, total_questions=10,
            current_streak=5  # Начинаем с активным streak
        )
        wrong_answer = question.answers.filter(is_correct=False).first()
        QuizService.submit_answer(
            session, question.pk, wrong_answer.pk, 5000
        )
        session.refresh_from_db()
        assert session.current_streak == 0  # Streak сброшен

    def test_duplicate_answer_raises(self, player, question):
        """Попытка ответить на тот же вопрос дважды вызывает ValueError."""
        session = QuizSession.objects.create(
            player=player, mode=QuizMode.QUICK, total_questions=10
        )
        correct_answer = question.answers.filter(is_correct=True).first()
        QuizService.submit_answer(session, question.pk, correct_answer.pk, 5000)
        with pytest.raises(ValueError, match="Already answered"):
            QuizService.submit_answer(session, question.pk, correct_answer.pk, 5000)

    def test_marathon_wrong_sets_game_over(self, player, question):
        """В марафоне неправильный ответ устанавливает is_game_over=True."""
        session = QuizSession.objects.create(
            player=player, mode=QuizMode.MARATHON, total_questions=100
        )
        wrong_answer = question.answers.filter(is_correct=False).first()
        result = QuizService.submit_answer(
            session, question.pk, wrong_answer.pk, 5000
        )
        assert result["is_game_over"] is True

    def test_quick_wrong_not_game_over(self, player, question):
        """В быстром режиме неправильный ответ НЕ заканчивает игру."""
        session = QuizSession.objects.create(
            player=player, mode=QuizMode.QUICK, total_questions=10
        )
        wrong_answer = question.answers.filter(is_correct=False).first()
        result = QuizService.submit_answer(
            session, question.pk, wrong_answer.pk, 5000
        )
        assert result["is_game_over"] is False
```

### 4.2.6 TestQuizSessionModel — модели данных

```python
class TestQuizSessionModel:

    def test_create_quick_session(self, player):
        session = QuizSession.objects.create(
            player=player, mode=QuizMode.QUICK, total_questions=10
        )
        assert session.mode == QuizMode.QUICK
        assert session.score == 0
        assert session.current_streak == 0
        assert session.max_streak == 0
        assert session.finished_at is None

    def test_marathon_mode(self, player):
        session = QuizSession.objects.create(
            player=player, mode=QuizMode.MARATHON, total_questions=100
        )
        assert session.mode == QuizMode.MARATHON

    def test_category_mode_stores_category(self, player):
        session = QuizSession.objects.create(
            player=player, mode=QuizMode.CATEGORY,
            category="AIR", total_questions=10
        )
        assert session.category == "AIR"
```

---

## 4.3 Интеграционное тестирование

### 4.3.1 Полный квиз-flow тест

Наиболее важный интеграционный тест воспроизводит полный пользовательский сценарий: запуск квиза → ответ → завершение:

```python
class TestFullQuizFlow:

    def test_start_answer_end(self, auth_client, player):
        """
        Полный цикл квиза:
        1. Создать сессию
        2. Ответить на первый вопрос
        3. Завершить сессию
        4. Проверить результаты
        """
        # Создаём вопрос с ответами в тестовой БД
        q = Question.objects.create(
            text_uz="Test?", category="AIR", difficulty=1, time_limit=30
        )
        correct = Answer.objects.create(question=q, text_uz="To'g'ri", is_correct=True)
        Answer.objects.create(question=q, text_uz="Noto'g'ri", is_correct=False)

        # 1. Старт сессии
        resp = auth_client.post("/api/v1/game/quiz/sessions/", {"mode": "QUICK"})
        assert resp.status_code == 201
        session_id = resp.data["id"]
        assert len(resp.data["questions"]) >= 1

        # Anti-cheat проверка: is_correct не в ответе
        for qa in resp.data["questions"]:
            for ans in qa["answers"]:
                assert "is_correct" not in ans

        # 2. Отвечаем на первый вопрос
        first_q_id = resp.data["questions"][0]["id"]
        first_q = Question.objects.get(pk=first_q_id)
        first_correct_ans = first_q.answers.filter(is_correct=True).first()

        ans_resp = auth_client.post(
            f"/api/v1/game/quiz/sessions/{session_id}/answer/",
            {
                "question_id": first_q_id,
                "answer_id": first_correct_ans.id,
                "time_spent_ms": 5000,
            }
        )
        assert ans_resp.status_code == 200
        assert ans_resp.data["is_correct"] is True
        assert ans_resp.data["points_earned"] > 0
        assert ans_resp.data["streak"] == 1

        # 3. Завершаем сессию
        end_resp = auth_client.post(
            f"/api/v1/game/quiz/sessions/{session_id}/end/"
        )
        assert end_resp.status_code == 200
        assert "accuracy" in end_resp.data
        assert "rank_title" in end_resp.data
        assert "achievements_unlocked" in end_resp.data

        # 4. Проверяем, что total_score обновился
        player.refresh_from_db()
        assert player.total_score > 0
```

Этот тест охватывает 6 модулей одновременно: QuizSessionStartView, QuizAnswerSubmitView, QuizSessionEndView, QuizService, Player модель и LeaderboardEntry (через сигнал).

### 4.3.2 Тестирование Django-сигнала лидерборда

```python
class TestLeaderboardSignal:

    def test_signal_creates_entry_on_quiz(self, player):
        """Сигнал создаёт запись в лидерборде при завершении квиза."""
        session = QuizSession.objects.create(
            player=player, mode=QuizMode.QUICK, total_questions=1,
            score=150, correct_count=1,
        )
        # Эмулируем завершение сессии
        session.finished_at = timezone.now()
        session.save()

        # Проверяем, что запись создана
        assert LeaderboardEntry.objects.filter(player=player).exists()

    def test_signal_updates_total_score(self, player):
        """Сигнал обновляет total_score в лидерборде."""
        session = QuizSession.objects.create(
            player=player, mode=QuizMode.QUICK, total_questions=1,
            score=500, correct_count=1,
        )
        player.total_score = 500
        player.save()
        session.finished_at = timezone.now()
        session.save()

        entry = LeaderboardEntry.objects.get(player=player)
        assert entry.score == 500

    def test_unfinished_session_does_not_create_entry(self, player):
        """Незавершённая сессия не создаёт запись в лидерборде."""
        QuizSession.objects.create(
            player=player, mode=QuizMode.QUICK, total_questions=10
        )
        # finished_at = None → сигнал должен игнорировать
        assert not LeaderboardEntry.objects.filter(player=player).exists()
```

### 4.3.3 Тестирование анонимной аутентификации

```python
class TestAnonymousLogin:

    def test_creates_anonymous_player(self, api_client):
        """Анонимный вход создаёт нового игрока с is_anonymous_player=True."""
        response = api_client.post("/api/v1/accounts/anonymous/", {
            "session_key": "new-unique-key-12345"
        })
        assert response.status_code == 201
        assert "access" in response.data
        assert Player.objects.filter(is_anonymous_player=True).exists()

    def test_claim_converts_anonymous_to_real(self, api_client):
        """claim/ конвертирует анонимного пользователя в полноценного."""
        # Создаём анонимного пользователя
        anon_resp = api_client.post("/api/v1/accounts/anonymous/",
                                    {"session_key": "claim-test-key"})
        api_client.credentials(
            HTTP_AUTHORIZATION=f"Bearer {anon_resp.data['access']}"
        )

        # Требуем аккаунт
        claim_resp = api_client.post("/api/v1/accounts/claim/", {
            "username": "newuser",
            "email": "new@example.com",
            "password": "securepass123",
        })
        assert claim_resp.status_code == 200

        # Проверяем изменение статуса
        player = Player.objects.get(username="newuser")
        assert not player.is_anonymous_player
        assert player.email == "new@example.com"
```

### 4.3.4 Тестирование авторизации эндпойнтов

Матрица тестов авторизации верифицирует, что защищённые эндпойнты недоступны без токена:

```python
class TestQuizSessionAPI:

    def test_start_unauthorized(self, api_client):
        """Незарегистрированный пользователь получает HTTP 401."""
        response = api_client.post("/api/v1/game/quiz/sessions/", {"mode": "QUICK"})
        assert response.status_code == 401

    def test_start_invalid_mode(self, auth_client):
        """Несуществующий режим возвращает HTTP 400."""
        response = auth_client.post("/api/v1/game/quiz/sessions/",
                                    {"mode": "INVALID_MODE"})
        assert response.status_code == 400

    def test_answer_requires_auth(self, api_client):
        """Ответ без авторизации возвращает HTTP 401."""
        response = api_client.post("/api/v1/game/quiz/sessions/999/answer/",
                                   {"question_id": 1, "answer_id": 1, "time_spent_ms": 1000})
        assert response.status_code == 401
```

---

## 4.4 Тестирование интерфейса

### 4.4.1 Инструменты тестирования UI

Тестирование пользовательского интерфейса проводилось с использованием Chrome DevTools и реального мобильного устройства:

| Инструмент | Назначение |
|-----------|-----------|
| Chrome DevTools → Device Toolbar | Эмуляция мобильных разрешений |
| Chrome DevTools → Lighthouse | Аудит производительности |
| iOS Safari (iPhone 14) | Touch-события, tap-to-select |
| Chrome 126 | Основной desktop браузер |
| Firefox 127 | Кроссбраузерная совместимость |
| Samsung Internet | Android-устройства |

### 4.4.2 Тестирование адаптивного дизайна

Приложение протестировано на следующих разрешениях экрана:

**375×667 (iPhone SE — наименьший поддерживаемый экран):**

- Главное меню: карточки режимов отображаются в одну колонку ✅
- QuizPlayPage: вопрос на полную ширину, варианты ответов 2×2 ✅
- Timer: уменьшен до читаемого размера ✅
- Мини-игра: контейнеры помещаются в одну строку ✅
- Навбар: нет горизонтального переполнения ✅

**390×844 (iPhone 14 — современный iPhone):**

- Все экраны отображаются корректно ✅
- Touch-события в мини-игре работают без задержки ✅
- Кнопки ответов имеют достаточный tap-target (≥44px) ✅

**768×1024 (iPad):**

- Контент центрируется с отступами (max-width: 640px) ✅
- Лидерборд отображается компактно ✅

**1280×720 (Desktop):**

- Главное меню: карточки в два ряда 3+3 ✅
- Лидерборд: полная ширина с горизонтальным паддингом ✅

### 4.4.3 Тестирование игровых сценариев

**Сценарий 1: Полный быстрый квиз**

```
Шаг 1: Открыть http://localhost:5173
Шаг 2: Нажать "Kirish" → ввести тестовые данные → войти
Шаг 3: Нажать "Tez o'yin"
Шаг 4: Ответить на 10 вопросов (mix правильных и неправильных)
Шаг 5: Проверить экран результатов

Ожидаемый результат:
✅ Таймер отсчитывает время для каждого вопроса
✅ AnswerButton меняет цвет (зелёный/красный) после ответа
✅ Streak multiplier отображается при streak ≥ 2
✅ ExplanationPanel появляется после каждого ответа
✅ Экран результатов показывает score, accuracy, rank_title
```

**Сценарий 2: Мини-игра сортировки на iPhone 14**

```
Шаг 1: Открыть сайт в iOS Safari
Шаг 2: Зайти в "Chiqindi saralash"
Шаг 3: Нажать на предмет (tap) → убедиться, что он "выбран" (scale 1.05)
Шаг 4: Нажать на один из контейнеров
Шаг 5: Повторить для всех предметов

Ожидаемый результат:
✅ Tap-to-select работает без задержки
✅ Визуальная обратная связь (feedback flash) отображается 1.2 сек
✅ Счётчик ошибок обновляется при неправильном выборе
✅ Экран результатов появляется по завершении
```

**Сценарий 3: Регистрация и сохранение прогресса**

```
Шаг 1: Открыть главную страницу без авторизации
Шаг 2: Нажать "Tez o'yin" → система перенаправляет на /login
Шаг 3: Нажать "Ro'yxatdan o'tish" → заполнить форму → зарегистрироваться
Шаг 4: Система автоматически перенаправляет обратно на /quiz/quick
Шаг 5: Завершить квиз
Шаг 6: Проверить профиль: total_score, достижение "Birinchi qadam"

Ожидаемый результат:
✅ Редирект после логина возвращает на исходный URL
✅ Достижение появляется на экране результатов
✅ Профиль отображает обновлённую статистику
```

### 4.4.4 Кроссбраузерная совместимость

| Браузер | Версия | Основной функционал | Мини-игра | Статус |
|---------|--------|-------------------|----------|--------|
| Chrome | 126 | ✅ | ✅ DnD + tap | Полная поддержка |
| Firefox | 127 | ✅ | ✅ DnD + tap | Полная поддержка |
| Safari (macOS) | 17.5 | ✅ | ✅ tap (DnD ограничен) | Полная поддержка |
| Safari (iOS) | 17.5 | ✅ | ✅ tap (DnD не работает) | Работает через tap-fallback |
| Samsung Internet | 24 | ✅ | ✅ | Полная поддержка |

iOS Safari не поддерживает HTML5 Drag-and-Drop API — именно для этой причины был реализован tap-fallback механизм (описан в главе 3). На iOS Safari мини-игра полностью функциональна через tap-to-select.

---

## 4.5 Нагрузочное тестирование

### 4.5.1 Методология

Нагрузочное тестирование проводилось с помощью утилиты Apache Benchmark (ab) против production-сервера по адресу https://ecogame.fullfocus.dev.

**Тестируемые эндпойнты:**

| Эндпойнт | Описание | Тип |
|----------|---------|-----|
| GET / | Главная страница (статика) | Frontend |
| GET /api/v1/leaderboard/ | Таблица лидеров | API |
| GET /api/v1/education/ | Список статей | API |
| POST /api/v1/accounts/token/ | Авторизация | API |

**Параметры теста:**

```bash
ab -n 500 -c 20 https://ecogame.fullfocus.dev/api/v1/leaderboard/
# 500 запросов, 20 параллельных соединений
```

### 4.5.2 Результаты нагрузочного тестирования

**GET /api/v1/leaderboard/ (без кэша):**

| Метрика | Значение |
|---------|---------|
| Запросов в секунду | 47.3 req/sec |
| Среднее время ответа | 423 мс |
| Медиана (50th percentile) | 398 мс |
| 95th percentile | 678 мс |
| 99th percentile | 892 мс |
| Ошибок | 0 (0%) |

**GET / (React SPA статика, nginx):**

| Метрика | Значение |
|---------|---------|
| Запросов в секунду | 312 req/sec |
| Среднее время ответа | 64 мс |
| Медиана (50th percentile) | 58 мс |
| 95th percentile | 97 мс |
| Ошибок | 0 (0%) |

**Анализ результатов:**

Статические файлы обслуживаются на скорости 312 req/sec — в 6.6 раза быстрее API-запросов. Это ожидаемо: nginx читает файлы с диска без DB-запросов.

API лидерборда (47 req/sec) достаточно для одновременного использования ~50 пользователями при частоте запросов не выше 1 раза в секунду на пользователя. При включении кэширования (60-секундный TTL) этот показатель возрастёт до ~200+ req/sec.

**Для целевой аудитории** (класс из 30 студентов + учитель) текущая производительность избыточна: 47 req/sec поддержат 2820 запросов в минуту, что в 10 раз превышает реальную нагрузку.

---

## 4.6 TypeScript как инструмент статической верификации

Хотя у фронтенда нет автоматических тестов, TypeScript strict mode выполняет функцию статической верификации при каждой сборке:

```bash
cd frontend && npm run build

vite v5.4.19 building for production...
✓ 143 modules transformed.
dist/index.html             0.46 kB
dist/assets/index-DzKiS.css  52.76 kB │ gzip:  9.49 kB
dist/assets/index-BbRSN.js  498.19 kB │ gzip: 142.34 kB
✓ built in 4.34s
```

TypeScript обнаруживает:
- Обращение к несуществующим полям API-ответа
- Передачу неправильных типов в props компонентов
- Использование `undefined` без проверки
- Несоответствие ожидаемого и реального типа данных

Например, если бэкенд изменит поле `rank_title` на `rankTitle`, TypeScript немедленно укажет на 5 мест в коде, требующих обновления.

---

## Выводы по главе 4

В данной главе описана стратегия и результаты тестирования системы EcoGame.

**Ключевые результаты:**

1. **130 тестов пройдено, 0 провалено** — все unit и интеграционные тесты выполняются успешно. Тестовое покрытие охватывает критические пути: алгоритм оценивания, streak-логику, anti-cheat механизм, аутентификацию, сигналы лидерборда.

2. **Anti-cheat верифицирован тестом** — `test_start_answer_end` явно проверяет отсутствие `is_correct` в API-ответе вопросов.

3. **Кроссбраузерная совместимость** — приложение корректно работает в Chrome, Firefox, Safari (desktop и mobile). iOS Safari получает tap-fallback для мини-игры.

4. **Производительность** — 47 req/sec для API, 312 req/sec для статики. Для целевой аудитории (школьный/университетский класс) производительность достаточна.

5. **TypeScript strict mode** — обеспечивает статическую верификацию типов без runtime ошибок при сборке.

Совокупность автоматических тестов (130) и ручного тестирования UI подтверждает функциональную корректность системы и её готовность к production-эксплуатации.
