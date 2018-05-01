// Import the Slate editor.
import { Editor } from 'slate-react';
// Import the `Value` model.
import { Value } from 'slate';
import * as React from 'React';
import SuggestionsPlugin from 'slate-suggestions';

const suggestions = [
  {
    key: 'asdf',
    value: 'asdf',
    suggestion: 'asdf' // Can be string or react component
  }
  // Some other suggestions
];

const suggestionsPlugin = SuggestionsPlugin({
  trigger: '@',
  capture: /@([\w]*)/,
  suggestions,
  onEnter: (suggestion) => {
    console.log(suggestion);
  }
});

// Extract portal component from the plugin
const { SuggestionPortal } = SuggestionsPlugin;

// Add the plugin to your set of plugins...
const plugins = [SuggestionsPlugin];
// Create our initial value...
// const existingValue = JSON.parse(localStorage.getItem('content'))
const initialValue = Value.fromJSON({
  document: {
    nodes: [
      {
        object: 'block',
        type: 'paragraph',
        nodes: [
          {
            object: 'text',
            leaves: [
              {
                text: 'A line of text in a paragraph.'
              }
            ]
          }
        ]
      }
    ]
  }
});

function MarkHotkey(options) {
  const { type, key } = options;
  // Return our "plugin" object, containing the `onKeyDown` handler.
  return {
    onKeyDown(event, change) {
      // Check that the key pressed matches our `key` option.
      if (!event.ctrlKey || event.key != key) return null;
      // Prevent the default characters from being inserted.
      event.preventDefault();
      // Toggle the mark `type`.
      change.toggleMark(type);
      return true;
    }
  };
}

// Initialize our bold-mark-adding plugin.
const boldPlugin = MarkHotkey({
  type: 'bold',
  key: 'b'
});
// Create an array of plugins.
const plugin = [boldPlugin];

function logText(value, byNode: boolean = false) {
  if (byNode) {
    let textNodes = value.document.getTexts();
    textNodes.forEach((node) => {
      const { key, text } = node;
      console.log(key, text);
    });
  } else {
    console.log(value.document.text);
  }
  console.log(
    value.document
      .getTexts()
      .map((x) => x.text)
      .toJSON()
  );
}

interface SlateSelection {
  object: string;
  anchorKey: string;
  anchorOffset: number;
  focusKey: string;
  focusOffset: number;
  isBackward: boolean;
  isFocused: boolean;
  marks?: any;
}
function logSelectionRange(value) {
  const selection: SlateSelection = value.selection.toJSON();
  const doc = value.document;
  console.log('selection:', value.selection.toJSON());
  console.log('anchorText:', value.anchorText.text);
  console.log('regex', getSpaceIndexes(value.anchorText.text))
}

function getSpaceIndexes(str) {
  var re = /\s/g;
  let match;
  let results = [];
do {
  match = re.exec(str);
  if (match) {
    console.log(match.index)
    results.push(match.index);
  }
} while (match);
  return results
}

function nearest(num: number, numArr: number[]){
  // left and right
  // return textnode start/end for edge words
}
// selection, document, history all create a change object
// marks vs inline: marks attach to chars and don't change the structure
// The anchor is where a range starts, and the focus is where it ends.
export class SlateEditor extends React.Component<any, any> {
  // Set the initial value when the app is first constructed.
  state = {
    value: initialValue
  };
  // On change, update the app's React state with the new editor value.
  onChange = ({ value }) => {
    // Check to see if the document has changed before saving.
    // if (value.document != this.state.value.document) {
    //   const content = JSON.stringify(value.toJSON())
    //   localStorage.setItem('content', content)
    // }

    logSelectionRange(value);
    // logText(value, true)
    this.setState({ value });
  };

  onKeyDown = (event, change, editor) => {
    if (!event.ctrlKey) return null;
    // Decide what to do based on the key code...
    switch (event.key) {
      // When "B" is pressed, add a "bold" mark to the text.
      case 'b': {
        event.preventDefault();
        change.toggleMark('bold');
        return true;
      }
      // When "`" is pressed, keep our existing code block logic.
      case '`': {
        const selection: SlateSelection = change.value.selection;

        event.preventDefault();
        change.insertText('code');
        return true;
      }
      case '`': {
        const isCode = change.value.blocks.some((block) => block.type == 'code');
        event.preventDefault();
        change.setBlocks(isCode ? 'paragraph' : 'code');
        return true;
      }
      default:
        return null;
    }
  };

  // Define a React component to render bold text with.
  BoldMark(props) {
    return <strong>{props.children}</strong>;
  }

  CodeNode(props) {
    // You must mix the attributes into your component.
    return (
      <pre {...props.attributes}>
        <code>{props.children}</code>
      </pre>
    );
  }

  // Add a `renderNode` method to render a `CodeNode` for code blocks.
  renderNode = (props) => {
    switch (props.node.type) {
      case 'code':
        return <this.CodeNode {...props} />;
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
          onKeyDown={this.onKeyDown}
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
