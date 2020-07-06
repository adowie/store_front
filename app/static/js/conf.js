$(function(){
	$("#receipt_header").html($("#receipt_header").text());//parse server return value as html
	$("#receipt_footer").html($("#receipt_footer").text());//parse server return value as html
	$("#edit_company").bind("click",editCompany);
	$("#cancel_company_edit").bind("click",cancelCompanyEdit);
});

function editCompany(){
	$("#cancel_company_edit").show();
	$(".no_hide").hide("slow");
	$(".hid").show("slow");
	$(this).hide();
}

function cancelCompanyEdit(){
	$("#edit_company").show();
	$(this).hide();
	$(".no_hide").show();
	$(".hid").hide();
}

