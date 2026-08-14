#include "pattern.h"


void FFT(Complex *x, int n) {
    if (n <= 1) {
        return;
    }

    Complex even[n/2];
    Complex odd[n/2];

    for (int i = 0; i < n/2; i++) {
        even[i] = x[2*i];
        odd[i]  = x[2*i + 1];
    }

    fft(even, n/2);
    fft(odd, n/2);

    for (int k = 0; k < n/2; k++) {
        double angle = -2.0 * M_PI * k / n;

        Complex w = {
            cos(angle),
            sin(angle)
        };

        Complex t = mul(w, odd[k]);

        x[k] = add(even[k], t);
        x[k + n/2] = sub(even[k], t);
    }
}


double GaussianLegendreQuadrature(
    double (*f)(double),
    double a,
    double b) {

    const double x1 = -0.5773502691896257;
    const double x2 =  0.5773502691896257;

    const double w1 = 1.0;
    const double w2 = 1.0;

    double c1 = (b - a) * 0.5;
    double c2 = (a + b) * 0.5;

    return c1 * (
        w1 * f(c1 * x1 + c2) +
        w2 * f(c1 * x2 + c2)
    );
}