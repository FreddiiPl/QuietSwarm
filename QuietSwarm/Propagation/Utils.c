#include <math.h>
#include "propagator.h"
#include "utils.h"


RotationalMatrix defineRotationalMatrix(double Omega, double omega, double i) {
    double cos_raan = cos(Omega);
    double sin_raan = sin(Omega);
    double cos_aop  = cos(omega);
    double sin_aop  = sin(omega);
    double cos_inc  = cos(i);
    double sin_inc  = sin(i);

    RotationalMatrix R;
    R.RotMatrix[0][0] = cos_raan * cos_aop - sin_raan * cos_inc * sin_aop;
    R.RotMatrix[0][1] = -cos_raan * sin_aop - sin_raan * cos_inc * cos_aop;
    R.RotMatrix[0][2] = sin_raan * sin_inc;

    R.RotMatrix[1][0] = sin_raan * cos_aop + cos_raan * cos_inc * sin_aop;
    R.RotMatrix[1][1] = -sin_raan * sin_aop + cos_raan * cos_inc * cos_aop;
    R.RotMatrix[1][2] = -cos_raan * sin_inc;

    R.RotMatrix[2][0] = sin_inc * sin_aop;
    R.RotMatrix[2][1] = sin_inc * cos_aop;
    R.RotMatrix[2][2] = cos_inc;

    return R;
}


double compute_acceleration(double val, double z, 
                            double r2, int j
                            ) {
                                
    double oblateness_term_normalized = 1.5 * J2;
    
    double r_mag3  = 1.0 / (r2 * sqrt(r2));
    double r_mag5 = 1.0 / (r2 * r2 * sqrt(r2));
    double acceleration;

    if (j == 2) {

        acceleration = - val * r_mag3 + oblateness_term_normalized * r_mag5 * val * (5 * z*z / r2 - 3);
    }
    else {
        acceleration = - val * r_mag3 + oblateness_term_normalized * r_mag5 * val * (5 * z*z / r2 - 1);
    }
    
    return acceleration;
}


double compute_velocity(double val, double acceleration, double h2) {
    return val + h2 * acceleration;
}