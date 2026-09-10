/**
 * Clero LOI -> Google Drive Upload
 * ---------------------------------
 * Nimmt das signierte LOI-PDF von eintragen.html entgegen und legt es im
 * vorgesehenen Drive-Ordner ab. Laeuft als Google Apps Script Web App,
 * damit die (rein clientseitige, serverlose) Website dort hinschreiben kann.
 *
 * EINRICHTUNG (einmalig, ca. 2 Minuten):
 * 1. https://script.google.com aufrufen, eingeloggt mit dem Google-Account,
 *    der Zugriff auf den Ziel-Ordner hat (der im FOLDER_ID unten verlinkte
 *    Ordner: https://drive.google.com/drive/folders/1YwqXYzlq9YjpnlzQZya1bw1IAjfz4Qqv).
 * 2. "Neues Projekt", diesen kompletten Code reinkopieren (ersetzt den
 *    Beispielcode).
 * 3. Optional: SHARED_SECRET unten auf einen eigenen, geheimen Wert aendern
 *    (nur damit nicht irgendwer im Netz beliebig Dateien in den Ordner laden
 *    kann). Wenn geaendert: den neuen Wert an Claude weitergeben, er muss auf
 *    der Website identisch eingetragen werden.
 * 4. Oben rechts "Bereitstellen" -> "Neue Bereitstellung".
 * 5. Zahnrad-Symbol bei "Typ auswaehlen" -> "Web-App".
 * 6. "Ausfuehren als": Ich (dein Account). "Zugriff": Jeder.
 * 7. "Bereitstellen" klicken, Berechtigungen bestaetigen (Zugriff auf Drive
 *    erlauben - Google zeigt eine Warnung "nicht verifizierte App", das ist
 *    normal bei einem privaten Script, auf "Erweitert" -> "zu Clero LOI
 *    Upload (unsicher) wechseln" klicken).
 * 8. Die angezeigte Web-App-URL (endet auf /exec) kopieren und an Claude
 *    schicken, damit sie in eintragen.html eingetragen wird.
 *
 * Spaetere Code-Aenderungen brauchen eine NEUE Bereitstellungsversion
 * ("Bereitstellen" -> "Bereitstellungen verwalten" -> Stift-Icon -> neue
 * Version waehlen), sonst laeuft weiter der alte Stand.
 */

var FOLDER_ID = '1YwqXYzlq9YjpnlzQZya1bw1IAjfz4Qqv';
var SHARED_SECRET = 'clero-loi-2026'; // beliebig aendern - muss dann auch in eintragen.html geaendert werden

function doPost(e) {
  try {
    var params = (e && e.parameter) || {};

    if (params.secret !== SHARED_SECRET) {
      return jsonOut({ ok: false, error: 'forbidden' });
    }

    var base64 = params.pdf_base64;
    if (!base64) {
      return jsonOut({ ok: false, error: 'missing pdf_base64' });
    }

    var filename = (params.filename || 'Clero-LOI.pdf').replace(/[\/\\]/g, '_');
    var bytes = Utilities.base64Decode(base64);
    var blob = Utilities.newBlob(bytes, 'application/pdf', filename);

    var folder = DriveApp.getFolderById(FOLDER_ID);
    folder.createFile(blob);

    return jsonOut({ ok: true });
  } catch (err) {
    return jsonOut({ ok: false, error: String(err) });
  }
}

function jsonOut(obj) {
  return ContentService.createTextOutput(JSON.stringify(obj)).setMimeType(ContentService.MimeType.JSON);
}
