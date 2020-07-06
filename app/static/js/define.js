var active_order = "";//active order tab
var disc_key = false;//active discount key
var count = 1;

// shortcut keys aka hot keys
var F2 = 113;//set customer dialog
var F4 = 115;//close all open widgets
var F6 = 117;//accept payment
var F7 = 118;//not yet implemented


function numformat(n) {
	// format number to money format
	return "$"+parseFloat(n).toFixed(2).replace(/./g, function(c, i, a) { 	return i && c !== "." && ((a.length - i) % 3 === 0) ? ',' + c : c;	});

}

function isFocused(el){
	// If input as focus
	if(el){
		if(typeof el.selectionStart == "number"){
			return el.selectionStart == 0 && el.selectionEnd == el.value.length;
		}else if(typeof document.selection != "undefined"){
			el.focus();
			return document.selection.createRange().text == el.value;
		}
	}
}


function img_preview_path(input){
   $('#pre_image')[0].src = (window.URL ? URL : webkitURL).createObjectURL(input.files[0]);
   $('#pre_image')[0].style.display = "block";
   $('#def_image')[0].style.display = "none";
}