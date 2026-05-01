#include <math.h>
#include "propagator.h"
#include "utils.h"


State initialize_state(OrbitalParameters orbit) {
    
    double rightAscensionOfAscendingNode = orbit.rightAscensionOfAscendingNode;
    double argumentOfPerigee             = orbit.argumentOfPerigee;
    double inlinationAngle               = orbit.inlinationAngle;
    double phaseAngles                   = orbit.phaseAngles;
    double semiMajorAxis                 = orbit.semiMajorAxis;
    double eccentricity                  = orbit.eccentricity;


    Vector3 initialPos;
    Vector3 initialVel;
    Vector3 initialAcc;
    
    double e2          = eccentricity * eccentricity;
    double r0          = (semiMajorAxis * ( 1 - e2) ) / ( 1 + eccentricity * cos(phaseAngles) );
    double v0          = sqrt(1.0 / semiMajorAxis * ( 1 - e2 ) );
    
    initialPos.x = r0 * cos(phaseAngles);
    initialPos.y = r0 * sin(phaseAngles);
    initialPos.z = 0;
    
    initialVel.x = -v0 * sin(phaseAngles);
    initialVel.y = v0 * (eccentricity  + cos(orbit.phaseAngles));
    initialVel.z = 0;
    
    double r0_squared = initialPos.x * initialPos.x + initialPos.y * initialPos.y + initialPos.z * initialPos.z;
    initialAcc.x = compute_acceleration(initialPos.x, initialPos.z, r0_squared, 0);
    initialAcc.y = compute_acceleration(initialPos.y, initialPos.z, r0_squared, 1);
    initialAcc.z = compute_acceleration(initialPos.z, initialPos.z, r0_squared, 2);
    
    /* 
    Transform position and velocity to Earth-Centered Inertial (ECI) coordinates
    */
   RotationalMatrix R = defineRotationalMatrix(rightAscensionOfAscendingNode,
    argumentOfPerigee,
    inlinationAngle);
    
    
    
    State state;
    state.positions.x = R.RotMatrix[0][0] * initialPos.x + R.RotMatrix[0][1] * initialPos.y + R.RotMatrix[0][2] * initialPos.z;
    state.positions.y = R.RotMatrix[1][0] * initialPos.x + R.RotMatrix[1][1] * initialPos.y + R.RotMatrix[1][2] * initialPos.z;
    state.positions.z = R.RotMatrix[2][0] * initialPos.x + R.RotMatrix[2][1] * initialPos.y + R.RotMatrix[2][2] * initialPos.z;

    state.velocities.x = R.RotMatrix[0][0] * initialVel.x + R.RotMatrix[0][1] * initialVel.y + R.RotMatrix[0][2] * initialVel.z;
    state.velocities.y = R.RotMatrix[1][0] * initialVel.x + R.RotMatrix[1][1] * initialVel.y + R.RotMatrix[1][2] * initialVel.z;
    state.velocities.z = R.RotMatrix[2][0] * initialVel.x + R.RotMatrix[2][1] * initialVel.y + R.RotMatrix[2][2] * initialVel.z;

    state.accelerations.x = R.RotMatrix[0][0] * initialAcc.x + R.RotMatrix[0][1] * initialAcc.y + R.RotMatrix[0][2] * initialAcc.z;
    state.accelerations.y = R.RotMatrix[1][0] * initialAcc.x + R.RotMatrix[1][1] * initialAcc.y + R.RotMatrix[1][2] * initialAcc.z;
    state.accelerations.z = R.RotMatrix[2][0] * initialAcc.x + R.RotMatrix[2][1] * initialAcc.y + R.RotMatrix[2][2] * initialAcc.z;


    return state;
}