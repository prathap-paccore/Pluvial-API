// JavaScript Document

$(document).ready(function(){
	
/*! **************************************************************************************** !*/
// Preload
	$(window).on('load', function () { // makes sure the whole site is loaded
		$('[data-loader="circle-side"]').fadeOut(); // will first fade out the loading animation
		$('#preloader').delay(350).fadeOut('slow'); // will fade out the white DIV that covers the website.
		$('body').delay(350);
	})
	
	
/*! **************************************************************************************** !*/
// Show hide password
	$('#password, #password1, #password2').hidePassword('focus', {
		toggle: {
			className: 'my-toggle'
		}
	});
	
	
/*! **************************************************************************************** !*/
// FORMS SHOW/HIDE
	$('#forgot').click(function(){
		$('#loginForm').fadeOut(300, function () {
			$('#forgotForm').fadeIn(300);
		});
	});
	$('#back-to-login').click(function(){
		$('#forgotForm').fadeOut(300, function () {
			$('#loginForm').fadeIn(300);
		});
	});
	$('#resetBtn').click(function(){
		$('#forgotForm').fadeOut(300, function () {
			$('#verifyForm').fadeIn(300);
		});
	});
	$('#changeNo').click(function(){
		$('#verifyForm').fadeOut(300, function () {
			$('#forgotForm').fadeIn(300);
		});
	});
	$('#otpSubmit').click(function(){
		$('#verifyForm').fadeOut(300, function () {
			$('#resetForm').fadeIn(300);
		});
	});
	$('#newLoginBtn').click(function(){
		$('#resetForm').fadeOut(300, function () {
			$('#loginForm').fadeIn(300);
		});
	});
	
	$('#registerBtn').click(function(){
		$('#registrationForm').fadeOut(300, function () {
			$('#registrationVerifyForm').fadeIn(300);
		});
	});
	
	$('#registrationVerifyForm #otpSubmit').click(function(){
		$('#registrationVerifyForm').fadeOut(300, function () {
			$('#successMessage').fadeIn(300);
		});
	});
	
	
	
	
	
	
/*! **************************************************************************************** !*/
// Float labels
	var floatlabels = new FloatLabels( 'form.input_style_1', {
		    style: 1
	});
	var floatlabels2 = new FloatLabels( 'form.input_style_2', {
		    style: 0
	});
	
	
	
/*! **************************************************************************************** !*/
// ENABLE DISABLE BUTTON OF FORM - ENABLES ONLY WHEN ALL FIELDS ARE FILLED.


$(function () {
  $('[data-toggle="tooltip"]').tooltip()
})



});