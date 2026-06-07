import numpy as np
import scipy.special as sp
from tqdm import tqdm


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
        
    
    def _get_mesh(self,):
        THETA, PHI = np.meshgrid(self.theta, self.phi, indexing='ij')
        
        return THETA, PHI

    
    
    def _get_phi_dependency(self, TH, PH, idealPattern, **patternKwargs):
        d_phi      = np.max(self.phi) / self.res
        
        pattern_ideal = idealPattern(TH, PH, **patternKwargs)
        exp_matrix    = np.exp(-1j * self.m[None, :] * self.phi[:, None])
        F_theta       = (pattern_ideal @ exp_matrix) * d_phi
        
        return F_theta.T
    
    
    def generateWeight(self, l, l_idx,
                       m, m_col_idx,):

        sph_harm   = sp.sph_harm_y(l, m[:, None], self.theta[None, :], 0.0)
        integrand = self.F_theta[m_col_idx, :] * np.conj(sph_harm)
        
        self.mode_weights[l_idx, m_col_idx] = np.sum(self.weights[None, :] * integrand, axis=1)
        
        return self.mode_weights[l_idx, m_col_idx], sph_harm
        
        
    
    def pattern(self, idealPattern, **patternKwargs):
        TH, PH        = self._get_mesh()
        self.F_theta  = self._get_phi_dependency(TH, PH, idealPattern, **patternKwargs)
        
        
        total_pattern = np.zeros((self.res, self.res), dtype = complex)

        for (l_idx, l) in tqdm(enumerate(self.l), total=len(self.l), ncols=100):
            m_modes   = np.arange(-l, l + 1)
            m_col_idx = m_modes + self.l_max
            
            weights, sph_harm   = self.generateWeight(l, l_idx, m_modes, m_col_idx)

            valid = np.abs(weights) > 1e-15
            if not np.any(valid):
                continue
            
            m_valid = m_modes[valid]
            w_valid = weights[valid]
            sph_harm_valid = sph_harm[valid, :]
            
            # sph_harm = sp.sph_harm_y(l, m_valid[None, None, :], TH[:, :, None], PH[:, :, None])
            # total_pattern += np.sum(w_valid * sph_harm, axis=2)
            
            theta_part = w_valid[:, None] * sph_harm_valid
            phi_part = np.exp(1j * m_valid[:, None] * self.phi[None, :])
            
            total_pattern += theta_part.T @ phi_part
    
    
    
        return (TH, PH, total_pattern)
    
    
        
        
        