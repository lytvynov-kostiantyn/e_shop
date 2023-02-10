document.getElementById("id_email").setAttribute("disabled", "disabled");

document.addEventListener('DOMContentLoaded', function() {
document.addEventListener('click', event => {
    const element = event.target;

    if (element.id.startsWith('btn_watchlist_hide')) {
        console.log('hide')
        document.getElementById("btn_watchlist_show").style.display = "block";
        document.getElementById("btn_watchlist_hide").style.display = "none";
        document.getElementById("watchlist_container").style.display = "none";
    }

    if (element.id.startsWith('btn_watchlist_show')) {
        console.log('show')
        document.getElementById("btn_watchlist_hide").style.display = "block";
        document.getElementById("btn_watchlist_show").style.display = "none";
        document.getElementById("watchlist_container").style.display = "block";
    }
})
return false;
})