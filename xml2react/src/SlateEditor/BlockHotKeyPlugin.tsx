export function BlockHotKey(options) {
  const { type, normalType, key } = options;

  // Return our "plugin" object, containing the `onKeyDown` handler.
  return {
    onKeyDown(event, change) {
      // Check that the key pressed matches our `key` option.
      if (!event.ctrlKey || event.key !== key) return null;

      // Prevent the default characters from being inserted.
      event.preventDefault();

      // Determine whether any of the currently selected blocks are of type `type`.
      const isType = change.value.blocks.some((block) => block.type === type);

      // Toggle the block type depending on `isType`.
      change.setBlocks(isType ? normalType : type);
      return true;
    }
  };
}
