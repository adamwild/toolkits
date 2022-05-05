// see https://developers.google.com/apps-script/guides/triggers/events
// https://developers.google.com/apps-script/reference/spreadsheet/range
// https://developers.google.com/apps-script/reference/spreadsheet/spreadsheet-app

function log(user, projectId, action, message) {
    var spreadsheet = SpreadsheetApp.getActiveSpreadsheet();
    var sheet = spreadsheet.getSheetByName("Logs");
    sheet.appendRow([new Date(), user, projectId, action, message])
  }


  function onEdit(e) {
    const range = e.range;
    const row = range.getRow();
    const column = range.getColumn();
    const sheetName = range.getSheet().getName();

    if (sheetName == "My Super Projects" && column==7) {
      const projectId = range.getSheet().getRange(row, 1).getDisplayValue();
      log(e.user, projectId, "My super Action",  e.oldValue + " => " + e.value);
    }

    if (sheetName == "My other super project" && column==4) {
      const projectId = range.getSheet().getRange(row, 1).getDisplayValue();
      log(e.user, projectId, "my other super action",  e.oldValue + " => " + e.value);


      if (e.oldValue == "Todo" && e.value == "In Progress"){
        range.getSheet().getRange(row, 5).setValue("Good luck! Started " + new Date());
      }
      if (e.oldValue == "In Progress" && e.value == "Done"){
        range.getSheet().getRange(row, 5).setValue("Congrats!");
      }
    }

  }


  updateRMProjectButtonCode = `
  <div>Are you sure you want to update projects?</div>
  <input type="button" class="button" value="yes!" onclick="updateRMProject(); google.script.host.close()">
  <input type="button" class="button" value="No!" onclick="google.script.host.close();">
  `

  function updateRMProjectButton() {
   var widget = HtmlService.createHtmlOutput(updateRMProjectButtonCode);
   SpreadsheetApp.getUi().showModalDialog(widget, "Update RM project");
  }

  function updateRMProject() {
    log("", 1, "updateRMPRoject", "coucou")
    return;
  }
