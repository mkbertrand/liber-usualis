<div class='decorated-wrapper'>
	<div class='decoration-left-wrapper'>

	</div>
	<div class='decorated-content-wrapper'>
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
</div>
