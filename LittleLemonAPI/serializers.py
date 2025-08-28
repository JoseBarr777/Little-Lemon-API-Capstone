from rest_framework import serializers

from .models import Category, MenuItem, Cart, Order, OrderItem
from django.contrib.auth.models import User

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'slug', 'title']

class MenuItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = MenuItem
        fields = ['id', 'title', 'price', 'category', 'featured', 'item_of_the_day']
        
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name']
        read_only_fields = ['id']

class CartSerializer(serializers.ModelSerializer):
    menuitem_title = serializers.CharField(source='menuitem.title', read_only=True)
    
    class Meta:
        model = Cart
        fields = ['id', 'menuitem', 'menuitem_title', 'quantity', 'unit_price', 'price']
        read_only_fields = ['id', 'unit_price', 'price', 'menuitem_title']
        
    def create(self, validated_data):
        # Set the user to the current authenticated user
        validated_data['user'] = self.context['request'].user
        
        # Auto-calculate unit_price and total price from menuitem
        menuitem = validated_data['menuitem']
        quantity = validated_data['quantity']
        
        validated_data['unit_price'] = menuitem.price
        validated_data['price'] = menuitem.price * quantity
        
        return super().create(validated_data)

class OrderItemSerializer(serializers.ModelSerializer):
    menuitem_title = serializers.CharField(source='menuitem.title', read_only=True)
    
    class Meta:
        model = OrderItem
        fields = ['id', 'menuitem', 'menuitem_title', 'quantity', 'unit_price', 'price']
        read_only_fields = ['id', 'menuitem_title']

class OrderSerializer(serializers.ModelSerializer):
    order_items = OrderItemSerializer(source='orderitem_set', many=True, read_only=True)
    user_username = serializers.CharField(source='user.username', read_only=True)
    delivery_crew_username = serializers.CharField(source='delivery_crew.username', read_only=True)
    
    class Meta:
        model = Order
        fields = ['id', 'user', 'user_username', 'delivery_crew', 'delivery_crew_username', 'status', 'total', 'date', 'order_items']
        read_only_fields = ['id', 'user', 'user_username', 'delivery_crew_username', 'total', 'date', 'order_items']