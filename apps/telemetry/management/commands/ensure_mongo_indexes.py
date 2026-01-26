from __future__ import annotations

import logging

from django.conf import settings
from django.core.management.base import BaseCommand

from common.mongo import get_mongo_database

logger = logging.getLogger(__name__)


def _ensure_index(collection, keys, name, **options) -> None:
    info = collection.index_information().get(name)
    desired_key = [(k, v) for k, v in keys]

    if info:
        current_key = info.get("key")
        current_ttl = info.get("expireAfterSeconds")
        desired_ttl = options.get("expireAfterSeconds")
        if current_key == desired_key and current_ttl == desired_ttl:
            return
        try:
            collection.drop_index(name)
        except Exception as exc:  # pragma: no cover - defensive
            logger.warning("Failed dropping index %s on %s: %s", name, collection.name, exc)
    try:
        collection.create_index(keys, name=name, **options)
    except Exception as exc:  # pragma: no cover - defensive
        logger.warning("Failed creating index %s on %s: %s", name, collection.name, exc)


def _ensure_timestamp_search(collection) -> None:
    _ensure_index(collection, [("timestamp", 1)], "timestamp_search")


def _ensure_timestamp_ttl(collection, ttl_seconds: int) -> None:
    if ttl_seconds <= 0:
        return
    _ensure_index(collection, [("timestamp", 1)], "timestamp_ttl", expireAfterSeconds=ttl_seconds)


class Command(BaseCommand):
    help = "Ensure MongoDB indexes for telemetry collections."

    def handle(self, *args, **options):
        if not getattr(settings, "MONGO_DB_URI", None):
            self.stdout.write(self.style.WARNING("MONGO_DB_URI not configured; skipping."))
            return

        db = get_mongo_database()

        base_collections = [
            "grid_rt_data",
            "grid_eny_now_data",
            "grid_day_data",
            "grid_eny_frz_data",
            "environment_data",
            "generator_data",
            "solar_data",
            "today_solar_data",
            "current_month_solar_data",
        ]

        for name in base_collections:
            _ensure_timestamp_search(db[name])

        # TTL collections (timestamp + expireAfterSeconds)
        ttl_today = getattr(settings, "MONGO_TODAY_TTL_SECONDS", 86400)
        ttl_7_days = getattr(settings, "MONGO_LAST_7_DAYS_TTL_SECONDS", 604800)
        ttl_30_days = getattr(settings, "MONGO_LAST_30_DAYS_TTL_SECONDS", 2592000)
        ttl_6_months = getattr(settings, "MONGO_LAST_6_MONTHS_TTL_SECONDS", 15552000)
        ttl_this_year = getattr(settings, "MONGO_THIS_YEAR_TTL_SECONDS", 31536000)

        today_collections = [
            "today_grid_rt_data",
            "today_grid_eny_now_data",
            "today_environment_data",
        ]
        last_7_days_collections = [
            "last_7_days_grid_rt_data",
            "last_7_days_environment_data",
            "last_7_days_grid_eny_now_data",
        ]
        last_30_days_collections = [
            "last_30_days_grid_rt_data",
            "last_30_days_environment_data",
            "last_30_days_grid_eny_now_data",
        ]
        last_6_months_collections = [
            "last_6_months_grid_rt_data",
            "last_6_months_environment_data",
            "last_6_months_grid_eny_now_data",
        ]
        this_year_collections = [
            "this_year_grid_rt_data",
            "this_year_environment_data",
            "this_year_grid_eny_now_data",
        ]

        for name in today_collections:
            _ensure_timestamp_ttl(db[name], ttl_today)
        for name in last_7_days_collections:
            _ensure_timestamp_ttl(db[name], ttl_7_days)
        for name in last_30_days_collections:
            _ensure_timestamp_ttl(db[name], ttl_30_days)
        for name in last_6_months_collections:
            _ensure_timestamp_ttl(db[name], ttl_6_months)
        for name in this_year_collections:
            _ensure_timestamp_ttl(db[name], ttl_this_year)

        # telemetry_events indexes
        telemetry = db["telemetry_events"]
        _ensure_timestamp_search(telemetry)
        _ensure_index(telemetry, [("timestamp", 1), ("topic", 1)], "timestamp_topic_search")

        self.stdout.write(self.style.SUCCESS("Mongo indexes ensured."))
