<div id="side-panel-left">
</div>
<div id="home-screen">
	<h1 id="main-title-label">Liber Usualis Project</h1>
	<nav id="center-nav" x-data="{
		pages:[
			{'path':'/{{preferredlocale}}/pray', 'name':'{{text['pray']}}'},
			{'path':'/{{preferredlocale}}/about', 'name':'{{text['about']}}'},
			{'path':'/{{preferredlocale}}/help', 'name':'{{text['help']}}'},
			{'path':'/{{preferredlocale}}/credit', 'name':'{{text['credit']}}'}
		]
		}">
		<template x-for="page in pages">
			<a class="nav-element-link" :href="page.path"><span class="nav-element-text" x-text="page.name"></span></a>
		</template>
	</nav>
	<div style="height:2em;"></div>
	<form id="paypal-donate-button" action="https://www.paypal.com/donate" method="post" target="_top">
	<input type="hidden" name="hosted_button_id" value="25CUBHQKYN67Y" />
	<input type="image" src="https://www.paypalobjects.com/en_US/i/btn/btn_donate_LG.gif" border="0" name="submit" title="PayPal - The safer, easier way to pay online!" alt="Donate with PayPal button" />
	<img alt="" border="0" src="https://www.paypal.com/en_US/i/scr/pixel.gif" width="1" height="1" />
	</form>
</div>
<div id="side-panel-right">
</div>
