#!/bin/bash
# Production deployment script for ecogame.fullfocus.dev
# Run on server after cloning the repo

set -e

echo "=== EcoGame Deploy Script ==="

# Apply migrations
echo "Running migrations..."
docker compose exec backend uv run python manage.py migrate --settings=config.settings.prod

# Load fixtures (run once)
echo "Loading fixtures..."
docker compose exec backend uv run python manage.py loaddata \
  fixtures/levels.json \
  fixtures/quiz_achievements.json \
  fixtures/educational_content.json \
  fixtures/eco_facts.json \
  fixtures/questions.json \
  --settings=config.settings.prod

echo "=== Deploy complete! ==="
echo "Visit: https://ecogame.fullfocus.dev"
