import { Editor } from 'slate-react';
import { Value } from 'slate';
import * as React from 'React';
import Plain from 'slate-plain-serializer'

// Add the plugin to your set of plugins...
import {WordCount} from './WordCountPlugin'
import {MarkHotkey} from './MarkHotKeyPlugin'
import {WrapInlineHotKey} from './WrapInlineHotKeyPlugin'
import * as slateUtils from './slateUtils'
import {Span} from 'glamorous'
import styled from 'styled-components';


const initialValue = Plain.deserialize(
  'This is editable plain text, just like a <textarea>!'
); // slate needs a fairly complex data structure of nested nodes

const boldPlugin = MarkHotkey({
  type: 'bold',
  key: 'b'
});

const wrapInline = WrapInlineHotKey({key: '`', type: "meta"})
const plugins = [boldPlugin,  wrapInline];
const SpanUp = styled.span`
  border-radius: 3px;
  padding-left: 3px;
  padding-right: 3px;
  background: transparent;
  color: palevioletred;
  border: 1px solid palevioletred;
`;

// selection, document, history all create a change object
// marks vs inline: marks attach to chars and don't change the structure
// The anchor is where a range starts, and the focus is where it ends.
export class SlateEditor extends React.Component<any, any> {
  state = {
    value: initialValue
  };

  onChange = ({ value }) => {
    slateUtils.logSelectionRange(value);
    this.setState({ value });
  };

  // Define a React component to render bold text with.
  BoldMark(props) {
    return <strong>{props.children}</strong>;
  }

  renderNode = (props) => {
    switch (props.node.type) {
      case 'meta':
        return <Span {...props} contentEditable={false} title='meta test' />;
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
    return (
      <div>
        <Editor
          plugins={plugins}
          value={this.state.value}
          onChange={this.onChange}
          renderNode={this.renderNode}
          renderMark={this.renderMark}
          style={{ border: '1px solid #4885ed', 'borderRadius:': '10px' }}
        />
      </div>
    );
  }
}
