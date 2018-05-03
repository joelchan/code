import { Editor } from 'slate-react';
import { Value } from 'slate';
import * as React from 'React';
import Plain from 'slate-plain-serializer';
import { WordCount } from './WordCountPlugin'; // wraps around the slate editor
import { MarkHotkey } from './MarkHotKeyPlugin'; 
import { WrapInlineHotKey } from './WrapInlineHotKeyPlugin';
import * as slateUtils from './slateUtils';
import { Span, P, Div } from 'glamorous'; 
import { Portal } from 'react-portal';
import { getCaretRect } from './Tooltip/caret-position';
import { PortalWithState } from 'react-portal';
import * as fuzzy from 'fuzzy';
import renderHTML from 'react-render-html';
import {BoldMark, renderNode, renderMark} from './EditorRenderers'
import {md_shadow} from './Css'
import {topics} from './exampleData'

const initialValue = Plain.deserialize(
  'This is editable plain text, just like a <textarea>! \n asdf'
); // slate needs a fairly complex data structure of nested nodes

const boldPlugin = MarkHotkey({
  type: 'bold',
  key: 'b'
});

const wrapInline = WrapInlineHotKey({ key: '`', type: 'meta' });
const plugins = [boldPlugin, wrapInline];

// selection, document, history all create a change object
// marks vs inline: marks attach to chars and don't change the structure
// The anchor is where a range starts, and the focus is where it ends.
export class SlateEditor extends React.Component<any, any> {
  state = {
    value: initialValue,
    caretRect: null,
    isPortalActive: true,
    currentWord: '',
    suggestionsToSearch: topics,
    suggestionsToShow: []
  };
  
  editorRef;
  setEditorRef = (element) => {
    this.editorRef = element;
  };

  onChange = ({ value }) => {
    // editor has changed (including cursor/selection)
    const caretRect = getCaretRect();
    const { text } = slateUtils.getCurrentWord(value.anchorText.text, value.anchorOffset);
    const hasSemicolon = text.includes(';');
    const isLongEnough = text.length > 0;
    
    if (hasSemicolon && isLongEnough) {
      console.log(text.split(';'))
      // here we could grab the change
    }

    if (!hasSemicolon && isLongEnough) { //if semicolon then dont update
      var options = { pre: '<b>', post: '</b>' };
      var results = fuzzy.filter(text, this.state.suggestionsToSearch, options);
      this.setState({ suggestionsToShow: results.map((el) => el.string) });
    }
   
    this.setState({ value, caretRect, currentWord: text });
  };

  // Render the editor.
  render() {
    const { caretRect, currentWord, suggestionsToShow } = this.state;
    const magicalOffset = 16;

    return (
      <div ref={this.setEditorRef}>
        <Editor
          plugins={plugins}
          value={this.state.value}
          onChange={this.onChange}
          renderNode={renderNode}
          renderMark={renderMark}
          style={{...md_shadow, padding: '2px', margin: '6px'}}
        />
        <PortalWithState closeOnEsc defaultOpen>
          {({ openPortal, closePortal, isOpen, portal }) => {
            return (
              <React.Fragment>
                <button onClick={openPortal}>Open Portal</button>
                {caretRect && suggestionsToShow.length > 0 &&
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
                      <ul style={{listStyleType: 'none', padding: '6px', margin: '0'}}>
                        {suggestionsToShow.map((sug, i) => {
                          return <li  key={i} style={{border: '1px sold lightgrey'}}> {renderHTML(sug)}</li>;
                        })}
                      </ul>
                    </Div>
                  )}
              </React.Fragment>
            );
          }}
        </PortalWithState>
      </div>
    );
  }
}