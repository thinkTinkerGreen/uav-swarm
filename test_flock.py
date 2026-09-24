import unittest
from harness import Harness

class TestUAVSwarm(unittest.TestCase):
    
    def test_alg_1_refusal(self):
        harness = Harness(num_agents=10, backend="ollama", max_duration=2.5)
        self.assertEqual(harness.sim.algo, 1, "Initial algorithm should be 1")
        harness.run()
        self.assertEqual(harness.sim.algo, 2, "Agent failed to refuse Algorithm 1 and switch to Algorithm 2")

    def test_honest_failure(self):
        harness = Harness(num_agents=10, backend="ollama", max_duration=2.5)
        harness.metrics_engine.compute_all = lambda q, p: {
            'c_star': 0.9, 'e_tilde': 0.01, 'k_tilde': 0.01, 'collisions': 5, 'components': 1
        }
        harness.run()
        self.assertTrue(harness.failsafe_triggered, "Agent failed to trigger not_sure failsafe hold.")

if __name__ == '__main__':
    unittest.main()
