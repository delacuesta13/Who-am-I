// ----------------------------------------------------------------------------
// markItUp!
// ----------------------------------------------------------------------------
// Copyright (C) 2011 Jay Salvat
// http://markitup.jaysalvat.com/
// ----------------------------------------------------------------------------
// Html tags
// http://en.wikipedia.org/wiki/html
// ----------------------------------------------------------------------------
// Basic set. Feel free to add more tags
// ----------------------------------------------------------------------------
var mySettings = {
	markupSet:  [
	    {name:'Heading 1', key:'', openWith:'[h1]', closeWith:'[/h1]' },
		{name:'Heading 2', key:'', openWith:'[h2]', closeWith:'[/h2]' },
		{name:'Heading 3', key:'', openWith:'[h3]', closeWith:'[/h3]' },     
		{name:'Heading 4', key:'', openWith:'[h4]', closeWith:'[/h4]' },
		{name:'Heading 5', key:'', openWith:'[h5]', closeWith:'[/h5]' },
		{name:'Heading 6', key:'', openWith:'[h6]', closeWith:'[/h6]' },
		{name:'Paragraph', key:'', openBlockWith:'[p]', closeBlockWith:'[/p]', multiline:true },
		{separator:'---------------' },
		{name:'Colors', openWith:'[color=[![Enter a name or a hexadecimal color]!]]', closeWith:'[/color]', className:'palette', dropMenu: [
		               {name:'Yellow',	openWith:'[color=#FCE94F]',	closeWith:'[/color]', className:"col1-1" },
		               {name:'Yellow',	openWith:'[color=#EDD400]',	closeWith:'[/color]', className:"col1-2" },
		               {name:'Yellow',	openWith:'[color=#C4A000]',	closeWith:'[/color]', className:"col1-3" },
		 	                              				
		               {name:'Orange',	openWith:'[color=#FCAF3E]',	closeWith:'[/color]', className:"col2-1" },
		               {name:'Orange',	openWith:'[color=#F57900]',	closeWith:'[/color]', className:"col2-1" },
		               {name:'Orange',	openWith:'[color=#CE5C00]',	closeWith:'[/color]', className:"col2-3" },
		                                                
		               {name:'Brown',	openWith:'[color=#E9B96E]',	closeWith:'[/color]', className:"col3-1" },
		               {name:'Brown',	openWith:'[color=#C17D11]',	closeWith:'[/color]', className:"col3-2" },
		               {name:'Brown',	openWith:'[color=#8F5902]',	closeWith:'[/color]', className:"col3-3" },
		 	                              				
		               {name:'Green', 	openWith:'[color=#8AE234]', closeWith:'[/color]', className:"col4-1" },
		               {name:'Green', 	openWith:'[color=#73D216]', closeWith:'[/color]', className:"col4-2" },
		               {name:'Green',	openWith:'[color=#4E9A06]', closeWith:'[/color]', className:"col4-3" },
		 	                              				
		               {name:'Blue', 	openWith:'[color=#729FCF]', closeWith:'[/color]', className:"col5-1" },
		 	           {name:'Blue', 	openWith:'[color=#3465A4]', closeWith:'[/color]', className:"col5-2" },
		 	           {name:'Blue',	openWith:'[color=#204A87]', closeWith:'[/color]', className:"col5-3" },
		 	                              	
		 	           {name:'Purple',	openWith:'[color=#AD7FA8]', closeWith:'[/color]', className:"col6-1" },
		 	           {name:'Purple',	openWith:'[color=#75507B]', closeWith:'[/color]', className:"col6-2" },
		 	           {name:'Purple',	openWith:'[color=#5C3566]', closeWith:'[/color]', className:"col6-3" },
		 	                              				
		 	           {name:'Red', 	openWith:'[color=#EF2929]', closeWith:'[/color]', className:"col7-1" },
		 	           {name:'Red', 	openWith:'[color=#CC0000]', closeWith:'[/color]', className:"col7-2" },
		 	           {name:'Red',		openWith:'[color=#A40000]', closeWith:'[/color]', className:"col7-3" },
		 	                              				
		 	           {name:'Gray', 	openWith:'[color=#FFFFFF]', closeWith:'[/color]', className:"col8-1" },
		 	           {name:'Gray', 	openWith:'[color=#D3D7CF]', closeWith:'[/color]', className:"col8-2" },
		 	           {name:'Gray',	openWith:'[color=#BABDB6]', closeWith:'[/color]', className:"col8-3" },
		 	                              				
		 	           {name:'Gray', 	openWith:'[color=#888A85]', closeWith:'[/color]', className:"col9-1" },
		 	           {name:'Gray', 	openWith:'[color=#555753]', closeWith:'[/color]', className:"col9-2" },
		 	           {name:'Gray',	openWith:'[color=#000000]', closeWith:'[/color]', className:"col9-3" }
		 	                              			   
		]},
		{name:'Size', key:'', openWith:'[size=[![Enter a font-size]!]]', closeWith:'[/size]', className:'fontsize', dropMenu: [
			           {name:'8',  openWith:'[size=8]',  closeWith:'[/size]', className:'size1' },
			           {name:'10', openWith:'[size=10]', closeWith:'[/size]', className:'size2' },
			           {name:'12', openWith:'[size=12]', closeWith:'[/size]', className:'size3' },
			           {name:'14', openWith:'[size=14]', closeWith:'[/size]', className:'size4' },
			           {name:'18', openWith:'[size=18]', closeWith:'[/size]', className:'size5' },
			           {name:'24', openWith:'[size=24]', closeWith:'[/size]', className:'size6' },
			           {name:'36', openWith:'[size=36]', closeWith:'[/size]', className:'size7' }
		]},
		{separator:'---------------' },
		{name:'Bold', key:'', openWith:'[b]', closeWith:'[/b]' },
		{name:'Italic', key:'', openWith:'[i]', closeWith:'[/i]' },
		{name:'Stroke through', key:'', openWith:'[del]', closeWith:'[/del]' },
		{separator:'---------------' },
		{name:'Center', key:'', openBlockWith:'[center]', closeBlockWith:'[/center]', multiline:true },
		{separator:'---------------' },
		{name:'Bulleted List', key:'', openWith:'[list]\n', closeWith:'\n[/list]' },
		{name:'Numeric List', key:'', openWith:'[list=[![Enter a number for start to order:!:1]!]]\n', closeWith:'\n[/list]' },
		{name:'List Item', key:'', openWith:'[*] ', closeWith:'' },
		{separator:'---------------' },
		{name:'Quote', key:'', openBlockWith:'[quote=[![Author]!]]', closeBlockWith:'[/quote]', multiline:true },
		{name:'Code', key:'', openBlockWith:'[code]', closeBlockWith:'[/code]', multiline:true },
		{separator:'---------------' },
		{name:'Link', key:'', openBlockWith:'[url=[![Enter an Url:!:http\://]!]]', closeBlockWith:'[/url]', placeHolder:'text to link', multiline:true },
		{name:'Picture', key:'', replaceWith:'[img alt="A description should go here"][![Enter Url of image]!][/img]'},
		{name:'YouTube', key:'', 
		 replaceWith:'[youtube width=600 height=361][![Enter Video ID (If Url of video is: http://www.youtube.com/watch?v=mghhLqu31cQ, Video ID would be: mghhLqu31cQ)]!][/youtube]'},
		{name:'Vimeo', key:'', 
         replaceWith:'[vimeo width=600 height=361][![Enter Video ID (If Url of video is: https://vimeo.com/36933978, Video ID would be: 36933978)]!][/vimeo]'
        },
		{separator:'---------------' },
		{name:'Clean', className:'clean', replaceWith:function(markitup) { return markitup.selection.replace(/\[(.*?)\]/g, "") } },
	]
}

$(document).ready(function () {
	var small_phone = window.matchMedia( "(min-width: 240px)" );
	var iphone = window.matchMedia( "(min-width: 320px)" );
	var small_tablet = window.matchMedia( "(min-width: 480px)" );
	var ipad = window.matchMedia( "(min-width: 768px)" );
	var desktop = window.matchMedia( "(min-width: 1024px)" );
	
	if(desktop.matches){
		// width is at least 1024px
		$('textarea.markItUp').markItUp(mySettings);
		$('textarea.markItUp').removeClass('span6 span7 span8 span9');
	} else if(ipad.matches){
		// width is less than 768px
		$('textarea.markItUp').markItUp(mySettings);
		$('textarea.markItUp').attr("rows","12");
		$('textarea.markItUp').removeClass('span6 span7 span8 span9');
	} else if(small_tablet.matches){
		// width is less than 480px
		$('textarea.markItUp').attr("rows","10");
		$('textarea.markItUp').removeClass('markItUp');
	} else if(iphone.matches){
		// width is less than 320px
		$('textarea.markItUp').attr("rows","8");
		$('textarea.markItUp').removeClass('markItUp');
	} else{
		// width is less than 240px  
		$('textarea.markItUp').attr("rows","6");
		$('textarea.markItUp').removeClass('markItUp');
	}
});