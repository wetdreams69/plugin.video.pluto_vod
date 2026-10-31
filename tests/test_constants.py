"""Tests unitarios para constants.py"""

import os
import sys

# Asegurar que el directorio raíz del addon esté en el path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from constants import (  # noqa: E402
    URL_AUTH_START,
    URL_SEARCH,
    URL_CATEGORIES,
    URL_CATEGORY_ITEMS,
    URL_SERIES_SEASONS,
    URL_EPISODES,
    URL_ON_DEMAND,
    URL_STREAM_STITCHER,
    URL_DRM_LICENSE,
    HEADERS_BASE,
    IST_HEADERS,
    AUTH_PARAMS,
    AUTH_PARAMS_START,
    SEARCH_PARAMS,
    CATEGORIES_PARAMS,
    CATEGORY_ITEMS_PARAMS,
    DEVICE_PARAMS,
    AD_MIN_DURATION,
    AD_MAX_DURATION,
    DRM_LICENSE_TYPE,
    MIME_TYPE_DASH,
    INPUTSTREAM_NAME,
    LOG_PREFIX_PLUTO,
    LOG_PREFIX_AD_SKIP,
)


def test_urls_son_validos():
    """Todas las URLs deben ser strings no vacíos y comenzar con https://."""
    urls = [
        URL_AUTH_START,
        URL_SEARCH,
        URL_CATEGORIES,
        URL_CATEGORY_ITEMS,
        URL_SERIES_SEASONS,
        URL_EPISODES,
        URL_ON_DEMAND,
        URL_STREAM_STITCHER,
        URL_DRM_LICENSE,
    ]
    for url in urls:
        assert isinstance(url, str)
        assert url.startswith("https://"), f"URL no segura: {url}"


def test_url_auth_start_tiene_formato_correcto():
    """URL_AUTH_START debe ser el endpoint de boot.pluto.tv."""
    assert URL_AUTH_START == "https://boot.pluto.tv/v4/start"


def test_url_search_tiene_formato_correcto():
    """URL_SEARCH debe ser el endpoint de búsqueda de Pluto TV."""
    assert URL_SEARCH == "https://service-media-search.clusters.pluto.tv/v1/search"


def test_url_drm_license_contiene_placeholder_token():
    """URL_DRM_LICENSE debe contener el placeholder {token}."""
    assert "{token}" in URL_DRM_LICENSE


def test_headers_base_contiene_claves_esperadas():
    """HEADERS_BASE debe incluir User-Agent, Accept, Origin y Referer."""
    assert "User-Agent" in HEADERS_BASE
    assert "Accept" in HEADERS_BASE
    assert "Origin" in HEADERS_BASE
    assert "Referer" in HEADERS_BASE


def test_auth_params_tiene_campos_requeridos():
    """AUTH_PARAMS debe incluir los campos de autenticación de Pluto TV."""
    campos = ["appName", "appVersion", "clientModelNumber", "deviceDNT",
              "deviceMake", "deviceModel", "deviceType", "deviceVersion",
              "serverSideAds"]
    for campo in campos:
        assert campo in AUTH_PARAMS


def test_auth_params_start_tiene_drm_capabilities():
    """AUTH_PARAMS_START debe incluir drmCapabilities para Widevine."""
    assert "drmCapabilities" in AUTH_PARAMS_START
    assert "widevine" in AUTH_PARAMS_START["drmCapabilities"]


def test_ad_min_menor_que_ad_max():
    """AD_MIN_DURATION debe ser menor que AD_MAX_DURATION."""
    assert AD_MIN_DURATION < AD_MAX_DURATION


def test_drm_license_type_es_widevine():
    """DRM_LICENSE_TYPE debe ser com.widevine.alpha."""
    assert DRM_LICENSE_TYPE == "com.widevine.alpha"


def test_mime_type_dash():
    """MIME_TYPE_DASH debe ser application/dash+xml."""
    assert MIME_TYPE_DASH == "application/dash+xml"


def test_inputstream_name():
    """INPUTSTREAM_NAME debe ser inputstream.adaptive."""
    assert INPUTSTREAM_NAME == "inputstream.adaptive"


def test_log_prefixes_no_vacíos():
    """Los prefijos de log no deben estar vacíos."""
    assert LOG_PREFIX_PLUTO
    assert LOG_PREFIX_AD_SKIP


def test_category_items_params_tiene_offset_y_page():
    """CATEGORY_ITEMS_PARAMS debe incluir offset y page."""
    assert "offset" in CATEGORY_ITEMS_PARAMS
    assert "page" in CATEGORY_ITEMS_PARAMS


def test_search_params_tiene_limit():
    """SEARCH_PARAMS debe incluir limit."""
    assert "limit" in SEARCH_PARAMS