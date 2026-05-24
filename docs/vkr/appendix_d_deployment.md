# Приложение Г. Диаграмма развёртывания

## Г.1. Общая схема развёртывания

```
┌─────────────────────────────────────────────────────────────────────┐
│                        ПОЛЬЗОВАТЕЛЬ (браузер)                       │
│                        https://ecogame.fullfocus.dev                │
└────────────────────────────────┬────────────────────────────────────┘
                                 │ HTTPS (443) + HTTP (80→303)
                                 ▼
┌─────────────────────────────────────────────────────────────────────┐
│                    CLOUDFLARE CDN (DNS Proxy)                       │
│            IP: 89.167.60.96  ←→  ecogame.fullfocus.dev             │
└────────────────────────────────┬────────────────────────────────────┘
                                 │ TCP 80 / 443
                                 ▼
┌──────────────────────── СЕРВЕР VPS (Debian) ────────────────────────┐
│  IP: 89.167.60.96   SSH port: 2222   User: deploy                  │
│                                                                     │
│  ┌──────────────────────────────────────────────────────────────┐   │
│  │                  Docker Engine                               │   │
│  │                                                              │   │
│  │  ┌──────────────────────────────────────────────────────┐   │   │
│  │  │ Сеть: coolify (bridge, external)                     │   │   │
│  │  │                                                      │   │   │
│  │  │  ┌────────────────────────────────────────────────┐  │   │   │
│  │  │  │ coolify-proxy (Traefik v3)                     │  │   │   │
│  │  │  │   :80 → HTTP entryPoint                        │  │   │   │
│  │  │  │   :443 → HTTPS entryPoint (Let's Encrypt)      │  │   │   │
│  │  │  │   certresolver: letsencrypt (HTTP challenge)   │  │   │   │
│  │  │  └───────────────────┬────────────────────────────┘  │   │   │
│  │  │                      │ маршрутизация по Host-header   │   │   │
│  │  └──────────────────────┼─────────────────────────────  │   │   │
│  │                         │                               │   │   │
│  │  ┌──────────────────────┼──────────────────────────┐    │   │   │
│  │  │ Сеть: ecogame (bridge, internal)                │    │   │   │
│  │  │                      │                          │    │   │   │
│  │  │        ┌─────────────▼────────────────────┐     │    │   │   │
│  │  │        │ ecogame-nginx-1 (nginx:alpine)   │     │    │   │   │
│  │  │        │ :80  (только внутри сети)         │     │    │   │   │
│  │  │        │ /api/*  → backend:8000            │     │    │   │   │
│  │  │        │ /admin/* → backend:8000           │     │    │   │   │
│  │  │        │ /static/* → volume static         │     │    │   │   │
│  │  │        │ /*      → frontend:80             │     │    │   │   │
│  │  │        └──────┬──────────────┬─────────────┘     │    │   │   │
│  │  │               │              │                    │    │   │   │
│  │  │   ┌───────────▼──┐  ┌────────▼──────────────┐    │    │   │   │
│  │  │   │ ecogame-     │  │ ecogame-frontend-1    │    │    │   │   │
│  │  │   │ backend-1    │  │ (nginx:alpine)         │    │    │   │   │
│  │  │   │ Django 6.0   │  │ React 19 SPA (static) │    │    │   │   │
│  │  │   │ + Gunicorn   │  │ /usr/share/nginx/html  │    │    │   │   │
│  │  │   │ :8000        │  │ :80                    │    │    │   │   │
│  │  │   └───────┬──────┘  └───────────────────────┘    │    │   │   │
│  │  │           │                                        │    │   │   │
│  │  │   ┌───────▼──────────────────────────────────┐   │    │   │   │
│  │  │   │ ecogame-postgres-1 (postgres:16-alpine)   │   │    │   │   │
│  │  │   │ :5432  (только внутри сети)               │   │    │   │   │
│  │  │   │ Volume: postgres_data (persistent)        │   │    │   │   │
│  │  │   └──────────────────────────────────────────┘   │    │   │   │
│  │  │                                                    │    │   │   │
│  │  │  Shared Volumes:                                   │    │   │   │
│  │  │    static_volume  → /app/static (nginx + backend)  │    │   │   │
│  │  │    media_volume   → /app/media  (nginx + backend)  │    │   │   │
│  │  └────────────────────────────────────────────────────┘    │   │   │
│  └──────────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────┘
```

## Г.2. Конфигурация Docker Compose (docker-compose.coolify.yml)

Ключевые параметры сервисов:

| Сервис | Образ | Порт (внутр.) | Зависит от |
|--------|-------|---------------|-----------|
| `postgres` | postgres:16-alpine | 5432 | — |
| `backend` | Dockerfile (python:3.12-slim) | 8000 | postgres (healthy) |
| `frontend` | Dockerfile (node:20 → nginx) | 80 | backend |
| `nginx` | Dockerfile (nginx:alpine) | 80 | backend, frontend |

Контейнер `nginx` подключён к двум сетям: внутренней `ecogame` (для
проксирования к backend и frontend) и внешней `coolify` (для получения
трафика от Traefik).

## Г.3. Traefik Labels (SSL и маршрутизация)

```yaml
labels:
  - "traefik.enable=true"
  # Middleware: редирект HTTP → HTTPS
  - "traefik.http.middlewares.ecogame-redirect-https.redirectscheme.scheme=https"
  # Middleware: gzip-сжатие
  - "traefik.http.middlewares.ecogame-gzip.compress=true"
  # HTTP-роутер (→ redirect to HTTPS)
  - "traefik.http.routers.http-0-ecogame-nginx.entryPoints=http"
  - "traefik.http.routers.http-0-ecogame-nginx.middlewares=ecogame-redirect-https"
  - "traefik.http.routers.http-0-ecogame-nginx.rule=Host(`ecogame.fullfocus.dev`) && PathPrefix(`/`)"
  - "traefik.http.routers.http-0-ecogame-nginx.service=ecogame-nginx"
  # HTTPS-роутер (с TLS)
  - "traefik.http.routers.https-0-ecogame-nginx.entryPoints=https"
  - "traefik.http.routers.https-0-ecogame-nginx.middlewares=ecogame-gzip"
  - "traefik.http.routers.https-0-ecogame-nginx.rule=Host(`ecogame.fullfocus.dev`) && PathPrefix(`/`)"
  - "traefik.http.routers.https-0-ecogame-nginx.tls=true"
  - "traefik.http.routers.https-0-ecogame-nginx.tls.certresolver=letsencrypt"
  - "traefik.http.routers.https-0-ecogame-nginx.service=ecogame-nginx"
  # Backend-сервис Traefik
  - "traefik.http.services.ecogame-nginx.loadbalancer.server.port=80"
```

## Г.4. Процесс развёртывания

```
1. git push origin main
       │
       ▼
2. SSH на сервер: ssh -p 2222 deploy@89.167.60.96
       │
       ▼
3. cd ~/ecogame && git pull
       │
       ▼
4. docker compose -f docker-compose.coolify.yml up -d --build
       │  (4 контейнера пересобираются)
       │
       ▼
5. docker compose exec backend uv run python manage.py migrate
       │
       ▼
6. docker compose exec backend uv run python manage.py loaddata \
       /app/fixtures/levels.json \
       /app/fixtures/eco_actions.json \
       /app/fixtures/achievements.json \
       /app/fixtures/educational_content.json \
       /app/fixtures/eco_facts.json
       │
       ▼
7. Traefik автоматически регистрирует новый сервис и
   получает SSL-сертификат от Let's Encrypt
       │
       ▼
8. https://ecogame.fullfocus.dev — сайт доступен
```

## Г.5. Параметры SSL-сертификата

| Параметр | Значение |
|----------|---------|
| Домен | ecogame.fullfocus.dev |
| Выдавший CA | Let's Encrypt (ISRG Root X1) |
| Алгоритм | ECDSA P-256 |
| Хранилище | `/traefik/acme.json` (на хосте) |
| Автообновление | Traefik renews за 30 дней до истечения |
| Challenge | HTTP-01 (через порт 80) |
