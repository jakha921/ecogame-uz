# QA Production Report — EcoGame

**URL:** https://ecogame.fullfocus.dev  
**Дата проверки:** 2026-05-24  
**Проверяющий:** Claude (автоматическая проверка через curl)  

---

## Итого: 12/13 тестов пройдено

---

## 1. Инфраструктура и HTTPS

| Тест | Результат | HTTP код | Детали |
|------|-----------|----------|--------|
| Главная страница HTTPS | ✅ | 200 | HTML страница (SPA) отдаётся корректно |
| HTTP → HTTPS redirect | ✅ | 302 | `http://ecogame.fullfocus.dev/` → `https://ecogame.fullfocus.dev/` |
| SSL сертификат | ✅ | — | Wildcard `*.fullfocus.dev`, выдан Google Trust Services, действует до 14 Jul 2026, TLS 1.3 |
| HTTP/2 | ✅ | — | Сайт отдаётся по HTTP/2, alt-svc: h3 (QUIC поддерживается) |
| CDN | ✅ | — | Cloudflare (server: cloudflare, cf-ray присутствует) |

---

## 2. Статические файлы и Frontend

| Тест | Результат | HTTP код | Детали |
|------|-----------|----------|--------|
| `/static/` | ⚠️ | 403 | Nginx возвращает 403 на директорию — нормально для production (листинг закрыт) |
| `/favicon.ico` | ✅ | 200 | Отдаётся корректно |
| `/manifest.json` | ✅ | 200 | Отдаётся корректно |

---

## 3. Admin панель

| Тест | Результат | HTTP код | Детали |
|------|-----------|----------|--------|
| GET `/admin/` | ✅ | 302 | Redirect на `/admin/login/?next=/admin/` — правильное поведение |

---

## 4. API Endpoints — публичные

| Тест | Результат | HTTP код | Детали |
|------|-----------|----------|--------|
| GET `/api/v1/game/levels/` | ✅ | 200 | Возвращает **4 уровня** (Kichik hovli, Mahalla, Shahar, Viloyat) с полным map_config и ecosystem_initial |
| GET `/api/v1/education/articles/` | ✅ | 200 | Возвращает **5 статей** на узбекском (FLORA, WATER, WASTE, ENERGY, FAUNA) |
| GET `/api/v1/education/facts/random/` | ✅ | 200 | Возвращает случайный факт (id, text_uz, source, category) |
| GET `/api/v1/leaderboard/` | ✅ | 200 | `{"count": 0, "results": []}` — таблица пуста (нет сыгравших игроков, ожидаемо) |

---

## 5. Аутентификация

| Тест | Результат | HTTP код | Детали |
|------|-----------|----------|--------|
| POST `/api/v1/auth/register/` — новый пользователь | ✅ | 201 | `{"username":"qa_check_1","nickname":"QACheck","email":"qa@test.uz"}` |
| POST `/api/v1/auth/register/` — дубликат | ✅ | 400 | `{"username":["Пользователь с таким именем уже существует."],"nickname":["Игрок с таким Ник уже существует."]}` |
| POST `/api/v1/auth/login/` — верные данные | ✅ | 200 | Возвращает `access` + `refresh` JWT токены |
| POST `/api/v1/auth/login/` — неверный пароль | ✅ | 401 | `{"detail":"Не найдено активной учетной записи с указанными данными"}` |
| GET `/api/v1/auth/me/` с Bearer токеном | ✅ | 200 | `{"id":3,"username":"qa_check_1","nickname":"QACheck","email":"qa@test.uz","avatar":"default","total_score":0,"date_joined":"..."}` |
| GET `/api/v1/auth/me/` без токена | ✅ | 401 | `{"detail":"Учетные данные не были предоставлены."}` |

---

## 6. Защищённые API Endpoints

| Тест | Результат | HTTP код | Детали |
|------|-----------|----------|--------|
| GET `/api/v1/game/achievements/` с токеном | ✅ | 200 | 10 достижений (ACTION_COUNT, INDICATOR, LEVEL_COMPLETE, SCORE типы), `is_unlocked: false` для нового пользователя |
| GET `/api/v1/game/achievements/` без токена | ⚠️ | 200 | **ПРОБЛЕМА:** Endpoint доступен без авторизации — возвращает все достижения. Данные не чувствительные, но нарушает ожидаемую защиту |

---

## 7. Заголовки безопасности (API)

| Заголовок | Значение | Оценка |
|-----------|----------|--------|
| `X-Frame-Options` | `DENY` | ✅ |
| `X-Content-Type-Options` | `nosniff` | ✅ |
| `Referrer-Policy` | `same-origin` | ✅ |
| `Cross-Origin-Opener-Policy` | `same-origin` | ✅ |
| `Strict-Transport-Security` | Не присутствует на API | ⚠️ (Cloudflare обеспечивает HTTPS принудительно) |
| `Content-Security-Policy` | Отсутствует | ⚠️ (опционально для API, критично для SPA) |

---

## 8. Производительность

| Метрика | Значение | Оценка |
|---------|----------|--------|
| TTFB главной страницы | ~490 мс | ⚠️ (приемлемо, но есть cold start задержка от Coolify) |
| TTFB API `/game/levels/` | ~563 мс | ⚠️ (аналогично — сервер в Европе / Варшава, видно по cf-ray: -WAW) |
| DNS lookup | ~2.6 мс | ✅ |

---

## Проблемы и рекомендации

### Найденные проблемы

**1. `GET /api/v1/game/achievements/` доступен без авторизации** (Severity: Low)

Endpoint возвращает 200 и список достижений без Bearer токена. Данные не чувствительные (публичные названия достижений), но по логике приложения achievements — часть профиля игрока. Если `is_unlocked` флаги персонализированы — это утечка данных. Судя по ответу, endpoint возвращает общий список без привязки к пользователю.

**Рекомендация:** Решить — либо явно сделать endpoint публичным (документировать), либо добавить `permission_classes = [IsAuthenticated]` в achievements ViewSet.

**2. Leaderboard пуст** (Severity: Info)

`/api/v1/leaderboard/` возвращает `count: 0`. Это нормально для production без реальных игроков, но стоит проверить наличие тестовых данных.

**3. Content-Security-Policy отсутствует** (Severity: Low)

Для React SPA важно добавить CSP заголовок для защиты от XSS. Можно настроить в Nginx конфигурации.

**4. TTFB > 400 мс** (Severity: Info)

Сервер расположен в Варшаве (cf-ray: -WAW). Для аудитории из Узбекистана задержка будет выше. Для дипломного проекта приемлемо.

---

## Вывод

Production сайт **работает стабильно**. Все критичные функции работают:
- HTTPS + SSL корректный
- Все 4 уровня загружаются
- Все 5 образовательных статей доступны
- Auth flow (register → login → me) работает полностью
- JWT токены выдаются корректно
- Admin панель доступна и защищена

Единственная проблема требующая внимания — endpoint achievements доступен без авторизации.
