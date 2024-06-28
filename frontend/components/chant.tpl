<div class='element-wrapper'>
	% if defined('rubric'):
		<div class='rubric'>{{rubric}}</div>
	% end
	<div class='chant-wrapper'>
		<gabc-chant src="/chant/{{src}}/{{tags}}"></gabc-chant> 
	</div>
	% if defined('translation'):
		<div class='chant-content-translation'>{{!translation}}</div>
	% end
</div>
