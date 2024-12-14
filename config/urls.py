from django.contrib import admin
from django.urls import path

from warc_manager_app import views

urlpatterns = [
    ## main ---------------------------------------------------------
    path('info/', views.info, name='info_url'),
    path('pre_login/', views.collection, name='pre_login_url'),
    path('login/', views.login, name='login_url'),
    path('logout/', views.logout, name='logout_url'),
    path('request_collection/', views.request_collection, name='request_collection_url'),
    path('hlpr_check_coll_id/', views.hlpr_check_coll_id, name='hlpr_check_coll_id_url'),
    path('hlpr_initiate_download/', views.hlpr_initiate_download, name='hlpr_initiate_download_url'),
    ## other --------------------------------------------------------
    path('', views.root, name='root_url'),  # redirects to `info`
    path('admin/', admin.site.urls),
    path('error_check/', views.error_check, name='error_check_url'),
    path('version/', views.version, name='version_url'),
]
