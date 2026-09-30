# Limitations

What this repo does not establish, stated up front so you can decide how much
weight to put on any number in it.

- **Core ML only, encoder only.** No comparison to ONNX Runtime, TFLite, or whisper.cpp, and no end-to-end on-device transcription number: the decoder ran on a Mac CPU throughout.
- **Four devices, one model.** A16, A18 Pro, A19 and A19 Pro, all iPhones, one ~20M-parameter model. Unit-to-unit variance within a model, iPads, other architectures and larger-model behaviour are all unmeasured. There is no A17 and nothing below an A16.
- **Three of the four phones cannot be re-run on demand.** Only the A16 is a device I own. Two were borrowed for a single afternoon, and the A19 is a tester's phone that was never in my hands.
- **Coverage is uneven across findings.** Low Power Mode is measured on two of the four devices, and the cold-load footprint figures on one.
- **Most figures are a single session's output**, not repeat-checked for run-to-run variance. The sustained runs on the A18 Pro and the A19 Pro are n=1 each.
- **Not every figure has a distribution behind it.** Raw per-run data is committed for the seven sustained runs (sessions 3, 4, 10, 11, 12) and for four memory-ceiling probes (sessions 9, 11, 12). Quick-test runs write no file, so sessions 1, 2, 5, 6 and the precision and Low Power Mode tables in sessions 11 and 12 are evidenced by screenshots in `results/screenshots/` instead.
- **Only one of the four encoder feature dump sets is committed.** The other three (the A18 Pro, the A19 Pro and the A16 re-measurement) are held out of git at 62MB each. The cross-device and cross-OS comparisons in session 12 are reproducible from the one committed set plus a re-run on your own hardware, not from files in this repo.
- **The iOS-version finding is a natural experiment, not a controlled one.** Four dump sets split cleanly along OS version with no other variable separating them, but nobody changed the OS on a single handset and re-measured.

## How the earlier findings fared

Ten findings were published here before the borrowed devices arrived. Seven
broke and three held. [RESULTS.md](RESULTS.md) carries the scoreboard, row by
row, alongside the sessions that produced each one and the corrections that
followed.

That is the reason to treat every magnitude here as a starting point for your
own measurement rather than as a constant.

## If it doesn't reproduce

If a number doesn't reproduce on your own run, or you run this on hardware
that isn't listed above, please open an issue with your conditions and your
output. Conditions matter more than you would expect: see
[REPRODUCING.md](REPRODUCING.md) for the protocol these numbers were taken
under.
