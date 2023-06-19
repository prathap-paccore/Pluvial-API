// JavaScript Document

/*! ================================================================================
								PRELOADER
==================================================================================*/
$(window).on('load', function () { // makes sure the whole site is loaded
	$('[data-loader="circle-side"]').fadeOut(); // will first fade out the loading animation
	$('#preloader').delay(350).fadeOut('slow'); // will fade out the white DIV that covers the website.
	$('body').delay(350);
});

/*! ================================================================================
								viewport
==================================================================================*/
var viewportmeta = document.querySelector('meta[name="viewport"]');
	if (viewportmeta) {
		if (screen.width < 375) {
			alert("< 375")
			var newScale = screen.width / 375;
			viewportmeta.content = 'width=375, minimum-scale=' + newScale + ', maximum-scale=1.0, user-scalable=no, initial-scale=' + newScale + '';
		} else {
			viewportmeta.content = 'width=device-width, maximum-scale=1.0, initial-scale=1.0';
		}
	}



$(document).ready(function() {
'use strict';



/*! ================================================================================
								SIDENAV
==================================================================================*/
	$('#sidebarCollapse').on('click', function () {
		$('body').toggleClass('sidebar-mini');
	});


/*! ================================================================================
								SMOOTH SCROLLBAR
==================================================================================*/
Scrollbar.initAll({
	alwaysShowTracks: true
});


/*! ================================================================================
								TABLE CHECKBOX
==================================================================================*/
$('#chkParent').click(function() {
	var isChecked = $(this).prop("checked");
	$('table tr:has(td)').find(':first-child input[type="checkbox"]').prop('checked', isChecked);
});
$('table tr:has(td)').find(':first-child input[type="checkbox"]').click(function() {
	var isChecked = $(this).prop("checked");
	var isHeaderChecked = $("#chkParent").prop("checked");
	if (isChecked == false && isHeaderChecked)
		$("#chkParent").prop('checked', isChecked);
	else {
		$('table tr:has(td)').find(':first-child input[type="checkbox"]').each(function() {
			if ($(this).prop("checked") == false)
				isChecked = false;
		});
		$("#chkParent").prop('checked', isChecked);
	}
});

	
/*! ================================================================================
								BOOTSTRAP SWITCH 
==================================================================================*/
if ($("[data-toggle='switch']").length != 0) {
	$("[data-toggle='switch']").bootstrapSwitch();
}

	
/*! ================================================================================
								BOOTSTRAP TOOLTIP INIT 
==================================================================================*/	
$(function () {
  $('[data-toggle="tooltip"]').tooltip()
})

	
/*! ================================================================================
								USER AVATAR UPLOAD
==================================================================================*/	
function readURL(input) {
    if (input.files && input.files[0]) {
        var reader = new FileReader();
        reader.onload = function(e) {
            $('#imagePreview').css('background-image', 'url('+e.target.result +')');
            $('#imagePreview').hide();
            $('#imagePreview').fadeIn(650);
        }
        reader.readAsDataURL(input.files[0]);
    }
}
$("#imageUpload").change(function() {
    readURL(this);
});
	
	
/*! ================================================================================
								QUILL TEXT EDITOR
==================================================================================*/	
	var QuillEditor = (function() {
	// Variables
	var $quill = $('[data-toggle="quill"]');

	// Methods
	function init($this) {
		// Get placeholder
		var placeholder = $this.data('quill-placeholder');
		// Init editor
		var quill = new Quill($this.get(0), {
			modules: {
				toolbar: [
					['bold', 'italic'],
					['link', 'blockquote', 'code', 'image'],
					[{
						'list': 'ordered'
					}, {
						'list': 'bullet'
					}]
				]
			},
			placeholder: placeholder,
			theme: 'snow'
		});
	}

	// Events
	if ($quill.length) {
		$quill.each(function() {
			init($(this));
		});
	}
})();
	
	
/*! ================================================================================
								ADD QUESTIONS CODE
==================================================================================*/	
	$("input[name$='optAnsType1']").click(function() {
        var inputVal = $(this).val();

        $("ul.qtnAns-options").hide();
        $("#qtnAns-options" + inputVal).show();
    });
	
	// Add new element
    $(".addText").click(function(){
        // Finding total number of elements added
        var total_element = $(".element").length;
        // last <div> with element class id
        var lastid = $(".element:last").attr("id");
        var split_id = lastid.split("_");
        var nextindex = Number(split_id[1]) + 1;
        var max = 5;
        // Check total number elements
        if(total_element < max ){
            // Adding new li container after last occurance of element class
            $(".element:last").after("<li class='element d-flex align-items-center position-relative' id='div_"+ nextindex +"'></li>");
            // Adding element to <li>
			$("#div_" + nextindex).append('<div class="d-flex align-items-center position-relative flex-grow-1"> <input type="text" class="form-control" placeholder="" id="ansChk' + nextindex + '"> <div class="custom-control custom-radio"> <input type="radio" id="anstype' + nextindex + '" name="ansType" class="custom-control-input"> <label class="custom-control-label" for="anstype' + nextindex + '"></label> </div> </div> <a href="javascript:void(0)" id="remove_' + nextindex + '" class="btn remove removeText"><i class="ri-subtract-fill"></i></a>');
        }
    });

    // Remove element
    $('body').on('click','.removeText',function(){
        var id = this.id;
        var split_id = id.split("_");
        var deleteindex = split_id[1];
        // Remove <div> with id
        $("#div_" + deleteindex).remove();
    });
	
	// Add new element
    $(".addImg").click(function(){
        // Finding total number of elements added
        var total_imgElement = $(".elementImg").length;
        // last <div> with element class id
        var lastImgid = $(".elementImg:last").attr("id");
        var splitimg_id = lastImgid.split("_");
        var nextImgindex = Number(splitimg_id[1]) + 1;
        var maxImg = 5;
        // Check total number elements
        if(total_imgElement < maxImg ){
            // Adding new li container after last occurance of element class
            $(".elementImg:last").after("<li class='elementImg d-flex align-items-center position-relative' id='Imgdiv_"+ nextImgindex +"'></li>");
            // Adding element to <li>
			$("#Imgdiv_" + nextImgindex).append('<div class="d-flex align-items-center position-relative flex-grow-1"> <input type="file" class="form-control" placeholder="" id="ansImgChk' + nextImgindex + '"> <div class="custom-control custom-radio"> <input type="radio" id="ansImgtype' + nextImgindex + '" name="ansType" class="custom-control-input"> <label class="custom-control-label" for="ansImgtype' + nextImgindex + '"></label> </div> </div> <a href="javascript:void(0)" id="remove_' + nextImgindex + '" class="btn remove removeImg"><i class="ri-subtract-fill"></i></a>');
        }
    });

    // Remove element
    $('body').on('click','.removeImg',function(){
        var imgid = this.id;
        var splitImg_id = imgid.split("_");
        var deleteImgindex = splitImg_id[1];
        $("#Imgdiv_" + deleteImgindex).remove();
    });
	
	
	$("input[name$='ansOptType2']").click(function() {
        var inputVal = $(this).val();

        $(".ansexplanations .form-control").hide();
        $("#ansExpl" + inputVal).show();
    });
	

/*! ================================================================================
								ADD EXAM FORM
==================================================================================*/
$(document).ready(function () {
	$(".add-form-row").click(function () {
		var html = $(".after-add-more").html();
		$(".add-remove-form").append(html);

		$(".add-remove-form > .form-row .btn").removeClass("btn-outline-success add-form-row").addClass("btn-outline-danger remove-form-row");
		$(".add-remove-form > .form-row .btn i").removeClass("ri-add-fill").addClass("ri-subtract-fill");
	});

	$("body").on("click", ".remove-form-row", function () {
		$(this).parents(".form-row").remove();
	});
});


/*! ================================================================================
								DATE TIME PICKER
==================================================================================*/
if ($("#datetimepicker").length != 0) {
		$('.datetimepicker').datetimepicker({
			icons: {
				time: "fa fa-clock-o",
				date: "fa fa-calendar",
				up: "fa fa-chevron-up",
				down: "fa fa-chevron-down",
				previous: 'fa fa-chevron-left',
				next: 'fa fa-chevron-right',
				today: 'fa fa-screenshot',
				clear: 'fa fa-trash',
				close: 'fa fa-remove'
			}
		});

		$('.datepicker').datetimepicker({
			format: 'MM/DD/YYYY',
			icons: {
				time: "fa fa-clock-o",
				date: "fa fa-calendar",
				up: "fa fa-chevron-up",
				down: "fa fa-chevron-down",
				previous: 'fa fa-chevron-left',
				next: 'fa fa-chevron-right',
				today: 'fa fa-screenshot',
				clear: 'fa fa-trash',
				close: 'fa fa-remove'
			}
		});

		$('.timepicker').datetimepicker({
			//          format: 'H:mm',    // use this format if you want the 24hours timepicker
			format: 'h:mm A', //use this format if you want the 12hours timpiecker with AM/PM toggle
			icons: {
				time: "fa fa-clock-o",
				date: "fa fa-calendar",
				up: "fa fa-chevron-up",
				down: "fa fa-chevron-down",
				previous: 'fa fa-chevron-left',
				next: 'fa fa-chevron-right',
				today: 'fa fa-screenshot',
				clear: 'fa fa-trash',
				close: 'fa fa-remove'
			}
		});

	}


/*! ================================================================================
								SWEET ALERTS
==================================================================================*/
$(function() {
        $('[data-toggle="sweet-alert"]').on('click', function(){
            var type = $(this).data('sweet-alert');

            switch (type) {
                case 'basic':
                    swal({
                        title: "Here's a message!",
                        text: 'A few words about this sweet alert ...',
                        buttonsStyling: false,
                        confirmButtonClass: 'btn btn-primary'
                    })
                break;

                case 'info':
                    swal({
                        title: 'Info',
                        text: 'A few words about this sweet alert ...',
                        type: 'info',
                        buttonsStyling: false,
                        confirmButtonClass: 'btn btn-info'
                    })
                break;

                case 'info':
                    swal({
                        title: 'Info',
                        text: 'A few words about this sweet alert ...',
                        type: 'info',
                        buttonsStyling: false,
                        confirmButtonClass: 'btn btn-info'
                    })
                break;

                case 'success':
                    swal({
                        title: 'Success',
                        text: 'A few words about this sweet alert ...',
                        type: 'success',
                        buttonsStyling: false,
                        confirmButtonClass: 'btn btn-success'
                    })
                break;

                case 'warning':
                    swal({
                        title: 'Warning',
                        text: 'A few words about this sweet alert ...',
                        type: 'warning',
                        buttonsStyling: false,
                        confirmButtonClass: 'btn btn-warning'
                    })
                break;

                case 'question':
                    swal({
                        title: 'Are you sure?',
                        text: 'A few words about this sweet alert ...',
                        type: 'question',
                        buttonsStyling: false,
                        confirmButtonClass: 'btn btn-default'
                    })
                break;

                case 'confirm':
                    swal({
                        title: 'Are you sure?',
                        text: "You won't be able to revert this!",
                        type: 'warning',
                        showCancelButton: true,
                        buttonsStyling: false,
                        confirmButtonClass: 'btn btn-danger',
                        confirmButtonText: 'Yes, delete it!',
                        cancelButtonClass: 'btn btn-secondary'
                    }).then((result) => {
                        if (result.value) {
                            // Show confirmation
                            swal({
                                title: 'Deleted!',
                                text: 'Your file has been deleted.',
                                type: 'success',
                                buttonsStyling: false,
                                confirmButtonClass: 'btn btn-primary'
                            });
                        }
                    })
                break;

                case 'image':
                    swal({
                        title: 'Sweet',
                        text: "Modal with a custom image ...",
                        imageUrl: '../../assets/img/ill/ill-1.svg',
                        buttonsStyling: false,
                        confirmButtonClass: 'btn btn-primary',
                        confirmButtonText: 'Super!'
                });
                break;

                case 'timer':
                    swal({
                        title: 'Auto close alert!',
                        text: 'I will close in 2 seconds.',
                        timer: 2000,
                        showConfirmButton: false
                    });
                break;
            }
        });

    });


/*! ================================================================================
								DASHBOARD CHARTS
==================================================================================*/
/*! approvalUsers */
/*var approvalUsersoptions = {
	series: [6],
	chart: {
		width:70,
		height: 120,
		type: 'radialBar',
		animations: {
			enabled: true,
		},
	},
	plotOptions: {
		radialBar: {
			hollow: {
				size: '65%',
			},
			track: {
              background: '#FFF4EC',
			},
			dataLabels: {
				name: {
                  show: false,
				},
				value: {
                  show: true,
                  fontSize: '20px',
                  fontFamily: 'Poppins',
                  fontWeight: 400,
                  color: '#171725',
                  offsetY: 8,
				},
			},
		},
	},
	labels: ['Approvals'],
	colors: ['#0062FF'],
};
var approvalUserschart = new ApexCharts(document.querySelector("#approvalUsers"), approvalUsersoptions);
approvalUserschart.render();
*/
/*! activeUsers */
/*var activeUsersoptions = {
	series: [82],
	chart: {
		width:70,
		height: 120,
		type: 'radialBar',
		animations: {
			enabled: true,
		},
	},
	plotOptions: {
		radialBar: {
			hollow: {
				size: '65%',
			},
			track: {
              background: '#FFF4EC',
			},
			dataLabels: {
				name: {
                  show: false,
				},
				value: {
                  show: true,
                  fontSize: '20px',
                  fontFamily: 'Poppins',
                  fontWeight: 400,
                  color: '#171725',
                  offsetY: 8,
				},
			},
		},
	},
	labels: ['Active'],
	colors: ['#3DD598'],
};
var activeUserschart = new ApexCharts(document.querySelector("#activeUsers"), activeUsersoptions);
activeUserschart.render();
*/
/*! inActiveUsers */
/*var inActiveUsersoptions = {
	series: [12],
	chart: {
		width:70,
		height: 120,
		type: 'radialBar',
		animations: {
			enabled: true,
		},
	},
	plotOptions: {
		radialBar: {
			hollow: {
				margin: 0,
				size: '65%',
			},
			track: {
              background: '#FFF4EC',
			},
			dataLabels: {
				name: {
                  show: false,
				},
				value: {
                  show: true,
                  fontSize: '20px',
                  fontFamily: 'Poppins',
                  fontWeight: 400,
                  color: '#171725',
                  offsetY: 8,
				},
			},
		},
	},
	labels: ['Inactive'],
	colors: ['#FF974A'],
	
};
var inActiveUserschart = new ApexCharts(document.querySelector("#inActiveUsers"), inActiveUsersoptions);
inActiveUserschart.render();
*/


/*! ================================================================================
								DASHBOARD DATE
==================================================================================*/
var now = dateFormat(new Date(), "dddd, mmmm dS, yyyy, h:MM:ss TT");
     // Saturday, June 9th, 2007, 5:46:21 PM
$('#date').append(now);


/*! ================================================================================
								CA DROPZONE
==================================================================================*/
var Dropzones = (function() {

	//
	// Variables
	//

	var $dropzone = $('[data-toggle="dropzone"]');
	var $dropzonePreview = $('.dz-preview');

	//
	// Methods
	//

	function init($this) {
		var multiple = ($this.data('dropzone-multiple') !== undefined) ? true : false;
		var preview = $this.find($dropzonePreview);
		var currentFile = undefined;

		// Init options
		var options = {
			url: $this.data('dropzone-url'),
			thumbnailWidth: null,
			thumbnailHeight: null,
			previewsContainer: preview.get(0),
			previewTemplate: preview.html(),
			maxFiles: (!multiple) ? 1 : null,
			acceptedFiles: (!multiple) ? 'image/*' : null,
			init: function() {
				this.on("addedfile", function(file) {
					if (!multiple && currentFile) {
						this.removeFile(currentFile);
					}
					currentFile = file;
				})
			}
		}

		// Clear preview html
		preview.html('');

		// Init dropzone
		$this.dropzone(options)
	}

	function globalOptions() {
		Dropzone.autoDiscover = false;
	}


	//
	// Events
	//

	if ($dropzone.length) {

		// Set global options
		globalOptions();

		// Init dropzones
		$dropzone.each(function() {
			init($(this));
		});
	}


})();

	
	
	
$('.listGrid-btns a').on('click', function(){
    $('a.active').removeClass('active');
    $(this).addClass('active');
});
	
$('.listGrid-btns .listView-btn').on('click', function(){
	$('.testsList').addClass('listView');
});
$('.listGrid-btns .gridView-btn').on('click', function(){
	$('.testsList').removeClass('listView');
});


});



