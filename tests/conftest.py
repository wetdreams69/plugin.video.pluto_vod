"""Configuración de pytest con mocks para módulos de Kodi y dependencias externas."""

import sys
import types
from unittest.mock import MagicMock, PropertyMock


def _mock_xbmc():
    """Crea un mock del módulo xbmc."""
    xbmc = MagicMock()
    xbmc.LOGDEBUG = 0
    xbmc.LOGINFO = 1
    xbmc.LOGERROR = 2
    xbmc.LOGWARNING = 3
    xbmc.log = MagicMock()
    return xbmc


def _mock_xbmcgui():
    """Crea un mock del módulo xbmcgui."""
    xbmcgui = MagicMock()
    dialog = MagicMock()
    dialog.input = MagicMock(return_value=None)
    dialog.ok = MagicMock()
    xbmcgui.Dialog = MagicMock(return_value=dialog)

    list_item = MagicMock()
    list_item.setArt = MagicMock()
    list_item.setInfo = MagicMock()
    list_item.setProperty = MagicMock()
    list_item.path = None
    xbmcgui.ListItem = MagicMock(return_value=list_item)
    return xbmcgui


def _mock_xbmcplugin():
    """Crea un mock del módulo xbmcplugin."""
    xbmcplugin = MagicMock()
    xbmcplugin.addDirectoryItem = MagicMock()
    xbmcplugin.setResolvedUrl = MagicMock()
    xbmcplugin.endOfDirectory = MagicMock()
    return xbmcplugin


def _mock_xbmcaddon():
    """Crea un mock del módulo xbmcaddon."""
    xbmcaddon = MagicMock()
    addon = MagicMock()
    addon.getSettingBool = MagicMock(return_value=False)
    type(addon).getSettingBool = PropertyMock(return_value=False)
    xbmcaddon.Addon = MagicMock(return_value=addon)
    return xbmcaddon


def _mock_cacheman():
    """Crea un mock del módulo cacheman."""
    cacheman = MagicMock()
    cache_manager = MagicMock()
    cache_manager.get = MagicMock(return_value=None)
    cache_manager.set = MagicMock()
    cacheman.CacheManager = MagicMock(return_value=cache_manager)
    return cacheman, cache_manager


def _mock_adskipper():
    """Crea un mock del módulo adskipper."""
    adskipper = MagicMock()
    adskipper.start_ad_skipper = MagicMock(return_value=(MagicMock(), MagicMock()))
    return adskipper


# --- Instalar mocks en sys.modules ANTES de importar los módulos del addon ---

sys.modules["xbmc"] = _mock_xbmc()
sys.modules["xbmcgui"] = _mock_xbmcgui()
sys.modules["xbmcplugin"] = _mock_xbmcplugin()
sys.modules["xbmcaddon"] = _mock_xbmcaddon()

_mock_cacheman, _mock_cache_manager = _mock_cacheman()
sys.modules["cacheman"] = _mock_cacheman

sys.modules["adskipper"] = _mock_adskipper()