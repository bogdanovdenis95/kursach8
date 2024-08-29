from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from .models import Habit
from datetime import time

User = get_user_model()


class HabitViewSetTest(APITestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            email='test@example.com', password='testpass123'
        )
        refresh = RefreshToken.for_user(self.user)
        self.access_token = str(refresh.access_token)
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.access_token)
        self.habit = Habit.objects.create(
            user=self.user,
            location="Home",
            time=time(19, 0),  # Use datetime.time object here
            action="Read a book",
            periodicity=1,
            estimated_time=10
        )

    def test_list_habits(self):
        response = self.client.get('/api/habits/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_create_habit(self):
        response = self.client.post('/api/habits/', {
            'user': self.user.id,
            'location': 'Office',
            'time': '12:00:00',
            'action': 'Exercise',
            'periodicity': 1,
            'estimated_time': 20
        })
        print(response.content)  # Add this line to see the error message
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_update_habit(self):
        response = self.client.put(f'/api/habits/{self.habit.id}/', {
            'user': self.user.id,
            'location': 'Office',
            'time': '12:00:00',
            'action': 'Exercise',
            'periodicity': 1,
            'estimated_time': 20
        })
        print(response.content)  # Add this line to see the error message
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_delete_habit(self):
        response = self.client.delete(f'/api/habits/{self.habit.id}/')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_list_public_habits(self):
        Habit.objects.create(
            user=self.user,
            location="Park",
            time=time(10, 0),
            action="Walk",
            periodicity=1,
            estimated_time=30,
            is_public=True
        )
        response = self.client.get('/api/public-habits/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)


class UserViewSetTest(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email='test@example.com',
            password='testpass123'
        )
        refresh = RefreshToken.for_user(self.user)
        self.access_token = str(refresh.access_token)
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.access_token)

    def test_user_list(self):
        response = self.client.get('/api/users/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_user_detail(self):
        response = self.client.get(f'/api/users/{self.user.id}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
