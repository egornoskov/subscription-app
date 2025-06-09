from django.http import HttpResponse
from django.urls import path


def dummy_view(request):
    return HttpResponse("Hello, this is a dummy view.")


urlpatterns = [
    path("", dummy_view, name="dummy"),
]
