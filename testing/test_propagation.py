from QuietSwarm.Classes.Swarm import Swarm


def main():
    dt          = 0.001
    tmax        = 6560
    n_steps     = int(tmax // dt)
    stride      = 10
    
    
    orbitalfile = "test.dat"
    
    swarm = Swarm(orbitalfile)
    output = swarm.propagate(n_steps=n_steps, dt=dt,stride=stride)
    swarm.compute_geometry(...) # to be written
    
    
if __name__ == "__main__":
    main()
