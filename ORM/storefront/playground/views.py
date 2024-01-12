from django.shortcuts import render
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Q, F, Value
from django.db.models.aggregates import Count, Max, Min, Avg, Sum
from store.models import *


def say_hello(request):
    # queryset = Product.objects.filter(unit_price__range=(20, 30))
    # queryset = Product.objects.all()[:5]
    # return render(request, 'hello.html', {'name': 'Mosh', 'products': list(queryset)})
    # products = Product.objects.values('id', 'title', 'orderitem__id').order_by('title')
    # products = OrderItem.objects.select_related('order', 'product').values('order__customer', 'product_id', 'product__title')
    orders = Order.objects.select_related('customer').order_by('-placed_at')[:5]
    return render(request, 'hello.html', {'name': 'Mosh', 'products': list(orders)})


def say_hello_old(request):
    pass
    # queryset = Customer.objects.annotate(is_new=Value(True)) 
    # queryset = Customer.objects.annotate(new_id= F('id') + 1 )
    # return render(request, 'hello.html', {'name': 'Mosh', "products": list(queryset)})
    
    # 4
    # query_set = Product.objects.count()
    
    # 5
    # exists = Product.objects.filter(pk=0).exists()
    
    # 6
    # queryset = Product.objects.filter(unit_price__range=(20, 30))
    # queryset = Product.objects.filter(collection__id__range=(1, 30))
    # queryset = Product.objects.filter(title__icontains="coffee")
    # queryset = Product.objects.filter(last_update__year=2021)    
    # return render(request, 'hello.html', {'name': 'Mosh', "products": list(queryset)})

    # 7
    # PRODUCTS: inventory < 10 AND unit_price < 20 
    # queryset = Product.objects.filter(inventory__lt=10, unit_price__lt=20)
    # queryset = Product.objects.filter(inventory__lt=10).filter(unit_price__lt=20)
    # queryset = Product.objects.filter(Q(inventory__lt=10) & ~Q(unit_price__lt=20))
    # return render(request, 'hello.html', {'name': 'Mosh', "products": list(queryset)})
    
    # 8
    # PRODUCTS: inventory = unit_price
    # queryset = Product.objects.filter(inventory=F('unit_price'))
    # queryset = Product.objects.filter(inventory=F('collection_id'))
    # return render(request, 'hello.html', {'name': 'Mosh', "products": list(queryset)})
    
    # 9
    # queryset = Product.objects.order_by('unit_price', '-title').reverse()
    # queryset = Product.objects.filter(collection__id=6).order_by('unit_price')
    # return render(request, 'hello.html', {'name': 'Mosh', "products": list(queryset)})
    # product = Product.objects.order_by('unit_price')[0]
    # product = Product.objects.earliest('unit_price')
    # product = Product.objects.latest('unit_price')
    # return render(request, 'hello.html', {'name': 'Mosh', "product": product})
    
    # 10
    # 0, 1, 2, 3, 4
    # 5 ,6, 7, 8, 9
    # queryset  = Product.objects.all()[:5]
    # queryset  = Product.objects.all()[5:10]
    # return render(request, 'hello.html', {'name': 'Mosh', "products": list(queryset)})
    
    # 11
    # queryset  = Product.objects.values('id', 'title', 'collection__title')         # dictionary
    # queryset  = Product.objects.values_list('id', 'title', 'collection__title')      # tuples
    
    # # Select products that have been ordered and sort them by title
    # queryset = Product.objects.filter(id__in=OrderItem.objects.values('product_id').distinct()).order_by('title')
    # return render(request, 'hello.html', {'name': 'Mosh', "products": list(queryset)})
    
    
    # 12
    # queryset  = Product.objects.only('id', 'title')         # instances
    
    # PROBLEM: because it returns instances, if u try to get any fields that are not in selected, Will result tons of queries
    # return render(request, 'hello.html', {'name': 'Mosh', "products": list(queryset)})

    # Opposite of only is defer, it returns all fields except selected, if u try to get any fields that are not in selected, Will result tons of queries
    # queryset  = Product.objects.defer('description')         # instances
    # return render(request, 'hello.html', {'name': 'Mosh', "products": list(queryset)})
    
    
    # 13
    # select_related (1) (ForeignKeyField)
    # prefetch_related (n) (ManyToManyField)
    
    # queryset  = Product.objects.select_related('collection__someOtherField').all()
    # queryset  = Product.objects.prefetch_related('promotions').all()
    # queryset  = Product.objects.prefetch_related('promotions').select_related('collection').all()
    # return render(request, 'hello.html', {'name': 'Mosh', "products": list(queryset)})
    
    # GET the last 5 records with their customer and items (incl product)
    # queryset = Order.objects.select_related('customer').order_by('-placed_at')[:5].prefetch_related('orderitem_set__product')
    # return render(request, 'hello.html', {'name': 'Mosh', "orders": list(queryset)})
    
    
    # 14
    # result = Product.objects.aggregate(count = Count('id'), min_price = Min('unit_price'))        #dictionary
    # result = Product.objects.filter(collection__id=1).aggregate(count = Count('id'), min_price = Min('unit_price'))
    # return render(request, 'hello.html', {'name': 'Mosh', "result": result })
    
    # 15
    # queryset = Customer.objects.annotate(is_new=Value(True)) 
    # queryset = Customer.objects.annotate(new_id= F('id') + 1 )
    # return render(request, 'hello.html', {'name': 'Mosh', "products": list(queryset)})