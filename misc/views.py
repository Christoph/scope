from django.shortcuts import render
from curate.tasks import test_task
from django.http import HttpResponse
import json
# Create your views here.


def artsy(request):
	# -{'topic': topic})
	return render(request, 'misc/artsy_rects_upon_suggest.html')


def test_task_view(request):
	test_task("without delay")
	test_task.delay("with delay")
	return HttpResponse(
		json.dumps({"success": "Changes have been saved"}),
				content_type="application/json"
			)
