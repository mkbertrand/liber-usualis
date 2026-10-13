# Copyright 2026 (AGPL-3.0-or-later), Miles K. Bertrand et al.

from datetime import date, timedelta

from fastapi.testclient import TestClient

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

def test_rite_api_failure_returns_the_error_page() -> None:
    response = client.get('/api/rite', params={'loc': 'en', 'date': 'garbage', 's': 'primarium', 'occasion': 'prima+officium', 'v': ''})
    assert response.status_code == 500
    assert 'Error incognitus.' in response.text

def test_json_endpoints_are_served_as_json() -> None:
    response = client.get('/api/ordo', params={'date': str(date.today()), 'time': '12:00', 'votives': ''})
    assert response.status_code == 200
    assert response.headers['content-type'] == 'application/json'
    assert 'tags' in response.json()
