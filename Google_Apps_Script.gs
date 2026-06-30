function doPost(e) {
  try {
    var ss = SpreadsheetApp.getActiveSpreadsheet();
    var data = JSON.parse(e.postData.contents);
    
    var sheetName = data.SheetName;
    var sheet;
    
    // Jika ada SheetName di payload, gunakan itu atau buat baru jika belum ada
    if (sheetName) {
      sheet = ss.getSheetByName(sheetName);
      if (!sheet) {
        sheet = ss.insertSheet(sheetName);
      }
      // Hapus SheetName dari data agar tidak menjadi kolom di tabel
      delete data.SheetName;
    } else {
      // Fallback untuk aplikasi lama yang tidak mengirim SheetName
      sheet = ss.getActiveSheet();
    }
    
    // Jika sheet masih kosong, tambahkan header
    if (sheet.getLastRow() === 0) {
      sheet.appendRow(Object.keys(data));
    }
    
    // Tambahkan baris data
    var row = Object.values(data);
    sheet.appendRow(row);
    
    return ContentService.createTextOutput(JSON.stringify({"result": "success"}))
      .setMimeType(ContentService.MimeType.JSON);
      
  } catch (err) {
    return ContentService.createTextOutput(JSON.stringify({"result": "error", "message": err.message}))
      .setMimeType(ContentService.MimeType.JSON);
  }
}
