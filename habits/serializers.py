from rest_framework import serializers
from .models import Habit


class HabitSerializer(serializers.ModelSerializer):
    class Meta:
        model = Habit
        fields = '__all__'

    def validate(self, data):
        """
        Проверка общих условий, которые не связаны с конкретными полями.
        """
        # Получаем объект до изменений для проверки
        instance = self.instance

        if instance:
            # Проверяем конфликт между вознаграждением и связанной привычкой
            if (
                'reward' in data and data.get('reward') and
                'linked_habit' in data and data.get('linked_habit')
            ):
                raise serializers.ValidationError(
                    "Нельзя одновременно указать и вознаграждение, и связанную привычку"
                )

            # Проверяем время выполнения
            if 'estimated_time' in data and data.get('estimated_time') > 120:
                raise serializers.ValidationError(
                    "Время на выполнение должно быть не больше 120 секунд."
                )

            # Проверяем связанную привычку
            if (
                'linked_habit' in data and data.get('linked_habit') and
                not data['linked_habit'].is_pleasant
            ):
                raise serializers.ValidationError(
                    "Связанная привычка должна быть приятной."
                )

            # Проверяем приятную привычку
            if (
                'is_pleasant' in data and data.get('is_pleasant') and
                ('reward' in data and data.get('reward') or
                 'linked_habit' in data and data.get('linked_habit'))
            ):
                raise serializers.ValidationError(
                 "Приятная привычка не может иметь вознаграждение или связанную привычк"
                )

        return data

    def validate_periodicity(self, value):
        """
        Проверка поля periodicity.
        """
        if not (1 <= value <= 7):
            raise serializers.ValidationError(
                "Периодичность выполнения привычки должна быть от 1 до 7 дней."
            )
        return value

    def validate_estimated_time(self, value):
        """
        Проверка поля estimated_time.
        """
        if value > 120:
            raise serializers.ValidationError(
                "Время на выполнение должно быть не больше 120 секунд."
            )
        return value

    def validate_linked_habit(self, value):
        """
        Проверка поля linked_habit.
        """
        if value and not value.is_pleasant:
            raise serializers.ValidationError(
                "Связанная привычка должна быть приятной."
            )
        return value

    def validate_is_pleasant(self, value):
        """
        Проверка поля is_pleasant.
        """
        if (
            value and
            (self.initial_data.get('reward') or
             self.initial_data.get('linked_habit'))
        ):
            raise serializers.ValidationError(
                "Приятная привычка не может иметь вознаграждение или связанную привычку"
            )
        return value

    def update(self, instance, validated_data):
        """
        Обновление экземпляра объекта с учетом частичного обновления.
        """
        # Обновляем только измененные поля
        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        # Выполняем валидацию на уровне модели после частичного обновления
        instance.clean()
        instance.save()

        return instance
