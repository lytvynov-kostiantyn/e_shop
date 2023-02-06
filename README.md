# E-Shop
### Description:

***About app***

This is a fairly simple web application that implements all the necessary functionality for the successful conduct of a small business. The application collects a minimum of information about its customers, all significant changes can be made to the application only with the approval of the administrator. A loyalty program has been implemented to motivate users. The purchase is made after confirmation by the administrator in order to avoid errors with the availability of goods for sale.

***Under the hood***

`admin.py` - here customization of the user profile is done in django admin and added other application models.

`forms.py` - implemented two forms for adding comments to products and a form for personal information of the buyer.

`models.py` - models have been developed for registering users, product categories, promotions, product brands, countries of products, products, comments on products and an order model.

`tests.py` - contains more than fifty different tests to check the correct operation of the application.

`urls.py` - the various routes that are used in the application are indicated.

`utils.py` - two functions have been developed to send emails to users to confirm registration and to the administrator to confirm the order.

`views.py` - the file contains all the functions for the correct operation of the server part of the application. 

`styles.css` - page style description file.

`script.js` - this file contains all the necessary scripts for the correct operation of the application on the client side.

`basket.html` - in this file, a user's basket for placing an order is developed.

`category_list.html` - the page displays the available products in the selected category. Also, for the convenience of searching, filters by product characteristics have been added.

`email_confirm_order.html` - email template for order confirmation by administrator.

`email_verify.html` - email template for user registration confirmation.

`index.html` - the start page of the application, which contains product categories, available promotions and five random products offered to the user.

`layout.html` - contains markup and template settings for all subsequent html pages.

`login.html` - login page for members loyalty program.

`loyalty.html` - the terms of the loyalty program for users are indicated.

`product.html` - product presentation page, contains a photo, description, comments on the product, its price and the ability to add to favorites and to the basket.

`register.html` - loyalty program member registration form.

`user_account.html` - contains personal information about the user with the possibility of changing it, the size of the discount on products under the loyalty program and a list of favorite products.

`requirements.txt` - 