from QuietSwarm.Classes.Swarm import Swarm


def main():
    dt          = 0.001
    tmax        = 6560
    n_steps     = int(tmax // dt)
    
    orbitalfile = "test.dat"
    
    
    swarm = Swarm(orbitalfile)
    swarm.propagate(n_steps=n_steps, dt=dt)
    

if __name__ == "__main__":
    main()
