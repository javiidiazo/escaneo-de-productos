"""Small helper around Paramiko to download the product feed via SFTP."""

from __future__ import annotations

import logging
import os
from pathlib import Path
from typing import Optional

import paramiko

logger = logging.getLogger(__name__)


class ProductFeedSFTPClient:
    def __init__(
        self,
        host: str,
        username: str,
        port: int = 22,
        password: Optional[str] = None,
        key_path: Optional[str] = None,
    ) -> None:
        self.host = host
        self.username = username
        self.port = port
        self.password = password
        self.key_path = key_path

    def _get_private_key(self) -> Optional[paramiko.PKey]:
        if not self.key_path:
            return None
        key_file = Path(self.key_path).expanduser()
        if not key_file.exists():
            raise FileNotFoundError(f"SFTP key not found: {key_file}")
        return paramiko.RSAKey.from_private_key_file(str(key_file))

    def download(self, remote_path: str, destination: str | Path) -> Path:
        destination_path = Path(destination)
        destination_path.parent.mkdir(parents=True, exist_ok=True)
        tmp_path = destination_path.with_suffix('.tmp')

        logger.info(
            "Downloading SFTP file from %s:%s to %s",
            self.host,
            remote_path,
            tmp_path,
        )

        transport = paramiko.Transport((self.host, self.port))
        try:
            private_key = self._get_private_key()
            if private_key:
                transport.connect(username=self.username, pkey=private_key)
            else:
                transport.connect(username=self.username, password=self.password)

            with paramiko.SFTPClient.from_transport(transport) as sftp:
                sftp.get(remote_path, str(tmp_path))

            tmp_path.replace(destination_path)
        finally:
            transport.close()

        logger.info("SFTP download completed: %s", destination_path)
        return destination_path


def build_client_from_env() -> ProductFeedSFTPClient:
    return ProductFeedSFTPClient(
        host=os.environ['SFTP_HOST'],
        username=os.environ['SFTP_USER'],
        port=int(os.environ.get('SFTP_PORT', '22')),
        password=os.environ.get('SFTP_PASSWORD'),
        key_path=os.environ.get('SFTP_KEY_PATH'),
    )


def download_xml(
    *,
    remote_path: str | None = None,
    destination: str | Path | None = None,
) -> Path:
    """Download the XML feed using environment variables.

    Allows overriding remote path or destination for ad-hoc downloads while
    keeping environment-driven configuration as defaults.
    """

    client = build_client_from_env()
    feed_remote_path = remote_path or os.environ['SFTP_REMOTE_PATH']
    feed_destination = destination or os.environ.get('XML_LOCAL_PATH')

    if not feed_destination:
        raise ValueError(
            'XML_LOCAL_PATH must be set when calling download_xml without destination.'
        )

    return client.download(feed_remote_path, feed_destination)
