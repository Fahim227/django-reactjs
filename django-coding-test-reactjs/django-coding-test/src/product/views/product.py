from typing import Any
from django import http
from django.views import generic
from django.views.generic import TemplateView, View
from product.models import Variant
from product.models import *
from django.db.models import Sum,Count
from django.views.decorators.csrf import requires_csrf_token,ensure_csrf_cookie
from django.utils.decorators import method_decorator
from django.http import HttpResponse
import json


def createProduct(request):
    print(request.method)
    print("createProduct=======")
    response_data= {}
    response_data['isSuccess'] = True
    response_data['message'] = 'Success'
    return HttpResponse(json.dumps(response_data), content_type="application/json")



class CreateProductView(generic.TemplateView):
    template_name = 'products/create.html'

    # @method_decorator(ensure_csrf_cookie)
    def post(self, request, *args, **kwargs):
        body = self.request.body
        # {"pName":"pName","pSku":"pSKU","pDesc":"Desc","pVariants":[{"option":1,"tags":["Tags"]}]}
        body = json.loads(body)
        print(body)
        productName = body['pName']
        productSku = body['pSku']
        productDescription = body['pDesc']
        product = Product.objects.create(title = productName,sku=productSku,description = productDescription)
        
        pVariants_list = body['pVariants']
        for variant in pVariants_list:
            if variant["option"] == 1:
                variant_title = "Size"
                variant_obj = Variant.objects.get(title = variant_title)
                for tag in variant["tags"]:
                    pVariant = ProductVariant.objects.create(variant_title = tag,variant = variant_obj,product=product)
                    # Here i did not able to run vue project and in react i was not able to
                    # to send tags wth ptice and stock 
                    # if i can get all the data i would create an new data in ProductVariantPrice here
        response_data= {}
        response_data['isSuccess'] = True
        response_data['message'] = 'Success'
        return HttpResponse(json.dumps(response_data), content_type="application/json")


    def get_context_data(self, **kwargs):
        context = super(CreateProductView, self).get_context_data(**kwargs)
        variants = Variant.objects.filter(active=True).values('id', 'title')
        context['product'] = True
        context['variants'] = list(variants.all())
        return context


class GetAllProducts(TemplateView):
    template_name='products/list.html'

    @method_decorator(ensure_csrf_cookie)
    def post(self, request, *args, **kwargs):
        context={}
        print(self.request.POST)
        title = self.request.POST['title']
        try:
            variant = self.request.POST['variant']
        except:
            variant = ''
        price_from = int(self.request.POST['price_from']) if len(self.request.POST['price_from']) != 0 else 0
        price_to = int(self.request.POST['price_to']) if len(self.request.POST['price_to']) != 0 else 0
        date = self.request.POST['date']
        # products = Product.objects.filter(title = title)
        # variants = ProductVariant.objects.filter(variant_title=variant,product__in = products)
        # vafriants_price = ProductVariantPrice.objects.filter(price__gt = price_from,price__lt = price_to,product_id__in = products,created_at__gte = date)
        all_products = []
        products = Product.objects.all()
        if len(title) != 0:
            products = Product.objects.filter(title = title)
        
        for product in products:
            data = {}
            print("product ======== {}".format(product.title))
            variants = ProductVariant.objects.select_related('variant').filter(product = product)
            data['variants'] = variants
            all_variants_prices = ProductVariantPrice.objects.filter(product=product)
            all_variants = []
            for variants_price in all_variants_prices:
                variant_dict = {}
                print(variants_price)
                if price_from != None and price_to != None:
                    if variants_price.price >= price_from and variants_price.price <= price_to :
                        if  (variants_price.product_variant_one.variant_title == variant and variants_price.product_variant_one != None) or (variants_price.product_variant_two != None and variants_price.product_variant_two.variant_title == variant) or (variants_price.product_variant_three != None and variants_price.product_variant_three.variant_title == variant):
                            var = variants_price.product_variant_one.variant_title if variants_price.product_variant_one != None else "" 
                            var+= "/"
                            var += variants_price.product_variant_two.variant_title if variants_price.product_variant_two != None else ""
                            var+= "/"
                            var += variants_price.product_variant_three.variant_title if variants_price.product_variant_three != None else "" 
                            variant_dict["variant"] = var
                            variant_dict["price"] = variants_price.price
                            variant_dict["stock"] = variants_price.stock
                            data['product'] = product
                            all_variants.append(variant_dict)
                        else:
                            var = variants_price.product_variant_one.variant_title if variants_price.product_variant_one != None else "" 
                            var+= "/"
                            var += variants_price.product_variant_two.variant_title if variants_price.product_variant_two != None else ""
                            var+= "/"
                            var += variants_price.product_variant_three.variant_title if variants_price.product_variant_three != None else "" 
                            variant_dict["variant"] = var
                            variant_dict["price"] = variants_price.price
                            variant_dict["stock"] = variants_price.stock
                            data['product'] = product
                            all_variants.append(variant_dict)
                if variant != None:
                    print("variants_price.product_variant_two.variant_title========== {}".format(variants_price.product_variant_two.variant_title))
                    if  (variants_price.product_variant_one.variant_title == variant and variants_price.product_variant_one != None) or (variants_price.product_variant_two != None and variants_price.product_variant_two.variant_title == variant) or (variants_price.product_variant_three != None and variants_price.product_variant_three.variant_title == variant):
                            var = variants_price.product_variant_one.variant_title if variants_price.product_variant_one != None else "" 
                            var+= "/"
                            var += variants_price.product_variant_two.variant_title if variants_price.product_variant_two != None else ""
                            var+= "/"
                            var += variants_price.product_variant_three.variant_title if variants_price.product_variant_three != None else "" 
                            variant_dict["variant"] = var
                            variant_dict["price"] = variants_price.price
                            variant_dict["stock"] = variants_price.stock
                            data['product'] = product
                            all_variants.append(variant_dict)
            if len(all_variants) != 0:
                data["all_variants"] = all_variants
                all_products.append(data)
            else:
                data['product'] = product
                all_products.append(data)
        all_variant = Variant.objects.all()
        drpdown_variant_list = []
        for variant in all_variant:
            drpdown_variant = {}
            drpdown_variant["variant"] = variant.title
            variant_title = {pVariant.variant_title for pVariant in  ProductVariant.objects.filter(variant = variant)}
            drpdown_variant["variant_titles"] = list(variant_title)
            drpdown_variant_list.append(drpdown_variant)
        context = {"all_data": all_products,"total_products":len(all_products),"dropdown_variant":drpdown_variant_list}
        return self.render_to_response(context)

    def get(self, request, *args, **kwargs):
        
        all_products = []
        products = Product.objects.all()
        for product in products:
            data = {
                "product": product,
            }
            variants = ProductVariant.objects.select_related('variant').filter(product = product)
            data['variants'] = variants
            all_variants_prices = ProductVariantPrice.objects.filter(product=product)
            all_variants = []
            for variants_price in all_variants_prices:
                variant = {}
                print(variants_price)
                var = variants_price.product_variant_one.variant_title if variants_price.product_variant_one != None else "" 
                var+= "/"
                var += variants_price.product_variant_two.variant_title if variants_price.product_variant_two != None else ""
                var+= "/"
                var += variants_price.product_variant_three.variant_title if variants_price.product_variant_three != None else "" 
                variant["variant"] = var
                variant["price"] = variants_price.price
                variant["stock"] = variants_price.stock
                all_variants.append(variant)
            data["all_variants"] = all_variants
            all_products.append(data)
        variant = ProductVariant.objects.select_related('product','variant').all()
        da = ProductVariant.objects.filter(variant__in = Variant.objects.all())
        all_variant = Variant.objects.all()
        drpdown_variant_list = []
        for variant in all_variant:
            drpdown_variant = {}
            drpdown_variant["variant"] = variant.title
            variant_title = {pVariant.variant_title for pVariant in  ProductVariant.objects.filter(variant = variant)}
            drpdown_variant["variant_titles"] = list(variant_title)
            drpdown_variant_list.append(drpdown_variant)
        print(drpdown_variant_list)
        context = {"all_data": all_products,"total_products":len(all_products),"dropdown_variant":drpdown_variant_list}
        return self.render_to_response(context)