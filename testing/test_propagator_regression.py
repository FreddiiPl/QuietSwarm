import unittest
from pathlib import Path
from QuietSwarm.Classes.Swarm import Swarm


class TestPropagatorRegression(unittest.TestCase):
    def test_propagate_output_length_matches_expected_stride(self):
        orbitalfile = Path(__file__).resolve().parent / "test.dat"
        swarm = Swarm(str(orbitalfile))

        n_steps = 2000
        stride = 2
        dt = 0.01

        output = swarm.propagate(n_steps=n_steps, dt=dt, stride=stride)

        expected_n_stride = (n_steps + stride - 1) // stride
        expected_length = expected_n_stride * swarm.nr_sats

        self.assertEqual(output.shape[0], expected_length)
        self.assertGreater(expected_length, 0)
        self.assertNotEqual(output[0]['x'], output[-1]['x'])
        self.assertNotEqual(output[0]['y'], output[-1]['y'])
        self.assertNotEqual(output[0]['z'], output[-1]['z'])


if __name__ == "__main__":
    unittest.main()
