from .wgs84        import *
from astropy.utils import iers

import erfa
import numpy as np



def GCRSRotMatrix(utc):
    ut1 = utc.ut1
    tt = utc.tt

    table = iers.earth_orientation_table.get()
    xp, yp = table.pm_xy(ut1)

    R_erfa = erfa.c2t06a(
        ut1.jd1,
        ut1.jd2,
        tt.jd1,
        tt.jd2,
        xp.to_value("rad"),
        yp.to_value("rad")
    )


    return R_erfa
    


def eciToecef(utc, state_eci):
    '''
    Based on IERS conventions -> GCRS - ITRF conversion using implemented precession-nutation model (IAU2000/2006)
    '''

    RotMatrix     = GCRSRotMatrix(utc)
    
    vector_eci  = np.column_stack((state_eci['x'], 
                                   state_eci['y'], 
                                   state_eci['z']))
    
    
    states_ecef = np.einsum("nij,nj->ni",
                            RotMatrix,
                            vector_eci
                            )
    
    
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


