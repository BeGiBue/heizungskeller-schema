Bereite eine neue Version vor und veröffentliche sie.

1. Lies `CONTEXT.md` und prüfe, ob die letzten Änderungen dort (Design-Entscheidungen) und im `README.md`
   (Funktionen, Optionen, Tabelle der Animationen) berücksichtigt sind. Ergänze fehlendes.
2. Erhöhe `CARD_VERSION` in `dist/heizungsanlage-card.js` und `version` in `package.json` auf dieselbe Nummer
   (Patch für Layout/Texte, Minor für neue Funktionen). Gewünschte Nummer vom Nutzer: $ARGUMENTS
3. Führe `npm run check` und `npm test` aus. Bei Fehlern nicht fortfahren.
4. Erzeuge bei Design-Änderungen die Vorschaubilder in `docs/` neu (`python3 tools/harness.py --docs`).
5. Ergänze in `CHANGELOG.md` oben einen Abschnitt `## X.Y.Z` mit den Änderungen (daraus werden die Release-Notes).
6. Committe mit einer aussagekräftigen deutschen Nachricht und pushe auf `main`. Der Workflow
   `.github/workflows/release.yml` legt dann automatisch Tag `vX.Y.Z` und das GitHub-Release mit
   `dist/heizungsanlage-card.js` als Anhang an (nur wenn es für diese Version noch kein Release gibt).
