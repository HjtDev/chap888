$(document).ready(function () {

    var csrf_token = $("input[name='csrfmiddlewaretoken']").val()

    function updateFinalPrice() {
        // Get values from the elements and remove " تومان"
        var totalPrice = parseInt($('#total-price').text().replace(' تومان', ''), 10);
        var discount = parseInt($('#discount').text().replace(' تومان', ''), 10);
        var postPrice = $('#shipment').is(':checked') ? parseInt($('#post-price').text().replace(' تومان', ''), 10) : 0;

        // Calculate final price
        var finalPrice = totalPrice + postPrice - discount;

        // Check if final price is zero or less
        if (finalPrice <= 0) {
            $('#final-price').text('رایگان'); // Display "رایگان"
        } else {
            $('#final-price').text(finalPrice + ' تومان'); // Display the calculated price
        }
    }

    // Initial calculation on page load (without shipping cost)
    updateFinalPrice();

    // Update final price when shipment checkbox changes
    $('#shipment').change(function () {
        // Show/hide shipping fields
        if ($(this).is(':checked')) {
            $('.shipping-field').show();  // Show shipping fields when checked

            // Add required attributes to the relevant inputs
            $('#province').attr('required', 'required');
            $('#city').attr('required', 'required');
            $('#address').attr('required', 'required');
            $('#postal_code').attr('required', 'required');
        } else {
            $('.shipping-field').hide();  // Hide shipping fields when unchecked

            // Remove required attributes from the relevant inputs
            $('#province').removeAttr('required');
            $('#city').removeAttr('required');
            $('#address').removeAttr('required');
            $('#postal_code').removeAttr('required');

            // Reset values of the input fields
            $('#province').val('');
            $('#city').val('');
            $('#address').val('');
            $('#postal_code').val('');

            // Uncheck the special address checkbox
            $('#ship-special-address').prop('checked', false);
        }

        updateFinalPrice(); // Recalculate final price when checkbox state changes
    });


    $('#ship-special-address').change(function () {
        if ($(this).is(':checked')) {
            $('#post-price').text('0 تومان');
        } else {
            $('#post-price').text('25000 تومان'); // Adjust this to your original price if needed
        }

        updateFinalPrice();
    });

    $('#conditions').change(function () {
        if ($(this).is(':checked')) {
            $('#pay-button').prop('disabled', false);
        } else {
            $('#pay-button').prop('disabled', true);
        }
    });

    $('#pay-button').click(function (e) {
        e.preventDefault();
        $('#form-submit').click();
    });

    $('#submit-discount').click(function (e) {
        e.preventDefault();

        // Retrieve values from inputs
        var phone = $('#phone').val().trim();
        var token = $('#discount-token').val().trim();
        var totalPrice = parseInt($('#total-price').text().replace(' تومان', ''), 10);

        // Validate phone number
        if (!phone || phone.length !== 11 || !phone.startsWith('09')) {
            $('#discount-result').text('لطفا شماره تلفن معتبر وارد کنید.').show();
            return; // Stop further execution
        }

        // Prepare data for AJAX request
        var data = {
            'phone': phone,
            'token': token,
            'price': totalPrice
        };

        // Send AJAX request
        $.ajax({
            url: '/checkout/check_discount/',  // Replace with your URL pattern
            type: 'POST',
            data: data,
            headers: {
                'X-CSRFToken': csrf_token
            },
            success: function (response) {
                if (response.ok) {
                    // Update discount result and total discount value
                    $('#discount').text(response.discount + ' تومان');
                    $('#discount-result').text('تخفیف اعمال شد!').show();
                    $('#form-token').val(token);
                    updateFinalPrice();
                } else {
                    // Show error message from response
                    $('#discount-result').text(response.error).show();
                }
            },
            error: function () {
                $('#discount-result').text('خطا در ارسال درخواست. لطفا دوباره تلاش کنید.').show();
            }
        });
    });
});