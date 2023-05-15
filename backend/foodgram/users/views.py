from api.serializers import (FollowSerializer, SubscribersSerializer,
                             UsersSerializer, UserSignUpSerializer)
from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from djoser.views import UserViewSet

from api.pagination import PageLimitPagination
from .models import Subscribers, User

app_name = 'users'


class CustomUserViewSet(UserViewSet):
    queryset = User.objects.all()
    pagination_class = PageLimitPagination
    lookup_field = 'pk'

    def get_serializer_class(self):
        if self.request.method in ['POST', 'PUT', 'PATCH']:
            return UserSignUpSerializer
        return UsersSerializer

    def get_serializer_context(self):
        return {
            'request': self.request,
            'format': self.format_kwarg,
            'view': self,
            'subscriptions': set(Subscribers.objects.filter(user_id=self.request.user).values_list('author_id', flat=True))
        }

    @action(
        methods=['post', 'delete'],
        detail=True,
        permission_classes=[IsAuthenticated,]
    )
    def subscribe(self, request, pk):
        user = request.user
        author = get_object_or_404(User, pk=pk)
        if request.method == 'POST':
            serializer = FollowSerializer(
                data={'user': user.pk, 'author': author.pk},
                context=self.get_serializer_context()
            )
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        elif request.method == 'DELETE':
            instance = get_object_or_404(Subscribers, author=pk, user=user)
            instance.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        methods=['GET'],
        detail=False,
        permission_classes=[IsAuthenticated]
    )
    def subscriptions(self, request):
        user = request.user
        queryset = User.objects.filter(following__user=user)
        page = self.paginate_queryset(queryset)
        serializer = SubscribersSerializer(page,
                                           many=True,
                                           context=self.get_serializer_context())
        return self.get_paginated_response(serializer.data)
