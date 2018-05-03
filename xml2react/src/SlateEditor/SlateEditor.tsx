import { Editor } from 'slate-react';
import { Value } from 'slate';
import * as React from 'React';
import Plain from 'slate-plain-serializer';

// Add the plugin to your set of plugins...
import { WordCount } from './WordCountPlugin';
import { MarkHotkey } from './MarkHotKeyPlugin';
import { WrapInlineHotKey } from './WrapInlineHotKeyPlugin';
import * as slateUtils from './slateUtils';
import { Span, P, Div } from 'glamorous';
import { Portal } from 'react-portal';
import position from './Tooltip/caret-position';
import { getCaretRect } from './Tooltip/caret-position';
import { PortalWithState } from 'react-portal';
import * as fuzzy from 'fuzzy';
import renderHTML from 'react-render-html';

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
    suggestionsToSearch: [
      'sensemaking',
      'formalism',
      'information management',
      'visualization',
      'data viz'
    ],
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
    if (text.length > 0) {
      var options = { pre: '<b>', post: '</b>' };

      var results = fuzzy.filter(text, this.state.suggestionsToSearch, options);
      this.setState({ suggestionsToShow: results.map((el) => el.string) });
      console.log(text, this.state.suggestionsToSearch, results.map((el) => el.string));
    }

    this.setState({ value, caretRect, currentWord: text });
  };

  // Define a React component to render bold text with.
  BoldMark(props) {
    return <strong>{props.children}</strong>;
  }

  renderNode = (props) => {
    const { node, attributes, children } = props;

    switch (props.node.type) {
      case 'meta':
        return (
          <Span {...attributes} contentEditable={false} title="meta test">
            {' '}
            {children}{' '}
          </Span>
        );
      default:
        return null;
    }
  };

  // Add a `renderMark` method to render marks.
  renderMark = (props) => {
    switch (props.mark.type) {
      case 'bold':
        return <this.BoldMark {...props} />;
      default:
        return null;
    }
  };

  // todo: reuse as shadow drop
  editorStyle = {
    boxShadow: '0 2px 3px rgba(0,0,0,0.16), 0 2px 3px rgba(0,0,0,0.23)',
    borderRadius: '2px',
    padding: '6px',
    margin: '10px',
    outline: '1px solid lightgrey'
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
          renderNode={this.renderNode}
          renderMark={this.renderMark}
          style={this.editorStyle}
        />
        <PortalWithState closeOnEsc>
          {({ openPortal, closePortal, isOpen, portal }) => {
            return (
              <React.Fragment>
                <button onClick={openPortal}>Open Portal</button>
                {caretRect &&
                  portal(
                    <Div
                      position="absolute"
                      left={caretRect.left + 'px'}
                      top={caretRect.top - magicalOffset + 36 + 'px'}
                      outline="1px solid green"
                      background="white"
                      {...this.editorStyle}
                      padding="2px"
                      margin="0px"
                    >
                      <ul>
                        {suggestionsToShow.map((sug) => {
                          return <li> {renderHTML(sug)}</li>;
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
