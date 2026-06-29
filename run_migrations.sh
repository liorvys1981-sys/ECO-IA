#!/usr/bin/env bash
# ECO-IA — Run database migrations
set -euo pipefail

ECO_IA_DIR="${ECO_IA_DIR:-/opt/eco-ia}"
echo "🗄️  Running ECO-IA database migrations..."

cd "$ECO_IA_DIR"
docker exec eco-ia-postgres psql -U eco_ia -d eco_ia -c "\l" > /dev/null 2>&1 || {
    echo "❌ PostgreSQL not running. Start with: systemctl start eco-ia"
    exit 1
}

if [[ -f ".venv/bin/alembic" ]]; then
    .venv/bin/alembic -c database/alembic.ini upgrade head
else
    docker exec eco-ia-api alembic -c database/alembic.ini upgrade head
fi
echo "✅ Migrations complete"
