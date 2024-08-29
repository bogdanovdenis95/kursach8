from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils.timezone import make_aware
from django_celery_beat.models import PeriodicTask, ClockedSchedule
import json
from datetime import datetime, timedelta


class Habit(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE
    )
    location = models.CharField(max_length=100)
    time = models.TimeField()
    action = models.CharField(max_length=255)
    is_pleasant = models.BooleanField(default=False)
    linked_habit = models.ForeignKey(
        'self', null=True, blank=True, on_delete=models.SET_NULL
    )
    periodicity = models.PositiveIntegerField(default=1)
    reward = models.CharField(max_length=255, null=True, blank=True)
    estimated_time = models.PositiveIntegerField()
    is_public = models.BooleanField(default=False)

    def clean(self):
        if self.reward and self.linked_habit:
            raise ValidationError(
                "Нельзя одновременно указать и вознаграждение, и связанную привычку."
            )
        if self.estimated_time > 120:
            raise ValidationError(
                "Время на выполнение должно быть не больше 120 секунд."
            )
        if self.linked_habit and not self.linked_habit.is_pleasant:
            raise ValidationError(
                "Связанная привычка должна быть приятной."
            )
        if self.is_pleasant and (self.reward or self.linked_habit):
            raise ValidationError(
                "Приятная привычка не может иметь вознаграждение или связанную привычку"
            )
        if not (1 <= self.periodicity <= 7):
            raise ValidationError(
                "Периодичность выполнения привычки должна быть от 1 до 7 дней."
            )

    def __str__(self):
        return f"{self.action} at {self.time} in {self.location}"

    def schedule_notification(self):
        """
        Создает или обновляет задачу напоминания в Celery Beat.
        """
        now = datetime.now()
        notify_time = datetime.combine(now.date(), self.time)
        if notify_time < now:
            notify_time += timedelta(days=1)
        notify_time = make_aware(notify_time)

        # Создаем или обновляем задачу
        ClockedSchedule.objects.update_or_create(
            clocked_time=notify_time,
            defaults={
                'clocked_time': notify_time,
            }
        )

        PeriodicTask.objects.update_or_create(
            name=f'habit_{self.id}_notification',
            defaults={
                'task': 'habits.tasks.send_telegram_notification',
                'one_off': True,
                'enabled': True,
                'clocked': ClockedSchedule.objects.get(clocked_time=notify_time),
                'kwargs': json.dumps({'habit_id': self.id}),
            }
        )

    def cancel_notification(self):
        """
        Отменяет задачу напоминания в Celery Beat.
        """
        PeriodicTask.objects.filter(name=f'habit_{self.id}_notification').delete()


@receiver(post_save, sender=Habit)
def manage_habit_notification(sender, instance, **kwargs):
    """
    Управляет задачами напоминания при создании или обновлении привычки.
    """
    if kwargs.get('created', False):
        # Если привычка была только что создана, планируем напоминание
        instance.schedule_notification()
    else:
        # Если привычка была обновлена, отменяем старое напоминание и планируем новое
        instance.cancel_notification()
        instance.schedule_notification()
