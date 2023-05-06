from django.shortcuts import get_object_or_404
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status

from api.serializers import UserSerializer, SubscribersSerializer, FollowSerializer
from .models import User, Subscribers

app_name = 'users'


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer

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
                context={"request": request}
            )
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        elif request.method == 'DELETE':
            instance = get_object_or_404(Subscribers, author=pk, user=user)
            instance.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        
    @action(
        methods=['get'],
        detail=False,
        permission_classes=[IsAuthenticated]
    )
    def subscriptions(self, request):
        user = request.user
        qs = user.following.all()
        serializer = SubscribersSerializer(qs,
                                           many=True,
                                           context={'request': request})
        return Response(serializer.data)
