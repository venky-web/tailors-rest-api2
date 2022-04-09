from django.shortcuts import get_object_or_404
from django.contrib.auth import get_user_model
from django.db.models import Q

from rest_framework import generics, status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes

from helpers import functions as helpers
from account import models, permissions, serializers
from account import custom_functions as c_func


class UserCreateView(generics.CreateAPIView):
    """view to create a new user"""
    queryset = get_user_model().objects.all()
    serializer_class = serializers.UserSerializer
    permission_classes = (IsAuthenticated | AllowAny,)
    authentication_classes = []

    def create(self, request, *args, **kwargs):
        """creates a new user in db"""
        c_func.check_for_username_password(request)
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        now = helpers.get_current_time()
        serializer.save(
            created_on=now,
            updated_on=now,
        )
        user = serializer.data
        business_id = request.query_params.get("bid", None)
        if business_id is not None:
            c_func.add_user_business_relation(business_id, user["id"],
                                              comments="Auto approved",
                                              status="Approved")
        response = Response()
        response.data = {
            "user": user,
        }
        return c_func.add_tokens(response, user)


class BusinessUserCreateView(generics.CreateAPIView):
    """view to create a new user"""
    queryset = get_user_model().objects.all()
    serializer_class = serializers.UserSerializer
    permission_classes = (IsAuthenticated | AllowAny,)
    authentication_classes = []

    def create(self, request, *args, **kwargs):
        """creates a new user in db"""
        c_func.check_for_username_password(request)
        business_data = request.data.get("business", None)
        if business_data is None:
            error = {
                "message": "Business information is missing"
            }
            return Response(error, status=status.HTTP_400_BAD_REQUEST)

        now = helpers.get_current_time()
        # business data serialization
        business_serializer = serializers.BusinessSerializer(data=business_data)
        business_serializer.is_valid(raise_exception=True)
        # user data serialization
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        business_serializer.save(created_on=now, updated_on=now)
        business = models.Business.objects.filter(id=business_serializer.data["id"]).first()
        serializer.save(
            created_on=now,
            updated_on=now,
            business=business,
            user_role="business_admin"
        )
        business_instance = c_func.update_business_staff_count(business.id)
        user = serializer.data
        response_data = {
            "user": user
        }
        response_data["user"]["business"] = serializers.BusinessSerializer(business_instance).data
        response = Response(data=response_data)
        return c_func.add_tokens(response, user)


class UserDetailView(generics.RetrieveUpdateDestroyAPIView):
    """user detail view to retrieve, update and destroy"""
    serializer_class = serializers.UserSerializer
    permission_classes = (IsAuthenticated, permissions.IsBusinessAdminOrStaff | permissions.IsOwner,
                          permissions.IsOwnerOrReadOnly,)

    def get_queryset(self):
        """returns queryset of active users"""
        return get_user_model().objects.filter(is_active=True, user_role="normal_user")

    def retrieve(self, request, *args, **kwargs):
        """returns a user obj with user id"""
        queryset = self.get_queryset()
        user = get_object_or_404(queryset, pk=kwargs["id"])
        self.check_object_permissions(request, user)
        serializer = self.get_serializer(user)
        if request.user.user_role == "business_admin" or request.user.user_role == "business_staff":
            response_data = c_func.get_user_data_for_business(request, serializer.data)
        else:
            response_data = c_func.get_user_profile_and_business_data(serializer.data)
        return Response(response_data, status=status.HTTP_200_OK)

    def update(self, request, *args, **kwargs):
        """updates a user obj"""
        queryset = self.get_queryset()
        user = get_object_or_404(queryset, pk=kwargs["id"])
        self.check_object_permissions(request, user)
        serializer = self.get_serializer(user, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save(
            request_user=request.user,
            updated_on=helpers.get_current_time()
        )
        response_data = c_func.get_user_profile_and_business_data(serializer.data)
        return Response(response_data, status=status.HTTP_200_OK)

    def destroy(self, request, *args, **kwargs):
        """deactivates a user"""
        queryset = self.get_queryset()
        user = get_object_or_404(queryset, pk=kwargs["id"])
        self.check_object_permissions(request, user)
        user.is_active = False
        user.save()
        return Response(None, status=status.HTTP_204_NO_CONTENT)


class UserProfileDetailView(generics.RetrieveUpdateAPIView):
    """retrieves and updates user profile data"""
    serializer_class = serializers.UserProfileSerializer
    queryset = models.UserProfile.objects.all()
    permission_classes = (IsAuthenticated, permissions.IsBusinessAdminOrStaffWithRelation | permissions.IsOwner,
                          permissions.IsOwnerOrReadOnly,)

    def retrieve(self, request, *args, **kwargs):
        """returns user profile data with matching user id"""
        user = get_object_or_404(get_user_model(), pk=kwargs["id"])
        self.check_object_permissions(request, user)
        user_profile = self.get_queryset().filter(user=kwargs["id"]).first()
        if user_profile:
            response_data = serializers.UserProfileReadOnlySerializer(user_profile).data
            return Response(response_data, status=status.HTTP_200_OK)
        else:
            return Response("{}", status=status.HTTP_200_OK)

    def update(self, request, *args, **kwargs):
        """updates a user profile"""
        user = get_object_or_404(get_user_model(), pk=kwargs["id"])
        self.check_object_permissions(request, user)
        user_profile = self.get_queryset().filter(user=kwargs["id"]).first()
        response_data = c_func.save_user_profile(request, user, user_profile)
        return Response(response_data, status=status.HTTP_200_OK)


class BusinessDetailView(generics.RetrieveUpdateDestroyAPIView):
    """view to retrieve, update and destroy business obj"""
    queryset = models.Business.objects.all()
    serializer_class = serializers.BusinessSerializer
    permission_classes = (IsAuthenticated, permissions.IsBusinessAdminOrStaff,
                          permissions.BusinessAdminOrStaffWithOwnBusiness,
                          permissions.ReadOnlyAccessToStaff)

    def retrieve(self, request, *args, **kwargs):
        """returns business obj with valid id"""
        queryset = self.get_queryset()
        business = get_object_or_404(queryset, pk=kwargs["id"])
        self.check_object_permissions(request, business)
        serialized_data = self.get_serializer(business).data
        return Response(serialized_data)

    def update(self, request, *args, **kwargs):
        """updates a business obj with valid id"""
        queryset = models.Business.objects.all()
        business = get_object_or_404(queryset, pk=kwargs["id"])
        self.check_object_permissions(request, business)
        serializer = self.get_serializer(business, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save(
            updated_on=helpers.get_current_time(),
            request_user=request.user
        )
        return Response(serializer.data)

    def destroy(self, request, *args, **kwargs):
        """deletes a business obj with valid id"""
        queryset = self.get_queryset()
        business = get_object_or_404(queryset, pk=kwargs["id"])
        self.check_object_permissions(request, business)
        business.delete()
        return Response(None, status=status.HTTP_204_NO_CONTENT)


class BusinessStaffView(generics.ListCreateAPIView):
    """creates a user or returns a list"""
    serializer_class = serializers.UserSerializer
    permission_classes = (IsAuthenticated, permissions.IsBusinessAdmin,
                          permissions.MaxStaffCount)

    def get_queryset(self):
        """returns queryset of users"""
        if self.request.user.is_superuser:
            return get_user_model().objects.all()

        return get_user_model().objects.filter(~Q(id=self.request.user.id), is_active=True,
                                               user_role="business_staff")

    def list(self, request, *args, **kwargs):
        """returns list of users with matching business id"""
        if request.user.is_superuser:
            staff_users = self.get_queryset()
        else:
            staff_users = self.get_queryset().filter(business=request.user.business)
        response_data = c_func.get_users(staff_users)
        return Response(response_data, status=status.HTTP_200_OK)

    def create(self, request, *args, **kwargs):
        """creates a new user in db"""
        business = None
        detail = {
            "message": "Business details are missing"
        }
        if request.user.is_superuser:
            business_id = request.data["business"]
            if business_id is None:
                return Response(detail, status=status.HTTP_400_BAD_REQUEST)

            business = models.Business.objects.filter(id=business_id).first()
        elif request.user.business:
            business = request.user.business

        if business is None:
            return Response(detail, status=status.HTTP_400_BAD_REQUEST)

        c_func.check_for_username_password(request)
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        now = helpers.get_current_time()
        serializer.save(
            created_on=now,
            updated_on=now,
            request_user=request.user,
            business=business,
            user_role="business_staff"
        )
        c_func.update_business_staff_count(business.id)
        response_data = c_func.get_user_profile_and_business_data(serializer.data)
        return Response(response_data, status=status.HTTP_200_OK)


class BusinessStaffDetailView(generics.RetrieveUpdateDestroyAPIView):
    """user detail view to retrieve, update and destroy"""
    serializer_class = serializers.UserSerializer
    permission_classes = (IsAuthenticated, permissions.IsBusinessAdminOrStaff, permissions.IsOwnBusiness,
                          permissions.ReadOnlyAccessToStaff | permissions.IsBusinessAdmin,
                          permissions.IsOwnerOrBusinessAdmin,)

    def get_queryset(self):
        """returns queryset of active users"""
        return get_user_model().objects.filter(is_active=True, user_role="business_staff")

    def retrieve(self, request, *args, **kwargs):
        """returns a staff user obj with related id"""
        queryset = self.get_queryset()
        user = get_object_or_404(queryset, pk=kwargs["staff_id"])
        self.check_object_permissions(request, user)
        serializer = self.get_serializer(user)
        response_data = c_func.get_user_profile_and_business_data(serializer.data)
        return Response(response_data, status=status.HTTP_200_OK)

    def update(self, request, *args, **kwargs):
        """updates a staff user obj with related id"""
        queryset = self.get_queryset()
        user = get_object_or_404(queryset, pk=kwargs["staff_id"])
        self.check_object_permissions(request, user)
        serializer = self.get_serializer(user, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save(
            request_user=request.user,
            updated_on=helpers.get_current_time()
        )
        response_data = c_func.get_user_profile_and_business_data(serializer.data)
        return Response(response_data, status=status.HTTP_200_OK)

    def destroy(self, request, *args, **kwargs):
        """deactivates a user"""
        queryset = self.get_queryset()
        user = get_object_or_404(queryset, pk=kwargs["staff_id"])
        self.check_object_permissions(request, user)
        user.is_active = False
        user.save()
        return Response(None, status=status.HTTP_204_NO_CONTENT)


class BusinessStaffProfileDetailView(generics.RetrieveUpdateAPIView):
    """retrieves and updates user profile data"""
    serializer_class = serializers.UserProfileSerializer
    queryset = models.UserProfile.objects.all()
    permission_classes = (IsAuthenticated, permissions.IsBusinessAdminOrStaff, permissions.IsOwnBusiness,
                          permissions.ReadOnlyAccessToStaff, permissions.IsOwnerOrBusinessAdmin,)

    def retrieve(self, request, *args, **kwargs):
        """returns user profile data with matching user id"""
        user = get_object_or_404(get_user_model(), pk=kwargs["staff_id"])
        self.check_object_permissions(request, user)
        queryset = self.get_queryset()
        user_profile = queryset.filter(user=kwargs["staff_id"]).first()
        if user_profile:
            response_data = serializers.UserProfileReadOnlySerializer(user_profile).data
            return Response(response_data, status=status.HTTP_200_OK)
        else:
            return Response("{}", status=status.HTTP_200_OK)

    def update(self, request, *args, **kwargs):
        """updates a user profile"""
        user = get_user_model().objects.filter(pk=kwargs["staff_id"]).first()
        self.check_object_permissions(request, user)
        queryset = self.get_queryset()
        user_profile = queryset.filter(user=kwargs["staff_id"]).first()
        response_data = c_func.save_user_profile(request, user, user_profile)
        return Response(response_data, status=status.HTTP_200_OK)


@api_view(["GET"])
@permission_classes([IsAuthenticated, permissions.IsBusinessAdminOrStaff])
def customers_list(request):
    """view to return list of customers tagged to business"""

    user_business_relations = models.UserBusinessRelation.objects.filter(business_id=request.user.business.id)
    users = []
    for relation in user_business_relations:
        if relation.request_status != "Approved":
            continue
        user = get_user_model().objects.filter(id=relation.user_id).first()
        if user:
            serialized_data = serializers.UserSerializer(user).data
            profile = models.UserProfile.objects.filter(user=relation.user_id).first()
            if profile:
                serialized_data["profile"] = serializers.CustomerProfileSerializer(profile).data
                relation = models.UserBusinessRelation.objects.filter(user_id=user.id,
                                                                      business_id=request.user.business.id).first()
                if relation and relation.request_status != "Approved":
                    serialized_data["profile"]["phone"] = "xxx"
                    serialized_data["profile"]["date_of_birth"] = None
                    serialized_data["profile"]["marital_status"] = "xxx"
            users.append(serialized_data)
    response = Response(data=users, status=status.HTTP_200_OK)
    return response
