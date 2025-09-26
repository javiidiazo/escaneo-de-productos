"""Utilities to parse the SFTP XML feed and persist it into the database."""

from __future__ import annotations

import io
import logging
import re
from decimal import Decimal, InvalidOperation
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Iterable

from django.db import transaction

from .models import Product

logger = logging.getLogger(__name__)

REQUIRED_FIELDS = {'barcode', 'title', 'price'}
_INVALID_XML_CHARS_RE = re.compile(r'[\x00-\x08\x0b\x0c\x0e-\x1f]')


def _extract_text(node: ET.Element, tag: str, default: str = '') -> str:
    child = node.find(tag)
    if child is None or child.text is None:
        return default
    return child.text.strip()


def _extract_attributes(node: ET.Element) -> dict:
    attributes_node = node.find('attributes')
    if attributes_node is None:
        return {}
    attributes: dict[str, str] = {}
    for child in attributes_node:
        if child.tag:
            attributes[child.tag] = (child.text or '').strip()
    return attributes


def _first_non_empty(values: Iterable[str]) -> str:
    for value in values:
        if value:
            return value
    return ''


def _collect_image(node: ET.Element) -> str:
    preferred_tags = [
        'imagen_jpg_600_1',
        'imagen_jpg_300_1',
        'imagen_jpg_150_1',
        'imagen_webp_600_1',
        'imagen_jpg_originales_1',
    ]
    for tag in preferred_tags:
        url = _extract_text(node, tag)
        if url:
            return url
    # Fallback: find the first tag that starts with "imagen" and has value
    for child in node:
        if child.tag.startswith('imagen') and child.text:
            return child.text.strip()
    return ''


def _map_xml_to_product(node: ET.Element) -> dict:
    barcode = _first_non_empty(
        (
            _extract_text(node, 'cod_ean'),
            _extract_text(node, 'codigo'),
            _extract_text(node, 'id'),
        )
    )

    price = _first_non_empty(
        (
            _extract_text(node, 'precio_web'),
            _extract_text(node, 'precio'),
            _extract_text(node, 'precio_mayorista'),
        )
    )

    attributes = {
        'linea': _extract_text(node, 'linea'),
        'rubro': _extract_text(node, 'rubro'),
        'sub_rubro': _extract_text(node, 'sub_rubro'),
        'talle': _extract_text(node, 'talle'),
        'marca': _extract_text(node, 'marca'),
        'id': _extract_text(node, 'id'),
        'codigo': _extract_text(node, 'codigo'),
        'stock': _extract_text(node, 'stock'),
    }
    # Remove empty values from attributes
    attributes = {k: v for k, v in attributes.items() if v}

    return {
        'barcode': barcode,
        'title': _extract_text(node, 'nombre'),
        'price': price,
        'currency': 'ARS',
        'image_url': _collect_image(node),
        'description': _first_non_empty(
            (
                _extract_text(node, 'descripcion_detallada'),
                _extract_text(node, 'descripcion'),
            )
        ),
        'brand': _extract_text(node, 'marca'),
        'attributes': attributes,
    }


def parse_products(xml_path: str | Path) -> Iterable[dict]:
    xml_file = Path(xml_path)
    if not xml_file.exists():
        raise FileNotFoundError(f"XML file not found: {xml_file}")

    raw_xml = xml_file.read_text(encoding='utf-8', errors='ignore')
    cleaned_xml = _INVALID_XML_CHARS_RE.sub('', raw_xml)
    tree = ET.parse(io.StringIO(cleaned_xml))
    root = tree.getroot()

    for product_node in root.findall('item'):
        product_data = _map_xml_to_product(product_node)

        if not REQUIRED_FIELDS.issubset(
            {k for k, v in product_data.items() if v}
        ):
            missing = REQUIRED_FIELDS - {
                k for k, v in product_data.items() if v
            }
            logger.warning(
                "Skipping product because of missing fields: %s", ','.join(missing)
            )
            continue

        yield product_data


def import_products(xml_path: str | Path) -> tuple[int, int]:
    created = 0
    updated = 0

    with transaction.atomic():
        for product_data in parse_products(xml_path):
            raw_price = product_data.pop('price')
            if isinstance(raw_price, str):
                raw_price = raw_price.replace(' ', '').replace(',', '.')
            try:
                price = Decimal(raw_price)
            except (InvalidOperation, TypeError) as exc:  # type: ignore[name-defined]
                logger.warning(
                    "Skipping product %s due to invalid price '%s': %s",
                    product_data.get('barcode'),
                    raw_price,
                    exc,
                )
                continue
            obj, obj_created = Product.objects.update_or_create(
                barcode=product_data['barcode'],
                defaults={
                    **product_data,
                    'price': price,
                },
            )
            if obj_created:
                created += 1
            else:
                updated += 1

    logger.info(
        "Imported products from %s (created=%s, updated=%s)",
        xml_path,
        created,
        updated,
    )
    return created, updated
