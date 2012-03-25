$(document).ready(function(){
	
	/* Navigation for mobile devices */
	
	// Create the dropdown base
	$("<select />").appendTo("#navTop-Mobile");
	
	// Create default option "Navigation"
	$("<option />", {
		"selected": "selected",
		"value"   : "",
		"text"    : "Navigation"
	}).appendTo("#navTop-Mobile select");
	
	// Populate dropdown with menu items
	$("header nav a").each(function() {
		var el = $(this);
		$("<option />", {
			"value"   : el.attr("href"),
			"text"    : el.text()
		}).appendTo("#navTop-Mobile select");
	});
	
	$("#navTop-Mobile select").change(function() {
		window.location = $(this).find("option:selected").val();
	});
	
});

function nl2br (str) {   
	return (str + '').replace(/([^>\r\n]?)(\r\n|\n\r|\r|\n)/g, '$1'+ '<br>' +'$2');
}