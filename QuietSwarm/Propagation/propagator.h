#ifndef PROPAGATOR_H
#define PROPAGATOR_H


/*
For general numerical application and stability
*/
#define epsilon 1.0e-12
#define epsilon2 (epsilon * epsilon)

/*
Constants definition - unitless versions based on IERS Convention (2010):
https://iers-conventions.obspm.fr/conventions_material.php
*/
#define mu 1.0
#define a 1.0
#define J2 0.0010826359

#define sigma_mu 2.0070223615090836e-9
#define sigma_a 1.5678560412142945e-8
#define sigma_J2 1.0e-10


/*
Global structs
*/
typedef struct {
    double x, y, z;
} Vector3 ;

typedef struct {
    double rightAscensionOfAscendingNode;
    double argumentOfPerigee;
    double inlinationAngle;
    double phaseAngles;
    double semiMajorAxis;
    double eccentricity;
} OrbitalParameters;

typedef struct {
    Vector3 positions;
    Vector3 velocities;
    Vector3 accelerations;
} State;


typedef struct {
    int n_sats;
    OrbitalParameters *orbitParam; // be sure to free once its use is over
    State *state; // be sure to free once its use is over
} Swarm;


/*
Initialize
*/
State initialize_state(OrbitalParameters orbit);


/*
Integrator - kick-drift Verlet integration
*/


State verlet_kick_drift_single_sat(State current_state, double h);

void swarm_step(Swarm *swarm, double h);

#endif