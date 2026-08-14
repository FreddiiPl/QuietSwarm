#ifndef RAYMARCH_H
#define RAYMARCH_H

#include <stdio.h>
#include <stdbool.h>
#include <math.h>


#define MAX_STEP 1000

typedef struct {
    double x, y, z;
} Vec3;

Vec3 vec3_add(Vec3 a, Vec3 b) {
    Vec3 result = {a.x + b.x, a.y + b.y, a.z + b.z};
    return result;
}

Vec3 vec3_scale(Vec3 v, double s) {
    Vec3 result = {v.x * s, v.y * s, v.z * s};
    return result;
}


typedef struct {
    double* data;
    int width;
    int height;
    double cellSize;
} DEM;

double get_dem_height(Vec3 pos, const DEM* dem) {
    int col = (int)pos.x / dem->cellSize;
    int row = (int)pos.z / dem->cellSize;

    if (col >= 0 && col < dem->width && row >= 0 && row < dem->height) {
        return dem->data[row * dem->width + col];
    }

    return 0.0;
}


#endif