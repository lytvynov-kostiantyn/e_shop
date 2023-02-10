document.getElementById("order_list").value = JSON.parse(localStorage.getItem("buy_product"));

window.onload = function() {
    total_count()
};