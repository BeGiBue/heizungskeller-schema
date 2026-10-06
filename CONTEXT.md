# Kontext: Heizungskeller Schema

Diese Datei hält fest, was über die Anlage und die verwendeten Entitäten bekannt ist. Sie dient als
Ausgangspunkt für weitere Änderungen an der Karte (`dist/heizungsanlage-card.js`).
In Claude Code wird sie automatisch geladen, wenn sie in `CLAUDE.md` umbenannt oder dort verlinkt wird.

## Anlage

- Gas-Brennwertkessel **Viessmann Vitocrossal 300**, eingebunden über die **ViCare-Integration**
- Warmwasserspeicher **Viessmann Vitocell 100-V**
- Enthärtungsanlage **Aqmos R2D2-32** (Kabinettgerät)
- Gaszähler und Wasserzähler; Gas und Wasser sind im Home-Assistant-**Energie-Dashboard** hinterlegt
- Heizkörper-Heizkreis, Warmwasser-Zirkulation und ein Wasserhahn als Zapfstelle im Schema
- Dashboard in der **Sections-Ansicht**, die Karte soll zwei Sektionen breit sein (`column_span: 2`)

## Vom Nutzer genannte Entitäten

| Entität | Bedeutung | Schlüssel in `entities:` |
|---|---|---|
| `sensor.vicare_outside_temperature` | Außentemperatur | `outside_temp` |
| `binary_sensor.vicare_frost_protection_active` | Frostschutz aktiv | `frost_protection` |
| `sensor.vicare_burner_hours` | Brennerstunden | `burner_hours` |
| `sensor.vicare_burner_starts` | Brennerstarts | `burner_starts` |
| `binary_sensor.vicare_burner_active` | Brenner aktiv | `burner_active` |
| `sensor.vicare_burner_modulation` | Brenner-Modulation (%) | `burner_modulation` |
| `sensor.vicare_boiler_temperature` | Kesseltemperatur | `boiler_temp` |
| `sensor.vicare_supply_temperature` | Vorlauftemperatur | `supply_temp` |
| `binary_sensor.vicare_circulation_pump_active` | Heizkreispumpe | `heating_pump` |
| `binary_sensor.vicare_dhw_pump_active` | Ladepumpe (Speicherladung) | `charge_pump` |
| `binary_sensor.vicare_dhw_circulation_pump_active` | Zirkulationspumpe Warmwasser | `dhw_circ_pump` |
| `binary_sensor.vicare_dhw_charging_active` | Warmwasser-Ladung aktiv | – (wird von der Karte nicht verwendet) |
| `sensor.vscotho1_72_ww_speichertemperatur` | Speichertemperatur (Ist) | `tank_temp` |
| `number.vscotho1_72_warmwassertemperatur` | Warmwasser-Solltemperatur | `tank_target` |
| `sensor.vicare_hot_water_min_temperature` | Mindest-Solltemperatur Warmwasser | `tank_min_target` |
| `sensor.vicare_hot_water_max_temperature` | Maximal-Solltemperatur Warmwasser | `tank_max_target` |
| `number.vscotho1_72_komforttemperatur` | Komforttemperatur | `comfort_temp` |
| `number.vscotho1_72_normaltemperatur` | Normaltemperatur | `normal_temp` |
| `number.vscotho1_72_reduzierte_temperatur` | Reduzierte Temperatur | `reduced_temp` |
| `number.vscotho1_72_steigung_der_heizkurve` | Steigung der Heizkurve | `curve_slope` |
| `number.vscotho1_72_verschiebung_der_heizkurve` | Verschiebung der Heizkurve | `curve_shift` |
| `sensor.wasserzahler_flow` | Wasser-Durchfluss | `water_flow` |
| `sensor.wasserzahler_total` | Wasserzähler-Stand (Fallback, falls im Energie-Dashboard kein Wasser eingetragen ist) | – (feste Rückfalloption) |
| `sensor.wasserzahler_water_temperature` | Kaltwassertemperatur | `water_temp` |

## Noch nicht genannt (optional)

Diese Werte sind in der Karte vorgesehen, aber ohne Entität zeigt die Anzeige „–" bzw. kommt aus dem Energie-Dashboard:

| Schlüssel | Bedeutung | Quelle |
|---|---|---|
| `gas_total`, `gas_today` | Gaszähler: Stand und Tagesverbrauch | automatisch aus dem Energie-Dashboard |
| `water_total`, `water_today` | Wasserzähler: Stand und Tagesverbrauch | automatisch aus dem Energie-Dashboard |
| `softener_regeneration` | Enthärtung: Regeneration | noch keine Entität bekannt |
| `softener_salt` | Enthärtung: Salzvorrat (%) | noch keine Entität bekannt |

## Zuordnung (vom Nutzer bestätigt)

- `vicare_circulation_pump_active` ist die **Heizkreispumpe**, `vicare_dhw_pump_active` die **Ladepumpe**,
  `vicare_dhw_circulation_pump_active` die **Warmwasser-Zirkulationspumpe**.
- `vicare_hot_water_min_temperature` / `…_max_temperature` sind der **Mindest- bzw. Maximal-Sollwert**.
  Die grauen Grenzlinien im Speicherdiagramm liegen **5 K unter dem Mindest-Sollwert** und **5 K über dem
  Maximal-Sollwert** (`limit_offset: 5`). Seit 1.0.3 sind sie zugleich der **niedrigste und höchste Skalenwert**
  des Diagramms; Werte außerhalb werden am Rand gezeichnet, die Zahlen rechts zeigen die echten Werte.

## Design- und Layout-Entscheidungen

- Zeichnung als SVG, Koordinatensystem 1400 Einheiten breit; Gerätegrafiken (Kessel, Speicher, Heizkörper,
  Gaszähler, Wasserzähler, Enthärtung) sind aus einem Mockup freigestellt und als WebP eingebettet.
  Pumpen, Hahn und Leitungen sind gezeichnet.
- Datenboxen stehen jeweils **unter ihrem Gerät**. Pumpen haben **keine Boxen und keine Namen**; läuft eine
  Pumpe, dreht sich das Flügelrad.
- Ladepumpe mittig zwischen Kessel und Speicher, Heizkreispumpe senkrecht darüber, Zirkulationspumpe mittig
  zwischen Speicher und Hahn. Der Kaltwasserzulauf geht gerade und mittig von unten in Kessel und Speicher.
- **Brennerbox:** ohne Titel und LED; ein 24-h-Graph mit Modulation (Fläche) und Kesseltemperatur (Linie),
  die beiden Istwerte rechts daneben. Seit 1.0.3 mit Y-Achse (Werte der Kesseltemperatur in °C, rot beschriftet).
- **Speicherbox:** ohne Titel; 24-h-Verlauf mit zwei grauen gestrichelten Grenzlinien (ohne Beschriftung) und
  orange gepunkteter Soll-Linie; rechts Maximum, Istwert und Minimum ohne „Min"/„Max". Brenner- und
  Speicherbox haben dieselbe Oberkante und Höhe (Speicherbox ist die Referenz).
- **Untere Leiste** in zwei Zeilen: Status (Außentemperatur, Frostschutz, Brennerstunden, Brennerstarts) und
  Einstellungen (Komfort, Normal, Reduziert, Warmwasser Soll, Verschiebung, Steigung).
- Tafel der Enthärtungsanlage (Regeneration, Salz %) ist immer sichtbar; Schriftzug „AQMOS".
- Enthärtungs-Tafel mit drei Zeilen: Regeneration (Datum ohne Uhrzeit), Salz %, Noch ca. N Regenerationen
  (`softener_remaining`). Zeitstempel werden in der Karte generell nur als Datum angezeigt. Die Kaltwasser-Box (breit)
  nutzt dieselben Schriftgrößen wie die anderen Boxen (Beschriftung 18, Wert 20).
- Kaltwassertemperatur steht über dem Wasserzähler, die Box ist so breit wie die Wasserzähler-Box (breites Layout).
- **Versionsnummer:** vom Nutzer auf **1.0.1** festgelegt (Zählung neu begonnen; vorherige interne Stände 3.x entfallen). Ab hier hochzählen.
- **Liter-Einheit:** normales kleines „l" der Schriftart (kein ℓ), „L" wird zu „l" (z. B. „177 l", „12 l/h").
- **Einheiten in Boxen mit mehreren Zahlenwerten** (Gas, Brenner-Werte, Speicher-Werte): Zahl rechtsbündig,
  Einheit linksbündig, alle Einheiten einer Box untereinander in einer Spalte (`numUnit`, `_alignUnits`).
- **Wasserzähler- und Enthärtungs-Box** (seit 1.0.5, auf Wunsch des Nutzers): alle Messwerte samt Einheit **rechtsbündig**
  am rechten Rand, in beiden Layouts (`numUnit(…, 'right')`, `data-ua="right"`).
- Wasserzähler: **Stand in m³ mit 2 Nachkommastellen**, **Durchfluss in l/h**. Die Sensoren des Nutzers liefern Liter (`wasserzahler_total`) und m³/h (`wasserzahler_flow`); die Karte rechnet um (`UNIT_FACTORS`, `_convertTo`). „Heute" bleibt unverändert (Einheit aus dem Energie-Dashboard, z. B. L). Titel groß, oben möglichst wenig Leerraum.
- Das Feld unter dem Heizkörper heißt **„Vorlauf"** (zeigt `supply_temp`; zwischenzeitlich „Heizkreis", auf Wunsch wieder „Vorlauf" in allen Karten und Boxen).
- Alle Einstellungen laufen über den visuellen Editor von Home Assistant (`ha-form`).

## Mobile Nutzung

**iPad (Querformat):** Das breite Layout war höher als der Bildschirm, die untere Leiste wurde abgeschnitten. Seit 1.0.2 passt sich
das breite Layout der Bildschirmhöhe an (`fit_screen`, `screen_offset`): `max-height` = Bildschirmhöhe minus Kopfzeile minus Abzug.

Genutzt wird die Karte vor allem auf dem **Handy** und einem **7"-Raspberry-Display im Hochformat**
(ca. 480 px breit), zusätzlich auf einem **13"-Tablet** (breites Layout).
Für schmale Bildschirme wurde **Variante 3 „reduziert"** gewählt: Kerngeräte mit großen Zahlen
(Vorlauf, Kessel, Speicher, Kaltwasser), alle Details hinter Schaltflächen (Akkordeon, immer nur ein Bereich
offen). Anordnung: Zeile 1 Diagramme, Status, Einstellungen; Zeile 2 Brenner, Gas, Wasser, Enthärtung;
die Schaltflächen sind pro Zeile gleich breit.
Im kompakten Schema sind alle drei Pumpen gleich groß (Größe der Ladepumpe), die Heizkreispumpe sitzt senkrecht
über der Ladepumpe. Die vier Werte-Boxen (Vorlauf, Kessel, Speicher, Kaltwasser) haben dieselbe Größe (110×52)
und dieselben Schriftgrößen (Beschriftung 13, Wert 20): Speicher- und Kaltwasser-Box sind gleich breit und senkrecht mittig übereinander,
die Kessel-Box steht horizontal mittig zur Speicher-Box (gleiche Mittellinie).
Im kompakten Layout sind die Abstände Überschrift → Schema und Schema → Details gleich groß (je ca. 27 Einheiten,
die Hälfte des früheren Abstands zur Überschrift). Die Zähler im Schema haben keine Beschriftung. Die Enthärtungsanlage ist 15 % größer als ursprünglich (Unterkante unverändert).
Im kompakten Schema stehen auch die Zähler: **Gaszähler links unten** (gelbe Leitung senkrecht in den Kessel),
**Wasserzähler rechts unten**, die **Enthärtungsanlage links neben dem Wasserzähler**. Das Wasser läuft vom
Wasserzähler über die Enthärtung zum bisherigen Kaltwassereingang (x=250, Knoten der Kaltwasserleitung) in das
bestehende Schema. Ein Tipp auf einen Zähler öffnet den passenden Detailbereich.
Im Bereich „Diagramme" haben beide Diagramme Überschriften mit kleiner Legende: „Brenner" (Modulation, Kesseltemperatur) und
„Warmwasserspeicher" (Soll, Grenzwerte).
Umschaltung automatisch bei < 700 px Breite oder fest über `layout: wide | compact`.
