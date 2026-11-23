import csv
from pathlib import Path

from Trilling.quick_calc import calc


SCRIPT_DIR = Path(__file__).resolve().parent
DATA_DIR = SCRIPT_DIR / "Trilling"
DATA_DIRS = [
    Path("degelijke metingen (no AI)/sweep"),
    Path("degelijke metingen (no AI)/finetune lage massa"),
    Path("heavy metingen/rond res freq"),
    Path("heavy metingen/sweeps"),
]
OUTPUT_FILE = SCRIPT_DIR / "analysis_results.csv"

rows = []
for relative_dir in DATA_DIRS:
    directory = DATA_DIR / relative_dir
    for filename in sorted(directory.glob("*.cylinder")):
        measurements = calc(filename)
        if measurements["wh_period"] is None:
            print(f"Warning: no complete wheel period detected in {filename}")
        rows.append({
            "directory": relative_dir.as_posix(),
            "file": filename.name,
            **measurements,
        })

if not rows:
    raise FileNotFoundError(f"No .cylinder files found in {DATA_DIR}")

fieldnames = ["directory", "file", *[key for key in rows[0] if key not in {"directory", "file"}]]
with OUTPUT_FILE.open("w", newline="") as output:
    writer = csv.DictWriter(output, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(rows)

print(f"Analyzed {len(rows)} files; results saved to {OUTPUT_FILE}")