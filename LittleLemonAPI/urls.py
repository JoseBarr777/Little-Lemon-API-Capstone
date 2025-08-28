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
    path('groups/manager/users/', views.ManagerUsersView.as_view(), name="manager-users"),
    path('groups/manager/users/<int:user_id>/', views.ManagerUserDetailView.as_view(), name="manager-user-detail"),
    path('groups/delivery-crew/users/', views.DeliveryCrewUsersView.as_view(), name="delivery-crew-users"),
    path('groups/delivery-crew/users/<int:user_id>/', views.DeliveryCrewUserDetailView.as_view(), name="delivery-crew-user-detail"),
    
    # cart management endpoints
    path('cart/menu-items/', views.CartView.as_view(), name="cart-menu-items"),
    
    # order management endpoints - Customer
    path('orders/', views.CustomerOrdersView.as_view(), name="customer-orders"),
    path('orders/<int:pk>/', views.CustomerOrderDetailView.as_view(), name="customer-order-detail"),
    
    # order management endpoints - Manager  
    path('orders/manager/', views.ManagerOrdersView.as_view(), name="manager-orders"),
    path('orders/manager/<int:pk>/', views.ManagerOrderDetailView.as_view(), name="manager-order-detail"),
    
    # order management endpoints - Delivery Crew
    path('orders/delivery/', views.DeliveryCrewOrdersView.as_view(), name="delivery-crew-orders"),
    path('orders/delivery/<int:pk>/', views.DeliveryCrewOrderDetailView.as_view(), name="delivery-crew-order-detail"),
    
    # item of the day
    path('item-of-the-day/', views.ItemOfTheDayView.as_view(), name="item-of-the-day"),
    
    
]
