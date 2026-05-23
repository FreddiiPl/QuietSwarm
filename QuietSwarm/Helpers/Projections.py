from QuietSwarm.Classes.Quaternion import Quaternion
from .wgs84        import *
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



def eciToecef(absolute_JD, state_eci):
    '''
    Based on IERS conventions -> GCRS - ITRF conversion using implemented precession-nutation model (IAU2000/2006)
    '''
    
    RotMatrix = GCRSRotMatrix(absolute_JD)

    vector_eci  = np.column_stack((state_eci['x'] * EARTH_SEMI_MAJOR_AXIS, 
                                   state_eci['y'] * EARTH_SEMI_MAJOR_AXIS, 
                                   state_eci['z'] * EARTH_SEMI_MAJOR_AXIS))
    
    states_ecef = vector_eci @ RotMatrix.T
    
    # konvertera tillbaka till tidigare struktur
    output_ecef = np.zeros(len(state_eci), dtype=[('x', '<f8'), ('y', '<f8'), ('z', '<f8')])
    output_ecef['x'] = states_ecef[:, 0]
    output_ecef['y'] = states_ecef[:, 1]
    output_ecef['z'] = states_ecef[:, 2]
    
    return output_ecef



def ecefTolla(states_ecef):
    # auxiliary values
    p     = np.sqrt(states_ecef["x"]**2 + states_ecef["y"]**2)
    theta = np.arctan2(states_ecef["z"] * EARTH_SEMI_MAJOR_AXIS, p * EARTH_SEMI_MINOR_AXIS)
    
    
    longitude = np.arctan2(states_ecef["y"], states_ecef["x"])
    
    latitude  = np.arctan2(states_ecef["z"] + EARTH_ECCENTRICITY_SQ2 * EARTH_SEMI_MINOR_AXIS * np.sin(theta)**3,
                         p - EARTH_ECCENTRICITY_SQ * EARTH_SEMI_MAJOR_AXIS * np.cos(theta)**3)
    
    radius_of_curvature = EARTH_SEMI_MAJOR_AXIS / np.sqrt(1 - EARTH_ECCENTRICITY_SQ * np.sin(latitude)**2)
    
    altitude  = p / np.cos(latitude) - radius_of_curvature
    
    states_lla = np.zeros(len(states_ecef), dtype=[('longitude', '<f8'), ('latitude', '<f8'), ('altitude', '<f8')])
    
    
    states_lla['longitude'] = np.rad2deg(longitude)
    states_lla['latitude'] = np.rad2deg(latitude)
    states_lla['altitude'] = altitude
    
    return states_lla


def llaToEcef(latitude, longitude, altitude):
    '''
    No clue if this work in a general sense - who cares for now
    '''
 
    radius_of_curvature = EARTH_SEMI_MAJOR_AXIS / np.sqrt(1 - EARTH_ECCENTRICITY_SQ * np.sin(latitude)**2)
    
    
    x = (radius_of_curvature + altitude) * np.cos(latitude) * np.cos(longitude)
    y = (radius_of_curvature + altitude) * np.cos(latitude) * np.sin(longitude)
    z = ((1 - EARTH_ECCENTRICITY_SQ)*radius_of_curvature + altitude) * np.sin(latitude)
    
    states_ecef = np.array((x, y, z),
                           dtype=np.dtype([('x', '<f8'), ('y', '<f8'), ('z', '<f8')])
                           )
    
    return states_ecef
    

    
def ecefToAzEl(observer):
    ...

