import json
import matplotlib.pyplot as plt
import scipy.fftpack
import numpy as np
from scipy.fftpack import fft, dct
#from util import smooth

def wave_ceptrum(numcep, waves, N, sample_rate):
    pow_spec = power_spectrum(waves, n=N)
    
    fb = filterbank(26, N, sample_rate)
    feat = np.dot(pow_spec, fb.T)
    #need energy?

    feat = np.log(feat)
    feat = dct(feat, type=2, axis=-1, norm='ortho')[:numcep]

    return feat

def power_spectrum(waves, n=None):
    if n == None:
        n = waves.shape[-1] 

    mag_spec = np.absolute(np.fft.rfft(waves, n))
    return 1.0 / n * np.square(mag_spec)

def filterbank(filt_num, N, sample_rate=80000, low_freq=0, high_freq=None):
    
    high_freq = high_freq or sample_rate / 2
    assert high_freq <= sample_rate / 2, "highfreq is greater than samplerate / 2"
    
    filt_points = np.linspace(low_freq, high_freq, filt_num + 1)
    bin = np.floor(N * filt_points / sample_rate)

    #rectangular filter
    fbank = np.zeros([filt_num, N // 2 + 1])
    for i in range(filt_num):
        for j in range(int(bin[i]), int(bin[i + 1])):
            fbank[i, j] = 1

    return fbank

def get_wave_feature(waves, sample_rate, N):
    #waves = smooth(waves)
    cep =  wave_ceptrum(26, waves, N, sample_rate)
    features = np.concatenate((cep, np.diff(cep, n=1), np.diff(cep, n=2)), axis=0)
    #features = np.array([])
    #waves = smooth(waves)
    #f = np.abs(fft(waves))
    features = np.append(features, np.mean(waves))
    features = np.append(features, np.std(waves))
    features = np.append(features, np.var(waves))
    features = np.append(features, np.amax(waves))
    features = np.append(features, np.amin(waves))
    features = np.append(features, np.median(waves))
    return features


if __name__ == "__main__":
    N = 2000
    sample_rate = 80000

    T = 1.0 / sample_rate

    x = np.linspace(0, N * T, N)
    #y = np.sin(100.0 * 2.0 * np.pi * x) + 0.5 * np.sin(150 * 2.0 * np.pi * x)
    data = json.load(open('3pin/LM337/data.json', 'r'))
    y = np.array(data[0]['pos1_neg3_test2']['wave'])
    print('start')
    #yf = power_spectrum(y)
    yc = get_wave_feature(y,sample_rate, N)
    print('done')
    print(yc)
    #xf = np.linspace(0, 1.0 / (2.0 * T), N / 2 + 1)

    #plt.plot(xf, yf)
    #plt.show()


