"""Tests unitarios para search.py"""

import os
import sys
from unittest.mock import MagicMock, patch

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import xbmc
import xbmcgui
import xbmcplugin

from search import (  # noqa: E402
    get_art,
    set_info,
    search,
    list_series,
    list_episodes,
    list_categories,
    list_category_items,
)


class TestGetArt:
    """Tests para la función get_art."""

    def test_get_art_con_item_none_retorna_diccionario_vacío(self):
        assert get_art(None) == {}

    def test_get_art_con_item_vacío_retorna_diccionario_vacío(self):
        assert get_art({}) == {}

    def test_get_art_extrae_featured_image_como_fanart(self):
        item = {"featuredImage": {"path": "https://example.com/fanart.jpg"}}
        art = get_art(item)
        assert art.get("fanart") == "https://example.com/fanart.jpg"

    def test_get_art_extrae_covers_347_500_como_poster(self):
        item = {
            "covers": [
                {"aspectRatio": "16:9", "url": "https://example.com/landscape.jpg"},
                {"aspectRatio": "347:500", "url": "https://example.com/poster.jpg"},
            ]
        }
        art = get_art(item)
        assert art.get("poster") == "https://example.com/poster.jpg"

    def test_get_art_extrae_covers_16_9_como_landscape(self):
        item = {
            "covers": [
                {"aspectRatio": "347:500", "url": "https://example.com/poster.jpg"},
                {"aspectRatio": "16:9", "url": "https://example.com/landscape.jpg"},
            ]
        }
        art = get_art(item)
        assert art.get("landscape") == "https://example.com/landscape.jpg"

    def test_get_art_thumb_se_asigna_del_poster_si_no_existe(self):
        item = {"covers": [{"aspectRatio": "347:500", "url": "https://example.com/poster.jpg"}]}
        art = get_art(item)
        assert art.get("thumb") == "https://example.com/poster.jpg"

    def test_get_art_icon_se_asigna_del_thumb(self):
        item = {"covers": [{"aspectRatio": "16:9", "url": "https://example.com/thumb.jpg"}]}
        art = get_art(item)
        assert art.get("icon") == "https://example.com/thumb.jpg"

    def test_get_art_covers_no_diccionarios_se_ignorán(self):
        item = {"covers": ["no_es_un_diccionario", {"aspectRatio": "347:500", "url": "https://example.com/poster.jpg"}]}
        art = get_art(item)

class TestSetInfo:
    """Tests para la función set_info."""

    def test_set_info_con_item_none_no_hace_nada(self):
        li = MagicMock()
        set_info(li, None)
        li.setInfo.assert_not_called()

    def test_set_info_establece_título_y_plot(self):
        li = MagicMock()
        item = {"name": "Película Test", "description": "Una descripción de prueba"}
        set_info(li, item)
        info = li.setInfo.call_args[0][1]
        assert info["title"] == "Película Test"
        assert info["plot"] == "Una descripción de prueba"

    def test_set_info_establece_género(self):
        li = MagicMock()
        item = {"name": "Test", "genre": "Acción"}
        set_info(li, item)
        info = li.setInfo.call_args[0][1]
        assert info["genre"] == "Acción"

    def test_set_info_establece_elenco_y_director(self):
        li = MagicMock()
        item = {
            "name": "Test",
            "clip": {"actors": ["Actor 1", "Actor 2"], "directors": ["Director 1"]},
        }
        set_info(li, item)
        info = li.setInfo.call_args[0][1]
        assert info["cast"] == ["Actor 1", "Actor 2"]
        assert info["director"] == "Director 1"

    def test_set_info_establece_año_desde_original_release_date(self):
        li = MagicMock()
        item = {"name": "Test", "clip": {"originalReleaseDate": "2023-05-15T00:00:00Z"}}
        set_info(li, item)
        info = li.setInfo.call_args[0][1]
        assert info["year"] == 2023
        assert info["premiered"] == "2023-05-15"

    def test_set_info_establece_mediatype_por_tipo(self):
        li = MagicMock()
        for tipo, mediatype_esperado in [
            ("movie", "movie"),
            ("series", "tvshow"),
            ("episode", "episode"),
        ]:
            item = {"name": "Test", "type": tipo}
            set_info(li, item)
            info = li.setInfo.call_args[0][1]
            assert info["mediatype"] == mediatype_esperado

    def test_set_info_establece_temporada_y_episodio(self):
        li = MagicMock()
        item = {"name": "Test", "type": "episode", "season": 2, "number": 5}
        set_info(li, item)
        info = li.setInfo.call_args[0][1]
        assert info["season"] == 2
        assert info["episode"] == 5

    def test_set_info_establece_duración_en_segundos(self):
        li = MagicMock()
        item = {"name": "Test", "type": "episode", "duration": 7200000}
        set_info(li, item)
        info = li.setInfo.call_args[0][1]
        assert info["duration"] == 7200

    def test_set_info_establece_mpaa_desde_rating(self):
        li = MagicMock()
        item = {"name": "Test", "rating": "PG-13"}
        set_info(li, item)
        info = li.setInfo.call_args[0][1]
        assert info["mpaa"] == "PG-13"

class TestSearch:
    """Tests para la función search."""

    @patch("search.get_token")
    def test_search_retorna_resultados_de_películas_y_series(self, mock_get_token):
        mock_get_token.return_value = "token_falso"

        with patch("search.http_get") as mock_http_get:
            mock_http_get.return_value = {
                "data": [
                    {"type": "movie", "name": "Película 1", "_id": "id1", "covers": []},
                    {"type": "series", "name": "Serie 1", "_id": "id2", "covers": []},
                    {"type": "channel", "name": "Canal 1", "_id": "id3", "covers": []},
                ]
            }

            with patch("search.xbmcplugin.addDirectoryItem") as mock_add_item, \
                 patch("search.xbmcplugin.endOfDirectory") as mock_end:
                search(1, "test")

                assert mock_add_item.call_count == 2
                mock_end.assert_called_once_with(1)

    @patch("search.get_token")
    def test_search_no_hace_nada_si_no_hay_resultados(self, mock_get_token):
        mock_get_token.return_value = "token_falso"

        with patch("search.http_get") as mock_http_get:
            mock_http_get.return_value = {"data": []}

            with patch("search.xbmcplugin.addDirectoryItem") as mock_add_item, \
                 patch("search.xbmcplugin.endOfDirectory") as mock_end:
                search(1, "test")
                mock_add_item.assert_not_called()
                mock_end.assert_called_once_with(1)

class TestListSeries:
    """Tests para la función list_series."""

    @patch("search.get_token")
    def test_list_series_retorna_temporadas(self, mock_get_token):
        mock_get_token.return_value = "token_falso"

        with patch("search.http_get") as mock_http_get:
            mock_http_get.return_value = {
                "seasons": [
                    {"number": 1, "episodes": []},
                    {"number": 2, "episodes": []},
                ]
            }

            with patch("search.xbmcgui.ListItem") as mock_li, \
                 patch("search.xbmcplugin.addDirectoryItem") as mock_add, \
                 patch("search.xbmcplugin.endOfDirectory") as mock_end:
                list_series(1, "content_id_123")

                assert mock_li.call_count == 2
                assert mock_add.call_count == 2
                mock_end.assert_called_once_with(1)

    @patch("search.get_token")
    def test_list_series_fallback_a_play_si_falla(self, mock_get_token):
        mock_get_token.return_value = "token_falso"

        with patch("search.http_get") as mock_http_get:
            mock_http_get.side_effect = Exception("Error de red")

            with patch("player.play") as mock_play:
                list_series(1, "content_id_123")
                mock_play.assert_called_once_with(1, "content_id_123", {})

class TestListEpisodes:
    """Tests para la función list_episodes."""

    @patch("search.get_token")
    def test_list_episodes_retorna_episodios_de_temporada(self, mock_get_token):
        mock_get_token.return_value = "token_falso"

        with patch("search.http_get") as mock_http_get:
            mock_http_get.return_value = {
                "seasons": [
                    {
                        "number": 1,
                        "episodes": [
                            {"_id": "ep1", "name": "Episodio 1"},
                            {"_id": "ep2", "name": "Episodio 2"},
                        ],
                    }
                ]
            }

            with patch("search.xbmcgui.ListItem") as mock_li, \
                 patch("search.xbmcplugin.addDirectoryItem") as mock_add, \
                 patch("search.xbmcplugin.endOfDirectory") as mock_end:
                list_episodes(1, "content_id_123", "1")

                assert mock_li.call_count == 2
                assert mock_add.call_count == 2
                mock_end.assert_called_once_with(1)

class TestListCategories:
    """Tests para la función list_categories."""

    @patch("search.get_token")
    def test_list_categories_retorna_categorías(self, mock_get_token):
        mock_get_token.return_value = "token_falso"

        with patch("search.http_get") as mock_http_get:
            mock_http_get.return_value = {
                "categories": [
                    {"name": "Cine", "_id": "cat1"},
                    {"name": "Series", "_id": "cat2"},
                ]
            }

            with patch("search.xbmcgui.ListItem") as mock_li, \
                 patch("search.xbmcplugin.addDirectoryItem") as mock_add, \
                 patch("search.xbmcplugin.endOfDirectory") as mock_end:
                list_categories(1)

                assert mock_li.call_count == 2
                assert mock_add.call_count == 2
                mock_end.assert_called_once_with(1)

    @patch("search.get_token")
    def test_list_categories_ignora_categorías_sin_nombre_o_id(self, mock_get_token):
        mock_get_token.return_value = "token_falso"

        with patch("search.http_get") as mock_http_get:
            mock_http_get.return_value = {
                "categories": [
                    {"name": "Cine", "_id": "cat1"},
                    {"name": None, "_id": "cat2"},
                    {"name": "Series", "_id": None},
                ]
            }

            with patch("search.xbmcgui.ListItem") as mock_li, \
                 patch("search.xbmcplugin.addDirectoryItem") as mock_add, \
                 patch("search.xbmcplugin.endOfDirectory") as mock_end:
                list_categories(1)

                assert mock_li.call_count == 1
                assert mock_add.call_count == 1
                mock_end.assert_called_once_with(1)

class TestListCategoryItems:
    """Tests para la función list_category_items."""

    @patch("search.get_token")
    def test_list_category_items_retorna_películas_y_series(self, mock_get_token):
        mock_get_token.return_value = "token_falso"

        with patch("search.http_get") as mock_http_get:
            mock_http_get.return_value = {
                "items": [
                    {
                        "_id": "movie1",
                        "name": "Película 1",
                        "type": "movie",
                        "covers": [],
                    },
                    {
                        "_id": "serie1",
                        "name": "Serie 1",
                        "type": "series",
                        "covers": [],
                    },
                ]
            }

            with patch("search.xbmcgui.ListItem") as mock_li, \
                 patch("search.xbmcplugin.addDirectoryItem") as mock_add, \
                 patch("search.xbmcplugin.endOfDirectory") as mock_end:
                list_category_items(1, "cat_id")

                assert mock_li.call_count == 2
                assert mock_add.call_count == 2
                mock_end.assert_called_once_with(1)