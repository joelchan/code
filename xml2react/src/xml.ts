import * as cheerio from 'cheerio';


export function getTextFromXML() {
    const xml = require('@assets/picf_sentences.xml');
    var $ = cheerio.load(xml, {
      xmlMode: true
    });
    
    let imgsCaptions: { [ids: string]: string }[] = $('fig')
      .toArray()
      .map((el, i) => {
        const href = $(el)
          .children('graphic')
          .attr('xlink:href');
        const caption = $(el)
          .children('caption')
          .text()
          .trim();
        return { href, caption };
      });
    
    let pText: string[][] = $('p:not(caption p)')
      .toArray()
      .map((el, i) => {
        const spansInP = $(el)
          .children('span')
          .toArray();
        return spansInP.map((el, i) => $(el).text());
      });
    
      return {pText, imgsCaptions}
}