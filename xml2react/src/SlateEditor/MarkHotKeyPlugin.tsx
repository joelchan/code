import * as React from 'React';


export function MarkHotkey(options?) {
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