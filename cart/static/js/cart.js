$(document).ready(function () {
    var prices = null;
    var csrf_token = $("input[name='csrfmiddlewaretoken']").val()

    function fetchPrices() {
        $.ajax({
            url: '/price_list/',
            type: 'GET',
            success: function (response) {
                prices = response;
                calculateTotals(prices);
            },
            error: function (xhr, status, error) {
                console.error('Error fetching price list:', error);
            }
        });
    }

    function calculateTotals(prices) {
        $('.cart-item').each(function () {
            var documentId = $(this).attr('id').split('-')[2];
            var size = $(this).find(`#document-size-${documentId}`).val();
            var color = $(this).find(`#document-color-${documentId}`).val();
            var type = $(this).find(`#document-type-${documentId}`).val();
            var extra = $(this).find(`#document-extra-${documentId}`).val();
            var quantity = parseInt($(this).find(`#document-quantity-${documentId}`).val(), 10);
            var pages = parseInt($(`#document-pages-${documentId}`).text(), 10);

            if(type !== 'ONE_SIDE' && pages % 2 !== 0) {
                pages += 1;
            }

            if(type === 'BOTH_SIDES') {
                pages = Math.max(1, pages / 2);
            } else if(type === 'TWO_PAGES_PER_SIDE') {
                pages = Math.max(1, pages / 4)
            }

            var total = (prices[size] + prices[color] + prices[type] + prices[extra]) * pages * quantity;

            $(this).find(`#document-price-${documentId}`).text(total + ' تومان');
        });
    }

    fetchPrices();

    $(document).on('change', '.cart-item select, .cart-item input[type=text]', function () {
        calculateTotals(prices);
    });

    $('#add-file-button').on('click', function (e) {
        e.preventDefault();
        $('#file-input').click();
    });

    $('#file-input').on('change', function () {
        var file = this.files[0];
        if (file && file.type === 'application/pdf') {
            var formData = new FormData();
            formData.append('pdf_file', file);

            $.ajax({
                url: '/cart/upload/',
                type: 'POST',
                headers: {
                    'X-CSRFToken': csrf_token
                },
                data: formData,
                contentType: false,
                processData: false,
                success: function (response) {
                    if (response.ok) {
                        var optionDisabled = (response.pages == 1) ? 'disabled':'';
                        var newRow = `
                                <tr id="row-document-${response.id}" class="cart-item">
                                    <td class="trash">
                                        <a href="" data-document="${response.id}" class="remove">
                                            <i class="ri-delete-bin-line"></i>
                                        </a>
                                    </td>
                                    <td class="document-name">
                                        <a href="">${response.filename}</a>
                                    </td>
                                    <td class="document-pages">
                                        <a id="document-pages-${response.id}">${response.pages}</a>
                                    </td>
                                    <td class="document-size">
                                        <select id="document-size-${response.id}">
                                            <option value="A3">A3</option>
                                            <option value="A4" selected>A4</option>
                                            <option value="A5">A5</option>
                                        </select>
                                    </td>
                                    <td class="document-color">
                                        <select id="document-color-${response.id}" style="width: 110px;">
                                            <option value="WB" selected>سیاه سفید</option>
                                            <option value="C50">رنگی 50 درصد</option>
                                            <option value="C100">رنگی 100 درصد</option>
                                        </select>
                                    </td>
                                    <td class="document-type">
                                        <select id="document-type-${response.id}">
                                            <option value="ONE_SIDE" selected>یک رو</option>
                                            <option value="BOTH_SIDES"${optionDisabled}>دو رو</option>
                                            <option value="TWO_PAGES_PER_SIDE" ${optionDisabled}>دو در یک</option></option>
                                        </select>
                                    </td>
                                    <td class="document-extra">
                                        <select id="document-extra-${response.id}" style="width: 110px;">
                                            <option value="NO_BINDING" selected>بدون صحافی</option>
                                            <option value="COVERED_NO_PUNCH">کاور شده بدون پانچ</option>
                                            <option value="COVERED_PUNCHED">کاور شده با پانچ</option>
                                        </select>
                                    </td>
                                    <td class="document-quantity">
                                        <div class="input-counter">
                                            <input type="text" value="1" class="text-center w-50" id="document-quantity-${response.id}">
                                        </div>
                                    </td>
                                    <td class="document-subtotal">
                                        <span class="subtotal-amount" id="document-price-${response.id}">9900 تومان</span>
                                    </td>
                                </tr>`;
                        $('.cart-table tbody').append(newRow);
                        calculateTotals(prices);
                        var currentCount = parseInt($('#cart-counter').text(), 10) || 0;
                        currentCount += 1;

                        if ($('#cart-counter').length === 0) {
                            var counterHtml = `<span id="cart-counter">${currentCount}</span>`;
                            $('.counter-container').append(counterHtml);
                        } else {
                            $('#cart-counter').text(currentCount);
                        }
                    } else {
                        alert(response.error);
                    }
                },
                error: function (xhr, status, error) {
                    alert('ارور: ' + error);
                }
            });
        } else {
            alert('لطفا یک فایل pdf. انتخاب کنید');
        }
    });

    $('.cart-table tbody').on('click', '.remove', function (e) {
        e.preventDefault();

        var documentId = $(this).data('document');

        $.ajax({
            url: '/cart/delete/',
            type: 'POST',
            data: {
                'document_id': documentId,
                'csrfmiddlewaretoken': csrf_token
            },
            success: function (response) {
                if (response.ok) {
                    $('#row-document-' + documentId).remove();
                    var currentCount = parseInt($('#cart-counter').text(), 10) - 1;
                    if (currentCount <= 0) {
                        $('#cart-counter').remove();
                    } else {
                        $('#cart-counter').text(currentCount);
                    }
                    calculateTotals(prices); // Recalculate totals after removing a row
                } else {
                    alert(response.error);
                }
            },
            error: function (xhr, status, error) {
                alert('مشکلی در حذف پیش آمده است لطفا صفحه را رفرش کرده و مجددا تلاش کنید');
            }
        });
    });

    $('.save-cart').on('click', function (e) {
        e.preventDefault();

        var cartData = {};

        $('.cart-item').each(function () {
            var documentId = $(this).attr('id').split('-')[2];
            var options = {
                page_size: $(this).find(`#document-size-${documentId}`).val(),
                print_color: $(this).find(`#document-color-${documentId}`).val(),
                print_type: $(this).find(`#document-type-${documentId}`).val(),
                extra_options: $(this).find(`#document-extra-${documentId}`).val(),
                quantity: $(this).find(`#document-quantity-${documentId}`).val()
            };
            cartData[documentId] = options;
        });

        $.ajax({
            url: '/cart/save/',
            type: 'POST',
            data: JSON.stringify(cartData),
            contentType: 'application/json',
            headers: {
                'X-CSRFToken': csrf_token
            },
            success: function (response) {
                if (response.ok) {
                    var $button = $('.save-cart');
                    $button.text('ذخیره شد');
                    $button.prop('disabled', true);

                    setTimeout(function () {
                        $button.prop('disabled', false);
                        $button.text('ذخیره سبد خرید');
                    }, 3000);
                } else {
                    alert(response.error);
                }
            },
            error: function (xhr, status, error) {
                alert('مشکلی در ذخیره سبد خرید پیش آمده است.');
            }
        });
    });
});