from django.http import JsonResponse

def validate(request):
    return JsonResponse({'message': 'Validated'})