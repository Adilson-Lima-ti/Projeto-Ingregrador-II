from decimal import Decimal
import copy
from products.models import Product

class Cart:
    def __init__(self, request):
        if request.session.get("cart") is None:
            request.session["cart"] = {}

        self.cart = request.session["cart"]
        self.session = request.session

    def __iter__(self):
        cart = copy.deepcopy(self.cart.copy())

        products = Product.objects.filter(id__in=cart)
        for product in products:
            cart[str(product.id)]["product"] = product


        for item in cart.values():
            item["price"] = Decimal(item["price"])
            item["total_price"] = item["price"] * item["quantity"]
            yield item
    
    
    def __len__(self):
        return sum(item["quantity"] for item in self.cart.values())


    def add(self, product, quantity=1, override_quantity=False):
        product_id = str(product.id)

        if product_id not in self.cart:
            self.cart[product_id] = {
            "quantity": 0,
            "price": str(product.price),
        }

        if override_quantity:
            self.cart[product_id]["quantity"] = quantity
        else:
            self.cart[product_id]["quantity"] += quantity

        self.save()

    def remove(self, product):
        product_id = str(product.id)

        if product_id in self.cart:
            del self.cart[product_id]
            self.save()

    def save(self):
        self.session.modified = True

        