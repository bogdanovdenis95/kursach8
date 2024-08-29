from rest_framework.permissions import BasePermission


class IsOwnerOrReadOnly(BasePermission):
    def has_object_permission(self, request, view, obj):
        # Редактирование и удаление только для владельца
        if request.method in ['PUT', 'PATCH', 'DELETE']:
            return obj.user == request.user
        return True
