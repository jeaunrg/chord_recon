from src import core, plot
import matplotlib.pyplot as plt
import queue
import sounddevice as sd
from matplotlib.animation import FuncAnimation
import numpy as np


VOLUME = 0.3
INTERVAL = 30
DOWNSAMPLE = 1
SAMPLERATE = 44100
WINDOW = 200
CHORD_SIZE = 1
SKIP_PITCH = False
rm_duplicate = False

# -------------------------------- INITIALIZE ---------------------------------#
NOTES = []

q = queue.Queue()
q2 = queue.Queue()


window_length = int(WINDOW * SAMPLERATE / (1000 * DOWNSAMPLE))
signal = np.zeros((window_length))
frequencies, intensities = core.apply_fft(signal)

fig = plt.figure()
ax1 = plot.plot_signal(signal, fig.add_subplot(311))
ax2 = plot.plot_fft(frequencies, intensities, fig.add_subplot(312))
piano = plot.Piano(fig.add_subplot(313))
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
        NOTES.append(chord[0])
        if len(NOTES) > 5:
            NOTES = NOTES[1:]
        if len(np.unique(NOTES)) == 1:
            piano.highlight(NOTES[0])
        ax2._children[0].set_ydata(intensities)

    return [ax1._children[0], ax2._children[0], piano.highlighter] + list(piano.keys.values())


stream = sd.Stream(channels=1, callback=record_callback)
anim = FuncAnimation(fig, update_record, interval=INTERVAL, blit=True)
with stream:
    plt.show()
