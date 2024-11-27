import datetime
import json
import logging

import trio
from django.conf import settings as project_settings
from django.http import HttpResponse, HttpResponseNotFound, HttpResponseRedirect
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
    # context = { 'message': 'Hello, world.' }
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


def request_collection(request):
    """
    Handles Archive-It collection download requests via htmx.
    """
    log.debug('starting request_collection()')
    if request.method == 'GET':
        log.debug('handling GET request')
        recents: list = request_collection_helper.get_recent_collections()
        context = {'recent_items': recents}
        return render(request, 'request_collection.html', context)

    elif request.method == 'POST':
        log.debug('POST request')
        collection_id = request.POST.get('collection_id', '').strip()

        if not collection_id:
            log.debug('no collection_id')
            return HttpResponse('<div class="alert">Collection ID is required.</div>', status=200)

        if request.POST.get('action') == 'really_start_download':
            return HttpResponse('<div class="alert">Download started. <a href="/info/">More info</a></div>')

        status = request_collection_helper.check_collection_status(collection_id)
        log.debug(f'status, ``{status}``')

        if status.get('exists') == 'in_progress':
            log.debug('status is in_progress')
            return HttpResponse('<div class="alert">Download in progress. <a href="/info/">More info</a></div>')

        if status.get('exists') == 'completed':
            log.debug('status is completed')
            return HttpResponse('<div class="alert">Download completed. <a href="/info/">More info</a></div>')

        if not status.get('exists'):
            log.debug('status does not exist')
            # Simulate API call using a helper stub
            api_data = request_collection_helper.get_collection_data(collection_id)
            log.debug(f'api_data, ``{api_data}``')
            if api_data:
                csrf_token = request.COOKIES.get('csrftoken')
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

            return HttpResponse('<div class="alert">No collection data found.</div>', status=404)

        return HttpResponse('<div class="alert">Unknown error occurred.</div>', status=500)

    ## end def request_collection()


# def request_collection(request):
#     """
#     Handles Archive-It collection download requests.
#     On GET, displays a form to input a collection ID.
#     On POST, checks and initiates a download process and redirects to avoid resubmission issues.
#     """
#     log.debug('starting request_collection()')

#     if request.method == 'GET':
#         # message = request.session.get('message', '')
#         message = request.session.pop('message', '')
#         return render(request, 'request_collection.html', {'message': message})

#     elif request.method == 'POST':
#         collection_id = request.POST.get('collection_id', '').strip()

#         if not collection_id:
#             request.session['message'] = 'Collection ID is required.'
#             return redirect(request.path)

#         log.debug(f'Received collection ID: {collection_id}')
#         status = request_collection_helper.check_collection_status(collection_id)

#         if status.get('exists'):
#             request.session['message'] = f'Collection {collection_id} is already downloaded or in process.'
#             return redirect(request.path)

#         ## Initiate download if not already handled
#         result = request_collection_helper.initiate_download(collection_id)
#         request.session['message'] = result.get('message', f'Collection {collection_id} download initiated.')
#         return redirect(request.path)

#     ## end def request_collection()


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
