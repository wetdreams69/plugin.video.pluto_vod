import sys
import xbmc
import xbmcgui
import xbmcplugin

from api import get_token, HEADERS_BASE, http_get
from constants import (
    URL_SEARCH,
    URL_SERIES_SEASONS,
    SEARCH_PARAMS,
    DEVICE_PARAMS,
    LOG_PREFIX_PLUTO,
)


def search(query):
    token = get_token()
    headers = HEADERS_BASE.copy()
    headers["Authorization"] = f"Bearer {token}"
    data = http_get(URL_SEARCH, headers, {**SEARCH_PARAMS, "q": query})
    xbmc.log(f"{LOG_PREFIX_PLUTO} Search OK", xbmc.LOGINFO)
    return [x for x in data.get("data", []) if x.get("type") in ["movie", "series"]]


def list_series(addon_handle, content_id):
    token = get_token()
    headers = HEADERS_BASE.copy()
    headers["Authorization"] = f"Bearer {token}"
    try:
        xbmc.log(f"{LOG_PREFIX_PLUTO} Getting seasons", xbmc.LOGINFO)
        data = http_get(
            URL_SERIES_SEASONS.format(content_id=content_id),
            headers,
            DEVICE_PARAMS,
        )
        for season in data.get("seasons", []):
            num = season.get("number")
            li = xbmcgui.ListItem(label=f"Season {num}")
            url = f"{sys.argv[0]}?action=episodes&id={content_id}&season={num}"
            xbmcplugin.addDirectoryItem(addon_handle, url, li, True)
        xbmcplugin.endOfDirectory(addon_handle)
        return
    except Exception as e:
        xbmc.log(f"{LOG_PREFIX_PLUTO} Seasons failed: {e}", xbmc.LOGWARNING)
    xbmc.log(f"{LOG_PREFIX_PLUTO} Fallback → play directo", xbmc.LOGINFO)
    from player import play
    play(addon_handle, content_id, {})


def list_episodes(addon_handle, content_id, season):
    token = get_token()
    headers = HEADERS_BASE.copy()
    headers["Authorization"] = f"Bearer {token}"
    data = http_get(
        URL_SERIES_SEASONS.format(content_id=content_id),
        headers,
        DEVICE_PARAMS,
    )
    for s in data.get("seasons", []):
        if str(s.get("number")) == season:
            for ep in s.get("episodes", []):
                title = ep.get("name", "Episode")
                ep_id = ep.get("_id")
                li = xbmcgui.ListItem(label=title)
                url = f"{sys.argv[0]}?action=play&id={ep_id}"
                xbmcplugin.addDirectoryItem(addon_handle, url, li, False)
    xbmcplugin.endOfDirectory(addon_handle)
