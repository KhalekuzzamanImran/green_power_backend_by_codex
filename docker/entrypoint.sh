#!/bin/sh
set -eu

echo "Checking migrations..."

max_tries=30
try=1
while [ "$try" -le "$max_tries" ]; do
    if python manage.py showmigrations --plan | grep -q '\[ \]'; then
        if python manage.py migrate --noinput; then
            break
        fi
        echo "Migrate failed (attempt $try/$max_tries); retrying in 2s..."
        try=$((try + 1))
        sleep 2
    else
        echo "No pending migrations."
        break
    fi
done

if [ "$try" -gt "$max_tries" ]; then
    echo "Migrate failed after $max_tries attempts."
    exit 1
fi

echo "Ensuring Mongo indexes..."
python manage.py ensure_mongo_indexes

python manage.py collectstatic --noinput

exec gunicorn config.asgi:application --bind 0.0.0.0:8000 --workers 3 --threads 4 --timeout 60 -k uvicorn.workers.UvicornWorker
