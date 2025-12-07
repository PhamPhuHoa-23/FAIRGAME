"""
Run Public Goods Game multiple times with specified parameters

Usage:
    python run_public_goods_with_args.py --num_runs <n> --language <lang> --multiplication_factor <r> --model <model>

Example:
    python run_public_goods_with_args.py --num_runs 10 --language en --multiplication_factor 2.0 --model claude
"""

import argparse
import subprocess
import sys
from pathlib import Path

# Model name mapping
MODEL_MAP = {
    "claude": "Claude35Haiku",
    "chatgpt": "OpenAIGPT4o",
    "mistralarge": "MistralLarge"
}

def get_config_name(language: str, multiplication_factor: float, model: str) -> str:
    """
    Generate config file name based on parameters.
    
    Args:
        language: Language code (en, vn)
        multiplication_factor: Multiplication factor (r value)
        model: Model name (claude, chatgpt, mistralarge)
    
    Returns:
        Config file name without extension
    """
    # Format r value: 1.1 -> r1.1, 2.0 -> r2, 2.9 -> r2.9
    if multiplication_factor == int(multiplication_factor):
        r_str = f"r{int(multiplication_factor)}"
    else:
        r_str = f"r{multiplication_factor}"
    
    return f"public_goods_game_{language}_{r_str}_{model}"


def main():
    parser = argparse.ArgumentParser(
        description="Run Public Goods Game multiple times with specified parameters",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python run_public_goods_with_args.py --num_runs 10 --language en --multiplication_factor 1.1 --model claude
  python run_public_goods_with_args.py --num_runs 4 --language en --multiplication_factor 2.0 --model claude
  python run_public_goods_with_args.py --num_runs 9 --language vn --multiplication_factor 2.0 --model mistralarge
        """
    )
    
    parser.add_argument(
        "--num_runs",
        type=int,
        required=True,
        help="Number of runs to execute"
    )
    
    parser.add_argument(
        "--language",
        type=str,
        required=True,
        choices=["en", "vn"],
        help="Language code (en or vn)"
    )
    
    parser.add_argument(
        "--multiplication_factor",
        type=float,
        required=True,
        help="Multiplication factor (r value), e.g., 1.1, 2.0, 2.9"
    )
    
    parser.add_argument(
        "--model",
        type=str,
        required=True,
        choices=["claude", "chatgpt", "mistralarge"],
        help="Model name: claude, chatgpt, or mistralarge"
    )
    
    parser.add_argument(
        "--call_type",
        type=str,
        default="local",
        choices=["local", "api"],
        help="Call type: local or api (default: local)"
    )
    
    args = parser.parse_args()
    
    # Get config name
    config_name = get_config_name(args.language, args.multiplication_factor, args.model)
    config_path = Path("resources/config/public_goods_game") / f"{config_name}.json"
    
    # Check if config file exists
    if not config_path.exists():
        print(f"❌ Error: Config file not found: {config_path}")
        print(f"Available config files:")
        config_dir = Path("resources/config/public_goods_game")
        if config_dir.exists():
            for f in sorted(config_dir.glob("public_goods_game_*.json")):
                print(f"  - {f.name}")
        sys.exit(1)
    
    print(f"Running Public Goods Game")
    print(f"{'='*60}")
    print(f"Language: {args.language}")
    print(f"Multiplication Factor: {args.multiplication_factor}")
    print(f"Model: {args.model} ({MODEL_MAP[args.model]})")
    print(f"Number of runs: {args.num_runs}")
    print(f"Config: {config_name}")
    print(f"{'='*60}\n")
    
    for i in range(1, args.num_runs + 1):
        print(f"\n{'='*60}")
        print(f"RUN {i}/{args.num_runs}")
        print(f"{'='*60}\n")
        
        # Run the game with specified config
        result = subprocess.run(
            [
                'python', 
                'public_goods_game_run.py', 
                args.call_type, 
                args.language,
                '--config', 
                config_name
            ],
            capture_output=False
        )
        
        if result.returncode != 0:
            print(f"\n❌ Run {i} failed with exit code {result.returncode}")
            user_input = input("Continue with next run? (y/n): ")
            if user_input.lower() != 'y':
                print("Stopping execution.")
                sys.exit(1)
        else:
            print(f"\n✓ Run {i} completed successfully")
    
    print(f"\n{'='*60}")
    print(f"ALL {args.num_runs} RUNS COMPLETED!")
    print(f"{'='*60}")


if __name__ == "__main__":
    main()

