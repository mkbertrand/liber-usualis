#!/usr/bin/env python3

# Copyright 2025-2026 (AGPL-3.0-or-later), Miles K. Bertrand et al.

import argparse
import json
import os
import traceback
import warnings
from datetime import date, datetime, timedelta
from typing import Any

import uvicorn
from fastapi import Cookie, FastAPI, Header, HTTPException, Request
from fastapi.exception_handlers import http_exception_handler
from fastapi.responses import FileResponse, HTMLResponse, RedirectResponse, Response
from fastapi.staticfiles import StaticFiles
from jinja2 import Environment, FileSystemLoader
from starlette.exceptions import HTTPException as StarletteHTTPException

import datamanage
from composer import util

import version_management

TOP_LEVEL_PAGES = [
    'index',
    'de-anno',
    'kalendar',
    'rubricae',
    'pray',
    'about',
    'donate',
    'resources'
]
PRAYER_TYPES = ['officium', 'ritus']
SELECT = ['officium-parvum-bmv', 'officium-defunctorum']
MOBILE_USER_AGENT_KEYWORDS = ['mobile', 'android', 'iphone', 'ipad']

CURSUS_OCCASIONS = ['matutinum-laudes', 'prima', 'tertia', 'sexta', 'nona', 'vesperae', 'completorium']
RITE_TITLES = {'matutinum-laudes': 'Matutinum \N{AMPERSAND} Laudes', 'prima': 'Prima', 'tertia': 'Tertia', 'sexta': 'Sexta', 'nona': 'Nona', 'vesperae': 'Vesperæ', 'completorium': 'Completorium', 'psalmi-graduales': 'Psalmi Graduales', 'psalmi-poenitentiales': 'Psalmi Pœnitentiales', 'ordo-commendationis-animae': 'Ordo Commendationis Animæ', 'formula-indulgentiam-articulo-mortis': 'Formula ad Impertiendam Indulgentiam Plenariam in Articulo Mortis', 'pro-prandio': 'Benedictio Mensæ (Pro Prandio)', 'pro-coena': 'Benedictio Mensæ (Pro Cœna)', 'itinerarium': 'Itinerarium Clericorum'}
# The hours as linked from the pray page, labelled as HTML
CURSUS_LINKS = [('matutinum-laudes', 'Matutinum &amp; Laudes'), ('prima', 'Prima'), ('tertia', 'Tertia'), ('sexta', 'Sexta'), ('nona', 'Nona'), ('vesperae', 'Vesperæ'), ('completorium', 'Completorium')]
PRAY_SCRIPT_TEXT_KEYS = ['banner-remain-here', 'suboptimal-content-banner-message', 'suboptimal-content-banner-go', 'outdated-content-banner-message', 'outdated-content-banner-go']

templates = Environment(loader=FileSystemLoader('.'), autoescape=True, trim_blocks=True, lstrip_blocks=True, keep_trailing_newline=True)
templates.globals['versioned_resource'] = version_management.get_versioned_resource
templates.globals['DEFINED_LOCALES'] = version_management.DEFINED_LOCALES

app = FastAPI(docs_url=None, redoc_url=None, openapi_url=None)
app.mount('/resources', StaticFiles(directory='web/resources'), name='resources')

def load_json(path: str) -> Any:
    with open(path, encoding='utf-8') as f:
        return json.load(f)

def request_locales(preferred_locale: str | None, accept_language: str | None) -> list[str]:
    locales = [preferred_locale] if preferred_locale else []
    try:
        locales.extend(version_management.localehunt(accept_language))
    except Exception:
        # A missing or malformed Accept-Language header leaves only the preferred locale and English
        pass
    if not 'en' in locales:
        locales.append('en')
    return locales

def page_title(page: str, locales: list[str]) -> str:
    titles = {}
    for locale in locales:
        if os.path.exists(f'web/locales/{locale}/resources/page-titles.json'):
            titles = load_json(f'web/locales/{locale}/resources/page-titles.json')
    return titles.get(page, '')

def is_mobile(user_agent: str) -> bool:
    return any(k in user_agent.lower() for k in MOBILE_USER_AGENT_KEYWORDS)

def shell_context(page: str, locales: list[str]) -> dict[str, Any]:
    locale = locales[0]
    return {
        'page': page,
        'locale': locale,
        'title': page_title(page, locales),
        'top_bar_text': load_json(f'web/locales/{locale}/resources/top-bar.json'),
    }

def page_context(page: str, locales: list[str]) -> tuple[str, dict[str, Any]]:
    if page == 'index':
        return 'web/templates/menu.jinja', {
            'body_template': 'web/pages/index.jinja',
            'text': load_json(version_management.bestlocalized(f'/pages/{page}.json', locales)),
        }
    elif page in ['de-anno', 'kalendar', 'rubricae']:
        if os.path.exists(f'web/pages/{page}.html'):
            return 'web/templates/latin-generic.jinja', {'body_template': f'web/pages/{page}.html'}
        return 'web/templates/latin-generic.jinja', {
            'body_template': f'web/pages/{page}.jinja',
            'text': load_json(version_management.bestlocalized(f'/pages/{page}.json', locales)),
        }
    else:
        return 'web/templates/generic.jinja', {
            'body_template': version_management.bestlocalized(f'/pages/{page}.html', locales),
            'page_stylesheet': f'/styles/{page}.css' if os.path.exists(f'web/resources/styles/{page}.css') else None,
        }

def next_hour(pdate: date, prayer_type: str, select: str, occasion: str) -> tuple[date, str, str]:
    if prayer_type == 'officium' and select != 'officium-defunctorum' and occasion in CURSUS_OCCASIONS:
        cursus_index = CURSUS_OCCASIONS.index(occasion)
        if cursus_index == len(CURSUS_OCCASIONS) - 1:
            return pdate + timedelta(days=1), CURSUS_OCCASIONS[0], select
        return pdate, CURSUS_OCCASIONS[cursus_index + 1], select
    return pdate, CURSUS_OCCASIONS[0], 'primarium'

def pray_context(locale: str, locales: list[str], rite_date: str | None, prayer_type: str | None, occasion: str | None, options: str, select: str, translation: str, votives: str, server_rendered: bool, today: date) -> dict[str, Any]:
    text = load_json(version_management.bestlocalized('/pages/pray.json', locales))
    rite = ''
    next_hour_href = None
    next_hour_occasion_name = ''
    day_title = ''
    rite_title_for_head = ''
    if rite_date is None:
        # Bare /<locale>/pray: no rite was chosen, so none is composed here; the page's script picks one based on the
        # reader's local time and soft-navigates there
        pdate = today
        rite_date = str(pdate)
        occasion = 'matutinum-laudes'
        prayer_type = 'officium'
        select = 'primarium'
        votives = ''
        next_hour_href = '#'
    elif not server_rendered:
        # Too far from today to compose here (see datamanage.is_server_rendered); the page's script loads the rite and
        # sets the title and the next-day links, which are left out so link-following crawlers go no further
        pdate = datetime.strptime(rite_date, '%Y-%m-%d').date()
    else:
        pdate = datetime.strptime(rite_date, '%Y-%m-%d').date()
        rite = datamanage.rendered_rite_request(rite_date, occasion + '+' + prayer_type, options, select, translation, votives)
        # The page's script likewise takes the day title from the rendered rite rather than calling /api/ordo; this is
        # cheap since the rite request is memoized
        day_title = datamanage.rite_request(rite_date, occasion + '+' + prayer_type, options, select, translation, votives)['used-primary'][0]
        rite_title_for_head = RITE_TITLES.get(occasion, occasion)
        next_hour_date, next_hour_occasion, next_hour_select = next_hour(pdate, prayer_type, select, occasion)
        next_hour_occasion_name = RITE_TITLES[next_hour_occasion]
        next_hour_href = f"/{locale}/officium/{next_hour_date}{'' if next_hour_select == 'primarium' else f'/{next_hour_select}'}/{next_hour_occasion}{'' if len(votives) == 0 else f'?v={votives}'}"
    return {
        'text': text,
        'date': rite_date,
        'pdate': pdate,
        # Only links within the server-rendered range lead on to the next day, and computing it at the end of the
        # calendar would overflow
        'next_day': pdate + timedelta(days=1) if server_rendered else None,
        'occasion': occasion,
        'select': select,
        'server_rendered': server_rendered,
        'rite': rite,
        'day_title': day_title,
        'rite_title_for_head': rite_title_for_head,
        'current_rite_title': RITE_TITLES.get(occasion, occasion),
        'next_hour_href': next_hour_href,
        'next_hour_occasion_name': next_hour_occasion_name,
        'hour_select': '/officium-parvum-bmv' if select == 'officium-parvum-bmv' else '',
        'hour_votives': '' if len(votives) == 0 else f'?v={votives}',
        'script_text': {key: text[key] for key in PRAY_SCRIPT_TEXT_KEYS},
        'CURSUS_LINKS': CURSUS_LINKS,
    }

def render(template_name: str, **context: Any) -> HTMLResponse:
    return HTMLResponse(templates.get_template(template_name).render(**context))

def error_page(error: str) -> HTMLResponse:
    return HTMLResponse(templates.get_template('web/resources/error500.jinja').render(error=error), status_code=500)

def translation_for_locale(locale: str) -> str:
    match locale:
        case 'en':
            return 'english'
        case 'de':
            return 'deutsch'
        case 'nl':
            return 'nederlands'
        case _:
            return 'none'

@app.exception_handler(StarletteHTTPException)
async def http_error(request: Request, exc: StarletteHTTPException) -> Response:
    if exc.status_code == 404:
        return HTMLResponse('Error 404', status_code=404)
    return await http_exception_handler(request, exc)

@app.get('/robots.txt')
def robots() -> FileResponse:
    return FileResponse('web/resources/robots.txt', media_type='text/plain')

@app.get('/')
def index() -> RedirectResponse:
    return RedirectResponse('/index', status_code=303)

@app.get('/api/ordo')
def ordo(date: str | None = None, time: str | None = None, votives: str = '') -> Response:
    return Response(util.dump_data(datamanage.ordo(date, time, votives)), media_type='application/json')

# Returns raw JSON so that frontend can format it as it will
@app.get('/api/composer')
def composer(date: str | None = None, rite: str | None = None, opt: str = '', select: str = 'primarium', translation: str = 'none', votives: str = '') -> Response:
    try:
        return Response(util.dump_data(datamanage.rite_request(date, rite, opt, select, translation, votives)), media_type='application/json')
    except Exception:
        traceback.print_exc()
        return error_page('Error incognitus.')

@app.get('/api/rite')
def rite(date: str | None = None, occasion: str | None = None, loc: str = 'none', s: str = 'primarium', v: str = '', opt: str = Cookie('')) -> HTMLResponse:
    try:
        return HTMLResponse(datamanage.rendered_rite_request(date, occasion, opt, s, translation_for_locale(loc), v))
    except Exception:
        traceback.print_exc()
        return error_page('Error incognitus.')

@app.get('/api/kalendar')
def kal() -> Response:
    with warnings.catch_warnings():
        warnings.simplefilter('ignore')
        return Response(datamanage.getdisplaykalendar(datamanage.DEFAULT_CORPUS), media_type='application/json')

@app.get('/{page}')
def bounce_to_locale(page: str, accept_language: str | None = Header(None)) -> RedirectResponse:
    if page not in TOP_LEVEL_PAGES:
        raise HTTPException(status_code=404)
    locales = request_locales(None, accept_language)
    return RedirectResponse(f'/{[loc for loc in locales if loc in version_management.DEFINED_LOCALES][0]}/{page}', status_code=303)

@app.get('/{preferred_locale}/{page}')
def local_page(preferred_locale: str, page: str, accept_language: str | None = Header(None), user_agent: str = Header('')) -> HTMLResponse:
    if preferred_locale not in version_management.DEFINED_LOCALES or page not in TOP_LEVEL_PAGES:
        raise HTTPException(status_code=404)
    locales = request_locales(preferred_locale, accept_language)
    if page == 'pray':
        return render('web/templates/pray.jinja', **shell_context(page, locales), mobile=is_mobile(user_agent),
                      **pray_context(locales[0], locales, None, None, None, '', 'primarium', 'none', '', True, date.today()))
    template_name, context = page_context(page, locales)
    return render(template_name, **shell_context(page, locales), **context)

@app.get('/{preferred_locale}/{prayer_type}/{rite_date}/{occasion}')
def pray(preferred_locale: str, prayer_type: str, rite_date: str, occasion: str, v: str = '', opt: str = Cookie(''), accept_language: str | None = Header(None), user_agent: str = Header('')) -> HTMLResponse:
    return pray_page(preferred_locale, prayer_type, rite_date, 'primarium', occasion, v, opt, accept_language, user_agent)

@app.get('/{preferred_locale}/{prayer_type}/{rite_date}/{select}/{occasion}')
def pray_select(preferred_locale: str, prayer_type: str, rite_date: str, select: str, occasion: str, v: str = '', opt: str = Cookie(''), accept_language: str | None = Header(None), user_agent: str = Header('')) -> HTMLResponse:
    if select not in SELECT:
        raise HTTPException(status_code=404)
    return pray_page(preferred_locale, prayer_type, rite_date, select, occasion, v, opt, accept_language, user_agent)

def pray_page(preferred_locale: str, prayer_type: str, rite_date: str, select: str, occasion: str, votives: str, options: str, accept_language: str | None, user_agent: str) -> HTMLResponse:
    if preferred_locale not in version_management.DEFINED_LOCALES or prayer_type not in PRAYER_TYPES:
        raise HTTPException(status_code=404)
    locales = request_locales(preferred_locale, accept_language)
    today = date.today()
    server_rendered = datamanage.is_server_rendered(datetime.strptime(rite_date, '%Y-%m-%d').date(), today)
    return render('web/templates/pray.jinja', **shell_context('pray', locales), mobile=is_mobile(user_agent),
                  **pray_context(locales[0], locales, rite_date, prayer_type, occasion, options, select, translation_for_locale(locales[0]), votives, server_rendered, today))

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Server')
    parser.add_argument('-a', '--addr', default='127.0.0.1', help='Set host address')
    parser.add_argument('-p', '--port', type=int, default=8080, help='Set port')
    args = parser.parse_args()
    uvicorn.run(app, host=args.addr, port=args.port)
