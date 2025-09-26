"""Celery tasks for periodic synchronisation of the product feed."""

from __future__ import annotations

import logging
from pathlib import Path

from django.conf import settings

from . import xml_loader

logger = logging.getLogger(__name__)


def sync_products_from_feed(xml_path: str | Path | None = None) -> tuple[int, int]:
    feed_path = Path(xml_path or settings.PRODUCT_FEED_LOCAL_PATH)
    logger.info("Syncing products from %s", feed_path)
    return xml_loader.import_products(feed_path)


try:
    from celery import shared_task
except ImportError:  # pragma: no cover - Celery optional
    shared_task = None


if shared_task:

    @shared_task
    def sync_products_from_feed_task() -> tuple[int, int]:
        return sync_products_from_feed()
