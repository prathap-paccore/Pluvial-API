// JavaScript Document
/*! ================================================================================
								PRELOADER
==================================================================================*/
	$(window).on('load', function () { // makes sure the whole site is loaded
		$('[data-loader="circle-side"]').fadeOut(); // will first fade out the loading animation
		$('#preloader').delay(350).fadeOut('slow'); // will fade out the white DIV that covers the website.
		$('body').delay(350);
	})

/*! ================================================================================
								SMOOTH SCROLLBAR
==================================================================================*/







$('.summary-qtns-table tr').click(function(){
        window.location = $(this).attr('href');
        return false;
    });