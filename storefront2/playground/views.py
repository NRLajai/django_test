from django.shortcuts import render
from store.models import *
from django.db.models.aggregates import Count

# def say_hello(request):
#     queryset = Product.objects.filter(
#         id__in=OrderItem.objects.values('product_id').distinct()).order_by('title')
#     return render(request, 'hello.html', {'name': 'Mosh', 'products': queryset})

def say_hello(request):
    queryset = Product.objects.filter(id__in=OrderItem.objects.values('product_id').distinct())
    # queryset = Product.objects.prefetch_related('promotions').select_related('collection').all()
    # queryset = Order.objects.select_related('customer').prefetch_related('orderitem_set__product').order_by('-placed_at')[:5]
    return render(request, 'hello.html', {'name': 'Mosh', 'products': list(queryset)})
    # return render(request, 'hello.html', {'name': 'Mosh'})
