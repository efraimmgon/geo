from django.http import HttpResponse
from django.shortcuts import render, redirect
from .forms import UploadFileForm

from .utils import handle_uploaded_file

def index(request):
	form = UploadFileForm()
	return render(request, 'escala/index.html', {'form': form})

def upload_file(request):
	if request.method == 'POST':
		form = UploadFileForm(request.FILES)
		if form.is_valid():
			handle_uploaded_file(request.FILES['file'])
			return redirect('escala:manager')
		else:
			return render(request, 'escala/index.html', {'form': form})