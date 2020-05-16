import numpy as np
from scipy import signal
# from scipy.fft import fftshift
import matplotlib.pyplot as plt

# fs = 10e3
# # N = 1e5
# N = 8192
# amp = 2 * np.sqrt(2)
# noise_power = 0.01 * fs / 2
# time = np.arange(N) / float(fs)
# mod = 500*np.cos(2*np.pi*0.25*time)
# carrier = amp * np.sin(2*np.pi*3e3*time + mod)
# noise = np.random.normal(scale=np.sqrt(noise_power), size=time.shape)
# noise *= np.exp(-time/5)
# x = carrier + noise
x = np.loadtxt("freefall_2.txt")
print(x.shape)

seg = 2**8
fs = 800000
f, t, Sxx = signal.spectrogram(x, fs, nperseg=seg, noverlap=(seg-1))
# f, t, Sxx = signal.spectrogram(x, fs)
print(x.shape)
print(f.shape)
print(t.shape)
print(Sxx.shape)
print(seg, len(t)*len(f))
# np.savetxt("array.txt", Sxx * 1e9, delimiter="\t")
plt.pcolormesh(t, f, Sxx)
plt.ylabel('Frequency [Hz]')
plt.xlabel('Time [sec]')
plt.show()
