"""
URL configuration for The Daily Dev (config project).
"""
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.contrib.sitemaps.views import sitemap
from django.http import HttpResponse
from django.urls import include, path
from django.views.generic import TemplateView

from articles.sitemaps import ArticleSitemap, StaticViewSitemap


def healthz(request):
    """Minimal liveness endpoint for container/orchestrator health checks.

    Deliberately avoids touching the database so it stays fast and doesn't
    report "unhealthy" during a brief DB blip that the app itself can
    tolerate.
    """
    return HttpResponse("ok", content_type="text/plain")

sitemaps = {
    "articles": ArticleSitemap,
    "static": StaticViewSitemap,
}

urlpatterns = [
    path("admin/", admin.site.urls),
    path("healthz/", healthz, name="healthz"),
    path("", include("newsroom.urls")),
    path("article/", include("articles.urls")),
    path(
        "sitemap.xml",
        sitemap,
        {"sitemaps": sitemaps},
        name="django.contrib.sitemaps.views.sitemap",
    ),
    path(
        "robots.txt",
        TemplateView.as_view(template_name="robots.txt", content_type="text/plain"),
        name="robots-txt",
    ),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
