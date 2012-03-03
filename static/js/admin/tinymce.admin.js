$(document).ready(function () {
	var small_phone = window.matchMedia( "(min-width: 240px)" );
	var iphone = window.matchMedia( "(min-width: 320px)" );
	var small_tablet = window.matchMedia( "(min-width: 480px)" );
	var ipad = window.matchMedia( "(min-width: 768px)" );
	var desktop = window.matchMedia( "(min-width: 1024px)" );
	
	var itemNav_1 = "";
	var itemNav_2 = "";
	
	//itemNav_1 = "bold,italic,strikethrough,|,justifycenter,formatselect,fontsizeselect,";
	//itemNav_2 = "forecolor,|,bullist,numlist,|,blockquote,|,link,unlink,|,image,|,removeformat";
	
	if(desktop.matches){
		// width is at least 1024px
		itemNav_1 = "formatselect,fontsizeselect,bold,italic,strikethrough,|,justifyleft,justifycenter,justifyright,|,";
		itemNav_1 += "bullist,numlist,|,outdent,indent,blockquote,|,forecolor,|,link,unlink,|,image,|,removeformat";
	} else if(ipad.matches){
		// width is less than 768px
		itemNav_1 = "formatselect,bold,italic,strikethrough,|,justifyleft,justifycenter,justifyright,|,";
		itemNav_1 += "bullist,numlist,|,blockquote,|,forecolor,|,link,unlink,|,image,|,removeformat";
	} else if(small_tablet.matches){
		// width is less than 480px
		itemNav_1 = "formatselect,bold,italic,strikethrough,|,justifyleft,justifycenter,justifyright,|,";
		itemNav_1 += "bullist,numlist,|,blockquote,|,link,unlink,|,image,|,removeformat";
	} else if(iphone.matches){
		// width is less than 320px
		itemNav_1 = "bold,italic,strikethrough,|,justifyleft,justifycenter,justifyright,|,";
		itemNav_1 += "bullist,numlist,|,link,unlink,|,removeformat";
	} else{
		// width is less than 240px  
		itemNav_1 = "bold,italic,strikethrough,|,justifycenter,|,";
		itemNav_1 += "bullist,numlist,|,removeformat";
	}

	$('textarea.tinymce').tinymce({
		script_url : get_static_url() + "js/tinymce/tiny_mce.js",
		theme: "advanced",
		skin : "o2k7",
		skin_variant : "silver",
		plugins: "autolink, autoresize, bbcode, directionality, fullscreen, inlinepopups, lists, wordcount, xhtmlxtras",
		
		theme_advanced_buttons1 : itemNav_1,
		theme_advanced_buttons2 : itemNav_2,
		theme_advanced_buttons3 : "",
		theme_advanced_buttons4 : "",
		theme_advanced_toolbar_location : "top",
		theme_advanced_toolbar_align : "left",
		theme_advanced_statusbar_location : "bottom",
		theme_advanced_resizing : true,
	});
});