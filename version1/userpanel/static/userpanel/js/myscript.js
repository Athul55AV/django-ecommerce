

$('.plus-cart').click(function(){
    var id=$(this).attr("pid").toString();
    var eml = $(this).closest('.quantity-container').find('.quantity')[0];
    console.log("pid =",id)
    $.ajax({
        type:"GET",
        url:"/pluscart",
        data:{
            prod_id:id
        },
        success:function(data){
            if (data.status === 'warning') {
                alert(data.message);
            } else {
                console.log("data =",data);
                eml.innerText=data.quantity
                document.getElementById("amount").innerText=data.amount
                document.getElementById("totalamount").innerText=data.totalamount
            }

        }

    })
})

$('.minus-cart').click(function(){
    var id=$(this).attr("pid").toString();
    var eml = $(this).closest('.quantity-container').find('.quantity')[0];
    $.ajax({
        type:"GET",
        url:"/minuscart",
        data:{
            prod_id:id
        },
        success:function(data){
            eml.innerText=data.quantity
            document.getElementById("amount").innerText=data.amount
            document.getElementById("totalamount").innerText=data.totalamount

        }

    })
})

$('.remove-cart').click(function(){
    var id=$(this).attr("pid").toString();
    var eml = this
    $.ajax({
        type:"GET",
        url:"/removecart",
        data:{
            prod_id:id
        },
        success:function(data){
            document.getElementById("amount").innerText=data.amount
            document.getElementById("totalamount").innerText=data.totalamount
            $(eml).closest('tr').remove();
            if (data.cart_count > 0) {
                $('#cart-count').text(data.cart_count);
            } else {
                $('#cart-count').text('');
            }
        }

    })
})


$('.plus-wishlist').click(function(){
    var id=$(this).attr("pid").toString();
    $.ajax({
        type:"GET",
        url:"/pluswishlist",
        data:{
            prod_id:id
        },
        success:function(data){
            window.location.href = `http://127.0.0.1:8000/productdetail/${id}`

        }

    })
})

$('.minus-wishlist').click(function(){
    var id=$(this).attr("pid").toString();
    $.ajax({
        type:"GET",
        url:"/minuswishlist",
        data:{
            prod_id:id
        },
        success:function(data){
            window.location.href = `http://127.0.0.1:8000/productdetail/${id}`

        }

    })
})

$('.remove-wishlist').click(function(){ 
    var id = $(this).attr("pid").toString();
    var eml = this;
    $.ajax({
        type: "GET",
        url: "/removewishlist", 
        data: {
            prod_id: id
        },
        success: function(data) {
            $(eml).closest('tr').remove();
            if (data.wishlist_count > 0) {
                $('#wishlist-count').text(data.wishlist_count);
            } else {
                $('#wishlist-count').text('');
            }
        }
    })
})

$('.cancel-order').click(function(){ 
    var orderId = $(this).attr("pid");
    var csrfToken = $('#csrf_token').val();
    $.ajax({
        type: "POST",
        url: "/cancelorder/", 
        data: {
            order_id: orderId,
            csrfmiddlewaretoken: csrfToken
        },
        success: function(data) {
            location.reload();
        }
    })
})

$('.return-order').click(function(){ 
    var orderId = $(this).attr("pid");
    var csrfToken = $('#csrf_token').val();
    $.ajax({
        type: "POST",
        url: "/returnorder/", 
        data: {
            order_id: orderId,
            csrfmiddlewaretoken: csrfToken
        },
        success: function(data) {
            location.reload();
        }
    })
})

