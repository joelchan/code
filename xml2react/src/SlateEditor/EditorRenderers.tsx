import * as React from 'React';
import { Span, P, Div } from 'glamorous';

export function BoldMark(props) {
  return <strong>{props.children}</strong>;
}

export function renderNode(props) {
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
}

export function renderMark(props) {
  switch (props.mark.type) {
    case 'bold':
      return <BoldMark {...props} />;
    default:
      return null;
  }
}
