#include "raymarch.h"



void GetRefractiveProperties(Vec3 pos, double* n, Vec3* gradient) {
    *n = 1.0; 

    gradient->x = 0.0;
    gradient->y = 0.0;
    gradient->z = 0.0;
};



Vec3 ComputeDirectionDerivative(Vec3 u, double n, Vec3 gradient) {
    double dotProduct = gradient.x * u.x + gradient.y * u.y + gradient.z * u.z;
    
    Vec3 delta;
    delta.x = gradient.x - dotProduct * u.x;
    delta.y = gradient.y - dotProduct * u.y;
    delta.z = gradient.z - dotProduct * u.z;
    
    double invN = 1.0 / n;
    return vec3_scale(delta, invN);
}


void EulerStep(Vec3 position, Vec3 direction, double ds, 
               Vec3 *updatedPosition, Vec3 *updatedDirection) {

    double currentRefractive;
    Vec3 refractiveGradient;


    GetRefractiveProperties(position, &currentRefractive, &refractiveGradient);
    

    updatedPosition->x = position.x + direction.x * ds;
    updatedPosition->y = position.y + direction.y * ds;
    updatedPosition->z = position.z + direction.z * ds;

    double dotProduct = refractiveGradient.x * direction.x + refractiveGradient.y * direction.y + refractiveGradient.z * direction.z;

    double deltaX = refractiveGradient.x - dotProduct * direction.x;
    double deltaY = refractiveGradient.y - dotProduct * direction.y;
    double deltaZ = refractiveGradient.z - dotProduct * direction.z;

    double currentRefractive_inv = (1 / currentRefractive);
    Vec3 nextDirection;
    nextDirection.x = direction.x + currentRefractive_inv * deltaX * ds;
    nextDirection.y = direction.y + currentRefractive_inv * deltaY * ds;
    nextDirection.z = direction.z + currentRefractive_inv * deltaZ * ds;

    // Normalize updatedDirection
    double length = sqrt(nextDirection.x * nextDirection.x + nextDirection.y * nextDirection.y + nextDirection.z * nextDirection.z);

    if (length > 0.0) {
        updatedDirection->x = nextDirection.x / length;
        updatedDirection->y = nextDirection.y / length;
        updatedDirection->z = nextDirection.z / length;
    }
    
}


void RK4Step(Vec3 position, Vec3 direction, double ds, 
             Vec3 *updatedPosition, Vec3 *updatedDirection) {
    
    double currentRefractive;
    Vec3 refractiveGradient;
    double half_ds = ds * 0.5;
    
    // 1
    GetRefractiveProperties(position, &currentRefractive, &refractiveGradient);
    Vec3 dr1 = direction;
    Vec3 du1 = ComputeDirectionDerivative(direction, currentRefractive, refractiveGradient);

    // 2
    Vec3 pos2 = vec3_add(position, vec3_scale(dr1, half_ds));
    Vec3 dir2 = vec3_add(direction, vec3_scale(du1, half_ds));
    GetRefractiveProperties(pos2, &currentRefractive, &refractiveGradient);
    Vec3 dr2 = dir2;
    Vec3 du2 = ComputeDirectionDerivative(dir2, currentRefractive, refractiveGradient);
            

    // 3
    Vec3 pos3 = vec3_add(position, vec3_scale(dr2, half_ds));
    Vec3 dir3 = vec3_add(direction, vec3_scale(du2, half_ds));
    GetRefractiveProperties(pos3, &currentRefractive, &refractiveGradient);
    Vec3 dr3 = dir3;
    Vec3 du3 = ComputeDirectionDerivative(dir3, currentRefractive, refractiveGradient);

    // 4
    Vec3 pos4 = vec3_add(position, vec3_scale(dr3, half_ds));
    Vec3 dir4 = vec3_add(direction, vec3_scale(du3, half_ds));
    GetRefractiveProperties(pos4, &currentRefractive, &refractiveGradient);
    Vec3 dr4 = dir4;
    Vec3 du4 = ComputeDirectionDerivative(dir4, currentRefractive, refractiveGradient);

    Vec3 sum_dr = vec3_add(vec3_add(dr1, vec3_scale(dr2, 2.0)), vec3_add(vec3_scale(dr3, 2.0), dr4));
    updatedPosition->x = position.x + sum_dr.x * (ds / 6.0);
    updatedPosition->y = position.y + sum_dr.y * (ds / 6.0);
    updatedPosition->z = position.z + sum_dr.z * (ds / 6.0);
    
    Vec3 sum_du = vec3_add(vec3_add(du1, vec3_scale(du2, 2.0)), vec3_add(vec3_scale(du3, 2.0), du4));
    Vec3 nextDirection;
    nextDirection.x = direction.x + sum_du.x * (ds / 6.0);
    nextDirection.y = direction.y + sum_du.y * (ds / 6.0);
    nextDirection.z = direction.z + sum_du.z * (ds / 6.0);

    double length = sqrt(nextDirection.x * nextDirection.x + nextDirection.y * nextDirection.y + nextDirection.z * nextDirection.z);

    if (length > 0.0) {
        updatedDirection->x = nextDirection.x / length;
        updatedDirection->y = nextDirection.y / length;
        updatedDirection->z = nextDirection.z / length;
    } else {
        *updatedDirection = direction;
    }
}


void rayMarch(Vec3 startPos, Vec3 startDir, double ds, const DEM* dem) {

    Vec3 currentPos = startPos;
    Vec3 currentDir = startDir;

    bool hit = false;

    for (int step = 0; step < MAX_STEP; step++) {
        double groundHeight = get_dem_height(currentPos, dem);

        if (currentPos.y <= groundHeight) {
            hit = true;
            break;
        }

        if (currentPos.x < 0 || currentPos.x > (dem->width * dem->cellSize) ||
            currentPos.z < 0 || currentPos.z > (dem->height * dem->cellSize)) {
            break;
        }

        Vec3 nextPos, nextDir;
        RK4Step(currentPos, currentDir, ds, &nextPos, &nextDir);

        currentPos = nextPos;
        currentDir = nextDir;
    }

    if (hit) {
        printf("Strålen träffade marken vid: X=%.2f, Y=%.2f, Z=%.2f\n", 
               currentPos.x, currentPos.y, currentPos.z);
    } else {
        printf("Strålen försvann ut i rymden/utanför kartan.\n");
    }
    
}
