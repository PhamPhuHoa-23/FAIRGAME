
from src.fairgame import FairGame
from src.public_goods_payoff_matrix import PublicGoodsPayoffMatrix
from src.public_goods_game_round import PublicGoodsGameRound


class PublicGoodsFairGame(FairGame):
    """
    Specialized FairGame for Public Goods Game.
    
    Uses PublicGoodsPayoffMatrix which calculates payoffs dynamically based on
    the number of contributors rather than predefined combinations.
    """

    def __init__(self, name, language, agents, n_rounds, n_rounds_known,
                 payoff_matrix_data, prompt_template, stop_conditions,
                 agents_communicate, public_goods_config):
        """
        Initialize the PublicGoodsFairGame.
        
        Args:
            name (str): The name of the game.
            language (str): The language used by the game.
            agents (dict): A dictionary mapping agent names to agent objects.
            n_rounds (int): The total number of rounds to play.
            n_rounds_known (str or bool): If the number of rounds is known to agents.
            payoff_matrix_data (dict): The data defining the payoff matrix.
            prompt_template (str): The template used to generate prompts for agents.
            stop_conditions (list): A list of combinations that end the game early.
            agents_communicate (str or bool): Whether agents communicate before choosing.
            public_goods_config (dict): Configuration for public goods game mechanics.
        """
        # Don't call parent __init__ yet, we need to create the specialized payoff matrix
        self.name = name
        self.language = language
        self.agents = agents
        self.n_rounds = int(n_rounds)
        self.n_rounds_known = self._str2bool(n_rounds_known)
        self.prompt_template = prompt_template
        self.stop_conditions = stop_conditions
        self.agents_communicate = self._str2bool(agents_communicate)
        self.current_round = 1
        
        # Import here to avoid circular dependency
        from src.game_history import GameHistory
        self.history = GameHistory()
        self.choices_made = []
        
        # Create specialized payoff matrix for public goods
        self.payoff_matrix = PublicGoodsPayoffMatrix(
            payoff_matrix_data,
            language,
            public_goods_config
        )
        self.public_goods_config = public_goods_config
    
    def _str2bool(self, value):
        """
        Convert a string or bool to a boolean value.
        
        Args:
            value (str or bool): The value to interpret as bool.
        
        Returns:
            bool: The interpreted boolean value.
        """
        return value if isinstance(value, bool) else value.strip().lower() == 'true'
    
    @property
    def description(self):
        """
        dict: A description of the game settings, including public goods config.
        """
        return {
            "name": self.name,
            "language": self.language,
            "agents": {name: agent.get_info() for name, agent in self.agents.items()},
            "n_rounds": self.n_rounds,
            "number_of_rounds_is_known": self.n_rounds_known,
            "public_goods_config": self.public_goods_config,
            "agents_communicate": self.agents_communicate
        }
    
    def run_round(self):
        """
        Run a single round using PublicGoodsGameRound.
        
        Overrides the parent method to use the specialized game round class.
        """
        round_runner = PublicGoodsGameRound(self)
        round_strategies = round_runner.run()
        self.choices_made.append(round_strategies)
        self.payoff_matrix.attribute_scores(list(self.agents.values()), round_strategies)
        round_runner._update_round_history()
