import * as React from 'react';
import * as ReactDOM from 'react-dom';
import * as glamorous from 'glamorous';
import { ThemeProvider, Div, Img, Span } from 'glamorous';
import * as reactStringReplace from 'react-string-replace';
import * as d3 from 'd3';
import {getTextFromXML} from './xml';
var {pText, imgsCaptions} = getTextFromXML();

var colorScale = d3.scaleOrdinal(d3.schemePastel1) as any;
const theme = {
  main: { color: 'red' }
};
import keydown from 'react-keydown';

@keydown
class App extends React.Component<{ text: string[][] }, any> {
  state = {
    highlightedPhrase: 'cognitive',
    paragraphIx: 0,
    sentenceIx: 0,
    key: 'n/a'
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

  componentWillReceiveProps( nextProps ) {
    const { keydown: { event } } = nextProps;
    if ( event ) {
      switch (event.key) {
        case 'f': this.setState({sentenceIx: this.state.sentenceIx+1}); break;
        case 'ArrowLeft': this.setState({sentenceIx: this.state.sentenceIx-1}); break;
        case 'ArrowRight': this.setState({sentenceIx: this.state.sentenceIx+1}); break;
        default: break;
      }

      this.setState( { key: event.key } );
    }
  }

  render() {
    let wordPattern = new RegExp(`(${this.state.highlightedPhrase})`, 'gim');

    let divs = this.props.text.map((p, pi) => {
      const isParagraphSelected = this.state.paragraphIx === pi;
      return (
        <Div key={pi} onMouseUp={(e) => this.updateStateFromSelectedText()}>
          <Div outline="1px solid black" background="lightgrey" textAlign="center">
            {pi + 1}
          </Div>
          {p.map((sentence, sentencei) => {
            const doesSentenceIxMatch = this.state.sentenceIx === sentencei;
            const isSentenceSelected = doesSentenceIxMatch && isParagraphSelected;
            
            return (
              <Span key={sentencei} background={isSentenceSelected ? '#C7E9C0':'none'}>
                <Highlight text={sentence} toMatch={wordPattern} />
              </Span>
            );
          })}
        </Div>
      );
    });
    // let divsWithMatch = this.props.text.map((t, ti) => {
    //   const retext = t.match(sentencePattern);
    //   if (retext !== null) {
    //     return (
    //       <Div key={ti} onMouseUp={(e) => this.updateStateFromSelectedText()}>
    //         <Div background={colorScale(ti % 9)}>{ti + 1}</Div>
    //         {retext.map((retext, i) => {
    //           return (
    //             <Div key={i}>
    //               <Highlight text={retext + '.'} toMatch={wordPattern} />
    //             </Div>
    //           );
    //         })}
    //       </Div>
    //     );
    //   } else {
    //     return null;
    //   }
    // });

    return (
      <Div>
        {this.state.key}
        <Div display="flex" onMouseUp={(e) => this.updateStateFromSelectedText()}>
          {imgsWithMatch(wordPattern)}
        </Div>
        <hr />
        <Div display={'flex'} flexDirection="row">
          <Div flex={1} paddingRight="10px">
            {divs}
          </Div>
          {/* <Div flex={1} paddingLeft="10px" borderLeft="1px solid black">
            {divsWithMatch}
          </Div> */}
        </Div>
      </Div>
    );
  }
}

function imgsWithMatch(wordPattern) {
  return imgsCaptions.map((imgCap, i) => {
    return (
      <Div>
        <Img maxWidth={'45vw'} src={require('@assets/' + imgCap.href)} />
        <Div>
          <Highlight text={imgCap.caption} toMatch={wordPattern} />{' '}
        </Div>
      </Div>
    );
  });
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

function matchSentencesRegex() {
  // delete?
  let wordPattern = new RegExp(`(${this.state.highlightedPhrase})`, 'gim');
  const phraseInSentence = `[A-Z][^\\.;\\?\\!]*(?:${this.state.highlightedPhrase})+[^\\.;\\?\\!]*`;
  const phraseStartsSentence = `${this.state.highlightedPhrase}*[^\\.;\\?\\!]*`;
  let sentencePattern = new RegExp(`(${phraseInSentence}|${phraseStartsSentence})`, 'gim');
}
