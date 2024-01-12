from django.urls import path, include
from . import views
from .views import *
from rest_framework.routers import SimpleRouter, DefaultRouter
from pprint import pprint
from rest_framework_nested import routers


router = routers.DefaultRouter()
router.register('products', views.ProductViewSet, basename="products")
router.register('collections', views.CollectionViewSet)
router.register('carts', views.CartViewSet)
router.register('customers', views.CustomerViewSet, basename="customer")
router.register('orders', views.OrderViewSet, basename="orders")

sukesk_router = path('sukesh/', Sukesh.as_view())

products_router = routers.NestedDefaultRouter(router, "products", lookup="product")
products_router.register("reviews", views.ReviewViewSet, basename="product-reviews")
cartitem_router = routers.NestedDefaultRouter(router, "carts", lookup="cart")
cartitem_router.register("items", views.CartItemViewSet, basename="cart-items")

urlpatterns = router.urls + products_router.urls + cartitem_router.urls + [sukesk_router]



# router = DefaultRouter()
# router.register('products', views.ProductViewSet)
# router.register('collections', views.CollectionViewSet)

# urlpatterns = router.urls

# router = SimpleRouter()
# router.register('products', views.ProductViewSet)
# router.register('collections', views.CollectionViewSet)
# # pprint(router.urls)

# urlpatterns = router.urls

# urlpatterns = [                       # To set specific / customized router
#     path('', include(router.urls))
# ]



# urlpatterns = [

# ]

# urlpatterns = [
#     path('products/', ProductList.as_view()),
#     # path('product-details/<int:id>', ProductDetail.as_view()),    #if use id, then set lookup_field in serializer
#     path('products/<int:pk>', ProductDetail.as_view()),
#     path('collections/', CollectionList.as_view()),
#     path('collections/<int:pk>', CollectionDetail.as_view(), name="collection-detail")
# ]

# # URLConf
# urlpatterns = [
#     path('products/', views.product_list),
#     path('product-details/<int:pk>', views.product_details),
#     path('collections/', views.collection_list),
#     path('collection-details/<int:pk>', views.collection_details, name="collection-detail")
# ]
