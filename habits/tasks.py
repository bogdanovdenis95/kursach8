import asyncio

import telegram
from celery import shared_task

from .models import Habit


@shared_task
def send_telegram_notification(habit_id):
    habit = Habit.objects.get(id=habit_id)
    bot = telegram.Bot(token='6875683912:AAHydQ3a5Sm8Y2oSvvMFeEJCVlEodQI7-X0')

    async def send_message():
        message = f"Напоминание: {habit.action} в {habit.time} в {habit.location}."
        await bot.send_message(chat_id='715858633', text=message)

    loop = asyncio.get_event_loop()
    loop.run_until_complete(send_message())
