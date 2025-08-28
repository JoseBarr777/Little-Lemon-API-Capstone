from django.shortcuts import render
from django.contrib.auth.models import User, Group

from rest_framework import generics, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from django_filters import FilterSet, filters
from django_filters.rest_framework import DjangoFilterBackend

from .models import Category, MenuItem, Cart, Order, OrderItem
from .serializers import CategorySerializer, MenuItemSerializer, UserSerializer, CartSerializer, OrderSerializer
from .permissions import IsManagerOrReadOnly, IsManager, IsCustomer, IsDeliveryCrew

from drf_spectacular.utils import extend_schema, extend_schema_view, OpenApiParameter
from drf_spectacular.types import OpenApiTypes


from rest_framework.permissions import IsAuthenticated

# Create your views here.

@extend_schema_view(
    get=extend_schema(
        summary="List categories",
        tags=["Categories"],
    ),
    post=extend_schema(
        summary="Create category (Manager only)",
        tags=["Categories"],
    ),
)
class CategoryListCreateView(generics.ListCreateAPIView):
    """
    GET: List categories (paginated, ordered by id).
    POST: Create a category with fields: slug, title.
    """
    queryset = Category.objects.all().order_by("id")
    serializer_class = CategorySerializer
    permission_classes = [IsManagerOrReadOnly]

@extend_schema_view(
    get=extend_schema(summary="Retrieve category", tags=["Categories"]),
    patch=extend_schema(summary="Update category (Manager only)", tags=["Categories"]),
    delete=extend_schema(summary="Delete category (Manager only)", tags=["Categories"]),
)
class CategoryDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    GET: Retrieve one category.
    PATCH/PUT: Update fields.
    DELETE: Remove the category.
    """
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [IsManagerOrReadOnly]
    

class MenuItemFilter(FilterSet):
    category = filters.NumberFilter(field_name="category_id")
    category_slug = filters.CharFilter(field_name="category__slug", lookup_expr="iexact")
    featured = filters.BooleanFilter()
    price_min = filters.NumberFilter(field_name="price", lookup_expr="gte")
    price_max = filters.NumberFilter(field_name="price", lookup_expr="lte")

    class Meta:
        model = MenuItem
        fields = ["category", "category_slug", "featured", "price_min", "price_max"]

@extend_schema_view(
    get=extend_schema(
        summary="List menu items",
        tags=["Menu Items"],
        parameters=[
            OpenApiParameter(name="search", description="Search title", required=False, type=str),
            OpenApiParameter(name="ordering", description="Comma-separated fields, e.g. `-price,title`", required=False, type=str),
            OpenApiParameter(name="category", description="Category ID", required=False, type=int),
            OpenApiParameter(name="category_slug", description="Category slug (iexact)", required=False, type=str),
            OpenApiParameter(name="featured", description="true/false", required=False, type=bool),
            OpenApiParameter(name="price_min", description="Minimum price", required=False, type=float),
            OpenApiParameter(name="price_max", description="Maximum price", required=False, type=float),
        ],
    ),
    post=extend_schema(summary="Create menu item (Manager only)", tags=["Menu Items"]),
)
class MenuItemListCreateView(generics.ListCreateAPIView):
    """
    GET: List menu items (paginated, ordered by id). (?search=, ?ordering=price,-title, ?category=1, ?featured=true, ?price_min=5)
    POST: Create a menu item with fields: title, price, category, featured.
    """
    queryset = MenuItem.objects.all().order_by("id")
    serializer_class = MenuItemSerializer
    filterset_class = MenuItemFilter
    search_fields = ["title"]
    ordering_fields = ["price", "title", "id"]
    permission_classes = [IsManagerOrReadOnly]
    
    

@extend_schema_view(
    get=extend_schema(summary="Retrieve menu item", tags=["Menu Items"]),
    patch=extend_schema(summary="Update menu item (Manager only)", tags=["Menu Items"]),
    delete=extend_schema(summary="Delete menu item (Manager only)", tags=["Menu Items"]),
)
class MenuItemDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    GET: Retrieve one menu item.
    PATCH/PUT: Update fields.
    DELETE: Remove the item.
    """
    queryset = MenuItem.objects.all()
    serializer_class = MenuItemSerializer
    permission_classes =[IsManagerOrReadOnly]


# User Group Management Views
@extend_schema_view(
    get=extend_schema(
        summary="List all managers",
        tags=["User Groups"],
        responses={200: UserSerializer(many=True)}
    ),
    post=extend_schema(
        summary="Add user to manager group",
        tags=["User Groups"],
        request=UserSerializer,
        responses={201: {"description": "User added to managers"}}
    ),
)
class ManagerUsersView(generics.ListCreateAPIView):
    """
    GET: Returns all managers
    POST: Assigns user to manager group
    """
    serializer_class = UserSerializer
    permission_classes = [IsManager]
    
    def get_queryset(self):
        manager_group, created = Group.objects.get_or_create(name='Manager')
        return manager_group.user_set.all()
    
    def create(self, request, *args, **kwargs):
        username = request.data.get('username')
        if not username:
            return Response({'error': 'Username required'}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            user = User.objects.get(username=username)
            manager_group, created = Group.objects.get_or_create(name='Manager')
            manager_group.user_set.add(user)
            return Response({'message': f'User {username} added to managers'}, status=status.HTTP_201_CREATED)
        except User.DoesNotExist:
            return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)


@extend_schema_view(
    delete=extend_schema(
        summary="Remove user from manager group",
        tags=["User Groups"],
        responses={200: {"description": "Success"}, 404: {"description": "User not found"}}
    ),
)
class ManagerUserDetailView(generics.DestroyAPIView):
    """
    DELETE: Removes user from manager group
    """
    queryset = User.objects.all()
    permission_classes = [IsManager]
    lookup_field = 'pk'
    lookup_url_kwarg = 'user_id'
    
    def destroy(self, request, *args, **kwargs):
        try:
            user = self.get_object()
            manager_group = Group.objects.get(name='Manager')
            manager_group.user_set.remove(user)
            return Response({'message': f'User {user.username} removed from managers'}, status=status.HTTP_200_OK)
        except User.DoesNotExist:
            return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)


@extend_schema_view(
    get=extend_schema(
        summary="List all delivery crew members",
        tags=["User Groups"],
        responses={200: UserSerializer(many=True)}
    ),
    post=extend_schema(
        summary="Add user to delivery crew group",
        tags=["User Groups"],
        request=UserSerializer,
        responses={201: {"description": "User added to delivery crew"}}
    ),
)
class DeliveryCrewUsersView(generics.ListCreateAPIView):
    """
    GET: Returns all delivery crew members
    POST: Assigns user to delivery crew group
    """
    serializer_class = UserSerializer
    permission_classes = [IsManager]
    
    def get_queryset(self):
        delivery_group, created = Group.objects.get_or_create(name='Delivery Crew')
        return delivery_group.user_set.all()
    
    def create(self, request, *args, **kwargs):
        username = request.data.get('username')
        if not username:
            return Response({'error': 'Username required'}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            user = User.objects.get(username=username)
            delivery_group, created = Group.objects.get_or_create(name='Delivery Crew')
            delivery_group.user_set.add(user)
            return Response({'message': f'User {username} added to delivery crew'}, status=status.HTTP_201_CREATED)
        except User.DoesNotExist:
            return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)


@extend_schema_view(
    delete=extend_schema(
        summary="Remove user from delivery crew group",
        tags=["User Groups"],
        responses={200: {"description": "Success"}, 404: {"description": "User not found"}}
    ),
)
class DeliveryCrewUserDetailView(generics.DestroyAPIView):
    """
    DELETE: Removes user from delivery crew group
    """
    queryset = User.objects.all()
    permission_classes = [IsManager]
    lookup_field = 'pk'
    lookup_url_kwarg = 'user_id'
    
    def destroy(self, request, *args, **kwargs):
        try:
            user = self.get_object()
            delivery_group = Group.objects.get(name='Delivery Crew')
            delivery_group.user_set.remove(user)
            return Response({'message': f'User {user.username} removed from delivery crew'}, status=status.HTTP_200_OK)
        except User.DoesNotExist:
            return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)


# Cart Management Views
@extend_schema_view(
    get=extend_schema(
        summary="List current user's cart items",
        tags=["Cart"],
        responses={200: CartSerializer(many=True)}
    ),
    post=extend_schema(
        summary="Add menu item to cart",
        tags=["Cart"],
        request=CartSerializer,
        responses={201: CartSerializer}
    ),
    delete=extend_schema(
        summary="Clear all cart items for current user",
        tags=["Cart"],
        responses={200: {"description": "Cart cleared"}}
    ),
)
class CartView(generics.ListCreateAPIView):
    """
    GET: Returns current items in the cart for the current user token
    POST: Adds the menu item to the cart. Sets the authenticated user as the user id for these cart items
    DELETE: Deletes all menu items created by the current user token
    """
    serializer_class = CartSerializer
    permission_classes = [IsCustomer]
    
    def get_queryset(self):
        return Cart.objects.filter(user=self.request.user)
    
    def delete(self, request, *args, **kwargs):
        Cart.objects.filter(user=request.user).delete()
        return Response({'message': 'All cart items deleted'}, status=status.HTTP_200_OK)


# Order Management Views
@extend_schema_view(
    get=extend_schema(
        summary="List orders for current user",
        tags=["Orders"],
        responses={200: OrderSerializer(many=True)}
    ),
    post=extend_schema(
        summary="Create order from cart items",
        tags=["Orders"],
        responses={201: OrderSerializer}
    ),
)
class CustomerOrdersView(generics.ListCreateAPIView):
    """
    GET: Returns all orders with order items created by this user
    POST: Creates a new order from current cart items, then clears cart
    """
    serializer_class = OrderSerializer
    permission_classes = [IsCustomer]
    
    def get_queryset(self):
        return Order.objects.filter(user=self.request.user)
    
    def create(self, request, *args, **kwargs):
        # Get current cart items
        cart_items = Cart.objects.filter(user=request.user)
        
        if not cart_items.exists():
            return Response({'error': 'Cart is empty'}, status=status.HTTP_400_BAD_REQUEST)
        
        # Calculate total
        total = sum(item.price for item in cart_items)
        
        # Create order
        order = Order.objects.create(
            user=request.user,
            total=total
        )
        
        # Create order items from cart items
        for cart_item in cart_items:
            OrderItem.objects.create(
                order=order,
                menuitem=cart_item.menuitem,
                quantity=cart_item.quantity,
                unit_price=cart_item.unit_price,
                price=cart_item.price
            )
        
        # Clear cart
        cart_items.delete()
        
        serializer = self.get_serializer(order)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


@extend_schema_view(
    get=extend_schema(
        summary="Get specific order for current user",
        tags=["Orders"],
        responses={200: OrderSerializer}
    ),
)
class CustomerOrderDetailView(generics.RetrieveAPIView):
    """
    GET: Returns all items for this order id. If the order doesn't belong to current user, returns 404
    """
    serializer_class = OrderSerializer
    permission_classes = [IsCustomer]
    
    def get_queryset(self):
        return Order.objects.filter(user=self.request.user)


@extend_schema_view(
    get=extend_schema(
        summary="List all orders (Manager only)",
        tags=["Orders"],
        responses={200: OrderSerializer(many=True)}
    ),
)
class ManagerOrdersView(generics.ListAPIView):
    """
    GET: Returns all orders with order items by all users
    """
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    permission_classes = [IsManager]


@extend_schema_view(
    get=extend_schema(
        summary="Get specific order (Manager only)",
        tags=["Orders"],
        responses={200: OrderSerializer}
    ),
    patch=extend_schema(
        summary="Update order - assign delivery crew, update status (Manager only)",
        tags=["Orders"],
        responses={200: OrderSerializer}
    ),
    delete=extend_schema(
        summary="Delete order (Manager only)",
        tags=["Orders"],
        responses={204: {"description": "Order deleted"}}
    ),
)
class ManagerOrderDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    GET: Get single order
    PATCH/PUT: Update order - assign delivery crew, update status
    DELETE: Delete order
    """
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    permission_classes = [IsManager]
    
    def update(self, request, *args, **kwargs):
        order = self.get_object()
        
        # Manager can update delivery_crew and status
        if 'delivery_crew' in request.data:
            delivery_crew_id = request.data.get('delivery_crew')
            if delivery_crew_id:
                try:
                    delivery_crew = User.objects.get(id=delivery_crew_id)
                    # Verify user is in delivery crew group
                    if not delivery_crew.groups.filter(name='Delivery Crew').exists():
                        return Response({'error': 'User is not in Delivery Crew group'}, status=status.HTTP_400_BAD_REQUEST)
                    order.delivery_crew = delivery_crew
                except User.DoesNotExist:
                    return Response({'error': 'Delivery crew user not found'}, status=status.HTTP_404_NOT_FOUND)
            else:
                order.delivery_crew = None
        
        if 'status' in request.data:
            order.status = request.data.get('status')
        
        order.save()
        serializer = self.get_serializer(order)
        return Response(serializer.data)


@extend_schema_view(
    get=extend_schema(
        summary="List orders assigned to delivery crew",
        tags=["Orders"],
        responses={200: OrderSerializer(many=True)}
    ),
)
class DeliveryCrewOrdersView(generics.ListAPIView):
    """
    GET: Returns all orders assigned to this delivery crew member
    """
    serializer_class = OrderSerializer
    permission_classes = [IsDeliveryCrew]
    
    def get_queryset(self):
        return Order.objects.filter(delivery_crew=self.request.user)


@extend_schema_view(
    patch=extend_schema(
        summary="Update order status (Delivery Crew only)",
        tags=["Orders"],
        responses={200: OrderSerializer}
    ),
)
class DeliveryCrewOrderDetailView(generics.UpdateAPIView):
    """
    PATCH: Update order status to 0 (out for delivery) or 1 (delivered)
    Delivery crew can only update status, nothing else
    """
    serializer_class = OrderSerializer
    permission_classes = [IsDeliveryCrew]
    
    def get_queryset(self):
        return Order.objects.filter(delivery_crew=self.request.user)
    
    def update(self, request, *args, **kwargs):
        order = self.get_object()
        
        # Delivery crew can only update status
        if 'status' in request.data:
            status_value = request.data.get('status')
            if status_value in [0, 1, '0', '1']:
                order.status = int(status_value)
                order.save()
                serializer = self.get_serializer(order)
                return Response(serializer.data)
            else:
                return Response({'error': 'Status must be 0 or 1'}, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({'error': 'Only status can be updated'}, status=status.HTTP_400_BAD_REQUEST)


# Item of the Day Management
@extend_schema_view(
    get=extend_schema(
        summary="Get current item of the day",
        tags=["Item of the Day"],
        responses={200: MenuItemSerializer}
    ),
    patch=extend_schema(
        summary="Set item of the day (Manager only)",
        tags=["Item of the Day"],
        request={"type": "object", "properties": {"menu_item_id": {"type": "integer"}}},
        responses={200: MenuItemSerializer}
    ),
)
class ItemOfTheDayView(generics.GenericAPIView):
    """
    GET: Returns the current item of the day
    PATCH: Sets a new item of the day (Manager only)
    """
    serializer_class = MenuItemSerializer
    
    def get_permissions(self):
        if self.request.method == 'GET':
            return []  # Anyone can view item of the day
        else:
            return [IsManager()]  # Only managers can update
    
    def get(self, request, *args, **kwargs):
        try:
            item_of_day = MenuItem.objects.get(item_of_the_day=True)
            serializer = self.get_serializer(item_of_day)
            return Response(serializer.data)
        except MenuItem.DoesNotExist:
            return Response({'message': 'No item of the day set'}, status=status.HTTP_404_NOT_FOUND)
    
    def patch(self, request, *args, **kwargs):
        menu_item_id = request.data.get('menu_item_id')
        
        if not menu_item_id:
            return Response({'error': 'menu_item_id is required'}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            # Clear current item of the day
            MenuItem.objects.filter(item_of_the_day=True).update(item_of_the_day=False)
            
            # Set new item of the day
            menu_item = MenuItem.objects.get(id=menu_item_id)
            menu_item.item_of_the_day = True
            menu_item.save()
            
            serializer = self.get_serializer(menu_item)
            return Response(serializer.data)
        except MenuItem.DoesNotExist:
            return Response({'error': 'Menu item not found'}, status=status.HTTP_404_NOT_FOUND)