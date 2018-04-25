import * as cheerio from 'cheerio';


export function getTextFromXML() { //for reader1, dep
    const xml = require('@assets/picf_nounphrases.xml');
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

const subTextArray = ($, elem ,subNode: string): string[] => {
    return $(elem).children(subNode).toArray().map((el, i) => $(el).text());
} 

type sentence = {text: string, nounPhrases: string[], paragraphNumber: number}
export function getJSONFromXML() {
    // const xml = require('@assets/picf_nounphrases.xml');
    // var $ = cheerio.load(xml, {
    //   xmlMode: true
    // });

    // let pText: sentence[] = $('p:not(caption p)')
    //   .toArray()
    //   .map((p, i) => {
    //     const spans = $(p)
    //       .children('span')
    //       .toArray();
    //       const sentences = spans.map((span, iSpan) => {
    //         return {text: $(span).text(), 
    //             nounPhrases: subTextArray($, span, 'np'),
    //             paragraphNumber: i}
    //       });
    //     return sentences
    //   });
}

getJSONFromXML()