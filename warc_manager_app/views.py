import datetime
import json
import logging

import trio
from django.conf import settings as project_settings
from django.contrib.auth.decorators import login_required
from django.http import HttpRequest, HttpResponse, HttpResponseNotFound, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse

from warc_manager_app.lib import request_collection_helper, version_helper
from warc_manager_app.lib.shib_handler import shib_decorator
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


@shib_decorator
def login(request):
    """
    Handles authentication and initial authorization (lib-staff) via shib. Then:
    - On successful authorization, logs user in and redirects to the `next_url`.
        - If no `next_url`, redirects to the `info` page.
    Called automatically by attempting to access an `@login_required` view.
    """
    log.debug('\n\nstarting shib_login()')
    next_url = request.GET.get('next', None)
    log.debug(f'next_url, ```{next_url}```')
    if not next_url:
        log.debug(f'session_keys, ```{list( request.session.keys() )}```')
        if request.session.get('redirect_url', None):
            redirect_url = request.session['redirect_url']
        else:
            # redirect_url = reverse( 'editor_index_url' )
            redirect_url = reverse('info_url')
    else:
        redirect_url = request.GET['next']  # may be same page
    if request.session.get('redirect_url', None):  # cleanup
        request.session.pop('redirect_url', None)
    log.debug('redirect_url, ```%s```' % redirect_url)
    return HttpResponseRedirect(redirect_url)


def logout(request):
    """
    Will log user out and redirect to the `info` page.
    """
    log.debug('starting logout()')
    return HttpResponseRedirect(reverse('info_url'))


## template to implement above
# def shib_logout( request ):
#     """ Clears session, hits shib logout, and redirects user to landing page. """
#     log.debug( 'request.__dict__, ```%s```' % request.__dict__ )
#     request.session[u'authz_info'][u'authorized'] = False
#     logout( request )
#     scheme = u'https' if request.is_secure() else u'http'
#     redirect_url = u'%s://%s%s' % ( scheme, request.get_host(), reverse(u'request_url') )
#     if request.get_host() == u'127.0.0.1' and project_settings.DEBUG == True:  # eases local development
#         pass
#     else:
#         encoded_redirect_url =  urlquote( redirect_url )  # django's urlquote()
#         redirect_url = u'%s?return=%s' % ( os.environ[u'EZSCAN__SHIB_LOGOUT_URL_ROOT'], encoded_redirect_url )
#     log.debug( u'in views.shib_logout(); redirect_url, `%s`' % redirect_url )
#     return HttpResponseRedirect( redirect_url )


@login_required
def request_collection(request: HttpRequest) -> HttpResponse:
    """
    Displays main page for requesting collection downloads.
    """
    log.debug('starting request_collection()')
    log.debug(f'user-authenticated-check, ``{request.user.is_authenticated}``')
    if request.user.is_authenticated:
        ## get user's first name
        user_first_name = request.user.first_name
        context = {'is_logged_in': 'yes', 'username': user_first_name}
    else:
        context = {'is_logged_in': 'no'}
    if request.method == 'GET':
        log.debug('handling GET request')
        recents: list = request_collection_helper.get_recent_collections()
        # context = {'recent_items': recents}
        context['recent_items'] = recents
        return render(request, 'request_collection.html', context)
    else:
        ## htmx POSTs are handled by the helper functions below
        resp = HttpResponse(status=405)  # Method Not Allowed
    return resp


@login_required
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


@login_required
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
