# File: warc_manager_app/lib/helper.py
import logging

from django.http import HttpRequest, HttpResponse
from django.shortcuts import render

log = logging.getLogger(__name__)


## GET request handler & helper -------------------------------------


def handle_get_request(request: HttpRequest) -> HttpResponse:
    log.debug('handling GET request')
    recents: list = get_recent_collections()
    context = {'recent_items': recents}
    return render(request, 'request_collection.html', context)


def get_recent_collections() -> list:
    """
    Shows the recent collections.
    Dummy implementation for now.
    """
    log.debug('Showing recent collections')
    # Dummy response
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
    # sort dict by date descending
    dummy_data.sort(key=lambda x: x['date'], reverse=True)
    return dummy_data


## POST request handler & helpers -----------------------------------


def handle_post_request(request: HttpRequest) -> HttpResponse:
    """
    POST manager.
    Called by views.request_collection()
    Flow...
    - check for collection_id; return alert if missing
    - check collection status; return alert if in progress or completed
    - get collection overview data; return alert if not found; return download confirmation form if found
    - check for confirm start download; start download if confirmed
    """
    ## check collection id ------------------------------------------
    # collection_id: str = request.POST.get('collection_id', '').strip()
    # if not collection_id:
    #     log.debug('no collection_id')
    #     return render_alert('Collection ID is required.', include_info_link=False)
    ## check collection status --------------------------------------
    # status: dict = check_collection_status(collection_id)
    # log.debug(f'status: {status}')
    # resp: HttpResponse | None = handle_status(status)
    # log.debug(f'collection status resp: {resp}')
    # if resp:  # in-progress or completed
    #     return resp
    ## get collection overview data ---------------------------------
    collection_overview_api_data: dict | None = get_collection_data(collection_id)
    log.debug(f'api_data: {collection_overview_api_data}')
    if collection_overview_api_data:
        csrf_token: str | None = request.COOKIES.get('csrftoken')
        return render_download_confirmation_form(collection_overview_api_data, collection_id, csrf_token)
    else:
        return render_alert('No collection data found.', status=404, include_info_link=False)
    ## check for confirm start download -----------------------------
    if request.POST.get('action') == 'really_start_download':
        start_download(collection_id)
        return render_alert('Download started')

    ## end def handle_post_request()


def render_alert(message: str, status: int = 200, include_info_link: bool = True) -> HttpResponse:
    """Returns an alert message with optional info link.
    Called by handle_post_request() in a variety of situations."""
    info_link = ' <a href="/info/">More info</a>' if include_info_link else ''
    return HttpResponse(f'<div class="alert">{message}{info_link}</div>', status=status)


def check_collection_status(collection_id):
    """
    Checks if the collection is already downloaded or in progress.
    Dummy implementation for now.
    """
    log.debug(f'Checking status for collection ID: {collection_id}')
    # Dummy response
    return {'exists': False}  # Return True if exists or in progress


def handle_status(status: dict) -> HttpResponse | None:
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
    Gets the collection data for the given collection.
    Dummy implementation for now.
    """
    log.debug(f'Getting data for collection ID: {collection_id}')
    # Dummy response
    return {'name': 'Test Collection', 'total_size': '1.2 GB', 'item_count': 1000}


def render_download_confirmation_form(api_data: dict, collection_id: str, csrf_token: str | None) -> HttpResponse:
    html_content = f"""
    <div>
        Number of items: {api_data["item_count"]}, Total size of all items: {api_data["total_size"]}
    </div>
    <form hx-post="/request_collection/" hx-target="#response" hx-swap="innerHTML">
        <input type="hidden" name="csrfmiddlewaretoken" value="{csrf_token}">
        <input type="hidden" name="action" value="really_start_download">
        <button
            hx-post="/request_collection/"
            hx-vals='{{"collection_id": "{collection_id}"}}'
            class="btn">
            Confirm start download
        </button>
    </form>
    """
    return HttpResponse(html_content)


def start_download(collection_id: str):
    log.debug(f'Starting download for collection ID: {collection_id}')
    # Dummy implementation
    return
