from django.db.models import Q
from django.shortcuts import get_object_or_404

from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status

from order.models import Order, OrderItem
from order import serializers
from helpers import functions as f


class OrderListCreateView(ListCreateAPIView):
    """ViewSet for orders"""
    serializer_class = serializers.OrderSerializer
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        """returns order list based on user type"""
        user = self.request.user
        orders = Order.objects.filter(Q(created_by=user.id) | Q(updated_by=user.id), Q(is_deleted=False))
        return orders

    def list(self, request, *args, **kwargs):
        """returns a list of orders"""
        queryset = self.get_queryset()
        serializer = self.serializer_class(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def create(self, request, *args, **kwargs):
        """Creates a new order in the DB"""
        serializer = self.serializer_class(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        user = self.request.user
        now = f.get_current_time()
        serializer.save(request_user=user, created_on=now, updated_on=now)
        return Response(serializer.data, status=status.HTTP_200_OK)


class OrderDetailView(RetrieveUpdateDestroyAPIView):
    """Retrieves, updates and deletes order"""
    serializer_class = serializers.OrderSerializer
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        """returns an order queryset for current user"""
        user = self.request.user
        orders = Order.objects.filter(created_by=user.id, is_deleted=False)
        return orders

    def retrieve(self, request, *args, **kwargs):
        """returns an order"""
        queryset = self.get_queryset()
        order = get_object_or_404(queryset, pk=kwargs["id"])
        serializer = self.serializer_class(order)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def update(self, request, *args, **kwargs):
        """updates an order in the db"""
        queryset = self.get_queryset()
        order = get_object_or_404(queryset, pk=kwargs["id"])
        user = self.request.user
        serializer = self.serializer_class(order, data=request.data, partial=True)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        serializer.save(request_user=user, updated_on=f.get_current_time())
        return Response(serializer.data, status=status.HTTP_200_OK)

    def delete(self, request, *args, **kwargs):
        """sets is_deleted flag to Y for order instance"""
        queryset = self.get_queryset()
        order = get_object_or_404(queryset, pk=kwargs["id"])
        user = self.request.user
        modified_product = self.get_serializer(order).data
        modified_product["is_deleted"] = True
        serializer = self.get_serializer(order, data=modified_product)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        serializer.save(request_user=user, updated_on=f.get_current_time())
        return Response(serializer.data, status=status.HTTP_204_NO_CONTENT)


class OrderItemListCreateView(ListCreateAPIView):
    """List and create view for order item"""
    serializer_class = serializers.OrderItemSerializer
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        """returns queryset for order items"""
        order_id = self.kwargs["order_id"]
        order_items = OrderItem.objects.filter(order_id=order_id, is_deleted=False)
        return order_items

    def list(self, request, *args, **kwargs):
        """returns a list of order items specific to the order"""
        get_object_or_404(Order, pk=kwargs["order_id"], is_deleted=False)
        queryset = self.get_queryset()
        serializer = self.serializer_class(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def create(self, request, *args, **kwargs):
        """creates a new order item for the specified order"""
        order = get_object_or_404(Order, pk=kwargs["order_id"], is_deleted=False)
        serializer = self.serializer_class(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        now = f.get_current_time()
        serializer.save(
            request_user=request.user,
            order=order,
            created_on=now,
            updated_on=now
        )
        return Response(serializer.data, status=status.HTTP_200_OK)


class OrderItemDetailView(RetrieveUpdateDestroyAPIView):
    """Retrieve, update and destroy view of order item"""
    serializer_class = serializers.OrderItemSerializer
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        """returns queryset of order items based on order id"""
        order_id = self.kwargs["order_id"]
        order_items = OrderItem.objects.filter(order_id=order_id, is_deleted=False)
        return order_items

    def retrieve(self, request, *args, **kwargs):
        """retrieves order item with id"""
        get_object_or_404(Order, pk=kwargs["order_id"], is_deleted=False)
        queryset = self.get_queryset()
        order_item = get_object_or_404(queryset, pk=kwargs["order_item_id"])
        serializer = self.get_serializer(order_item)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def update(self, request, *args, **kwargs):
        """updates an order item with id"""
        get_object_or_404(Order, pk=kwargs["order_id"], is_deleted=False)
        queryset = self.get_queryset()
        order_item = get_object_or_404(queryset, pk=kwargs["order_item_id"])
        serializer = self.serializer_class(order_item, data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        serializer.save(
            request_user=request.user,
            updated_on=f.get_current_time()
        )
        return Response(serializer.data, status=status.HTTP_200_OK)

    def destroy(self, request, *args, **kwargs):
        """marks an order item is_deleted to Y"""
        get_object_or_404(Order, pk=kwargs["order_id"], is_deleted=False)
        queryset = self.get_queryset()
        order_item = get_object_or_404(queryset, pk=kwargs["order_item_id"])
        modified_order_item = self.serializer_class(order_item).data
        modified_order_item["is_deleted"] = True
        serializer = self.serializer_class(order_item, data=modified_order_item)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        serializer.save(
            request_user=request.user,
            updated_on=f.get_current_time()
        )
        return Response(serializer.data, status.HTTP_200_OK)
