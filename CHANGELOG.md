# Changelog

## 1.0.6

- Neue Gerätegrafiken: Viessmann Vitocrossal 300 (Kessel), Vitocell 100-V (Speicher), Gaszähler, Wasserzähler und
  Aqmos-Enthärtungsanlage. Flammen- und Füllfenster sind als Overlay aufgesetzt, die Unterkanten von Kessel und Speicher
  liegen auf einer Höhe, die Leitungsanschlüsse wurden angepasst.
- Heizkörper als Vektorgrafik im Stil des Wasserhahns; in der kompakten Ansicht ist der Rücklauf am Heizkörper angeschlossen.
- Liter werden als normales „l“ angezeigt (statt ℓ).

## 1.0.5

- Boxen „Wasserzähler“ und „Enthärtungsanlage“: Alle Messwerte stehen jetzt samt Einheit rechtsbündig (bündig am rechten
  Rand), im breiten und im kompakten Layout. Die übrigen Boxen (Gas, Brenner, Speicher) behalten die Einheiten-Spalte.

## 1.0.4

- Enthärtungs-Tafel: Zeitstempel (letzte Regeneration) werden nur noch als Datum angezeigt (keine Uhrzeit, kein Überlappen mehr
  mit der Beschriftung). Neue Zeile „Noch ca. N Regenerationen“ mit der neuen Entität `softener_remaining` (Restbestand),
  auch im Karteneditor. Die Tafel ist im breiten Layout etwas breiter.
- Breites Layout: Die Kaltwasser-Box nutzt dieselben Schriftgrößen wie die anderen Boxen.

## 1.0.3

- Speicherdiagramm: Die Skala reicht jetzt von 5 K unter dem Mindest-Sollwert bis 5 K über dem Maximal-Sollwert
  (`limit_offset`); die grauen Grenzlinien sind Unter- und Obergrenze.
- Brennerdiagramm: Y-Achse mit den Werten der Kesseltemperatur.

## 1.0.2

- Breites Layout: Das Schema passt sich der Bildschirmhöhe an und wird ohne Scrollen vollständig angezeigt, z. B. auf dem iPad
  im Querformat (vorher war die untere Leiste abgeschnitten). Neue Optionen `fit_screen` (Standard an) und `screen_offset`
  (Abzug für Kopfzeile und Ränder in px, Standard 32), auch im Karteneditor.
- Vorschau-Werkzeug: `tools/harness.py --height` zeigt nur den sichtbaren Bereich, um die Passung ohne Scrollen zu prüfen.

## 1.0.1

- Layout Anpassungen

## 1.0.0

Erstes Release der Home-Assistant-Karte `custom:heizungsanlage-card`.

- Animiertes Anlagenschema einer Gas-/Ölheizung: Kessel mit Flamme (Größe folgt der Modulation), Warmwasserspeicher mit
  Füllanzeige, Heizkreis-, Lade- und Zirkulationspumpe mit drehendem Flügelrad, Heizkörper, Wasserhahn,
  Gas- und Wasserzähler, Enthärtungsanlage.
- Leitungen laufen nur, wenn die jeweilige Pumpe bzw. der Durchfluss aktiv ist.
- 24-h-Verläufe: Brenner (Modulation und Kesseltemperatur) und Warmwasserspeicher (Soll-Linie, Grenzlinien,
  Maximum, Istwert, Minimum).
- Gas und Wasser (Stand und Tagesverbrauch) automatisch aus dem Energie-Dashboard.
- Zwei Layouts: **breit** (Tablet/Desktop) und **kompakt** (Handy, Hochformat) mit Kerngeräten im Schema und
  aufklappbaren Detailbereichen; Umschaltung automatisch nach Breite oder fest per `layout`.
- Visueller Editor (deutsch und englisch) für alle Einstellungen, kein YAML nötig.
- Klick auf einen Wert öffnet den Home-Assistant-Entitätsdialog; native Formatierung der Werte.
- Gerätegrafiken sind eingebettet, die Karte besteht aus einer einzigen Datei ohne externe Abhängigkeiten.
