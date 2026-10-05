# Changelog

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
