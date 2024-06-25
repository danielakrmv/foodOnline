let autocomplete; // Defines an autocomplete variable that will be used to create a new object of type google.maps.places.Autocomplete.

// Define the initAutoComplete() function that is called to initialize the auto-completion of locations.
function initAutoComplete(){
autocomplete = new google.maps.places.Autocomplete(
    // Creates a new object of type google.maps.places.Autocomplete that binds to an HTML element with id 'id_address' and provides auto-completion of locations.
    // Selects an HTML element with id 'id_address' where the user can enter an address.
    document.getElementById('id_address'),
    {
        // The default location types used to predict locations.
        types: ['geocode', 'establishment'],
        // default in this app is "BG" - add your country code
        componentRestrictions: {'country': ['bg']},
    })
// Adds a listener for the 'place_changed' event, which is called when the user selects a location from the provided locations.
autocomplete.addListener('place_changed', onPlaceChanged);
}

// This function is called when the user has already selected a location
function onPlaceChanged (){
    var place = autocomplete.getPlace(); // Gets the selected location from the autocomplete object.

    // Checks if the user has selected a valid location. If not, an error message is set or the data is reset.
    if (!place.geometry){
        document.getElementById('id_address').placeholder = "Start typing...";
    }
    else{
        // console.log('place name=>', place.name)
    }
    // get the address components and assign them to the fields

    // Creates a new object of type google.maps.Geocoder that is used to geocode the entered address.
    var geocoder = new google.maps.Geocoder()
    var address = document.getElementById('id_address').value

    // Sends a request to geocode the entered address and calls the function back when it receives a response from the API.
    geocoder.geocode({'address': address}, function(results, status){

        if(status==google.maps.GeocoderStatus.OK){
            // Retrieves the location coordinates from the geocoding result.
            var latitude = results[0].geometry.location.lat();
            var longitude = results[0].geometry.location.lng();

            $('#id_latitude').val(latitude);
            $('#id_longitude').val(longitude);

            $('#id_address').val(address);
        }
        
    });

    // Loops through the address components and assigns other address data

    for(var i=0; i<place.address_components.length; i++){
        for(var j=0; j<place.address_components[i].types.length; j++){
            // get country
            if(place.address_components[i].types[j] == 'country'){
                $('#id_country').val(place.address_components[i].long_name);
            }
            // get city
            if(place.address_components[i].types[j] == 'locality'){
                $('#id_city').val(place.address_components[i].long_name);
            }
            // get pincode
            if(place.address_components[i].types[j] == 'postal_code'){
                $('#id_pin_code').val(place.address_components[i].long_name);
            }else{
                $('#id_pin_code').val("");
            }
        }
    }
}

$(document).ready(function(){
    // add to cart
    // at the moment I click on the add_to_cart button it will take the respective food_id and the url
    // will send the GET request to this particular url using ajax
    // This is a jQuery selector that binds to all elements with the .add_to_cart class. When one of these items is clicked, the following function is executed:
    $('.add_to_cart').on('click', function(e){
        // This line prevents standard browser behavior, which typically involves reloading the page after submitting a form or performing navigation.
        e.preventDefault();

        // These two lines retrieve the food_id and url data from the data-id and data-url attributes of the element to which the clicked function is bound.
        food_id = $(this).attr('data-id');
        url = $(this).attr('data-url');
        
        // This is jQuery's way of sending an AJAX request. The object passed as an argument sets the query parameters.
        $.ajax({
            // The request type is GET, which means a request is sent to the server to get information.
            type: 'GET',
            url: url,
            // The function that will be executed when the request is successful. The response parameter contains the data returned by the server.
            success: function(response){
                // The status of the response is checked: if response.status is 'login_required', then an information message is displayed and the user is redirected to the login page.
                if(response.status == 'login_required'){
                    swal(response.message, '', 'info').then(function(){
                        window.location = '/login';
                    })
                }else if(response.status == 'Failed'){
                    swal(response.message, '', 'error')
                }
                else{
                    // If the operation is successful, the HTML elements with the IDs #cart_counter and #qty-<food_id> are updated with the information from the response, which includes the number of items in the cart and the number of the item added.
                    $('#cart_counter').html(response.cart_counter['cart_count']);
                    $('#qty-'+food_id).html(response.qty);

                    // subtotal, tax and grand total
                    // The last line calls the applyCartAmounts function, which updates the total price information for the products in the cart, including subtotal, tax, and total.
                    applyCartAmounts(
                        response.cart_amount['subtotal'],
                        response.cart_amount['tax_dict'],
                        response.cart_amount['grand_total']
                    )
                }
            }
        })
    })

    // place the cart item quantity on load
    $('.item_qty').each(function(){
        var the_id = $(this).attr('id')
        var qty = $(this).attr('data-qty')
        $('#'+the_id).html(qty)
    })

    // DECREASE CART
    $('.decrease_cart').on('click', function(e){
        e.preventDefault();
        food_id = $(this).attr('data-id');
        url = $(this).attr('data-url');
        cart_id = $(this).attr('id');

        $.ajax({
            type: 'GET',
            url: url,
            success: function(response){
                if(response.status == 'login_required'){
                    swal(response.message, '', 'info').then(function(){
                        window.location = '/login';
                    })
                }
                else if(response.status == 'Failed'){
                    swal(response.message, '', 'error')
                }else{
                    $('#cart_counter').html(response.cart_counter['cart_count']);
                    $('#qty-'+food_id).html(response.qty);

                    applyCartAmounts(
                        response.cart_amount['subtotal'],
                        response.cart_amount['tax_dict'],
                        response.cart_amount['grand_total']
                    )

                    if(window.location.pathname == '/cart/'){
                        removeCartItem(response.qty, cart_id);
                        checkEmptyCart();
                    }

                }
            }
        })
    })

    // DELETE CART ITEM
    $('.delete_cart').on('click', function(e){
        e.preventDefault();
        
        cart_id = $(this).attr('data-id');
        url = $(this).attr('data-url');
        
        
        $.ajax({
            type: 'GET',
            url: url,
            success: function(response){
                console.log(response)
                if(response.status == 'Failed'){
                    swal(response.message, '', 'error')
                }else{
                    $('#cart_counter').html(response.cart_counter['cart_count']);
                    swal(response.status, response.message, "success")

                    applyCartAmounts(
                        response.cart_amount['subtotal'],
                        response.cart_amount['tax_dict'],
                        response.cart_amount['grand_total']
                    )

                    removeCartItem(0, cart_id);
                    checkEmptyCart();
                } 
            }
        })
    })

    // delete the cart element if the quantity is zero
    function removeCartItem(cartItemQty, cart_id){
        if(cartItemQty <= 0){
            // remove the cart item element
            document.getElementById("cart-item-"+cart_id).remove()
        }
    }

    // Check if the cart is empty
    function checkEmptyCart(){
        var cart_counter = document.getElementById('cart_counter').innerHTML
        if(cart_counter == 0){
            document.getElementById("empty-cart").style.display = "block";
        }
    }

    // apply cart amounts
    function applyCartAmounts(subtotal, tax_dict, grand_total){
        if(window.location.pathname == '/cart/'){
            $('#subtotal').html(subtotal)
            $('#total').html(grand_total)

            // console.log(tax_dict)
            for(key1 in tax_dict){
                // console.log(tax_dict[key1])
                for(key2 in tax_dict[key1]){
                    // console.log(tax_dict[key1][key2])
                    $('#tax-'+key1).html(tax_dict[key1][key2])
                }
            }
        }
    }

    // ADD OPENING HOURS
    $('.add_hour').on('click', function(e){
        e.preventDefault();
        // Retrieve the values ​​from the form fields
        var day = document.getElementById('id_day').value
        var from_hour = document.getElementById('id_from_hour').value
        var to_hour = document.getElementById('id_to_hour').value
        var is_closed = document.getElementById('id_is_closed').checked
        // Retrieve the CSRF token from the hidden field in the HTML form
        var csrf_token = $('input[name=csrfmiddlewaretoken]').val()
        // Get the URL to send the AJAX request
        var url = document.getElementById('add_hour_url').value

        // Checking if the "Closed" option is selected
        if(is_closed){
            is_closed = 'True'
            condition = "day != ''"
        }else{
            is_closed = 'False'
            condition = "day != '' && from_hour != '' && to_hour != ''"
        }

        // Condition to check if all required fields are filled
        // when we pass dynamic var into if condition we need to use eval()
        if(eval(condition)){
            $.ajax({
                // Send an AJAX request to the server
                type: 'POST',
                url: url,
                data: {
                    'day': day,
                    'from_hour': from_hour,
                    'to_hour': to_hour,
                    'is_closed': is_closed,
                    'csrfmiddlewaretoken': csrf_token,
                },
                success: function(response){
                    // If the request is successful
                    if(response.status == 'success'){
                        // Create the HTML for a new row in the hours table
                        if(response.is_closed == 'Closed'){
                            html = '<tr id="hour-'+response.id+'"><td><b>'+response.day+'</b></td><td>Closed</td><td><a href="#" class="remove_hour" data-url="/vendor/opening-hours/remove/'+response.id+'/">Remove</a></td></tr>'; 
                        }else{
                            html = '<tr id="hour-'+response.id+'"><td><b>'+response.day+'</b></td><td>'+response.from_hour+' - '+response.to_hour+'</td><td><a href="#" class="remove_hour" data-url="/vendor/opening-hours/remove/'+response.id+'/">Remove</a></td></tr>';
                        }
                        // Add the new row to the working hours table
                        $(".opening_hours").append(html)
                        // Format reset
                        document.getElementById("opening_hours").reset();
                    }else{
                        // sweet alert for error
                        swal(response.message, '', "error")
                    }
                }
            })
        }else{
            swal('Please fill all fields', '', 'info')
        }
    });

    // REMOVE OPENING HOURS

    $(document).on('click', '.remove_hour', function(e){
        e.preventDefault();
        url = $(this).attr('data-url');

        $.ajax({
            type: 'GET',
            url: url,
            success: function(response){
                if(response.status == 'success'){
                    document.getElementById('hour-'+response.id).remove()  
                }
            }
        })
    })

    // document ready close
});