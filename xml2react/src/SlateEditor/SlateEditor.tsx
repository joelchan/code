import { Editor } from 'slate-react';
import { Value } from 'slate';
import * as React from 'React';
import Plain from 'slate-plain-serializer';

// Add the plugin to your set of plugins...
import { WordCount } from './WordCountPlugin';
import { MarkHotkey } from './MarkHotKeyPlugin';
import { WrapInlineHotKey } from './WrapInlineHotKeyPlugin';
import * as slateUtils from './slateUtils';
import { Span, P } from 'glamorous';
import { Portal } from 'react-portal';
import  SuggestionsPlugin from './slate-suggestions/lib/index'
import position from './Tooltip/caret-position'
import { PortalWithState } from 'react-portal';

const suggestions = [
  {
    key: 'Jon Snow',
    value: '@Jon Snow',
    suggestion: '@Jon Snow' // Can be either string or react component
  },
  {
    key: 'John Evans',
    value: '@John Evans',
    suggestion: '@John Evans'
  }
]

const initialValue = Plain.deserialize('This is editable plain text, just like a <textarea>!'); // slate needs a fairly complex data structure of nested nodes

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
    isPortalActive: true
  };
  
  suggestionsPlugin = SuggestionsPlugin({
    trigger: '@',
    capture: /@([\w]*)/,
    suggestions,
    onEnter: (suggestion, change) => {
      const { anchorText, anchorOffset } = this.state.value
      const text = anchorText.text
      let index = { start: anchorOffset - 1, end: anchorOffset }
      if (text[anchorOffset - 1] !== '@') {
        index = slateUtils.getCurrentWord(text, anchorOffset - 1, anchorOffset - 1)
      }
      const newText = `${text.substring(0, index.start)}${suggestion.value} `
      change
        .deleteBackward(anchorOffset)
        .insertText(newText)
      return true;
    }
  })
  SuggestionPortal = this.suggestionsPlugin.SuggestionPortal;

  onChange = ({ value }) => {
    // slateUtils.logSelectionRange(value);
    this.setState({ value });
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

  // Render the editor.
  render() {
    const { SuggestionPortal } = this.suggestionsPlugin
    const pos = position() || {left: 0, top: 0}
    return (
      <P marginLeft='20px'>
        <P position='absolute' left={pos.left}></P>
        <Editor
          plugins={plugins}
          value={this.state.value}
          onChange={this.onChange}
          renderNode={this.renderNode}
          renderMark={this.renderMark}
          style={{ border: '1px solid #4885ed', 'borderRadius:': '10px' }}
        />
    <PortalWithState closeOnEsc>
      {({ openPortal, closePortal, isOpen, portal }) => {
      return (
        <React.Fragment>
          <button onClick={openPortal}>
            Open Portal
          </button>
          {portal(
            <P position='absolute' left={pos.left + 'px'} top={pos.top + 'px'}>
              This is more advanced Portal. It handles its own state.{' '}
              <button onClick={closePortal}>Close me!</button>, hit ESC or
              click outside of me.
            </P>
          )}
        </React.Fragment>
      )}}
    </PortalWithState>
      </P>
    );
  }
}
