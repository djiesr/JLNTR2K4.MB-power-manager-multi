# Catroniq - Power Manager multiboard

ESPHome firmware for the Catroniq multiboard energy monitor: an ESP32 main board with 2 CT clamp inputs, plus up to 5 MCP3008 extension boards of 8 inputs each (2, 10, 18, 26, 34 or 42 circuits).

Install page: https://djiesr.github.io/JLNTR2K4.MB-power-manager-multi/

## Files

| File | Circuits |
|---|---|
| `power-manager-multi-02.yaml` | 2 (main board only) |
| `power-manager-multi-10.yaml` | 10 (1 extension board) |
| `power-manager-multi-18.yaml` | 18 |
| `power-manager-multi-26.yaml` | 26 |
| `power-manager-multi-34.yaml` | 34 |
| `power-manager-multi-42.yaml` | 42 (5 extension boards) |

**These files are generated.** Edit `tools/generate.py`, then run:

```
python tools/generate.py
```

Circuits are named after the connectors printed on the boards: A1-A2 on the main board, B0-B7 on the 1st extension board, C0-C7 on the 2nd, up to F0-F7. Internal ids keep the circuit number (`c01` = A1, `c03` = B0...).

Every circuit is generated identically in every size (same ids, names and sub-device), so moving a board to a bigger size keeps the CT settings, daily totals and Home Assistant history of the existing circuits. Keep it that way when editing the generator.

Pushing to `main` builds the six firmwares and publishes the install page on GitHub Pages. Devices check that page for updates every 6 hours; bump `VERSION` in `tools/generate.py` to publish an update.
