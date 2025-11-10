import librosa
import numpy as np
import scipy.signal as sps
import sounddevice as sd


def beat_detect(audio_path, threshold=0.35, lowpass=260, min_gap=0.09, scale=1016):

    # Load audio
    y, sr = librosa.load(audio_path, mono=True)
    y = librosa.util.normalize(y)

    # 1) Percussive extraction (stronger kick isolation)
    y_harm, y_perc = librosa.effects.hpss(y, margin=(1.0, 5.0))

    # 2) Band-Pass filter (keeps kick body + attack)
    lowcut = 50                      # kick thump lower bound
    highcut = lowpass                # slider controls upper bound
    b, a = sps.butter(4, [lowcut/(sr/2), highcut/(sr/2)], btype='band')
    y_kick = sps.filtfilt(b, a, y_perc)

    # 3) Enhance transient edges (makes kick spikes sharp)
    y_kick = librosa.effects.preemphasis(y_kick, coef=0.85)

    # 4) Get onset strength envelope
    hop = 256
    onset_env = librosa.onset.onset_strength(y=y_kick, sr=sr, hop_length=hop)

    # 5) Peak detection based on threshold
    # Only keep peaks above threshold * max peak height
    height_value= height=threshold * np.max(onset_env)
    peak_indices, _ = sps.find_peaks(onset_env,height_value,prominence=0.05)
    print("Strongest beat is at",height_value)

    # Convert frame indices -> time in seconds
    raw_times = librosa.frames_to_time(peak_indices, sr=sr, hop_length=hop)

    # 6) Remove double-hits using min_gap (seconds)
    times_sec = []
    for t in raw_times:
        if not times_sec or (t - times_sec[-1] > min_gap):
            times_sec.append(t)

    # 7) Convert to Alight Motion units
    times_am = [round(t * scale) for t in times_sec]
    print(f"[DETECTED] Beats found: {len(times_sec)}")


    return times_am, times_sec

def preview_with_clicks(audio_path, times_sec, speed=1.0):
    y, sr = librosa.load(audio_path, mono=True)

    # Make a short click sound (1ms spike)
    click = np.zeros(int(sr * 0.01))
    click[0] = 1.0  # sharp transient click

    # Copy audio to overlay clicks
    y_click = np.copy(y)

    # Add click at each detected beat
    for t in times_sec:
        idx = int(t * sr)
        if idx < len(y_click):
            y_click[idx:idx+len(click)] += click

    # ✅ Correct playback speed handling
    if speed != 1.0:
        new_length = int(len(y_click) / speed)  
        y_click = np.interp(
            np.linspace(0, len(y_click), new_length),
            np.arange(len(y_click)),
            y_click
        )

    sd.play(y_click, sr)
    sd.wait()

def debug_visualize(audio_path, times_sec, y=None, sr=None, y_kick=None):
    import librosa, librosa.display, matplotlib.pyplot as plt, numpy as np

    if y is None or sr is None:
        y, sr = librosa.load(audio_path, mono=True)

    # If filtered kick signal not provided, regenerate quickly:
    if y_kick is None:
        _, y_perc = librosa.effects.hpss(y)
        b, a = sps.butter(3, 250 / (sr / 2), btype='lowpass')
        y_kick = sps.filtfilt(b, a, y_perc)

    fig, ax = plt.subplots(3, 1, figsize=(14, 8), sharex=True)

    # 1) Full waveform
    librosa.display.waveshow(y, sr=sr, ax=ax[0], alpha=0.6)
    ax[0].set_title("Full Waveform")
    ax[0].vlines(times_sec, -1, 1, color='red', linewidth=1.2)

    # 2) Kick-isolated waveform
    librosa.display.waveshow(y_kick, sr=sr, ax=ax[1], alpha=0.8, color='orange')
    ax[1].set_title("Kick-Filtered Signal (used for beat detection)")
    ax[1].vlines(times_sec, -1, 1, color='red', linewidth=1.2)

    # 3) Onset envelope (peak energy changes)
    onset_env = librosa.onset.onset_strength(y=y_kick, sr=sr)
    frames = librosa.frames_to_time(np.arange(len(onset_env)), sr=sr)
    ax[2].plot(frames, onset_env, color='purple')
    ax[2].set_title("Onset Strength Envelope")
    ax[2].vlines(times_sec, min(onset_env), max(onset_env), color='red', linewidth=1.2)

    plt.xlabel("Time (seconds)")
    plt.show()

    
beats_am, beats_sec = beat_detect("Backend/Resource/crank.mp3", 0.5, 250, 0.085)


debug_visualize("Backend/Resource/crank.mp3", beats_sec)






