import numpy as np

class Quaternion:
    def __init__(self,w,x,y,z):
        self.w    = w
        self.quat = np.array([x,y,z])
        
    
    @staticmethod
    def fromAxisAngle(x,y,z,angle):
        eps  = 1e-12
        norm = np.sqrt(x**2 + y**2 + z**2)

        x /= (norm + eps)
        z /= (norm + eps)
        y /= (norm + eps)
        
        w = np.cos(angle / 2)
        x *= np.sin(angle / 2)
        y *= np.sin(angle / 2)
        z *= np.sin(angle / 2)
        
        
        return Quaternion(w,x,y,z)
    
    
    def RotMat3x3(self):
        R3 = np.zeros((3,3))
        
        w = self.w
        x = self.quat[0]
        y = self.quat[1]
        z = self.quat[2]
        
        diagonal_vals     = np.diag([1 - 2*(y**2 + z**2), 1 - 2*(x**2 + z**2), 1 - 2*(x**2 + y**2)])
        off_diag_1_top    = np.diag([2*(x*y - w*z), 2*(y*z - w*x)], k=1)
        off_diag_1_bottom = np.diag([2*(x*y + w*z), 2*(y*z + w*x)], k=-1)
        
        off_diag_2_top    = np.diag([2*(x*z + w*y)], k=2)
        off_diag_2_bottom = np.diag([2*(x*z - w*y)], k=-2)
        
        R3 += (diagonal_vals +
               off_diag_1_top + off_diag_1_bottom +
               off_diag_2_top + off_diag_2_bottom
               )
        
        return R3
        
        