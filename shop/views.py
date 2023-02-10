from django.utils.http import urlsafe_base64_decode
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse

from django.contrib.auth.tokens import default_token_generator as token_generator
from django.core.paginator import Paginator
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse

import random

from django.views.decorators.csrf import ensure_csrf_cookie

from .utils import send_email_verify, send_email_confirm_order, discount
from .models import BrandFilter, Category, CountryFilter, Product, Sale, User, Comments, Basket
from .forms import NewCommentForm, UserForm, RegistrationForm


BRANDS = BrandFilter.objects.all()
COUNTIES = CountryFilter.objects.all()


def index(request):
    categories = Category.objects.all()
    sales = Sale.objects.all()

    # Adding 5 random products on page
    random_products = set()
    while len(random_products) < 5:
        random_product = random.choice(Product.objects.filter(status='a'))
        random_products.add(random_product)

    return render(request, "shop/index.html", {
        "categories": categories,
        "sales": sales,
        "random_products": random_products
    })


def loyalty(request):
    return render(request, "shop/loyalty.html")


def login_view(request):
    if request.method == "POST":
        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # If Invalid authentication
        if user is None:
            messages.info(request, 'Invalid username and/or password')
            return render(request, "shop/login.html")

        # If Invalid authentication
        if not user.email_verify:
            messages.info(request, 'Invalid verification. Check your email.')
            send_email_verify(request, user)
            return render(request, "shop/login.html")

        # if authentication and verification successful
        else:
            login(request, user)
            return HttpResponseRedirect(reverse("index"))

    else:
        return render(request, "shop/login.html")


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))


def register(request):
    registration_form = RegistrationForm()

    if request.method == "POST":
        data = RegistrationForm(request.POST)

        # Checking user input
        if data.is_valid():
            users_list = User.objects.all().values_list('username', flat=True)

            # checking users password
            if data.cleaned_data['password'] != data.cleaned_data['confirmation']:
                message = 'Passwords must match.'

            # checking users login in db
            elif data.cleaned_data['username'] in users_list:
                message = 'Username already taken.'

            else:
                # creating new user
                user = User.objects.create_user(
                    data.cleaned_data['username'],
                    data.cleaned_data['email'],
                    data.cleaned_data['password']
                )
                user.save()
                # sending confirm email to the user
                send_email_verify(request, user)
                message = 'Confirm your email.'

        else:
            message = 'Invalid data'

        return render(request, "shop/register.html", {
            'registration_form': registration_form,
            "message": message
        })

    # get method
    else:
        return render(request, "shop/register.html", {
            'registration_form': registration_form,
        })


# User email verification
def email_verify(request, uidb64, token):
    try:
        # decoding ID from email url
        user_id = urlsafe_base64_decode(uidb64).decode()
        user = User.objects.get(id=user_id)
    except Exception as ex:
        print(ex)
        user = None

    # Checking token and update verify status
    if user is not None and token_generator.check_token(user, token):
        user.email_verify = True
        user.save()
        login(request, user)
        return HttpResponseRedirect(reverse("index"))

    else:
        messages.info(request, 'Invalid verification')
        return HttpResponseRedirect(reverse("login"))


# Rendering list of products in requested category
def category_list(request, name_category):
    try:
        category = Category.objects.get(name_category=name_category)
    except ObjectDoesNotExist:
        return HttpResponseRedirect(reverse("index"))

    db_products = Product.objects.filter(status='a').filter(category=category.id)

    posts_division = Paginator(db_products, 10)
    requested_page = int(request.GET.get("requested_page", 1))
    product_listing = posts_division.page(requested_page)

    return render(request, "shop/category_list.html", {
        "product_listing": product_listing,
        "brands": BRANDS,
        "countries": COUNTIES,
        "category": category
    })


# Handling product filter request
def filters(request):
    # dict with user request
    filter_request = request.GET
    print(filter_request)

    # Getting required product name
    title_buffer = []
    title_request = filter_request.get("q")
    title_list = Product.objects.all().values_list('title', flat=True)
    if title_request is None or len(title_request) == 0:
        title_buffer = title_list
    else:
        for title in title_list:
            if title_request.lower() in title.lower():
                title_buffer.append(title)

    # Getting required category
    category_request = filter_request.getlist("category")
    all_categories = Category.objects.all().values_list('id', flat=True)
    try:
        category_buffer = list(map(int, category_request))
    except (ValueError, TypeError):
        category_buffer = all_categories
    else:
        if len(category_request) == 0:
            category_buffer = all_categories

    # Getting required starting price of product
    try:
        price_from = float(filter_request.get("price_from"))
    except (ValueError, TypeError):
        price_from = 0

    # Getting required ending price of product
    try:
        price_to = float(filter_request.get("price_to"))
    except (ValueError, TypeError):
        db_max_price = Product.objects.filter(status='a').order_by('price').last()
        price_to = db_max_price.price

    # Getting required brand of product
    brand_request = filter_request.getlist("brand")
    brand_list = BrandFilter.objects.all().values_list('id', flat=True)
    try:
        brand_buffer = list(map(int, brand_request))
    except (ValueError, TypeError):
        brand_buffer = brand_list
    else:
        if len(brand_request) == 0:
            brand_buffer = brand_list

    # Getting required country of product
    country_request = filter_request.getlist("country")
    country_list = CountryFilter.objects.all().values_list('id', flat=True)
    try:
        country_buffer = list(map(int, country_request))
    except (ValueError, TypeError):
        country_buffer = country_list
    else:
        if len(country_request) == 0:
            country_buffer = country_list

    # Final request to db
    queryset = Product.objects.filter(
        status='a',
        title__in=title_buffer,
        category__in=category_buffer,
        price__gte=price_from,
        price__lte=price_to,
        brand__in=brand_buffer,
        country__in=country_buffer
    ).distinct()

    posts_division = Paginator(queryset, 10)
    requested_page = int(filter_request.get("requested_page", 1))
    product_listing = posts_division.page(requested_page)

    return render(request, "shop/category_list.html", {
        "product_listing": product_listing,
        "brands": BRANDS,
        "countries": COUNTIES,
        "category": category_buffer
    })


# Rendering product page
@ensure_csrf_cookie
def product(request, pk):
    # checking page in db
    try:
        current_page = Product.objects.get(id=pk)
    except ObjectDoesNotExist:
        return HttpResponseRedirect(reverse("index"))

    comments = Comments.objects.filter(lot_pk=pk)

    # input form for new comments
    new_comment = NewCommentForm()

    return render(request, "shop/product.html", {
        "product": current_page,
        "comments": comments,
        "new_comment": new_comment
    })


# Adding comments to the product page
@login_required(login_url='/login')
def new_comments(request, pk):
    if request.method == "POST":
        # input from user
        comment_input = NewCommentForm(request.POST)
        # checking input
        if comment_input.is_valid():
            # adding new comment
            new_comment = Comments()
            new_comment.user = User.objects.get(username=request.user.username)
            new_comment.comment = comment_input.cleaned_data.get("comment")
            new_comment.lot_pk = Product.objects.get(id=pk)
            new_comment.save()
            messages.info(request, 'Your comment added to the page')
            return HttpResponseRedirect(reverse("product", args=[pk]))
        else:
            messages.info(request, 'Invalid input.')
            return HttpResponseRedirect(reverse("product", args=[pk]))
    else:
        return HttpResponseRedirect(reverse("product", args=[pk]))


# AJAX
@login_required
def watchlist(request, pk):
    if request.method != "POST":
        return JsonResponse({"error": "POST request required."}, status=400)
    else:
        requested_product = Product.objects.get(id=pk)
        product_watchlist = requested_product.watchlist.all()
        user = User.objects.get(username=request.user.username)
        if request.user in product_watchlist:
            requested_product.watchlist.remove(user)
            watchlist_status = False
        else:
            requested_product.watchlist.add(user)
            watchlist_status = True
        return JsonResponse({"watchlist_status": watchlist_status}, status=200)


@login_required
def user_account(request):
    # form for changing personal inf
    user = User.objects.get(username=request.user.username)
    user_form = UserForm(instance=user)

    # size of user discount
    money_amount = user.purchase_amount
    user_discount = discount(money_amount)

    # user watchlist
    users_watchlist = []
    products = Product.objects.all()
    for value in products:
        if user.id in value.watchlist_list_id():
            users_watchlist.append(value)

    return render(request, "shop/user_account.html", {
        "personal_inf": user_form,
        "discount": user_discount,
        "watchlist": users_watchlist,
    })


@login_required
def personal_inf(request):
    if request.method == "POST":
        user_input = UserForm(request.POST)
        if user_input.is_valid():
            # adding new comment
            new_inf = User.objects.get(username=request.user.username)
            new_inf.first_name = user_input.cleaned_data.get("first_name")
            new_inf.last_name = user_input.cleaned_data.get("last_name")
            new_inf.address = user_input.cleaned_data.get("address")
            new_inf.phone_number = user_input.cleaned_data.get("phone_number")
            new_inf.save()
            messages.info(request, 'Changes applied')
            return HttpResponseRedirect(reverse("user_account"))
        else:
            messages.info(request, 'Invalid input.')
            return HttpResponseRedirect(reverse("user_account"))

    else:
        return HttpResponseRedirect(reverse("index"))


def basket(request):
    # form for personal inf
    user_form = UserForm()

    # dict with user basket
    user_basket = request.GET.get('basket_list')
    if user_basket is None or len(user_basket) == 0:
        queryset = None
    else:
        basket_list = user_basket.split(',')
        queryset = Product.objects.filter(status='a', id__in=basket_list).distinct().order_by('title')

    if request.user.username:
        user = User.objects.get(username=request.user.username)
        user_form = UserForm(instance=user)
        money_amount = user.purchase_amount
        user_discount = discount(money_amount)
    else:
        user_discount = None

    return render(request, "shop/basket.html", {
        "personal_inf": user_form,
        "discount": user_discount,
        "basket": queryset
    })


def make_order(request):
    if request.method == "POST":
        # print(request.POST)
        # checking that basket is not empty
        order_list = request.POST.get('order_list')
        if not order_list:
            messages.info(request, 'Your basket is empty')
            return HttpResponseRedirect(reverse("basket"))

        # checking user personal inf
        user_input = UserForm(request.POST)
        if user_input.is_valid():
            order_inf = {
                'first_name': request.POST.get('first_name'),
                'last_name': request.POST.get('last_name'),
                'address': request.POST.get('address'),
                'phone_number': request.POST.get('phone_number'),
                'email': request.POST.get('email'),
            }

            # find user discount (if user login)
            if request.user.username:
                user = User.objects.get(username=request.user.username)
                money_amount = user.purchase_amount
                user_discount = discount(money_amount)
            else:
                user_discount = 0

            # add order_id
            last_order_id = Basket.objects.all().order_by('order_id').last()
            if last_order_id is None:
                new_order_num = 1
            else:
                new_order_num = last_order_id.order_id + 1

            # creating user order list 
            order = []
            total_price = 0

            new_order_list = list(map(int, order_list.split(',')))

            for i in new_order_list:
                requested_product = Product.objects.get(id=i)
                amount = int(request.POST.get(f'{i}'))
                if amount > requested_product.amount:
                    messages.info(request, 'Invalid amount input, please try again')
                    return HttpResponseRedirect(reverse("index"))
                order.append(f'ID: {i} - TITLE: {requested_product.title} - AMOUNT: {amount}')

                total_price += round((amount * requested_product.price * ((100 - user_discount) / 100)), 2)

                # add order to 'basket' db
                new_order = Basket()
                new_order.order_id = new_order_num
                if request.user.username:
                    new_order.user = User.objects.get(username=request.user.username)
                new_order.title = requested_product
                new_order.amount = amount
                new_order.price = round((amount * requested_product.price * ((100 - user_discount) / 100)), 2)
                new_order.save()

            order_inf['total'] = total_price
            order_inf['order_id'] = new_order_num

            # admin
            admin = User.objects.get(is_staff=True)

            # sending email to admin for confirming order
            send_email_confirm_order(request, order_inf, order, admin)

            messages.info(request, 'Our managers already work on your order')
            return HttpResponseRedirect(reverse("index"))

        else:
            messages.info(request, 'Invalid input')
            return HttpResponseRedirect(reverse("index"))

    else:
        return HttpResponseRedirect(reverse("index"))


def order_close(request, uidb64, token):
    try:
        order_id = urlsafe_base64_decode(uidb64).decode()
        orders_to_close = Basket.objects.filter(order_id=order_id)
    except Exception as ex:
        print(ex)
        orders_to_close = None
    admin = User.objects.get(is_staff=True)
    if orders_to_close is not None and token_generator.check_token(admin, token):
        for order in orders_to_close:
            # closing order
            order.status = 'c'
            order.save()

            # updating product amount
            product_amount = order.title.amount
            new_amount = product_amount - order.amount
            if new_amount <= 0:
                new_amount = 0
                order.title.status = 'c'
                order.title.save()
            order.title.amount = new_amount
            order.title.save()

            # updating user purchase_amount
            if order.user:
                total_price = order.user.purchase_amount + order.price
                order.user.purchase_amount = total_price
                order.user.save()

        messages.info(request, 'Order closed')
        return HttpResponseRedirect(reverse("index"))

    else:
        messages.info(request, 'Invalid verification')
        return HttpResponseRedirect(reverse("index"))
