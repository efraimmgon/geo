/* OSC FUNCTIONS */

function O(obj) {
	if (typeof obj == 'object') return obj
	else return document.getElementById(obj)
}

function S(obj) {
	return O(obj).style
}

function C(name) {
	var elements = document.getElementsByTagName('*')
	var objects = []
	
	for (var i = 0; i < elements.length; ++i)
		if (elements[i].className == name)
			objects.push(elements[i])
	
	return objects
}


/* NAV DROPDOWN APP */

var main = function() {	
	// DROPDOWN: HEADER.PHP
	toggleMenu('.dropdown_toggle1', '.dropdown_menu1');
	toggleMenu('.dropdown_toggle2', '.dropdown_menu2');
	toggleMenu('.dropdown_toggle3', '.dropdown_menu3');

	menuToggle();

	function toggleMenu(menu, subMenu) {
		$(menu).on('mouseover', function() {
			$(subMenu).show();
		})
		$(menu).on('mouseout', function() {
			$(subMenu).hide();
		})
	}

	function menuToggle() {
		var menu = $('.menu');

		menu.children().children().on('mouseover', function() {
			$(this).addClass('active');
		})
		menu.children().children().on('mouseout', function() {
			$(this).removeClass('active');
		})
	}

}
	
$(document).ready(main);