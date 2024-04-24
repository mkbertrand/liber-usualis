<div class='element-wrapper'>
	% if defined(rubric):
		<div class='rubric'>{{rubric}}</div>
	% end
	<div class='chant-wrapper'>
		<gabc-chant>{{gabc}}</gabc-chant> 
	</div>
	% if defined(translation):
		<div class='translation'>{{translation}}</div>
	% end
</div>
