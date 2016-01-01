$(function() {
	// Important: identifies the place where the lat lng wiil be taken
	var region = "Sinop, Mato Grosso, Brazil"; 
	var index = 1; 

	var $feedback = $('#id_feedback');
	var $rangeStart = $('#id_start');
	var $rangeStop = $('#id_stop');
	var $pksArray = $('#id_pks');
	var $responseData = $('#id_response_data');

	getLatLng();

	updateForm();

	function getLatLng() {
	/* Fetches the data from the DB, finds its lat lng, and updates the info */
		// a hack to get the html to be uploaded
		if (index % 2 == 0) {
			var stopArray = $pksArray.val();
			stopArray = stopArray.split(',');

			stopArray.sort(function(a, b) {
				return a - b;
			});

			if ($rangeStart.val() == 0) {
				$rangeStart.val(stopArray[0]);
			}

			var stop = stopArray[stopArray.length - 1]
			$rangeStop.val(stop);
			
			if (index == 20) {
				alert("Got all.");
				return;
			} else {
				index++;
				return getLatLng();	
			}
		}

		$data = $rangeStop.serialize()

		var $request = $.ajax({
			url: '/setup/get_address/',
			data: $data
		})
		.fail( function(jqXHR, textStatus, errorThrown) {
			alert("Request failed: " + textStatus + ', ' + errorThrown);
		})
		.done( function(json) {
			if (json.end) {
				alert(json.end);
				return;
			}

			$.each(json, function() {
				var id = this.pk;
				var natureza = this.fields.natureza;
				var local = this.fields.local;
				var ponto = local + ', ' + region;

				var geocoder = new google.maps.Geocoder();
				geocoder.geocode({'address': ponto}, function(results, status) {
					if (status === google.maps.GeocoderStatus.OK) { 
						$found = $("<br> <input id='loc-" + id + "' type='text' name='loc-" + 
							id + "' value='" + id + ' ' + 
							results[0].geometry.location.lat() + ' ' +
							results[0].geometry.location.lng() + "' />");
						$feedback.append($found);
							
						if (id) {
							var value = $pksArray.val();
							if (value) {
								value = value + ',' + id;
							} else {
								value = id;
							}			
							$pksArray.val(value);
						}
					} else {
						$statusError = $('<br /> ' + id + ': ' + local + ': ' + status);
						$feedback.append($statusError);
					}
				});  // geocoder 
			}); // $.each()
			index++;
			return timeout = setTimeout(getLatLng, 20000);
		})
	}; // getLatLng()

	function updateForm() {
		var $form = $('#id_updateForm');
		$form.on('submit', function(e) {
			e.preventDefault();
			var $data = $form.serialize();

			var $request = $.ajax({
				url: '/setup/update_db/',
				method: 'POST',
				data: $data
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
				alert("Request failed: " + textStatus + ', ' + errorThrown);
			});
		});
	}; // updateForm()

});	// IIAF