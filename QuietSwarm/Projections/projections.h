#include <math.h>

#ifndef PROPAGATOR_H
#define PROPAGATOR_H


/* 
Need definition of physical scale for various conversions
*/
#define mu 3.986004418e14
#define a 6378136
#define T sqrt(a * a * a / mu)

#define sigma_mu 8e5
#define sigma_a 0.1

/*
Julian 2000 reference
*/
#define J2000 2451545.0
#define SECONDS_PER_DAY 86400.0


/*
function definitions
*/
double currentJulianDateTimeJ2000(const char *UT1);
void CIOLocatorAngle();
void CIPCoordinates();



#endif