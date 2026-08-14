#include "pattern.h"

void phiFFT(Complex *Fphi, int Nphi) {
    FFT(Fphi, Nphi);
}


double pattern(double theta, double phi) {
    return exp((theta + phi) / 2);
}


Complex modeWeight(int l, int m, int Ntheta, int Nphi) {
    
    Complex result = (Complex){0.0, 0.0};

    double dtheta = M_PI / Ntheta;
    double dphi   = 2.0 * M_PI / Nphi;

    Complex Fphi[Nphi];

    for (int th = 0; th < Ntheta; th++) {
        double theta = (th + 0.5) * dtheta;

        for (int ph = 0; ph < Nphi; ph++) {
            double phi = ph * dphi;

            double f   = pattern(theta, phi);

            Fphi[ph].real = f;
            Fphi[ph].imag = 0.0;
        }

        phiFFT(Fphi, Nphi);

        Complex Fm = Fphi[m];

        Fm.real /= Nphi;
        Fm.imag /= Nphi;

        double P         = associatedLegendrePolynomial(l, m, cos(theta));
        double sin_theta = sin(theta);
        
        result.real += (Fm.real * P * sin_theta * dtheta);
        result.imag += (Fm.imag * P * sin_theta * dtheta);
    }
    
    return result;
}


