"""
Reorganize Public Goods Game results into directory structure:
    language/multiplication_factor/model/

Usage:
    python reorganize_public_goods_results.py [--dry-run]
"""

import argparse
import shutil
from pathlib import Path
import re
import glob

RESULTS_PATH = Path("resources/results")
TARGET_BASE = Path("resources/results")

# Model name mapping from filename to directory name
MODEL_NAME_MAP = {
    "claude35haiku": "claude",
    "chatgpt4o": "chatgpt",
    "mistrallarge": "mistralarge"
}


def parse_filename(filename: str) -> dict:
    """
    Parse result filename to extract language, r value, and model.
    
    Expected format: results_public_goods_game_round_known_<lang>_<n>_agents_<m>_rounds_<model>_cost<cost>_r<r>_<num>.csv
    
    Returns:
        dict with keys: language, r_value, model, original_filename
        Returns None if filename doesn't match pattern
    """
    # Pattern: results_public_goods_game_round_known_<lang>_<n>_agents_<m>_rounds_<model>_cost<cost>_r<r>_<num>.csv
    pattern = r"results_public_goods_game_round_known_(\w+)_\d+_agents_\d+_rounds_(\w+)_cost\d+_r([\d.]+)_\d+\.csv"
    
    match = re.match(pattern, filename)
    if not match:
        return None
    
    language = match.group(1)
    model_raw = match.group(2).lower()
    r_value = match.group(3)
    
    # Map model name
    model = MODEL_NAME_MAP.get(model_raw, model_raw)
    
    return {
        "language": language,
        "r_value": r_value,
        "model": model,
        "original_filename": filename
    }


def get_target_path(language: str, r_value: str, model: str) -> Path:
    """
    Get target path for organized results.
    
    Args:
        language: Language code (en, vn)
        r_value: Multiplication factor as string (e.g., "1.1", "2", "2.9")
        model: Model name (claude, chatgpt, mistralarge)
    
    Returns:
        Path object for target directory
    """
    # Format r_value: convert to float and format consistently
    try:
        r_float = float(r_value)
        if r_float == int(r_float):
            r_str = f"r{int(r_float)}"
        else:
            r_str = f"r{r_float}"
    except ValueError:
        # If conversion fails, use as-is
        r_str = f"r{r_value}"
    
    return TARGET_BASE / language / r_str / model


def organize_results(dry_run: bool = False) -> None:
    """
    Organize results files into directory structure.
    
    Args:
        dry_run: If True, only print what would be done without actually moving files
    """
    if not RESULTS_PATH.exists():
        print(f"❌ Results directory not found: {RESULTS_PATH}")
        return
    
    # Find all public goods game result files
    pattern = str(RESULTS_PATH / "results_public_goods_game_round_known_*.csv")
    result_files = glob.glob(pattern)
    
    if not result_files:
        print(f"⚠️  No public goods game result files found in {RESULTS_PATH}")
        return
    
    print(f"Found {len(result_files)} result files")
    print(f"{'='*60}")
    
    if dry_run:
        print("DRY RUN MODE - No files will be moved\n")
    
    moved_count = 0
    skipped_count = 0
    error_count = 0
    
    for file_path in sorted(result_files):
        file_path_obj = Path(file_path)
        filename = file_path_obj.name
        
        # Parse filename
        info = parse_filename(filename)
        if not info:
            print(f"⚠️  Skipping (unrecognized format): {filename}")
            skipped_count += 1
            continue
        
        # Get target path
        target_dir = get_target_path(info["language"], info["r_value"], info["model"])
        target_file = target_dir / filename
        
        if dry_run:
            print(f"Would move: {filename}")
            print(f"  From: {file_path_obj}")
            print(f"  To:   {target_file}")
            print(f"  Info: lang={info['language']}, r={info['r_value']}, model={info['model']}")
            print()
        else:
            try:
                # Create target directory
                target_dir.mkdir(parents=True, exist_ok=True)
                
                # Move file
                shutil.move(str(file_path_obj), str(target_file))
                print(f"✓ Moved: {filename} -> {target_dir}")
                moved_count += 1
            except Exception as e:
                print(f"❌ Error moving {filename}: {e}")
                error_count += 1
    
    print(f"{'='*60}")
    if dry_run:
        print(f"Summary: {len(result_files)} files would be organized")
    else:
        print(f"Summary:")
        print(f"  Moved: {moved_count}")
        print(f"  Skipped: {skipped_count}")
        print(f"  Errors: {error_count}")
        print(f"\nResults organized in: {TARGET_BASE}")


def main():
    parser = argparse.ArgumentParser(
        description="Reorganize Public Goods Game results into directory structure",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
The results will be organized as:
    resources/results/
        <language>/
            r<multiplication_factor>/
                <model>/
                    <result_files>.csv

Example:
    resources/results/
        en/
            r2/
                claude/
                    results_public_goods_game_round_known_en_3_agents_10_rounds_claude35haiku_cost10_r2_0.csv
        """
    )
    
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be done without actually moving files"
    )
    
    args = parser.parse_args()
    
    organize_results(dry_run=args.dry_run)


if __name__ == "__main__":
    main()

