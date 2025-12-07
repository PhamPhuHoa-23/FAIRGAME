"""
Run Public Goods Game 10 times consecutively
Each run will automatically increment the file number
"""

import subprocess
import sys

def main():
    # Get language from command line argument (default: en)
    language = sys.argv[1] if len(sys.argv) > 1 else 'en'
    
    print(f"Running Public Goods Game 10 times with language: {language}")
    print("=" * 60)
    
    for i in range(1, 5):
        print(f"\n{'='*60}")
        print(f"RUN {i}/10")
        print(f"{'='*60}\n")
        
        # Run the game
        result = subprocess.run(
            ['python', 'public_goods_game_run.py', 'local', language],
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
    print(f"ALL 10 RUNS COMPLETED!")
    print(f"{'='*60}")

if __name__ == "__main__":
    main()
