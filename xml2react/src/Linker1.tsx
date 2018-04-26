import * as React from 'react';
import * as ReactDOM from 'react-dom';
import * as glamorous from 'glamorous';
import { ThemeProvider, Div, Img, Span, Input } from 'glamorous';
import * as reactStringReplace from 'react-string-replace';
import * as d3 from 'd3';
import { getTextFromXML, getJSONFromXML } from './xml';
var { pText, imgsCaptions } = getTextFromXML();
import * as utils from 'utils';
import { SlateEditor } from './SlateEditor';
import { Button } from 'antd';
import 'antd/lib/button/style/index.css';
import { Tags } from './Tags/index';

export class Linker1 extends React.Component<any, { sentences: sentence[]; value: any }> {
  state = {
    sentences: [{ text: '', id: '', nounPhrases: [], paragraphNumber: 0 }],
    value: ''
  };

  componentWillMount() {
    this.setState({ sentences: getJSONFromXML() });
  }

  filterSentences(sentences) {}

  handleChange = (event, newValue, newPlainTextValue, mentions) => {
    this.setState({ value: newValue });
  };
  // Item = ({ entity: { name, char } }) => <div>{`${name}: ${char}`}</div>
  render() {
    const sentences = this.state.sentences.filter((s) => s.paragraphNumber === 6);
    const connectors = ['has', 'is', 'contains', 'happen in'].map(x=>({name: x}))
    return (
      <div>
        {[sentences[0]].map((sentence, i) => {
          const nounPhrases = sentence.nounPhrases.map(x=>({name: x}))
          console.log(nounPhrases)
          return (
            <Div key={sentence.id}>
              {sentence.text}
              <Div display='flex' width="100%">
                 <AutoComplete suggestions={nounPhrases}></AutoComplete>
                 <AutoComplete suggestions={connectors}></AutoComplete>
                 <AutoComplete suggestions={nounPhrases}></AutoComplete>
              </Div>
            </Div>
          );
        })}
      </div>
    );
  }
}
import Autosuggest from 'react-autosuggest';

// Imagine you have a list of languages that you'd like to autosuggest.


class AutoComplete extends React.Component<any, any> {
  state = {
    value: '',
    suggestions: []
  };
  languages = [
    {
      name: 'C',
      year: 1972
    },
    {
      name: 'Elm',
      year: 2012
    }
  ];
  
  // Teach Autosuggest how to calculate suggestions for any given input value.
  getSuggestions = (value) => {
    const inputValue = value.trim().toLowerCase();
    const inputLength = inputValue.length;
  
    return inputLength === 0 ? [] : this.props.suggestions.filter(lang =>
      lang.name.toLowerCase().slice(0, inputLength) === inputValue
    );
  };
  
  // When suggestion is clicked, Autosuggest needs to populate the input
  // based on the clicked suggestion. Teach Autosuggest how to calculate the
  // input value for every given suggestion.
  getSuggestionValue = suggestion => suggestion.name;
  
  // Use your imagination to render suggestions.
  renderSuggestion = suggestion => (
    <div>
      {suggestion.name}
    </div>
  );

  onChange = (event, { newValue }) => {
    this.setState({
      value: newValue
    });
  };

  // Autosuggest will call this function every time you need to update suggestions.
  // You already implemented this logic above, so just use it.
  onSuggestionsFetchRequested = ({ value }) => {
    this.setState({
      suggestions: this.getSuggestions(value)
    });
  };

  // Autosuggest will call this function every time you need to clear suggestions.
  onSuggestionsClearRequested = () => {
    this.setState({
      suggestions: []
    });
  };

  render() {
    const { value, suggestions } = this.state;

    // Autosuggest will pass through all these props to the input.
    const inputProps = {
      placeholder: '',
      value,
      onChange: this.onChange
    };

    // Finally, render it!
    return (
      <Autosuggest
        suggestions={suggestions}
        onSuggestionsFetchRequested={this.onSuggestionsFetchRequested}
        onSuggestionsClearRequested={this.onSuggestionsClearRequested}
        getSuggestionValue={this.getSuggestionValue}
        renderSuggestion={this.renderSuggestion}
        inputProps={inputProps}
      />
    );
  }
}