/**
 * Clero LOI -> Google Drive Upload
 * ---------------------------------
 * Nimmt das signierte LOI-PDF von eintragen.html / verzeichnis.html / creator.html
 * entgegen und legt es im passenden Drive-Ordner ab - Host-LOIs (Community/Founding-20)
 * und Creator-LOIs landen in getrennten Ordnern. Laeuft als Google Apps Script Web App,
 * damit die (rein clientseitige, serverlose) Website dort hinschreiben kann.
 *
 * Legt IMMER nur genau eine PDF-Datei pro Aufruf ab, nichts anderes (kein .txt o.ae.) -
 * das Script bricht mit einem Fehler ab, statt irgendeinen Fallback-Dateityp zu schreiben.
 *
 * Hinweis: die frueher hier ueber Monate gesammelten Host-LOI-PDFs (und ein einzelnes
 * .txt) im urspruenglichen Ordner kamen NICHT von diesem Script (das war bis 2026-09-10
 * inaktiv), sondern von einer separaten, aelteren Automatisierung, die Anhaenge aus dem
 * n.emrich@clero.de-Postfach in Drive sichert. Das einzelne .txt deckt sich zeitlich und
 * inhaltlich exakt mit der (inzwischen behobenen) Doppel-Mail: die zusaetzliche Mail ohne
 * PDF-Anhang wurde dort offenbar als Text abgelegt, weil kein Anhang vorhanden war. Mit
 * nur noch einer Mail (immer mit PDF) sollte das von selbst aufhoeren. Dieses Script hier
 * ersetzt diese alte Automatisierung fuer neue Einreichungen, sobald es deployed und die
 * DRIVE_UPLOAD_URL auf den Seiten gesetzt ist.
 *
 * EINRICHTUNG (einmalig, ca. 2 Minuten):
 * 1. https://script.google.com aufrufen, eingeloggt mit dem Google-Account,
 *    der Zugriff auf BEIDE Ziel-Ordner hat (siehe FOLDERS unten).
 * 2. "Neues Projekt", diesen kompletten Code reinkopieren (ersetzt den
 *    Beispielcode).
 * 3. Optional: SHARED_SECRET unten auf einen eigenen, geheimen Wert aendern
 *    (nur damit nicht irgendwer im Netz beliebig Dateien in die Ordner laden
 *    kann). Wenn geaendert: den neuen Wert an Claude weitergeben, er muss auf
 *    den Websites identisch eingetragen werden.
 * 4. Oben rechts "Bereitstellen" -> "Neue Bereitstellung".
 * 5. Zahnrad-Symbol bei "Typ auswaehlen" -> "Web-App".
 * 6. "Ausfuehren als": Ich (dein Account). "Zugriff": Jeder.
 * 7. "Bereitstellen" klicken, Berechtigungen bestaetigen (Zugriff auf Drive
 *    erlauben - Google zeigt eine Warnung "nicht verifizierte App", das ist
 *    normal bei einem privaten Script, auf "Erweitert" -> "zu Clero LOI
 *    Upload (unsicher) wechseln" klicken).
 * 8. Die angezeigte Web-App-URL (endet auf /exec) kopieren und an Claude
 *    schicken, damit sie auf allen drei Seiten eingetragen wird.
 *
 * Spaetere Code-Aenderungen (z.B. neue Ordner-IDs) brauchen eine NEUE
 * Bereitstellungsversion ("Bereitstellen" -> "Bereitstellungen verwalten" ->
 * Stift-Icon -> neue Version waehlen), sonst laeuft weiter der alte Stand.
 */

var FOLDERS = {
  host: '1YwqXYzlq9YjpnlzQZya1bw1IAjfz4Qqv',    // eintragen.html + verzeichnis.html (Community/Founding-20-LOI)
  creator: '1abEZ0k2VIjFyQ6UQAxlBivoYyo0TbEeI'  // creator.html (Founding-Creator-LOI)
};
var SHARED_SECRET = 'clero-loi-2026'; // beliebig aendern - muss dann auch auf den Seiten geaendert werden

function doPost(e) {
  try {
    var params = (e && e.parameter) || {};

    if (params.secret !== SHARED_SECRET) {
      return jsonOut({ ok: false, error: 'forbidden' });
    }

    var folderKey = params.folder === 'creator' ? 'creator' : 'host'; // unbekannt/fehlend -> host (Rueckwaertskompatibilitaet)
    var folderId = FOLDERS[folderKey];
    if (!folderId) {
      return jsonOut({ ok: false, error: 'unknown folder: ' + folderKey });
    }

    var base64 = params.pdf_base64;
    if (!base64) {
      return jsonOut({ ok: false, error: 'missing pdf_base64' });
    }

    var filename = (params.filename || 'Clero-LOI.pdf').replace(/[\/\\]/g, '_');
    if (!/\.pdf$/i.test(filename)) filename += '.pdf'; // hier soll wirklich nur je eine PDF abgelegt werden
    var bytes = Utilities.base64Decode(base64);
    var blob = Utilities.newBlob(bytes, 'application/pdf', filename);

    var folder = DriveApp.getFolderById(folderId);
    folder.createFile(blob);

    return jsonOut({ ok: true, folder: folderKey });
  } catch (err) {
    return jsonOut({ ok: false, error: String(err) });
  }
}

function jsonOut(obj) {
  return ContentService.createTextOutput(JSON.stringify(obj)).setMimeType(ContentService.MimeType.JSON);
}
