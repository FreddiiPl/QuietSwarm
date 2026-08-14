#ifndef PATTERN_H
#define PATTERN_H

#include <math.h>
#include <complex.h>


typedef struct {
    double real;
    double imag;
} Complex;

Complex add(Complex a, Complex b) {
    Complex c;
    c.real = a.real + b.real;
    c.imag = a.imag + b.imag;

    return c;
};

Complex sub(Complex a, Complex b) {
    Complex c;
    c.real = a.real - b.real;
    c.imag = a.imag - b.imag;

    return c;
};

Complex mul(Complex a, Complex b) {
    Complex c;

    c.real = a.real * b.real - a.imag * b.imag;
    c.imag = a.real * b.imag + a.imag * b.real;

    return c;
};


void FFT(Complex *x, int n);

double GaussianLegendreQuadrature(double (*f)(double), double a, double b);


double associatedLegendrePolynomial(double x, int l, int m);
double sphericalHarmonics(double theta, double phi, int l, int m);
void pattern();


#endif