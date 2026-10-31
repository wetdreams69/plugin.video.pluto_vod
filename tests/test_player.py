"""Tests unitarios para player.py"""

import os
import sys
from unittest.mock import MagicMock, patch

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import xbmc
import xbmcgui
import xbmcplugin
import xbmcaddon

from player import play  # noqa: E402


class TestPlay:
    """Tests para la función play."""

    @patch("player.get_token")
    @patch("player.http_get")
    def test_play_obtiene_stream_url_y_resuelve(self, mock_http_get, mock_get_token):
        """play debe obtener el stream URL y llamar setResolvedUrl."""
        mock_get_token.return_value = "token_falso"

        # Mock de la respuesta del endpoint de episodios
        mock_http_get.return_value = {
            "stitched": {
                "paths": [
                    {"type": "mpd", "path": "/stitch/dash/episode/123/main.mpd"},
                    {"type": "hls", "path": "/stitch/hls/episode/123/master.m3u8"},
                ]
            }
        }

        with patch("player.xbmcaddon.Addon") as mock_addon_class, \
             patch("player.xbmcplugin.setResolvedUrl") as mock_resolve, \
             patch("player.xbmcgui.ListItem") as mock_li:
            mock_addon = MagicMock()
            mock_addon.getSettingBool.return_value = False
            mock_addon_class.return_value = mock_addon
            mock_li_instance = MagicMock()
            mock_li.return_value = mock_li_instance

            play(1, "content_id_123", {})

            # Verificar que se construyó y resolvió la URL
            mock_resolve.assert_called_once()
            args = mock_resolve.call_args[0]
            assert args[0] == 1  # addon_handle
            assert args[1] is True  # success

    @patch("player.get_token")
    @patch("player.http_get")
    def test_play_habilita_ad_skipper_si_configurado(self, mock_http_get, mock_get_token):
        """Si ads_skipper está habilitado, debe iniciar el ad skipper."""
        mock_get_token.return_value = "token_falso"

        mock_http_get.return_value = {
            "stitched": {
                "paths": [
                    {"type": "mpd", "path": "/stitch/dash/episode/123/main.mpd"},
                ]
            }
        }

        ad_skipper_data = {}

        with patch("player.xbmcaddon.Addon") as mock_addon_class, \
             patch("player.xbmcplugin.setResolvedUrl"), \
             patch("player.xbmcgui.ListItem") as mock_li, \
             patch("player.start_ad_skipper") as mock_ad_skipper:
            mock_addon = MagicMock()
            mock_addon.getSettingBool.return_value = True
            mock_addon_class.return_value = mock_addon
            mock_li.return_value = MagicMock()
            mock_ad_skipper.return_value = (MagicMock(), MagicMock())

            play(1, "content_id_123", ad_skipper_data)

            mock_ad_skipper.assert_called_once()
            assert "skipper" in ad_skipper_data
            assert "thread" in ad_skipper_data

    @patch("player.get_token")
    @patch("player.http_get")
    def test_play_no_dash_path_lanza_error(self, mock_http_get, mock_get_token):
        """Si no hay path DASH, debe lanzar ValueError."""
        mock_get_token.return_value = "token_falso"
        mock_http_get.return_value = {"stitched": {"paths": []}}

        with patch("player.xbmcaddon.Addon") as mock_addon_class, \
             patch("player.xbmcgui.Dialog") as mock_dialog, \
             patch("player.xbmcplugin.setResolvedUrl") as mock_resolve:
            mock_addon = MagicMock()
            mock_addon.getSettingBool.return_value = False
            mock_addon_class.return_value = mock_addon

            play(1, "content_id_123", {})

            # Debe llamar setResolvedUrl con False (fallo)
            mock_resolve.assert_called_with(1, False, xbmcgui.ListItem())
            mock_dialog.return_value.ok.assert_called_once()

    @patch("player.get_token")
    @patch("player.http_get")
    def test_play_incluye_headers_inputstream(self, mock_http_get, mock_get_token):
        """El ListItem debe incluir headers de inputstream.adaptive."""
        mock_get_token.return_value = "token_falso"

        mock_http_get.return_value = {
            "stitched": {
                "paths": [
                    {"type": "mpd", "path": "/stitch/dash/episode/123/main.mpd"},
                ]
            }
        }

        with patch("player.xbmcaddon.Addon") as mock_addon_class, \
             patch("player.xbmcplugin.setResolvedUrl"), \
             patch("player.xbmcgui.ListItem") as mock_li:
            mock_addon = MagicMock()
            mock_addon.getSettingBool.return_value = False
            mock_addon_class.return_value = mock_addon
            mock_li_instance = MagicMock()
            mock_li.return_value = mock_li_instance

            play(1, "content_id_123", {})

            # Verificar que se configuraron las propiedades de inputstream
            mock_li_instance.setProperty.assert_any_call(
                "inputstream", "inputstream.adaptive"
            )
            mock_li_instance.setProperty.assert_any_call(
                "inputstream.adaptive.license_type", "com.widevine.alpha"
            )
            mock_li_instance.setProperty.assert_any_call("IsPlayable", "true")