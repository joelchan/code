import * as React from 'react';
import * as ReactDOM from 'react-dom';
import * as glamorous from 'glamorous';
import { ThemeProvider, Div, Img, Span, Input } from 'glamorous';
import * as reactStringReplace from 'react-string-replace';
import * as d3 from 'd3';
import { getTextFromXML, getJSONFromXML } from './xml';
var { pText, imgsCaptions } = getTextFromXML();
import * as utils from 'utils';

export class Linker1 extends React.Component<any, any> {
  state = {
    sentences: null
  };

  componentWillMount() {
    this.setState({ sentences: getJSONFromXML() });
  }

  filterSentences(sentences) {
      
  }

  render() {
    const { sentences } = this.state;
    return (
      <div>
        {pText[6].map((text, i) => {
          return (
            <Div key={i}>
              {text}
              <div>
                <Input width="100%" marginBottom={'8px'} />
              </div>
            </Div>
          );
        })}
      </div>
    );
  }
}

// "hard" condition -> high cost scenario -> imagine needing a ~$1500 car repair -> high monetary concerns -> the poor only
// "easy" condition -> low cost scenario  -> imagine needing a ~$150 car repair -> low monetary concerns -> poor & rich
