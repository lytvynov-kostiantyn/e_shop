from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    address = models.CharField(max_length=100, blank=True)
    phone_number = models.CharField(max_length=100, null=True, blank=True)
    email_verify = models.BooleanField(default=False)
    purchase_amount = models.IntegerField(default=0)


class Category(models.Model):
    name_category = models.CharField(max_length=30)
    category_image_link = models.URLField(blank=True, max_length=250)

    def __str__(self):
        return f"{self.name_category}"


# current sales
class Sale(models.Model):
    sale_img = models.URLField(blank=True, max_length=250)
    sale_link = models.CharField(max_length=100, null=True, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-timestamp"]

    def __str__(self):
        return f"{self.pk}"


class BrandFilter(models.Model):
    brand_name = models.CharField(max_length=30)

    class Meta:
        ordering = ["brand_name"]

    def __str__(self):
        return f"{self.brand_name}"


class CountryFilter(models.Model):
    country_name = models.CharField(max_length=30)

    class Meta:
        ordering = ["country_name"]

    def __str__(self):
        return f"{self.country_name}"


class Product(models.Model):
    title = models.CharField(max_length=100)
    brand = models.ForeignKey(BrandFilter, on_delete=models.SET_NULL, null=True)
    description = models.TextField()
    price = models.IntegerField()
    country = models.ForeignKey(CountryFilter, on_delete=models.SET_NULL, null=True)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True)
    image_link = models.URLField(blank=True, max_length=250)
    amount = models.IntegerField()
    watchlist = models.ManyToManyField(User, related_name="likes", blank=True)

    def watchlist_list_id(self):
        return self.watchlist.values_list('id', flat=True)

    STATUS = (
            ('a', 'active'),
            ('c', 'close')
        )
    status = models.CharField(max_length=1, choices=STATUS, default='a')

    def __str__(self):
        return f"{self.pk} - {self.title}"


# comments for products
class Comments(models.Model):
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    comment = models.TextField()
    lot_pk = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True)
    time_of_creation = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-time_of_creation"]

    def __str__(self):
        return f"{self.lot_pk} - {self.user}"


class Basket(models.Model):
    order_id = models.IntegerField()
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    title = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True)
    amount = models.IntegerField()
    price = models.FloatField()

    STATUS = (
            ('a', 'active'),
            ('c', 'close')
        )
    status = models.CharField(max_length=1, choices=STATUS, default='a')

    def __str__(self):
        return f"{self.pk} - {self.order_id} - {self.user}"
