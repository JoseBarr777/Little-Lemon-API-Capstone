from django.urls import path

from . import views

app_name = "littlelemon"

urlpatterns = [
    
    # category endpoints (for testing)
    path("categories/", views.CategoryListCreateView.as_view(), name="categories"),
    path("categories/<int:pk>/", views.CategoryDetailView.as_view(), name="category-detail"),
    
    
    # menu-items endpoints
    path("menu-items/", views.MenuItemListCreateView.as_view(), name="menu-item"),
    path("menu-items/<int:pk>/", views.MenuItemDetailView.as_view(), name="menu-item-detail"),
    
    # user group management endpoints
    # path('groups/managers/users/',)
    # path('groups/managers/users/<int:pk>/',)
    # path('groups/delivery-crew/users/',)
    # path('groups/delivery-crew/users/<int:pk>/',)
    
    # cart management endpoints
    # path('cart/menu-items/,')
    
    # order management endpoints
    # path('orders/,')
    # path('orders/<int:pk>/,')
    
    
]
