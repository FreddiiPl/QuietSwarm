#include "pattern.h"


double complex sphericalHarmonics(double theta, double phi, int l, int m) {

    double constant       = (2.0*l + 1.0) * tgamma(l - m + 1.0) / (4.0 * M_PI * tgamma(l + m + 1));
    double complex azimuthal_part = exp(I * m * phi);

    double x              = cos(theta);
    double elevation_part = associatedLegendrePolynomial(x, l, m);
    

    return constant * elevation_part * azimuthal_part;
}