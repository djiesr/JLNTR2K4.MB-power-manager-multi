"""Generate the ESPHome configs for every multiboard size.

    python tools/generate.py

Do not edit the generated power-manager-multi-XX.yaml files by hand: edit this
script and run it again.

Every channel is generated the same way in every size (same ids, names and
sub-device). This is what keeps a channel's CT settings, daily totals and Home
Assistant history when a board is moved from one size to a bigger one.
"""

from pathlib import Path

VERSION = "8.0.0"
REPO = "djiesr/JLNTR2K4.MB-power-manager-multi"
PAGES_URL = "https://djiesr.github.io/JLNTR2K4.MB-power-manager-multi"

# Channels 1-2 are on the main board, then 8 per MCP3008 extension board
ONBOARD_PINS = ["GPIO34", "GPIO35"]
EXTENSION_CS_PINS = ["GPIO13", "GPIO15", "D8", "GPIO32", "GPIO33"]
SIZES = [2 + 8 * n for n in range(len(EXTENSION_CS_PINS) + 1)]  # 2, 10, ..., 42

ROOT = Path(__file__).resolve().parent.parent


def stem(size):
    return f"power-manager-multi-{size:02d}"


def header(size):
    labels = "".join(f"  ct_clamp_{c:02d}: 'C{c:02d}'\n" for c in range(1, size + 1))
    devices = "".join(
        f'    - id: dev_c{c:02d}\n      name: "$hostname $ct_clamp_{c:02d}"\n' for c in range(1, size + 1))
    return f"""# GENERATED FILE - edit tools/generate.py and run it again.
# Catroniq - Power Manager multiboard, {size} circuits

# These substitutions allow the end user to override certain values
substitutions:
  name: "power-manager-multi"
  # Modify variables if you use multiple boards
  hostname: 'PM'
  board_label: 'JLNTR2K4.MB'
  # Modify variables based on your circuit, like "breaker 01" or "dryer"
{labels}  # Modify variable based on your language
  measured_current: 'Measured Current'
  measured_power: 'Measured Power'
  measured_total_power_daily: 'Measured Daily Total'
  total_power: 'Total Power'
  total_daily_energy: 'Total Daily Energy'
  ct_model: 'CT Model'
  ct_output: 'CT Output'
  ct_none: 'None'
  circuit_voltage: 'Circuit Voltage'
  ct_correction: 'CT Correction'

esphome:
  name: "${{name}}"
  # One Home Assistant device per circuit (sensors + CT settings)
  devices:
{devices}  # Automatically add the mac address to the name
  # so you can use a single firmware for all devices
  name_add_mac_suffix: true
  project:
    name: esphome.power-manager-multi
    version: "{VERSION}"

esp32:
  board: wemos_d1_mini32
  framework:
    type: esp-idf

logger:

api:

ota:
  - platform: esphome
  # Lets the device install the firmware published on GitHub Pages
  - platform: http_request

http_request:
  verify_ssl: true

# Home Assistant shows "Update available" when a new version is published
update:
  - platform: http_request
    name: Firmware
    source: {PAGES_URL}/{stem(size)}/manifest.json
    update_interval: 6h

dashboard_import:
  package_import_url: github://{REPO}/{stem(size)}.yaml@main

wifi:
  ap:
    password: "12345678"

captive_portal:

# Wi-Fi setup over USB from the install page. Bluetooth improv (esp32_improv)
# is left out: it keeps ~50 KB of RAM busy, needed for HTTPS updates on big boards.
improv_serial:

# Free memory, to check there is room for HTTPS updates
debug:
  update_interval: 60s

web_server:
  port: 80
  version: 2

time:
  - platform: sntp
    id: my_time

text_sensor:
  - platform: wifi_info
    ip_address:
      name: $hostname ESP IP Address
      id: ip_now
      entity_category: diagnostic
      disabled_by_default: true
    ssid:
      name: $hostname ESP Connected SSID
      entity_category: diagnostic
      disabled_by_default: true
    mac_address:
      name: $hostname ESP Mac Wifi Address
      entity_category: diagnostic
      disabled_by_default: true
"""


def hardware(size):
    boards = (size - 2) // 8
    out = ""
    if boards:
        out += """
spi:
  clk_pin: D5
  mosi_pin: D7
  miso_pin: D6

# One MCP3008 per extension board
mcp3008:
"""
        out += "".join(
            f"  - cs_pin: {EXTENSION_CS_PINS[b]}\n    id: main_board_{b + 1}\n" for b in range(boards))
    return out


def source_sensor(c):
    if c <= len(ONBOARD_PINS):
        return f"""  - platform: adc
    pin: {ONBOARD_PINS[c - 1]}
    id: adc_c{c:02d}
    attenuation: 12db
    update_interval: 60s
    internal: true
"""
    board, pin = divmod(c - len(ONBOARD_PINS) - 1, 8)
    return f"""  - platform: mcp3008
    mcp3008_id: main_board_{board + 1}
    number: {pin}
    id: adc_c{c:02d}
    update_interval: 60s
    internal: true
"""


def channel_sensors(c):
    n = f"{c:02d}"
    return source_sensor(c) + f"""
  - platform: ct_clamp
    sensor: adc_c{n}
    id: measured_current_c{n}
    name: $measured_current
    device_id: dev_c{n}
    update_interval: 15s
    accuracy_decimals: 3
    filters:
      - lambda: |-
          static const float RATING[] = {{0, 5, 10, 15, 20, 30, 50, 100}};
          static const float OUT_V[] = {{1.0, 0.5, 0.333}};
          float rating = RATING[id(ct_model_c{n}).active_index().value_or(0)];
          float out_v = OUT_V[id(ct_output_c{n}).active_index().value_or(0)];
          if (rating == 0 || x <= 0.003f) return 0.0f;
          return (x - 0.003f) * rating / (out_v - 0.003f) * id(ct_correction_c{n}).state / 100.0f;

  - platform: template
    id: power_c{n}
    name: $measured_power
    device_id: dev_c{n}
    unit_of_measurement: 'kW'
    device_class: power
    state_class: measurement
    update_interval: 15s
    accuracy_decimals: 3
    lambda: |-
      if (id(measured_current_c{n}).state > 0.03) {{
        static const float VOLTS[] = {{120.0f, 240.0f, 230.0f}};
        float volts = VOLTS[id(circuit_voltage_c{n}).active_index().value_or(0)];
        return id(measured_current_c{n}).state * volts / 1000;
      }}
      return 0.0;

  - platform: total_daily_energy
    id: tde_c{n}
    name: $measured_total_power_daily
    device_id: dev_c{n}
    power_id: power_c{n}
    device_class: energy
    restore: true

"""


def totals(size):
    ids = ", ".join(f"id(power_c{c:02d})" for c in range(1, size + 1))
    return f"""  # Whole board
  - platform: template
    id: power_total
    name: $hostname $total_power
    unit_of_measurement: 'kW'
    device_class: power
    state_class: measurement
    update_interval: 15s
    accuracy_decimals: 3
    lambda: |-
      float total = 0;
      for (auto *s : {{{ids}}}) {{
        if (!std::isnan(s->state)) total += s->state;
      }}
      return total;

  - platform: total_daily_energy
    id: tde_total
    name: $hostname $total_daily_energy
    power_id: power_total
    device_class: energy
    restore: true
"""


def settings(size):
    selects, numbers = "", ""
    for c in range(1, size + 1):
        n = f"{c:02d}"
        common = f"""    device_id: dev_c{n}
    entity_category: config
    optimistic: true
    restore_value: true
"""
        selects += f"""  - platform: template
    id: ct_model_c{n}
    name: $ct_model
{common}    options: ["$ct_none", "5 A", "10 A", "15 A", "20 A", "30 A", "50 A", "100 A"]
    initial_option: "$ct_none"

  - platform: template
    id: ct_output_c{n}
    name: $ct_output
{common}    options: ["1 V", "0.5 V", "0.333 V"]
    initial_option: "1 V"

  # 230 V is last: the select saves its index, keep existing choices valid
  - platform: template
    id: circuit_voltage_c{n}
    name: $circuit_voltage
{common}    options: ["120 V", "240 V", "230 V"]
    initial_option: "120 V"

"""
        numbers += f"""  - platform: template
    id: ct_correction_c{n}
    name: $ct_correction
{common}    initial_value: 100
    min_value: 50
    max_value: 150
    step: 0.1
    unit_of_measurement: "%"
    mode: box

"""
    return (
        "\n########################################################## CT Clamp configuration (editable in HA) ##########################################\n\n"
        "select:\n" + selects + "number:\n" + numbers)


def display(size):
    pages = f"""      - id: page_info
        lambda: |-
          it.print(0, 0, id(font_title), "Power Manager");
          it.print(0, 16, id(font_small), "${{board_label}} - {size} c.");
          it.printf(0, 32, id(font_small), "IP %s", id(ip_now).state.c_str());
          it.printf(0, 48, id(font_small), "Tot %6.0f W", id(power_total).state * 1000);
"""
    for first in range(1, size + 1, 4):
        chans = list(range(first, min(first + 4, size + 1)))
        cur = ", ".join(f"id(measured_current_c{c:02d})" for c in chans)
        pwr = ", ".join(f"id(power_c{c:02d})" for c in chans)
        pages += f"""      - id: page_c{first:02d}
        lambda: |-
          sensor::Sensor *cur[] = {{{cur}}};
          sensor::Sensor *pwr[] = {{{pwr}}};
          for (int i = 0; i < {len(chans)}; i++)
            it.printf(0, i * 16, id(font_small), "C%02d %5.1fA %5.0fW", {first} + i, cur[i]->state, pwr[i]->state * 1000);
"""
    return f"""
# Screen
i2c:
  scl: D1
  sda: D2
  scan: false

font:
  - file: "gfonts://Roboto"
    id: font_title
    size: 14
  - file: "gfonts://Roboto Mono"
    id: font_small
    size: 12

interval:
  - interval: 5s
    then:
      - display.page.show_next: oled

display:
  - platform: ssd1306_i2c
    id: oled
    model: "SSD1306 128x64"
    reset_pin: D0
    address: 0x3C
    update_interval: 1s
    pages:
{pages}"""


def build(size):
    s = header(size) + hardware(size) + """
sensor:
  - platform: debug
    free:
      name: $hostname Free Memory
      entity_category: diagnostic
      disabled_by_default: true
    block:
      name: $hostname Largest Free Block
      entity_category: diagnostic
      disabled_by_default: true

"""
    for c in range(1, size + 1):
        s += f"  ###### Circuit C{c:02d} ######\n" + channel_sensors(c)
    s += totals(size) + settings(size) + display(size)
    return s


if __name__ == "__main__":
    for size in SIZES:
        path = ROOT / f"{stem(size)}.yaml"
        path.write_text(build(size), encoding="utf-8", newline="\n")
        print(path.name)
