/**
 * Wall of Love backend for awesomemarketers.fi/wall-of-love/
 *
 * Setup, once:
 *  1. Create a Google Sheet. Open Extensions > Apps Script and paste this file in.
 *  2. Put the sheet id in SHEET_ID below (the long string in the sheet URL).
 *  3. Deploy > New deployment > Web app.
 *       Execute as: Me
 *       Who has access: Anyone
 *  4. Copy the /exec URL it gives you and paste it into ENDPOINT
 *     in wall-of-love/index.html, then push the site.
 *
 * Re-deploy (Manage deployments > edit > new version) after any change here,
 * otherwise the live URL keeps running the old code.
 */

var SHEET_ID = '';            // <- paste the sheet id
var SHEET_NAME = 'Responses';
var MIN_FILL_MS = 5000;       // anything submitted faster than this is a bot

function doPost(e) {
  try {
    var d = JSON.parse(e.postData.contents || '{}');

    // honeypot: real people never see this field
    if (d.website) return out({ ok: true });

    // bot guard: forms filled within 5 seconds are not filled by humans
    if (d.startedAt && (Date.now() - Number(d.startedAt)) < MIN_FILL_MS) {
      return out({ ok: false, error: 'too fast' });
    }

    var rating = parseInt(d.rating, 10);
    if (!(rating >= 1 && rating <= 5)) return out({ ok: false, error: 'bad rating' });

    // only keep identity fields when they actually gave permission
    var mayPublish = d.mayPublish === true || d.mayPublish === 'true';
    var mayUsePhoto = mayPublish && (d.mayUsePhoto === true || d.mayUsePhoto === 'true');

    sheet().appendRow([
      new Date(),
      rating,
      clip(d.comment, 1200),
      mayPublish ? 'YES' : '',
      mayPublish ? clip(d.firstName, 80) : '',
      mayPublish ? clip(d.lastName, 80) : '',
      mayPublish ? clip(d.company, 120) : '',
      mayPublish ? clip(d.jobTitle, 120) : '',
      mayUsePhoto ? clip(d.linkedin, 300) : '',
      mayUsePhoto ? 'YES' : '',
      ''   // Published? fill in by hand once a quote is on the site
    ]);
    return out({ ok: true });
  } catch (err) {
    return out({ ok: false, error: String(err) });
  }
}

function doGet() {
  return out({ ok: true, service: 'wall-of-love' });
}

function sheet() {
  var ss = SpreadsheetApp.openById(SHEET_ID);
  var sh = ss.getSheetByName(SHEET_NAME);
  if (!sh) {
    sh = ss.insertSheet(SHEET_NAME);
    sh.appendRow(['When', 'Rating', 'Comment', 'May publish', 'First name',
                  'Last name', 'Company', 'Job title', 'LinkedIn', 'May use photo', 'Published?']);
    sh.setFrozenRows(1);
  }
  return sh;
}

function clip(v, n) { return String(v == null ? '' : v).slice(0, n); }

function out(obj) {
  return ContentService.createTextOutput(JSON.stringify(obj))
    .setMimeType(ContentService.MimeType.JSON);
}
