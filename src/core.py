import numpy as np
import sounddevice as sd
import soundfile as sf
import pandas as pd
import os
dir_path = os.path.dirname(os.path.realpath(__file__))
note_frequencies = pd.read_csv(os.path.join(dir_path, '..', 'data', 'note_frequencies.csv'),
                               sep=';', header=None, encoding='latin-1', index_col=0)

def write_sound(sample, filename, fs=44100):
    sf.write(filename, sample, fs)

def read_sound(filename):
    data, fs = sf.read(filename, always_2d=True)
    return data, fs

def record_signal(duration=5, fs=44100):
    y = sd.rec(int(duration * fs), samplerate=fs, channels=1)
    sd.wait()
    return y

def play_signal(y, fs):
    sd.play(y, fs)

def find_true_note(frequence):
    diff = (note_frequencies - frequence).abs()
    idx = np.where(diff.values == diff.values.min())
    note = note_frequencies.index[idx[0][0]]
    pitch = note_frequencies.columns[idx[1][0]]
    return note, pitch

def find_chord(frequencies, intensities, chord_size=3, skip_pitch=False):
    base_freq_ids = np.argsort(-intensities)
    frequencies = np.abs(frequencies[base_freq_ids])
    chord = []
    for f in frequencies:
        note, pitch = find_true_note(f)
        if not skip_pitch:
            note += '-' + str(pitch)

        if note not in chord:
            chord.append(note)
            if len(chord) == chord_size:
                break
    return chord

def apply_fft(signal, sample_rate=44100, rm_duplicate=False, skip_freqs=False):
    t = np.arange(signal.shape[0])
    frequencies = np.fft.fftfreq(t.shape[-1]) * sample_rate
    intensities = abs(np.fft.fft(signal).real)

    # remove duplicated negative data
    if rm_duplicate:
        positiv_freq_indexes = frequencies > 0
        frequencies = frequencies[positiv_freq_indexes]
        intensities = intensities[positiv_freq_indexes]
    return frequencies, intensities
