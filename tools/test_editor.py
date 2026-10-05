#!/usr/bin/env python3
"""Prüft Editor und beide Layouts im Headless-Browser (mit Platzhalter für <ha-form>).

Aufruf:  python3 tools/test_editor.py      (Exit-Code 1 bei Fehlern)
"""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from harness import CARD, STATES  # noqa: E402

TEST_JS = """
async () => {
  const out = {};
  const Card = customElements.get('heizungsanlage-card');
  const ed = Card.getConfigElement();
  document.body.appendChild(ed);
  ed.hass = {language: 'de', states: {}};
  ed.setConfig({type: 'custom:heizungsanlage-card', entities: {water_temp: null}, layout: 'compact'});
  await new Promise((r) => setTimeout(r, 50));
  const f = ed._form;
  out.hasForm = !!f;
  out.sections = f.schema.length;
  out.fields = f.schema.flatMap((s) => s.schema).length;
  out.waterTempCleared = f.data.e_water_temp === '';
  out.layoutInForm = f.data.layout;
  out.labelDe = f.computeLabel({name: 'e_boiler_temp'});
  let got = null;
  ed.addEventListener('config-changed', (e) => (got = e.detail.config));
  f.dispatchEvent(new CustomEvent('value-changed', {detail: {value: {...f.data, title: 'X', e_burner_active: 'binary_sensor.x', e_gas_total: 'sensor.g', layout: 'wide', e_water_temp: ''}}}));
  out.changed = got;
  f.dispatchEvent(new CustomEvent('value-changed', {detail: {value: ed._toData({})}}));
  out.lean = got;
  ed.hass = {language: 'en-GB', states: {}};
  out.labelEn = ed._form.computeLabel({name: 'e_boiler_temp'});
  return out;
}
"""

LAYOUT_JS = """
([states, layout, width]) => {
  document.body.style.width = width + 'px';
  const c = document.createElement('heizungsanlage-card');
  c.setConfig(layout === 'auto' ? {} : {layout});
  document.body.appendChild(c);
  c.hass = {states, language: 'de', callWS: async () => ({})};
  const r = c.shadowRoot;
  const has = (id) => !!r.getElementById(id);
  return {
    cls: r.querySelector('svg').getAttribute('class'),
    ids: ['boiler', 'tank-hot', 'pm-heat', 'pm-chg', 'pm-circ', 'ln-heat-f', 'ln-cold', 'flame', 'v-supply', 'v-tank', 'v-cold'].filter((i) => !has(i)),
    topics: r.querySelectorAll('.btn[data-topic]').length,
    meters: r.querySelectorAll('g[data-topic]:not(.btn)').length,
    heizkreis: r.textContent.includes('Heizkreis'),
    burnerOn: r.getElementById('boiler').classList.contains('on'),
  };
}
"""


def main():
    from playwright.sync_api import sync_playwright

    js = open(CARD, encoding="utf8").read()
    states = {k: {"state": v[0], "attributes": {"unit_of_measurement": v[1]}} for k, v in STATES.items()}
    fails = []

    def check(name, cond):
        print(("PASS " if cond else "FAIL ") + name)
        if not cond:
            fails.append(name)

    with sync_playwright() as p:
        b = p.chromium.launch()
        pg = b.new_page()
        errs = []
        pg.on("pageerror", lambda e: errs.append(str(e)))
        pg.set_content("<html><body></body></html>")
        pg.add_script_tag(content="customElements.define('ha-form', class extends HTMLElement{});")
        pg.add_script_tag(content=js)
        r = pg.evaluate(TEST_JS)
        print(json.dumps(r, indent=1, ensure_ascii=False))
        check("Editor erzeugt ha-form", r["hasForm"])
        check("Editor hat 8 Bereiche", r["sections"] == 8)
        check("Editor hat mindestens 30 Felder", r["fields"] >= 30)
        check("Abgewählte Entität ist im Formular leer", r["waterTempCleared"])
        check("Layout-Wert im Formular", r["layoutInForm"] == "compact")
        check("Abweichungen werden gespeichert", r["changed"].get("title") == "X" and r["changed"]["entities"].get("gas_total") == "sensor.g" and r["changed"].get("layout") == "wide")
        check("Leerer Wert wird als null gespeichert", r["changed"]["entities"].get("water_temp") is None and "water_temp" in r["changed"]["entities"])
        check("Standardwerte ergeben schlanke Konfiguration", r["lean"] == {"type": "custom:heizungsanlage-card"})
        check("Editor zweisprachig (de/en)", r["labelDe"] == "Kesseltemperatur" and r["labelEn"] == "Boiler temperature")

        for layout, width, cls in [("wide", 1100, "wide"), ("compact", 390, "narrow"), ("auto", 390, "narrow"), ("auto", 1100, "wide")]:
            pg2 = b.new_page(viewport={"width": width, "height": 900})
            pg2.on("pageerror", lambda e: errs.append(str(e)))
            pg2.set_content("<html><body></body></html>")
            pg2.add_script_tag(content=js)
            res = pg2.evaluate(LAYOUT_JS, [states, layout, width])
            tag = f"Layout {layout} @ {width}px"
            check(f"{tag}: Klasse {cls}", res["cls"] == cls)
            check(f"{tag}: alle Elemente vorhanden" + (f" (fehlt: {res['ids']})" if res["ids"] else ""), not res["ids"])
            check(f"{tag}: Brenner-Animation aktiv", res["burnerOn"])
            check(f"{tag}: 'Heizkreis' statt 'Vorlauf'", res["heizkreis"])
            if cls == "narrow":
                check(f"{tag}: 7 Detail-Schaltflächen", res["topics"] == 7)
                check(f"{tag}: 3 Zähler/Geräte im Schema antippbar", res["meters"] == 3)
            pg2.close()
        check("Keine JavaScript-Fehler im Browser", not errs)
        if errs:
            print(errs)
        b.close()
    print("\n%d Fehler" % len(fails) if fails else "\nAlle Prüfungen bestanden")
    sys.exit(1 if fails else 0)


if __name__ == "__main__":
    main()
