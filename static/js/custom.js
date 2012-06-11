       $(document).ready(function () {
				$(".ftrd-lbl1").click(function(){
                $('.sliderinner ul').animate({left: '0'});
				$('.handle').animate({left:'0'});
        });
						$(".ftrd-lbl2").click(function(){
                $('.sliderinner ul').animate({left: '-940'});
				$('.handle').animate({left:'195'});
        });
								$(".ftrd-lbl3").click(function(){
                $('.sliderinner ul').animate({left: '-1880'});
				$('.handle').animate({left:'380'});
        });
										$(".ftrd-lbl4").click(function(){
                $('.sliderinner ul').animate({left: '-2820'});
				$('.handle').animate({left:'570'});
        });
												$(".ftrd-lbl5").click(function(){
                $('.sliderinner ul').animate({left: '-3760'});
				$('.handle').animate({left:'760'});
        });
		
		
		function mycarousel_initCallback(carousel) {
    jQuery('.cnext').bind('click', function() {
        carousel.next();
        return false;
    });

    jQuery('.cprev').bind('click', function() {
        carousel.prev();
        return false;
    });
};


		jQuery('.carousels').jcarousel({
        scroll: 1,
        initCallback: mycarousel_initCallback,
        // This tells jCarousel NOT to autobuild prev/next buttons
        buttonNextHTML: null,
        buttonPrevHTML: null
    });
	//search
		$(".menu1 li").hover(
  function () {
    $(this).find("div").fadeIn();
  }, 
  function () {
    $(this).find("div").fadeOut();
  }
);

		$(".cartstatus").click(function(){
		$(".cartdrop").fadeToggle(300);
		$(".logreg").hide();
		if(!$(this).hasClass("cartstatus2")){ $(this).addClass("cartstatus2");}
		else { $(this).removeClass("cartstatus2");}
		});
		$(".loginregister").click(function(){
		$(".logreg").fadeToggle(300);
		$(".cartdrop").hide();
		if(!$(this).hasClass("loginregisteractive")){ $(this).addClass("loginregisteractive");}
		else { $(this).removeClass("loginregisteractive");}
		});

	$(".search").click(function() {
  $('.searchtoggle').toggle('fast', function() {
  });
});
$(".slideprev").click(function(){
var udaljeno = $(".sliderinner ul").css("left");
if(udaljeno!='0px'){
$('.sliderinner ul').animate({left: '+=940'});
var palica = $(".handle").css("left");
if(palica == '195px'){
$(".handle").animate({left:'0'});
}
if(palica == '380px'){
$(".handle").animate({left:'195'});
}
if(palica == '570px'){
$(".handle").animate({left:'380'});
}
if(palica == '760px'){
$(".handle").animate({left:'570'});
}
}
});
//desna
$(".slidenext").click(function(){
var udaljeno = $(".sliderinner ul").css("left");
if(udaljeno!='-3760px'){
$('.sliderinner ul').animate({left: '-=940'});
var palica = $(".handle").css("left");
if(palica == '0px'){
$(".handle").animate({left:'195'});
}
if(palica == '195px'){
$(".handle").animate({left:'380'});
}
if(palica == '380px'){
$(".handle").animate({left:'570'});
}
if(palica == '570px'){
$(".handle").animate({left:'760'});
}
}
});
	$('.googleinner').gMap({ markers: [{ latitude: 47.660937,
                              longitude: 9.569803,
                              html: "Here we are!",
                              popup: true }],
                  zoom: 6 });
	//gridswitch
	$('.gridtype').click(function(){
                $('.griditems').hide();
				$('.grayprod').show();
        });
        $('.listtype').click(function(){
		        $('.grayprod').hide();
                $('.griditems').show();
        });				  
	$('input.star').rating();	
//slider 2
			$('.slider2 ul').anythingSlider({
 navigationFormatter : function(index, panel){
  return " " + index; // This would have each tab with the text 'Panel #X' where X = index
 },
 height:381,
 hashtags:false,
 buildArrows:false
});			
var widthslide = $('.thumbNav').width();
    		var wholewidth = 940 - widthslide;
			wholewidth = wholewidth/2;
    		$('.thumbNav').css('margin-left',wholewidth);	
	//tabs
var tabContainers = $('div.tabs > div');
			tabContainers.hide().filter(':first').show();
			
			$('div.tabs ul.tabNavigation a').click(function () {
				tabContainers.hide();
				tabContainers.filter(this.hash).show();
				$('div.tabs ul.tabNavigation li').removeClass('ewizz');
				$(this).parent().addClass('ewizz');
				return false;
			}).filter(':first').click();			
        });