$(function(){
	// $("#loginForm input#password").bind("keyup",selectCompany);
	$("select#company").attr("disabled",false);

	$("select").bind("change",activateAdderWidget);
	$("select#company").bind("change",setCompanyName);

});

function addCustomerWidget(){
	$("#customer_adder").show("slow");
	$("#customer_adder .cls_btn").click(function(){
		$("#customer_adder").hide("slow");
	});
}

function addProductsWidget(){
	$("#product_adder").show("slow");
	$("#product_adder .cls_btn").click(function(){
		$("#product_adder").hide("slow");
	});
}
 
function setCompanyName(){
	$val = $(this).val();
	if(!isNaN($val) && $val.indexOf("add_") == -1)
		$("input#sel_company_name").val($.trim($(this).children("option:selected").text()));
}

function selectCompany(){
	$(this).change(function(){
		if($("#loginForm input#username").val()){
			if($(this).val().length > 5){
				// $("select#company").attr("disabled",false);
				$(".validation-summary-errors").html("");
			}else {
				// $("select#company").attr("disabled",true);
				$(".validation-summary-errors").html("Invalid Password!");
			}
		}else {
				$(".validation-summary-errors").html("Enter Username!");
		}
	});
}

function activateAdderWidget(){
	$widget = $(this).val();

	getWidget($(this),$widget);

}

function getWidget($caller,$widget){
	if(isNaN($widget) && $widget.indexOf("add_") !== -1){
		$.post("/widgets/",{"widget":$widget},function(data){
			$("body").append('<div class="widget" id="'+$widget+'_widget"><span class="widget_cls"><i class="fa fa-times-circle fa-2x"></i></span><span class="widget_error"></span><div class="widget-body"></div>');

			$("#"+$widget+"_widget .widget-body").html(data);

			$("input[name='created_date']").val(today());
			$("#"+$widget+"_widget").show("slow");

			$("#"+$widget+"_widget .widget_cls").click(function(){
				$("#"+$widget+"_widget").remove();
				$(".widget_error").html("");
				$caller.val($caller.children("option:first-child").val());
				
			});
			$(".error_cls").click(function(){
				$("#error_message").remove();
				$("#"+$widget+"_widget").remove();
			});

			$("input#add_company").bind("click",addCompany);
			$("input#add_company_type").bind("click",addCompanyType);
			$("input#add_company_owner").bind("click",addCompanyOwner);


			$("select").bind("change",activateAdderWidget);
		});
	}
}

function addCompany(){
	$form = $("form#company_adder");
	$ajax = $("#"+$form.attr("id")+" input#ajax");

	if($ajax.length < 1)
		$("<input type='hidden' value=1 name='ajax' id='ajax' />").appendTo($form);
	
	$data = $form.serializeObject();

	if(checkFieldsVal($form)){
		$.post("/company/create/",$data,function(data){
			$res = JSON.parse(data);
			
			if($res.result.error == "success"){
				$(".widget_error").html("<span class='success'>New Company Added successfully</span>");
				$("select#company option:not('option:first-child,option:last-child')").remove();
					setTimeout(function(){
						$(parseTypes($res.result.types)).insertAfter($("select#company option:first-child"));
						cleanFields($form);
						$("#add_company_widget").remove();
					},1000);
			}else{
				$(".widget_error").html($res.result.error);
			}
		});
	}
	
}

function addCompanyType(){
	$form = $("form#company_type_adder");

	$ajax = $("#"+$form.attr("id")+" input#ajax");

	if($ajax.length < 1)
		$("<input type='hidden' value=1 name='ajax' id='ajax' />").appendTo($form);

	$data = $form.serializeObject();
	
	if(checkFieldsVal($form)){
		$.post("/company/type/create/",$data,function(data){
			$res = JSON.parse(data);
			if($res.result.error == "success"){
				$(".widget_error").html("<span class='success'>New Company Type Added successfully</span>");
				$("select#company_type option:not('option:first-child,option:last-child')").remove();
					setTimeout(function(){
						$(parseTypes($res.result.types)).insertAfter($("select#company_type option:first-child"));
						cleanFields($form);
						$("#add_company_type_widget").remove();
					},1000);
			}else{
				$(".widget_error").html($res.result.error);
			}
		});
	}
}

function addCompanyOwner(){
	$form = $("form#add_company_owner");
	$ajax = $("#"+$form.attr("id")+" input#ajax");

	if($ajax.length < 1)
		$("<input type='hidden' value=1 name='ajax' id='ajax' />").appendTo($form);

	$data = $form.serializeObject();

	if(checkFieldsVal($form)){
		$.post("/customers/create/",$data,function(data){
			$res = JSON.parse(data);
			if($res.result.error == "success"){
				$(".widget_error").html("<span class='success'>New Company Owner Added successfully</span>");
				$("select#company_owner option:not('option:first-child,option:last-child')").remove();
					setTimeout(function(){
						$(parseTypes($res.result.types)).insertAfter($("select#company_owner option:first-child"));
						cleanFields($form);
					},200);
			}else{
				$(".widget_error").html($res.result.error);
			}
		});
	}
}	

function cleanFields($form){
	$fields = $("#"+$form.attr("id")+" input:not('input[type=hidden],input[type=file],input[type=button]'), #"+$form.attr("id")+" select");
	$.each($fields,function(i){
		$(this).val("");
	});
}

function parseTypes(types){
	$html = "";// "<option value=''> --- Select ---</option>";
	$.each(types[0],function(i,val){
		$html += "<option value='"+val.id+"' >"+val.name+"</option>";
	});
	// $html += "<option class='add_' value='add_company_type'> -- Add Type -- </option>";

	return $html
}

function checkFieldsVal($form){
	$fields = $("#"+$form.attr("id")+" input:not('input[type=hidden],input[type=file]'), #"+$form.attr("id")+" select");

	$.each($fields,function(i){

		if($(this).val() == "" || $(this).val().indexOf("add_") !== -1 ){
			$(this).addClass("error");
		}else{
			$(this).removeClass("error");
		}
	});

	if(!$fields.hasClass("error"))
		return true;
	else
		return false;
	
}
