
from src.prompt_creator import PromptCreator


class PublicGoodsPromptCreator(PromptCreator):
    """
    Specialized PromptCreator for Public Goods Game.
    
    Extends the base PromptCreator to handle public goods specific placeholders
    like contributionCost, multiplicationFactor, numAgents, and example calculations.
    """
    
    def __init__(self, lang, prompt_template, n_rounds, n_rounds_known, payoff_matrix, public_goods_config):
        """
        Initialize the PublicGoodsPromptCreator.
        
        Args:
            lang (str): Language code.
            prompt_template (str): Template string with placeholders.
            n_rounds (int): Number of rounds.
            n_rounds_known (bool): Whether agents know the number of rounds.
            payoff_matrix: The payoff matrix instance.
            public_goods_config (dict): Public goods specific configuration.
        """
        super().__init__(lang, prompt_template, n_rounds, n_rounds_known, payoff_matrix)
        self.public_goods_config = public_goods_config
    
    def map_placeholders(self, agent_name, opponents, current_round, history):
        """
        Build the dictionary of placeholders including public goods specific values.
        
        Args:
            agent_name (str): Name of the current agent.
            opponents (list): List of opponent agents.
            current_round (int): Current round number.
            history (str): Game history string.
        
        Returns:
            dict: Dictionary mapping placeholder names to values.
        """
        # Get base placeholders from parent
        values = super().map_placeholders(agent_name, opponents, current_round, history)
        
        # Add public goods specific placeholders
        cost = self.public_goods_config['contributionCost']
        multiplier = self.public_goods_config['multiplicationFactor']
        num_agents = self.public_goods_config['numAgents']
        
        values['contributionCost'] = cost
        values['multiplicationFactor'] = multiplier
        values['numAgents'] = num_agents
        
        # Calculate example scenarios
        # If all contribute
        total_if_all_contribute = cost * num_agents
        pool_if_all_contribute = total_if_all_contribute * multiplier
        payoff_if_all_contribute = pool_if_all_contribute / num_agents
        net_gain_if_all_contribute = payoff_if_all_contribute - cost
        
        values['totalIfAllContribute'] = total_if_all_contribute
        values['payoffIfAllContribute'] = payoff_if_all_contribute
        values['netGainIfAllContribute'] = net_gain_if_all_contribute
        
        # If only one contributes (solo contribution)
        solo_pool = cost * multiplier
        solo_contribution_return = solo_pool / num_agents
        solo_contribution_net = solo_contribution_return - cost
        
        values['soloContributionReturn'] = solo_contribution_return
        values['soloContributionNet'] = solo_contribution_net
        
        return values
