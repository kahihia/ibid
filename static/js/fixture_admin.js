
$(function() {
	$('[id^="add_id"]').remove();
	$('[id$="-item"]').combobox();

	$('[id$="-item"]').change(function(){
		data = {'item_id' : $(this).val()};
		
		var set_number = $(this).attr('id').replace('id_templateauction_set-', '').replace('-item', '');
		
		$.post('/item_price/', data, 
				function(data){update_precap_field(data, set_number);}, 
					"json");
	});
	
	$('[id$="-precap_bids"]').each(function(){
		var set_number = $(this).attr('id').replace('id_templateauction_set-', '').replace('-precap_bids', '');
		
		$('<a id="x3link-' + set_number + '" href="#"> x3</a>').insertAfter($(this));
		$('<a id="x2link-' + set_number + '" href="#"> x2</a>').insertAfter($(this));
	});
	
	$('.add-row').remove();
	
	//extra button
	var url_array = document.location.href.split('/');
	var model_id = parseInt(url_array[url_array.length-2])
	
	if (model_id) {
		$('.submit-row').append('<input id="run_btn" type="button" class="default" value="Run Fixture"/>');
		$('#run_btn').click(function(){
			$.post('/run_fixture/', {'fixture_id' : model_id}, function(data){show_confirmation()}, "json");
		});
	}
	
});


function show_confirmation(){
	var html =	'<ul class="messagelist"><li class="info">' +
				'The fixture was run successfully.' +
				'</li></ul>';
	$(html).insertAfter('.breadcrumbs');
}

function update_precap_field(data, set_number){
	var precap_id = '#id_templateauction_set-' + set_number + '-precap_bids';
	$(precap_id).val(data.price);
	
	$('#x3link-' + set_number).click(function(){
		$(precap_id).val(data.price * 3)
	});
	
	$('#x2link-' + set_number).click(function(){
		$(precap_id).val(data.price * 2)
	});
}