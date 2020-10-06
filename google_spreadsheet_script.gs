/**
 * Get info from DOI to fill Sheet 1,2
 * Go to "Publish" -> "Deploy as Sheet Add-on..." and follow steps
 *
 * https://github.com/restrepo/webpy
 * @customfunction
 */
function getInfoFromDOI(DOI) {
  var array = [];
  /*var url = 'http://gfif.udea.edu.co/python/atom.xml';*/
  var gdoi="http://gfif.udea.edu.co/python/revista.php?doi="+DOI
  var tmp = UrlFetchApp.fetch(gdoi).getContentText();
  var url = "http://gfif.udea.edu.co/python/revista.xml";
  /*var url = inpxml;*/
  var xml = UrlFetchApp.fetch(url).getContentText();
  var document = XmlService.parse(xml);
  var root = document.getRootElement();
  var atom = XmlService.getNamespace('http://www.w3.org/2005/Atom');
  var entries = document.getRootElement().getChildren('entry', atom);
  for (var i = 0; i < entries.length; i++) {
    var title = entries[i].getChild('title', atom).getText();
    var date = entries[i].getChild('published', atom).getValue();
    array.push([title, date]);
  }
  return array;
}
