from rest_framework import generics, viewsets
from rest_framework.permissions import AllowAny, IsAuthenticated

from users.permissions import IsOwnerOrReadOnly

from .models import Habit
from .paginators import CustomPagination
from .serializers import HabitSerializer


class HabitViewSet(viewsets.ModelViewSet):
    queryset = Habit.objects.all()
    serializer_class = HabitSerializer
    pagination_class = CustomPagination  # Пагинация
    permission_classes = [IsAuthenticated, IsOwnerOrReadOnly]

    def get_queryset(self):
        if self.action == 'list':
            return Habit.objects.filter(user=self.request.user).order_by('id')
        return Habit.objects.filter(user=self.request.user).order_by('id')

    def perform_create(self, serializer):
        habit = serializer.save(user=self.request.user)
        habit.full_clean()  # Вызываем валидацию модели

    def perform_update(self, serializer):
        habit = serializer.save(user=self.request.user)
        habit.full_clean()  # Вызываем валидацию модели


class HabitListView(generics.ListCreateAPIView):
    queryset = Habit.objects.all()
    serializer_class = HabitSerializer


class PublicHabitListView(generics.ListAPIView):
    queryset = Habit.objects.filter(is_public=True)
    serializer_class = HabitSerializer
    pagination_class = CustomPagination
    permission_classes = [AllowAny]
