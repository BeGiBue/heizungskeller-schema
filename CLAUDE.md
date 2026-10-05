# CLAUDE.md – Arbeitsanweisungen für dieses Repository

## Projekt

Home-Assistant-Custom-Card **`custom:heizungsanlage-card`**: animiertes Anlagenschema einer Gas-Heizung
(Viessmann Vitocrossal 300 + Vitocell 100-V, Integration ViCare). Die gesamte Karte ist **eine einzige,
in sich geschlossene Datei**: `dist/heizungsanlage-card.js` (kein Build-Schritt, keine Abhängigkeiten,
keine externen Requests). HACS lädt genau diese Datei.

**Vor jeder Änderung `CONTEXT.md` lesen** (Anlage, Entitäten, Layout- und Design-Entscheidungen des Nutzers).

## Regeln

1. Nur `dist/heizungsanlage-card.js` ändern (plus Doku). Die Base64-Bilder in `const IMG` **nie von Hand
   bearbeiten oder umformatieren**; Bilder werden mit `tools/images.py` getauscht.
2. Nach jeder Änderung: `npm run check` (Syntax) und `npm test` (Editor + beide Layouts), danach die Vorschau in
   **beiden Layouts** ansehen (`npm run preview`, siehe unten) und das Ergebnis prüfen, bevor committet wird.
3. `CARD_VERSION` (Zeile 11) und `package.json` hochzählen: Patch für Layout/Texte, Minor für neue Funktionen. Der Nutzer hat
   die Version auf **1.0.1** festgelegt, die Zählung läuft ab dort weiter.
4. Ändern sich Verhalten, Optionen oder Design-Entscheidungen, `README.md` und `CONTEXT.md` mitpflegen.
5. Texte in der Karte sind **deutsch**; der Editor ist deutsch **und** englisch (`EDITOR_I18N`).
6. Native Home-Assistant-Mittel verwenden: `ha-form`-Editor, `hass-more-info` bei Klick auf Werte,
   `hass.formatEntityState` für Zahlen, Sections-Breite über `getGridOptions()`. Kein `localStorage`,
   keine eigenen Netzwerkzugriffe; Daten nur über `hass` (States, `callWS`).
7. Standardwerte der Entitäten (`DEFAULTS.entities`) sind die des Nutzers und dürfen nicht stillschweigend
   geändert werden, sonst bricht sein Dashboard.
8. Der Nutzer beschreibt Änderungen oft in Positions- und Ausrichtungsangaben („mittig zwischen …", „50 nach
   links", „Oberkante an … ausrichten"). Koordinaten genau berechnen, nicht schätzen, und danach in der
   Vorschau nachprüfen.

## Aufbau von `dist/heizungsanlage-card.js`

| Teil | Zweck |
|---|---|
| `CARD_VERSION`, `IMG` | Version; eingebettete Gerätebilder (WebP als Data-URI: boiler, tank, rad, gas, wm, soft) |
| `C`, `PUMP_INNER`, `DEFAULTS` | Leitungsfarben; gezeichnete Pumpe; Standard-Konfiguration inkl. aller Entitäten |
| `class HeizungsanlageCard` | die Karte |
| `connectedCallback` / `_useNarrow` | `ResizeObserver`: unter 700 px → kompaktes Layout (`layout: auto`) |
| `_build`, `_css` | Shadow-DOM aufbauen, Klick-Handler (`data-entity` → more-info, `data-topic` → Akkordeon) |
| `_svgWide()` | breites Layout, `viewBox 0 0 1400 1150` |
| `_svgNarrow()` / `_defs()` | kompaktes Layout (Handy), `viewBox 0 0 600 H`, Details hinter Schaltflächen |
| `_st`, `_num`, `_on`, `_fmt`, `_fmtVal`, `_unitOf` | Zugriff auf States und Formatierung |
| `_loadEnergy` | Gas/Wasser aus dem Energie-Dashboard (`energy/get_prefs`, Statistiken) |
| `_update()` | schaltet Animationen (Klasse `on`), setzt Texte, Speicherfüllung, zeichnet Diagramme |
| `_loadHistory`, `_series`, `_drawBurnerChart`, `_drawChart` | 24-h-Verläufe (alle 5 min neu geladen) |
| `EDITOR_I18N`, `class HeizungsanlageCardEditor` | visueller Editor mit `ha-form` (`_schema`, `_toData`, `_fromData`) |
| Registrierung am Ende | `customElements.define`, `window.customCards` |

## Koordinatensysteme

Einheiten ≈ Pixel bei Breite 1400 (breit) bzw. 600 (kompakt); die Grafik skaliert mit der Kartenbreite.

**Breit** (`_svgWide`): Alles außer Titel liegt in `<g transform="translate(0,-104)">`; die Koordinaten im Code
sind die „alten" ohne diese Verschiebung (angezeigtes y = Codewert − 104).
Anker: Kessel-Bild `x300 y400 w220`, Speicher `858,415 w130`, Heizkörper `1180,262 w170`, Gaszähler `40,445 w130`,
Wasserzähler `22,823 w120`, Enthärtung `263,789 w80`. Pumpen (Achse y): Heizkreis `(689,290)`, Lade `(689,500)`,
Zirkulation `(1125,500)`. Leitungen: Heizkreis-Vorlauf y290, -Rücklauf y355; Ladekreis/Zirkulation Vorlauf y500,
Rücklauf y600; Kaltwasser-Hauptleitung y860 mit Abzweigen bei x410 (Kessel, mittig), x923 (Speicher, mittig)
und x1284 (Hahn). Boxen: Brenner `434,686 290×152`, Speicher `950,686 312×152` (gleiche Oberkante/Höhe, Speicherbox
ist Referenz), Gas `20,572`, Wasser `20,912`, Enthärtung `360,912`, Vorlauf-Feld `1190,392`, Kaltwasser-Feld
`20,768`. Untere Leiste `y1080–1232` (Status- und Einstellungszeile).

**Kompakt** (`_svgNarrow`): Schema in `translate(0,100)`: Kessel `30,170 w150`, Speicher `335,183 w100`, Heizkörper
`440,52 w140`, Pumpen `(300,80)`, `(257,245)`, `(488,245)`; Kaltwasser-Knoten `(250,450)`. Schaltflächen ab y730,
Detailbereich ab y854. Die Höhe der `viewBox` hängt vom geöffneten Thema ab.

## Konventionen

- **Animationen** hängen an der CSS-Klasse `on`: `<g class="line" id="ln-…">`, `<g class="pump" id="pm-…">`,
  `#boiler`, `#drops`. `_update()` setzt die Klasse anhand der Entitäten (Tabelle in `README.md`).
  Neue Animation = Element mit ID + CSS-Regel unter `.…on` + Zeile in `_update()`.
- **Einheiten:** Wasserstand wird in m³ (2 Nachkommastellen), Durchfluss in ℓ/h angezeigt; `_convertTo(id, ziel)` rechnet
  über `UNIT_FACTORS` aus der Einheit der Entität um (unbekannte Einheit → unveränderte Anzeige). Neue Einheit = Eintrag dort.
- **Zahl + Einheit:** Werte in Boxen mit mehreren Zahlenwerten werden mit `numUnit(id, gruppe, x, y, style)` erzeugt (zwei
  Textelemente). `setT` trennt Text per `_splitUnit`, `_alignUnits()` richtet die Einheiten einer Gruppe linksbündig
  untereinander aus. Liter immer mit **ℓ** (`_liter`), nie mit „L" oder „l".
- **Texte setzen** über `setT(id, text)`; schreibt zusätzlich in das Element `<id>-d` (kompakte Ansicht zeigt
  einige Werte zugleich im Schema und im Detailbereich).
- **Klickbar** ist alles mit `data-entity="…"` (öffnet den Home-Assistant-Dialog). Leere Entität = nicht klickbar.
- **Diagramme** lesen ihre Geometrie aus `data-x0/x1/y0/y1/xr` am Zielelement (`#chart`, `#chart-burner`),
  sonst gelten die Standardwerte des breiten Layouts.
- Konfigurationsschlüssel liegen in `DEFAULTS`; jeder neue Schlüssel braucht ein Feld im Editor
  (`_schema`, `_toData`, `_fromData`, Labels in `EDITOR_I18N`) und einen Eintrag im README.
- Ein leer gewählte Entität wird im Editor als `null` gespeichert (bewusst abgewählt).

## Vorschau und Tests

Benötigt Python 3 sowie `pip install playwright pillow` und `playwright install chromium`.
Ist das in der Umgebung nicht möglich, Änderungen sorgfältig durch Code-Lesen prüfen und dem Nutzer ausdrücklich
sagen, dass keine Vorschau erzeugt werden konnte.

```bash
npm run check                                   # node --check
npm test                                        # tools/test_editor.py: Editor + beide Layouts
npm run preview                                 # tools/out/breit.png und tools/out/kompakt*.png
python tools/harness.py --width 390 --topic diagrams --out tools/out/x.png   # einzelnes Bild
python tools/images.py extract                  # Gerätebilder nach assets/devices/*.webp
python tools/images.py embed                    # Bilder aus assets/devices/ wieder einbetten
```

Die Vorschau nutzt Testdaten (siehe `tools/harness.py`) – kein echtes Home Assistant. Die Bilder
`docs/vorschau.png` und `docs/vorschau-kompakt.png` im README werden bei größeren Design-Änderungen mit
`python tools/harness.py` neu erzeugt.

## Typische Aufgaben

- **Gerät oder Box verschieben:** Koordinaten im jeweiligen `_svg…`-Block ändern, **verbundene Leitungen** (`line(...)`)
  und Beschriftungen mitziehen, Ausrichtungen (mittig, gleiche Oberkante) rechnerisch einhalten.
- **Neue Entität/Option:** `DEFAULTS` → Editor (Schema, Daten, Labels de/en) → Anzeige/`_update()` → README + `CONTEXT.md`.
- **Gerätebild tauschen:** `tools/images.py extract`, WebP in `assets/devices/` ersetzen, `embed`; danach Vorschau prüfen.
- **Neues Thema im kompakten Layout:** Eintrag in `topics` (Schaltfläche) und Zweig `open === '…'` in `_svgNarrow()`.

## Veröffentlichen

Version erhöhen (`CARD_VERSION` und `package.json`), Abschnitt `## X.Y.Z` in `CHANGELOG.md` ergänzen, Doku abgleichen,
`npm run check` + `npm test`, committen und auf `main` pushen. Der Workflow `.github/workflows/release.yml` legt dann
Tag `vX.Y.Z` und GitHub-Release (Notes aus `CHANGELOG.md`, Anhang `dist/heizungsanlage-card.js`) automatisch an
(siehe `.claude/commands/release.md`).
