$(function() { 
	var map, gm, oms, iw;
	var markers = [];
	var ocorrencias = [];
	var heatmapData = [];
	var natRoubo = 0;
	var natFurto = 0;
	var natHom = 0;
	var natOutros = 0;
	var notEven = 1;
	var $html;
	var heatmap = new google.maps.visualization.HeatmapLayer();

	var $settings = $('#settings');
	var $ocorrenciasForm = $('#ocorrenciasForm');
	var $info = $('#id_info');
	var $dados_ocorrencias = $('#dados-ocorrencias');

	$settings.hide();
	$('#control').on('click', function() {
		$settings.slideToggle();
	});

	/* type of marker */
	var styleType = 'basicMarker';
	$('#styleForm').on('change', function(e) {
		e.preventDefault();
		styleType = $('#id_marker_style').val();
		clearLocations();
		$settings.slideToggle();
	})

	var myLatLng = {lat: -11.855275, lng: -55.505966}

	initialize();

	function initialize() {
		map = new google.maps.Map(document.getElementById('map'), {
			zoom: 15,
			center: myLatLng,
			mapTypeId: google.maps.MapTypeId.ROADMAP
		});
		
		gm = google.maps;
		iw = new gm.InfoWindow();
		oms = new OverlappingMarkerSpiderfier(map);
	}

	$ocorrenciasForm.on('submit', function(e) {
		e.preventDefault();
		clearLocations();

		natRoubo = 0;
		natFurto = 0;
		natEnt = 0;
		natHom = 0;
		natOutros = 0;
		ocorrencias = [];

		$.ajax({
			type: "POST",
			url: '/analise_criminal/mapAjax/',
			data: $ocorrenciasForm.serialize(),
			success: function(json) {
				if (json.errors) {
					var $error = $('<ul class="errorlist"></ul>');
					for (var key in json.errors) {
						$error.append('<li>' + key + ': ' + json.errors[key][0] + '</li>');
					}
					$info.append($error);
					return;
				}

				$.each(json, function() {

					var json_id = this.pk;
					var json_natureza = this.fields.natureza;
					var json_bairro = this.fields.bairro;
					var json_via = this.fields.via;
					var json_numero = this.fields.numero;
					var json_data = this.fields.formatted_date;
					var json_weekday = this.fields.weekday;
					var json_hora = this.fields.hora;
					var lat = this.fields.latitude;
					var lng = this.fields.longitude;

					if (json_numero) {
						json_via += ', ' + json_numero;
					}
					
					if (lat && lng) {
						var latLng = new google.maps.LatLng(
							parseFloat(lat),
							parseFloat(lng)
						);
						if (styleType == 'basicMarker') {
							var address = json_bairro + ', ' + json_via;
							createMarker(latLng, json_id, json_natureza, address);
						} 
						ocorrencias.push({natureza: json_natureza, bairro: json_bairro, 
							via: json_via, data: json_data, hora: json_hora, weekday: json_weekday});
					} else {
						var notFound = '<br>' + json_id + ': ' + json_bairro + ', ' + 
						json_via + ': not found';
						$info.append(notFound);
					}
				}); 
			},
			fail: function() {
				$info.html('Houve um problema com a solicitação. [AJAX]');
			},
			complete: function() {
				if (ocorrencias.length == 0) {
					return;
				}
				tableGeneration();
				sortableTable();
			}
		}); // END of ajax call
	}); // END of ocorrenciasForm
	
	oms.addListener('spiderfy', function(markers) {
		iw.close();
	});

	function createMarker(latlng, id, natureza, address) {
		var html = "<b> id: " + id + ' ' + natureza + "</b> <br />" + address;
		var marker = new google.maps.Marker({
			map: map,
			position: latlng,
			draggable: true
		});
		google.maps.event.addListener(marker, 'click', function() {
			iw.setContent(html);
			iw.open(map, marker);
		});
		google.maps.event.addListener(marker, 'dragend', function(evt) {
			$('#updateForm').append("<br /><input id='" + id + "' name='" + id + 
				"' type='text' value='" + id + ' ' + evt.latLng.lat().toFixed(8) + 
				' ' + evt.latLng.lng().toFixed(8) + "' />");
		})
			
		markers.push(marker);
		oms.addMarker(marker);
	} // END OF createMarker()

	function tableGeneration() {
		/* 
		** Creates the table based on the data given by the ajax call 
		** global: ocorrencias
		*/
		var $table = $('<table class="sortable"></table>');
		var $thead = $(
			"<thead>" +
				"<tr>" +
					"<th data-sort='name'>Natureza</th>" +
					"<th data-sort='name'>Bairro</th>" +
					"<th data-sort='name'>Via</th>" +
					"<th data-sort='date'>Data</th>" +
					"<th data-sort='weekday'>Dia da semana</th>" +
					"<th data-sort='duration'>Hora</th>" +
				"</tr>" +
			"</thead>"
		);

		$table.append($thead);
		var $tableBody = $('<tbody></tbody>');

		for (var i = 0; i < ocorrencias.length; i++) {
			var ocorrencia = ocorrencias[i];

			if (notEven % 2 == 0) {
				var $row = $('<tr class="even"></tr>');	
			} else {
				var $row = $('<tr></tr>');	
			}
			
			$row.append( $('<td></td>').text(ocorrencia.natureza) );
			$row.append( $('<td></td>').text(ocorrencia.bairro) );
			$row.append( $('<td></td>').text(ocorrencia.via) );
			$row.append( $('<td></td>').text(ocorrencia.data) );
			$row.append( $('<td></td>').text(ocorrencia.weekday) );
			$row.append( $('<td></td>').text(ocorrencia.hora) );
			$tableBody.append( $row );

			notEven++
		}
		$table.append($tableBody);
		$dados_ocorrencias.append($table);
	} // tableGeneration()

	function sortableTable() {
		/* Allows the tables to be sorted */
		var compare = {
			name: function(a, b) {
				a = a.replace(/^(rua)|(avenida)|(jardim)\s/i, '');
				b = b.replace(/^(rua)|(avenida)|(jardim)\s/i, '');

				if (a < b) return -1;
				else return a > b ? 1 : 0;
			},
			duration: function(a, b) {
				if (a == 'null') {
					return 1;
				} else if (b == 'null') {
					return -1;
				}
				a = a.split(':');
				b = b.split(':');

				a = Number(a[0]) * 60 + Number(a[1]);
				b = Number(b[0]) * 60 + Number(b[1]);

				return a - b;
			},
			date: function(a, b) {
				a = returnDate(a);
				b = returnDate(b);
				function returnDate(dateString) {
					var day = dateString.split('/')[0];
					var month = dateString.split('/')[1];
					var year = dateString.split('/')[2];
					var dateObj = new Date(year, month, day);
					return dateObj.getTime();
				}
				a = new Date(a);
				b = new Date(b);

				return a - b;
			},
			weekday: function(a, b) {
				function returnWeekday(x) {
					switch (x) {
						case 'Segunda': x = 1; break;
						case 'Terça': x = 2; break;
						case 'Quarta': x = 3; break;
						case 'Quinta': x = 4; break;
						case 'Sexta': x = 5; break;
						case 'Sábado': x = 6; break;
						case 'Domingo': x = 7; break;
					}
					return x;
				}
				a = returnWeekday(a);
				b = returnWeekday(b);

				return a - b;
			}
		}; // compare

		$('.sortable').each(function() {

			var $table = $(this);
			var $tbody = $table.find('tbody');
			var $controls = $table.find('th');
			var rows = $tbody.find('tr').toArray();

			$controls.on('click', function() {
				$('.even').removeClass('even');

				var $header = $(this);
				var order = $header.data('sort');
				var column;

				if ($header.is('.ascending') || $header.is('.descending')) {
					$header.toggleClass('ascending descending');
					$tbody.append(rows.reverse());

					$('.sortable tr:odd').addClass('even');
				} else {
					$header.addClass('ascending');
					$header.siblings().removeClass('ascending descending');
					if (compare.hasOwnProperty(order)) {
						column = $controls.index(this);

						rows.sort(function(a, b) {
							a = $(a).find('td').eq(column).text();
							b = $(b).find('td').eq(column).text();
							return compare[order](a, b);
						});
						$tbody.append(rows);

						$('.sortable tr:odd').addClass('even');
					}
				}
			});
		});
	} // sortableTable()

	function clearLocations() {
		/* Resets the markers and heatmapData array, clearing the map */
		iw.close();
		for (var i = 0; i < markers.length; i++) {
			markers[i].setMap(null);
		}
		markers.length = 0;
		heatmapData.length = 0;
		heatmap.setMap(null);
		document.getElementById('errors').innerHTML = '';
		$info.html('');
		$dados_ocorrencias.html('');
	}
});