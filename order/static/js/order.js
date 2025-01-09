$(document).ready(function () {
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
        } else {
            $('.shipping-field').hide();  // Hide shipping fields when unchecked
        }
        updateFinalPrice(); // Recalculate final price when checkbox state changes
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
        alert('pressed');
    })
});