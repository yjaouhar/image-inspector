from pathlib import Path

# Resolve project-relative paths from the src/ directory.
BASE_DIR = Path(__file__).resolve().parents[1] 
OUTPUT_DIR = BASE_DIR / "output"



PGP_BEGIN = "-----BEGIN PGP"
PGP_END = "-----END PGP"