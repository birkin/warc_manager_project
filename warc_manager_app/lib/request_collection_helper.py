# File: warc_manager_app/lib/helper.py
import logging
import pprint
from typing import Any, Dict, List, Optional

import httpx
from django.conf import settings
from django.http import HttpResponse

log = logging.getLogger(__name__)


def get_recent_collections() -> list:
    """
    Shows the recent collections.
    Dummy implementation for now.
    Called by views.request_collection().
    """
    log.debug('Showing recent collections')
    dummy_data = [
        {
            'date': '2024-09-01',
            'collection_id': 1,
            'title': 'Test Collection 1',
            'number_of_items': 25,
            'total_size': '100 MB',
            'status': 'complete',
        },
        {
            'date': '2024-09-02',
            'collection_id': 2,
            'title': 'Test Collection 2',
            'number_of_items': 50,
            'total_size': '200 MB',
            'status': 'in-progress',
        },
        {
            'date': '2024-09-03',
            'collection_id': 3,
            'title': 'Test Collection 3',
            'number_of_items': 75,
            'total_size': '150 MB',
            'status': 'complete',
        },
        {
            'date': '2024-09-04',
            'collection_id': 4,
            'title': 'Test Collection 4',
            'number_of_items': 100,
            'total_size': '2.1 GB',
            'status': 'in-progress',
        },
        {
            'date': '2024-09-01',
            'collection_id': 5,
            'title': 'Test Collection 5',
            'number_of_items': 125,
            'total_size': '300 MB',
            'status': 'complete',
        },
    ]
    ## sort dict by date descending
    dummy_data.sort(key=lambda x: x['date'], reverse=True)
    return dummy_data


def render_alert(
    message: str,
    include_info_link: bool = True,
    status: int = 200,
) -> HttpResponse:
    """
    Returns an alert message with optional info link.
    Called by htmx-post-handlers in views.hlpr_check_coll_id() and views.hlpr_initiate_download().
    """
    info_link = ' <a href="/info/">More info</a>' if include_info_link else ''
    html_content = f'<div class="alert">{message} {info_link}</div>'
    return HttpResponse(html_content, status=status)


def check_collection_status(collection_id):
    """
    Checks if the collection is already downloaded or in progress.
    Dummy implementation for now.
    Called by views.hlpr_check_coll_id().
    """
    log.debug(f'Checking status for collection ID: {collection_id}')
    return {'exists': False}  # Return True if exists or in progress


def handle_status(status: dict) -> HttpResponse | None:
    """
    Handles the status of the collection, determined in check_collection_statu().
    Called by views.hlpr_check_coll_id().
    """
    STATUS_MESSAGES: dict[str, str] = {
        'in_progress': 'Download in progress',
        'completed': 'Download completed',
    }
    status_key = status.get('exists')
    if status_key in STATUS_MESSAGES:
        log.debug(f'status is {status_key}')
        return render_alert(STATUS_MESSAGES[status_key])
    elif not status_key:
        log.debug('status does not exist; will fetch collection data')
        return None
    else:
        return render_alert('Unknown error occurred', status=500)


def get_collection_data(collection_id) -> dict | None:
    """
    Gets the initial collection data overview for the given collection.
    Dummy implementation for now.
    Called by views.hlpr_check_coll_id().
    """
    log.debug(f'getting data for collection ID: {collection_id}')
    url = f'{settings.WASAPI_URL_ROOT}?collection={collection_id}'
    log.debug(f'url = ``{url}``')
    auth: httpx.BasicAuth = httpx.BasicAuth(username=settings.WASAPI_USR, password=settings.WASAPI_KEY)
    client: httpx.Client = httpx.Client(auth=auth)
    resp: httpx.Response = client.get(url)
    # log.debug(f'resp.content, ``{resp.content}``')
    log.debug(f'resp = ``{resp}``')
    elapsed_time: float = resp.elapsed.total_seconds()
    log.debug(f'elapsed_time, ``{elapsed_time}`` seconds')
    log.debug(f'type(elapsed_time), ``{type(elapsed_time)}``')
    # log.debug(f'resp.__dict__ = ``{pprint.pformat(resp.__dict__)}``')
    # log.debug(f'resp.content = ``{resp.content}``')
    log.debug('hereZZ')
    if resp.status_code == 200:
        log.debug('200 status, so evaluating json')
        json_data: dict = resp.json()
        if json_data.get('count', 0) < 1:
            log.debug(f'json_data for empty-count response, ``{pprint.pformat(json_data)}``')
            log.debug('no data found')
            overview_data = None
        else:
            log.debug('data found')
            # overview_data: dict = parse_collection_data(resp)
            overview_data: dict = parse_collection_data(resp, client)
    else:
        log.debug('non-200 status, so setting overview_data to None')
        overview_data = None
    return overview_data


def parse_collection_data(resp: httpx.Response, client: httpx.Client) -> dict:
    """
    Parses collection-data api response.
    Called by get_collection_data().
    """
    log.debug('starting parse_collection_data()')
    data: dict = resp.json()
    log.debug(f'data (first 1.5K chars), ``{pprint.pformat(data)[:1500]}``')
    log.debug(f'data.keys(), ``{data.keys()}``')
    log.debug(f'data.keys(), ``{pprint.pformat(data.keys())}``')
    ## set up files holder ------------------------------------------
    all_files: List[str] = []
    current_data: Dict[str, Any] = data
    ## store existing files -----------------------------------------
    all_files.extend(current_data.get('files', []))
    log.debug(f'number of files initially, ``{len(all_files)}``')
    ## loop through the remaining pages using "next" links ----------
    next_url: Optional[str] = data.get('next')
    while next_url:
        response = client.get(next_url)
        if response.status_code != 200:
            raise RuntimeError(f'Failed to fetch data from ``{next_url}``: ``{response.status_code}``')
        current_data = response.json()
        all_files.extend(current_data.get('files', []))
        next_url = current_data.get('next')
    ## go through the files and get the total size ------------------
    file_count: int = len(all_files)
    log.debug(f'file_count, ``{file_count}``')
    log.debug(f'First 5 files: {all_files[:5]}')
    total_size_in_bytes: int = sum([file['size'] for file in all_files])
    total_size_gb: float = total_size_in_bytes / (1024**3)
    data = {'total_size': f'{total_size_gb:.2f} GB', 'item_count': file_count}
    return data


def render_download_confirmation_form(api_data: dict, collection_id: str, csrf_token: str | None) -> str:
    """
    Preps html for the download confirmation form.
    This is triggered by a previous htmx POST request that gets overview collection data
    Called by views.hlpr_check_coll_id().
    """
    html_content = f"""
    <div>
        Number of items: {api_data["item_count"]}, Total size of all items: {api_data['total_size']}
    </div>
    <form hx-post="/hlpr_initiate_download/" hx-target="#response" hx-swap="innerHTML">
        <input type="hidden" name="csrfmiddlewaretoken" value="{csrf_token}">
        <input type="hidden" name="coll_id" value="{collection_id}">
        <input type="hidden" name="action" value="really_start_download">
        <button
            class="btn">
            Confirm start download
        </button>
    </form>
    """
    return html_content


# def render_download_confirmation_form(api_data: dict, collection_id: str, csrf_token: str | None) -> HttpResponse:
#     """
#     Preps html for the download confirmation form.
#     This is triggered by a previous htmx POST request that gets overview collection data
#     Called by views.hlpr_check_coll_id().
#     """
#     html_content = f"""
#     <div>
#         Number of items: {api_data["item_count"]}, Total size of all items: {api_data["total_size"]}
#     </div>
#     <form hx-post="/hlpr_initiate_download/" hx-target="#response" hx-swap="innerHTML">
#         <input type="hidden" name="csrfmiddlewaretoken" value="{csrf_token}">
#         <input type="hidden" name="coll_id" value="{collection_id}">
#         <input type="hidden" name="action" value="really_start_download">
#         <button
#             class="btn">
#             Confirm start download
#         </button>
#     </form>
#     """
#     return HttpResponse(html_content)


def start_download(collection_id: str):
    log.debug(f'Starting download for collection ID: {collection_id}')
    # Dummy implementation
    return
