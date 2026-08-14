#include "pattern.h"


double sectorialLegendre(double x, int m) {
    double polynomial = 1.0;
    if (m > 0) {
        double squareTerm = sqrt( ( 1.0 - x ) * ( 1.0 + x ));
        double oddFactor  = 1.0;

        for (int i = 0; i <=m; i++) {
            polynomial *= -oddFactor * squareTerm;
            oddFactor  += 2.0;
        }
    }


    return polynomial;
}


double tesseralLegendre(double x, int l, int m) {
    return x * (2 * m - 1);
}


double associatedLegendrePolynomial(double x, int l, int m) {
    if (m < 0 || m > l || fabs(x) > 1.0) {
        return 0.0;
    }

    double start = sectorialLegendre(x, m);
    if (l == m) {
        return start;
    }

    double next = tesseralLegendre(x, l, m);
    next *= start;
    if (l == m + 1) {
        return next;
    }

    double final = 0.0;
    for (int current_l = m + 2; current_l <= l; current_l) {
        final = (x * ( 2 * current_l + 1 ) * next - 
                ( current_l + m - 1 )  * start) / (current_l - m);
        

        start = next;
        next  = final;
    }

    return final;
}