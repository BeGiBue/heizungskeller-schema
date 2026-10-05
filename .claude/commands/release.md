Bereite eine neue Version vor und veröffentliche sie.

1. Lies `CONTEXT.md` und prüfe, ob die letzten Änderungen dort (Design-Entscheidungen) und im `README.md`
   (Funktionen, Optionen, Tabelle der Animationen) berücksichtigt sind. Ergänze fehlendes.
2. Erhöhe `CARD_VERSION` in `dist/heizungsanlage-card.js` und `version` in `package.json` auf dieselbe Nummer
   (Patch für Layout/Texte, Minor für neue Funktionen). Gewünschte Nummer vom Nutzer: $ARGUMENTS
3. Führe `npm run check` und `npm test` aus. Bei Fehlern nicht fortfahren.
4. Erzeuge bei Design-Änderungen die Vorschaubilder in `docs/` neu (`python3 tools/harness.py --docs`).
5. Committe mit einer aussagekräftigen deutschen Nachricht, pushe und lege (wenn gewünscht) einen Release `vX.Y.Z`
   mit der Datei `dist/heizungsanlage-card.js` als Anhang an.
