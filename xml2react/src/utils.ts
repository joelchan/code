export function getSelectedTextFromWindow(trim: boolean = true): string|null {
  // 
  let text = window.getSelection().toString();
  if (text.length > 0) {
    return trim ? text.trim() : text;
  } else {
    return null;
  }
};
