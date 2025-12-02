from django.http import JsonResponse
from django.views import View

class AIModelView(View):
    def get(self, request):
        return JsonResponse({
            'message': 'AI Models endpoint working!',
            'data': []
        })