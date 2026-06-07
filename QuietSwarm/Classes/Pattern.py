import numpy as np
import scipy.special as sp
from tqdm import tqdm

import matplotlib.pyplot as plt
import matplotlib as mpl

# Default figure settings
mpl.rcParams['axes.linewidth'] = 1.2
mpl.rcParams['xtick.direction'] = "in"
mpl.rcParams['xtick.top'] = True
mpl.rcParams['ytick.direction'] = "in"
mpl.rcParams['ytick.right'] = True
mpl.rcParams['xtick.minor.visible'] = True
mpl.rcParams['ytick.minor.visible'] = True
mpl.rcParams['font.weight'] = "bold"
mpl.rcParams['axes.labelweight'] = "bold"
mpl.rcParams['font.size'] = 12

class Pattern:
    
    def __init__(self,
                 res,
                 wl,
                 a,
                 ):
        self.res  = res
        
        x, self.weights = sp.roots_legendre(self.res)
        self.theta      = np.arccos(x)
        self.phi        = np.linspace(0, 2 * np.pi, self.res)
        
        self.l     = np.arange(2 * np.pi * a / wl, dtype = int)
        self.l_max = self.l[-1]
        self.m          = np.arange(-self.l_max, self.l_max + 1)
        
        self.mode_weights  = np.zeros((len(self.l), 2 * self.l_max + 1), dtype = complex)
        
        print(f"Initialized Pattern with l_max={self.l_max}, total modes={len(self.l) * (2 * self.l_max + 1)}")
        self.P_lm          = self._precompute_legendre(x)
        print("Precomputed Legendre polynomials up to l_max.")
        
    
    def _get_mesh(self,):
        THETA, PHI = np.meshgrid(self.theta, self.phi, indexing='ij')
        
        return THETA, PHI

    
    def _precompute_legendre(self, x):
        """Precomputes regularized associated Legendre polynomials using standard recurrence."""
        P = np.zeros((self.l_max + 1, self.l_max + 1, self.res))
        
        # P_00
        P[0, 0] = 1.0 / np.sqrt(4 * np.pi)
        if self.l_max == 0: return P
        
        # P_10 and P_11
        P[1, 0] = x * np.sqrt(3 / (4 * np.pi))
        P[1, 1] = -np.sqrt(1 - x**2) * np.sqrt(3 / (8 * np.pi))
        
        # Standard stable stable recurrence relation over l and m
        for m in tqdm(range(self.l_max + 1), total=self.l_max + 1, ncols=100, desc="Precomputing P_lm"):
            if m > 1:
                # Compute the m==l baseline diagonal edge
                P[m, m] = -np.sqrt((2 * m + 1) / (2 * m)) * np.sqrt(1 - x**2) * P[m-1, m-1]
            
            # Compute the off-diagonal items (l > m)
            for l in range(m + 1, self.l_max + 1):
                if l == m + 1:
                    P[l, m] = x * np.sqrt(2 * l + 1) * P[l-1, m]
                else:
                    c1 = np.sqrt((4 * l**2 - 1) / (l**2 - m**2))
                    c2 = np.sqrt(((l - 1)**2 - m**2) / (4 * (l - 1)**2 - 1))
                    P[l, m] = c1 * (x * P[l-1, m] - c2 * P[l-2, m])
        return P
    
    
    def _compute_spherical_harmonics(self, l, m_modes):
        
        sph_harm = np.zeros((len(m_modes), self.res))
        
        for i, m in enumerate(m_modes):
                abs_m = abs(m)
                # Fetch precomputed value
                val = self.P_lm[l, abs_m]
                # Apply Condon-Shortley phase for negative orders
                if m < 0:
                    val = ((-1)**abs_m) * val
                sph_harm[i, :] = val
        
        
        return sph_harm
    
    
    def _compute_weights(self, sph_harm, l_idx, m_col_idx):
        integrand = self.F_theta[m_col_idx, :] * np.conj(sph_harm)
        weights = np.sum(self.weights[None, :] * integrand, axis=1)
        
        self.mode_weights[l_idx, m_col_idx] = weights
        
        return self.mode_weights[l_idx, m_col_idx]
    
    
    
    def _get_phi_dependency(self, TH, PH, idealPattern, **patternKwargs):
        d_phi      = np.max(self.phi) / self.res
        pattern_ideal = idealPattern(TH, PH, **patternKwargs)
        
        F_theta = np.fft.fft(pattern_ideal, axis=1) * d_phi
        freqs   = np.fft.fftfreq(self.res, d=1/self.res).astype(int)
        m_mapping = {f: idx for idx, f in enumerate(freqs) if -self.l_max <= f <= self.l_max}     
        
        F_theta_mapped = np.zeros((len(self.m), self.res), dtype=complex)
        for f, col in m_mapping.items():
            m_idx = f + self.l_max
            F_theta_mapped[m_idx, :] = F_theta[:, col]
            
        return F_theta_mapped
    
        
    
    def pattern(self, idealPattern, **patternKwargs):
        TH, PH        = self._get_mesh()
        self.F_theta  = self._get_phi_dependency(TH, PH, idealPattern, **patternKwargs)
        
        
        self.total_pattern = np.zeros((self.res, self.res), dtype = complex)

        for (l_idx, l) in tqdm(enumerate(self.l), total=len(self.l), ncols=100):
            m_modes   = np.arange(-l, l + 1)
            m_col_idx = m_modes + self.l_max
            
            sph_harm   = self._compute_spherical_harmonics(l, m_modes)
                
            integrand = self.F_theta[m_col_idx, :] * sph_harm
            weights = np.sum(self.weights[None, :] * integrand, axis=1)
            self.mode_weights[l_idx, m_col_idx] = weights

            valid = np.abs(weights) > 1e-6
            if not np.any(valid):
                continue
            
            m_valid = m_modes[valid]
            w_valid = weights[valid]
            sph_harm_valid = sph_harm[valid, :]

            
            theta_part = w_valid[:, None] * sph_harm_valid
            phi_part = np.exp(1j * m_valid[:, None] * self.phi[None, :])
            
            
            self.total_pattern += np.sum(theta_part * phi_part, axis=0)

        
        return (TH, PH, self.total_pattern.T)
    
    
    
    def plot_polar(self, TH, PH, pattern, title="Pattern", **kwargs):
        fig, ax = plt.subplots(subplot_kw={'projection': 'polar'})
        ax.set_title(title, fontweight="bold")
        
        
        sc = ax.contourf(PH, np.rad2deg(TH), pattern.real, **kwargs)
        fig.colorbar(sc,ax=ax, label="Normalized Gain")
        plt.tight_layout()
        plt.savefig(f"{title.replace(' ', '_').lower()}.png", dpi=300)
        
        
    def plot_cartesian(self, TH, PH, pattern, title="Pattern", **kwargs):
        fig, ax = plt.subplots()
        ax.set_title(title, fontweight="bold")
        
        sc = ax.pcolormesh(np.rad2deg(TH), np.rad2deg(PH), pattern.real, **kwargs)
        fig.colorbar(sc, ax=ax, label="Normalized Gain")
        plt.tight_layout()
        plt.savefig(f"{title.replace(' ', '_').lower()}.png", dpi=300)
    
    
    def plot_3d(self, TH, PH, pattern, title="Pattern", **kwargs):
        fig, ax = plt.subplots(subplot_kw={'projection': '3d'}, figsize=(12, 8))
        ax.set_title(title, fontweight="bold")
        
        x = pattern.real * np.sin(TH) * np.cos(PH)
        y = pattern.real * np.sin(TH) * np.sin(PH)
        z = pattern.real * np.cos(TH)
        
        sc = ax.plot_surface(x, y, z, **kwargs)
        ax.set_aspect('equal', adjustable='box') 
        fig.colorbar(sc, ax=ax, label="Normalized Gain")
        plt.tight_layout()
        plt.savefig(f"{title.replace(' ', '_').lower()}.png", dpi=300)
        