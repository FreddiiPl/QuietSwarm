from QuietSwarm.Classes.Quaternion import Quaternion
from astropy.time  import Time
import erfa
import numpy as np


def GCRSRotMatrix(absolute_JD):
    '''
    GCRS - ITRF rotation matrix based on IERS convention
    '''
    
    t_universal_time    = Time(absolute_JD, format="jd", scale="ut1")
    t_terrestrial_time  = Time(absolute_JD, format="jd", scale="tt")
    
    era     = t_universal_time.earth_rotation_angle(longitude=0).radian
    
    X, Y    = erfa.xy06(t_terrestrial_time.jd1, t_terrestrial_time.jd2)
    s       = erfa.s06(t_terrestrial_time.jd1, t_terrestrial_time.jd2, X, Y)
    s_prime = erfa.sp00(t_terrestrial_time.jd1, t_terrestrial_time.jd2)
    
    a       = (1/2) + (1/8) * (X**2 + Y**2)
    
    quaternion = Quaternion
    w1 = quaternion.fromAxisAngle(1,0,0, Y).RotMat3x3()
    w2 = quaternion.fromAxisAngle(0,1,0, X).RotMat3x3()
    w3 = quaternion.fromAxisAngle(0,0,1, -s_prime).RotMat3x3()
    q  = quaternion.fromAxisAngle(0,0,1,s).RotMat3x3()
    
    R  = quaternion.fromAxisAngle(0,0,1, era).RotMat3x3()
    W  = w3 @ w2 @ w1
    Q  = np.array([[1 - a * X**2, -a * X * Y, X],
                    [-a * X * Y, 1 - a * Y**2, Y],
                    [-X, -Y, 1 - a * (X**2 + Y**2)]]) @ q
    
    RotMatrix = Q @ R @ W
    
    return RotMatrix