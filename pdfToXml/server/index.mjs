
var puppeteer = require('puppeteer')



async function ssr(url) {
  //ssr = server side rendering
  // this converts a jquery-ified page into a single html file.
  const browser = await puppeteer.launch({headless: true});
  const page = await browser.newPage();
  await page.goto(url, {waitUntil: 'networkidle0'});
  const html = await page.content(); // serialized HTML of page DOM.
  await browser.close();
  return html;
}

var fs = require('fs');


ssr('http://localhost:3000').then(res => {
  fs.writeFile("clean.html", res, function(err){
    if (err) throw err;
     console.log("success");
    }); 
})