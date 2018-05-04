import * as _ from 'lodash';
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

export function extendToWord(change, startOfWord, endOfWord) {
  const startOffset = change.value.selection.startOffset;
  const endOffset = change.value.selection.endOffset;
  change.moveOffsetsTo(startOfWord - startOffset, endOfWord - endOffset);
}

import { greaterNumber, lowerNumber } from 'get-closest';
export function getCurrentWord(text: string, cursorLocInText: number) {
  const spaceIndexes: number[] = getSpaceIndexes(text);
  const isIndexSpace = spaceIndexes.includes(cursorLocInText - 1);
  const ix: number = isIndexSpace ? cursorLocInText : cursorLocInText - 1;
  const spaceToTheLeft: number = spaceIndexes[lowerNumber(ix, spaceIndexes)] | 0;
  const _spaceToTheRight: number = spaceIndexes[greaterNumber(ix, spaceIndexes)];
  const spaceToTheRight = _spaceToTheRight !== undefined ? _spaceToTheRight : text.length;

  return {
    start: spaceToTheLeft,
    end: spaceToTheRight,
    text: text.slice(spaceToTheLeft, spaceToTheRight).trim(),
    spaceBefore: spaceToTheLeft > 0 ? ' ' : '',
    spaceAfter: spaceToTheRight < text.length ? ' ' : ''
  };
}
export const keyCommand2Index = { f: 0, d: 1, s: 2, a: 3 };
export const Index2KeyCommanrd = _.invert(keyCommand2Index)
console.log(Index2KeyCommanrd)
export function keyCommandToReplaceText(currentWord, suggestions, nodeText, change) {
  const { text, start, end, spaceBefore, spaceAfter } = currentWord;
  const [word, keyCommand] = text.split(';');
  const suggestionIx = _.get(keyCommand2Index, keyCommand, null);
  const isWordCap = /^[A-Z]/.test(word);
  //todo: caps after .space with regex
  const reDotSpace = /\.\s+/;
  let isSentenceStart = false;
  
  if (suggestionIx !== null) {
    const sug = suggestions[suggestionIx];
    const textToInsert = (isWordCap || start === 0 || isSentenceStart)
      ? sug.charAt(0).toUpperCase() + sug.slice(1)
      : sug;
    change.moveOffsetsTo(start, end);
    change.insertText(spaceBefore + textToInsert);
  }
}
