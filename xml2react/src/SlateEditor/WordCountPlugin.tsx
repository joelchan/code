import * as React from 'React';
import ReactJson from 'react-json-view'

export function WordCount(options?: any) {
    // slatejs plugin
    return {
      renderEditor(props) {
        console.log(props)
        return (
          <div>
            <div>{props.children}</div>
            <span className="word-counter">
              Word Count: {props.value.document.text.split(' ').length} {options}
            </span>
            <ReactJson src={props.value.toJSON()} />
          </div>
        )
      },
    }
  }