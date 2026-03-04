import shutil
from src.config import TRIMMED_DIR, OVERLAYED_DIR, NORMALISED_DIR, FADED_DIR, FINAL_DIR

CLEAN_DIRS = [TRIMMED_DIR, OVERLAYED_DIR, NORMALISED_DIR, FADED_DIR, FINAL_DIR]

if __name__ == "__main__":
    confirm = input("This will delete all output files except downloads. Continue? (y/n): ")
    if confirm.lower() == "y":
        for directory in CLEAN_DIRS:
            if directory.exists():
                shutil.rmtree(directory)
                directory.mkdir()
                print(f"Cleaned: {directory}")
            else:
                print(f"Skipped (doesn't exist): {directory}")
        print("Done.")
    else:
        print("Aborted.")
