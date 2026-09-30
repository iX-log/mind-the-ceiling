# mind-the-ceiling

*Your app gets a fixed slice of the phone. It is smaller than you think, and
it does not grow when the phone does.*
<details>

<summary><strong>TL;DR</strong></summary><br>
Before you put an AI model on an iPhone, you want to know:

- **Speed**: how fast does it actually run?
- **Memory**: how much RAM does it really use?
- **Endurance**: does it get slower the longer you run it?
- **Accuracy**: what do you lose by shrinking the model?

This repo answers all four, measured on physical hardware, across quantization
levels, using the Whisper-base encoder as the running example.
</details>


<details>
<summary><strong>Huh? ELI5, please</strong></summary>

* Your app only gets a limited amount of memory.
  * Use too much and iOS kills it.
  * Run the same AI model for long enough and it can also start slowing down.

* This project measures both on real iPhones so you know what to expect.

</details>

<details>
<summary><strong>The app</strong></summary><br>

A small SwiftUI app you build and run on a physical device. The simulator has
no Neural Engine, so latency and thermal numbers do not reproduce there.

| Button | What it does | What you get |
|---|---|---|
| **Quick (100)** | 100 inferences | Load time, model cost at load, median and p95 latency. On screen only, writes no file |
| **Sustained (10 min)** | A 600-second loop | `sustained-*.json` with every sample's latency, footprint and thermal state |
| **Memory ceiling** | Allocates 32MB blocks until iOS ends the process | `ceiling-progress.json`, fsynced after every block, because nothing survives the kill that wasn't already on disk |
| **Dump features** | Writes the encoder's output for each audio window | `.bin` files you can score for accuracy or compare across devices |

<div style="display: flex; justify-content: space-between;">
  <img src="results/screenshots/iphone17promax-quick-fp16-cold.png" width="33%">
  <img src="results/screenshots/iphone17promax-sustained-summary.png" width="33%">
</div>

</details>

<details>

<summary><strong>Run the app</strong></summary><br>

No Python needed: `fetch-models.sh` pulls the three converted models from this
repo's release and puts them where Xcode expects them.

```
git clone https://github.com/iX-log/mind-the-ceiling.git
cd mind-the-ceiling
scripts/fetch-models.sh
open ios/BenchApp/BenchApp.xcodeproj
```

Pick a physical device in Xcode and run. Airplane mode, off charger, and let
the phone cool first, or the first minute of any run measures the last thing
you did rather than this one.

</details>

<details>
<summary><strong>Reproduce the published numbers</strong></summary><br>

Converting the models yourself, scoring accuracy and regenerating the charts
needs the Python side. Every command and its expected output is in
[REPRODUCING.md](REPRODUCING.md); this is the shape of it.

1. **Convert the model** on a Mac. Traces the Whisper encoder, converts to Core ML, applies int8 and int4 quantization. Prints a numeric check against the PyTorch original.
2. **Prepare audio fixtures** from LibriSpeech test-clean, unpacked for latency and packed into 30-second windows for accuracy.
3. **Export the fixtures to raw `.bin`** for the iOS app.
4. **Copy the models into the Xcode folder**, which `fetch-models.sh` already did if you used it.
5. **Build and run on a physical device.** The simulator has no Neural Engine.
6. **Run the measurement protocol**: pick a precision and input mode, then the button you need.
7. **Pull the results off the device** with `scripts/pull-results.sh`, passing your own device UDID and bundle id.
8. **Score accuracy** from a "Dump features" run.
9. **Regenerate the charts** from the pulled JSON.

</details>

<details>
<summary><strong>What we found</strong></summary><br>

| Measurement | Result | Session |
|---|---|---|
| Memory ceiling before the process is killed | Fixed per device and does not scale with RAM: 3072 MiB on the A16 (54% of its reported 5.505 GiB), 3376 MiB on both the 8GB A18 Pro and the 12GB A19 Pro | 9, 11, 12 |
| Sustained-run behaviour | Device-specific in shape: A16 steps, A19 and A19 Pro creep, A18 Pro steps then creeps. Final drift +7% to +28%, not monotonic with generation | 8, 10, 11, 12 |
| Quantization vs. memory | The 10MB int4 model cost 66MB at cold load, against 51.8MB for the 39MB fp16 model | 12 |
| Quantization vs. accuracy | WER 3.4% (fp16), 3.8% (int8), 8.8% (int4) | 7 |
| Quantization vs. speed | int4 is 4x smaller than fp16 but only ~3% faster (likely compute-bound, not confirmed with a layer trace) | 5 |
| Load time, cold vs. warm | 1002-2083ms cold, 22-138ms warm | 1-6, 11, 12 |
| Steady-state inference | 43.0ms median, 44.2ms p95 (100 runs) | 6 |
| Low Power Mode | +56% on the A16, +94% on the A19 Pro, and 16x wider latency spread | 3, 12 |

Conditions, per-session caveats and the raw data: [RESULTS.md](RESULTS.md).
What to do about each of these: [ADVICE.md](ADVICE.md).

</details>

<details>
<summary><strong>Charts</strong></summary><br>

**The memory ceiling does not scale with RAM.** Two phones 4GB apart are cut off at the same byte.

![Horizontal bar chart comparing three iPhones. Blue bars show physical memory as each device reports it. Orange bars show the memory the app gets before it is killed: 3,221,225,472 bytes on the A16, and the identical 3,539,992,576 bytes on both the A18 Pro and the A19 Pro.](results/charts/ceiling-vs-ram.png)

**Ten minutes of steady work, seven runs, four devices.** Each run normalised to its own first minute, so the lines show slowdown rather than speed.

![Seven sustained runs normalised to each run's own first-minute median, plotted as percent slower over 600 seconds.](results/charts/cross-device-normalised.png)

**Quantization shrinks the file, not the memory.** The smallest model on disk had the largest resident cost.

![Grouped bar chart across fp16, int8 and int4 on the iPhone 17 Pro Max. Size on disk descends from 39.4 MB to 19.8 MB to 10.0 MB. Memory at first load does not follow: 51.8 MB, 34.1 MB, 66.0 MB.](results/charts/quantization-memory.png)

**int8 is close to free. int4 is not.** Half the size for 0.4 points of word error rate, then 2.6x the errors for the next halving.

![Bar chart of disk size against a line of aggregate WER across fp16, int8, and int4.](results/charts/quantization-tradeoff.png)

**Low Power Mode changes the shape of the distribution.** The spread widens about sixteen times, so a median tells you almost nothing.

![Range chart of 100 inference runs in each of two conditions on the iPhone 17 Pro Max. Normal mode spans 26.0 to 27.3 ms. Low Power Mode spans 39.5 to 60.9 ms.](results/charts/low-power-spread.png)

</details>

<details>
<summary><strong>Where to look next</strong></summary><br>

| File | What's in it |
|---|---|
| [ADVICE.md](ADVICE.md) | What each finding means for shipping code |
| [RESULTS.md](RESULTS.md) | Every session, every condition, every correction, and the scoreboard |
| [LIMITATIONS.md](LIMITATIONS.md) | What this does not establish |
| [REPRODUCING.md](REPRODUCING.md) | Setup and the full protocol |

Four devices, one model, and several findings come from a single phone. Of ten
findings published before the borrowed devices arrived, seven broke and three
held: the full list is in [LIMITATIONS.md](LIMITATIONS.md). Treat every
magnitude here as a starting point for your own measurement, not a constant.

If a number doesn't reproduce on your run, please open an issue with your
conditions and output.

</details>

<details>
<summary><strong>License</strong></summary><br>

Code is [MIT](LICENSE). Measurement data under `results/` (raw JSON, charts,
screenshots) is [CC-BY-4.0](https://creativecommons.org/licenses/by/4.0/):
cite this repo if you use the numbers.

[![License: MIT](https://img.shields.io/badge/code-MIT-blue.svg)](LICENSE)
[![Data: CC BY 4.0](https://img.shields.io/badge/data-CC--BY--4.0-lightgrey.svg)](https://creativecommons.org/licenses/by/4.0/)
[![Platform: Core ML / iOS](https://img.shields.io/badge/platform-Core%20ML%20%2F%20iOS-black.svg)](REPRODUCING.md)

</details>

<details>

<summary><strong>Author</strong></summary><br>

Ixhen Hasani, [ix-dev.com](https://ix-dev.com)

</details>
