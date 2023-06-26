from django.shortcuts import render


# Create your views here.
def debug(request):
    return render(request, "debug.html", context={"test_check": "ok"})
