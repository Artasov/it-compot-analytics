import logging

from django.conf import settings
from django.db import connections
from django.http import HttpResponse
from django_minio_backend import MinioBackend
from django_redis import get_redis_connection

from apps.Core.tasks.test_tasks import test_periodic_task

log = logging.getLogger('base')


# def signout(request):
#     logout(request)
#     return redirect('stupid_auth')


# def stupid_auth(request) -> HttpResponse:
#     form = StupidAuthForm(request.POST or None)
#     if form.is_valid():
#         email = form.cleaned_data['email']
#         username = email.split('@')[0]
#         password = form.cleaned_data['password']
#         try:
#             User.objects.get(email=email)
#         except User.DoesNotExist:
#             User.objects.create_user(
#                 username=username, email=email,
#                 password=settings.TEACHER_SALARY_PASSWORD
#             )
#         user = authenticate(request, username=username, password=password)
#         if user:
#             login(request, user)
#             add_user_to_group(user, 'teacher')
#             return redirect('menu')
#         else:
#             form.add_error(None, 'Что-то пошло не так.')
#     return render(request, 'Core/stupid_auth.html', {'form': form})


def health_test(request) -> HttpResponse:
    # Celery check
    test_periodic_task.delay('param1')

    # Проверка Redis
    if not get_redis_connection().flushall():
        log.error('Redis have not yet come to life')
        return HttpResponse("Redis error", status=500)
    try:
        connections['default'].cursor()
    except Exception as e:
        log.error(f'DB have not yet come to life: {str(e)}')
        return HttpResponse(f"DB error: {str(e)}", status=500)
    if not settings.DEV:
        minio_available = MinioBackend().is_minio_available()  # An empty string is fine this time
        if not minio_available:
            log.error(f'MINIO ERROR')
            log.error(minio_available.details)
            log.error(f'MINIO_STATIC_FILES_BUCKET = {MinioBackend().MINIO_STATIC_FILES_BUCKET}')
            log.error(f'MINIO_MEDIA_FILES_BUCKET = {MinioBackend().MINIO_MEDIA_FILES_BUCKET}')
            log.error(f'base_url = {MinioBackend().base_url}')
            log.error(f'base_url_external = {MinioBackend().base_url_external}')
            log.error(f'HTTP_CLIENT = {MinioBackend().HTTP_CLIENT}')
            return HttpResponse(f"MINIO ERROR", status=500)
    return HttpResponse("OK")
