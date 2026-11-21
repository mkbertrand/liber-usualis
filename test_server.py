# Copyright 2026 (AGPL-3.0-or-later), Miles K. Bertrand et al.

import re
from datetime import date, timedelta

from fastapi.testclient import TestClient

import datamanage
from server import app

client = TestClient(app, follow_redirects=False)

def test_bare_pages_redirect_to_the_preferred_locale() -> None:
    assert client.get('/').headers['location'] == '/index'
    response = client.get('/about', headers={'Accept-Language': 'de-DE,de;q=0.9'})
    assert response.status_code == 303
    assert response.headers['location'] == '/de/about'
    assert client.get('/about').headers['location'] == '/en/about'

def test_unknown_paths_are_not_found() -> None:
    for path in ['/nonexistent', '/en/nonexistent', '/xx/pray', '/en/hour/2026-10-13/prima', '/en/officium/2026-10-13/unknown-select/prima']:
        response = client.get(path)
        assert response.status_code == 404, path
        assert response.text == 'Error 404'

def test_top_level_pages_render_complete_documents() -> None:
    for path in ['/en/index', '/de/index', '/en/about', '/en/donate', '/en/resources', '/en/de-anno', '/en/kalendar', '/en/rubricae']:
        response = client.get(path)
        assert response.status_code == 200, path
        assert response.text.rstrip().endswith('</html>'), path
        assert 'id="top-bar-title"' in response.text, path

def test_more_menu_holds_feedback_theme_and_locales() -> None:
    response = client.get('/de/about')
    menu = response.text[response.text.index('<div id="more-menu-container">'):response.text.index('<script>', response.text.index('<div id="more-menu-container">'))]
    assert 'aria-label="Mehr"' in menu
    assert 'href="mailto:admin@liberusualis.org">Feedback geben</a>' in menu
    assert 'id="dark-mode-toggle"' in menu and 'Dunkles Design: ' in menu and '>An</span>' in menu and '>Aus</span>' in menu
    assert 'href="/en/about"' in menu and 'href="/la/about"' in menu
    assert 'data-locale="de" aria-current="true">Deutsch</a>' in menu
    assert 'id="locale-selector-button"' in menu and 'Sprache: Deutsch</button>' in menu
    rite_text = client.get(f'/en/officium/{date.today()}/prima').text
    assert f'href="/la/officium/{date.today()}/prima"' in rite_text
    for path in ['/en/index', f'/en/officium/{date.today()}/prima']:
        text = client.get(path).text
        assert text.count('id="dark-mode-toggle"') == 1, path
        assert 'site-footer' not in text, path

def test_only_the_pray_page_collapses_the_top_bar_itself() -> None:
    shared_script = "bar.classList.contains('top-bar-menu-open') || !moreMenu.hidden"
    assert shared_script in client.get('/en/about').text
    assert shared_script not in client.get(f'/en/officium/{date.today()}/prima').text

def test_rite_near_today_is_server_rendered() -> None:
    response = client.get(f'/en/officium/{date.today()}/prima')
    assert response.status_code == 200
    assert 'data-server-rendered="true"' in response.text
    assert 'class="large-title"' in response.text
    assert 'noindex' not in response.text

def test_rite_far_from_today_is_left_to_the_client() -> None:
    for rite_date in [date.today() + timedelta(days=800), date(9999, 12, 31)]:
        response = client.get(f'/en/officium/{rite_date}/prima')
        assert response.status_code == 200, rite_date
        assert 'data-server-rendered="false"' in response.text
        assert '<meta name="robots" content="noindex, nofollow">' in response.text

def test_sitemap_index_lists_only_server_rendered_dates() -> None:
    response = client.get('/sitemap.xml')
    assert response.status_code == 200
    assert response.headers['content-type'] == 'application/xml'
    assert '<sitemapindex ' in response.text
    locs = re.findall(r'<loc>([^<]*)</loc>', response.text)
    assert len(locs) < 50000
    assert 'https://breviary.cc/sitemaps/en.xml' in locs
    sitemap_dates = {date.fromisoformat(m) for m in re.findall(r'/sitemaps/en/(\d{4}-\d{2}-\d{2})\.xml', response.text)}
    assert sitemap_dates == set(datamanage.server_rendered_dates(date.today()))

def test_locale_sitemap_lists_top_level_pages() -> None:
    response = client.get('/sitemaps/de.xml')
    assert response.status_code == 200
    assert '<loc>https://breviary.cc/de/about</loc>' in response.text
    assert '/en/' not in response.text
    assert client.get('/sitemaps/xx.xml').status_code == 404

def test_dated_sitemap_lists_the_hours_of_that_day() -> None:
    response = client.get(f'/sitemaps/la/{date.today()}.xml')
    assert response.status_code == 200
    locs = re.findall(r'<loc>([^<]*)</loc>', response.text)
    assert len(locs) == 7
    assert f'https://breviary.cc/la/officium/{date.today()}/completorium' in locs

def test_dated_sitemap_outside_the_range_is_not_found() -> None:
    for path in [f'/sitemaps/en/{date.today() + timedelta(days=800)}.xml', '/sitemaps/en/garbage.xml', f'/sitemaps/xx/{date.today()}.xml']:
        assert client.get(path).status_code == 404, path

def test_robots_points_to_the_sitemap() -> None:
    assert 'Sitemap: https://breviary.cc/sitemap.xml' in client.get('/robots.txt').text

def test_favicon_is_served() -> None:
    response = client.get('/favicon.ico')
    assert response.status_code == 200
    assert response.headers['content-type'] == 'image/x-icon'

def test_rite_api_failure_returns_the_error_page() -> None:
    response = client.get('/api/rite', params={'loc': 'en', 'date': 'garbage', 's': 'primarium', 'occasion': 'prima+officium', 'v': ''})
    assert response.status_code == 500
    assert 'Error incognitus.' in response.text

def test_json_endpoints_are_served_as_json() -> None:
    response = client.get('/api/ordo', params={'date': str(date.today()), 'time': '12:00', 'votives': ''})
    assert response.status_code == 200
    assert response.headers['content-type'] == 'application/json'
    assert 'tags' in response.json()

def test_head_requests_answer_like_get() -> None:
    for path in ['/', '/robots.txt', '/en/about', '/api/ordo?date=2026-10-30&time=diurnale', '/en/nonexistent']:
        head = client.head(path)
        get = client.get(path)
        assert head.status_code == get.status_code, path
        assert head.content == b'', path

def test_pages_link_their_canonical_address() -> None:
    for path, canonical in [
        ('/en/about', 'https://breviary.cc/en/about'),
        ('/en/ordo', 'https://breviary.cc/en/ordo'),
        ('/en/index', 'https://breviary.cc/en/index'),
        ('/en/pray', 'https://breviary.cc/en/pray'),
        ('/en/officium/2026-10-30/vesperae?v=de-joseph', 'https://breviary.cc/en/officium/2026-10-30/vesperae?v=de-joseph'),
        ('/la/officium/2026-11-2/officium-defunctorum/vesperae', 'https://breviary.cc/la/officium/2026-11-02/officium-defunctorum/vesperae'),
    ]:
        response = client.get(path)
        assert response.status_code == 200, path
        assert f'<link rel="canonical" href="{canonical}">' in response.text, path
        assert '"url":"https://breviary.cc/"' in response.text, path

def test_rite_pages_are_not_stored() -> None:
    # Browsers reuse stored pages on Back/Forward, but the rite depends on the opt cookie, not only on the address
    response = client.get(f'/en/officium/{date.today()}/vesperae', cookies={'opt': 'sine-ritibus'})
    assert response.status_code == 200
    assert response.headers['cache-control'] == 'no-store'
