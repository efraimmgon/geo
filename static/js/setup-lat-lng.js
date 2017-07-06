$(function() {
	// GLOBAL STATE ------------------------------------------------

	var app_state = {
	// Important: identifies the place where the lat lng wiil be taken
		region: "Sinop - MT",
		count: 0,
		$feedback: $('#id_feedback'),
		$responseData: $('#id_response_data')
	};

	// Helper

	// destructive
	var partition = function partition(arr, n) {
		if (arr.length) {
			return [arr.splice(0, n)].concat(partition(arr, n));
		} else {
			return [];
		}
	};

	// Functions ---------------------------------------------------

	var geocode = function (ponto, address, id) {
		"Find a lat and lng based on the given address."
		var geocoder = new google.maps.Geocoder(),
			latitude,
			longitude,
			response = {address: address, id: id}

		geocoder.geocode({'address': ponto}, function(results, status) {
			if (status === google.maps.GeocoderStatus.OK) {
				latitude = results[0].geometry.location.lat();
				longitude = results[0].geometry.location.lng();
	// latitude === -11.8608456 & longitude === -55.50954509999997
	// seem to be the default location for Sinop
				return response.OK = {lat: latitude, lng: longitude};
			} else {
				return response.ERROR = {status: status};
			}

	var render_result = function (response) {
		if (response.OK) {
			var $item = $("<p></p>").append(
				"<input name='" + response.id + "' type='text' value='" +
				response.OK.lat + " " + response.OK.lng + "' />" +
				 "<br />" + response.address
			);
			app_state.$feedback.append($item);
		} else {
			app_state.$feedback.append(
				$('<p>' + response.id + ': ' + response.address + ': ' +
				  response.ERROR.status + '</p>')
			);
		}
	};

	var render_item = function (item) {
		var id = item.pk,
			natureza = item.fields.natureza,
			bairro = item.fields.bairro,
			via = item.fields.via,
			numero = item.fields.numero,
			ponto;

		// format args for visual inspection
		via = via ? (via + ", ") : "";
		numero = numero ? ("nº " + numero + " - ") : "";
		bairro = bairro ? (bairro + " - ") : "";

		addrs = via + numero + bairro;
		ponto = addrs + region;

		response = geocode(ponto, addrs, id);
		render_result(response);
	};

	var process_json = function process_json(items) {
		if (!items.length) {
			return alert("Done");
		}

		var next_items = items[0],
			remaining_items = items.slice(1);

		next_items.map(render_item);

		setTimeout(process_json, (20 * 1000), remaining_items);
	};

	var getLatLng = function () {
		var $request = $.ajax({
			url: '/setup/get-address/'
		})
		.fail( function(jqXHR, textStatus, errorThrown) {
			alert("Request failed: " + textStatus + ', ' + errorThrown);
		})
		.done( function(json) {
			process_json(partition(json, 10));
		});
	};

	var updateForm = function () {
		var $form = $('#id_updateForm');

		$form.on('submit', function(e) {
			e.preventDefault();
			var $request = $.ajax({
				url: '/setup/update-db/',
				method: 'POST',
				data: $form.serialize()
			})
			.done( function(json) {
				if (json.errors) {
					alert(json.errors);
				}
				if (json.OK) {
					app_state.$responseData.append(json.OK);
				}
			})
			.fail( function(jqXHR, textStatus, errorThrown) {
				alert("Request failed: "+ textStatus +', '+ errorThrown);
			});
		});
	};

	// Execution ---------------------------------------------------

	// Fetch data from the DB, find its lat & lng, and update the info
	getLatLng();

	// - Take a json object containing an address and
	// - append an input elt with the lat and lng based on the address.
	// Note:
	We do this so we can catch some errors concerning the point
	// and its address, although I believe this can be automated.
	// If a point is not found based on the address then it falls
	// back to a default point. All we have to do is select the rows
	// and group them by latitude & longitude. The one with most
	// occurrences is the default one, most likely. (We can later
	// compare the lat and long with the address to find out)
	updateForm();

});	// IIAF
