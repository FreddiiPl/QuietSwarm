from QuietSwarm.Classes.Swarm import Swarm


def main():
    dt          = 0.01
    tmax        = 6560
    n_steps     = int(tmax // dt)
    
    
    orbitalfile = "test.dat"
    state_filepath = r"/Users/fredrikplane/Documents/GithubProjects/QuietSwarm/testing/datasets/state.dat"
    
    swarm = Swarm(orbitalfile)
    output = swarm.propagate(n_steps=n_steps, dt=dt,filepath=state_filepath)
    swarm.compute_geometry(...) # to be written
    
    
if __name__ == "__main__":
    main()
