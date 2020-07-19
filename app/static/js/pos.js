$(document).ready(function(){
	setTimeout(loader_destroy,1000);
	autoLoader();
	
	$(window).on("resize",function(){
		scollActiveTabIntoView();
	});

	nav_module = window.location.pathname.split("/")[1];
	if(nav_module)
		$("#"+nav_module).addClass("mm-active");

	$(".cls_order_details").on("click",clsOrderDetails);
   	$("#import_file").on("change",sendFile);
});

function sendFile(){
	$("#products_creator").submit();
}

function clsOrderDetails(){
	$("#"+$(this).attr("id")+".order-details").hide();
}

function historyBack(){
	window.history.go(-1);
}

function resetAutoLoaderBinds(){
	$(document).unbind("keydown",hotKeys);

	$(".product_list_view").unbind("click",switchView);
	$(".product_detail_view").unbind("click",switchView);
	
	$(".product_search_input").unbind("focus",search);
	
	$(".line_item").unbind("click",lineItemAction);
	
	$(".add_order_tab").unbind("click",createOrder);

	$(".tab").unbind("click",activeOrderTab);
	$(".product_adder").unbind("click",addLineItem);
	$(".order_cancel").unbind("click",cancelOrder);
	$(".select_customer").unbind("click",selectCustomer);
	$(".line_remove").off("click",voidLineItem);
	$(".line_delete").off("click",removeLineItem);
	$(".qty_mod").off("change",setItemQty);
	$(".disc_mod").off("change",setItemDiscount);
	$(".variant_options").off("change",setProductVariant)

	// $("#pos_order.active .avail_disc").unbind("change",setDiscountMultiplier);
	// $("#pos_order.active .active_changer").unbind("change",discountLineItem);
}

function autoLoader(){

	resetAutoLoaderBinds();//reset autoloader binds
	curFormat();
	$(document).bind("keydown",hotKeys);
	$(".pos_category_filter").bind("change",filterCategory);

	$(".product_list_view").bind("click",switchView);
	$(".product_detail_view").bind("click",switchView);
	
	$(".product_search_input").bind("focus",search);
	
	$(".line_item").bind("click",lineItemAction);
	
	$(".add_order_tab").bind("click",createOrder);

	$(".tab").bind("click",activeOrderTab);
	$(".product_adder").bind("click",addLineItem);
	$(".order_cancel").bind("click",cancelOrder);
	$(".select_customer").bind("click",selectCustomer);
	$(".line_remove").on("click",voidLineItem);
	$(".line_delete").on("click",removeLineItem);
	$(".qty_mod").on("change",setItemQty);
	$(".disc_mod").on("change",setItemDiscount);
	$(".variant_options").on("change",setProductVariant)

	// $("#pos_order.active .avail_disc").bind("change",setDiscountMultiplier);
	// $("#pos_order.active .active_changer").bind("change",discountLineItem);


	$("#pos_order.active #pos_product_view,#pos_order.active #pos_cart_nav,#pos_order.active #pos_payment_tab").click(function(){
		$("#avail_disc").hide();
		$("#pos_cart_keys > ul > ul").remove();
	});

	$(".line_item").children(":not('#line_discount')").click(function(){
		$("#avail_disc").hide();
		$("#pos_cart_keys > ul > ul").remove();
	});

	doToolTip();
	
	checkPayerActive()//verify that items are added to the cart and disable/enable payment button accordingly

	keepProductView();
	setActiveTab();

	keyBoard();
	zeroNoneDiscount();
}

function setProductVariant(){
	var _values = $(this).val().split(":");
	var _name = _values[2];
	var _parent = _values[1];
	var _price = _values[3];
	$(".product_"+_parent).attr("name",_name);
	$(".product_"+_parent+" .product_adder").attr("name",_name);
	$(".product_"+_parent+" .product_adder").attr("price",_price);
	$(".product_"+_parent+" .the_price").attr("data",_price).html("$"+_price);
}

function setItemQty(){
	var order_id = $(this).attr("order");
	var line_id = $(this).attr("line");
	var line_name = $(this).attr("name");
	
	$.post("/pos/orderline/",{"order":order_id,"line":line_id,"qty":$(this).val(),"name":line_name,"company_id":company_,"add_qty":1},function(data){
			$("#pos_content").html(data);
			autoLoader();
	});
}

function setItemDiscount(){
	var order_id = $(this).attr("order");
	var line_id = $(this).attr("line");
	var item_code = $(this).attr("code");
	var line_name = $(this).attr("name");
	
	$.post("/pos/orderline/",{"order":order_id,"line":line_id,"discount":$(this).val(),"name":line_name,"item_code":item_code,"company_id":company_,"add_discount":1},function(data){
			$("#pos_content").html(data);
			autoLoader();
	});
}

function removeLineItem(){
	var line_id = $(this).attr("line");
	var order_id = $(this).attr("order");
	$.post('/pos/orderline/remove/',{"line":line_id,"order":order_id},function(resp){
		$("#pos_content").html(resp);
		autoLoader();
	}); 
}

function voidLineItem(){
	var line_id = $(this).attr("line");
	var order_id = $(this).attr("order");
	$.post('/pos/orderline/void/',{"line":line_id,"order":order_id},function(resp){
		$("#pos_content").html(resp);
		autoLoader();
	}); 
}

function checkPayerActive(){
	var payee = $("#pos_order.active .payment_selector");//active payee
	var inactive_payee =  $("#pos_order.inactive .payment_selector");
	var cart_items = $("#pos_order.active .pos_cart_items_list .line_item");

	if(cart_items.length > 0)
		payee.attr("disabled",false);
	else
		payee.attr("disabled",true);

	payee.bind("click",acceptPayment);
	inactive_payee.unbind("click");
}


function reInitPaymentAccepter(order){
	setTimeout(function(){
		$("#pos_order[order='"+order+"'] .payment_selector").click();
	},200);
}


function acceptPayment(){
	var amount_due = $("#pos_order.active .ext_total").attr("val");
	var order_id = $("#pos_order.active").attr("order");
	var pos_ = $("#pos_order.active").attr("pos_");
	var pos_id = $("#pos_order.active").attr("pos_id");
	var customer = $("#pos_order.active .select_customer").attr("customer");
	var user_id = $("#user_id").val();
	
	$.post("/pos/order/payment/",{"payment":"dialog","amount_due":amount_due,"customer":customer,"order":order_id,"company":company_,"pos_":pos_,"pos_id":pos_id,"user":user_id},function(data){
		$("body").append('<div class="widget" order="'+order_id+'" id="payment_widget"><span class="widget_cls"  data-placement="left" title="Cancel Payment"><i class="fa fa-times-circle fa-2x"></i></span><span class="widget_error"></span><div class="widget-body"></div>');
		$("#payment_widget .widget-body").html(data);
	curFormat();

		$("#payment_widget").show("slow");

		$(".headfixed").fixHeader();
		
		$("#payment_type button.ptb").bind("click",addPaymentLine);
		$("#pos_payment_keypad_keys .key").bind("click",paymentScreenKeyBoard);
		testPaymentprocessor();//enable payment processor function if payment lines exists at startup
		
		$(".payment_line").on("click",makeLineActive);//init payment line functions
		$(".line_dump").on("click",removePaymentLine);//init payment line functions
		$(".payment_amount_entry").on("focus",tabLineActive);//init payment line functions
		
		$("#receipt_header").html($("#receipt_header").text());//render server return value as html
		$("#receipt_footer").html($("#receipt_footer").text());//render server return value as html

		$("#payment_widget .widget_cls").click(function(){
			$("#payment_widget").remove();
			$(".widget_error").html("");				
		});

		$(".error_cls").click(function(){
			$("#payment_widget").remove();
		});

		$(".select_customer").bind("click",selectCustomer);

		doToolTip();

	});
}

function checkNoPaymentAdded(){
	var null_payment_note = $("#no_payment");
	if(null_payment_note.length > 0)
		return true;
	else
		return false;
}

function getPaymentAmountDue(){
	var amount_due = "0.00";
	var payment_line = $(".payment_line");

	if(payment_line.length < 1){
		amount_due = parseFloat($("#payment_balance").val()).toFixed(2);
	}else{

		var last_pay_line = $(".payment_line:last-child");
		var lpad = parseFloat(last_pay_line.children("#payment_due").attr("val")); //amount due on last payment line
		var lptd = last_pay_line.children("td").children(".payment_amount_entry").val(); //cash tendered on last payment line

		if(lptd == "")
			lptd = 0;


		var ramd = parseFloat(lpad - lptd).toFixed(2);//real amount due

		if(ramd <= 0 )
			amount_due = "0.00";
		else
			amount_due = ramd;

	}

	return amount_due;
}


function addPaymentLine(){
	var method = $(this).attr("method");
	var method_id = $(this).val();
	var pc_ = $(this).attr("id"); //payment css class 
	var amount_due = getPaymentAmountDue();
	var change = $("#payment_change").val();
	var line_id = method+"_"+autoGenId(9);
	var payment_line = '<tr id="payment_line" class="payment_line '+pc_+' active" id_="'+line_id+'" method="'+method_id+'"> <td id="line_dump"  title="Remove Payment" class="line_dump"><i class="fa fa-trash"></i></td> <td id="payment_method">'+method+'</td> <td id="payment_due" class="active" val="'+amount_due+'">'+amount_due+'</td> <td id="payment_received" class="active"> <input type="text" id="payment_amount_entry" class="payment_amount_entry active" placeholder="0.00" /> </td> <td id="payment_change" class="active">'+change+'</td> </tr>';

	$(".payment_line #payment_received .payment_amount_entry").removeClass("active");//remove active flag from entry field so user can follow
	$(".payment_line #payment_received .payment_amount_entry").unbind("keyup",paymentKeyBoard);//remove onclick bind to prevent dup execution
	$(".payment_line").children("td").removeClass("active");//remove active flag from previous entries

	if(checkNoPaymentAdded())//verify that no payment as yet been added
		$("#no_payment").remove();//remove no payment notification

	$("#payment_tendered tbody").append(payment_line);//add a payment line
	$(".payment_line").bind("click",makeLineActive);
	$(".line_dump").bind("click",removePaymentLine);
	$(".payment_amount_entry").on("focus",tabLineActive);
	// $(".payment_amount_entry.active").bind("change",savePayment);
	$(".payment_amount_entry.active").focus();
	payment_entry = document.getElementById($(".payment_amount_entry.active").attr("id"));
	if(isFocused(payment_entry))
		$(".payment_line.active #payment_received.active .payment_amount_entry").bind("keyup",paymentKeyBoard);//bind keyboard to currently active payment line

	$(".payment_line.active #payment_received.active .payment_amount_entry").on("keydown",deActivePaymentEntry);//bind keyboard to currently active payment line

}

function savePayment(){
	var line = $(".payment_line.active");// active payment line
	var amount_due = parseFloat(line.children("#payment_due").attr("val"));
	var amount_received = parseFloat($(this).val());
	var payment_id = line.attr("id_");
	var payment_method = parseInt(line.attr("method"));
	var payment_change = parseFloat(line.children("#payment_change").text());
	var pos_id = $("#pos_order.active").attr("pos_");
	var order = $("#pos_order.active").attr("order");

	$.post("/pos/order/payment/save/",{"pos_":pos_id,"payment_id":payment_id,"amount_due":amount_due,"amount_received":amount_received,"order":order,"payment_method":payment_method,"change":payment_change},function(data){
		// $("#payment_tendered tbody").html(data);
	});
}

function autoGenId(len){
	var id = "";
	var cypher_ = [];
	var cypher = "0123456789?@#$!%&ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz";
	
	for(var i = 0;i < cypher.length;i++)
		cypher_.push(cypher[i]);

	for(var i = 0;i < len;i++)
		id += cypher_[ (Math.floor(Math.random() * cypher.length)) ];

	return id;
}

function removePaymentLine(){
	var line = $(this).parent();
	var line_id = line.attr("id_");
	var pos_id = $("#pos_order.active").attr("pos_");
	var order = $("#pos_order.active").attr("order");

	$.post("/pos/order/payment/remove/",{"pos_":pos_id,"payment":line_id,"order":order},function(data){
		// $("#payment_tendered tbody").html(data);
		line.remove();
		testPaymentprocessor();
	});

	// console.log("removing");
}

function tabLineActive(){
	$(this).parent().parent().click();
}

function makeLineActive(){
	$(".payment_line #payment_received .payment_amount_entry").unbind("keyup",paymentKeyBoard);//remove event bind to prevent dup execution
	$(".payment_line #payment_received .payment_amount_entry.active").unbind("change",savePayment);//remove even bind to prevent dup execution

	$(".payment_line").children("td").removeClass("active");//remove active flag from previous entries
	$(".payment_line #payment_received .payment_amount_entry").removeClass("active");//remove active flag from entry field so user can follow

	$(this).addClass("active");
	$(this).children("td").addClass("active");

	$(".payment_line.active #payment_received.active .payment_amount_entry").addClass("active");
	// $(".payment_amount_entry.active").focus();

	$(".payment_line.active #payment_received.active .payment_amount_entry.active").bind("keyup",paymentKeyBoard);//bind keyboard to currently active payment line
	$(".payment_line.active #payment_received.active .payment_amount_entry.active").on("keydown",deActivePaymentEntry);//bind keyboard to currently active payment line
	$(".payment_line #payment_received .payment_amount_entry.active").bind("change",savePayment);
}


function deActivePaymentEntry(e){
	var key = e.keyCode;
	if(key == 13 || key == 9 || key == 27){
		$(this).removeClass("active");
		$(this).parent().siblings().removeClass("active");
		$(this).blur();
	}
}

function paymentScreenKeyBoard(){
	var key = $(this).attr("key");
	var tended_ = $(".payment_amount_entry.active");

	var new_val = 0;
	var val_ = 0;

	var specialKeys =  ["_dec","_del"];
		
	if($.inArray(key,specialKeys) !== -1){
		val_ = applyScreenSpecialKey(key,tended_.val());
	}else{
		val_ = tended_.val()+key;
	}
			
	new_val = onlyNumbers(val_);
	
	tended_.val(new_val);
	
	tallyPayments();
}

function paymentKeyBoard(e){

	var key = e.keyCode;
	var tended_ = $("#payment_received.active .payment_amount_entry");
	
	var new_val = onlyNumbers(tended_.val());
	
	tended_.val(new_val);
	
	tallyPayments();

}

function applyScreenSpecialKey(key,str_){
	switch(key){
		case "_dec"://apply decimal key
				var val = str_ + ".";
				return val;
			break;
		case "_del"://apply backspace
				return str_.substr(0,(str_.length -1));
			break;
		
		default:
			return 0;

	}
}


function tallyPayments(){
	var lines = $(".payment_line");
	var payment_balance = $("#payment_balance");
	var payment_change = $("#payment_change");

	testPaymentprocessor();


	lines.each(function(){
		var change = 0;

		var change_display = $(this).children("#payment_change");
		var change_val = parseFloat($(this).children("#payment_change").text());
		
		var pc = parseFloat($(this).prev().children("#payment_change").text());//previous change as float

		var prev_change = !isNaN(pc) ? pc : 0;

		var payment_due = $(this).children("#payment_due").attr("val");
		var payment_received = $(this).children("#payment_received").children(".payment_amount_entry").val();
		

		if(payment_received == "")
			payment_received = 0;

		if(payment_due == "")
			payment_due = 0;

		var cur_bal = payment_due - parseFloat(payment_received); 

		if(parseFloat(payment_received) > payment_due ){
			change = parseFloat(payment_received) - payment_due;
			cur_bal = 0;
		}

		updated_change = change + prev_change;

		payment_change.val(updated_change.toFixed(2));
		payment_balance.val(cur_bal.toFixed(2)); 

		change_display.html(updated_change.toFixed(2));

		$(this).next().children("#payment_due").attr("val",cur_bal.toFixed(2));
		$(this).next().children("#payment_due").html(cur_bal.toFixed(2));
		$(this).next().children("#payment_change").html(updated_change.toFixed(2));
		// console.log(i);
	});	
}

function testPaymentprocessor(){
	var lines = $(".payment_line");
	var entry_vals = [];//entry with value > 0 for test 

	if(lines.length > 0 ){
		lines.each(function(){
			var entry = $(this).children("td").children(".payment_amount_entry").val();
			if(entry > 0){
				entry_vals.push(entry);
			}

		});

	}else{
		$("#payment_tendered tbody").html('<tr id="no_payment"><td colspan=4>No payments are added yet. Select a payment type to add a payment.</td></tr>');

		$("#do_payment").attr("disabled",true);
		$("#do_payment").removeClass("fa faa-bounce animated");
	}
		

	if(entry_vals.length > 0){
		$("#do_payment").attr("disabled",false);
		$("#do_payment").addClass("fa fa-bounce animated");
	}else{
		$("#do_payment").attr("disabled",true);
		$("#do_payment").removeClass("fa faa-bounce animated");

	}
}

function onlyNumbers(str_){
	var str = str_;
	var test_str = /[a-zA-Z\s\[\]\\!@#;%_,"'\{\}:\?\~\`\+\-\=\$/\^&\*\(\)\|]/;
	var dec_test = /([\.{2,}])/;
	var indices = [];
	var dec_indices = [];
	var str_a = [];
	var new_str = str_;

	for(var i=0; i < str.length; i++) {
		str_a[i] = str_.charAt(i);
	}

	if(dec_test.test(str_)){
		for(var i=0; i < str.length; i++) {
			if(str[i] == ".")
	    		dec_indices.push(i);
		}
	}

	for(var i=0; i < str.length; i++) {
	    if (test_str.test(str[i]) ) 
	    	indices.push(i);	
	}

	if(dec_indices.length > 1)
		str_a[dec_indices[1]] = "";

	if(indices.length > 0)
		str_a[indices[0]] = "";

	new_str = str_a.join('');

	return new_str;
}

function tallyCart(){
	var order = $("#pos_order.active .pos_cart_items_list");
	var tax_ = 0;
	var total_ = 0;
	var sub_ext = 0;
	var discount_ = getDiscount(order);

	var cart = order.children();
	var cart_items = cart.children(".line_item");

	cart_items.each(function(){
		var ext_ = $(this).children("#line_extended");
		var tax_t = $(this).children("#line_tax");
		var _ext = parseFloat(ext_.attr("val"));
		var _tax = parseFloat(tax_t.attr("val"));
		
		sub_ext += _ext;
		tax_ += _tax
	});

	// tax_ = sub_ext * (tax_rate / 100);
	total_ = parseFloat(sub_ext + tax_);

	if(isNaN(discount_))
		discount_ = 0;
	// cart.children(".line_discount").children("#disc_amount").html("$"+discount_);

	cart.children(".line_sub_total").children("#ext_sub_total").html("$"+sub_ext);
	cart.children(".line_tax").children("#tax_").html("$"+tax_);
	cart.children(".line_total").children("#ext_total").html("$"+total_);
	
	return [tax_,discount_,sub_ext,total_]; 
}


function getDiscount(order){
	return parseFloat(order.children("#disc_applied").val());
}

function selectCustomer(){
	var order_id = $(this).attr("order");
	var pos_id = $(this).attr("pos");
	var customer_id = $(this).attr("customer");
	
	$.post("/pos/order/customer/dialog/",{"order_id":order_id,"pos_":pos_id,"company":company_,"customer":customer_id},function(data){
		$("body").append('<div class="widget" id="customers_widget"><span class="widget_cls"><i class="fa fa-times-circle fa-2x"></i></span><span class="widget_error"></span><div class="widget-body"></div>');
		$("#customers_widget .widget-body").html(data);

		$("#customers_widget").show("slow");

			$("#customers_widget .widget_cls").click(function(){
				$("#customers_widget").remove();
				$(".widget_error").html("");				
			});

			$(".error_cls").click(function(){
				$("#customers_widget").remove();
			});
			$(".customer_line").bind("click",function(){
				var customer_tax_id = $(this).attr("tax");
				var customer_name = $(this).attr("name");
				var customer_ = $(this).attr("customer");
				var order_id = $(this).attr("order");
				// var pos_id = $(this).attr("pos");

				setCustomer(order_id,company_,customer_,customer_tax_id,customer_name,pos_id);
			});
	});
}


function setCustomer(order,company,customer,tax_id,name,pos){
	$(".selected_customer_name").html(name+" - "+tax_id+"&nbsp;&nbsp;&nbsp;<span class='set_customer'><button type='button' class='btn btn-warning'>SET CUSTOMER</button></span>");
	$(".set_customer").click(function(){

		$.post("/pos/order/customer/set/",{"order_id":order,"company_id":company,"customer_id":customer,"tax_id":tax_id,"pos_id":pos},function(data){
				$("#pos_content").html(data);

				payment_widget = $("#payment_widget.widget"); 
				//verify caller if payment widget is active re initialize
				if(payment_widget.length > 0)
					reInitPaymentAccepter(order);

				autoLoader();
		});
	});
}

function cancelOrder(){
	var tab_indx = $(this).parent().attr("index");
	var order_id = $(this).parent().attr("val");
	var user_id = $("#user_id").val();
	var pos_ = $("#pos_").val();
	$this = $(this);
	
	var line_item = $("#pos_order[order="+order_id+"] #pos_cart_items .line_item");
	var tabs = $("#pos_order[order="+order_id+"] .tab"); 
	
		if(line_item.length < 1) {
			$.post("/pos/order/cancel/",{"order_id": order_id,"company_id": company_,"user_id": user_id,"pos_":pos_},function(data){
				$("#pos_content").html(data);
				
				var prev_order = $this.parent().parent().prev().children("#order_tab").attr("val");
				var next_order = $this.parent().parent().next().children("#order_tab").attr("val");
				
				if(tab_indx > 1)
					active_order = prev_order;
				else
					active_order = next_order;
				// setActiveTab();
				autoLoader();
			});
		}else{
			$("#alert_error_message .alert_error_body").html("<span class='error'>There are Items on this Transaction...<button type='button' class='btn btn-warning' id='cancel_order_confirm'>CLOSE</button> anyway? <button type='button' class='btn btn-success' id='cancel_order_close'>CANCEL</button> </span>");
			$("#alert_error_message").show();

			$("button#cancel_order_close").click(function(){
				$("#alert_error_message").hide();
				$("#alert_error_message .alert_error_body").html("");
			});

			$("button#cancel_order_confirm").click(function(){
				$.post("/pos/order/cancel/",{"order_id": order_id,"company_id": company_,"user_id": user_id,"pos_":pos_},function(data){
					$("#pos_content").html(data);
					$("#alert_error_message").hide();
					$("#alert_error_message .alert_error_body").html("");

					var prev_order = $this.parent().parent().prev().children("#order_tab").attr("val");
					var next_order = $this.parent().parent().next().children("#order_tab").attr("val");
					
					if(tab_indx > 1)
						active_order = prev_order;
					else
						active_order = next_order;
				
					autoLoader();
				});
			});
		}
	
}

function setActiveTab(){
	setScroller();
	if(active_order){
		$("#pos_order.active #order_tab.active").removeClass("active").addClass("inactive");
		$("#pos_order.active").removeClass("active").addClass("inactive");

		$("#pos_order[order='"+active_order+"']").removeClass("inactive").addClass("active");
		$("#pos_order[order='"+active_order+"'] #order_tab[val='"+active_order+"']").removeClass("inactive").addClass("active").click();
	}

}

function scollActiveTabIntoView(tab){
	var tabs = $("#pos_order.active .tab");
	var tab_nav_width = (tabs.length * (tabs.outerWidth() * 1.2) );
	var tab_indx = tab ? tab : $(".tab.active").attr("index");
	var tab_width =  $(".tab.active").outerWidth();
	var tab_view =  - ( tab_indx * tab_width - ( 2 * tab_width ) );
	var scroller = $("#pos_order.active .tabs_nav");

	scroll_lim = $(window).width() - ($(window).width() * (30/100)) - ( 1 * tab_width );

	if(tab_nav_width >= scroll_lim ){
		if(tab_indx <= 3)
			scroller.animate({"left": 0 }, 100);
		else
			scroller.animate({"left": tab_view+"px" }, 100);
	}else{
			scroller.animate({"left": 0 }, 100);
	}
}

function setScroller(){
	var tabs = $("#pos_order.active .tab");
	var tab_nav = $(".tabs_nav");

	var tab_nav_width = (tabs.length * (tabs.outerWidth() * 1.2) );

	tab_nav.css({"width":tab_nav_width+"px","height":(tabs.outerHeight() + 10) + "px"});

	scollActiveTabIntoView();
}

function switchView(){
	$(this).addClass("active");
	$(this).siblings().removeClass("active");
	$id = $(this).attr("id");
	$("#pos_order.active .view").hide();
	$("#pos_order.active #pos_"+$id).show();
}

function activeOrderTab(){
	var order_id = $(this).attr("val");
	var tab_indx = $(this).attr("index");
	active_order = order_id;

	$("#order_tab.active").removeClass("active").addClass("inactive");
	$(this).removeClass("inactive").addClass("active");

	$("#pos_order[order='"+order_id+"']").addClass("active").removeClass("inactive");
	$("#pos_order[order='"+order_id+"']").siblings().removeClass("active").addClass("inactive");
	$("#pos_order[order='"+order_id+"'] #order_tab[val='"+order_id+"']").removeClass("inactive").addClass("active");
	
	// $("#pos_order.active .avail_disc").bind("change",setDiscountMultiplier);
	
	// $("#pos_order.active .active_changer").unbind("change",discountLineItem);
	// $("#pos_order.active .active_changer").bind("change",discountLineItem);


	scollActiveTabIntoView(tab_indx);
	checkPayerActive();//verify that items are added to the cart and disable/enable payment button accordingly
	distroyInactiveWidgets();//on change order distroy or minimize action widets 
	keyBoard();
	// autoLoader();
}

function distroyInactiveWidgets(){
	$("#customers_widget").remove();
}

function keyBoard(){	
	screenKeyBoard();
	physicalKeyBoard();	
}

function screenKeyBoard(){
	var x = 0;
	$("#pos_order.active #pos_cart_keys .key").click(function(){
		var changer = $("#pos_order.active .active_changer");
		var activeChanger = document.getElementById(changer.attr("id"));
		changer.focus();
		changer.select();
		if( x == 0)
			changer.val("");

		var key = $(this).attr("key");
		var specialKeys =  ["_disc","_set","_dec","_void","_del"];
		// console.log(key);
		if($.inArray(key,specialKeys) == -1){	
			var val = changer.val();
			var new_val = val+key;
			changer.val(new_val);
		}else{
			applySpecialKey(key);
		}
		x = x+1
	});
}

function applySpecialKey(key){
	// console.log("Applying special key "+key);
	var changer = $("#pos_order.active .active_changer");
	switch(key){
		case "_set":
			if(changer.length > 0)
				changer.change();
			break;
		case "_dec":
			if(changer.length > 0){
				var val = onlyNumbers(changer.val(changer.val() + "."));
				changer.val(val);
			}
			break;
		case "_del":
			if(changer.length > 0)
				changer.val(changer.val().substr(0,(changer.val().length -1)));
			
			break;
		case "_disc":
			discounter();
			break;
		case "_void":
			voider();
			break;
		default:
			return 0;

	}
}

function physicalKeyBoard(){
	$("body").keyup(function(e){
		var key = e.keyCode;
		// var validkeysArray = [8,96,97,98,99,100,101,102,103,104,105,13,107,109,46,48,49,50,51,52,53,54,55,56,57,190,27,9,68,39,37];
		var changer = $("#pos_order.active .active_changer");
		var caller = $("#pos_order.active #"+changer.attr("caller"));
			if(e.ctrlKey && e.shiftKey && key == 68)
				key = 1001;

			if(changer.length > 0){
				new_val = onlyNumbers(changer.val());	
				changer.val(new_val);
			}

			if(key == 13 || key == 9){
				if(changer.val() == caller.attr("val"))
					changer.hide();
					caller.removeClass("active");
			}

			if(key == 27){
				val = caller.attr("val");

				if(val == "None")
					val = "0%";

					caller.html(val);
					changer.hide();
					caller.removeClass("active");
			}
		if(key == 1001)
			discounter();
	});
}


function voider(){
	var order_id = parseInt($("#pos_order.active #order_tab.active #order_id").val());
	var line_id = $("#pos_order.active .line_item.active").attr("line");
	var line_item_voided = $("#pos_order.active .line_item.active.voided");
	voided = 0;
	if(line_item_voided.length < 1)
		voided = 1;

	$.post("/pos/orderline/void/",{"line":line_id,"order":order_id},function(data){
		$("#pos_content").html(data);
		autoLoader();
	});
}

function loader_destroy(){
	$("#loader").hide();
}

function doToolTip(){
	$("[title]").mouseover(function(){
		var tool = $(this);
		var tip = tool.attr("title");
		var tip_block = $(".tip-block");
		
		if(typeof tip != "undefined"){
			if(tip == "")
				tip = tool.attr("title_");

			if(tip_block.length < 1)
				$("<div class='tip-block'>"+tip+"</div>").appendTo($("body"));
			else
				tip_block.html(tip);

			tool.attr("title_",tip);
			tool.attr("title","");
		
			tool.mouseout(function(){
				tool.attr("title",tip);
				$(".tip-block").remove();
			});
			$(".tip-block").css({"position":"fixed","z-index":"200","top":($(this).offset().top - 25),"left":$(this).offset().left,"padding":"3px 35px","border-radius":"3px","background":"#000","color":"#fff","white-space": "nowrap"});
			
			var tip_width = $(".tip-block").width();
			var tip_left = $(this).offset().left;
			var tip_window_dif = $("body").width() - (tip_width * 1.20);
			
			if((tip_left + tip_width) > $("body").width())
			$(".tip-block").css({"left": tip_window_dif});

			// if()

		}
	});
}


function search(){
	$where = $(this).attr("name");
	$this = $(this);
	$(this).keyup(function(){
		if($where == "products")
			$search_dialog = $("#pos_order.active .p_view");
			$val = $(this).val().toLowerCase();

		if($val.length >= 3){
			$("#pos_order.active .product_search_loader").show();
			$.post("/search/",{"in_":$where,"for_":$val,"by":null,"company":company_},function(data){
				$search_dialog.html(data);
				$("#pos_order.active .product_search_loader").hide();
				$(".product").bind("click",addLineItem);
				keepProductView();
			});
		}
	});
}

function filterCategory(){
	var cat_id = $(this).val();
	$("#pos_order.active .product_search_loader").show();

	$.post("/search/",{"by":"category","for_":cat_id,"in_":"products","company":company_},function(data){
		$("#pos_order.active .p_view").html(data);
		$("#pos_order.active .product_search_loader").hide();

		$(".product").bind("click",addLineItem);
		keepProductView();
	});
}


function searchOptions(){
	var u_text = "";
	search_results = $(".search_item .s_item_text");
	if(search_results.text().length > 30){
		u_text = search_results.text().substr(0,30);
		search_results.text(u_text+"....");
	}
	$(".set_item").bind("click",addLineItem);
	$(".show_item_detail").bind("click",showItemDetail);
	$(".search_item").bind("mouseover",hideItemDetails);
	doToolTip();
}

function hideItemDetails(){
	$(".item_detail").hide();
}

function showItemDetail(){
	var par_ = $(this).parent();
	var detail_ = par_.children(".item_detail");
	var det_left = par_.offset().left - (par_.outerWidth() * .8);
	var det_top = par_.offset().top + (par_.outerHeight() * .2);
	detail_.css({"left":det_left+"px","top":det_top+"px"}).show();
}

function zeroNoneDiscount(){
	$(".line_item #line_discount").each(function(val){
		val = $.trim($(this).attr("val"));
		if(val == "None")
			$(this).html(0+"%");
	});
}

function keepProductView(){
	var orders = $("#pos_order");
	 $.each(orders,function(){
	 	var view_id = $(this).children(".view_toggle.active").attr("id");
		if(view_id)
			var view_id_str = view_id.split("_");
		
		if(view_id_str)
			var view = view_id_str[1];

		$(this).children(".view").hide();
		$(this).children("#pos_product_"+view+"_view").show();
		$(this).children(".view_toggle").removeClass("active");
		$(this).children("#product_"+view+"_view").addClass("active");
	});
}

function lineItemAction(){
	$(this).addClass("active well");	
	$(this).siblings().removeClass("active well");
	$(this).siblings().children().removeClass("active");
	$("#pos_cart_keys > ul > ul > li:nth-child(2)").removeClass("disabled").attr("disabled",false);
	if(!$(this).hasClass("voided")){
		// $(this).children("#line_qty, #line_price").bind("click",setAction);
		// $(this).children("#line_discount").bind("click",activateDiscounter);

	}else{
		// $(this).children("#line_qty, #line_price").unbind("click",setAction);
		// $(this).children("#line_discount").unbind("click",activateDiscounter);
	}
	
	// $(this).children("#line_code, #line_extended,#line_desc,#line_discount").bind("click",deactiveChanger);
	// $("#pos_order.active #pos_product_view,#pos_order.active #pos_cart_nav,#pos_order.active #pos_payment_tab").click(function(){
	// 	$(".line_item").removeClass("active well");
	// 	deactiveChanger();
	// })

}

function deactiveChanger(){
	var active_changer = $("#pos_order.active .active_changer");
	var cid = active_changer.attr("caller");
	var caller = $("#pos_order.active #"+cid);

		val = active_changer.val()
		if(val == "None")
			val = "0.00%";

		caller.html(val);
		active_changer.hide();
	
	$(this).siblings().removeClass("active");
	active_changer.unbind("change");
}

function setAction(){
	var val = $(this).attr("val");
	var id = $(this).attr("id");
	var caller_top = $(this).offset().top;
	var caller_left = $(this).offset().left;
	var changer = $("#pos_order.active .active_changer");
	$(this).siblings().removeClass("active");
	$(this).addClass("active");
		
	changer.attr("caller",id);
	changer.val(val);
	changer.css({"top":caller_top+"px","left":caller_left+"px","width":($(this).width()+5),"height":$(this).height()});
	changer.show();
	changer.focus().select();
}


function addLineItem(){
	// var view = $(this).attr("view");
	var first_item = 1;
	var item_code = $(this).attr("code"); 
	var item_name = $(this).attr("name");
	var item_price = parseFloat($(this).attr("price")).toFixed(2);
	var item_taxable = parseInt($(this).attr("taxable"));
	var user_ = $("#user_id").val();
	
	var item_company = company_;//parseInt($(this).attr("company"));
	var order_id = parseInt($("#pos_order.active .tab.active #order_id").val());
	var cart_num = parseInt($("#pos_order.active .tab.active").attr("index"));

	var line_item = $("#pos_order.active #pos_cart_items .line_item#line_item_"+item_code+"_"+item_name);
	var item_price = parseFloat(line_item.children("#line_price").attr("val")).toFixed(2);
	var item_qty = parseFloat(line_item.children("#line_qty").attr("val"));
	var item_discount = parseFloat(line_item.children("#line_discount").attr("val"));
	
	item_price = !isNaN(item_price) ? item_price : 0;
	item_qty = !isNaN(item_qty) ? (item_qty + 1) : 1;
	item_discount = !isNaN(item_discount) ? item_discount : 0;

	if(!isNaN(item_qty)){
		$.post("/pos/orderline/",{"cart":0,"order_id":order_id,"item_code":item_code,"name":item_name,"company_id":item_company,"price":item_price,"qty":item_qty,"discount":item_discount},function(data){
				$("#pos_content").html(data);
				autoLoader();
		});
	}
}

// function updateLineitem(){
// 	var user_ = $("#user_id").val();
	
// 	var item_code = parseInt($("#pos_order.active .line_item.active").attr("code"));
// 	var item_company = parseInt(company_);
// 	var order_id = parseInt($("#pos_order.active .tab.active #order_id").val());
// 	var item_taxable = parseInt($(this).attr("taxable"));

// 	var line_item = $("#pos_order.active #pos_cart_items #line_item[code='"+item_code+"']");

// 	var item_price = parseFloat(line_item.children("#line_price").attr("val"));
// 	var item_qty = parseFloat(line_item.children("#line_qty").attr("val"));
// 	var item_discount = parseInt(line_item.children("#line_discount").attr("val"));
// 	var item_tax = item_taxable ? (item_price * item_qty) * (company_tax / 100) : 0;

// 	var cartTotals = tallyCart();
// 	tax = cartTotals[0];
// 	discount = cartTotals[1];
// 	sub_total = cartTotals[2];
// 	total = cartTotals[3];
// 	var item_extended = line_item.children("#line_extended").attr("val");
// 	if(!isNaN(item_qty)){
// 		$.post("/pos/orderline/",{"cart":0,"tax":item_tax,"order_id":order_id,"item_code":item_code,"company_id":item_company,"price":item_price,"qty":item_qty,"extended":item_extended,"discount":item_discount,"order_tax":tax,"disc_amount":discount,"sub_total":sub_total,"amount_due":total,"user_id":user_,"fi":0},function(data){
// 				$("#pos_content").html(data);
// 				autoLoader();
// 		});
// 	}
	
// }

function discounter(){
	var disc_ = $("#pos_order.active #avail_disc");
	var caller_top = $("#pos_order.active .key[key='_disc']").offset().top ;
	var caller_left = $("#pos_order.active .key[key='_disc']").offset().left;

	disc_.css({"top":caller_top+"px","left":caller_left+"px"})
	disc_.show();
	disc_key = true;
}

function setDiscountMultiplier(){
	var disc_per = $(this).val();
	$(this).hide();
	
	if(disc_per.toLowerCase() != "none"){
		if(disc_key){
			var disc_options = $("#pos_order.active .disc_type");
			if(disc_options.length < 1){
				var active_line = $("#pos_order.active .line_item.active");
				
				if(active_line.length > 0)
					disable = "";
				else
					disable = 'disabled';

				$("<ul class='disc_type'><li class='disc_' val='_all' _disc='"+disc_per+"' title='Discount Transaction'>All</li><li class='disc_ "+disable+"' _disc='"+disc_per+"' val='_line' "+disable+" title='Discount selected Line Item' >Line</li><li class='disc_' val='_close' title='Cancel Discount' >X</li></ul>").insertAfter("#pos_order.active .key[key='_disc']");
			}
			$("#pos_order.active #pos_cart_keys > ul > ul.disc_type .disc_").bind("click",applyDiscount);
		}else{
			discountLineItem(disc_per);
		}
	}
}


function activateDiscounter(){
	var caller_top = $(this).offset().top;
	var caller_left = $(this).offset().left;
	var disc_ = $("#pos_order.active #avail_disc");

	disc_.val($(this).attr("val"));
	disc_.css({"top":caller_top+"px","left":caller_left+"px"})
	disc_.show();
	disc_key = false;
}

function applyDiscount(){
	var options = $(this).parent();
	var option_ = $(this).attr("val");
	var disc_per = $(this).attr("_disc");
	
	if(option_ == "_close")
		options.remove();

	if(option_ == "_all")
		discountTransaction(disc_per);

	if(option_ == "_line")
		discountLineItem(disc_per);
}

function discountTransaction(line_disc){
	var lines_ = $("#pos_order.active .line_item");
	var applied_disc = $("#pos_order.active #disc_applied");
	var disc_show = $("#pos_order.active .line_discount #disc_amount");
	var order_id = parseInt($("#pos_order.active .tab.active #order_id").val());
	var user_ = $("#user_id").val();
	var new_disc_amount = 0;

	var cart = {"order_id": order_id,
				"company_id": company_,
				"user_id": user_,
				"order_tax": 0,
				"disc_amount": 0,
				"sub_total": 0,
				"amount_due": 0,
				"cart": 1,
				"items_": []
			};
	
	applied_disc.val(new_disc_amount);

	lines_.each(function(){
		var line = $(this);
		var line_price = parseFloat(line.children("#line_price").attr("val")).toFixed(2);
		var line_qty = parseFloat(line.children("#line_qty").attr("val"));
		var line_tax = parseFloat(line.children("#line_tax").attr("val"));
		var prev_discount = parseFloat(line.children("#line_discount").attr("predisc")).toFixed(2);
		var line_extended = line.children("#line_extended");
		var old_ext = (line_qty * line_price);
		var disc_amount = old_ext * line_disc / 100;
		var new_ext = old_ext - disc_amount;
		var item_taxable = parseInt($(this).attr("taxable"));
		// var item_tax = item_taxable ? (item_price * item_qty) * (company_tax / 100) : 0;
		
		if(line_disc == 0)
			disc_amount = 0;

		line.children("#line_discount").attr("val",line_disc);
		line.children("#line_discount").html(line_disc+"%");
		line_extended.attr("val",new_ext);
		line_extended.html("$"+line_extended.attr("val"));
		new_disc_amount = parseFloat(parseFloat(applied_disc.val()) + disc_amount).toFixed(2);
		applied_disc.val(new_disc_amount);
		disc_show.html("$"+new_disc_amount);

		cart.items.push({
			"tax": line_tax,
			"order_id": order_id,
			"item_code": line.attr("code"),
			"price": line_price,
			"qty": line_qty,
			"extended": line_extended.attr("val"),
			"discount": line_disc,
			"fi":0
		});
	});

	var cartTotals = tallyCart();
	tax = cartTotals[0];
	discount = cartTotals[1];
	sub_total = cartTotals[2];
	total = cartTotals[3];
	
	cart.order_tax = tax;
	cart.disc_amount = discount;
	cart.sub_total = sub_total;
	cart.amount_due = total;

	cart.items = JSON.stringify(cart.items);
	updateCart(cart);

	$("#pos_order.active .disc_type").remove();

}

function discountLineItem(line_disc){
	var line = $("#pos_order.active .line_item.active");
	if(isNaN(line_disc)){
		var val_ = parseFloat($(this).val());
		var caller = $(this).attr("caller");
		if(!val_)
			val_ = 0.00;

		$("#pos_order.active #"+caller).attr("val",val_); 
		line_disc = line.children("#line_discount").attr("val");
	}

	if(line.length > 0){
		var disc_show = $("#pos_order.active .line_discount #disc_amount");
		
		var line_price = parseFloat(line.children("#line_price").attr("val"));
		var line_qty = parseFloat(line.children("#line_qty").attr("val"));
		var line_tax = parseFloat(line.children("#line_tax").attr("val"));
		var line_extended = line.children("#line_extended");

		var prev_line_tax = parseFloat(line.children("#line_tax").attr("pretax"));
		var prev_line_qty = parseFloat(line.children("#line_qty").attr("preqty"));
		var prev_discount = parseInt(line.children("#line_discount").attr("predisc"));
		var prev_line_price = parseFloat(line.children("#line_price").attr("preprice"));

		var prev_ext = (prev_line_qty * prev_line_price);
		var now_ext = (line_price * line_qty);

		var disc_amount = now_ext * line_disc / 100;
				
		var new_ext =  now_ext - disc_amount;

		var prev_discount_amount = prev_ext * prev_discount / 100;

		var applied_disc = $("#pos_order.active #disc_applied");

		line.children("#line_discount").attr("val",line_disc);

		line_extended.attr("val",new_ext);
		line_extended.html("$"+line_extended.attr("val"));
		
		line.children("#line_discount").attr("predisc",line_disc);
		line.children("#line_price").attr("preprice",line_price);

		console.log("completing command->Add Discount to Line Item: "+count);
		count++;


		new_disc_amount = parseFloat(parseFloat(applied_disc.val()) + disc_amount - prev_discount_amount);

		applied_disc.val(new_disc_amount);
		disc_show.html("$"+new_disc_amount);
		
		// updateLineitem();
		$("#pos_order.active .disc_type").remove();
	}
	

}

function notifyAlert($msg,btnLabel,autoHide){
	$btn_type = "btn-success";
	$cancel = btnLabel.toUpperCase().match(/CANCEL/g);
	$exit = btnLabel.toUpperCase().match(/EXIT/g);
	if($cancel){
		if($cancel.length > 0){
			$btn_type = "btn-warning";
		}
	}
	$clsA = "<h6><center><button id='ok' class='btn btn-small "+$btn_type+"' >"+btnLabel+"</button></center></h6>";
	if($exit){
	 if($exit.length > 0){
			$btn_type = "btn-warning";
		}
		$clsA = "";
	}
  	$(".custom-alert .content").html("<h1><center>"+$msg+"</center></h1> "+$clsA); 
  	// setTimeout(function(){
  	// 	$cheight = $(".alert .content").innerHeight();	
  	// 	if($cheight !== 0){
  	// 		$(".alert").animate({height: $cheight});
  	// 	}
  	// },500);	
  	showHideNotif(autoHide);
}

function showHideNotif(autoHide){
	$(".custom-alert").addClass("s").show();

  	$(".custom-alert button#ok").click(function(){
		$("span.alert_cls").click();
  	});

  	$("span.alert_cls").click(function(){
		$(".custom-alert").removeClass("s").addClass("c").hide();
		$(".custom-alert .content").html("");
 	});

  	if($(".custom-alert").hasClass("s")){
	  if(autoHide){
	  	hideAlert();
	  }else{
	  	clearTimeout(hide);
	  }
	}else{
		if($(".custom-alert").hasClass("c") && $(".custom-alert").html() == ""){
			$(".custom-alert").addClass("s").show();
		}
	}
}

function hideAlert(){
	hide = setTimeout(function(){
		alertCls();
	},(gameSpeed + 1000));
}

function alertCls(){
	$("span.alert_cls").click();
}

function updateCart(cart){
	if(cart){
		$.post("/pos/orderline/",cart,function(data){
			$("#pos_content").html(data);
			autoLoader();
		});
	}
}

function createOrder(){
	var pos_ = $("#pos_").val();
	var user_id = $("#user_id").val();
	var active_order_items = $("#pos_order.active #pos_cart_items_list tbody tr").length
	active_order = "";

	if(active_order_items > 0){
		$.post("/pos/order/create/",{"pos_":pos_,"company_id":company_,"user_id":user_id},function(data){
			$("#pos_content").html(data);
			autoLoader();
		});
	}
}

function hotKeys(e){
	var key = e.keyCode;
	if( key == F2)
		sc_setCustomer();
	else if(key == F4)
		sc_closeOpenWidgets();
	else if(key == F6)
		sc_acceptPayment();
}

function sc_setCustomer(){
	$(".select_customer").click();
}

function sc_closeOpenWidgets(){
	$(".widget_cls").click();
}

function sc_acceptPayment(){
	$(".payment_selector").click();
}

function curFormat(){
	$(".cur").each(function(){
		num_ = 0;
		num = parseFloat($(this).html());
		if(num)
			num_ = numformat(num);
		
		$(this).html(num_);
	});
}