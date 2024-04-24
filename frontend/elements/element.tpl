<div class='element-wrapper'>
	% if defined(rubric):
		<div class='rubric'>{{rubric}}</div>
	% end
	<div class='text-wrapper'>
		{{element}}
	</div>
	% if defined(translation):
		<div class='translation'>{{translation}}</div>
	% end
</div>
