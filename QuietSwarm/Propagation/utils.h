#ifndef UTILS_H
#define UTILS_H

typedef struct {
    double RotMatrix[3][3];
} RotationalMatrix;

RotationalMatrix defineRotationalMatrix(double Omega, double omega, double i);

double compute_acceleration(double val, double z, 
                            double r2, int j
                            );

double compute_velocity(double val, double acceleration, double h2);
#endif