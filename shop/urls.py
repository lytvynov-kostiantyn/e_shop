from django.urls import path
from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("register", views.register, name="register"),
    path("email_verify/<uidb64>/<token>/", views.email_verify, name='email_verify'),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("loyalty", views.loyalty, name="loyalty"),
    path("category_list/<str:name_category>", views.category_list, name="category_list"),
    path("product/<int:pk>", views.product, name="product"),
    path("new_comment/<str:pk>", views.new_comments, name="new_comment"),
    path("filter", views.filters, name="filter"),
    path("user_account", views.user_account, name="user_account"),
    path("personal_inf", views.personal_inf, name="personal_inf"),
    path("basket", views.basket, name="basket"),
    path("make_order", views.make_order, name="make_order"),
    path("order_close/<uidb64>/<token>/", views.order_close, name="order_close"),

    # AJAX
    path("product/watchlist/<int:pk>", views.watchlist, name="watchlist")
]

