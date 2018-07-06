import { extendToWord } from './slateUtils';

export function WrapInlineHotKey(options: { type: 'meta'; key: string }) {
  const { type, key } = options;

  // Return our "plugin" object, containing the `onKeyDown` handler.
  return {
    onKeyDown(event, change, editor) {
      // Check that the key pressed matches our `key` option.
      if (!event.ctrlKey || event.key !== key) return null;

      // Prevent the default characters from being inserted.
      event.preventDefault();

      if (editor.value.selection.isExpanded) {
        // Wrap the selected text with an inline element
        change.wrapInline(type).collapseToEnd();
      } else {
        // Expand the current selection and then wrap that.
        change
          .call(extendToWord)
          .wrapInline(type)
          .collapseToEnd();
      }
    }
  };
}
