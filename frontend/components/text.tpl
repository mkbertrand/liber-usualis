<div class='text-wrapper'>
	% if defined('rubric'):
		<div class='rubric'>{{rubric}}</div>
	% end
	<div class='text-content-latin'>
		{{!content}}
	</div>
	% if defined('translation'):
		<div class='text-content-translation'>{{!translation}}</div>
	% end
</div>
