import librosa
import numpy as np
import scipy.signal as sps

class Beatdetector:
    def __init__(self, threshold=0.5, lowpass=200, min_gap=0.08, scale=1016):
        self.threshold = threshold
        self.lowpass = lowpass
        self.min_gap = min_gap
        self.scale = scale

    def detect(self, audio_path):
        # Load audio
        y, sr = librosa.load(audio_path, mono=True)
        y = librosa.util.normalize(y)

        # 1) Percussive extraction
        y_harm, y_perc = librosa.effects.hpss(y, margin=(1.0, 5.0))

        # 2) Band-pass filter
        lowcut = 50
        highcut = self.lowpass
        b, a = sps.butter(4, [lowcut/(sr/2), highcut/(sr/2)], btype='band')
        y_kick = sps.filtfilt(b, a, y_perc)

        # 3) Enhance transient edges
        y_kick = librosa.effects.preemphasis(y_kick, coef=0.85)

        # 4) Onset strength envelope
        hop = 256
        onset_env = librosa.onset.onset_strength(y=y_kick, sr=sr, hop_length=hop)

        # 5) Peak detection
        height_value = self.threshold * np.max(onset_env)
        peak_indices, _ = sps.find_peaks(onset_env, height_value, prominence=0.05)

        print("Strongest beat threshold =", height_value)

        # Frame → seconds
        raw_times = librosa.frames_to_time(peak_indices, sr=sr, hop_length=hop)

        # 6) Remove double hits
        times_sec = []
        for t in raw_times:
            if not times_sec or (t - times_sec[-1] > self.min_gap):
                times_sec.append(t)

        # 7) Convert to AM units
        times_am = [round(t * self.scale) for t in times_sec]

        print(f"[DETECTED] Beats found: {len(times_sec)}")

        return times_am, times_sec
