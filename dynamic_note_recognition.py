from src import core, plot
import matplotlib.pyplot as plt
import queue
import sounddevice as sd
from matplotlib.animation import FuncAnimation
import numpy as np


CHORD_SIZE = 3
VOLUME = 1
INTERVAL = 30
DOWNSAMPLE = 1
SAMPLERATE = 44100
WINDOW = 200
SKIP_PITCH = True
rm_duplicate = False

# -------------------------------- INITIALIZE ---------------------------------#
# NOTES = []
NOTES = {}

q = queue.Queue()
q2 = queue.Queue()


window_length = int(WINDOW * SAMPLERATE / (1000 * DOWNSAMPLE))
signal = np.zeros((window_length))
frequencies, intensities = core.apply_fft(signal)

fig = plt.figure()
ax1 = plot.plot_signal(signal, fig.add_subplot(311))
ax2 = plot.plot_fft(frequencies, intensities, fig.add_subplot(312))
ax3 = plot.plot_background(200, 'hsv', fig.add_subplot(325))
piano = plot.Piano(fig.add_subplot(326))
plt.tight_layout()
# ---------------------------------- PROCESS ----------------------------------#
def record_callback(indata, outdata, frames, time, status):
    outdata[:] = indata * VOLUME
    q.put(indata[::DOWNSAMPLE, 0])

def update_record(frame):
    global signal, NOTES
    while True:
        try:
            data = q.get_nowait()
        except queue.Empty:
            break
        shift = len(data)
        signal = np.roll(signal, -shift, axis=0)
        signal[-shift:] = data

    # update plot lines
    ax1._children[0].set_ydata(signal)

    # get fft
    _, intensities = core.apply_fft(signal, SAMPLERATE, rm_duplicate=rm_duplicate)
    if intensities[0] > 1:
        chord = core.find_chord(frequencies, intensities, chord_size=CHORD_SIZE, skip_pitch=SKIP_PITCH)
        cvalues = []
        for i, n in enumerate(chord):
            if n not in NOTES:
                NOTES[n] = 0
            cvalues += [plot.NOTES.index(n)] * (CHORD_SIZE - i)
            NOTES[n] += CHORD_SIZE - i
        piano.highlights(NOTES)

        ax2._children[0].set_ydata(intensities)
        color_value = int(np.round(np.mean(cvalues), 0)) / len(plot.NOTES)
        ax3._children[0].set_data([[color_value]])
    else:
        NOTES = {k: 0 for k in NOTES.keys()}
    return [ax1._children[0], ax2._children[0], ax3._children[0]] + [k.highlighter for k in piano.keys.values()] + list(piano.keys.values())


stream = sd.Stream(channels=1, callback=record_callback)
anim = FuncAnimation(fig, update_record, interval=INTERVAL, blit=True)
with stream:
    plt.show()
