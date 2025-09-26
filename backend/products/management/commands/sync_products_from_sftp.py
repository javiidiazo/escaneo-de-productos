from __future__ import annotations

import logging
from pathlib import Path

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError

from ...sftp_client import build_client_from_env
from ...xml_loader import import_products

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = "Download the product feed via SFTP and update the local database."

    def add_arguments(self, parser):  # type: ignore[override]
        parser.add_argument(
            '--remote-path',
            default=settings.PRODUCT_FEED_REMOTE_PATH,
            help='Remote path to the XML feed on the SFTP server.',
        )
        parser.add_argument(
            '--local-path',
            default=settings.PRODUCT_FEED_LOCAL_PATH,
            help='Local path where the XML file will be stored.',
        )
        parser.add_argument(
            '--skip-download',
            action='store_true',
            help='Skip SFTP download and just import the existing XML file.',
        )

    def handle(self, *args, **options):  # type: ignore[override]
        local_path = Path(options['local_path'])
        remote_path = options['remote_path']
        skip_download = options['skip_download']

        if not skip_download:
            try:
                client = build_client_from_env()
            except KeyError as exc:
                raise CommandError(
                    f"Missing SFTP credential environment variable: {exc}"  # noqa: TRY003
                ) from exc

            client.download(remote_path=remote_path, destination=local_path)

        created, updated = import_products(local_path)
        self.stdout.write(
            self.style.SUCCESS(
                f"Sync completed. Created: {created}, Updated: {updated}."
            )
        )

        if skip_download:
            logger.info('sync_products_from_sftp executed without download step')

        # Explicitly return None so Django's command runner doesn't try to
        # treat (created, updated) as a printable tuple.
