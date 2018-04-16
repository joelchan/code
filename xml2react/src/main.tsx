import * as React from 'react';
import * as ReactDOM from 'react-dom';
import * as cheerio from 'cheerio';
import * as glamorous from 'glamorous';
import { ThemeProvider, Div, Img } from 'glamorous';
import * as reactStringReplace from 'react-string-replace';
import * as d3 from 'd3';
var colorScale = d3.scaleOrdinal(d3.schemePastel1) as any;
console.log(colorScale(0).toString());
const theme = {
  main: { color: 'red' }
};

const xml = require('@assets/picf.xml');
var $ = cheerio.load(xml, {
  xmlMode: true
});


let imgsCaptions: {[ids:string]: string}[] = $('fig').toArray()
.map((el, i) => {
  const href = $(el).children('graphic').attr("xlink:href");
  const caption = $(el).children('caption').text().trim();
  return {href, caption}
});

console.log(imgsCaptions[0])

// todo: util
let pText: string[] = $('p:not(caption p)')
  .toArray()
  .map((el, i) => {
    return $(el).text();
  });


class App extends React.Component<{ text: string[] }, any> {
  state = {
    highlightedPhrase: 'cognitive'
  };

  updateStateFromSelectedText = () => {
    const text = window
      .getSelection()
      .toString()
      .trim();
    if (text.length > 0) {
      this.setState({
        highlightedPhrase: text
      });
    }
  };

  render() {
    let wordPattern = new RegExp(`(${this.state.highlightedPhrase})`, 'gim');


    const phraseInSentence = 
          `[A-Z][^\\.;\\?\\!]*(?:${this.state.highlightedPhrase})+[^\\.;\\?\\!]*`
    const phraseStartsSentence = `${this.state.highlightedPhrase}*[^\\.;\\?\\!]*`
    let sentencePattern = new RegExp(
      `(${phraseInSentence}|${phraseStartsSentence})`,
      'gim'
    );
    let divs = this.props.text.map((t, ti) => {
      return (
        <Div key={ti} onMouseUp={(e) => this.updateStateFromSelectedText()}>
          <Div background={colorScale(ti % 9)}>{ti + 1}</Div>
          <Highlight text={t} toMatch={wordPattern} />
        </Div>
      );
    });
    let divsWithMatch = this.props.text.map((t, ti) => {
      const retext = t.match(sentencePattern);
      if (retext !== null) {
        return (
          <Div key={ti} onMouseUp={(e) => this.updateStateFromSelectedText()}>
            <Div background={colorScale(ti % 9)}>{ti + 1}</Div>
            {retext.map((retext, i) => {
              return (
                <Div key={i}>
                  <Highlight text={retext + '.'} toMatch={wordPattern} />
                </Div>
              );
            })}
          </Div>
        );
      } else {
        return null;
      }
    });

    return (
      <Div>
        <Div display='flex' onMouseUp={(e) => this.updateStateFromSelectedText()}>{imgsWithMatch(wordPattern)}</Div>
        <hr/>
        <Div display={'flex'} flexDirection="row">
          <Div flex={1} paddingRight="10px">
            {divs}
          </Div>
          <Div flex={1} paddingLeft="10px" borderLeft="1px solid black">
            {divsWithMatch}
          </Div>
        </Div>
      </Div>
    );
  }
}

function imgsWithMatch(wordPattern) {
 return imgsCaptions.map((imgCap, i) => {
    return (
      <Div>
        <Img maxWidth={'45vw'} src={require("@assets/" + imgCap.href)} />
        <Div>
        <Highlight text={imgCap.caption} toMatch={wordPattern} /> </Div>
      </Div>
    )
})
}

function Highlight(props: { text: string; toMatch: string | RegExp }) {
  return reactStringReplace(props.text, props.toMatch, (match, mi) => (
    <span
      key={mi}
      style={{
        fontWeight: 'bold'
      }}
    >
      {match}
    </span>
  ));
}

ReactDOM.render(<App text={pText} />, document.getElementById('root'));
