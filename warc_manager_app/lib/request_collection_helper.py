# File: warc_manager_app/lib/helper.py
import logging

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


def render_alert(message: str, status: int = 200, include_info_link: bool = True) -> HttpResponse:
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


def get_collection_data(collection_id):
    """
    Gets the initial collection data overview for the given collection.
    Dummy implementation for now.
    Called by views.hlpr_check_coll_id().
    """
    log.debug(f'getting data for collection ID: {collection_id}')
    url = f'{settings.WASAPI_URL_ROOT}/collections/{collection_id}'
    auth: httpx.BasicAuth = httpx.BasicAuth(username='finley', password=settings.WASAPI_KEY)
    client: httpx.Client = httpx.Client(auth=auth)
    resp: httpx.Response = client.get(url)
    log.debug(f'resp = ``{resp}``')
    log.debug(f'resp.content = ``{resp.content}``')
    log.debug('hereZZ')

    return {'name': 'Test Collection', 'total_size': '1.2 GB', 'item_count': 1000}


def render_download_confirmation_form(api_data: dict, collection_id: str, csrf_token: str | None) -> str:
    """
    Preps html for the download confirmation form.
    This is triggered by a previous htmx POST request that gets overview collection data
    Called by views.hlpr_check_coll_id().
    """
    html_content = f"""
    <div>
        Number of items: {api_data["item_count"]}, Total size of all items: {api_data["total_size"]}
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
