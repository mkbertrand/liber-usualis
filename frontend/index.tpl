<!DOCTYPE html>
<html lang='en'>
	<head>
		<title>Psalterium</title>
		% include('frontend/header.tpl')
		<link rel="stylesheet" type="text/css" href="/styles/index.css">
		<link rel="stylesheet" type="text/css" href="/styles/breviarium.css">
		<script async data-main="/js/gabc-chant.js" src="/js/require.js"></script>
	</head>
	<body>
		<div class='lyric-font' style='font-size: 1px; visibility: hidden;' >I<span class='b'>I<span class='i'>I</span></span><span class='i'>I</span><span style="font-family:'Exsurge Characters';">V. R.</span></div>
		<div id='content-wrapper'>
			{{!office}}
		</div>
	</body>
</html>
