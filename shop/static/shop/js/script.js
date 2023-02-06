document.addEventListener('DOMContentLoaded', function() {
    document.addEventListener('click', event => {
        const element = event.target;

        // sending filter_form when user clicks on brand filter 
        if (element.id.startsWith('brand_filter_')) {
            let id = element.dataset.id;
            console.log(`btn "brand_filter_${id}" has been clicked`);
            document.getElementById('filter_form').submit();
        }
        
        // sending filter_form when user clicks on country filter 
        if (element.id.startsWith('country_filter_')) {
            let country_name = element.dataset.id;
            console.log(`btn "country_filter_${country_name}" has been clicked`);
            document.getElementById('filter_form').submit();
        }

        if (element.id.startsWith('pag_btn_')) {
            let page_num = element.dataset.id;
            console.log(page_num);
            document.getElementById('requested_page').value = page_num;
            document.getElementById('filter_form').submit();
        }

        // cleaning localStorage user clicks on logo
        if (element.id.startsWith('brand_logo') || element.id.startsWith('category_') || element.id.startsWith('name_search_btn')) {
            console.log('brand_logo has been clicked');
            localStorage.removeItem('name_search');
            localStorage.removeItem('price_from');
            localStorage.removeItem('price_to');
            localStorage.removeItem('CheckboxChecked');
            localStorage.removeItem('category');
        }

        // editing user watchlist
        if (element.id.startsWith('watchlist-edit-')) {
            let id = element.dataset.id;
            console.log(`btn "watchlist-${id}" has been clicked`);
            edit_watchlist(id);
        }

        // adding product to the basket
        if (element.id.startsWith('buy_product_')) {
            // if basket empty, create array
            let list = JSON.parse(localStorage.getItem("buy_product"));
            if(list == null) {
                list = []
            };

            // getting element id
            let data = element.dataset.id;

            // if product already in basket
            if (list.indexOf(data) != -1) {
                localStorage.setItem("buy_product", JSON.stringify(list));
            } else {
                // adding product to the basket
                list.push(data)
                localStorage.setItem("buy_product", JSON.stringify(list));
            }
        }

        // rendering basket
        if (element.id.startsWith('basket')) {
            let list = JSON.parse(localStorage.getItem("buy_product"));
            // adding data to the basket form in layout.html
            document.getElementById("basket_list").value = list;
            document.getElementById("basket_form").submit();
        }

        // remove product amount in the basket
        if (element.id.startsWith('remove_amount_')) {
            // getting product id
            let id = element.dataset.id;
            // getting product amount
            let value = document.getElementById(`amount_${id}`).value;
            // set new product amount
            let newValue = value - 1;

            if (newValue === 0) {
                // remove amount from localstorage
                localStorage.removeItem(`amount_${id}`);

                let list = JSON.parse(localStorage.getItem("buy_product"));
                let index = list.indexOf(id)
                // remove one element by index from basket
                list.splice(index, 1)

                // adding data to the basket form in layout.html and send it
                if(list.length === 0) {
                    localStorage.removeItem('buy_product');
                    document.getElementById("basket_form").submit();
                } else {
                    localStorage.setItem("buy_product", JSON.stringify(list));
                    document.getElementById("basket_list").value = list;
                    document.getElementById("basket_form").submit();
                }
            } else {
                document.getElementById(`amount_${id}`).value = newValue;
                localStorage.setItem(`amount_${id}`, newValue);
            }
            // call function that counts total price
            total_count()
        }

        // add product amount in the basket
        if (element.id.startsWith('add_amount_')) {
            let id = element.dataset.id;
            // getting max amount of product
            let max_amount = element.dataset.amount;
            let value = document.getElementById(`amount_${id}`).value;
            let num = Number(value)

            // add one to product amount
            let newValue = num + 1;

            // if new amount is bigger than we have in db
            if(newValue > max_amount) {
                alert('Sorry, but this quantity cannot be ordered.');
            } else {
                document.getElementById(`amount_${id}`).value = newValue;
                localStorage.setItem(`amount_${id}`, newValue);
                // call function that counts total price
                total_count()
            }
        }

        // Adding category id to localstorage
        if (element.id.startsWith('category_')) {
            let id = element.dataset.id;
            localStorage.setItem("category", id);
        }

        // Adding name request to localstorage
        if (element.id.startsWith('name_search_btn')) {
            let input = document.getElementById("name_search").value;
            localStorage.setItem("name_search", input);
        }

        // cleaning local storage
        if (element.id.startsWith('clear_basket')) {
            localStorage.clear();
            document.getElementById("basket_form").submit();
        }

        // cleaning local storage
        if (element.id.startsWith('make_order')) {
            localStorage.clear();
        }
    })
    return false;
})


// from stackoverflow
// saving checkbox status to localstorage
$('input[data-id]').on('input', function() {
    let aChecked = [];
    $('input[data-id]:checked').each(function() { aChecked.push($(this).data('check')); });
    localStorage.setItem('CheckboxChecked', aChecked.join(';'));
});


// from stackoverflow
// getting checkbox status from localstorage after reload page
$(document).ready(function() {
    if (localStorage.getItem('CheckboxChecked')) {
        $('input[data-id]').prop('checked', false);
        let aChecked = localStorage.getItem('CheckboxChecked').split(';');
        aChecked.forEach(function(str) { $('input[data-id="' + str + '"]').prop('checked', true); });
    }
});


// saving price limits, search name to localstorage and getting it after page reload
document.getElementById("name_search").value = localStorage.getItem('name_search');
document.getElementById("name_query").value = localStorage.getItem('name_search');
document.getElementById("price_from").value = localStorage.getItem('price_from');
document.getElementById("price_to").value = localStorage.getItem('price_to');
document.getElementById("category").value = localStorage.getItem('category');


// saving price limits to localstorage
function handleInput()
{
  localStorage.setItem('price_from', document.getElementById("price_from").value);
  localStorage.setItem('price_to', document.getElementById("price_to").value);
}

// from stackoverflow
// sending filter_form when user clicks on 'Enter'
document.getElementById('filter_form').addEventListener('keydown', function(e){
  if (e.keyCode == 13) {
    this.submit();
  }
})

function edit_watchlist(id) {
    fetch(`watchlist/${id}`, {
        method: 'POST',
    })
    .then(response => response.json())
    .then(result => {
    let watchlist_status = result.watchlist_status;
    if (watchlist_status == false) {
        document.getElementById(`addtowatchlist-${id}`).style.display = 'block';
        document.getElementById(`dellfromwatchlist-${id}`).style.display = 'none';
    } else {
        document.getElementById(`addtowatchlist-${id}`).style.display = 'none';
        document.getElementById(`dellfromwatchlist-${id}`).style.display = 'block';
    }
    });
}


// checking users order input
function make_order() {
    if(document.getElementById('id_first_name').value === '') {
        alert('Invalid input');
    }
    else if(document.getElementById('id_last_name').value === '') {
        alert('Invalid input');
    }
    else if(document.getElementById('id_address').value === '') {
        alert('Invalid input');
    }
    else if(document.getElementById('id_email').value === '') {
        alert('Invalid input');
    }
    else if(document.getElementById('id_phone_number').value === '') {
        alert('Invalid input');
    } else {
        document.getElementById("order_form").submit();
    }
}


// counting total value in basket
function total_count() {
    let list = JSON.parse(localStorage.getItem("buy_product"));

    // Getting amount of products
    for(let index in list) {
        let id = list[index];
        let amount = localStorage.getItem(`amount_${id}`);
        if (amount === null) {
            document.getElementById(`amount_${id}`).value = '1';
        } else {
            document.getElementById(`amount_${id}`).value = localStorage.getItem(`amount_${id}`)
        }
    }

    let TOTAL = 0;
    let discount = 0;

    if (document.getElementById('discount')) {
        discount = document.getElementById('discount').innerHTML
    }

    for(let index in list) {
        let id = list[index]
        let amount = document.getElementById(`amount_${id}`).value;
        let price = document.getElementById(`price_${id}`).innerHTML;
        TOTAL = TOTAL + (amount * price * ((100 - discount) / 100));
    }
    document.getElementById('total_price').innerHTML = `Total: ${TOTAL.toFixed(2)}$`;
}
