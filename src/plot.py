import matplotlib.pyplot as plt
from matplotlib import patches
import numpy as np
plt.style.use('seaborn-dark')

NOTES = ['do', 'do#', 'ré', 'mib', 'mi', 'fa', 'fa#', 'sol', 'lab', 'la', 'sib', 'si']


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
    ax.set_title('Spectrum')
    ax.set_ylim((0, 3000))
    ax.set_xlim((0, 2000))
    ax.grid()
    return ax

def plot_background(value, cmap='hsv', ax=None):
    if ax is None:
        fig, ax = plt.subplots()
    im = ax.imshow([[0.5]], cmap=cmap, aspect='auto', vmin=0, vmax=1)
    # print(im == ax._children[0])
    # im.set_data([[0.3]])
    ax.set_xticklabels([])
    ax.set_yticklabels([])
    return ax

class PianoKey(patches.Rectangle):
    def __init__(self, note):
        self.note = note
        self.is_black = '#' in note or 'b' in note
        if self.is_black:
            w, h, self.zorder, self.color =  0.6, 0.7, 3, 'k'
        else:
            w, h, self.zorder, self.color = 1, 1, 1, 'w'
        patches.Rectangle.__init__(self, (0, 0), w, h, linewidth=0.2, edgecolor='k', zorder=self.zorder, facecolor=self.color)
        self.highlighter = patches.Rectangle((0, 0),  w, h, linewidth=0, zorder=self.zorder+1, facecolor='r', alpha=0)

    def set_x(self, *args, **kwargs):

        self.highlighter.set_x(*args, **kwargs)
        return patches.Rectangle.set_x(self, *args, **kwargs)

    def highlight(self, boolean=True, intensity=1):
        if boolean == False:
            self.highlighter.set(alpha=0)
        else:
            self.highlighter.set(alpha=intensity)


class Piano:
    def __init__(self, ax, octaves=[1]):
        self.highlighted = []

        if ax is None:
            fig, self.ax = plt.subplots()
        else:
            self.ax = ax

        self.octaves = octaves
        notes = NOTES

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
                self.ax.add_patch(key.highlighter)
                self.keys[note] = key
        self.ax.set_xlim(0, 7 * len(self.octaves))
        self.ax.set_ylim(1, 0)

        self.highlighter = patches.Rectangle((0, 0), 1, 1, color='r', zorder=2, linewidth=0, alpha=0)
        self.ax.add_patch(self.highlighter)

        self.ax.set_xticklabels([])
        self.ax.set_yticklabels([])

    def highlight(self, note, intensity=1):
        key = self.get_key(note)
        key.highlight(intensity=intensity)
        self.highlighted.append(key)

    def reset_highlighted(self):
        for key in self.highlighted:
            key.highlight(False)
        self.highlighted = []

    def highlights(self, notes_intensities):
        max_int = max(notes_intensities.values())
        if max_int > 20:
            self.reset_highlighted()
            for note, intensity in notes_intensities.items():
                if intensity > 0.5 * max_int:
                    self.highlight(note, intensity / max_int)

    def get_key(self, note):
        if note not in self.keys:
            if '-' not in note:
                n, num = note, '1'
            else:
                n, num = note.split('-')
            closest_octave_id = np.argmin(np.abs(np.array(self.octaves) - int(num)))
            note = f"{n}-{self.octaves[closest_octave_id]}"
        return self.keys[note]
