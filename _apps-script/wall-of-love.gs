/**
 * Wall of Love backend for awesomemarketers.fi/wall-of-love/
 *
 * DEPLOYED 2026-10-14. This file is the source of truth; the live copy is the
 * Apps Script project "Wall of Love backend" in anna@awesomemarketers.fi:
 *   https://script.google.com/u/0/home/projects/1TuaPXhNGgzKxpnlnQNA9n_oJNXt0P62LeQUIsl8R1yLLGx3iPZrWY3FF/edit
 * Web app, Execute as: Me (anna@awesomemarketers.fi), Who has access: Anyone.
 * Its /exec URL is wired into ENDPOINT in wall-of-love/index.html.
 * Responses land in the sheet "Wall of Love responses (private)", separate from
 * the Awesome Meets sheet.
 *
 * After ANY change here: paste the file back into that project, save, then
 * Deploy > Manage deployments > edit (pencil) > Version: New version > Deploy.
 * Editing the code alone does nothing; the live URL keeps running the old
 * version until you cut a new one. The /exec URL itself does not change.
 */

var SHEET_ID = '1deoNMOJNTH_e4v1rERXtRL1pfNSk1eXojPoZr9x_hI8';  // 'Wall of Love responses (private)'
var SHEET_NAME = 'Sheet1';   // the tab the headers are already on
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
