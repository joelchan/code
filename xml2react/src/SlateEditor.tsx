// Import the Slate editor.
import { Editor } from 'slate-react'
// Import the `Value` model.
import { Value } from 'slate'
​import * as React from 'React'
import SuggestionsPlugin from 'slate-suggestions'

const suggestions = [
  {
    key: 'jon-snow',
    value: '@Jon Snow',
    suggestion: '@Jon Snow' // Can be string or react component
  },
  // Some other suggestions
]

const suggestionsPlugin = SuggestionsPlugin({
  trigger: '@',
  capture: /@([\w]*)/,
  suggestions,
  onEnter: (suggestion) => {
    console.log(suggestion)
  }
})

// Extract portal component from the plugin
const { SuggestionPortal } = SuggestionsPlugin

// Add the plugin to your set of plugins...
const plugins = [
    SuggestionsPlugin
]
// Create our initial value...
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
                text: 'A line of text in a paragraph.',
              },
            ],
          },
        ],
      },
    ],
  },
})

// Define our app...
export class SlateEditor extends React.Component<any,any> {
    // Set the initial value when the app is first constructed.
    state = {
      value: initialValue,
    }
  ​
    // On change, update the app's React state with the new editor value.
    onChange = ({ value }) => {
      this.setState({ value })
    }
  ​
    // Render the editor.
    render() {
      return (
        <div>
        <Editor value={this.state.value} onChange={this.onChange}   plugins={plugins}
      />
      <SuggestionPortal
    />
    </div>
    )
    }
  }