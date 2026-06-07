from QuietSwarm.Classes.Pattern import Pattern
import numpy as np
from scipy.special import j1

def physicalCircularAperture(theta, phi, wl, a):
    # k_wavenumber = 2 * pi / wavelength
    k_w = 2 * np.pi / wl
    x = k_w * a * np.sin(theta) + 1e-12 # avoid division by zero
    
    # Standard Airy disk pattern formula for intensity/gain
    pattern = (2 * j1(x) / x)
    
    pattern_dB = 20 * np.log10(np.maximum(pattern, 1e-2)) 
    pattern_dB = pattern_dB - np.max(pattern_dB)
    plot_radius = pattern_dB + 40
    
    return plot_radius

def idealGaussian(theta, phi, k, wl, a):
    theta_3dB = k * (wl / a)
    gaussian = np.exp(-0.5 * (theta**2) / theta_3dB**2)
    return gaussian


def idealDipole(theta, phi):
    eps = 1e-12
    sin_theta = np.sin(theta) + eps
    
    numerator = np.cos((np.pi / 2) * np.cos(theta))
    pattern   = numerator / sin_theta
    
    pattern   = np.where((theta == 0) | (theta == np.pi), 0.0, pattern)
    
    return pattern


def main():
    res   = 500
    a     = 0.05 # m
    nu    = 8e9 # Hz
    c     = 2.998e8 # m/s
    wl    = c / nu # m

    
    rad = Pattern(res=res, a=a, wl=wl)
    
    theta, phi, pattern = rad.pattern(physicalCircularAperture, wl=wl, a=a)
    # theta, phi, pattern = rad.pattern(idealDipole)
    
    rad.plot_polar(theta, phi, pattern, title="Polar Pattern", cmap='viridis', levels=50)
    # rad.plot_cartesian(theta, phi, pattern, title="Cartesian Pattern", shading='auto', cmap='viridis')
    rad.plot_3d(theta, phi, pattern, title="3D Pattern", cmap='viridis')
    



if __name__ == "__main__":
    main()
    