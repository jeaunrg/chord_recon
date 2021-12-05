import numpy as np
from src import core, plot
import matplotlib.pyplot as plt
import os
dir_path = os.path.dirname(os.path.realpath(__file__))


CHORD_SIZE = 3
SKIP_PITCH = False
# INPUT = 5
INPUT = os.path.join(dir_path, 'data', 'do_sol_real.wav')

# ------------------------------ INITIALIZE -----------------------------------#
if isinstance(INPUT, int):
    # record signal
    duration, sample_rate = INPUT, 44100
    print("start recording...")
    signal = core.record_signal(duration, sample_rate)
    print("stop recording")
else:
    # Load data from wav file
    signal, sample_rate = core.read_sound(INPUT)

signal = signal[:,0]


# ------------------------------ PROCESS --------------------------------------#
# FFT
frequencies, intensities = core.apply_fft(signal, sample_rate)

# find main notes
chord = core.find_chord(frequencies, intensities, chord_size=CHORD_SIZE, skip_pitch=SKIP_PITCH)


# ------------------------------ RESULTS --------------------------------------#
fig = plt.figure()
fig.suptitle(' '.join(chord))

# Plot sound wave
plot.plot_signal(signal, fig.add_subplot(211))

# Plot spectrum
plot.plot_fft(frequencies, intensities, fig.add_subplot(212))

plt.tight_layout()
plt.show()
