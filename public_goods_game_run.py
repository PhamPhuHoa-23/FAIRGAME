"""
Public Goods Game Runner

This script runs the Public Goods Game using the FairGame framework.
It loads the configuration, creates games, runs them, and saves results.

Usage:
    python public_goods_game_run.py <call_type>
    
    call_type: 'local' or 'api'
        - local: Runs games locally using FairGameFactory
        - api: Sends request to FairGame API server

Example:
    python public_goods_game_run.py local
"""

import sys
import os
from pathlib import Path
from typing import Dict, Any
import requests
from dotenv import load_dotenv
import glob

from src.io_managers.file_manager import FileManager
from src.results_processing.results_processor import ResultsProcessor

RESOURCES_PATH = Path("resources")
TEMPLATES_PATH = RESOURCES_PATH / "game_templates"
CONFIG_PATH = RESOURCES_PATH / "config"
RESULTS_PATH = RESOURCES_PATH / "results"

HEADERS = {"Content-Type": "application/json"}


def load_env_variables() -> str:
    """
    Load environment variables and return the FairGame API URL.
    
    Returns:
        str: The FairGame API URL, defaults to local if not set.
    """
    load_dotenv()
    return os.getenv("FAIRGAME_URL", "http://127.0.0.1:5003/create_and_run_games")


class PublicGoodsGameRunner:
    """
    Orchestrates the running of Public Goods Games either locally or via API.
    """

    def __init__(self, call_type: str, config: Dict[str, Any], 
                 templates: Dict[str, str], fairgame_url: str) -> None:
        """
        Initialize the game runner.
        
        Args:
            call_type (str): Type of call ("local" or "api").
            config (Dict[str, Any]): Game configuration dictionary.
            templates (Dict[str, str]): Mapping of language -> template text.
            fairgame_url (str): URL for the FairGame API (if using "api" call_type).
        """
        self.call_type = call_type
        self.config = config
        self.templates = templates
        self.config["promptTemplate"] = self.templates
        self.fairgame_url = fairgame_url

    def run(self) -> Dict[str, Any]:
        """
        Execute the game based on call_type ("local" or "api").
        
        Returns:
            Dict[str, Any]: Results from running the games.
        
        Raises:
            ValueError: If call_type is invalid.
        """
        if self.call_type == "local":
            return self._local_call()
        elif self.call_type == "api":
            return self._api_call()
        else:
            raise ValueError("Invalid call type. Expected 'local' or 'api'.")

    def _local_call(self) -> Dict[str, Any]:
        """
        Execute the game locally using FairGameFactory.
        
        Returns:
            Dict[str, Any]: Game results.
        """
        from src.fairgame_factory import FairGameFactory
        game_factory = FairGameFactory()
        return game_factory.create_and_run_games(self.config)

    def _api_call(self) -> Dict[str, Any]:
        """
        Execute the game by sending a POST request to the FairGame API.
        
        Returns:
            Dict[str, Any]: Game results from API response.
        """
        response = requests.post(self.fairgame_url, json=self.config, headers=HEADERS)
        return response.json()


def parse_arguments(argv: list) -> tuple:
    """
    Extract the call type, language, and optional config name from command-line arguments.
    
    Args:
        argv (list): Command-line arguments.
    
    Returns:
        tuple: (call_type, language, config_name)
    
    Raises:
        ValueError: If required arguments are not provided.
    """
    if len(argv) < 2:
        raise ValueError("Usage: python public_goods_game_run.py <call_type> [language] [--config <config_name>]\n"
                        "  call_type: 'local' or 'api'\n"
                        "  language: 'en' or 'vn' (default: 'en')\n"
                        "  --config: Optional config file name (without extension)")
    
    call_type = argv[1]
    language = argv[2] if len(argv) > 2 and not argv[2].startswith('--') else 'en'
    
    # Check for --config flag
    config_name = None
    if '--config' in argv:
        config_idx = argv.index('--config')
        if config_idx + 1 < len(argv):
            config_name = argv[config_idx + 1]
    
    return call_type, language, config_name


def load_template_file(template_name: str, language: str) -> str:
    """
    Load a game template file based on template name and language.
    
    Args:
        template_name (str): Base name of the template.
        language (str): Language code (e.g., 'en', 'vn').
    
    Returns:
        str: Template content.
    """
    template_filepath = TEMPLATES_PATH / f"{template_name}_{language}.txt"
    return FileManager.read_template_file(template_filepath)


def load_config_file(config_dir: str, config_name: str) -> Dict[str, Any]:
    """
    Load a JSON config file for the game.
    
    Args:
        config_dir (str): Directory name under CONFIG_PATH.
        config_name (str): Config file name without extension.
    
    Returns:
        Dict[str, Any]: Configuration dictionary.
    """
    config_filepath = CONFIG_PATH / config_dir / f"{config_name}.json"
    return FileManager.read_json_file(config_filepath)


def save_results(results: Dict[str, Any], config_name: str, config: Dict[str, Any], language: str) -> str:
    """
    Convert results to a DataFrame and save as CSV with auto-incrementing number suffix.
    
    Args:
        results (Dict[str, Any]): Game results to save.
        config_name (str): Base name for the results file.
        config (Dict[str, Any]): Game configuration.
        language (str): Language code (e.g., 'en', 'vn').
        
    Returns:
        str: The filename that was saved.
    """
    results_processor = ResultsProcessor()
    df = results_processor.process(results)
    
    # Extract parameters for filename
    num_agents = len(config['agents']['names'])
    num_rounds = config['nRounds']
    llm_name = config['llm'].lower().replace('openai', '').replace('gpt', 'chatgpt').replace('-', '')
    
    # Get contribution cost and multiplication factor from config
    contribution_cost = int(config.get('publicGoodsConfig', {}).get('contributionCost', 0))
    multiplication_factor = config.get('publicGoodsConfig', {}).get('multiplicationFactor', 0)
    # Format multiplication factor as integer if it's a whole number, otherwise 1 decimal
    r_value = int(multiplication_factor) if multiplication_factor == int(multiplication_factor) else multiplication_factor
    
    # Base filename pattern without number
    base_pattern = f"results_{config_name}_{language}_{num_agents}_agents_{num_rounds}_rounds_{llm_name}_cost{contribution_cost}_r{r_value}"
    
    # Find existing files with this pattern
    existing_files = glob.glob(str(RESULTS_PATH / f"{base_pattern}_*.csv"))
    
    # Extract numbers from existing files
    max_number = -1
    for file_path in existing_files:
        filename = Path(file_path).stem  # Get filename without extension
        # Extract the number at the end
        try:
            number_part = filename.split('_')[-1]
            number = int(number_part)
            max_number = max(max_number, number)
        except (ValueError, IndexError):
            continue
    
    # Next number is max + 1 (starts at 0 if no files exist)
    next_number = max_number + 1
    
    # Create final filename with number
    filename = f"{base_pattern}_{next_number}.csv"
    results_filepath = RESULTS_PATH / filename
    FileManager.save_results_csv(df, results_filepath)
    
    return filename



def main() -> None:
    """
    Main entry point for running Public Goods Games.
    
    Loads configuration, templates, runs games, and saves results.
    """
    # Parse command-line arguments
    call_type, language, config_name_arg = parse_arguments(sys.argv)

    # Load environment variables
    fairgame_url = load_env_variables()

    # Configuration parameters
    config_dir = "public_goods_game"
    config_name = config_name_arg if config_name_arg else "public_goods_game_round_known"
    template_name = "public_goods_game"
    
    # Load config file
    config = load_config_file(config_dir, config_name)
    
    # Override config to use only the selected language
    config['languages'] = [language]
    print(f"DEBUG: Config languages after override: {config['languages']}")
    
    # Load template for the selected language
    template_content = load_template_file(template_name, language)
    templates = {language: template_content}
    
    # Create runner and execute
    runner = PublicGoodsGameRunner(call_type, config, templates, fairgame_url)
    results = runner.run()

    # Save results and get the actual filename with number
    saved_filename = save_results(results, config_name, config, language)
    
    print(f"\nPublic Goods Game completed successfully!")
    print(f"Language: {language}")
    print(f"Results saved to: {RESULTS_PATH / saved_filename}")


if __name__ == "__main__":
    main()
