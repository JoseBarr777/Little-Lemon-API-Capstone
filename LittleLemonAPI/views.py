from django.shortcuts import render

from rest_framework import generics
from django_filters import FilterSet, filters
from django_filters.rest_framework import DjangoFilterBackend

from .models import Category, MenuItem
from .serializers import CategorySerializer, MenuItemSerializer
from .permissions import IsManagerOrReadOnly

from rest_framework.permissions import IsAuthenticated

# Create your views here.

class CategoryListCreateView(generics.ListCreateAPIView):
    """
    GET: List categories (paginated, ordered by id).
    POST: Create a category with fields: slug, title.
    """
    queryset = Category.objects.all().order_by("id")
    serializer_class = CategorySerializer
    permission_classes = [IsAuthenticated ,IsManagerOrReadOnly]


class CategoryDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    GET: Retrieve one category.
    PATCH/PUT: Update fields.
    DELETE: Remove the category.
    """
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [IsAuthenticated ,IsManagerOrReadOnly]
    

class MenuItemFilter(FilterSet):
    category = filters.NumberFilter(field_name="category_id")
    category_slug = filters.CharFilter(field_name="category__slug", lookup_expr="iexact")
    featured = filters.BooleanFilter()
    price_min = filters.NumberFilter(field_name="price", lookup_expr="gte")
    price_max = filters.NumberFilter(field_name="price", lookup_expr="lte")

    class Meta:
        model = MenuItem
        fields = ["category", "category_slug", "featured", "price_min", "price_max"]

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
    permission_classes = [IsAuthenticated, IsManagerOrReadOnly]
    
class MenuItemDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    GET: Retrieve one menu item.
    PATCH/PUT: Update fields.
    DELETE: Remove the item.
    """
    queryset = MenuItem.objects.all()
    serializer_class = MenuItemSerializer
    permission_classes =[IsAuthenticated, IsManagerOrReadOnly]
    