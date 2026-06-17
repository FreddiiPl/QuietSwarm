from QuietSwarm.Classes.Pattern import Pattern
import numpy as np
from scipy.special import j1



def realisticQuadApertureWithPhaseError(theta, phi, wl, a):
    # k-vektor
    k_w = 2 * np.pi / wl
    x = k_w * a * np.sin(theta) + 1e-12
    
    # 1. Grundläggande Airy-disk (som din tidigare kod)
    airy = (2 * j1(x) / x)
    
    # 2. Introducera en azimuthal asymmetri (4-faldig symmetri, som en kvadratisk apertur)
    # Detta gör att strålen får "vingar" eller sidolober i ett kors (+ form)
    quad_modulation = 1.0 + 0.5 * np.cos(4 * phi)
    
    # 3. Introducera ett progressivt fasfel (t.ex. från en skev eller termiskt deformerad parabol)
    # Ju längre ut i vinkel (theta), desto mer fasförskjutning uppstår
    phase_error = 2.0 * (theta**2) * np.sin(4 * phi)
    
    # Kombinera till ett komplext fält
    complex_pattern = airy * quad_modulation * np.exp(1j * phase_error)
    
    # Omvandla till dB-skala och lägg till offset för plottning (precis som i din main)
    pattern_dB = 20 * np.log10(np.maximum(np.abs(complex_pattern), 1e-2))
    pattern_dB = pattern_dB - np.max(pattern_dB)
    plot_radius = pattern_dB + 40
    
    return plot_radius



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



def idealDipole(theta, phi):
    eps = 1e-12
    sin_theta = np.sin(theta) + eps
    
    numerator = np.cos((np.pi / 2) * np.cos(theta))
    pattern   = numerator / sin_theta
    
    pattern   = np.where((theta == 0) | (theta == np.pi), 0.0, pattern)
    
    return pattern


def idealGaussian(theta, phi, k, wl, a):
    theta_3dB = k * (wl / a)
    gaussian = np.exp(-0.5 * (theta**2) / theta_3dB**2)
    return gaussian


def main():
    res   = 500
    a     = 0.3 # m
    nu    = 13.25e9 # Hz
    c     = 2.998e8 # m/s
    wl    = c / nu # m
    above_l = 10
    
    rad = Pattern(res=res, a=a, wl=wl, above_l=above_l)
    
    theta, phi, pattern = rad.pattern(realisticQuadApertureWithPhaseError, wl=wl, a=a)
    # theta, phi, pattern = rad.pattern(idealGaussian, k=1, wl=wl, a=a)
    
    total_ideal_energy = np.sum(np.abs(rad.pattern_ideal)**2)
    residual_energy = np.sum(np.abs(pattern.real - rad.pattern_ideal)**2)
    error_percentage = (residual_energy / total_ideal_energy) * 100

    print(f"Med above_l={above_l} (l_max={rad.l_max}) är det totala rekonstruktionsfelet: {error_percentage:.2f}%")
    
    rad.plot_polar(theta, phi, pattern.real, cmap='viridis', levels=50)
    rad.plot_3d(theta, phi, pattern, title="3D Pattern", cmap='viridis')
    



if __name__ == "__main__":
    main()
    