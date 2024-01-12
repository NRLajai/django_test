from django.shortcuts import render, get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from django.http import HttpResponse
from django.db.models.aggregates import Count
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticated, AllowAny, IsAdminUser, DjangoModelPermissions
from rest_framework.decorators import action
from rest_framework.decorators import api_view
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.mixins import CreateModelMixin, RetrieveModelMixin, DestroyModelMixin, ListModelMixin, UpdateModelMixin
from rest_framework.viewsets import GenericViewSet
from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView
from rest_framework.viewsets import ModelViewSet
from rest_framework import status
from .models import *
from .serializers import *
from .filters import ProductFilter
from .pagination import DefaultPagination
from .permissions import *



class Sukesh(APIView):
    def get(self, request):
        return Response("hey its me sukesh.")


class ProductViewSet(ModelViewSet):
    queryset = Product.objects.select_related("collection").all()
    serializer_class = ProductSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]       
    # filterset_fields = ["collection_id", "unit_price"]    # default filter
    filterset_class = ProductFilter
    # pagination_class = PageNumberPagination               # Pagination only to this view
    pagination_class = DefaultPagination
    permission_classes = [IsAdminOrReadOnly]
    search_fields =  ["title", "description"]
    ordering_fields = ["unit_price", "last_update"]

    # def get_queryset(self):                                              #manunall filtering
    #     queryset = Product.objects.select_related("collection").all()
    #     collection_id = self.request.query_params.get("collection_id")
    #     if collection_id is not None:
    #         queryset = queryset.filter(collection_id=collection_id)
    #     return queryset

    def get_serializer_context(self):
        return {"request": self.request}
    
    def destroy(self, request, *args, **kwargs):
        if OrderItem.objects.filter(product_id=kwargs['pk']).count() > 0:
            return Response({'error': "Product cannot be deleted, because it linked to product item"}, status=status.HTTP_405_METHOD_NOT_ALLOWED)
        return super().destroy(request, *args, **kwargs)

    # def delete(self, request, pk):                    # this func shows delete btn in product list, to override this, we use destroy()
    #     product = get_object_or_404(Product, pk=pk)
    #     if product.orderitems.count() > 0:
    #         return Response({'error': "Product cannot be deleted, because it linked to product item"}, status=status.HTTP_405_METHOD_NOT_ALLOWED)
    #     product.delete()
    #     return Response(status=status.HTTP_204_NO_CONTENT)
    

class CollectionViewSet(ModelViewSet):
    queryset = Collection.objects.annotate(products_count=Count("products")).all()
    serializer_class = CollectionSerializer
    permission_classes = [IsAdminOrReadOnly]

    def destroy(self, request, *args, **kwargs):
        if Product.objects.filter(collection_id=kwargs['pk']).count() > 0:
            return Response({'error': "Colelction cannot be deleted, because it has more than one product"}, status=status.HTTP_405_METHOD_NOT_ALLOWED)
        return super().destroy(request, *args, **kwargs)

    # def delete(self, request, pk):
    #     collection = get_object_or_404(Collection.objects.annotate(products_count=Count("products")).all(), pk=pk)
    #     if collection.products.count() > 0:
    #         return Response({'error': "Colelction cannot be deleted, because it has more than one product"}, status=status.HTTP_405_METHOD_NOT_ALLOWED)
    #     collection.delete()
    #     return Response(status=status.HTTP_204_NO_CONTENT)


class ReviewViewSet(ModelViewSet):
    # queryset = Review.objects.all()
    serializer_class = ReviewSerializer

    def get_queryset(self):
        return Review.objects.filter(product_id=self.kwargs["product_pk"])        

    def get_serializer_context(self):
        return {"product_id": self.kwargs["product_pk"]}


class CartViewSet(CreateModelMixin, RetrieveModelMixin, DestroyModelMixin, GenericViewSet):
    queryset = Cart.objects.prefetch_related("items__product").all()
    serializer_class = CartSerializer


class CartItemViewSet(ModelViewSet):
    http_method_names = ["get", "post", "patch", "delete"]

    # serializer_class = CartItemSerializer

    def get_queryset(self):
        return CartItem.objects \
            .filter(cart_id=self.kwargs["cart_pk"])\
            .select_related("product")
    
    def get_serializer_context(self):
        return {"cart_id": self.kwargs["cart_pk"]}
    
    def get_serializer_class(self):
        if self.request.method == "POST":
            return AddCartItemSerializer
        elif self.request.method == "PATCH":
            return UpdateCartItemSerializer
        return CartItemSerializer

    
# class CustomerViewSet(CreateModelMixin, RetrieveModelMixin, UpdateModelMixin, GenericViewSet):
class CustomerViewSet(ModelViewSet):
    queryset = Customer.objects.all()
    serializer_class = CustomerSerializer
    permission_classes=[IsAdminUser]

    # def get_permissions(self):
    #     if self.request.method == "GET":
    #         return [AllowAny()]
    #     return [IsAuthenticated()]

    @action(detail=True, permission_classes=[ViewCustomerHistoryPermissions])
    def history(self, request, pk):
        return Response("ok")

    @action(detail=False, methods=["GET", "PUT"], permission_classes=[IsAuthenticated])
    # @action(detail=False, methods=["GET", "PUT"])           # detail = False, action available in list view [localhost/customers/me]
    def me(self, request):                                    # detail = True, action available in detail view [localhost/customers/1/me]
        # customer, created = Customer.objects.get_or_create(user_id=request.user.id)
        customer = Customer.objects.get(user_id=request.user.id)        # instead create customer in query, we use signal to create customer
        if request.method == "GET":
            serializer = CustomerSerializer(customer)
        elif request.method == "PUT":
            serializer = CustomerSerializer(customer, data=request.data)
            serializer.is_valid(raise_exception=True)
            serializer.save()
        return Response(serializer.data)


class OrderViewSet(ModelViewSet):
    http_method_names = ["get", "post", "patch", "delete", "head", "options"]

    def get_permissions(self):
        if self.request.method in ["PATCH", "DELETE"]:
            return [IsAdminUser()]
        return [IsAuthenticated()]
    
    def get_serializer_class(self):
        if self.request.method == 'POST':
            return CreateOrderSerializer
        elif self.request.method == 'PATCH':
            return UpdateOrderSerializer
        return OrderSerializer

    # def get_serializer_context(self):
    #     return {"user_id": self.request.user.id} 
    
    def get_queryset(self):
        user = self.request.user

        if user.is_staff:
            return Order.objects.all()
        
        # (customer_id, created) = Customer.objects.only("id").get_or_create(user_id=user.id)
        customer_id = Customer.objects.only("id").get(user_id=user.id)       # instead create customer in query, we use signal to create customer
        return Order.objects.filter(customer_id=customer_id)

    def create(self, request, *args, **kwargs):                 # to return response, we override create(), instead directly use save()
        serializer = CreateOrderSerializer(
                        data=request.data, 
                        context={"user_id": self.request.user.id})
        serializer.is_valid(raise_exception=True)
        order = serializer.save()
        serializer = OrderSerializer(order)
        return Response(serializer.data)


# class ProductList(ListCreateAPIView):
#     queryset = Product.objects.select_related("collection").all()
#     serializer_class = ProductSerializer

#     # def get_query(self):
#     #     return Product.objects.select_related("collection").all()
    
#     # def get_serializer_class(self):
#     #     return ProductSerializer
    
#     def get_serializer_context(self):
#         return {"request": self.request}
    

# class ProductDetail(RetrieveUpdateDestroyAPIView):
#     queryset = Product.objects.all()
#     serializer_class = ProductSerializer
#     # lookup_field = "id"          # in url , if it has id, then set this field
    
#     def delete(self, request, pk):
#         product = get_object_or_404(Product, pk=pk)
#         if product.orderitems.count() > 0:
#             return Response({'error': "Product cannot be deleted, because it linked to product item"}, status=status.HTTP_405_METHOD_NOT_ALLOWED)
#         product.delete()
#         return Response(status=status.HTTP_204_NO_CONTENT)


# class CollectionList(ListCreateAPIView):
#     queryset = Collection.objects.annotate(products_count=Count("products")).all()
#     serializer_class = CollectionSerializer

#     # def get_query(self):
#     #     return Collection.objects.annotate(products_count=Count("products")).all()
    
#     # def get_serializer_class(self):
#     #     return CollectionSerializer

# class CollectionDetail(RetrieveUpdateDestroyAPIView):
#     queryset = Collection.objects.annotate(products_count=Count("products")).all()
#     serializer_class = CollectionSerializer

#     def delete(self, request, pk):
#         collection = get_object_or_404(Collection.objects.annotate(products_count=Count("products")).all(), pk=pk)
#         if collection.products.count() > 0:
#             return Response({'error': "Colelction cannot be deleted, because it has more than one product"}, status=status.HTTP_405_METHOD_NOT_ALLOWED)
#         collection.delete()
#         return Response(status=status.HTTP_204_NO_CONTENT)
    

# class CollectionList(APIView):
#     def get(self, request):
#         queryset = Collection.objects.annotate(products_count=Count("products")).all()
#         serializer = CollectionSerializer(queryset, many=True)
#         return Response(serializer.data)
    
#     def post(self, request):
#         serializer = CollectionSerializer(data=request.data)            
#         serializer.is_valid(raise_exception=True)
#         serializer.save()
#         return Response(serializer.data, status=status.HTTP_201_CREATED)


# class CollectionDetail(APIView):
#     def get(self, request, id):
#         collection = get_object_or_404(Collection.objects.annotate(products_count=Count("products")).all(), pk=id)
#         serializer = CollectionSerializer(collection)
#         return Response(serializer.data)

#     def put(self, request, id):
#         collection = get_object_or_404(Collection.objects.annotate(products_count=Count("products")).all(), pk=id)
#         serializer = CollectionSerializer(collection, data=request.data)
#         serializer.is_valid(raise_exception=True)
#         serializer.save()               
#         return Response(serializer.data, status=status.HTTP_200_OK)
    
#     def delete(self, request, id):
#         collection = get_object_or_404(Collection.objects.annotate(products_count=Count("products")).all(), pk=id)
#         if collection.products.count() > 0:
#             return Response({'error': "Colelction cannot be deleted, because it has more than one product"}, status=status.HTTP_405_METHOD_NOT_ALLOWED)
#         collection.delete()
#         return Response(status=status.HTTP_204_NO_CONTENT)



# class ProductList(APIView):
#     def get(self, request):
#         queryset = Product.objects.select_related("collection").all()
#         serializer = ProductSerializer(queryset, many=True, context={"request": request})
#         return Response(serializer.data)
    
#     def post(self, request):
#         serializer = ProductSerializer(data=request.data)        
#         serializer.is_valid(raise_exception=True)
#         serializer.save()
#         return Response(serializer.data, status=status.HTTP_201_CREATED)
    

# class ProductDetail(APIView):
#     def get(self, request, id):
#         product = get_object_or_404(Product, pk=id)
#         serializer = ProductSerializer(product)
#         return Response(serializer.data)    
    
#     def put(self, request, id):
#         product = get_object_or_404(Product, pk=id)
#         serializer = ProductSerializer(product, data=request.data)
#         serializer.is_valid(raise_exception=True)
#         serializer.save()               
#         return Response(serializer.data, status=status.HTTP_200_OK)
    
#     def delete(self, request, id):
#         product = get_object_or_404(Product, pk=id)
#         if product.orderitems.count() > 0:
#             return Response({'error': "Product cannot be deleted, because it linked to product item"}, status=status.HTTP_405_METHOD_NOT_ALLOWED)
#         product.delete()
#         return Response(status=status.HTTP_204_NO_CONTENT)
        
        
# @api_view(['GET', 'POST'])
# def collection_list(request):
#     if request.method == "GET":
#         queryset = Collection.objects.annotate(products_count=Count("products")).all()
#         serializer = CollectionSerializer(queryset, many=True)
#         return Response(serializer.data)
    
#     elif request.method == "POST":
#         serializer = CollectionSerializer(data=request.data)        
#         # if serializer.is_valid():
#         #     serializer.validated_data            
#         #     return Response(serializer.validated_data)
#         # else:
#         #     return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
#         serializer.is_valid(raise_exception=True)
#         serializer.save()
#         # serializer.validated_data
#         return Response(serializer.data, status=status.HTTP_201_CREATED)


# @api_view(["GET", "PUT", "DELETE"])
# def collection_details(request, id):
#     collection = get_object_or_404(Collection.objects.annotate(products_count=Count("products")).all(), pk=id)

#     if request.method == "GET":
#         serializer = CollectionSerializer(collection)
#         return Response(serializer.data)
#     elif request.method == "PUT":
#         serializer = CollectionSerializer(collection, data=request.data)
#         serializer.is_valid(raise_exception=True)
#         serializer.save()               
#         return Response(serializer.data, status=status.HTTP_200_OK)
#     elif request.method == 'DELETE':
#         if collection.products.count() > 0:
#             return Response({'error': "Colelction cannot be deleted, because it has more than one product"}, status=status.HTTP_405_METHOD_NOT_ALLOWED)
#         collection.delete()
#         return Response(status=status.HTTP_204_NO_CONTENT)


# @api_view(['GET', 'POST'])
# def product_list(request):
#     if request.method == "GET":
#         queryset = Product.objects.select_related("collection").all()
#         serializer = ProductSerializer(queryset, many=True, context={"request": request})
#         return Response(serializer.data)
    
#     elif request.method == "POST":
#         serializer = ProductSerializer(data=request.data)        
#         # if serializer.is_valid():
#         #     serializer.validated_data            
#         #     return Response(serializer.validated_data)
#         # else:
#         #     return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
#         serializer.is_valid(raise_exception=True)
#         serializer.save()
#         # serializer.validated_data
#         return Response(serializer.data, status=status.HTTP_201_CREATED)


# @api_view(["GET", "PUT", "DELETE"])
# def product_details(request, pk):
#     product = get_object_or_404(Product, pk=pk)

#     if request.method == "GET":
#         serializer = ProductSerializer(product)
#         return Response(serializer.data)
#     elif request.method == "PUT":
#         serializer = ProductSerializer(product, data=request.data)
#         serializer.is_valid(raise_exception=True)
#         serializer.save()               
#         return Response(serializer.data, status=status.HTTP_200_OK)
#     elif request.method == 'DELETE':
#         if product.orderitems.count() > 0:
#             return Response({'error': "Product cannot be deleted, because it linked to product item"}, status=status.HTTP_405_METHOD_NOT_ALLOWED)
#         product.delete()
#         return Response(status=status.HTTP_204_NO_CONTENT)


# @api_view()
# def product_list(request):
#     queryset = Product.objects.select_related("collection").all()
#     serializer = ProductSerializer(queryset, many=True, context={"request": request})
#     return Response(serializer.data)


# @api_view()
# def product_details(request, id):
#     product = get_object_or_404(Product, pk=id)
#     serializer = ProductSerializer(product)
#     return Response(serializer.data)


# @api_view()
# def collection_details(request, pk):
#     collection = get_object_or_404(Collection, pk=pk)
#     serializer = CollectionSerializer(collection)
#     return Response(serializer.data)
