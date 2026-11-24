import csv
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from Trilling.quick_calc import calc


SCRIPT_DIR = Path(__file__).resolve().parent
DATA_DIR = SCRIPT_DIR / "Trilling"
DATA_SERIES = [
    (Path("degelijke metingen (no AI)/sweep"), "Low mass - sweep"),
    (Path("degelijke metingen (no AI)/finetune lage massa"), "Low mass - resonance fine-tuning"),
    (Path("heavy metingen/rond res freq"), "Heavy mass - resonance measurements"),
    (Path("heavy metingen/sweeps"), "Heavy mass - sweep"),
]
OUTPUT_FILE = SCRIPT_DIR / "analysis_results.csv"
PLOT_FILE = SCRIPT_DIR / "amplitude_response.png"

rows = []
for relative_dir, series in DATA_SERIES:
    directory = DATA_DIR / relative_dir
    for filename in sorted(directory.glob("*.cylinder")):
        measurements = calc(filename)
        if measurements["wh_period"] is None:
            print(f"Warning: no complete wheel period detected in {filename}")
        rows.append({
            "directory": relative_dir.as_posix(),
            "series": series,
            "file": filename.name,
            **measurements,
        })

if not rows:
    raise FileNotFoundError(f"No .cylinder files found in {DATA_DIR}")

fieldnames = ["directory", "file", *[
    key for key in rows[0] if key not in {"directory", "series", "file"}
]]
with OUTPUT_FILE.open("w", newline="") as output:
    writer = csv.DictWriter(output, fieldnames=fieldnames, extrasaction="ignore")
    writer.writeheader()
    writer.writerows(rows)

fig, ax = plt.subplots(figsize=(9, 6))
for _, series in DATA_SERIES:
    points = sorted(
        (row for row in rows if row["series"] == series and row["wh_freq"] is not None),
        key=lambda row: row["wh_freq"],
    )
    if not points:
        continue
    ax.errorbar(
        [row["wh_freq"] for row in points],
        [row["amp"] for row in points],
        yerr=[row["amp_sdev"] for row in points],
        fmt="o-",
        markersize=3,
        capsize=2,
        linewidth=1,
        label=series,
    )

ax.set(
    title="Driven oscillator amplitude response",
    xlabel="Driving frequency [Hz]",
    ylabel="Oscillation amplitude [cm]",
)
ax.grid(True, alpha=0.3)
ax.legend()
fig.tight_layout()
fig.savefig(PLOT_FILE, dpi=200)
plt.close(fig)

print(f"Analyzed {len(rows)} files; results saved to {OUTPUT_FILE}")
print(f"Amplitude-response plot saved to {PLOT_FILE}")