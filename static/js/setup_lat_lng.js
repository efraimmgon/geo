$(function() {
	// Important: identifies the place where the lat lng wiil be taken
	var region = "Sinop, Mato Grosso, Brazil"; 
	var index = 1; 

	var $feedback = $('#id_feedback');
	var $rangeStart = $('#id_start');
	var $rangeStop = $('#id_stop');
	var $pksArray = $('#id_pks');

	getLatLng();

	updateForm();

	function getLatLng() {
	/* Fetches the data from the DB, finds its lat lng, and updates the info */
		alert(index);
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
			
			if (index == 4) {
				alert("Got all.");
				return;
			} else {
				index++;
				return getLatLng();	
			}
		}

		$data = $rangeStop.serialize()

		$.ajax({
			url: '/setup/get_address/',
			data: $data,
			success: function(data) {
				$.each(data, function() {
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
						/*		value = $pksArray.val();
								value = value.split(',');
								$pksArray.val(value);*/
							}
						} else {
							$statusError = $('<br /> ' + id + ': ' + local + ': ' + status);
							$feedback.append($statusError);
						}
					});  // geocoder 
				}); // $.each()
			},
			complete: function() {
				/* Controls when the function is run */
				index++;
				return timeout = setTimeout(getLatLng, 20000);	
			}
		}); // $.ajax()
	}; // getLatLng()

	function updateForm() {
		var $form = $('#id_updateForm');
		$form.on('submit', function(e) {
			e.preventDefault();
			var $data = $form.serialize();

			$.ajax({
				type: "POST",
				url: '/setup/update_db/',
				data: $data,
				complete: function() {
					alert("Update done.");
				},
				success: function(data) {
					var $response = $(data);
					$feedback.append($response);
				}, // success
				fail: function() {
					alert("Sync failed. Please try again later.");
				}	
			}); // $.ajax
		}); // submit event
	}; // updateForm()

});	// IIAF