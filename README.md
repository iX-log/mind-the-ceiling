# mind-the-ceiling

*Your app gets a fixed slice of the phone. It is smaller than you think, and
it does not grow when the phone does.*

What a Core ML model actually costs on an iPhone: memory, speed, endurance and
accuracy, measured on physical devices and published with the raw data.

[![License: MIT](https://img.shields.io/badge/code-MIT-blue.svg)](LICENSE)
[![Data: CC BY 4.0](https://img.shields.io/badge/data-CC--BY--4.0-lightgrey.svg)](https://creativecommons.org/licenses/by/4.0/)
[![Platform: Core ML / iOS](https://img.shields.io/badge/platform-Core%20ML%20%2F%20iOS-black.svg)](REPRODUCING.md)

## Explain it like I'm five

You want your app to run an AI model on the phone instead of sending data to a
server. Writing that code is the easy part. The hard part is what the phone
does to you afterwards: it hands your app a fixed slice of memory and ends the
process if you cross the line, and the same work gets slower the longer you
keep doing it.

None of that is written on the box. So this repo measures it on real phones,
one small speech model, one variable at a time, and publishes every number
with the conditions that produced it.

## The app

A small SwiftUI app you build and run on a physical device. The simulator has
no Neural Engine, so latency and thermal numbers do not reproduce there.

![The app running on an iPhone 17 Pro Max. The lower third is the whole interface: a precision picker set to fp16, a "Real input (LibriSpeech mel)" toggle, and the buttons Quick (100), Sustained (10 min), Dump features, Memory ceiling and Clear ceiling data. Above it, the output of a quick run: 1104.1 ms to load, 51.8 MB of model cost against 39.4 MB on disk, and a median of 26.2 ms over 100 inferences.](results/screenshots/iphone17promax-quick-fp16-cold.png)

| Button | What it does | What you get |
|---|---|---|
| **Quick (100)** | 100 inferences | Load time, model cost at load, median and p95 latency. On screen only, writes no file |
| **Sustained (10 min)** | A 600-second loop | `sustained-*.json` with every sample's latency, footprint and thermal state |
| **Memory ceiling** | Allocates 32MB blocks until iOS ends the process | `ceiling-progress.json`, fsynced after every block, because nothing survives the kill that wasn't already on disk |
| **Dump features** | Writes the encoder's output for each audio window | `.bin` files you can score for accuracy or compare across devices |

![The same app after a finished ten-minute run: 21,885 inferences over 600 seconds, a median of 27.5 ms, first minute 26.2 ms against last minute 28.0 ms for a drift of +1.8 ms, the thermal state moving from nominal to fair at 344.4 seconds, and the filename it wrote. Above that, the result of the last memory ceiling probe: 105 blocks allocated, 3375.7 MB of footprint, 0.3 MB left.](results/screenshots/iphone17promax-sustained-summary.png)

## Run the app

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

<details>
<summary><b>Reproduce the published numbers</b>: nine steps, and a Python environment</summary>

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
<summary><b>What we found</b>: eight measurements, and the session each came from</summary>

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
<summary><b>Charts</b>: five figures, all regenerated from the committed data</summary>

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

## Where to look next

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

## License

Code is [MIT](LICENSE). Measurement data under `results/` (raw JSON, charts,
screenshots) is [CC-BY-4.0](https://creativecommons.org/licenses/by/4.0/):
cite this repo if you use the numbers.

## Author

Ixhen Hasani, [ix-dev.com](https://ix-dev.com)
