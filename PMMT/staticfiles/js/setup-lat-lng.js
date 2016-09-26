$(function() {
	// Important: identifies the place where the lat lng wiil be taken
	var region = "Sinop - MT"; 
	var count = 0; 

	var $feedback = $('#id_feedback');
	var $responseData = $('#id_response_data');

	getLatLng();

	updateForm();

	function getLatLng() {
	/* Fetches the data from the DB, finds its lat lng, and updates the info */
		// a hack to get the html to be uploaded
		var $request = $.ajax({
			url: '/setup/get_address/'
		})
		.fail( function(jqXHR, textStatus, errorThrown) {
			alert("Request failed: " + textStatus + ', ' + errorThrown);
		})
		.done( function(json) {
			process_json(json);
		}); // .done()
	}; // getLatLng()

	function process_json(json) {
		/* Takes a json object, containing an address, and 
		appends an input elt with the lat and lng based on the address*/
		if (json.end) {
			alert('No more!');
			return;
		}
		if (count == json.length) {
			alert('DONE');
			return;
		}
		var id = json[count].pk;
		var natureza = json[count].fields.natureza;
		var bairro = json[count].fields.bairro;
		var via = json[count].fields.via;
		var numero = json[count].fields.numero;
		if (via) 	via 	= via + ', ';			
		else 	 	via 	= '';
		if (numero) numero 	= 'nº ' + numero + ' - ';
		else 		numero 	= '';
		if (bairro == 'Centro') {
			bairro = 'Setor Comercial';
		}
		if (bairro) bairro 	= bairro + ' - ';
		else 		bairro 	= ''; 
		var addrs = via + numero + bairro;
		var ponto = addrs + region;

		find_lat_lng(ponto, addrs, id);
		count++;
		if (count % 10 == 0) {
			setTimeout(process_json, 20000, json);
		} else {
			process_json(json);
		}
	};

	function find_lat_lng(ponto, address, id) {
		/* Finds a lat and lng based on a given address. */
		var geocoder = new google.maps.Geocoder();
		geocoder.geocode({'address': ponto}, function(results, status) {
			if (status === google.maps.GeocoderStatus.OK) { 
				var latitude = results[0].geometry.location.lat();
				var longitude = results[0].geometry.location.lng();
				if (latitude == -11.8608456 && 
					longitude == -55.50954509999997) {
					latitude = null;
					longitude = null;
				}
				$found = $("<p> <input name='"+ id +"' type='text' value='"+
					latitude +' '+
					longitude +"' /><br />"+
					address +"</p>");
				$feedback.append($found);
			} /*else if (status == 'ZERO_RESULTS') {
				var latitude = null;
				var longitude = null;
				$found = $("<p> <input name='"+ id +"' type='text' value='"+
					latitude +' '+
					longitude +"' /><br />"+
					address +"</p>");
				$feedback.append($found);
			} */else {
				$statusError = $(
					'<p> '+ id +': '+ address +': '+ status +'</p>'
				);
				$feedback.append($statusError);
			}
		});
	};

	function updateForm() {
		var $form = $('#id_updateForm');
		$form.on('submit', function(e) {
			e.preventDefault();
			var $request = $.ajax({
				url: '/setup/update_db/',
				method: 'POST',
				data: $form.serialize()
			})
			.done( function(json) {
				if (json.errors) {
					alert(json.errors);
				}
				if (json.OK) {
					$responseData.append(json.OK);
				}
			})
			.fail( function(jqXHR, textStatus, errorThrown) {
				alert("Request failed: "+ textStatus +', '+ errorThrown);
			});
		});
	}; // updateForm()

});	// IIAF
