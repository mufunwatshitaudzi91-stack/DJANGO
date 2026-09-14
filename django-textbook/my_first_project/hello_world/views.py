from django.http import HttpResponse

def hello_world(request):
    name = "Django Developer"
    response_text = f"Hello, {name}! Welcome to your first view."
    return HttpResponse(response_text)
    