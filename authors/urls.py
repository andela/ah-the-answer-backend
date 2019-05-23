"""authors URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.11/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.urls import include, path

from django.contrib import admin

from django.conf.urls import url


from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi

schema_view = get_schema_view(
    openapi.Info(
        title="Authors Haven API",
        default_version='v1',
        description="Auhtors Haven is an app for the creative at heart",
        contact=openapi.Contact(email="authorshaven24@gmail.com"),
        license=openapi.License(name="MIT License"),
    ),
    public=True,
    permission_classes=(permissions.AllowAny,))


urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include(('authors.apps.authentication.urls',
                          'authors.apps.authentication'),
                          namespace='authentication')),
    path('api/', include(('authors.apps.profiles.urls', 'authors.apps.profile'),
                         namespace='profile')),
    path('api/', include(('authors.apps.articles.urls', 'authors.apps.articles'),
                         namespace='articles')),
    path('api/', include(('authors.apps.follow.urls', 'authors.apps.follow'),
                         namespace='follow')),
    path('api/', include(('authors.apps.report.urls', 'authors.apps.report'),
                         namespace='report')),
    path(
        'api/',
        include(
            ('authors.apps.comments.urls', 'authors.apps.comments'),
            namespace="comments"
        )
    ),
    path(
        'api/',
        include(
            ('authors.apps.stats.urls', 'authors.apps.stats'),
            namespace="stats"
        )
    ),
    path(
        'api/',
        include(
            ('authors.apps.notify.urls', 'authors.apps.notify'),
            namespace="notifications"
        )
    ),

    path('api/redoc/', schema_view.with_ui('redoc',
                                           cache_timeout=0),
         name='schema-redoc'),
    path('api/swagger/', schema_view.with_ui('swagger',
                                             cache_timeout=0),
         name='schema-swagger-ui'),
    path(
        'api/',
        include(
            ('authors.apps.bookmark.urls', 'authors.apps.bookmark'),
            namespace='bookmark'
        )
    ),
]
