from django.http import HttpResponse
from django.shortcuts import render, get_object_or_404
from django.views.generic import View
from .forms import UploadFileForm
from scipy.io import wavfile
import os

from backend.controllers import pcpcontroller
from backend import models
from chord_recognition.settings import PCP_PARTAL_PATH
from django.shortcuts import redirect


class Home(View):

    def get(self, request):
        form = UploadFileForm()
        return render(request, 'templates/home/index.html', {'form': form})

    def post(self, request):
        form = UploadFileForm(request.POST, request.FILES)
        if form.is_valid():
            new_pcp = pcpcontroller.extract_chords_from_audiofile(request.FILES['file'])
            return redirect('view_pcp', path=new_pcp.path)
        return render(request, 'templates/home/index.html', {'form': form})


class ViewPCP(View):

    def get(self, request, path):
        pcp = get_object_or_404(models.PCPFile, path=path)
        path = os.path.join(PCP_PARTAL_PATH, pcp.path)
        return render(request, 'templates/home/view_pcp.html', {'img': path})


class ViewPreviousResults(View):

    def get(self, request):
        pcps = models.PCPFile.objects.all().values_list('path', flat=True)
        paths = [os.path.join(PCP_PARTAL_PATH, p) for p in pcps]
        return render(request, 'templates/home/view_pcps.html', {'imgs': paths})
