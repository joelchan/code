// Acquire from http://jsfiddle.net/gliheng/vbucs/12/
// see https://codepen.io/pc035860/pen/FeIEj?editors=0010

export function getCaretRect() {
  // had to hardcode a 16px offset for top that works with any margin/padding
  const selection = document.getSelection();
  if (selection.rangeCount === 0) return null;
  const range = selection.getRangeAt(0).cloneRange();
  return range.getBoundingClientRect();
}

// delete this
function position($node?, offsetx?, offsety?) {
  offsetx = offsetx || 0;
  offsety = offsety || 0;

  let nodeLeft = 0;
  let nodeTop = 0;
  if ($node) {
    nodeLeft = $node.offsetLeft;
    nodeTop = $node.offsetTop;
  }

  const pos = { left: 0, top: 0, right: 0, bottom: 0 };
  let doc: any = document;
  if (doc.selection) {
    const range = doc.selection.createRange();
    pos.left = range.offsetLeft + offsetx - nodeLeft;
    pos.top = range.offsetTop + offsety - nodeTop;
  } else if (window.getSelection) {
    const sel = window.getSelection();
    if (sel.rangeCount === 0) return null;
    const range = sel.getRangeAt(0).cloneRange();

    try {
      range.setStart(range.startContainer, range.startOffset - 1);
    } catch (e) {}

    const rect = range.getBoundingClientRect();
    if (range.endOffset === 0 || range.toString() === '') {
      // first char of line
      if (range.startContainer === $node) {
        // empty div
        if (range.endOffset === 0) {
          pos.top = 0;
          pos.left = 0;
        } else {
          // firefox need this
          console.log('UNTESTED IN FIREFOX');
          const range2 = range.cloneRange();
          range2.setStart(range2.startContainer, 0);
          const rect2 = range2.getBoundingClientRect();
          pos.left = rect2.left + offsetx - nodeLeft;
          pos.top = rect2.top + rect2.height + offsety - nodeTop;
        }
      } else {
        pos.top = (range.startContainer as any).offsetTop;
        pos.left = (range.startContainer as any).offsetLeft;
      }
    } else {
      pos.left = rect.left + offsetx - nodeLeft;
      pos.right = rect.right + offsetx - nodeLeft;
      pos.top = rect.top + offsety - nodeTop;
    }
  }
  return pos;
}

export default position;
