#include <math.h>

#ifndef PROPAGATOR_H
#define PROPAGATOR_H

/* 
Need definition of physical scale for various conversions - IERS Convention
*/
#define mu 3.986004418e14
#define a 6378136
#define T sqrt(a * a * a / mu)

#define sigma_mu 8e5
#define sigma_a 0.1

/*
Julian 2000 reference
*/
#define JULIAN_DATE_J2000 2451545.0
#define SECONDS_PER_DAY 86400.0


/*
Structs
*/

typedef struct {
    double l;
    double l_prime;
    double F;
    double D;
    double Omega;
} Delauney;

typedef struct {
    double L_Me; // Merkurius
    double L_Ve; // Venus
    double L_E;  // Jorden
    double L_Ma; // Mars
    double L_J;  // Jupiter
    double L_Sa; // Saturnus
    double L_U;  // Uranus
    double L_Ne; // Neptunus
    double p_A;  // Allmän precession i longitud
} Planetary;

typedef struct {
    double X, Y;
} CIP;


#define MAX_ROWS_X 1600
#define MAX_ROWS_Y 1275

typedef struct {
    int j;
    double index;
    double val1;
    double val2;
    double c[14];
} CelestialParameters;



/*
function definitions
*/
double currentJulianDateTimeJ2000(const char *UT1);
void CIOLocatorAngle();
CIP CIPCoordinates(double t_JD);

/*
Paths
*/
static const char tab5_2a[] = "IERS/tab5.2a.csv";
static const char tab5_2b[] = "IERS/tab5.2b.csv";



#endif