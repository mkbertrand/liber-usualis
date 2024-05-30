<div class='element-wrapper'>
	% if defined('rubric'):
		<div class='rubric'>{{rubric}}</div>
	% end
	<div class='element-text-content-latin'>
		{{!content}}
	</div>
	% if defined('translation'):
		<div class='element-text-content-translation'>{{!translation}}</div>
	% end
</div>
