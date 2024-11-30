import datetime
import json
import logging

import trio
from django.conf import settings as project_settings
from django.http import HttpRequest, HttpResponse, HttpResponseNotFound, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse

from warc_manager_app.lib import request_collection_helper, version_helper
from warc_manager_app.lib.version_helper import GatherCommitAndBranchData

log = logging.getLogger(__name__)


# -------------------------------------------------------------------
# main urls
# -------------------------------------------------------------------


def info(request):
    """
    The "about" view.
    Can get here from 'info' url, and the root-url redirects here.
    """
    log.debug('starting info()')
    ## prep data ----------------------------------------------------
    context = {
        'quote': 'The best life is the one in which the creative impulses play the largest part and the possessive impulses the smallest.',
        'author': 'Bertrand Russell',
    }
    ## prep response ------------------------------------------------
    if request.GET.get('format', '') == 'json':
        log.debug('building json response')
        resp = HttpResponse(
            json.dumps(context, sort_keys=True, indent=2),
            content_type='application/json; charset=utf-8',
        )
    else:
        log.debug('building template response')
        resp = render(request, 'info.html', context)
    return resp


def request_collection(request: HttpRequest) -> HttpResponse:
    """
    Displays main page for requesting collection downloads.
    """
    log.debug('starting request_collection()')
    if request.method == 'GET':
        log.debug('handling GET request')
        recents: list = request_collection_helper.get_recent_collections()
        context = {'recent_items': recents}
        return render(request, 'request_collection.html', context)
    else:
        ## htmx POSTs are handled by the helper functions below
        resp = HttpResponse(status=405)  # Method Not Allowed
    return resp


def hlpr_check_coll_id(request: HttpRequest) -> HttpResponse:
    """
    Handles request_collection() htmx check-id POST of the submitted collection-id.
    - If collection-id is missing, an alert is returned.
    - If the collection is in-progress or completed, an alert is returned.
    - If the collection is not in-progress or completed, the download-confirmation form is returned.
    """
    log.debug('starting hlpr_check_coll_id()')
    ## check collection id ------------------------------------------
    collection_id: str = request.POST.get('collection_id', '').strip()
    if not collection_id:
        log.debug('no collection_id')
        return request_collection_helper.render_alert('Collection ID is required.', include_info_link=False)
    else:
        ## check for in-progress or completed -----------------------
        status: dict = request_collection_helper.check_collection_status(collection_id)
        log.debug(f'status: {status}')
        resp: HttpResponse | None = request_collection_helper.handle_status(status)
        log.debug(f'collection status resp: {resp}')
        if resp:  # in-progress or completed
            return resp
        else:
            ## get collection overview data --------------------------
            collection_overview_api_data: dict | None = request_collection_helper.get_collection_data(collection_id)
            log.debug(f'api_data: {collection_overview_api_data}')
            if collection_overview_api_data:
                log.debug('collection data found, so rending download confirmation form')
                csrf_token = request.COOKIES.get('csrftoken')
                ## return download confirmation form ----------------
                html_content: str = request_collection_helper.render_download_confirmation_form(
                    collection_overview_api_data, collection_id, csrf_token
                )
                return HttpResponse(html_content)
            else:
                log.debug('no collection data found, so rendering no-data-found alert')
                resp: HttpResponse = request_collection_helper.render_alert(
                    message='No collection data found.', include_info_link=False
                )
                return resp


def hlpr_initiate_download(request: HttpRequest) -> HttpResponse:
    """
    Handles request_collection() htmx confirm-download POST.
    - If the confirm-download is received, the job will be enqueued and an alert will be returned.
    """
    log.debug('starting hlpr_initiate_download()')
    collection_id = request.POST.get('collection_id', '').strip()
    if request.POST.get('action') == 'really_start_download':
        request_collection_helper.start_download(collection_id)
        return request_collection_helper.render_alert('Download started')
    else:
        return HttpResponse(status=405)  # Method Not Allowed


# -------------------------------------------------------------------
# support urls
# -------------------------------------------------------------------


def error_check(request):
    """
    Offers an easy way to check that admins receive error-emails (in development).
    To view error-emails in runserver-development:
    - run, in another terminal window: `python -m smtpd -n -c DebuggingServer localhost:1026`,
    - (or substitue your own settings for localhost:1026)
    """
    log.debug('starting error_check()')
    log.debug(f'project_settings.DEBUG, ``{project_settings.DEBUG}``')
    if project_settings.DEBUG is True:  # localdev and dev-server; never production
        log.debug('triggering exception')
        raise Exception('Raising intentional exception to check email-admins-on-error functionality.')
    else:
        log.debug('returning 404')
        return HttpResponseNotFound('<div>404 / Not Found</div>')


def version(request):
    """
    Returns basic branch and commit data.
    """
    log.debug('starting version()')
    rq_now = datetime.datetime.now()
    gatherer = GatherCommitAndBranchData()
    trio.run(gatherer.manage_git_calls)
    info_txt = f'{gatherer.branch} {gatherer.commit}'
    context = version_helper.make_context(request, rq_now, info_txt)
    output = json.dumps(context, sort_keys=True, indent=2)
    log.debug(f'output, ``{output}``')
    return HttpResponse(output, content_type='application/json; charset=utf-8')


def root(request):
    return HttpResponseRedirect(reverse('info_url'))
