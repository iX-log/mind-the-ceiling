# What to do about it in your own app

Eight things the measurements in [RESULTS.md](RESULTS.md) imply for shipping
code. Every magnitude comes from four iPhones and one model, so read them as
things to check on your own hardware rather than as constants. What each one
rests on is in [LIMITATIONS.md](LIMITATIONS.md).

## Memory

**Budget with `os_proc_available_memory()`, and don't assume a bigger phone
helps.** The call returns a fixed per-device limit minus your current
footprint, arithmetically, not an estimate, so you can budget against it
precisely. But the limit does not scale with RAM: an 8GB iPhone 16 Pro and a
12GB iPhone 17 Pro Max both return 3,539,992,576 bytes. Crossing it ends the
process.

**Measure footprint, never infer it from file size.** On the one device where
all three precisions were cold-loaded, the 10MB int4 model cost 66MB of
footprint against the 39MB fp16 model's 51.8MB. Palettized weights expand at
load, so quantization compresses the download and not the resident cost.

## Loading

**Load the model at launch, before anyone is waiting.** Cold loads ran 1002 to
2083ms across sessions 1 to 6, 11 and 12. A load with the file already in the
page cache ran 22 to 138ms.

## Precision

**Use int8, not int4.** Half the size for 0.4 points of word error rate. int4
halves it again for 2.6x the errors, and costs more memory at load rather than
less. int4 bought about 3% on latency, which is the one thing it does buy.

## Sustained work

**Expect slowdown, and measure the device you ship to.** Four devices produced
three different shapes: the A16 holds flat then steps, the A19 and A19 Pro
creep smoothly, the A18 Pro does both in sequence. Final drift ran +7% to +28%
and did not improve with chip generation.

**Cool the device before you benchmark.** Same phone, same protocol: +12.1%
drift from a cooled start against +46.1% warm. That is a bigger swing than two
chip generations.

**Don't trigger behaviour on `thermalState`.** Across seven sustained runs the
reported transition landed anywhere from 147 seconds before the slowdown to 45
seconds after it, with no pattern by device or by state. It is not
consistently early or consistently late, which rules it out as a trigger in
either direction.

## Low Power Mode

**Treat it as a different distribution, not a slower one.** It cost +94% on the
A19 Pro against +56% on the A16, and widened the latency spread from 1.3ms to
21.4ms. A median tells you almost nothing under it, so budget from p95 and max.
Under Low Power Mode a 2026 phone ran slower than a 2022 phone at full speed.
