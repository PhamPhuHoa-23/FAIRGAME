
from src.game_round import GameRound
from src.public_goods_prompt_creator import PublicGoodsPromptCreator


class PublicGoodsGameRound(GameRound):
    """
    Specialized GameRound for Public Goods Game.
    
    Uses PublicGoodsPromptCreator to handle public goods specific template variables.
    """
    
    def create_prompt(self, agent, phase):
        """
        Create a prompt for an agent using the PublicGoodsPromptCreator.
        
        Args:
            agent: The agent object to create the prompt for.
            phase (str): The phase of the round ('communicate' or 'choose').
        
        Returns:
            str: The prompt to be sent to the agent.
        """
        opponents = self._get_opponents(agent)
        prompt_creator = PublicGoodsPromptCreator(
            self.game.language,
            self.game.prompt_template,
            self.game.n_rounds,
            self.game.n_rounds_known,
            self.game.payoff_matrix,
            self.game.public_goods_config
        )
        return prompt_creator.fill_template(
            agent,
            opponents,
            self.round_number,
            self.game.history.rounds,
            phase
        )
