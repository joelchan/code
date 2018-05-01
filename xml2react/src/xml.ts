import * as cheerio from 'cheerio';
var uniqid = require('uniqid');
import * as _ from 'lodash'

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

// todo: xml utils
const subTextArray = ($, elem ,subNode: string): string[] => {
    return $(elem).children(subNode).toArray().map((el, i) => $(el).text());
} 
let getSpans = ($, node) => $(node).children('span').toArray();


export function getJSONFromXML(): sentence[] {
    const xml = require('@assets/picf_nounphrases.xml');
    var $ = cheerio.load(xml, {
      xmlMode: true
    });

    let paragraphs= $('p:not(caption p)').toArray()
    const sentences = paragraphs.map((p, i) => {
        const spans = getSpans($, p)
          const sents = spans.map((span, iSpan) => {
            return {
                id: uniqid('sentence-'),
                text: $(span).text(), 
                nounPhrases: subTextArray($, span, 'np'),
                paragraphNumber: i}
          });
        return sents
      });
      return _.flatten(sentences);
}

