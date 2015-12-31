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
	var index = 1;
	var $html;
	var heatmap = new google.maps.visualization.HeatmapLayer();

	var $settings = $('#settings');
	var $ocorrenciasForm = $('#ocorrenciasForm');

	$settings.hide();
	$('#control').on('click', function() {
		$settings.slideToggle();
	});

	/* type of marker */
	var styleType = 'basicMarker';
	$('#styleForm').on('change', function(e) {
		e.preventDefault();
		styleType = $('#styleType').val();
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
			success: function(data) {
				$.each(data, function() {
					var id = this.id;
					var natureza = this.natureza;
					var local = this.local;

					if (this.lat && this.lng) {
						var latLng = new google.maps.LatLng(
							parseFloat(this.lat),
							parseFloat(this.lng)
						);
						if ($styleType == 'basicMarker') {
							createMarker(latLng, id, natureza, local);
						} else {
							heatmapData.push(latLng);	
						}
						ocorrencias.push({natureza: this.natureza, local: this.local, data: this.unixtime, hora: this.hora});
					} else {
						var el = document.getElementById('current');
							var content = el.innerHTML;
						el.innerHTML = content +  "<br> " + id + ': ' + local + ': not found';
					}
				}); 
			},
			fail: function() {
				document.getElementById('current').innerHTML = 'Houve um problema com a solicitação. [AJAX]';
			},
			complete: function() {
				if ($styleType == 'heatmap') {
					createHeatmap(heatmapData);
				}
				tableGeneration();
				sortableTable();

				$html = '<h3>Ocorrências Registradas</h3>';
				if (natRoubo) $html += '<span style="padding-right: 30px">Roubos: ' + natRoubo + '</span>';
				if (natFurto) $html += '<span style="padding-right: 30px">Furtos: ' + natFurto + '</span>';
				if (natEnt) $html += '<span style="padding-right: 30px">Entorpecentes: ' + natEnt + '</span>';
				if (natHom) $html += '<span style="padding-right: 30px">Homicídios: ' + natHom + '</span>';
				if (natOutros) $html += '<span>Outras ocorrências: ' + natOutros + '</span>';

				var elInfo = document.getElementById('info')
				elInfo.innerHTML = $html;
			}
		}); // END of ajax call
	}); // END of ocorrenciasForm
	
	oms.addListener('spiderfy', function(markers) {
			iw.close();
	});
	
	function centerMapRegion() {
		var geocoder = new google.maps.Geocoder();
		geocoder.geocode({address: region}, function(results, status) {
			if(status == google.maps.GeocoderStatus.OK) {
				map.setCenter(results[0].geometry.location);
			} else {
				alert('Geocode was not successful for the following reason: ' + status);
			}
		});
	}

	function createMarker(latlng, id, natureza, address) {
		var html = "<b> id: " + id + ' ' + natureza + "</b> <br />" + address;
		window.setTimeout(function() {
			var markerColor, markerText;
			if(/furto/i.test(natureza)) {
				markerColor = "E25A5A";
				markerText = "F"
			} else if(/roubo/i.test(natureza)) {
				markerColor = "fff";
				markerText = "R";
			} else if(/hom/i.test(natureza)){
				markerColor = "000";
				markerText = "H";
			} else if(/drogas/i.test(natureza)){
				markerColor = "b4eeb4";
				markerText = "E";
			} else {
				markerColor = "ddd";
				markerText = "O";
				natOutros++;
			}
			var marker = new StyledMarker({
				styleIcon: new StyledIcon(StyledIconTypes.MARKER,{color: markerColor,text: markerText}),
				position:latlng,
				map:map
			});
			google.maps.event.addListener(marker, 'click', function() {
				iw.setContent(html);
				iw.open(map, marker);
			});
			google.maps.event.addListener(marker, 'mouseover', function() {
				marker.setOpacity(0.5);
			});
			google.maps.event.addListener(marker, 'mouseout', function() {
				marker.setOpacity(1);
			});
			markers.push(marker);
			oms.addMarker(marker);
		}, 100 * index); // END of setTimeout

		var test;
		if(/roubo/i.test(natureza)) test = 1;
		else if(/furto/i.test(natureza)) test = 2;
		else if(/homic[ií]dio/i.test(natureza)) test = 3;
		else if(/drogas/i.test(natureza)) test = 4;
		else test = 5;

		switch(test){
			case 1: natRoubo++; break;
			case 2: natFurto++; break;
			case 3: natHom++; break;
			case 4: natEnt++; break;
			case 5: natOutros++; break;
		}
		index++;
	} // END OF createMarker()

	function createHeatmap(heatmapData) {
		heatmap = new google.maps.visualization.HeatmapLayer({
			data: heatmapData,
			dissipating: false,
			map: map
		})
		heatmap.set('radius', 1);
		heatmap.set('scaleRadius', false);
	}

	function tableGeneration() {
	/* Creates the table based on the data given by the ajax call */
		document.getElementById('dados-ocorrencias').innerHTML = '';
		var $table = $('<table class="sortable"></table>');
		var $thead = $(
			"<thead>" +
				"<tr>" +
					"<th data-sort='name'>Natureza</th>" +
					"<th data-sort='name'>Local</th>" +
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
			var data = new Date(ocorrencia.data * 1000);
			var dataOcorrencia = data.getDate() + '/' + (data.getMonth() + 1) + '/' + data.getFullYear();
			var weekday = data.getDay();
			switch(weekday) {
				case 0: weekday = 'Domingo'; break;
				case 1: weekday = 'Segunda'; break;
				case 2: weekday = 'Terça'; break;
				case 3: weekday = 'Quarta'; break;
				case 4: weekday = 'Quinta'; break;
				case 5: weekday = 'Sexta'; break;
				case 6: weekday = 'Sábado'; break;
			}

			if (notEven % 2 == 0) {
				var $row = $('<tr class="even"></tr>');	
			} else {
				var $row = $('<tr></tr>');	
			}
			
			$row.append( $('<td></td>').text(ocorrencia.natureza) );
			$row.append( $('<td></td>').text(ocorrencia.local) );
			$row.append( $('<td></td>').text(dataOcorrencia) );
			$row.append( $('<td></td>').text(weekday) );
			$row.append( $('<td></td>').text(ocorrencia.hora) );
			$tableBody.append( $row );

			notEven++
		}
		$table.append($tableBody);
		$('#dados-ocorrencias').append($table);
	} // tableGeneration()

	function sortableTable() {
	/* Allows the table to be sorted */
		var compare = {
			name: function(a, b) {
				a = a.replace(/^(rua)|(avenida)|(mt) /i, '');
				b = b.replace(/^(rua)|(avenida)|(mt) /i, '');

				if (a < b) return -1;
				else return a > b ? 1 : 0;
			},
			duration: function(a, b) {
				a = a.split(':');
				b = b.split(':');

				a = Number(a[0]) * 60 + Number(a[1]);
				b = Number(b[0]) * 60 + Number(b[1]);

				return a - b;
			},
			date: function(a, b) {
				a = returnDate(a);
				b = returnDate(b);
				function returnDate(a) {
					var day = a.split('/')[0];
					var month = a.split('/')[1];
					var year = a.split('/')[2];
					var dateA = new Date(year, month, day);
					return a = dateA.getTime();
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
		document.getElementById('current').innerHTML = '';

		index = 1;
	}
});