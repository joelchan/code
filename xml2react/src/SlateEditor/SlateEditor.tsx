import { Editor } from 'slate-react';
import { Value } from 'slate';
import * as React from 'React';
import Plain from 'slate-plain-serializer';
import { WordCount } from './WordCountPlugin'; // wraps around the slate editor
import { MarkHotkey } from './MarkHotKeyPlugin';
import { WrapInlineHotKey } from './WrapInlineHotKeyPlugin';
import * as slateUtils from './slateUtils';
import { Span, P, Div, Textarea } from 'glamorous';
import { Portal } from 'react-portal';
import { getCaretRect } from './Tooltip/caret-position';
import { PortalWithState } from 'react-portal';
import * as fuzzy from 'fuzzy';
import renderHTML from 'react-render-html';
import { BoldMark, renderNode, renderMark } from './EditorRenderers';
import { md_shadow } from './Css';
import { topics } from './exampleData';
import * as _ from 'lodash';
import { DefaultButton, IButtonProps } from 'office-ui-fabric-react/lib/Button';
import { Reader1 } from '../Reader1';
const initialValue = Plain.deserialize(''); // slate needs a fairly complex data structure of nested nodes
import { getTextFromXML, getJSONFromXML } from '../xml';
import { Highlight } from '../Reader1';
const boldPlugin = MarkHotkey({
  type: 'bold',
  key: 'b'
});

const wrapInline = WrapInlineHotKey({ key: '`', type: 'meta' });
const plugins = [boldPlugin, wrapInline];

const getReadingText = gql`
  {
    readingText @client
  }
`;

// selection, document, history all create a change object
// marks vs inline: marks attach to chars and don't change the structure
// The anchor is where a range starts, and the focus is where it ends.
interface EditorProps {
  readingText: string;
  suggestionsToSearch: any[];
}
// todo: regex things ()[] in autocomplete cause errors
class _SlateEditor extends React.Component<EditorProps, any> {
  editorRef;
  // todo: clear out unused state, add interface
  state = {
    value: initialValue,
    caretRect: null,
    isPortalActive: true,
    currentWord: '',
    suggestionsToSearch: topics,
    suggestionsToShow: [],
    sentences: [{ text: '', id: '', nounPhrases: [], paragraphNumber: 0 }],
    readingLocation: { sentenceNumber: 0, paragraphNumber: 0 },
    nounPhrases: [], //todo: not used?
    addedPhrases: [], //todo: delete if deleted from editor
    pastedText: 'We discuss some implications for poverty policy.'
  };

  setEditorRef = (element) => {
    this.editorRef = element;
  };

  updateSentences = (xml: string) => {
    const sentences = getJSONFromXML(xml);
    this.setState({ sentences });
    const text2show = extractSentenceData(sentences, this.state.readingLocation);
    this.setState({ suggestionsToSearch: text2show.nounPhrases });
    console.log('update', text2show);
  };

  onChange = (change) => {
    let { value } = change; //this value won't update, but change.value will
    // editor has changed (including cursor/selection)
    const caretRect = getCaretRect();
    const currentWord = slateUtils.getCurrentWord(value.anchorText.text, value.anchorOffset);
    const { text, start, end, spaceBefore, spaceAfter } = currentWord;
    const hasSemicolon = text.includes(';');
    const isLongEnough = text.length > 0;

    if (!hasSemicolon && isLongEnough) {
      //if semicolon then dont update
      var options = { pre: '<b>', post: '</b>' };
      var results = fuzzy.filter(text, this.props.suggestionsToSearch, options);
      const toShow = results.map((el) => ({ html: el.string, text: el.original }));
      this.setState({ suggestionsToShow: toShow });
    }

    if (hasSemicolon && isLongEnough) {
      const suggestions = this.state.suggestionsToShow.map((x) => x.text);
      if (text.split(';').length === 2) {
        const selectedSuggestion = slateUtils.keyCommandToReplaceText(
          currentWord,
          suggestions,
          text,
          change
        );
        if (selectedSuggestion !== null) {
          console.log(selectedSuggestion);
          this.setState({
            addedPhrases: [...this.state.addedPhrases, selectedSuggestion]
          });
        }
      }
    }

    this.setState({ value: change.value, caretRect, currentWord: text });
  };

  onSubmitText = (value: string, xml: string) => {
    console.log('xml update', value, xml);
    this.setState({ pastedText: value });
    this.updateSentences(xml);
  };

  // Render the editor.
  render() {
    //todo: actual entity nodes in editor and reader
    let wordPattern = new RegExp(`(${this.state.addedPhrases.join('|')})`, 'gim');
    const { sentences, readingLocation, addedPhrases } = this.state;
    const text2show = extractSentenceData(sentences, readingLocation);
    const { caretRect, currentWord, suggestionsToShow } = this.state;
    const magicalOffset = 16;
    const loaded = this.props.readingText !== '' && this.props.suggestionsToSearch.length > 0;
    return (
      <div ref={this.setEditorRef} style={{ margin: '6px' }}>
      {!loaded && <Div>Enter text bellow to test out autocomplete on your text.</Div>}
        <Highlight text={this.props.readingText} toMatch={wordPattern} />
          <Editor
            spellCheck={false}
            plugins={plugins}
            value={this.state.value}
            onChange={this.onChange}
            renderNode={renderNode}
            renderMark={renderMark}
            style={{
              borderRadius: '20px',
              outline: '1px solid grey',
              padding: '2px',
              marginTop: '10px'
            }}
          />
        

        <PortalWithState closeOnEsc defaultOpen>
          {({ openPortal, closePortal, isOpen, portal }) => {
            return (
              <React.Fragment>
                <DefaultButton
                  style={{ margin: '5px' }}
                  primary={true}
                  data-automation-id="test"
                  text={isOpen ? 'Hide AutoComplete' : 'Show AutoComplete'}
                  onClick={isOpen ? closePortal : openPortal}
                />
                {caretRect &&
                  suggestionsToShow.length > 0 &&
                  portal(
                    <Div
                      position="absolute"
                      left={caretRect.left + 'px'}
                      top={caretRect.top - magicalOffset + 36 + 'px'}
                      outline="1px solid green"
                      background="white"
                      {...md_shadow}
                      padding="2px"
                      margin="0px"
                    >
                      <ul style={{ listStyleType: 'none', padding: '4px', margin: '0' }}>
                        {suggestionsToShow.slice(0, 4).map((sug, i) => {
                          return (
                            <li
                              key={i}
                              style={{
                                border: '1px sold lightgrey',
                                marginBottom: '4px'
                              }}
                            >
                              {/* todo: seperate component */}
                              <Span
                                borderRadius="20%"
                                background="lightblue"
                                display="inline-block"
                                width="8px"
                                marginRight="6px"
                                paddingLeft="4px"
                                paddingRight="4px"
                                fontWeight="bold"
                                textAlign="center"
                                verticalAlign="middle"
                              >
                                {_.get(slateUtils.Index2KeyCommanrd, i, '.')}
                              </Span>
                              {renderHTML(sug.html)}
                            </li>
                          );
                        })}
                      </ul>
                    </Div>
                  )}
              </React.Fragment>
            );
          }}
        </PortalWithState>
        

        {loaded && (
          <Div fontSize='12px'>
            Text parsed by server. Input with nounphrase autocomplete enabled. Try typing things in
            the text area and type ;fdsa to autocomplete. Esc hides the autocomplete popup.
          </Div>
        )}
        {!loaded && <ReadingTextForm /> }
      </div>
    );
  }
}

const fetchXmlTagsFromNLP = gql`
  query getXMLFromNLP($text: String) {
    xmlFromNLP(text: $text)
  }
`;

// todo: is there a way to not do nest queries for local -> remote queries?
export function SlateEditor() {
  return (
    <Query query={getReadingText}>
      {(q1) => {
        return (
          <Query query={fetchXmlTagsFromNLP} variables={{ text: q1.data.readingText }}>
            {({ data }) => {
              const sentences = getJSONFromXML(data.xmlFromNLP);
              // todo: readingIndex is for moving through multiple paragraphs/sentences
              const text2show = extractSentenceData(sentences, { paragraphNumber: 0 });
              return (
                <_SlateEditor
                  readingText={text2show.text}
                  suggestionsToSearch={text2show.nounPhrases}
                />
              );
            }}
          </Query>
        );
      }}
    </Query>
  );
}

function extractSentenceData(sentences, readingIndex) {
  const sents: sentence[] = sentences.filter(
    (s) => s.paragraphNumber === readingIndex.paragraphNumber
  );
  const nounPhrases = _.flattenDeep(sents.map((s) => s.nounPhrases));
  return { text: sents.map((s) => s.text).join(' '), nounPhrases };
}

import { gql } from 'apollo-boost';
import { Query } from 'react-apollo';

function ReadingTextForm() {
  let input;
  return (
    <Query query={getReadingText}>
      {({ loading, error, data, refetch, networkStatus, client }) => {
        return (
          <Div
            position='absolute'
            bottom={0}
            width='90%'
            marginBottom='20px'
          >
            <form
              onSubmit={(e) => {
                e.preventDefault();
                client.writeData({
                  data: {
                    readingText: input.value
                  }
                });
                input.value = '';
              }}
            >
              <Div>Enter plain text here to be processed by server. It will then
                be added to the above autocomplete component. </Div>
              <textarea
                style={{ width: '100%', height: '100px' }}
                defaultValue={''}
                ref={(node) => {
                  input = node;
                }}
              />
              <br />
              <DefaultButton type="submit">
                Send To Server & Fetch Noun Phrases
              </DefaultButton>
            </form>
          </Div>
        );
      }}
    </Query>
  );
}
