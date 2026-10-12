# Soft-to-Rigid — Unofficial 2D Packing Launcher

An independent command-line companion for [Yohei Nakajima's **soft-to-rigid**](https://github.com/yoheinakajima/soft-to-rigid). Choose a 2D packing family, piece count, algorithm, random seed, and number of trials. The Python script calls the **original Node.js research engine** and produces a local, self-contained HTML replay of its best run.

This is a separate utility from the `soft-to-rigid-packing` (3D cube) launcher.

## Features

- Seven 2D families from the upstream catalog (see table below).
- Five upstream search methods: `harden`, `grow`, `rigid`, `sa`, `pc`.
- Optional 32-bit random seeds (`--random-seed`, **off by default**).
- Multiple trials (`--trials`) with printed results and a best-run replay.
- Embedded, offline-viewable HTML canvas playback with play/pause and a timeline. No Python packages, CDN, or HTTP server needed for the viewer.
- Creates isolated experiment directories without touching published upstream campaign data.

## Requirements

- Python 3.10 or later
- Node.js available on `PATH`
- A checkout of the **different** upstream repository: <https://github.com/yoheinakajima/soft-to-rigid>
- A modern browser for the generated 2D replay

This package does **not** bundle or replace the upstream algorithm. No `pip install` is required for the Python launcher. The upstream research pipeline has additional Python dependencies for its own analysis, which are not required for this launcher.

## Install

1. Clone or download the upstream repository:

   ```bash
   git clone https://github.com/yoheinakajima/soft-to-rigid.git
   cd soft-to-rigid
   ```

2. Copy `packing2d_launcher.py` from this package to the root of that repository, next to `engine/`, `catalog/`, `methods/`, and `campaigns/`.
3. Check Node.js and Python with `node --version` and `python --version`.

Alternatively, run the script from another directory with `--repo PATH_TO_SOFT_TO_RIGID`.

## Quick start

```bash
python packing2d_launcher.py --family squ-in-squ --n 11 --seed 17
```

Try random seeds:

```bash
python packing2d_launcher.py --family squ-in-squ --n 11 --random-seed
```

Run 10 different seeds, showing the best replay:

```bash
python packing2d_launcher.py --family squ-in-squ --n 11 --trials 10 --random-seed
```

Try triangles and another search method:

```bash
python packing2d_launcher.py --family tri-in-squ --n 12 --method rigid --budget 2
```

## Supported 2D families

| Family code | Pieces | Container |
| --- | --- | --- |
| `squ-in-squ` | Unit squares | Square |
| `squ-in-cir` | Unit squares | Circle |
| `squ-in-tri` | Unit squares | Equilateral triangle |
| `tri-in-tri` | Equilateral triangles | Equilateral triangle |
| `tri-in-squ` | Equilateral triangles | Square |
| `hex-in-squ` | Regular hexagons | Square |
| `cir-in-squ` | Unit-diameter circles | Square |

These are the seven primary families in the upstream research comparison. This launcher does **not** claim to support arbitrary shapes or 3D cubes.

## Options

| Option | Default | Purpose |
| --- | --- | --- |
| `--family` | `squ-in-squ` | 2D family from table |
| `--n` | `11` | Number of pieces |
| `--method` | `harden` | Upstream method (`harden`, `grow`, `rigid`, `sa`, `pc`) |
| `--budget` | `1` | Upstream relative computation budget (positive) |
| `--seed` | `17` | Fixed 32-bit seed |
| `--random-seed` | Off | Generate random seed(s), overriding `--seed` |
| `--trials` | `1` | Number of distinct seeds to run |
| `--repo` | Script directory | Path to the upstream checkout |
| `--no-browser` | Off | Save replay without opening it |

Run `python packing2d_launcher.py --help` for CLI help.

**Note:** `--budget` is a multiplier in the upstream engine; it is **not** the `--compact`/`--morph`/`--settle` interface of the earlier cube launcher. Fixed-seed trials increment the supplied seed; random-seed trials use independently generated seeds.

## Output

Each invocation creates a new `campaigns/launcher2d-YYYYMMDD-HHMMSS-XXXXXXXX/` directory in the upstream checkout, containing:

```text
plan.json            # generated upstream campaign plan
runs-w0.jsonl        # one JSON line per completed trial
replays/*.json       # upstream's best-run replay data
replay.html          # self-contained, browser-viewable 2D animation
```

The official `engine/run.js` does the computation and records the best replay. The launcher prints each trial's measured `L` and the best seed. `L` is the enclosing square/triangle **side length** or enclosing circle **radius**, according to family. The displayed frame geometry is an illustrative local browser rendering of upstream replay values, not an independent geometric validator.

For large `n`, large budgets, or numerous trials, runs can take considerable time and consume disk space. Old launcher-specific experiment directories are intentionally **not** deleted automatically. You may remove your own `campaigns/launcher2d-*` directories when you no longer need them.

## Troubleshooting

- **`engine/run.js not found`**: Copy the script into the root of **`soft-to-rigid`**, not `soft-to-rigid-packing`, or supply `--repo`.
- **Node.js missing**: Install Node.js and restart the terminal.
- **A trial fails**: See the printed error and the run directory's `runs-w0.jsonl`. Some parameter combinations may be computationally impractical.
- **No animation opens**: Manually open the generated `replay.html`. Pass `--no-browser` if preferred.
- **Unexpected result**: Numerical packing is stochastic; repeat with another seed or a larger budget. A small `L` alone does not prove optimality.

## Credits and AI disclosure

The original [soft-to-rigid](https://github.com/yoheinakajima/soft-to-rigid) project, its simulation code, experiments, and scientific results belong to their respective rights holders. The original project credits Yohei Nakajima and notes development with Claude under the author's direction.

**`packing2d_launcher.py` and both README documents in this companion package were generated by OpenAI's ChatGPT under human direction.** This is an unofficial independent companion; it is not endorsed by Yohei Nakajima, the original project, or OpenAI.

## License

The upstream project is published under the MIT License; see its own `LICENSE` file. That license applies to its code, which this package does not redistribute. The standalone launcher is supplied here without a separate explicit license grant. Before publishing your own launcher repository and inviting third-party reuse, choose a license for your own code and include its full text. Review the rights of any assets you redistribute.

## Replay improvements (v2)

- The viewer interpolates positions, rotations, and scale between recorded samples for smoother ~60 FPS playback. **This does not create additional simulation samples**; the upstream engine still determines the recorded frame count.
- During the harden/compress stage, if a frame has no usable positions, the viewer displays the closest available valid state instead of a blank canvas. Early stage visuals may therefore be approximations rather than the exact simulation state.

## Clean generated runs

```bash
python packing2d_launcher.py --clean
python packing2d_launcher.py --clean --clean-days 7
```

`--clean` deletes only `campaigns/launcher2d-*` directories whose `plan.json` identifies them as launcher-generated. It does not remove upstream campaigns. Cleaning deletes stored results and replay HTML files, so back up important results first.

## v3: harden/compress visibility

The viewer now clamps the display-only shape scale during harden/compress. This addresses frames where the upstream scale reaches zero even though positions are present. The displayed shapes in this stage are illustrative, not exact geometry; computed results are unchanged.

## v4: compress visibility fix

In the fully softened (`u=1`) compress phase, polygons collapse to a zero-length centerline. A thick Canvas stroke on that degenerate path draws nothing. The viewer now renders the corresponding circle explicitly. Simulation values remain unchanged.
