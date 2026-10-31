"""Tests unitarios para api.py"""

import json
import os
import sys
from unittest.mock import MagicMock, patch

# Asegurar que el directorio raíz del addon esté en el path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Los mocks de conftest ya están instalados en sys.modules
import api  # noqa: E402
from api import build_url, http_get, get_token  # noqa: E402


class TestBuildUrl:
    """Tests para la función build_url."""

    def test_build_url_sin_params_devuelve_url_original(self):
        """Si no hay params, se devuelve la URL tal cual."""
        url = "https://example.com/api"
        assert build_url(url) == url
        assert build_url(url, None) == url
        assert build_url(url, {}) == url

    def test_build_url_con_params_agrega_query_string(self):
        """Se deben agregar los parámetros como query string."""
        url = "https://example.com/api"
        params = {"q": "test", "limit": 50}
        result = build_url(url, params)
        assert result.startswith(url + "?")
        assert "q=test" in result
        assert "limit=50" in result

    def test_build_url_codifica_valores_especiales(self):
        """Los valores con caracteres especiales deben ser codificados."""
        url = "https://example.com/api"
        params = {"q": "película española"}
        result = build_url(url, params)
        assert "%" in result  # caracteres codificados


class TestHttpGet:
    """Tests para la función http_get."""

    @patch("api.urllib.request.urlopen")
    @patch("api.cache_manager")
    def test_http_get_retorna_datos_json(self, mock_cache_manager, mock_urlopen):
        """http_get debe parsear y retornar los datos JSON de la respuesta."""
        mock_response = MagicMock()
        mock_response.read.return_value = json.dumps({"ok": True}).encode()
        mock_urlopen.return_value.__enter__.return_value = mock_response
        mock_cache_manager.get.return_value = None

        resultado = http_get("https://example.com/api")

        assert resultado == {"ok": True}
        mock_urlopen.assert_called_once()

    @patch("api.urllib.request.urlopen")
    @patch("api.cache_manager")
    def test_http_get_usa_cuando_hay_caché(self, mock_cache_manager, mock_urlopen):
        """Si hay caché, no debe hacer la petición HTTP."""
        mock_cache_manager.get.return_value = {"cached": True}

        resultado = http_get("https://example.com/api", cache_name="test_cache")

        assert resultado == {"cached": True}
        mock_urlopen.assert_not_called()

    @patch("api.urllib.request.urlopen")
    @patch("api.cache_manager")
    def test_http_get_guarda_en_caché(self, mock_cache_manager, mock_urlopen):
        """Debe guardar en caché cuando se especifica cache_name."""
        mock_response = MagicMock()
        mock_response.read.return_value = json.dumps({"data": 123}).encode()
        mock_urlopen.return_value.__enter__.return_value = mock_response
        mock_cache_manager.get.return_value = None

        http_get("https://example.com/api", cache_name="fetch_category_data")

        mock_cache_manager.set.assert_called_once()
        # Verificar que se pasó un TTL
        args, kwargs = mock_cache_manager.set.call_args
        assert "ttl" in kwargs


class TestGetToken:
    """Tests para la función get_token."""

    @patch("api.cache_manager")
    def test_get_token_retorna_caché_si_existe(self, mock_cache_manager):
        """Si hay token en caché, debe retornarlo directamente."""
        mock_cache_manager.get.return_value = "token_caché_123"

        token = get_token()

        assert token == "token_caché_123"

    @patch("api.http_get")
    @patch("api.cache_manager")
    def test_get_token_obtiene_nuevo_si_no_hay_caché(
        self, mock_cache_manager, mock_http_get
    ):
        """Si no hay caché, debe obtener un nuevo token de la API."""
        mock_cache_manager.get.return_value = None
        mock_http_get.return_value = {"sessionToken": "nuevo_token_abc"}

        token = get_token()

        assert token == "nuevo_token_abc"
        mock_http_get.assert_called_once()
        # Verificar que se guardó en caché
        mock_cache_manager.set.assert_called_once()