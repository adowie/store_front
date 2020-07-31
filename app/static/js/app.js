preloader();
var hide = null;
$mobile = false;
$(function(){
	if($("input[name='created_date']").val() == "")
	$("input[name='created_date']").val(today());	

	$("input#item_remover").bind("click",initItem);
	$("input#remove_category").bind("click",initCategory);


	$("input#uom_").bind("change",setUomConversion);

	$("input.image_select,button.image_select").bind("click",imageSelector);

	$("#error_message .error_cls").bind("click",closeErrormessage);
	$("select.has_adder").bind("change",initAdderWidget);

	$("#change_customer_type").bind("click",editCustomerType);
	$("#product_search").bind("keypress",fetchProductList);
	$(".show_order_details").on("click",showOrderDetail);
	$("#company_products_list").contentEditable().click(setFieldType);
	$("#company_products_list").contentEditable().change(updateProductMeta);
	$("input#username").focus();
	$(".dis_item_image").on("mouseover",popOutImage);
	$(".dis_item_add_as_variant").on("click",enableVariantInput);
	$(".edit_variant").on("click",editVariant);
	$(".cat_prod_item").on("click",toggleChecked);
	$(".cat_item").on("click",setActiveCategory);
	$("#product_list .bg, .category_product_list .bg").on("click",clsCategoryDialog);
	$(".edit_category").on("click",editCategory);

  	var panel_ = $('.form-panel.two');
  	var panelOne = 100;
  	var panelTwo = 300;
  	
  	if(panel_.length > 0){
  		panelOne = panel_.height();
  		panelTwo = panel_[0].scrollHeight;
  	}

	$('.form-panel.two').on('click', function(e) {
		
	    $('.form-toggle').addClass('visible');
	    $('.form-panel.one').addClass('hidden');
	    $('.form-panel.two').addClass('active');
	    $('.form').animate({
	      'height': panelTwo
	    }, 200);
	});

	$('.form-toggle').on('click', function(e) {
	  
	    $(this).removeClass('visible');
	    $('.form-panel.one').removeClass('hidden');
	    $('.form-panel.two').removeClass('active');
	    $('.form').animate({
	      'height': panelOne
	    }, 200);
	});


	if($('.form-panel.two').hasClass("active")){
		
	    $('.form-toggle').addClass('visible');
	    $('.form-panel.one').addClass('hidden');
	  
	    $('.form').animate({
	      'height': panelTwo
	    }, 200);
	}
	addressNavigator();
	errorReportParser();
});


function editCategory(){
	$("#category_product_list_"+$(this).data("category")).show("slow");
}

function clsCategoryDialog(){
	$("#product_list, .category_product_list").hide();
}

function setActiveCategory(){
	var category_ = $(this).data("category");
	var category_name = $(this).data("name");
	$("input#category").val(category_);
	$("#active_category_name").html(category_name);
	$("#product_list").show("slow");
}

function toggleChecked(){
	$(this).toggleClass("selected");
	if(!$(this).hasClass("selected"))
		$(this).children("input").attr("checked",false);
	else
		$(this).children("input").attr("checked",true);

	if($(".cat_prod_item input:checked").length > 0)
		$("#add_category_products").show("slow");
	else
		$("#add_category_products").hide("slow");			
	

}

function editVariant(){
	var variant_id = $(this).data("variant-id");
	var variant_name = $(this).data("variant-name");
	var variant_image = $(this).data("variant-image");
	var variant_qty = $(this).data("variant-qty");
	var variant_price = $(this).data("variant-price");

	$("input#variant_id").val(variant_id);
	$("input#variant_name").val(variant_name);
	$("input#variant_image").val(variant_image);
	$("input#variant_qty").val(variant_qty);
	$("input#variant_price").val(variant_price);
	$("input#variant_update").val(1);
}

function setFieldType(e){
	var field_ = $(e.target);
	var field_name = field_.attr("id");
	var item_code = field_.data("item-code");
	var field_type = field_.data("type");
	var field_value = field_.html();
	if(field_type == "bool"){
		if(field_value.toUpperCase() == "TRUE"){
			field_.html(0);
			value_word = "False";
		}else{
			if(field_value.toUpperCase() == "FALSE"){
				field_.html(1);
			}
		}
		setTimeout(function(){
			field_.blur();
			window.getSelection().removeAllRanges();
		},100);
	}else{
		field_.on("keydown",function(e){
			var key = e.keyCode;
		    if(key === 13 || key === 27) {
				field_.blur();
				window.getSelection().removeAllRanges();
		    }
		});
	}
}

function enableVariantInput(){
	$("#variant_converter").remove();
	var product_id = $(this).data("product-id");
	var product_name = $(this).data("product-name");
	var product_price = $(this).data("product-price");
	var product_image = $(this).data("product-image");
	var product_code = $(this).data("product-code");
	var product_qty = $(this).data("product-qty");
	if(product_name != "" && parseInt(product_price) > 0){
		$(this).html("<input type='text' class='form-control' id='variant_converter' placeholder='Enter Product code'>");
		$("#variant_converter").focus();
		$("#variant_converter").on("keyup",function(e){
			var key_ = e.keyCode;
			if(key_ == 27){
				$(this).parent().html('<span class="fa fa-plus fa-2x"></span>');
			}else{
				console.log(key_)
				if(key_ == 9 && $(this).val().length < 1){
					$(this).parent().html('<span class="fa fa-plus fa-2x"></span>');
				}
			}
		});
		$("#variant_converter").on("change",function(){
			var target_parent = $(".product_line#product_"+$.trim($(this).val()));
			if(target_parent.length > 0){
				var parent_product = target_parent.children(".dis_item_add_as_variant");
				var parent_id = parent_product.data("product-id");
				var parent_name = parent_product.data("product-name");
				var parent_price = parent_product.data("product-price");
				
				if($.trim(parent_name) != "" && parseFloat(parent_price) > 0 ){
					$.post("/products/variant/add/",{"bulk":1,"variant_code":product_code,"product_id":parent_id,"name":product_name,"price":product_price,"variant_image":product_image,"qty":product_qty},function(){
						window.location.reload();
					});
				}else{
					notifyAlert("<h3>You cannot add a variant to a product that does not have a price or a name.</h3>", "ok", false);
				}
		
				$(this).blur();
			}
		});
	}else{
		notifyAlert("Complete setup for this product to set it as a variant.", "ok", false);
	}	
}

function popOutImage(){
	$("#popupimage").html($(this).children("img").clone()).show();
	$(this).on("mouseout",function(){
		$("#popupimage").hide();
	});
}

function updateProductMeta(e){
	var field_ = $(e.changedField[0]);
	var field_name = field_.attr("id");
	var item_code = field_.data("item-code");
	var field_type = field_.data("type");
	var data = e.changed['undefined'];
	var action = e.action;

	if(action == 'save'){
		if(data != ''){
			var value_word = "True";
			$.post("/product/update/",{"item":item_code,"field":field_name,"value":data},function(response){
				var error = parseInt(response);
				if(!error){
					if(field_type == 'bool'){
						if(parseInt(data) == 0)
							value_word = "False";

						field_.html(value_word);
					}
					var product_ = $(".product_line#product_"+item_code).children(".dis_item_add_as_variant");
					if(field_name == "item_price"){
						product_.data("product-price",data)
					}else{
						if(field_name == "item_name"){
							product_.data("product-name",data);
						}
					}

				}

			});
		}
	}

}

function showOrderDetail(){
	$(this).toggleClass("active");

	if($(this).hasClass("active"))
		$("#"+$(this).attr("id")+".order-details, #"+$(this).attr("id")+".order-details-h4").show();
	else
		$("#"+$(this).attr("id")+".order-details, #"+$(this).attr("id")+".order-details-h4").hide();

}

function fetchProductList(){
	var _val = $(this).val();
	if(_val.length > 3){
		$.post("/search/",{"for_":_val,"in_":"category"},function(response){
			$("#product_list").html(response);
			$(".proc_add").bind("click",addProductToCategory);
		});
	}
}

function addProductToCategory(){
	var prod_data = $(this).attr("data").split(":");
	var prod_ = '';
		prod_ += '<li id="cat_prod_'+prod_data[0]+'">';
		prod_ += '<input type="hidden" name="category_products[]" value="'+prod_data[0]+'">';
		prod_ += '   <div >';
		prod_ += '      <span class="add_proc_img"><img src="/static/'+prod_data[2]+'" /></span>';
		prod_ += '      <span class="add_proc_name">'+prod_data[1]+'</span>';
		prod_ += '      <span class="proc_remove" data="'+prod_data[0]+'">';
		prod_ += '        <i class="fa fa-minus fa-2x"></i>';
		prod_ += '      </span>';
		prod_ += '    </div>';
		prod_ += '  </li>';

	prod_ += $("#selected_products ul").html();

	$("#product_"+prod_data[0]+" .proc_add").unbind("click");
	$("#selected_products ul").html(prod_);
	$(".proc_remove").bind("click",removeProductFromCategory);

}


function removeProductFromCategory(){
	var prod_id = $(this).attr("data");
	$("#cat_prod_"+prod_id).remove();
	$("#product_"+prod_id+" .proc_add").bind("click", addProductToCategory);

}

function editCustomerType(){
	//$("");//TODO enable customer type to be changed
}

function setUomConversion(){
	$uom_ = verifyNumVal($(this).val());
	$conversion = 1 / $uom_;
	$("input#uom_conversion").val($conversion); 
}

function verifyNumVal(val){
	return val;
}

function initCategory(){
	$checked = $("input#"+$(this).attr("id")+":checked").length
	if($checked > 0){
		activateCategoryRemoval(true);
	}else{
		activateCategoryRemoval(false);
	}
}

function activateCategoryRemoval(activate){
	if(activate){
		$("input#category_remover_btn").attr("type","submit");
		$("input#category_remover_btn").show();
	}else{
		$("input#category_remover_btn").attr("type","button");
		$("input#category_remover_btn").hide();
	}
}

function initItem(){
	$checked = $("input#"+$(this).attr("id")+":checked").length
	if($checked > 0){
		activateItemRemove(true);
		addToFormUpdate($(this).parent().parent());
	}else{
		activateItemRemove(false);
	}
}


function errorReportParser(){
	$("#error_message .error_body").html($("#error_message .error_body").text());
	modUpdater();
}

function modUpdater(){
	module = addressNavigator();
	$("button#"+module+"_update").click(function(){
		$("input#"+module+"_update").val(1);
		$("form#"+module+"_creator").submit();
	});
	$("#"+module+"_update_cancel").click(function(){
		$("#error_message").hide();
	});
}

function addToFormUpdate(mod){
	$(mod).children().each(function(i,v){
		$id = $(this).attr("id");
		$val = $.trim($(this).text());
		$data = $.trim($(this).attr("data"));

		
		if($val == "True")
			$val = 1;
		else if($val == "False")
			$val = 0;

		if($data == "True")
			$data = 1;
		else if($data == "False")
			$data = 0;

		if(typeof $id !== "undefined"){
			$("input#"+$id).val($val);
			$("select#"+$id).val($data);

			$("textarea#"+$id).text($val);
		}
	});
}

function imageSelector(){
	$("input#image_").click();
	$imageSelector = $(this);
	$("input#image_").change(function(e){
        var fileName = e.target.files[0].name; 
        $imageSelector.val(fileName);
    });
}

function activateItemRemove(activate){
	if(activate){
		$("#remove_item").addClass("activate");
		$("#remove_item").bind("click",removeItem);
	}else{
		$("#remove_item").removeClass("activate");
		$("#remove_item").unbind("click",removeItem);
	}
}


function removeItem(){
	$(".remover_btn").click();
}

function closeErrormessage(){
	$(this).parent().hide();
}

function today(){
	var today = new Date();
	var day = today.getDate();
	var month = today.getMonth()+1; //January is 0!
	var year = today.getFullYear();
	var Hour = today.getHours();// > 12 ? today.getHours() - 12 : (today.getHours() < 10 ? "0" + today.getHours() : today.getHours());
	var Minute = today.getMinutes() < 10 ? "0" + today.getMinutes() : today.getMinutes();
	var Seconds = today.getSeconds() < 10 ? "0" + today.getSeconds() : today.getSeconds();
	var Meridiem = today.getHours();// > 12 ? "PM" : "AM";
	var time = Hour + ":" + Minute + ":" + Seconds;// + Meridiem;

	if(day < 10) {
	    day = '0'+day
	} 

	if(month < 10) {
	    month = '0'+month
	} 

	today = year + '-' + month + '-' + day+" "+time;

	return today;
}


function addressNavigator(){
	var location = window.location.href;
	split_loc = location.split("/");
	module = split_loc[3];
	sub_module = split_loc[4];
	mod = "";

	if(sub_module == "" || typeof sub_module == "undefined" ){
		if(typeof module !== "undefined" && module !== ""){
			mod = module;
		}
	}else{
		mod = sub_module;
	}

	if(mod == "create" || mod == "add" || mod == "delete" || mod == "update" )
		mod = module

	setActive(mod);	

	return mod;
}

function setActive(mod){
	if(mod == ""){
		$("ul.nav li").removeClass("active");
	}else{
		$("ul.nav li").removeClass("active");
		$("ul.nav li."+mod).addClass("active");
	}
}


function initAdderWidget(){
	$val = $(this).val();

	if($val.indexOf("add_") >= 0){
		console.log($val)
	}
}

function preloader(){
	var images = [];
	images[0] = new Image();
	images[0].src = "/static/img/login_bg.png";
}