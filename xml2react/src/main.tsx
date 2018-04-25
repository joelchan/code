import * as React from 'react';
import * as ReactDOM from 'react-dom';
import * as glamorous from 'glamorous';
import { ThemeProvider, Div, Img, Span, Input } from 'glamorous';
import * as reactStringReplace from 'react-string-replace';
import * as d3 from 'd3';
import {getTextFromXML} from './xml';
var {pText, imgsCaptions} = getTextFromXML();
import * as utils from 'utils'
import {Reader1} from './Reader1'
import {Linker1} from './Linker1'

var colorScale = d3.scaleOrdinal(d3.schemePastel1) as any;
const theme = {
  main: { color: 'red' }
};
import keydown from 'react-keydown';

class App extends React.Component<any, any> {
  render(){
    return (
      // <Reader1 text={pText}></Reader1>
      <Linker1 />
    )
  }
}

// "hard" condition -> high cost scenario -> imagine needing a ~$1500 car repair -> high monetary concerns -> the poor only
// "easy" condition -> low cost scenario  -> imagine needing a ~$150 car repair -> low monetary concerns -> poor & rich



ReactDOM.render(<App text={pText} />, document.getElementById('root'));
