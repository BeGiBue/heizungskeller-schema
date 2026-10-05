#!/usr/bin/env python3
"""Rendert die Karte mit Testdaten (kein echtes Home Assistant) und speichert Screenshots.

Beispiele:
  python3 tools/harness.py --all                       # breit + kompakt (zu/auf) nach tools/out/
  python3 tools/harness.py --width 390 --topic gas --out tools/out/gas.png
  python3 tools/harness.py --docs                      # Vorschaubilder für docs/ neu erzeugen

Benötigt: pip install playwright pillow  und  playwright install chromium
"""
import argparse
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CARD = os.path.join(ROOT, "dist", "heizungsanlage-card.js")

# Testzustände (Einheit, Wert) passend zu den Standard-Entitäten der Karte
STATES = {
    "sensor.vicare_outside_temperature": ("12.7", "°C"),
    "binary_sensor.vicare_frost_protection_active": ("off", ""),
    "sensor.vicare_burner_hours": ("21436", "h"),
    "sensor.vicare_burner_starts": ("99126", ""),
    "binary_sensor.vicare_burner_active": ("on", ""),
    "sensor.vicare_burner_modulation": ("45", "%"),
    "sensor.vicare_boiler_temperature": ("58", "°C"),
    "sensor.vicare_supply_temperature": ("52.3", "°C"),
    "binary_sensor.vicare_circulation_pump_active": ("on", ""),
    "binary_sensor.vicare_dhw_pump_active": ("on", ""),
    "binary_sensor.vicare_dhw_circulation_pump_active": ("off", ""),
    "sensor.vscotho1_72_ww_speichertemperatur": ("44.1", "°C"),
    "number.vscotho1_72_warmwassertemperatur": ("53", "°C"),
    "number.vscotho1_72_komforttemperatur": ("24", "°C"),
    "number.vscotho1_72_normaltemperatur": ("20", "°C"),
    "number.vscotho1_72_reduzierte_temperatur": ("18", "°C"),
    "number.vscotho1_72_steigung_der_heizkurve": ("1.1", ""),
    "number.vscotho1_72_verschiebung_der_heizkurve": ("0", "°C"),
    "sensor.wasserzahler_flow": ("0.012", "m³/h"),   # wie beim Nutzer: Durchfluss in m³/h
    "sensor.wasserzahler_total": ("539954", "L"),    # Stand in Litern
    "sensor.wasserzahler_water_temperature": ("12.4", "°C"),
    "sensor.vicare_hot_water_min_temperature": ("45", "°C"),
    "sensor.vicare_hot_water_max_temperature": ("60", "°C"),
    "sensor.gas_zaehler": ("5236.26", "m³"),
}

# Mock für hass.callWS: Energie-Dashboard, Statistiken und 24-h-Verläufe
MOCK_JS = """
([states, config, topic]) => {
  const c = document.createElement('heizungsanlage-card');
  c.setConfig(config);
  document.body.appendChild(c);
  c.hass = {
    states, language: 'de',
    callWS: async (m) => {
      if (m.type === 'energy/get_prefs') return {
        energy_sources: [{type: 'gas', stat_energy_from: 'sensor.gas_zaehler'}],
        device_consumption_water: [{stat_consumption: 'sensor.wasserzahler_total'}]};
      if (m.type === 'recorder/statistics_during_period') return {[m.statistic_ids[0]]: m.statistic_ids[0].includes('wasser') ? [{change: 100}, {change: 77}] : [{change: 1.8}, {change: 0.9}]};
      if (m.type === 'recorder/get_statistics_metadata') return [{display_unit_of_measurement: m.statistic_ids[0].includes('wasser') ? 'L' : 'm³'}];
      const now = Date.now() / 1000, out = {};
      m.entity_ids.forEach((id) => {
        out[id] = Array.from({length: 144}, (_, i) => {
          let v;
          if (id.includes('modulation')) v = (i % 36 < 14) ? 20 + (i % 36) * 4 : 0;
          else if (id.includes('boiler')) v = 45 + (i % 36 < 14 ? (i % 36) * 1.6 : Math.max(0, 22 - (i % 36 - 14)) * .9);
          else v = 40 + 8 * Math.sin(i / 9) + (i % 30) / 10;
          return {lu: now - (143 - i) * 600, s: String(v)};
        });
      });
      return out;
    }};
  window.__card = c;
}
"""


def render(width, out, topic="", config=None, scale=2, pw=None, height=None):
    from playwright.sync_api import sync_playwright

    states = {k: {"state": v[0], "attributes": {"unit_of_measurement": v[1]}} for k, v in STATES.items()}
    js = open(CARD, encoding="utf8").read()
    html = (
        f'<html><body style="margin:0;background:#fff;width:{width}px;--primary-text-color:#212121;'
        "--secondary-text-color:#727272;--divider-color:#ddd;--secondary-background-color:#f4f6f8;"
        '--card-background-color:#fff"></body></html>'
    )
    with sync_playwright() as p:
        b = p.chromium.launch()
        pg = b.new_page(viewport={"width": int(width), "height": int(height or 900)}, device_scale_factor=scale)
        pg.on("pageerror", lambda e: print("PAGEERROR", str(e)[:400], file=sys.stderr))
        pg.set_content(html)
        pg.add_script_tag(content=js)
        pg.evaluate(MOCK_JS, [states, config or {}, topic])
        pg.wait_for_timeout(700)
        if topic:
            pg.evaluate(
                "(t)=>{const el=window.__card.shadowRoot.querySelector('[data-topic=\"'+t+'\"]');"
                "if(!el) throw new Error('Thema nicht gefunden: '+t); el.dispatchEvent(new Event('click'));}",
                topic,
            )
            pg.wait_for_timeout(500)
        info = pg.evaluate(
            "()=>{const s=window.__card.shadowRoot.querySelector('svg');return s.getAttribute('class')+' '+s.getAttribute('viewBox')}"
        )
        os.makedirs(os.path.dirname(os.path.abspath(out)), exist_ok=True)
        pg.screenshot(path=out, full_page=height is None)  # mit --height nur der sichtbare Bereich
        b.close()
    print(f"{out}  ({info})")


def trim(path):
    """Weißen Rand unten/rechts abschneiden."""
    from PIL import Image, ImageChops

    im = Image.open(path).convert("RGB")
    bb = ImageChops.difference(im, Image.new("RGB", im.size, (255, 255, 255))).getbbox()
    if bb:
        im.crop((max(bb[0] - 8, 0), max(bb[1] - 8, 0), min(bb[2] + 8, im.width), min(bb[3] + 8, im.height))).save(path, optimize=True)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--width", type=int, default=1400)
    ap.add_argument("--height", type=int, default=None, help="Fensterhöhe in px; dann nur der sichtbare Bereich (zeigt, ob die Karte ohne Scrollen passt)")
    ap.add_argument("--topic", default="", help="kompakte Ansicht: Bereich aufklappen (diagrams, gas, water, softener, settings, status, burner)")
    ap.add_argument("--out", default=os.path.join(ROOT, "tools", "out", "vorschau.png"))
    ap.add_argument("--layout", default="auto", choices=["auto", "wide", "compact"])
    ap.add_argument("--all", action="store_true", help="breit, kompakt und kompakt mit Diagrammen nach tools/out/")
    ap.add_argument("--docs", action="store_true", help="Vorschaubilder für docs/ erzeugen")
    a = ap.parse_args()
    out = os.path.join(ROOT, "tools", "out")
    if a.all:
        render(1400, f"{out}/breit.png", scale=1)
        render(390, f"{out}/kompakt.png")
        render(390, f"{out}/kompakt-diagramme.png", topic="diagrams")
    elif a.docs:
        d = os.path.join(ROOT, "docs")
        render(1400, f"{d}/vorschau.png", scale=1)
        trim(f"{d}/vorschau.png")
        render(390, f"{out}/_k0.png")
        render(390, f"{out}/_k1.png", topic="diagrams")
        from PIL import Image

        ims = []
        for n in ("_k0", "_k1"):
            trim(f"{out}/{n}.png")
            ims.append(Image.open(f"{out}/{n}.png"))
        h = max(i.height for i in ims)
        comp = Image.new("RGB", (sum(i.width for i in ims) + 30, h), (205, 212, 222))
        comp.paste(ims[0], (0, 0))
        comp.paste(ims[1], (ims[0].width + 30, 0))
        comp.save(f"{d}/vorschau-kompakt.png", optimize=True)
        print(f"{d}/vorschau-kompakt.png")
    else:
        cfg = {} if a.layout == "auto" else {"layout": a.layout}
        render(a.width, a.out, a.topic, cfg, height=a.height)


if __name__ == "__main__":
    main()
