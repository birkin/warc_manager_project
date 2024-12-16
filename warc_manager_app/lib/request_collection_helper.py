import logging
import pprint
from typing import List, Optional

import httpx
from django.conf import settings
from django.http import HttpResponse

from warc_manager_app import models

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

    ## end def get_recent_collections()


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
    collection_data_prepper = CollectionDataPrepper(collection_id)
    initial_collection_data: dict | None = collection_data_prepper.grab_initial_collection_data()
    if initial_collection_data:
        collection_data_prepper.get_rest_of_files(initial_collection_data)
        overview_data = collection_data_prepper.build_overview_dict()
    else:
        overview_data = None
    log.debug(f'overview_data, ``{overview_data}``')
    return overview_data


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
    <form id="confirm_download" hx-post="/hlpr_initiate_download/" hx-target="#response" hx-swap="innerHTML">
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


def start_download(collection_id: str):
    log.debug(f'Starting download for collection ID: {collection_id}')
    ## dummy implementation
    return


class CollectionDataPrepper:
    """
    Class to prepare collection data for a given collection ID.
    - Makes the initial API call for the given collection-id.
    - Inspects the response and makes multiple subsequent "next" calls if necessary.
    - Builds an overview dict with the total size and number of items.
    Called by get_collection_data().
    """

    def __init__(self, collection_id: str):
        self.url = f'{settings.WASAPI_URL_ROOT}?collection={collection_id}'
        log.debug(f'url = ``{self.url}``')
        self.auth: httpx.BasicAuth = httpx.BasicAuth(username=settings.WASAPI_USR, password=settings.WASAPI_KEY)
        self.client: httpx.Client = httpx.Client(auth=self.auth)
        self.all_files: List[str] = []

    def grab_initial_collection_data(self) -> dict | None:
        """
        Makes the initial request to the collection data API.
        Called by get_collection_data().
        """
        resp: httpx.Response = self.client.get(self.url)
        elapsed_time: float = resp.elapsed.total_seconds()
        log.debug(f'elapsed_time, ``{elapsed_time}`` seconds')
        if resp.status_code == 200:
            log.debug('200 status, so evaluating json')
            data: dict = resp.json()
            if data.get('count', 0) < 1:  # eg, collection-id `19111` returns a 200, but a count of zero
                log.debug(f'data for empty-count response, ``{pprint.pformat(data)}``')
                data = None
            else:
                log.debug(f'data.keys(), ``{pprint.pformat(data.keys())}``')
        else:
            log.debug('non-200 status, so setting overview_data to None')
            data = None
        return data

    def get_rest_of_files(self, data: dict) -> dict:
        """
        Makes as many "next" API-calls as necessary.
        Called by get_collection_data().
        """
        log.debug('starting parse_collection_data()')
        log.debug(f'data (first 1.5K chars), ``{pprint.pformat(data)[:1500]}``')
        ## store existing files -----------------------------------------
        self.all_files.extend(data.get('files', []))
        log.debug(f'number of files initially, ``{len(self.all_files)}``')
        ## loop through the remaining pages using "next" links ----------
        next_url: Optional[str] = data.get('next')
        while next_url:
            response = self.client.get(next_url)
            if response.status_code != 200:
                raise RuntimeError(f'Failed to fetch data from ``{next_url}``: ``{response.status_code}``')
            current_data = response.json()
            self.all_files.extend(current_data.get('files', []))
            next_url = current_data.get('next')
        return

    # def build_overview_dict(self) -> dict:
    #     """
    #     Builds the overview dict.
    #     Called by get_collection_data().
    #     Note -- this is where I need to do the save.
    #     """
    #     file_count: int = len(self.all_files)
    #     log.debug(f'file_count, ``{file_count}``')
    #     log.debug(f'First 5 files: {pprint.pformat(self.all_files[:5])}')
    #     total_size_in_bytes: int = sum([file['size'] for file in self.all_files])
    #     total_size_gb: float = total_size_in_bytes / (1024**3)
    #     data = {'total_size': f'{total_size_gb:.2f} GB', 'item_count': file_count}
    #     return data

    def build_overview_dict(self) -> dict:
        """
        Builds the overview dict.
        Called by get_collection_data().
        Note -- this is where I need to do the save.
        """
        file_count: int = len(self.all_files)
        log.debug(f'file_count, ``{file_count}``')
        log.debug(f'First 3 files: {pprint.pformat(self.all_files[:3])}')

        ## save query ---------------------------------------
        try:
            collection = models.Collection.objects.create(
                arc_collection_id=collection_id,
                item_count=collection_overview_api_data['item_count'],
                size_in_bytes=collection_overview_api_data['size_in_bytes'],
                status='queried',
                all_files=collection_overview_api_data['all_files'],
            )
            collection.save()
        except Exception:
            log.exception('error on collection save,')

        total_size_in_bytes: int = sum([file['size'] for file in self.all_files])
        total_size_gb: float = total_size_in_bytes / (1024**3)
        data = {'total_size': f'{total_size_gb:.2f} GB', 'item_count': file_count}
        return data

    ## end class CollectionDataPrepper
