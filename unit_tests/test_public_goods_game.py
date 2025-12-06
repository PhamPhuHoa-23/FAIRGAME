"""
Unit tests for Public Goods Game functionality.

Tests the core components of the Public Goods Game implementation including
the payoff matrix, game mechanics, and prompt creation.
"""

import unittest
from pathlib import Path
import sys

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.public_goods_payoff_matrix import PublicGoodsPayoffMatrix
from src.agent import Agent


class TestPublicGoodsPayoffMatrix(unittest.TestCase):
    """
    Test cases for PublicGoodsPayoffMatrix class.
    """

    def setUp(self):
        """
        Set up test fixtures.
        """
        self.matrix_data = {
            "weights": {},
            "strategies": {
                "en": {
                    "strategy1": "Contribute",
                    "strategy2": "Free-ride"
                }
            },
            "combinations": {},
            "matrix": {}
        }
        
        self.public_goods_config = {
            "contributionCost": 10,
            "multiplicationFactor": 2.0,
            "numAgents": 4
        }
        
        self.payoff_matrix = PublicGoodsPayoffMatrix(
            self.matrix_data,
            "en",
            self.public_goods_config
        )
    
    def test_initialization(self):
        """
        Test that the payoff matrix initializes correctly.
        """
        self.assertEqual(self.payoff_matrix.contribution_cost, 10)
        self.assertEqual(self.payoff_matrix.multiplication_factor, 2.0)
        self.assertEqual(self.payoff_matrix.num_agents, 4)
    
    def test_calculate_payoff_all_contribute(self):
        """
        Test payoff calculation when all agents contribute.
        
        Expected: Each agent gets (4 * 10 * 2.0 / 4) - 10 = 20 - 10 = 10
        """
        payoff = self.payoff_matrix.calculate_payoff(
            agent_contributed=True,
            num_contributors=4
        )
        self.assertEqual(payoff, 10.0)
    
    def test_calculate_payoff_none_contribute(self):
        """
        Test payoff calculation when no agents contribute.
        
        Expected: Each agent gets (0 * 2.0 / 4) - 0 = 0
        """
        payoff = self.payoff_matrix.calculate_payoff(
            agent_contributed=False,
            num_contributors=0
        )
        self.assertEqual(payoff, 0.0)
    
    def test_calculate_payoff_solo_contributor(self):
        """
        Test payoff calculation when only one agent contributes.
        
        Expected for contributor: (10 * 2.0 / 4) - 10 = 5 - 10 = -5
        Expected for free-rider: (10 * 2.0 / 4) - 0 = 5
        """
        contributor_payoff = self.payoff_matrix.calculate_payoff(
            agent_contributed=True,
            num_contributors=1
        )
        freerider_payoff = self.payoff_matrix.calculate_payoff(
            agent_contributed=False,
            num_contributors=1
        )
        self.assertEqual(contributor_payoff, -5.0)
        self.assertEqual(freerider_payoff, 5.0)
    
    def test_calculate_payoff_two_contributors(self):
        """
        Test payoff calculation when two agents contribute.
        
        Expected for contributor: (2 * 10 * 2.0 / 4) - 10 = 10 - 10 = 0
        Expected for free-rider: (2 * 10 * 2.0 / 4) - 0 = 10
        """
        contributor_payoff = self.payoff_matrix.calculate_payoff(
            agent_contributed=True,
            num_contributors=2
        )
        freerider_payoff = self.payoff_matrix.calculate_payoff(
            agent_contributed=False,
            num_contributors=2
        )
        self.assertEqual(contributor_payoff, 0.0)
        self.assertEqual(freerider_payoff, 10.0)
    
    def test_get_weights_for_combination(self):
        """
        Test that get_weights_for_combination returns correct payoffs.
        """
        strategy_list = ["Contribute", "Contribute", "Free-ride", "Free-ride"]
        payoffs = self.payoff_matrix.get_weights_for_combination(strategy_list)
        
        # 2 contributors: each contributor gets 0, each free-rider gets 10
        expected = (0.0, 0.0, 10.0, 10.0)
        self.assertEqual(payoffs, expected)
    
    def test_get_combination_key(self):
        """
        Test that get_combination_key generates correct keys.
        """
        round_strategies = ["strategy1", "strategy1", "strategy2", "strategy2"]
        key = self.payoff_matrix.get_combination_key(round_strategies)
        self.assertEqual(key, "combination_2_contributors")
    
    def test_attribute_scores(self):
        """
        Test that attribute_scores correctly assigns payoffs to agents.
        """
        # Create mock agents
        agents = [
            Agent("agent1", "TestLLM", "cooperative", 0),
            Agent("agent2", "TestLLM", "selfish", 0),
            Agent("agent3", "TestLLM", "strategic", 0),
            Agent("agent4", "TestLLM", "altruistic", 0)
        ]
        
        # 3 contribute, 1 free-rides
        round_strategies = ["strategy1", "strategy1", "strategy1", "strategy2"]
        
        self.payoff_matrix.attribute_scores(agents, round_strategies)
        
        # Expected: (3 * 10 * 2.0 / 4) - 10 = 15 - 10 = 5 for contributors
        # Expected: (3 * 10 * 2.0 / 4) - 0 = 15 for free-rider
        self.assertEqual(agents[0].last_score(), 5.0)
        self.assertEqual(agents[1].last_score(), 5.0)
        self.assertEqual(agents[2].last_score(), 5.0)
        self.assertEqual(agents[3].last_score(), 15.0)


class TestPublicGoodsGameConfig(unittest.TestCase):
    """
    Test cases for Public Goods Game configuration loading.
    """
    
    def test_config_file_exists(self):
        """
        Test that the config file exists and is readable.
        """
        config_path = Path("resources/config/public_goods_game/public_goods_game_round_known.json")
        self.assertTrue(config_path.exists(), f"Config file not found at {config_path}")
    
    def test_template_files_exist(self):
        """
        Test that the template files exist for both languages.
        """
        en_template = Path("resources/game_templates/public_goods_game_en.txt")
        vn_template = Path("resources/game_templates/public_goods_game_vn.txt")
        
        self.assertTrue(en_template.exists(), f"English template not found at {en_template}")
        self.assertTrue(vn_template.exists(), f"Vietnamese template not found at {vn_template}")


def run_tests():
    """
    Run all tests and display results.
    """
    # Create test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Add test cases
    suite.addTests(loader.loadTestsFromTestCase(TestPublicGoodsPayoffMatrix))
    suite.addTests(loader.loadTestsFromTestCase(TestPublicGoodsGameConfig))
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Return exit code
    return 0 if result.wasSuccessful() else 1


if __name__ == "__main__":
    sys.exit(run_tests())
