from django.http import HttpResponse


def test_crispy_view(request):
    return HttpResponse("OK")
