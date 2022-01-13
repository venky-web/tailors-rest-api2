from django.shortcuts import get_object_or_404
from django.contrib.auth import get_user_model

from rest_framework import generics
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework import status

from account.serializers import UserSerializer
from helpers import functions as f


class UserCreateView(generics.CreateAPIView):
    """view to create a new user"""
    queryset = get_user_model().objects.all()
    serializer_class = UserSerializer
    permission_classes = (AllowAny,)
    authentication_classes = []

    def create(self, request, *args, **kwargs):
        """creates a new user in db"""
        email = request.data.get("email", None)
        if email:
            user = self.get_queryset().filter(email=email).first()
            if user and user.is_active == False:
                error = {
                    "message": "User is inactive"
                }
                return Response(error, status=status.HTTP_400_BAD_REQUEST)
        else:
            error = {
                "message": "Email or password is missing"
            }
            return Response(error, status=status.HTTP_400_BAD_REQUEST)

        serializer = self.serializer_class(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        now = f.get_current_time()
        serializer.save(created_on=now, updated_on=now)
        return Response(serializer.data, status=status.HTTP_200_OK)


class UserListView(generics.ListAPIView):
    """creates a user or returns a list"""
    queryset = get_user_model().objects.all()
    serializer_class = UserSerializer
    permission_classes = (IsAuthenticated,)


class UserDetailView(generics.RetrieveUpdateDestroyAPIView):
    """user detail view to retrieve, update and destroy"""
    queryset = get_user_model().objects.all()
    serializer_class = UserSerializer
    permission_classes = (IsAuthenticated,)

    def retrieve(self, request, *args, **kwargs):
        """returns a user obj with user id"""
        queryset = self.get_queryset()
        user = get_object_or_404(queryset, pk=kwargs["id"])
        serializer = self.get_serializer(user)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def update(self, request, *args, **kwargs):
        """updates a user obj"""
        queryset = self.get_queryset()
        user = get_object_or_404(queryset, pk=kwargs["id"])
        serializer = self.get_serializer(user, data=request.data, partial=True)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        serializer.save(
            request_user=request.user,
            updated_on=f.get_current_time()
        )
        return Response(serializer.data, status=status.HTTP_200_OK)

    def destroy(self, request, *args, **kwargs):
        """deactivates a user"""
        queryset = self.get_queryset()
        user = get_object_or_404(queryset, pk=kwargs["id"])
        modified_user = self.get_serializer(user).data
        modified_user["is_active"] = False
        serializer = self.get_serializer(user, data=modified_user, partial=True)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        serializer.save(
            request_user=request.user,
            updated_on=f.get_current_time()
        )
        return Response(serializer.data, status=status.HTTP_200_OK)


class BusinessListCreateView(generics.ListCreateAPIView):
    """"""