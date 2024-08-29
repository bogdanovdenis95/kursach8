# habit_tracker/celery.py
from __future__ import absolute_import, unicode_literals
import os
from celery import Celery

# Установите переменную окружения для Django настроек
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'habit_tracker.settings')

app = Celery('habit_tracker')

# Используйте строки для конфигурации, чтобы избегать проблем импорта
app.config_from_object('django.conf:settings', namespace='CELERY')

# Загрузите задачи из всех зарегистрированных приложений Django
app.autodiscover_tasks()
