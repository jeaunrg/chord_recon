import matplotlib.pyplot as plt
from matplotlib import patches
import numpy as np
plt.style.use('seaborn-dark')


def plot_signal(signal, ax=None):
    if ax is None:
        fig, ax = plt.subplots()
    ax.plot(signal)
    ax.set_xlim(0, len(signal))
    ax.set_ylim(-1, 1)
    ax.set_xlabel('Time')
    ax.set_ylabel('Amplitude')
    ax.set_title('Sound Wave')
    ax.grid()
    return ax

def plot_fft(frequencies, intensities, ax=None):
    if ax is None:
        fig, ax = plt.subplots()
    ax.plot(frequencies, intensities)
    ax.set_xlabel('Frequency (Hz)')
    ax.set_ylabel('Amplitude')
    ax.set_title('Spectrum Recording on Piano')
    ax.set_ylim((0, 3000))
    ax.set_xlim((0, 2000))
    ax.grid()
    return ax


class PianoKey(patches.Rectangle):
    def __init__(self, note):
        self.is_highlighted = False
        self.note = note
        self.is_black = '#' in note or 'b' in note
        if self.is_black:
            w, h, self.zorder, self.color =  0.6, 0.7, 3, 'k'
        else:
            w, h, self.zorder, self.color = 1, 1, 1, 'w'
        patches.Rectangle.__init__(self, (0, 0), w, h, linewidth=0.2, edgecolor='k', zorder=self.zorder, facecolor=self.color)

class Piano:
    def __init__(self, ax, octaves=[3, 4, 5]):
        self.current_note = None

        if ax is None:
            fig, self.ax = plt.subplots()
        else:
            self.ax = ax

        self.octaves = octaves
        notes = ['do', 'do#', 'ré', 'mib', 'mi', 'fa', 'fa#', 'sol', 'lab', 'la', 'sib', 'si']

        values = np.zeros((1, 7 * len(self.octaves)))
        self.ax.imshow(values, aspect='auto')
        self.keys = {}
        x = -1
        for i in self.octaves:
            for n in notes:
                note = f"{n}-{i}"
                key = PianoKey(note)
                if key.is_black:
                    key.set_x(x+0.66)
                else:
                    x += 1
                    key.set_x(x)
                self.ax.add_patch(key)
                self.keys[note] = key
        self.ax.set_xlim(0, 7 * len(self.octaves))
        self.ax.set_ylim(1, 0)

        self.highlighter = patches.Rectangle((0, 0), 1, 1, color='r', zorder=2, linewidth=0)
        self.ax.add_patch(self.highlighter)

        self.ax.set_xticklabels([])
        self.ax.set_yticklabels([])

    def highlight(self, note):
        key = self.get_key(note)
        self.highlighter.set_xy(key.get_xy())
        self.highlighter.set_width(key.get_width())
        self.highlighter.set_height(key.get_height())
        self.highlighter.set(zorder=key.zorder+1)

    def get_key(self, note):
        if note not in self.keys:
            n, num = note.split('-')
            closest_octave_id = np.argmin(np.abs(np.array(self.octaves) - int(num)))
            note = f"{note.split('-')[0]}-{self.octaves[closest_octave_id]}"
        return self.keys[note]
