import * as React from 'react';
import * as ReactDOM from 'react-dom';
import * as glamorous from 'glamorous';
import { ThemeProvider, Div, Img, Span } from 'glamorous';
import * as reactStringReplace from 'react-string-replace';
import * as d3 from 'd3';
import { getTextFromXML } from './xml';
var { pText, imgsCaptions } = getTextFromXML();

var colorScale = d3.scaleOrdinal(d3.schemePastel1) as any;
const theme = {
  main: { color: 'red' }
};
import keydown from 'react-keydown';

@keydown
export class Reader1 extends React.Component<{ text: string[][] }, any> {
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

  componentWillReceiveProps(nextProps) {
    const {
      keydown: { event }
    } = nextProps;
    if (event) {
      //todo: arrow to next paragraph
      switch (event.key) {
        case 'f':
          this.setState({ sentenceIx: this.state.sentenceIx + 1 });
          break;
        case 'ArrowLeft':
          this.setState({ sentenceIx: this.state.sentenceIx - 1 });
          break;
        case 'ArrowRight':
          this.setState({ sentenceIx: this.state.sentenceIx + 1 });
          break;
        default:
          break;
      }

      this.setState({ key: event.key });
    }
  }

  render() {
    let wordPattern = new RegExp(`(${this.state.highlightedPhrase})`, 'gim');

    // todo: replace this with divsWithMatch but set match to 'all'
    let divs = this.props.text.map((p, pi) => {
      const isParagraphSelected = this.state.paragraphIx === pi;
      return (
        <Div key={pi} onMouseUp={(e) => this.updateStateFromSelectedText()}>
          <Div
            outline="1px solid black"
            background="lightgrey"
            textAlign="center"
          >
            {pi + 1}
          </Div>
          {p.map((sentence, sentencei) => {
            const doesSentenceIxMatch = this.state.sentenceIx === sentencei;
            const isSentenceSelected =
              doesSentenceIxMatch && isParagraphSelected;

            return (
              <Span
                key={sentencei}
                background={isSentenceSelected ? '#C7E9C0' : 'none'}
              >
                <Highlight text={sentence} toMatch={wordPattern} />
              </Span>
            );
          })}
        </Div>
      );
    });

    // todo: replace divs component above with this but add filter prop
    let divsWithMatch = this.props.text.map((p, pi) => {
      const isParagraphSelected = this.state.paragraphIx === pi;
      return (
        <Div key={pi} onMouseUp={(e) => this.updateStateFromSelectedText()}>
          <Div
            outline="1px solid black"
            background="lightgrey"
            textAlign="center"
          >
            {pi + 1}
          </Div>
          {p.map((sentence, sentencei) => {
            let wordPattern = new RegExp(
              `(${this.state.highlightedPhrase})`,
              'gim'
            );
            const doesSentenceIxMatch = this.state.sentenceIx === sentencei;
            const isSentenceSelected =
              doesSentenceIxMatch && isParagraphSelected;
            if ((wordPattern as any).test(sentence)) {
              return (
                <Span
                  key={sentencei}
                  background={isSentenceSelected ? '#C7E9C0' : 'none'}
                >
                  <Highlight text={sentence} toMatch={wordPattern} />
                </Span>
              );
            } else {
              return null;
            }
          })}
        </Div>
      );
    });

    return (
      <Div>
        <Div display={'flex'} flexDirection="row">
          <Div flex={1} paddingRight="10px">
            {divs}
          </Div>
          <Div flex={1} paddingLeft="10px" borderLeft="1px solid black">
            {divsWithMatch}
          </Div>
        </Div>
        <Div
          display="flex"
          onMouseUp={(e) => this.updateStateFromSelectedText()}
        >
          {imgsWithMatch(wordPattern)}
        </Div>
      </Div>
    );
  }
}

function imgsWithMatch(wordPattern) {
  return imgsCaptions.map((imgCap, i) => {
    const imgName = imgCap.href.replace(/\\\"/g, '');
    console.log(imgName);
    return (
      <Div>
        <Img maxWidth={'45vw'} src={require('@assets/' + imgName)} />
        <Div>
          <Highlight text={imgCap.caption} toMatch={wordPattern} />{' '}
        </Div>
      </Div>
    );
  });
}

// bold a matched phrase
export function Highlight(props: { text: string; toMatch: string | RegExp }) {
  return reactStringReplace(props.text, props.toMatch, (match, mi) => (
    <span
      key={mi}
      style={{
        fontWeight: 'bold',
        color: '#4078F2'
      }}
    >
      {match}
    </span>
  ));
}

// use this to parse sentences in js with regex
function matchSentencesRegex() {
  // delete?
  let wordPattern = new RegExp(`(${this.state.highlightedPhrase})`, 'gim');
  const phraseInSentence = `[A-Z][^\\.;\\?\\!]*(?:${
    this.state.highlightedPhrase
  })+[^\\.;\\?\\!]*`;
  const phraseStartsSentence = `${this.state.highlightedPhrase}*[^\\.;\\?\\!]*`;
  let sentencePattern = new RegExp(
    `(${phraseInSentence}|${phraseStartsSentence})`,
    'gim'
  );
}
