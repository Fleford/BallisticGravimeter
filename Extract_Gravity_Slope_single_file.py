import os
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

# x = np.loadtxt("freefall_4.txt")
# x = np.loadtxt("Captures_null/10.txt")
# x = np.loadtxt("Captures_5_18_2020/26.txt")
# x = np.loadtxt("Captures_rapidfire/72.txt")
# x = np.loadtxt("Captures_null_seismic/10.txt")

# Prepare an array of peak spacing
peak_spacing_array = []

all_captures = np.loadtxt('Capture.txt', delimiter=',')

for x in all_captures:
    print(x)

    # x = signal.resample(x, len(x) * 2**0)
    # print(x.shape)

    seg = 2**8
    fs = 1000000
    f, t, ft_array = signal.spectrogram(x, fs, nperseg=seg, noverlap=(seg-1))
    # f, t, Sxx = signal.spectrogram(x, fs)
    print(x.shape)
    print(f.shape)
    print(t.shape)
    print(ft_array.shape)
    print(seg, len(t)*len(f))
    # np.savetxt("array.txt", ft_array * 1e9, delimiter="\t")
    # plt.pcolormesh(t, f, ft_array)
    # plt.ylabel('Frequency [Hz]')
    # plt.xlabel('Time [sec]')
    # plt.show()
    print()

    # Transform initial array
    print("Median:", np.median(ft_array))
    ft_array = ft_array / np.median(ft_array)
    ft_array = ft_array**1

    # Prepare a list of peak spacing
    peak_spacing_list = []

    # # For each slice of the spectrogram,
    for freq_indx, ft_array_slice in enumerate(ft_array):
        # ft_array_slice = ft_array[30]
        # ft_array_slice = np.array([0, 0, 1, 2, 3, 4, 5, 4, 3, 2, 1, 2, 3, 4, 5, 6, 5, 4, 3, 2, 1])

        # # Take a slice
        # plt.plot(ft_array_slice)
        # plt.show()
        # plt.pause(0.1)

        index_array = np.arange(len(ft_array_slice))
        # print(index_array)
        # print(ft_array_slice)

        # Calculate center
        ft_index_array = ft_array_slice * index_array
        center = np.sum(ft_index_array) / np.sum(ft_array_slice)
        print("Center:", center)

        # Calculate width
        index_center_offset_array_sqrd = (index_array - center)**2
        ft_index_mean_offset_array = ft_array_slice * index_center_offset_array_sqrd
        width = np.sqrt(np.sum(ft_index_mean_offset_array) / np.sum(ft_array_slice)) * 2
        print("Width:", width)

        # Cut array into two halves
        print()
        dividing_index = np.int(center)
        print("Dividing index: ", np.int(center))
        first_half = ft_array_slice[:dividing_index]
        print("first half: ", first_half)
        print("max index", np.argmax(first_half))
        print("max val", first_half[np.argmax(first_half)])
        second_half = ft_array_slice[dividing_index:]
        print("second_half: ", second_half)
        print("max index", np.argmax(second_half))
        print("max val", second_half[np.argmax(second_half)])
        peak_spacing = (len(first_half) - np.argmax(first_half)) + (np.argmax(second_half))
        print("peak spacing: ", peak_spacing)

        # Convert peak spacing into freq/time
        peak_spacing = (1/peak_spacing) * fs * f[freq_indx]

        # Append result to a list
        peak_spacing_list.append(peak_spacing)

    # Append peak spacing list to the array
    peak_spacing_array.append(peak_spacing_list)

# Report final result
peak_spacing_array = np.asarray(peak_spacing_array)
mean_peak_spacing_array = np.mean(peak_spacing_array, axis=0)
std_peak_spacing_array = np.std(peak_spacing_array, axis=0)
cov_peak_spacing_array = std_peak_spacing_array / mean_peak_spacing_array
print()
print('peak_spacing_array')
print(peak_spacing_array.shape)
np.savetxt('peak_spacing_array.txt', peak_spacing_array)
np.savetxt('peak_spacing_array_transpose.txt', np.transpose(peak_spacing_array))
np.savetxt('mean_peak_spacing_array_transpose.txt', np.transpose(mean_peak_spacing_array))
np.savetxt('cov_peak_spacing_array_transpose.txt', np.transpose(cov_peak_spacing_array))