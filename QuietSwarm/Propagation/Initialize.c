
#include "propagator.h"
#include "utils.h"


State initialize_state(OrbitalParameters orbit) {
    
    double rightAscensionOfAscendingNode = orbit.rightAscensionOfAscendingNode;
    double argumentOfPerigee             = orbit.argumentOfPerigee;
    double inclinationAngle               = orbit.inclinationAngle;
    double phaseAngles                   = orbit.phaseAngles;
    double semiMajorAxis                 = orbit.semiMajorAxis / a_normalizer;
    double eccentricity                  = orbit.eccentricity;


    // Vector3 initialPos;
    // Vector3 initialVel;
    
    double e2          = eccentricity * eccentricity;
    double r0          = (semiMajorAxis * ( 1 - e2) ) / ( 1 + eccentricity * cos(phaseAngles) );
    double v0          = sqrt(1.0 / (semiMajorAxis * ( 1 - e2 )) );
    
    Vector3 initialPos = { r0 * cos(phaseAngles), r0 * sin(phaseAngles), 0.0 };
    Vector3 initialVel = { -v0 * sin(phaseAngles), v0 * (eccentricity + cos(phaseAngles)), 0.0 };
    // Vector3 initialAcc;
    
    /* 
    Transform position and velocity to Earth-Centered Inertial (ECI) coordinates
    */
   RotationalMatrix R = defineRotationalMatrix(rightAscensionOfAscendingNode,
                                                argumentOfPerigee,
                                                inclinationAngle);
    
    
    
    State state;
    state.positions.x = R.RotMatrix[0][0] * initialPos.x + R.RotMatrix[0][1] * initialPos.y + R.RotMatrix[0][2] * initialPos.z;
    state.positions.y = R.RotMatrix[1][0] * initialPos.x + R.RotMatrix[1][1] * initialPos.y + R.RotMatrix[1][2] * initialPos.z;
    state.positions.z = R.RotMatrix[2][0] * initialPos.x + R.RotMatrix[2][1] * initialPos.y + R.RotMatrix[2][2] * initialPos.z;

    state.velocities.x = R.RotMatrix[0][0] * initialVel.x + R.RotMatrix[0][1] * initialVel.y + R.RotMatrix[0][2] * initialVel.z;
    state.velocities.y = R.RotMatrix[1][0] * initialVel.x + R.RotMatrix[1][1] * initialVel.y + R.RotMatrix[1][2] * initialVel.z;
    state.velocities.z = R.RotMatrix[2][0] * initialVel.x + R.RotMatrix[2][1] * initialVel.y + R.RotMatrix[2][2] * initialVel.z;

    double r0_squared = state.positions.x * state.positions.x + 
                        state.positions.y * state.positions.y + 
                        state.positions.z * state.positions.z;

    state.accelerations.x = compute_acceleration(state.positions.x, state.positions.z, r0_squared, 0);
    state.accelerations.y = compute_acceleration(state.positions.y, state.positions.z, r0_squared, 1);
    state.accelerations.z = compute_acceleration(state.positions.z, state.positions.z, r0_squared, 2);



    return state;
}