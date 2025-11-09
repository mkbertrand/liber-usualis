function translation(locale) {
	if (locale == 'en') {
		return ['english'];
	} else if (locale == 'de') {
		return ['deutsch'];
	} else {
		return ['english'];
	}
}

// Featured art panels will be 3:10
const panelratio = 3/10;

var panelsopen = false;
var panelquotient = 0;
var riteheight = 1;
function dopanelsize() {
	var height = $(window).innerHeight() - parseInt(window.getComputedStyle(document.body).getPropertyValue('--top-bar-title-height').slice(0, -2)) - 1;
	var minritewidth = height / 1.6;
	var panelwidth = height * panelratio;
	canmakepanels = panelwidth * 2 + minritewidth < $(document).width();

	if (!canmakepanels) {
		$('#rite-page-container').css('width', '100%');
		$('#side-panel-left').css('width', 0);
		$('#side-panel-right').css('width', 0);
		$('#content-container-outer').css('width', '100%');
		panelsopen = false;
		panelquotient = 0;
		return;
	}

	// In other words, the rite panel will never be wider than 1:1
	ritewidth = Math.min(height, $(document).width() - 2 * panelwidth);

	$('#rite-page-container').css('width', `${ritewidth}px`);
	$('#side-panel-left').css('width', `${panelwidth}px`);
	$('#side-panel-right').css('width', `${panelwidth}px`);
	$('#content-container-outer').css('width', `${ritewidth + panelwidth * 2}px`);

	panelsopen = true;

	if (panelwidth / riteheight != panelquotient) {
		generatepanels();
	}

	panelquotient = panelwidth / riteheight;
}

function generatepanels() {
	riteheight = $('#rite-container').height();
}
