var hide = null;
$(function(){
	// var crop_;
	paginLinks();
	var active_form = form_map[$("#active_form").val()];
	$("#"+active_form+"-tab").click();
	$(".nav-link").on("mouseup",function(){
		$(".alert").hide();
	});
	// $("#do_recovery").attr("disabled",true);
	$("[name='c_pass']").on("change",verifyPasswordMatch);
	$(".flashed-messages").on("click",closeAlert);
	$("#products_per_page").on("change",changeProductsPerPage);
	$("[data-link]").on("click",goToOrder);
	$(".variant_options").on("change",addOsfLineItem);
	$(".qty-minus").on("click",minusItemQty);
	$(".qty-plus").on("click",addItemQty);
	$(".qty-text").on("change",updateItemQty);
	$(".edit_image").on("click",function(){
		$("#"+$(this).attr("for")).click();
	})
	$("#activation_link").on("click",function(){
		$(this).remove();
	});
	if($("#orders").length > 0)
		setOrderFilters();

	$("[data-toggle='tooltip']").tooltip();
	$(".add_fav").on("click",addFavourite);

	$(".search_type").on("click",initSearchType);
	initBusinessEnrollmentWizard();
});


function initBusinessEnrollmentWizard(){
	$(".wiz").hide();
	$("#start_business_enrollment_wiz").on("click",function(){
		$(this).hide("slow");
		$(".wiz-start").show("slow");
		$(".wiz input").on("change",function(){
			if(!$(this).parent().hasClass("wiz-bump")){
				if(!$(this).parent().next().hasClass("wiz-image")){
					$(this).parent().next().show("slow");
					$(this).parent().next().children("input").focus();
				}else{
					useImageSelector($(this).parent().next());
				}

			}else{
				if(!$(this).parent().parent().next().children(":eq(0)").hasClass("wiz-image")){
					$(this).parent().parent().next().children(":eq(0)").show("slow");					
					$(this).parent().parent().next().children(":eq(0)").children("input").focus();					
				}else{
					useImageSelector($(this).parent().parent().next().children(":eq(0)"));
				}
			}
		});
	});
}

function useImageSelector(target_){
	// $("#"+for_).click();
	notifyAlert(target_.attr("note")+"<h5><button id='yes' class='btn btn-success'>YES</button></h5>","CANCEL",false);
	$("#yes").click(function(){
		$("#"+target_.attr("for")).click();
		$("#"+target_.attr("for")).on("change",setPreviewImage);
		$(".alert").hide("slow");
	});
	$("#ok").click(function(){
		$("#"+target_.attr("for")).change();
		$(".alert").hide("slow");
	});
}


function buildImagePreview(input,preview) {
  if (input.files && input.files[0]) {
    var reader = new FileReader();
    reader.onload = function() {
      preview.attr('src', reader.result);
    }
    reader.readAsDataURL(input.files[0]); // convert to base64 string
  }
}

function setPreviewImage(){
	var preview_id = $(this).attr("id");
	if(preview_id == "image_"){
		buildImagePreview(this,$("#store-logo img"));
		$("#store-logo").show();
	}else{
		if(preview_id == "store_front_image"){
			buildImagePreview(this,$("#store-front-image img"));
			$("#store-front-image").show();
		}
	}
}

function initSearchType(){
	$(".search_type").removeClass("active");
	$(this).addClass("active");
	$("#search_type").val($(this).attr("data"));
}

function addFavourite(){
	var fav = $(this);
	fav.toggleClass("favourite");

	var fav_ = fav.attr("data").split(":");

	var fav_type = fav_[0];
	var fav_id = fav_[1];
	var fav_name = fav_[2];
	var fav_company = fav_[3];
	var nav_module = window.location.pathname.split("/")[1];

	if(fav_type && fav_id){
		$.post("/favourite/",{"company":fav_company,"type":fav_type,"item":fav_id},function(response){
			var success = JSON.parse(response);
			if(success.success){
				if(nav_module == "favourites")
					window.location.reload();

				$(".fav-count").html(success.favs);
				if(fav.hasClass("favourite"))
					fav.tooltip('hide').attr("data-original-title","Remove "+ fav_name + " from favourites.").tooltip('show');
				else
					fav.tooltip('hide').attr("data-original-title","Add "+ fav_name + " to favourites for easy access.").tooltip('show');
			}
		});
	}
}

function addItemQty(){
	var effect = $(this).prev();
	var qty = parseInt(effect.val());
	var new_qty = 1;

	if( !isNaN( qty ))
		new_qty = qty + 1;
	effect.val(new_qty);
	effect.change();
}

function minusItemQty(){
	var effect = $(this).next();
	var qty = effect.val();
	var new_qty = 1;

	if( !isNaN( qty ) && qty > 1)
		new_qty = qty - 1;
	effect.val(new_qty);
	effect.change();
}

function updateItemQty(){
	var item_qty = $(this).val();
	var item_name = $(this).attr("v_name");
	var order_id = $(this).attr("order");
	var item_code = $(this).attr("item");
	var item_price = $(this).attr("price");
	var item_company = $(this).attr("company");
	var item_discount = 0;

	if(!isNaN(item_qty)){
		$.post("/pos/orderline/",{"cart":0,"order_id":order_id,"item_code":item_code,"name":item_name,"company_id":item_company,"price":item_price,"qty":item_qty,"discount":item_discount},function(data){
			window.location = "?";
		});
	}
}


function notifyAlert($msg,btnLabel,autoHide){
	$btn_type = "btn-success-ok";
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
  	$(".alert .content").html("<h1><center>"+$msg+"</center></h1> "+$clsA); 
  	// setTimeout(function(){
  	// 	$cheight = $(".alert .content").innerHeight();	
  	// 	if($cheight !== 0){
  	// 		$(".alert").animate({height: $cheight});
  	// 	}
  	// },500);	
  	showHideNotif(autoHide);
}

function showHideNotif(autoHide){
	$(".alert").addClass("s").show();

  	$(".alert button#ok").click(function(){
		$("span.alert_cls").click();
  	});

  	$("span.alert_cls").click(function(){
		$(".alert").removeClass("s").addClass("c").hide();
		$(".alert .content").html("");
 	});

  	if($(".alert").hasClass("s")){
	  if(autoHide){
	  	hideAlert();
	  }else{
	  	clearTimeout(hide);
	  }
	}else{
		if($(".alert").hasClass("c") && $(".alert").html() == ""){
			$(".alert").addClass("s").show();
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

function addOsfLineItem(){
	var variant = $(this).val().split(":");
	var variant_name = variant[0];
	var variant_price = variant[1];
	var variant_code = variant[2];

	$("#product_price_"+variant_code).html("$"+parseFloat(variant_price).toFixed(2));
	var variant_link = $("#item_add_link_"+variant_code).attr("href").split("/");
	variant_link[(variant_link.length-2)] = variant_name;
	var selected_variant_link = variant_link.join("/");
	$("#item_add_link_"+variant_code).attr("href",selected_variant_link);
}

function goToOrder(){
	var link = $(this).attr("data-link");
	window.location = link;
}

function paginLinks(){
	$("div.pagination ul").addClass("pagination justify-content-end mt-50");
	$("div.pagination ul li").addClass("page-item");
	$("div.pagination ul li a").addClass("page-link");
}

function changeProductsPerPage(){
	$(this).parent().submit();
}

function closeAlert(){
	$(this).hide();
}

function verifyPasswordMatch(){
	var pass_ = $("name['password']").val();
	if(pass_ == $(this).val()){
		$(this).removeClass("error")
		$("#do_recovery").attr("disabled",false);
	}else{
		$(this).addClass("error")
		$("#do_recovery").attr("disabled",true);
	}

}

function ParseFile(elem) {
	// display an image
	if (elem.files && elem.files[0]) {
		var reader = new FileReader();
		reader.onload = function(e) {
			var img_src = e.target.result
			crop_ = $("#pic_cropper").croppie('bind',{
			    url: img_src
			});
		}
		reader.readAsDataURL(elem.files[0]);
	}
}

function setOrderFilters(){
	var col_types = [];
	var filtersConfig = {
		base_path: '/static/js/tablefilter/',
		// btn_reset: true,
		sort: true,
		rows_counter: {
            text: 'Orders Found: '
        },
  		loader: true,
  		paging: true,
  		mark_active_columns: true,
  		sticky_headers: true,
  		extensions: [
                {
                    name: 'sort'
                }, {
                    name: 'colOps',
                    id: [
                        'sum_discs', 
                        'sum_subs', 
                        'sum_taxs', 
                        'sum_totals'
                    ],
                    col: [
                        
                        3, 
                        4,
                        5, 
                        6 
                       
                    ],
                    operation: [
                        'sum',
                        'sum', 
                        'sum', 
                        'sum'
                        
                    ],
                    decimal_precision: [
                        2, 
                        2,
                        2, 
                        2
                       
                    ],
                    format_result: [
                  			{ prefix: '$' },
                  			{ prefix: '$' },
                  			{ prefix: '$' },
                  			{ prefix: '$' }
                	]
                }
            ],
  		filters_cell_tag: 'th',
        themes: [{
            name: 'transparent'
        }],
	};

	$.each($(".ft"),function(i,col){
		var col_num = 'col_'+i;
		var filter_type = $(this).attr('filter-type');
		var filter_data_type = $(this).attr('filter-data-type');
		if(filter_type != 'normal')
			filtersConfig[col_num] = filter_type;
		
		col_types.push(filter_data_type);
	});
	filtersConfig['col_types'] = col_types;
	
	var tf = new TableFilter('orders', filtersConfig);
	tf.init();
	$(".helpBtn").remove();

	$(".filter_company_orders").on("click",function(){
		var filter_by = $(this).attr("href").split("#")[1];
		if(filter_by.toLowerCase() == "all")
			filter_by = "";

		tf.clearFilters();
		tf.setFilterValue(10, filter_by);
		tf.filter();
	});


}

function globalSocket($socket,silent){
  var websocket = new WebSocket($socket_type+'://'+$socket); 
  websocket.onopen = function(event) { 
  	console.log("connected");
  }

  websocket.onmessage = function(event) {   
    sortMessage(event);
  };
  
  websocket.onerror = function(event){
    
  };

  websocket.onclose = function(event){
  
  }; 
  return $my_socket;
}

function sortMessage(event){
  var resp = JSON.parse(event.data);

  if(resp.message_type == "chat_connection_ack"){
    
  }

}