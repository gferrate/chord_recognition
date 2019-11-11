from django.http import HttpResponse
from django.shortcuts import render
from django.views.generic import View
from .forms import UploadFileForm
from scipy.io import wavfile

from backend.controllers import pcpcontroller
from backend import models


class Home(View):

    def get(self, request):
        form = UploadFileForm()
        return render(request, 'templates/home/index.html', {'form': form})

    def post(self, request):
        form = UploadFileForm(request.POST, request.FILES)
        if form.is_valid():
            pcp_extractor = pcpcontroller.PCPExtractor(
                file=request.FILES['file'],
                window_size=1024*5
            )
            pcp_extractor.read_file()
            delta = pcp_extractor.get_tempo()
            chords = []
            for delay in range(0, pcp_extractor.data.size-delta, delta):
                chord = pcp_extractor.get_single_chord(delay, delta)
                if chord:
                    try:
                        last_chord = chords[-1][1]
                        if last_chord == chord:
                            continue
                    except IndexError:
                        pass
                    second = delay / pcp_extractor.fs
                    chords.append((round(second, 1), chord))
            results = []
            MARGIN = 0.5
            for second, chord in chords:
                is_ok = False
                for good_chord, sec_from, sec_to in pcpcontroller.ground_truth:
                    if ((second >= (sec_from - MARGIN)) and
                        (second <= (sec_to + MARGIN)) and
                            (chord == good_chord)):
                        is_ok = True
                        break
                if is_ok:
                    results.append((second, chord, True))
                else:
                    results.append((second, chord, False))
            new_pcp = pcp_extractor.save_plot_wave_with_results(results)
            return render(request, 'templates/home/view_pcp.html', {'img': new_pcp.path})
