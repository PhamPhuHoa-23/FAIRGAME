
from src.payoff_matrix import PayoffMatrix


class PublicGoodsPayoffMatrix(PayoffMatrix):
    """
    Specialized payoff matrix for Public Goods Game.
    
    Instead of using predefined combinations, this class calculates payoffs
    based on the number of contributors vs free-riders.
    
    Payoff formula for each agent:
        payoff = (total_contributions * multiplication_factor / num_agents) - individual_contribution
    """

    def __init__(self, matrix_data, language, public_goods_config):
        """
        Initialize the PublicGoodsPayoffMatrix.
        
        Args:
            matrix_data (dict): Standard matrix data with strategies.
            language (str): Language key for strategies.
            public_goods_config (dict): Configuration containing:
                - contributionCost (float): Cost to contribute.
                - multiplicationFactor (float): Multiplier for total pool.
                - numAgents (int): Number of agents in the game.
        """
        super().__init__(matrix_data, language)
        self.contribution_cost = public_goods_config['contributionCost']
        self.multiplication_factor = public_goods_config['multiplicationFactor']
        self.num_agents = public_goods_config['numAgents']
    
    def calculate_payoff(self, agent_contributed, num_contributors):
        """
        Calculate payoff for a single agent.
        
        Args:
            agent_contributed (bool): Whether this agent contributed.
            num_contributors (int): Total number of agents who contributed.
        
        Returns:
            float: The payoff for this agent.
        """
        total_contributions = num_contributors * self.contribution_cost
        pool_value = total_contributions * self.multiplication_factor
        equal_share = pool_value / self.num_agents
        
        individual_cost = self.contribution_cost if agent_contributed else 0
        return equal_share - individual_cost
    
    def attribute_scores(self, agents, round_strategies):
        """
        Calculate and attribute scores to agents based on their choices.
        
        Args:
            agents (list): List of agent objects.
            round_strategies (list of str): Strategy keys chosen by each agent.
        """
        # Get the strategy key for "contribute" (strategy1)
        contribute_key = 'strategy1'
        
        # Count total contributors
        num_contributors = sum(1 for strategy in round_strategies if strategy == contribute_key)
        
        # Assign payoffs to each agent
        for agent, strategy in zip(agents, round_strategies):
            agent_contributed = (strategy == contribute_key)
            payoff = self.calculate_payoff(agent_contributed, num_contributors)
            agent.add_score(payoff)
    
    def get_weights_for_combination(self, strategy_list):
        """
        Override to calculate weights dynamically based on contribution counts.
        
        Args:
            strategy_list (list of str): Strategy names chosen by agents.
        
        Returns:
            tuple: Tuple of payoff values for each agent.
        """
        name_to_key = {name: key for key, name in self.strategies.items()}
        key_list = [name_to_key.get(strategy_name) for strategy_name in strategy_list]
        
        contribute_key = 'strategy1'
        num_contributors = sum(1 for key in key_list if key == contribute_key)
        
        payoffs = []
        for strategy_key in key_list:
            agent_contributed = (strategy_key == contribute_key)
            payoff = self.calculate_payoff(agent_contributed, num_contributors)
            payoffs.append(payoff)
        
        return tuple(payoffs)
    
    def get_combination_key(self, round_strategies):
        """
        Generate a combination key based on the number of contributors.
        
        Args:
            round_strategies (list of str): Strategy keys selected for a round.
        
        Returns:
            str: A combination key like 'combination_3_contributors'.
        """
        contribute_key = 'strategy1'
        num_contributors = sum(1 for strategy in round_strategies if strategy == contribute_key)
        return f'combination_{num_contributors}_contributors'
