"""booktray URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.urls import include, path
from django.views.decorators.csrf import csrf_exempt
from graphene_django.views import GraphQLView
from django.conf import settings
from django.conf.urls.static import static
# import this

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", include("tray.urls")),
    path("",include("payments.urls")),
    # path('accounts/', include('django.contrib.auth.urls')),
    path(
        "password_reset/",
        auth_views.PasswordResetView.as_view(
            template_name="tray/password/password_reset.html"
        ),
        name="password_reset",
    ),
    path(
        "password_reset/done/",
        auth_views.PasswordResetDoneView.as_view(
            template_name="tray/password/password_reset_done.html"
        ),
        name="password_reset_done",
    ),
    path(
        "reset/<uidb64>/<token>/",
        auth_views.PasswordResetConfirmView.as_view(
            template_name="tray/password/password_reset_confirm.html"
        ),
        name="password_reset_confirm",
    ),
    path(
        "reset/done/",
        auth_views.PasswordResetCompleteView.as_view(
            template_name="tray/password/password_reset_complete.html"
        ),
        name="password_reset_complete",
    ),
    path(
        "graphql/",
        csrf_exempt(GraphQLView.as_view(graphiql=True)),
    ),
]

if settings.DEBUG:
     urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
admin.site.site_title = "Alltray admin"
admin.site.site_header = "Alltray Admin"
admin.site.index_title = "welcome to Alltray admin"
