#include "projections.h"
#include "paths.h"
#include <stdio.h>
#include <unistd.h>
#include <limits.h>
#include <string.h>

static const double ARCSEC_TO_RAD = 3.14159265358979323846 / (180.0 * 3600.0);
static const double UAS_TO_RAD    = (3.14159265358979323846 / (180.0 * 3600.0)) * 1e-6;



int CIPfundamentalArguments(CelestialParameters *data, int max_row, const char *file) {
    char absolute_path[PATH_MAX];
    int nrows = 0;


   
    getAbsolutePath(absolute_path, PATH_MAX, file);
        
    FILE* fptr = fopen(absolute_path, "r");
    if (fptr == NULL) {
        perror("fopen");
        return 1;
    }

    char line[512];
    while(fgets(line, sizeof(line), fptr) != NULL) {    

        if (line[0] == 'j') continue;

        CelestialParameters row;

        int n = sscanf(line,
            "%d,%lf,%lf,%lf,%lf,%lf,%lf,%lf,%lf,%lf,%lf,%lf,%lf,%lf,%lf,%lf,%lf,%lf",
            &row.j,
            &row.index,
            &row.val1,
            &row.val2,
            &row.c[0], &row.c[1], &row.c[2], &row.c[3],
            &row.c[4], &row.c[5], &row.c[6], &row.c[7],
            &row.c[8], &row.c[9], &row.c[10], &row.c[11],
            &row.c[12], &row.c[13]
        );

        // printf("DEBUG n = %d | line starts: %.30s\n", n, line);
        
        if (n==18 && nrows < max_row) {
            data[nrows++] = row;
        }

    }
    fclose(fptr);

    return nrows;
}


Delauney DelauneyArguments(double t_JD, double t_JD2, double t_JD3, 
                       double t_JD4) {
    
    Delauney args;

    args.l = (485868.249036 + 1717915923.2178 * t_JD + 31.8792 * t_JD2
           + 0.051635 * t_JD3 - 0.00024470 * t_JD4) * ARCSEC_TO_RAD;

    args.l_prime = (1287104.79305 + 129596581.0481 * t_JD + 0.5532 * t_JD2
                 + 0.000136 * t_JD3 - 0.00001149 * t_JD4) * ARCSEC_TO_RAD;

    args.F = (335779.526232 + 1739527264.8478 * t_JD - 12.7512 * t_JD2
           - 0.001037 * t_JD3 + 0.00000417 * t_JD4) * ARCSEC_TO_RAD;

    args.D = (1072260.703692 + 1602961601.2090 * t_JD - 6.3706 * t_JD2 
           + 0.006593 * t_JD3 - 0.00003169 * t_JD4) * ARCSEC_TO_RAD;
    
    args.Omega = (450160.398036 - 6962890.5431 * t_JD + 7.4722 * t_JD2
               + 0.00702 * t_JD3 - 0.00005939 * t_JD4) * ARCSEC_TO_RAD;

    
    args.l       = fmod(args.l,       2.0 * M_PI);
    args.l_prime = fmod(args.l_prime, 2.0 * M_PI);
    args.F       = fmod(args.F,       2.0 * M_PI);
    args.D       = fmod(args.D,       2.0 * M_PI);
    args.Omega   = fmod(args.Omega,   2.0 * M_PI);
        
    return args;
} 

Planetary planetaryArguments(double t_JD, double t_JD2) {
    Planetary plan;

    plan.L_Me = 2.526137408 + 2608.7903141574 * t_JD;
    plan.L_Ve = 3.135340804 + 1021.3285546211 * t_JD;
    plan.L_E  = 1.753470314 +  628.3075849991 * t_JD;
    plan.L_Ma = 6.203476113 +  334.0612426700 * t_JD;
    plan.L_J  = 0.599546497 +   52.9690962641 * t_JD;
    plan.L_Sa = 0.874016757 +   21.3299104960 * t_JD;
    plan.L_U  = 5.481293872 +    7.4781598567 * t_JD;
    plan.L_Ne = 5.311886287 +    3.8133035638 * t_JD;

    plan.p_A  = 0.02438175 * t_JD + 0.00000538691 * t_JD2;

    plan.L_Me = fmod(plan.L_Me, 2.0 * M_PI);
    plan.L_Ve = fmod(plan.L_Ve, 2.0 * M_PI);
    plan.L_E  = fmod(plan.L_E,  2.0 * M_PI);
    plan.L_Ma = fmod(plan.L_Ma, 2.0 * M_PI);
    plan.L_J  = fmod(plan.L_J,  2.0 * M_PI);
    plan.L_Sa = fmod(plan.L_Sa, 2.0 * M_PI);
    plan.L_U  = fmod(plan.L_U,  2.0 * M_PI);
    plan.L_Ne = fmod(plan.L_Ne, 2.0 * M_PI);
    plan.p_A  = fmod(plan.p_A,  2.0 * M_PI);

    if (plan.L_Me < 0) plan.L_Me += 2.0 * M_PI;
    if (plan.L_Ve < 0) plan.L_Ve += 2.0 * M_PI;
    if (plan.L_E  < 0) plan.L_E  += 2.0 * M_PI;
    if (plan.L_Ma < 0) plan.L_Ma += 2.0 * M_PI;
    if (plan.L_J  < 0) plan.L_J  += 2.0 * M_PI;
    if (plan.L_Sa < 0) plan.L_Sa += 2.0 * M_PI;
    if (plan.L_U  < 0) plan.L_U  += 2.0 * M_PI;
    if (plan.L_Ne < 0) plan.L_Ne += 2.0 * M_PI;
    if (plan.p_A  < 0) plan.p_A  += 2.0 * M_PI;

    return plan;
}


CIP CIPCoordinates(double t_JD){

    CIP celestial_position;

    double t_JD2 = t_JD * t_JD;
    double t_JD3 = t_JD2 * t_JD;
    double t_JD4 = t_JD3 * t_JD;
    double t_JD5 = t_JD4 * t_JD;


    Delauney args       = DelauneyArguments(t_JD, t_JD2, t_JD3, t_JD4);
    Planetary plan_args = planetaryArguments(t_JD, t_JD2);


    celestial_position.X = (-0.016617 + 2004.191898 * t_JD - 0.4297829 * t_JD2
                           -0.19861834 * t_JD3 + 0.000007578 * t_JD4
                           +0.0000059285 * t_JD5) * ARCSEC_TO_RAD;
    
    celestial_position.Y = (-0.006951 - 0.025896 * t_JD - 22.4072747 * t_JD2
                           +0.00190059 * t_JD3 + 0.001112526 * t_JD4
                           +0.0000001358 * t_JD5) * ARCSEC_TO_RAD;

    
    CelestialParameters paramX[MAX_ROWS_X];
    CelestialParameters paramY[MAX_ROWS_Y];

    int nrowsX = CIPfundamentalArguments(paramX, MAX_ROWS_X, tab5_2a);
    int nrowsY = CIPfundamentalArguments(paramY, MAX_ROWS_Y, tab5_2b);

    printf("DEBUG: nrowsX = %d, nrowsY = %d\n", nrowsX, nrowsY);

    // Add to XY
    double sumX = 0.0;
    for (int i = 0; i < nrowsX; i++)
    {
        double val1  = paramX[i].val1;
        double val2  = paramX[i].val2;
        double theta = paramX[i].c[0]*args.l + paramX[i].c[1]*args.l_prime 
                     + paramX[i].c[2]*args.F + paramX[i].c[3]*args.D 
                     + paramX[i].c[4]*args.Omega + paramX[i].c[5] * plan_args.L_Me
                     + paramX[i].c[6] * plan_args.L_Ve + paramX[i].c[7] * plan_args.L_E
                     + paramX[i].c[8] * plan_args.L_Ma + paramX[i].c[9] * plan_args.L_J
                     + paramX[i].c[10] * plan_args.L_Sa + paramX[i].c[11] * plan_args.L_U
                     + paramX[i].c[12] * plan_args.L_Ne + paramX[i].c[13] * plan_args.p_A;
        
        double wave = val1 * sin(theta) + val2 * cos(theta);

        if (paramX[i].j == 0) sumX += wave;
        else if (paramX[i].j == 1) sumX += wave * t_JD;
        else if (paramX[i].j == 2) sumX += wave * t_JD2;
        else if (paramX[i].j == 3) sumX += wave * t_JD3;
        else if (paramX[i].j == 4) sumX += wave * t_JD4;

    }
    celestial_position.X += sumX * UAS_TO_RAD;


    double sumY = 0.0;
    for (int i = 0; i < nrowsY; i++)
    {
        double val1  = paramY[i].val1;
        double val2  = paramY[i].val2;
        double theta = paramY[i].c[0]*args.l + paramY[i].c[1]*args.l_prime 
                     + paramY[i].c[2]*args.F + paramY[i].c[3]*args.D 
                     + paramY[i].c[4]*args.Omega + paramY[i].c[5] * plan_args.L_Me
                     + paramY[i].c[6] * plan_args.L_Ve + paramY[i].c[7] * plan_args.L_E
                     + paramY[i].c[8] * plan_args.L_Ma + paramY[i].c[9] * plan_args.L_J
                     + paramY[i].c[10] * plan_args.L_Sa + paramY[i].c[11] * plan_args.L_U
                     + paramY[i].c[12] * plan_args.L_Ne + paramY[i].c[13] * plan_args.p_A;
        
        double wave = val1 * cos(theta) + val2 * sin(theta);

        if (paramY[i].j == 0) sumY += wave;
        else if (paramY[i].j == 1) sumY += wave * t_JD;
        else if (paramY[i].j == 2) sumY += wave * t_JD2;
        else if (paramY[i].j == 3) sumY += wave * t_JD3;
        else if (paramY[i].j == 4) sumY += wave * t_JD4;

    }
    celestial_position.Y += sumY * UAS_TO_RAD;

    // // Corrections
    // double eps_0        = 84381.406 * ARCSEC_TO_RAD;
    // double psi_A        = ( -0.0000000951 * t_JD + 0.000132851 * t_JD2
    //                          - 0.00114045 * t_JD3 - 1.0790069 * t_JD4 
    //                          + 5038.481507 * t_JD5) * ARCSEC_TO_RAD;

    // double chi_A        = ( -0.0000000560 * t_JD + 0.000170663 * t_JD2 
    //                     - 0.00121197 * t_JD3 - 2.3814292 * t_JD4 
    //                     + 10.556403 * t_JD5) * ARCSEC_TO_RAD;


    // double common_term  = (psi_A * cos(eps_0)) - chi_A;

    // double deltaX       = ()

    return celestial_position;

}


void CIOLocator(CIP celestial_position) {
    
}



void eciToecef(double *normalized_time) {

    /*
    Precession and nutation?
    */

}