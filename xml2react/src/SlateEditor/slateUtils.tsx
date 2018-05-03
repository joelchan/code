export function logText(value, byNode: boolean = false) {
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

export function logSelectionRange(value) {
  const selection: SlateSelection = value.selection.toJSON();
  const doc = value.document;
  console.log('selection:', value.selection.toJSON());
  console.log('anchorText:', value.anchorText.text);
  console.log('regex', getSpaceIndexes(value.anchorText.text));
}

export function getSpaceIndexes(str: string): number[] {
  var re = /\s/g;
  let match;
  let results = [];
  do {
    match = re.exec(str);
    if (match) {
      results.push(match.index);
    }
  } while (match);
  return results;
}

export function hasSomeOfTypeInNode(
  change,
  valueNode: 'block' | 'span' | 'mark',
  nodeType: string
) {
  return change.value[valueNode].some((node) => node.type == nodeType);
}

export function extendToWord(change, editor) {
  // Expand the current selection to the nearest space
  const currentTextNode = change.value.anchorText;
  const startOffset = change.value.selection.startOffset;
  const endOffset = change.value.selection.endOffset;
  const endSearchText = currentTextNode.text.slice(endOffset);
  const startSearchText = currentTextNode.text
    .slice(0, startOffset)
    .split('')
    .reverse()
    .join('');
  console.log(startSearchText, endSearchText);
  let endOfWord = endSearchText.search(/\s/);
  let startOfWord = startSearchText.search(/\s/);
  if (endOfWord === -1) {
    endOfWord = endSearchText.length;
  } else {
    // endOfWord-- // We don't want to select the actual space character too
  }
  if (startOfWord === -1) {
    startOfWord = startSearchText.length;
  } else {
    //startOfWord; // We don't want to select the actual space character too
  }

  console.log(startOfWord, endOfWord);
  change.moveOffsetsTo(startOffset - startOfWord, endOffset + endOfWord);
}

import { greaterNumber, lowerNumber } from 'get-closest';
export function getCurrentWord(text: string, cursorLocInText: number) {
  const spaceIndexes: number[] = getSpaceIndexes(text);
  const isIndexSpace = spaceIndexes.includes(cursorLocInText-1);
  const ix: number = isIndexSpace ? cursorLocInText : cursorLocInText-1;
  const spaceToTheLeft: number = spaceIndexes[lowerNumber(ix, spaceIndexes)] | 0;
  const spaceToTheRight: number = spaceIndexes[greaterNumber(ix, spaceIndexes)];
  return {
    start: spaceToTheLeft,
    end: spaceToTheRight,
    text: text.slice(spaceToTheLeft, spaceToTheRight).trim()
  };
}
