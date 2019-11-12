import os
from scipy.io import wavfile
import numpy as npy
import matplotlib.pyplot as plot
import aifc
from scipy import signal
from skimage.feature import peak_local_max
from numpy import fft
import matplotlib.collections as collections
import librosa

from backend import models
from chord_recognition.settings import PCP_IMAGES_ROOT


song_1_ground_truth = [
    ('La# Maj', 0, 2),
    ('Sol Maj', 2, 4),
    ('Re# Maj', 4, 8),
    ('Do Maj', 8, 10),
    ('La Maj', 10, 12),
    ('Mi Maj', 12, 14),
    ('La# Maj', 16, 18),
    ('Sol Maj', 18, 20),
    ('Re# Maj', 20, 24),
    ('Do Maj', 24, 26),
    ('La Maj', 26, 28),
    ('Mi Maj', 28, 30)
]


class PCPExtractor:

    def __init__(self, file, window_size=1024*8, delay=0,
                 plot_results=False, window_function_name='cosine'):
        self.window_size = window_size
        self.window_function_name = window_function_name
        self.reduced_window = int(self.window_size / 2)
        self.delay = delay
        self.fref = 261.63
        self.fs = None
        self.data = None
        self.plot_results = plot_results
        self.file = file
        self.CHORDS = {
            'Do Maj': ['do', 'mi', 'sol'],
            'Do # Maj': ['do#', 'mi#', 'sol#'],
            'Re Maj': ['re', 'fa#', 'la'],
            'Mib Maj': ['mib', 'sol', 'sib'],
            'Mi Maj': ['mi', 'sol#', 'si'],
            'Fa Maj': ['fa', 'la', 'do'],
            'Fa# Maj': ['fa#', 'la#', 'do#'],
            'Sol Maj': ['sol', 'si', 're'],
            'Lab Maj': ['lab', 'do', 'mib'],
            'La Maj': ['la', 'do#', 'mi'],
            'Sib Maj': ['sib', 're', 'fa'],
            'Si Maj': ['si', 're#', 'fa#'],
            'Do Min': ['do', 'mib', 'sol'],
            'Do# Min': ['do#', 'mi', 'sol#'],
            'Re Min': ['re', 'fa', 'la'],
            'Mib Min': ['mib', 'solb', 'sib'],
            'Mi Min': ['mi', 'sol', 'si'],
            'Fa Min': ['fa', 'lab', 'do'],
            'Fa# Min': ['fa#', 'la', 'do#'],
            'Sol Min': ['sol', 'sib', 're'],
            'Lab Min': ['lab', 'b', 'mib'],
            'La Min': ['la', 'do', 'mi'],
            'Sib Min': ['sib', 'reb', 'fa'],
            'Si Min': ['si', 're', 'fa#']
        }

    def get_tempo(self):
        self.read_file()
        y, sr = librosa.load(self.file)
        tempo, beats = librosa.beat.beat_track(y=y, sr=sr)
        tempo = tempo or 20
        return int((60/tempo)*self.fs)

    def apply_delay(self, delay, window_size):
        self.delay = delay
        self.window_size = window_size

    def read_file(self):
        """Sets self.fs and self.data attributes"""
        self.fs, self.data = wavfile.read(self.file)
        self.data = (self.data[:, 0] + self.data[:, 1]) / 2

    def enwindow_data(self):
        """Sets the window_data attribute"""

        windowed_data = self.data[self.delay:self.delay+self.window_size]

        if self.window_function_name == 'cosine':
            window_function = signal.windows.cosine(self.window_size)
        elif self.window_function_name == 'hamming':
            window_function = signal.hamming(self.window_size)
        else:
            # TODO: try with other functions
            raise Exception('To be implemented')
        self.windowed_data = windowed_data * window_function
        if self.plot_results:
            self.plot_data()

    def plot_data(self):
        fig, ax = plot.subplots()
        ax.plot(range(int(npy.size(self.data))), self.data)

        fig, ax = plot.subplots()
        ax.plot(range(self.window_size), self.windowed_data)

    def compute_fft(self):
        self.spectrum = abs(fft.fft(self.windowed_data))
        if self.plot_results:
            self.plot_fft()

    def plot_fft(self):
        fig, ax = plot.subplots()
        ax.plot(range(self.reduced_window), self.spectrum[0:self.reduced_window])

    def filter_fft(self):
        indexes = peak_local_max(self.spectrum, min_distance=5)
        filtered_spectrum = npy.zeros(len(self.spectrum))
        for i in indexes:
            filtered_spectrum[i] = self.spectrum[i]
        self.spectrum = filtered_spectrum
        if self.plot_results:
            self.plot_filtered_fft()

    def plot_filtered_fft(self):
        fig, ax = plot.subplots()
        ax.plot(
            range(self.reduced_window), self.spectrum[0:self.reduced_window]
        )

    def calculate_PCP(self, normalize_values=True):
        mapping = npy.zeros(self.reduced_window).astype(int)
        mapping[0] = -1
        PCP = npy.zeros(12)

        # TODO: AQUI PASSA ALGO RARO, mapping[0] mai es crida per tant
        # lo del -1 es com si no hi sigues
        for x in range(1, self.reduced_window):
            real_f_hz = self.fs * x / self.window_size
            mapping[x] = int(
                npy.mod(round(12 * npy.log2(real_f_hz / self.fref)), 12)
            )
            PCP[mapping[x]] += npy.square(self.spectrum[x])

        if normalize_values:
            PCP = PCP / max(PCP)

        # Convert to dict
        notes = [
            'do', 'do#', 're', 're#', 'mi', 'fa',
            'fa#', 'sol', 'sol#', 'la', 'la#', 'si'
        ]
        self.PCP = dict(zip(notes, PCP))
        if self.plot_results:
            self.plot_PCP()

    def plot_PCP(self):
        fig, ax = plot.subplots()
        plot.bar(self.PCP.keys(), self.PCP.values())

    def extract_chord(self, try_relaxed=True):
        """Extracts the chord from the PCP.

        If try_relaxed=True, it will pick the closest chord if not found
        """

        def get_chord_name(notes_found):
            matching_chord = None
            for chord_name, chord_notes in self.CHORDS.items():
                if sorted(chord_notes) == sorted(notes_found):
                    # If found, returns the chord
                    return chord_name
            return None

        sorted_PCP_dict = sorted(
            self.PCP.items(), key=lambda kv: kv[1], reverse=True
        )
        sorted_notes = [n[0] for n in sorted_PCP_dict]
        matching_chord = get_chord_name(sorted_notes[:3])
        if try_relaxed and not matching_chord:
            # Un approach mes correcte potser es baixant un semito en alguna nota, etc
            # Try picking the 1st, 2nd and 4th notes of the PCP
            #            print('Not found, trying with 4th PCP note')
            notes_found = sorted_notes[:2] + sorted_notes[3:4]
            matching_chord = get_chord_name(notes_found)
        self.notes_found = sorted_notes[:3]
        self.matching_chord = matching_chord
        if self.plot_results:
            self.print_chord_results()

    def print_chord_results(self):
        print('\n' * 2)
        print('-' * 30)
        if self.matching_chord:
            print('The chord found is ', matching_chord)
        else:
            print('No matching chord found')
            print('Notes found: ', ', '.join(self.notes_found))
        print('-' * 30)
        print('\n' * 2)

    def save_plot_wave_with_results(self, results):
        fig, ax = plot.subplots(dpi=200)
        ax.set_title('Data with found chords')
        ax.plot(range(int(npy.size(self.data))), self.data, linewidth=1)

        y_positions = [max(self.data)/2, min(self.data)/2]
        current_y_idx = 0
        x_offset = 0
        for second, chord, is_ok in results:
            coord = second * self.fs
            if is_ok == True:
                plot.axvline(x=coord, color='g')
                bbox={'facecolor': 'green', 'alpha': 0.5, 'pad': 1}
                ax.text(coord + x_offset, 0, chord,
                        rotation='vertical', bbox=bbox, fontsize=7)
            elif is_ok == False:
                plot.axvline(x=coord, color='r')
                bbox={'facecolor': 'red', 'alpha': 0.5, 'pad': 1}
                ax.text(coord + x_offset, 0, chord,
                        rotation='vertical', bbox=bbox, fontsize=7)
            elif is_ok == 'no_ground_truth':
                plot.axvline(x=coord, color='grey')
                bbox={'facecolor': 'grey', 'alpha': 0.5, 'pad': 1}
                ax.text(coord + x_offset, 0, chord,
                        rotation='vertical', bbox=bbox, fontsize=7)

            current_y_idx = (current_y_idx + 1) % 2
        new_pcp = models.PCPFile.objects.create()
        fig.savefig(os.path.join(PCP_IMAGES_ROOT,new_pcp.path), dpi=fig.dpi)
        return new_pcp


    def get_single_chord(self, delay=None, window_size=None):
        if self.data is None or not self.data.any():
            self.read_file()
        self.delay = delay if delay else self.delay
        self.window_size = window_size if window_size else self.window_size
        self.enwindow_data()
        self.compute_fft()
        self.filter_fft()
        self.calculate_PCP()
        self.extract_chord()
        return self.matching_chord


def extract_chords_from_audiofile(file, ground_truth=None):
    pcp_extractor = PCPExtractor(file=file, window_size=1024*5)
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
    if ground_truth:
        results = []
        MARGIN = 0.5
        for second, chord in chords:
            is_ok = False
            for good_chord, sec_from, sec_to in ground_truth:
                if ((second >= (sec_from - MARGIN)) and
                    (second <= (sec_to + MARGIN)) and
                        (chord == good_chord)):
                    is_ok = True
                    break
            if is_ok:
                results.append((second, chord, True))
            else:
                results.append((second, chord, False))
    else:
        results = [c + ('no_ground_truth',) for c in chords]

    return pcp_extractor.save_plot_wave_with_results(results)
