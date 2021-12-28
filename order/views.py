from django.shortcuts import get_object_or_404
from django.db.models import Q

from rest_framework.viewsets import ModelViewSet
from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status

from order.models import Order, OrderItem
from order import serializers


class OrderListCreateView(ListCreateAPIView):
    """ViewSet for orders"""
    serializer_class = serializers.OrderSerializer
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        """returns order list based on user type"""
        user = self.request.user
        orders = Order.objects.filter(Q(created_by=user.id) | Q(updated_by=user.id), Q(is_deleted="N"))
        return orders

    def list(self, request, *args, **kwargs):
        """returns a list of orders"""
        queryset = self.get_queryset()
        serializer = self.serializer_class(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def create(self, request, *args, **kwargs):
        """Creates a new order in the DB"""
        user = self.request.user
        serializer = self.serializer_class(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        serializer.save(user=user)
        return Response(serializer.data, status=status.HTTP_200_OK)


class OrderUpdateDeleteView(RetrieveUpdateDestroyAPIView):
    """Retrieves, updates and deletes order"""
    serializer_class = serializers.OrderSerializer
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        """returns an order queryset for current user"""
        user = self.request.user
        orders = Order.objects.filter(created_by=user.id)
        return orders

    def retrieve(self, request, *args, **kwargs):
        """returns an order"""
        order = get_object_or_404(Order, pk=kwargs["id"])
        serializer = self.serializer_class(order)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def update(self, request, *args, **kwargs):
        """updates an order in the db"""
        user = self.request.user
        order = get_object_or_404(Order, pk=kwargs["id"])
        serializer = self.serializer_class(order, data=request.data, partial=True)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        serializer.save(user=user)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def delete(self, request, *args, **kwargs):
        """sets is_deleted flag to Y for order instance"""
        user = self.request.user
        order = get_object_or_404(Order, pk=kwargs["id"])
        order.is_deleted = "Y"
        print(order)
        serializer = self.serializer_class(data=order)
        if serializer.is_valid():
            serializer.save(user=user)
        return Response(serializer.data, status=status.HTTP_204_NO_CONTENT)


class OrderItemViewSet(ModelViewSet):
    """viewSet for order items"""
    queryset = OrderItem.objects.all()
    serializer_class = serializers.OrderItemSerializer
    permission_classes = (IsAuthenticated,)
