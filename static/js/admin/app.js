$(document).ready(function() {
	
	$('.scrollTop').click(function () {
		var destination = $(this).attr("href");
		$('body,html').animate({
			scrollTop: $(destination).offset().top
		}, 600);
		return false;
	});
	
})