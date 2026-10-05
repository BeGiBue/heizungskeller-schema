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
async ([states, layout, width]) => {
  document.body.style.width = width + 'px';
  const c = document.createElement('heizungsanlage-card');
  c.setConfig(layout === 'auto' ? {} : {layout});
  document.body.appendChild(c);
  c.hass = {states, language: 'de', callWS: async (m) => {
    if (m.type === 'energy/get_prefs') return {device_consumption_water: [{stat_consumption: 'sensor.wasserzahler_total'}]};
    if (m.type === 'recorder/statistics_during_period') return {[m.statistic_ids[0]]: [{change: 177}]};
    if (m.type === 'recorder/get_statistics_metadata') return [{display_unit_of_measurement: 'L'}];
    return {};
  }};
  await new Promise((res) => setTimeout(res, 150)); // Energie-Dashboard-Abfrage abwarten
  const r = c.shadowRoot;
  const has = (id) => !!r.getElementById(id);
  // Zahl und Einheit eines Wertes (getrennte Textelemente) zusammensetzen
  const val = (id) => {
    const n = r.getElementById(id), u = r.getElementById(id + '-u');
    return n ? (n.textContent + (u && u.textContent ? ' ' + u.textContent : '')) : null;
  };
  const ux = (ids) => ids.map((id) => { const u = r.getElementById(id + '-u'); return u ? u.getAttribute('x') : null; });
  const nx = (ids) => ids.map((id) => { const n = r.getElementById(id); return n ? n.getAttribute('x') : null; });
  const water = ['v-water-today', 'v-water-total', 'v-water-flow'];
  return {
    cls: r.querySelector('svg').getAttribute('class'),
    ids: ['boiler', 'tank-hot', 'pm-heat', 'pm-chg', 'pm-circ', 'ln-heat-f', 'ln-cold', 'flame', 'v-supply', 'v-tank', 'v-cold'].filter((i) => !has(i)),
    topics: r.querySelectorAll('.btn[data-topic]').length,
    meters: r.querySelectorAll('g[data-topic]:not(.btn)').length,
    vorlauf: r.textContent.includes('Vorlauf') && !r.textContent.includes('Heizkreis'),
    wt: val('v-water-total'),
    wf: val('v-water-flow'),
    wh: val('v-water-today'),
    waterUx: ux(water),
    waterNx: nx(water),
    burnerUx: ux(['v-mod', 'v-boiler']),
    tankUx: ux(['v-tank', 'ch-max', 'ch-min']),
    burnerOn: r.getElementById('boiler').classList.contains('on'),
  };
}
"""


FIT_JS = """
([states, config]) => {
  document.body.style.width = '1100px';
  const c = document.createElement('heizungsanlage-card');
  c.setConfig(config);
  document.body.appendChild(c);
  c.hass = {states, language: 'de', callWS: async () => ({})};
  const svg = c.shadowRoot.querySelector('svg');
  const fields = customElements.get('heizungsanlage-card').getConfigElement();
  document.body.appendChild(fields);
  fields.hass = {language: 'de', states: {}};
  fields.setConfig({});
  const names = fields._form ? fields._form.schema.flatMap((s) => s.schema).map((x) => x.name) : [];
  return {fit: svg.classList.contains('fit'), offset: svg.getAttribute('style'), names};
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
            check(f"{tag}: Klasse {cls}", res["cls"].split()[0] == cls)
            check(f"{tag}: alle Elemente vorhanden" + (f" (fehlt: {res['ids']})" if res["ids"] else ""), not res["ids"])
            check(f"{tag}: Brenner-Animation aktiv", res["burnerOn"])
            check(f"{tag}: Box heißt 'Vorlauf' (nicht 'Heizkreis')", res["vorlauf"])
            if cls == "wide":
                check(f"{tag}: Wasserzähler-Stand in m³ mit 2 Nachkommastellen (L → m³)", res["wt"] == "539,95 m³")
                check(f"{tag}: Durchfluss in ℓ/h (m³/h → ℓ/h)", res["wf"] == "12 ℓ/h")
                check(f"{tag}: Liter-Symbol ℓ statt L", res["wh"] == "177 ℓ")
                same = lambda a: len(set(a)) == 1 and a[0] is not None
                check(f"{tag}: Wasserzähler-Box: Einheiten linksbündig untereinander", same(res["waterUx"]))
                check(f"{tag}: Wasserzähler-Box: Zahlen rechtsbündig vor der Einheitenspalte", same(res["waterNx"]))
                check(f"{tag}: Brenner-Box: Einheiten linksbündig untereinander", same(res["burnerUx"]))
            if cls == "narrow":
                check(f"{tag}: 7 Detail-Schaltflächen", res["topics"] == 7)
                check(f"{tag}: 3 Zähler/Geräte im Schema antippbar", res["meters"] == 3)
            pg2.close()
        # Anpassung an die Bildschirmhöhe (breites Layout)
        pg3 = b.new_page(viewport={"width": 1100, "height": 900})
        pg3.on("pageerror", lambda e: errs.append(str(e)))
        pg3.set_content("<html><body></body></html>")
        pg3.add_script_tag(content="customElements.define('ha-form', class extends HTMLElement{});")
        pg3.add_script_tag(content=js)
        fit_default = pg3.evaluate(FIT_JS, [states, {"layout": "wide"}])
        fit_off = pg3.evaluate(FIT_JS, [states, {"layout": "wide", "fit_screen": False}])
        fit_off32 = pg3.evaluate(FIT_JS, [states, {"layout": "wide", "screen_offset": 80}])
        check("Breites Layout passt sich standardmäßig der Bildschirmhöhe an", fit_default["fit"] and "--fit-offset:32px" in fit_default["offset"])
        check("fit_screen: false schaltet die Anpassung ab", not fit_off["fit"])
        check("screen_offset wird übernommen", "--fit-offset:80px" in fit_off32["offset"])
        check("Editor bietet fit_screen und screen_offset an", "fit_screen" in fit_default["names"] and "screen_offset" in fit_default["names"])
        check("Keine JavaScript-Fehler im Browser", not errs)
        if errs:
            print(errs)
        b.close()
    print("\n%d Fehler" % len(fails) if fails else "\nAlle Prüfungen bestanden")
    sys.exit(1 if fails else 0)


if __name__ == "__main__":
    main()
