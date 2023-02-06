from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from django.contrib.auth.tokens import default_token_generator as token_generator
import random
from django.test import Client, TestCase
from django.urls import reverse
from django.contrib.messages import get_messages

from e_shop.shop.views import discount
from e_shop.shop.models import Basket, BrandFilter, Category, Comments, CountryFilter, Product, Sale, User

# Create your tests here.

c = Client()


class ShopTestCase(TestCase):
    def setUp(self):
        Sale.objects.create(sale_img='test_sale')
        for i in range(3):
            Category.objects.create(name_category=f'test_category_{i}')
        for i in range(4):
            BrandFilter.objects.create(brand_name=f'test_brand_{i}')
        for i in range(5):
            CountryFilter.objects.create(country_name=f'test_country_{i}')
        for i in range(15):
            if i < 5:
                Product.objects.create(
                    title=f'{i}',
                    brand=BrandFilter.objects.get(brand_name='test_brand_0'),
                    description='test',
                    price=50,
                    country=CountryFilter.objects.get(country_name='test_country_0'),
                    category=Category.objects.get(name_category='test_category_0'),
                    amount=1
                )
            elif 5 <= i < 10:
                Product.objects.create(
                    title=f'{i}',
                    brand=BrandFilter.objects.get(brand_name='test_brand_1'),
                    description='test',
                    price=100,
                    country=CountryFilter.objects.get(country_name='test_country_1'),
                    category=Category.objects.get(name_category='test_category_1'),
                    amount=1
                )
            else:
                Product.objects.create(
                    title=f'{i}',
                    brand=BrandFilter.objects.get(brand_name='test_brand_2'),
                    description='test',
                    price=150,
                    country=CountryFilter.objects.get(country_name='test_country_2'),
                    category=Category.objects.get(name_category='test_category_2'),
                    amount=1
                )

    def test_index(self):
        sale = Sale.objects.get(sale_img='test_sale')
        category = Category.objects.get(name_category='test_category_0')

        response = c.get(reverse("index"))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'shop/index.html')

        self.assertIn(category, response.context['categories'])
        self.assertEqual(len(response.context['categories']), 3)

        self.assertIn(sale, response.context['sales'])
        self.assertEqual(len(response.context['sales']), 1)

        self.assertEqual(len(response.context['random_products']), 5)

    def test_register_get(self):
        response = c.get("/shop/register")

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'shop/register.html')

    def test_register_post(self):
        response = c.post("/shop/register", {
            'username': 'test',
            'email': 'test@mail.com',
            'password': '123',
            'confirmation': '123',
        })

        users = User.objects.all()

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'shop/register.html')

        self.assertEqual(len(users), 1)
        self.assertEqual(response.context['message'], "Confirm your email.")

    def test_register_post_error_data(self):
        response = c.post("/shop/register", {
            'username': 'test',
            'email': 'test@mail.com',
            'password': '123',
            'confirmation': '321',
        })

        users = User.objects.all()

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'shop/register.html')

        self.assertNotEqual(len(users), 1)
        self.assertEqual(response.context['message'], "Passwords must match.")

    def test_register_post_error_data_2(self):
        User.objects.create(
            username='test',
            email='test@mail.com',
            password='123',
        )

        response = c.post("/shop/register", {
            'username': 'test',
            'email': 'test@mail.com',
            'password': '123',
            'confirmation': '123',
        })

        users = User.objects.all()

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'shop/register.html')

        self.assertEqual(len(users), 1)
        self.assertEqual(response.context['message'], "Username already taken.")

    def test_register_post_no_data(self):
        response = c.post("/shop/register", {
            'username': '',
            'email': '',
            'password': '',
            'confirmation': '',
        })

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'shop/register.html')

        self.assertEqual(response.context['message'], "Invalid input.")

    def test_login_get(self):
        response = c.get("/shop/login")

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'shop/login.html')

    def test_email_verify(self):
        user = User.objects.create(
            username='test',
            email='test@mail.com',
            email_verify=False,
            is_active=True,
        )
        user.set_password('123')
        user.save()
        uid = urlsafe_base64_encode(force_bytes(user.id))
        token = token_generator.make_token(user)

        response = c.get(f"/shop/email_verify/{uid}/{token}", follow=True)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'shop/index.html')

    def test_email_verify_invalid_token(self):
        user = User.objects.create(
            username='test',
            email='test@mail.com',
            email_verify=False,
            is_active=True,
        )
        user.set_password('123')
        user.save()
        uid = urlsafe_base64_encode(force_bytes(user.id))
        token = token_generator.make_token(user) + 'x'

        response = c.get(f"/shop/email_verify/{uid}/{token}", follow=True)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'shop/login.html')

    def test_email_verify_invalid_uidb64(self):
        user = User.objects.create(
            username='test',
            email='test@mail.com',
            email_verify=False,
            is_active=True,
        )
        user.set_password('123')
        user.save()
        uid = urlsafe_base64_encode(force_bytes(0))
        token = token_generator.make_token(user)

        response = c.get(f"/shop/email_verify/{uid}/{token}", follow=True)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'shop/login.html')

    def test_login_post(self):
        user = User.objects.create(
            username='test',
            email='test@mail.com',
            email_verify=True,
            is_active=True,
        )
        user.set_password('123')
        user.save()

        response = c.post("/shop/login", {
            'username': 'test',
            'password': '123',
        })

        self.assertEqual(response.status_code, 302)

    def test_login_post_no_verify(self):
        user = User.objects.create(
            username='test',
            email='test@mail.com',
            email_verify=False,
            is_active=True,
        )
        user.set_password('123')
        user.save()

        response = c.post("/shop/login", {
            'username': 'test',
            'password': '123',
        })

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'shop/login.html')

    def test_login_post_invalid_input(self):
        user = User.objects.create(
            username='test',
            email='test@mail.com',
            email_verify=True,
            is_active=True,
        )
        user.set_password('123')
        user.save()

        response = c.post("/shop/login", {
            'username': 'test32',
            'password': '123'
        })

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'shop/login.html')

    def test_logout(self):
        response = c.get("/shop/logout")

        self.assertEqual(response.status_code, 302)

    def test_loyalty(self):
        response = c.get("/shop/loyalty")

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'shop/loyalty.html')

    def test_category(self):
        boo = len(BrandFilter.objects.all())
        baz = len(CountryFilter.objects.all())
        foo = len(Category.objects.all())

        x = random.randint(0, (foo - 1))

        response = c.get(f"/shop/category_list/test_category_{x}", {
            'requested_page': '1'
        })

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'shop/category_list.html')

        self.assertEqual(len(response.context['brands']), boo)
        self.assertEqual(len(response.context['countries']), baz)

        self.assertEqual(response.context['product_listing'].number, 1)

    def test_category_invalid_category(self):
        response = c.get("/shop/category_list/boo", {
            'requested_page': '1'
        })

        self.assertEqual(response.status_code, 302)

    def test_product_invalid_id(self):
        max_id = max(Product.objects.all().values_list('id', flat=True))

        response = c.get(f"/shop/product/{max_id + 1}")

        self.assertEqual(response.status_code, 302)

    def test_product(self):
        x = random.randint(1, 15)
        boo = Product.objects.get(id=x)
        user = User.objects.create(
            username='test',
            email='test@mail.com',
            email_verify=True,
            is_active=True,
        )
        for i in range(x):
            Comments.objects.create(
                user=user,
                comment=f'{i}',
                lot_pk=boo
            )

        response = c.get(f"/shop/product/{x}")

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'shop/product.html')

        self.assertEqual(boo, response.context['product'])

        self.assertEqual(len(response.context['comments']), x)

        self.assertTrue(response.context['new_comment'])

    def test_product_no_comments(self):
        x = random.randint(1, 15)
        boo = Product.objects.get(id=x)

        response = c.get(f"/shop/product/{x}")

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'shop/product.html')

        self.assertEqual(boo, response.context['product'])

        self.assertFalse(response.context['comments'])

        self.assertTrue(response.context['new_comment'])

    def test_new_comment_get(self):
        x = random.randint(1, 15)
        user = User.objects.create(
            username='test_user',
            email='test@mail.com',
            email_verify=True,
            is_active=True,
        )
        user.set_password('123')
        user.save()

        self.client = Client()
        self.client.login(username='test_user', password='123')

        response = c.get(f"/shop/new_comment/{x}")

        self.assertEqual(response.status_code, 302)

    def test_new_comment_post_no_data(self):
        x = random.randint(1, 15)
        user = User.objects.create(
            username='test_user',
            email='test@mail.com',
            email_verify=True,
            is_active=True,
        )
        user.set_password('123')
        user.save()

        self.client = Client()
        self.client.login(username='test_user', password='123')

        response = c.post(f"/shop/new_comment/{x}")

        self.assertEqual(response.status_code, 302)

    def test_new_comment_post(self):
        x = random.randint(1, 15)
        user = User.objects.create(
            username='test_user',
            email='test@mail.com',
            email_verify=True,
            is_active=True,
        )
        user.set_password('123')
        user.save()

        self.client = Client()
        self.client.login(username='test_user', password='123')

        response = self.client.post(f"/shop/new_comment/{x}", {
            'comment': 'test'
        })

        # boo = Product.objects.get(id=x)
        # print(Comments.objects.filter(lot_pk=boo))

        self.assertEqual(response.status_code, 302)

        self.assertEqual(len(Comments.objects.filters(lot_pk=x)), 1)

    def test_filter_search(self):
        tests = ['', '1', 'Hello, world!']
        for i in tests:
            response = c.get(f"/shop/filter", {
                'q': f'{i}',
            })

            boo = BrandFilter.objects.all()
            baz = CountryFilter.objects.all()
            foo = Category.objects.all()

            product_count = len(Product.objects.filters(title__contains=f'{i}'))

            self.assertEqual(response.status_code, 200)
            self.assertTemplateUsed(response, 'shop/category_list.html')

            self.assertEqual(len(response.context['brands']), len(boo))
            self.assertEqual(len(response.context['countries']), len(baz))
            self.assertEqual(len(response.context['category']), len(foo))

            if product_count <= 10:
                self.assertEqual(len(response.context['product_listing'].object_list), product_count)
                self.assertEqual(response.context['product_listing'].number, 1)
                self.assertFalse(response.context['product_listing'].has_next())
                self.assertFalse(response.context['product_listing'].has_previous())
                self.assertFalse(response.context['product_listing'].has_other_pages())
            if product_count > 10:
                self.assertEqual(len(response.context['product_listing'].object_list), 10)
                self.assertEqual(response.context['product_listing'].number, 1)
                self.assertTrue(response.context['product_listing'].has_next())
                self.assertFalse(response.context['product_listing'].has_previous())
                self.assertTrue(response.context['product_listing'].has_other_pages())
                self.assertEqual(response.context['product_listing'].next_page_number(), 2)
            if product_count == 0:
                self.assertEqual(response.context['product_listing'].number, 1)
                self.assertEqual(len(response.context['product_listing'].object_list), 0)
                self.assertFalse(response.context['product_listing'].has_next())
                self.assertFalse(response.context['product_listing'].has_previous())
                self.assertFalse(response.context['product_listing'].has_other_pages())

    def test_filter_price_from(self):
        tests = ['', '-5', '51', 'Hello, world!']
        for i in tests:
            response = c.get(f"/shop/filter", {
                'price_from': f'{i}'
            })

            try:
                i = int(i)
            except ValueError:
                i = 0
            product_count = len(Product.objects.filters(price__gte=f'{i}'))

            boo = BrandFilter.objects.all()
            baz = CountryFilter.objects.all()
            foo = Category.objects.all()

            self.assertEqual(response.status_code, 200)
            self.assertTemplateUsed(response, 'shop/category_list.html')

            self.assertEqual(len(response.context['brands']), len(boo))
            self.assertEqual(len(response.context['countries']), len(baz))
            self.assertEqual(len(response.context['category']), len(foo))

            if product_count <= 10:
                self.assertEqual(len(response.context['product_listing'].object_list), product_count)
                self.assertEqual(response.context['product_listing'].number, 1)
                self.assertFalse(response.context['product_listing'].has_next())
                self.assertFalse(response.context['product_listing'].has_previous())
                self.assertFalse(response.context['product_listing'].has_other_pages())
            if product_count > 10:
                self.assertEqual(len(response.context['product_listing'].object_list), 10)
                self.assertEqual(response.context['product_listing'].number, 1)
                self.assertTrue(response.context['product_listing'].has_next())
                self.assertFalse(response.context['product_listing'].has_previous())
                self.assertTrue(response.context['product_listing'].has_other_pages())
                self.assertEqual(response.context['product_listing'].next_page_number(), 2)
            if product_count == 0:
                self.assertEqual(response.context['product_listing'].number, 1)
                self.assertEqual(len(response.context['product_listing'].object_list), 0)
                self.assertFalse(response.context['product_listing'].has_next())
                self.assertFalse(response.context['product_listing'].has_previous())
                self.assertFalse(response.context['product_listing'].has_other_pages())

    def test_filter_price_to(self):
        max_price = Product.objects.filters(status='a').order_by('price').last().price
        tests = ['', '-5', '51', 'Hello, world!']
        for i in tests:
            response = c.get(f"/shop/filter", {
                'price_to': f'{i}'
            })

            try:
                i = int(i)
            except ValueError:
                i = max_price
            product_count = len(Product.objects.filters(price__lte=f'{i}'))

            boo = BrandFilter.objects.all()
            baz = CountryFilter.objects.all()
            foo = Category.objects.all()

            self.assertEqual(response.status_code, 200)
            self.assertTemplateUsed(response, 'shop/category_list.html')

            self.assertEqual(len(response.context['brands']), len(boo))
            self.assertEqual(len(response.context['countries']), len(baz))
            self.assertEqual(len(response.context['category']), len(foo))

            if product_count <= 10:
                self.assertEqual(len(response.context['product_listing'].object_list), product_count)
                self.assertEqual(response.context['product_listing'].number, 1)
                self.assertFalse(response.context['product_listing'].has_next())
                self.assertFalse(response.context['product_listing'].has_previous())
                self.assertFalse(response.context['product_listing'].has_other_pages())
            if product_count > 10:
                self.assertEqual(len(response.context['product_listing'].object_list), 10)
                self.assertEqual(response.context['product_listing'].number, 1)
                self.assertTrue(response.context['product_listing'].has_next())
                self.assertFalse(response.context['product_listing'].has_previous())
                self.assertTrue(response.context['product_listing'].has_other_pages())
                self.assertEqual(response.context['product_listing'].next_page_number(), 2)
            if product_count == 0:
                self.assertEqual(response.context['product_listing'].number, 1)
                self.assertEqual(len(response.context['product_listing'].object_list), 0)
                self.assertFalse(response.context['product_listing'].has_next())
                self.assertFalse(response.context['product_listing'].has_previous())
                self.assertFalse(response.context['product_listing'].has_other_pages())

    def test_filter_brand(self):
        tests = ['', '-1', '1', 'Hello, world!']
        response = c.get("/shop/filter", {
            'brand': tests
        })

        brands = []
        for i in tests:
            try:
                int(i)
                brands.append(i)
            except (ValueError, TypeError):
                pass
        product_count = len(Product.objects.filters(brand__in=brands))

        boo = BrandFilter.objects.all()
        baz = CountryFilter.objects.all()
        foo = Category.objects.all()

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'shop/category_list.html')

        self.assertEqual(len(response.context['brands']), len(boo))
        self.assertEqual(len(response.context['countries']), len(baz))
        self.assertEqual(len(response.context['category']), len(foo))

        if product_count <= 10:
            self.assertEqual(len(response.context['product_listing'].object_list), product_count)
            self.assertEqual(response.context['product_listing'].number, 1)
            self.assertFalse(response.context['product_listing'].has_next())
            self.assertFalse(response.context['product_listing'].has_previous())
            self.assertFalse(response.context['product_listing'].has_other_pages())
        if product_count > 10:
            self.assertEqual(len(response.context['product_listing'].object_list), 10)
            self.assertEqual(response.context['product_listing'].number, 1)
            self.assertTrue(response.context['product_listing'].has_next())
            self.assertFalse(response.context['product_listing'].has_previous())
            self.assertTrue(response.context['product_listing'].has_other_pages())
            self.assertEqual(response.context['product_listing'].next_page_number(), 2)
        if product_count == 0:
            self.assertEqual(response.context['product_listing'].number, 1)
            self.assertEqual(len(response.context['product_listing'].object_list), 0)
            self.assertFalse(response.context['product_listing'].has_next())
            self.assertFalse(response.context['product_listing'].has_previous())
            self.assertFalse(response.context['product_listing'].has_other_pages())

    def test_filter_country(self):
        tests = ['', '-1', '1', '2', 'Hello, world!']
        response = c.get("/shop/filter", {
            'country': tests
        })

        country = []
        for i in tests:
            try:
                int(i)
                country.append(i)
            except (ValueError, TypeError):
                pass
        product_count = len(Product.objects.filters(country__in=country))

        boo = BrandFilter.objects.all()
        baz = CountryFilter.objects.all()
        foo = Category.objects.all()

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'shop/category_list.html')

        self.assertEqual(len(response.context['brands']), len(boo))
        self.assertEqual(len(response.context['countries']), len(baz))
        self.assertEqual(len(response.context['category']), len(foo))

        if product_count <= 10:
            self.assertEqual(len(response.context['product_listing'].object_list), product_count)
            self.assertEqual(response.context['product_listing'].number, 1)
            self.assertFalse(response.context['product_listing'].has_next())
            self.assertFalse(response.context['product_listing'].has_previous())
            self.assertFalse(response.context['product_listing'].has_other_pages())
        if product_count > 10:
            self.assertEqual(len(response.context['product_listing'].object_list), 10)
            self.assertEqual(response.context['product_listing'].number, 1)
            self.assertTrue(response.context['product_listing'].has_next())
            self.assertFalse(response.context['product_listing'].has_previous())
            self.assertTrue(response.context['product_listing'].has_other_pages())
            self.assertEqual(response.context['product_listing'].next_page_number(), 2)
        if product_count == 0:
            self.assertEqual(response.context['product_listing'].number, 1)
            self.assertEqual(len(response.context['product_listing'].object_list), 0)
            self.assertFalse(response.context['product_listing'].has_next())
            self.assertFalse(response.context['product_listing'].has_previous())
            self.assertFalse(response.context['product_listing'].has_other_pages())

    def test_filter(self):
        q = '1'
        categories = [1]
        requested_page = 1
        price_from = 0
        price_to = 200
        brand_buffer = [1, 2, 3]
        country_buffer = [1, 2, 3]
        result = 1

        response = c.get("/shop/filter", {
            'q': q,
            'category': categories,
            'requested_page': requested_page,
            'price_from': price_from,
            'price_to': price_to,
            'brand': brand_buffer,
            'country': country_buffer
        })

        product_count = len(Product.objects.filters(
            title__contains=q,
            category__in=categories,
            price__gte=price_from,
            price__lte=price_to,
            brand__in=brand_buffer,
            country__in=country_buffer))
        # print(product_count)

        boo = BrandFilter.objects.all()
        baz = CountryFilter.objects.all()

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'shop/category_list.html')

        self.assertEqual(product_count, result)

        self.assertEqual(len(response.context['brands']), len(boo))
        self.assertEqual(len(response.context['countries']), len(baz))
        self.assertEqual(len(response.context['category']), len(categories))

        self.assertEqual(len(response.context['product_listing'].object_list), product_count)
        self.assertEqual(response.context['product_listing'].number, 1)
        self.assertFalse(response.context['product_listing'].has_next())
        self.assertFalse(response.context['product_listing'].has_previous())
        self.assertFalse(response.context['product_listing'].has_other_pages())

    def test_filter_no_filters(self):
        q = ''
        categories = ['']
        requested_page = 2
        price_from = 0
        price_to = 200
        brand_buffer = [1, 2, 3]
        country_buffer = [1, 2, 3]
        result = 15

        response = c.get("/shop/filter", {
            'q': q,
            'category': categories,
            'requested_page': requested_page,
            'price_from': price_from,
            'price_to': price_to,
            'brand': brand_buffer,
            'country': country_buffer
        })

        product_count = len(Product.objects.filters(
            title__contains=q,
            price__gte=price_from,
            price__lte=price_to,
            brand__in=brand_buffer,
            country__in=country_buffer))
        # print(product_count)

        boo = BrandFilter.objects.all()
        baz = CountryFilter.objects.all()
        foo = Category.objects.all()

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'shop/category_list.html')

        self.assertEqual(product_count, result)

        self.assertEqual(len(response.context['brands']), len(boo))
        self.assertEqual(len(response.context['countries']), len(baz))
        self.assertEqual(len(response.context['category']), len(foo))

        self.assertEqual(len(response.context['product_listing'].object_list), 5)
        self.assertEqual(response.context['product_listing'].number, 2)
        self.assertFalse(response.context['product_listing'].has_next())
        self.assertTrue(response.context['product_listing'].has_previous())
        self.assertTrue(response.context['product_listing'].has_other_pages())

    def test_filter_price_limits(self):
        q = ''
        categories = ['']
        requested_page = 1
        price_from = 51
        price_to = 149
        brand_buffer = [1, 2, 3]
        country_buffer = [1, 2, 3]
        result = 5

        response = c.get("/shop/filter", {
            'q': q,
            'category': categories,
            'requested_page': requested_page,
            'price_from': price_from,
            'price_to': price_to,
            'brand': brand_buffer,
            'country': country_buffer
        })

        product_count = len(Product.objects.filters(
            title__contains=q,
            price__gte=price_from,
            price__lte=price_to,
            brand__in=brand_buffer,
            country__in=country_buffer))
        # print(product_count)

        boo = BrandFilter.objects.all()
        baz = CountryFilter.objects.all()
        foo = Category.objects.all()

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'shop/category_list.html')

        self.assertEqual(product_count, result)

        self.assertEqual(len(response.context['brands']), len(boo))
        self.assertEqual(len(response.context['countries']), len(baz))
        self.assertEqual(len(response.context['category']), len(foo))

        self.assertEqual(len(response.context['product_listing'].object_list), product_count)
        self.assertEqual(response.context['product_listing'].number, 1)
        self.assertFalse(response.context['product_listing'].has_next())
        self.assertFalse(response.context['product_listing'].has_previous())
        self.assertFalse(response.context['product_listing'].has_other_pages())

    def test_filter_empty_page(self):
        q = ''
        categories = ['']
        requested_page = 1
        price_from = 51
        price_to = 149
        brand_buffer = [1, 3]
        country_buffer = [1, 2, 3]
        result = 0

        response = c.get("/shop/filter", {
            'q': q,
            'category': categories,
            'requested_page': requested_page,
            'price_from': price_from,
            'price_to': price_to,
            'brand': brand_buffer,
            'country': country_buffer
        })

        product_count = len(Product.objects.filters(
            title__contains=q,
            price__gte=price_from,
            price__lte=price_to,
            brand__in=brand_buffer,
            country__in=country_buffer))
        # print(product_count)

        boo = BrandFilter.objects.all()
        baz = CountryFilter.objects.all()
        foo = Category.objects.all()

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'shop/category_list.html')

        self.assertEqual(product_count, result)

        self.assertEqual(len(response.context['brands']), len(boo))
        self.assertEqual(len(response.context['countries']), len(baz))
        self.assertEqual(len(response.context['category']), len(foo))

        self.assertEqual(response.context['product_listing'].number, 1)
        self.assertEqual(len(response.context['product_listing'].object_list), 0)
        self.assertFalse(response.context['product_listing'].has_next())
        self.assertFalse(response.context['product_listing'].has_previous())
        self.assertFalse(response.context['product_listing'].has_other_pages())

    def test_user_account(self):
        user = User.objects.create(
            username='test_user',
            email='test@mail.com',
            email_verify=True,
            is_active=True,
            purchase_amount=1000
        )
        user.set_password('123')
        user.save()

        self.client = Client()
        self.client.login(username='test_user', password='123')

        boo = discount(user.purchase_amount)

        for i in range(1, 5):
            random_product = Product.objects.get(id=i)
            random_product.watchlist.add(user)

        response = self.client.post("/shop/user_account")

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'shop/user_account.html')

        self.assertTrue(response.context['personal_inf'])

        self.assertEqual(response.context['discount'], boo)

        self.assertEqual(len(response.context['watchlist']), 4)

    def test_personal_inf_get(self):
        user = User.objects.create(
            username='test_user',
            email='test@mail.com',
            email_verify=True,
            is_active=True,
            purchase_amount=1000
        )
        user.set_password('123')
        user.save()

        self.client = Client()
        self.client.login(username='test_user', password='123')

        response = self.client.get("/shop/personal_inf", follow=True)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'shop/index.html')

    def test_personal_inf_post_no_data(self):
        user = User.objects.create(
            username='test_user',
            email='test@mail.com',
            email_verify=True,
            is_active=True,
            purchase_amount=1000
        )
        user.set_password('123')
        user.save()

        self.client = Client()
        self.client.login(username='test_user', password='123')

        response = self.client.post("/shop/personal_inf", {
            'first_name': '',
            'last_name': '',
            'email': '',
            'address': '',
            'phone_number': '',
        })

        self.assertEqual(response.status_code, 302)

    def test_personal_inf_post(self):
        user = User.objects.create(
            username='test_user',
            email='test@mail.com',
            email_verify=True,
            is_active=True,
            purchase_amount=1000
        )
        user.set_password('123')
        user.save()

        self.client = Client()
        self.client.login(username='test_user', password='123')

        response = self.client.post("/shop/personal_inf", {
            'first_name': 'test',
            'last_name': 'test-test',
            'email': 'change@mail.com',
            'address': 'test street',
            'phone_number': '+38095',
        })
        messages = list(get_messages(response.wsgi_request))

        self.assertEqual(len(messages), 1)
        self.assertEqual(str(messages[0]), 'Changes applied')

        self.assertEqual(response.status_code, 302)

        user = User.objects.get(username='test_user')
        self.assertEqual(user.first_name, 'test')
        self.assertEqual(user.email, 'test@mail.com')
        self.assertEqual(user.phone_number, '+38095')

    def test_basket_not_login_empty_basket(self):
        response = self.client.get("/shop/basket", {
            'basket_list': ''
        })

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'shop/basket.html')

        self.assertTrue(response.context['personal_inf'])
        self.assertEqual(response.context['discount'], None)
        self.assertEqual(response.context['basket'], None)

    def test_basket_not_login(self):
        response = self.client.get(f"/shop/basket", {
            'basket_list': '1,2,4'
        })

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'shop/basket.html')

        self.assertTrue(response.context['personal_inf'])
        self.assertEqual(response.context['discount'], None)

        self.assertEqual(len(response.context['basket']), 3)

    def test_basket_login_empty_basket(self):
        user = User.objects.create(
            username='test_user',
            email='test@mail.com',
            email_verify=True,
            is_active=True,
            purchase_amount=1000
        )
        user.set_password('123')
        user.save()
        self.client = Client()
        self.client.login(username='test_user', password='123')

        boo = discount(user.purchase_amount)

        response = self.client.get("/shop/basket", {
            'basket_list': ''
        })

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'shop/basket.html')

        self.assertTrue(response.context['personal_inf'])
        self.assertEqual(response.context['discount'], boo)
        self.assertEqual(response.context['basket'], None)

    def test_basket_login(self):
        user = User.objects.create(
            username='test_user',
            email='test@mail.com',
            email_verify=True,
            is_active=True,
            purchase_amount=1000
        )
        user.set_password('123')
        user.save()
        self.client = Client()
        self.client.login(username='test_user', password='123')

        boo = discount(user.purchase_amount)

        response = self.client.get("/shop/basket", {
            'basket_list': '2,5'
        })

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'shop/basket.html')

        self.assertTrue(response.context['personal_inf'])
        self.assertEqual(response.context['discount'], boo)
        self.assertEqual(len(response.context['basket']), 2)

    def test_watchlist_get(self):
        user = User.objects.create(
            username='test_user',
            email='test@mail.com',
            email_verify=True,
            is_active=True,
            purchase_amount=1000
        )
        user.set_password('123')
        user.save()
        self.client = Client()
        self.client.login(username='test_user', password='123')

        x = random.randint(1, 15)

        response = self.client.get(f"/shop/product/watchlist/{x}")

        self.assertEqual(response.status_code, 400)

    def test_watchlist_post_add(self):
        user = User.objects.create(
            username='test_user',
            email='test@mail.com',
            email_verify=True,
            is_active=True,
            purchase_amount=1000
        )
        user.set_password('123')
        user.save()
        self.client = Client()
        self.client.login(username='test_user', password='123')

        x = random.randint(1, 15)

        response = self.client.post(f"/shop/product/watchlist/{x}")

        product = Product.objects.get(id=x)

        self.assertIn(user, product.watchlist.all())
        self.assertEqual(response.status_code, 200)

    def test_watchlist_post_remove(self):
        user = User.objects.create(
            username='test_user',
            email='test@mail.com',
            email_verify=True,
            is_active=True,
            purchase_amount=1000
        )
        user.set_password('123')
        user.save()
        self.client = Client()
        self.client.login(username='test_user', password='123')

        x = random.randint(1, 15)

        random_product = Product.objects.get(id=x)
        random_product.watchlist.add(user)

        response = self.client.post(f"/shop/product/watchlist/{x}")

        self.assertNotIn(user, random_product.watchlist.all())
        self.assertEqual(response.status_code, 200)

    def test_make_order_get(self):
        response = self.client.get("/shop/make_order", follow=True)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'shop/index.html')

    def test_make_order_post_empty_basket(self):
        response = self.client.post(f"/shop/make_order", {}, follow=True)
        messages = list(get_messages(response.wsgi_request))

        self.assertEqual(len(messages), 1)
        self.assertEqual(str(messages[0]), 'Your basket is empty')

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'shop/basket.html')

    def test_make_order_post_invalid_form(self):
        response = self.client.post("/shop/make_order", {
            'order_list': ['1,2'],
            'email': 'invalid email address'
        }, follow=True)
        messages = list(get_messages(response.wsgi_request))

        self.assertEqual(len(messages), 1)
        self.assertEqual(str(messages[0]), 'Invalid input')

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'shop/index.html')

    def test_make_order_post_invalid_amount(self):
        response = self.client.post("/shop/make_order", {
            'first_name': 'David',
            'last_name': 'Malan',
            'address': 'Harvard University Massachusetts Hall Cambridge, MA 02138',
            'phone_number': '(617) 495-1000',
            'email': 'harvard@email.com',
            'order_list': ['1,2'],
            '1': 100,
            '2': 1
        }, follow=True)
        messages = list(get_messages(response.wsgi_request))

        self.assertEqual(len(messages), 1)
        self.assertEqual(str(messages[0]), 'Invalid amount input, please try again')

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'shop/index.html')

    def test_make_order_post(self):
        admin_user = User.objects.create(
            username='test_user',
            email='test@mail.com',
            email_verify=True,
            is_active=True,
            is_staff=True,
            purchase_amount=1000
        )
        admin_user.set_password('123')
        admin_user.save()

        response = self.client.post("/shop/make_order", {
            'first_name': 'David',
            'last_name': 'Malan',
            'address': 'Harvard University Massachusetts Hall Cambridge, MA 02138',
            'phone_number': '6174951000',
            'email': 'harvard@email.com',
            'order_list': ['1'],
            '1': 1,
        }, follow=True)
        messages = list(get_messages(response.wsgi_request))

        self.assertEqual(len(messages), 1)
        self.assertEqual(str(messages[0]), 'Our managers already work on your order')

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'shop/index.html')

    def test_order_close_invalid_uidb64(self):
        admin_user = User.objects.create(
            username='test_user',
            email='test@mail.com',
            email_verify=True,
            is_active=True,
            is_staff=True,
        )
        admin_user.set_password('123')
        admin_user.save()
        self.client = Client()
        self.client.login(username='test_user', password='123')

        uid = urlsafe_base64_encode(force_bytes(10))
        token = token_generator.make_token(User.objects.get(is_staff=True))

        response = self.client.get(f"/shop/order_close/{uid}/{token}", follow=True)
        messages = list(get_messages(response.wsgi_request))

        self.assertEqual(len(messages), 1)
        self.assertEqual(str(messages[0]), 'Invalid verification')

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'shop/index.html')

    def test_order_close_invalid_token(self):
        admin_user = User.objects.create(
            username='test_user',
            email='test@mail.com',
            email_verify=True,
            is_active=True,
            is_staff=True,
        )
        admin_user.set_password('123')
        admin_user.save()
        user = User.objects.create(
            username='test_user2',
            email='test@mail.com',
            email_verify=True,
            is_active=True,
            is_staff=False,
        )
        self.client = Client()
        self.client.login(username='test_user', password='123')

        order = Basket.objects.create(
            order_id=100,
            title=Product.objects.get(id=1),
            amount=1,
            price=100,
        )

        uid = urlsafe_base64_encode(force_bytes(order.order_id))
        token = token_generator.make_token(user)

        response = self.client.get(f"/shop/order_close/{uid}/{token}", follow=True)
        messages = list(get_messages(response.wsgi_request))

        self.assertEqual(len(messages), 1)
        self.assertEqual(str(messages[0]), 'Invalid verification')

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'shop/index.html')

    def test_order_close(self):
        admin_user = User.objects.create(
            username='test_user',
            email='test@mail.com',
            email_verify=True,
            is_active=True,
            is_staff=True,
        )
        admin_user.set_password('123')
        admin_user.save()
        self.client = Client()
        self.client.login(username='test_user', password='123')

        order = Basket.objects.create(
            order_id=100,
            title=Product.objects.get(id=1),
            amount=1,
            price=100,
        )

        uid = urlsafe_base64_encode(force_bytes(order.order_id))
        token = token_generator.make_token(User.objects.get(is_staff=True))

        response = self.client.get(f"/shop/order_close/{uid}/{token}", follow=True)
        messages = list(get_messages(response.wsgi_request))

        self.assertEqual(len(messages), 1)
        self.assertEqual(str(messages[0]), 'Order closed')

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'shop/index.html')

        closed_order = Basket.objects.get(order_id=100)

        self.assertEqual(closed_order.status, 'c')
        self.assertEqual(closed_order.title.status, 'c')
        self.assertEqual(closed_order.title.amount, 0)
