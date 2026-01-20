#!/bin/sh
set -eu

echo "Running migrations..."
python manage.py makemigrations

max_tries=30
try=1
while [ "$try" -le "$max_tries" ]; do
    if python manage.py migrate --noinput; then
        break
    fi
    echo "Migrate failed (attempt $try/$max_tries); retrying in 2s..."
    try=$((try + 1))
    sleep 2
done

if [ "$try" -gt "$max_tries" ]; then
    echo "Migrate failed after $max_tries attempts."
    exit 1
fi

python manage.py collectstatic --noinput

exec gunicorn config.wsgi:application --bind 0.0.0.0:8000 --workers 3 --threads 4 --timeout 60
