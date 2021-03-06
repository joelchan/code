const pdf2htmlexCss = {
  _: "display:.*?",
  m: "transform",
  w: "width",
  h: "height",
  x: "left",
  y: "bottom",
  ff: "font-family",
  fs: "font-size",
  fc: "color",
  sc: "text-shadow",
  ls: "letter-spacing",
  ws: "word-spacing"
};

function getScrollTop(el) {
  const $el = el instanceof jQuery ? el : $(el);
  const offsetFromPage = $el[0].offsetTop; //can also do offsetLeft
  const pageOffset = $el.closest(".pf.w0.h0")[0].offsetTop; //basicly a page container
  return pageOffset + offsetFromPage;
}

// todo: title, abstract, keywords
$(document).ready(function() {
  $("body").css("margin", 0);
  $("#page-container")
    .children(".pf.w0.h0")
    .each(function(i, item) {
      if (i > 5) $(this).remove();
    });

  $.post(
    "http://localhost:5656/KnowledgeSharing",
    { a: 111, b: 111 },
    res => {
      // console.log(res);
    },
    "json"
  );
  $.getJSON("save.json", data => {
    // console.log("json", data);
  });

  $("body").attr("id", "scrollArea");
  $("#page-container").attr("id", "contentArea");
  var clusterize = new Clusterize({
    scrollId: "scrollArea",
    contentId: "contentArea"
  });
  $("img")
    .attr("draggable", "false")
    .attr("ondragstate", "return false");
  $rect = $("<div>&nbsp;</div>")
    .attr("id", "selectionRect")
    .css({
      position: "absolute",
      outline: "1px solid black",
      "z-index": 100
    });
  $("body").append($rect);

  const classes = $("div")
    .toArray()
    .reduce((acc, item, ix, array) => {
      return acc.concat(...$(item)[0].classList);
    }, []);
  const counts = _.countBy(classes.filter(x => x.includes("h")));
  const mostCommonClass =
    "." +
    _.maxBy(_.keys(counts), function(o) {
      return counts[o];
    }) +
    ", .h7"; //todo: save list of classes
  const pageHeaderHeight = 620; //todo: filter by position / page combo
  const superscript = ".fs2";
  var headersAndParagraphs = $(mostCommonClass)
    .not(superscript)
    .filter((ix, item) => {
      const notPageHeader =
        +$(item)
          .css("bottom")
          .replace("px", "") < pageHeaderHeight;
      return notPageHeader;
    })
    .toArray();

  let elementInfo = headersAndParagraphs.map((item, index, array) => {
    return {
      numbers: getPosition(item),
      classes: $(item)[0].classList,
      index,
      text: getFixText($(item))
    };
  });

  let differences = elementInfo.reduce((state, item, i, array) => {
    const length = array.length;
    const keys = _.keys(array[0].numbers);
    if (i < length - 2) {
      const diff = keys.reduce((state_, key) => {
        return {
          ...state_,
          [key]: Math.round(array[i].numbers[key] - array[i + 1].numbers[key])
        };
      }, {});
      return state.concat({ ...diff, indexes: [i, i + 1] });
    } else {
      return state;
    }
  }, []);

  const roundCountSort = anArray => {
    const countArray = _
      .toPairs(_.countBy(anArray, Math.round))
      .map(x => [+x[0], x[1]]);
    const sortByCount = _.sortBy(countArray, x => x[1]).reverse();
    const sortBySize = _.sortBy(countArray, x => x[0]).reverse();
    return { sortByCount, sortBySize };
  };

  const countArrays = ["bottom", "left", "width"].reduce((state, key) => {
    const whatToCount = differences.map(x => x[key]);
    const { sortByCount, sortBySize } = roundCountSort(whatToCount); //from diffs
    return { ...state, [key]: { sortBySize, sortByCount } };
  }, {});

  const mostCommonVertDist = countArrays.bottom.sortByCount[0][0];

  const widthTolerance = 3;
  const { sortByCount, sortBySize } = roundCountSort(
    elementInfo.map(x => x.numbers.width)
  );
  const mostCommonParagraphLineWidth = sortByCount[0][0];

  const probablyIndentDist = countArrays.left.sortByCount[1][0]; // after zero

  const titleRegex = /^\d\./;
  const lastLineRegex = /[\.)]\s*$/;

  const isEndOfParagraph = ix => {
    //todo: more functions like this
    return (
      elementInfo[ix].numbers.width <
      mostCommonParagraphLineWidth - widthTolerance
    );
  };

  const isInVertDistRange = (ix, lowerFactor, upperFactor) => {
    return (
      Math.abs(differences[ix].bottom) >
        Math.abs(mostCommonVertDist) * lowerFactor &&
      Math.abs(differences[ix].bottom) <
        Math.abs(mostCommonVertDist) * upperFactor
    );
  };

  let tagState = "";
  differences.forEach((diff, ix, array) => {
    const prevIx = ix > 0 ? ix - 1 : ix;
    const text = elementInfo[ix].text;

    const nextVertDistLikeParagraph =
      diff.bottom === mostCommonVertDist || diff.bottom === 0;

    const prevVertDistLikeParagraph =
      ix > 0 ? differences[ix - 1].bottom === mostCommonVertDist : false;

    const paragraphLike =
      nextVertDistLikeParagraph || prevVertDistLikeParagraph;

    const newParagraphLike =
      diff.left === probablyIndentDist ||
      elementInfo[prevIx].tag === "h3" ||
      (isInVertDistRange(prevIx, 1, 1.8) && tagState !== "");

    const titleLike = titleRegex.test(text);
    const endsInPeriod = lastLineRegex.test(text);

    if (paragraphLike) {
      tagState = "p";
      $(headersAndParagraphs[ix]).css("background-color", "lightblue");
      elementInfo[ix].tag = "p-middle";
      if (newParagraphLike) {
        $(headersAndParagraphs[ix]).css("background-color", "lightgreen");
        elementInfo[ix].tag = "p-start";
        if (
          !isEndOfParagraph(prevIx) &&
          lastLineRegex.test(elementInfo[prevIx].text)
        ) {
          elementInfo[prevIx].tag = "p-end";
          $(headersAndParagraphs[prevIx]).css("background-color", "silver");
        }
      } else if (elementInfo[prevIx].tag === "p-end") {
        $(headersAndParagraphs[ix]).css("background-color", "lightgreen");
        elementInfo[ix].tag = "p-start";
      }
      if (isEndOfParagraph(ix) && endsInPeriod && !newParagraphLike) {
        $(headersAndParagraphs[ix]).css("background-color", "silver");
        elementInfo[ix].tag = "p-end";
      }
      if ($(headersAndParagraphs[ix]).is(":first-child")) {
        $(headersAndParagraphs[ix]).css("outline", "1px solid blue");
        elementInfo[ix].tag = "page-start";
      }

      if (isInVertDistRange(ix, 5, Infinity)) {
        $(headersAndParagraphs[ix]).css("outline", "3px solid orange");
        elementInfo[ix].tag = "page-end";
      }
    } else if (titleLike) {
      tagState = "h3";
      elementInfo[ix].tag = "h3";
      $(headersAndParagraphs[ix]).css("background-color", "pink");
    } else {
      tagState = "";
    }
  });

  let initNewState = {
    top: 0,
    bottom: 0,
    width: 0,
    height: 0,
    left: 0,
    width: 0,
    id: "#",
    classes: "",
    text: "",
    $page: "",
    $item: ""
  };
  let textChunkCounts = -1;

  const newDivs = elementInfo.reduce((state, item, ix, array) => {
    const { left, bottom, height, width, right } = item.numbers;

    if (["p-start", "page-start"].includes(item.tag)) {
      const top_ = bottom + height;
      textChunkCounts += 1;
      return state.concat({
        ...initNewState,
        bottom,
        left,
        width,
        top: top_,
        height: height,
        $page: $(headersAndParagraphs[ix]).closest(".pc.w0.h0"),
        $item: $(headersAndParagraphs[ix]),
        text: item.text
      });
    } else if (
      ["p-middle", "p-end", "page-end"].includes(item.tag) &&
      textChunkCounts > -1
    ) {
      const isBiggerWidth = width > state[textChunkCounts].width;
      const isLowerBottom = bottom < state[textChunkCounts].bottom;
      const furtherLeft = left < state[textChunkCounts].left;

      state[textChunkCounts] = {
        ...state[textChunkCounts],
        width: isBiggerWidth ? width : state[textChunkCounts].width,
        bottom: isLowerBottom ? bottom : state[textChunkCounts].bottom,
        left: furtherLeft ? left : state[textChunkCounts].left,
        height: state[textChunkCounts].top - bottom,
        text: state[textChunkCounts].text + " " + item.text //todo: if line ends in dash
      };
      return state;
    } else {
      return state;
    }
  }, []);

  // console.log(_.countBy(elementInfo.map(x => x.tag)));
  $("div.pf.w0.h0").each(function() {
    $(this).css({ width: 1200 });
    $(this)
      .children("div.pc.w0.h0")
      .css({ width: 1200 });
  });

  newDivs.forEach((item, ix) => {
    // $(headersAndParagraphs[ix]).remove()
    const $rect = newRect();
    const $drawnRect = $rect
      .css("left", item.left + 400)
      .css("width", item.width)
      .css("bottom", item.bottom)
      .css("height", item.height)
      .text(item.text)
      .css("font-size", "10px")
      .css("z-index", 200);
    item.$rect = $drawnRect;
    item.$page.prepend($drawnRect);
  });
});

const notSections = [""];
function getPosition(el) {
  const right = +$(el)
    .css("right")
    .replace("px", "");
  return {
    left: +$(el)
      .css("left")
      .replace("px", ""),
    bottom: +$(el)
      .css("bottom")
      .replace("px", ""),
    width: +$(el).width() / 4,
    height: +$(el).height() / 4,
    right: right
  };
}

function getFixText($item) {
  // deals with random spaces
  let strOut = "";
  $item.contents().each(function() {
    const isText = this.nodeType === 3; //Node.TEXT_NODE
    const isSpan = this.nodeType === 1;
    if (isText) {
      strOut += this.nodeValue.replace(" ", "");
    } else if (isSpan) {
      strOut += $(this).text();
    }
  });
  return strOut;
}

const {
  Observable,
  Subject,
  ReplaySubject,
  from,
  of,
  range,
  fromEvent,
  repeat
} = rxjs;
const {
  skipUntil,
  takeUntil,
  mergeMap,
  take,
  tap,
  finalize,
  filter
} = rxjs.operators;

const mouseMove$ = fromEvent(document, "mousemove");
const mouseDown$ = fromEvent(document, "mousedown");
const mouseUp$   = fromEvent(document, "mouseup");

var newRect = () =>
  $("<div>&nbsp;</div>").css({
    position: "absolute",
    outline: "1px solid black",
    "z-index": 100
  });
var getDragSelect = (downData, moveData = { clientX: 1, clientY: 1 }) => {
  const { offsetX, offsetY, clientX, clientY } = downData;
  const w = moveData.clientX - clientX; //dragging right positive
  const h = moveData.clientY - clientY; //dragging down positive
  const x = w < 0 ? clientX + w : clientX;
  const y = h < 0 ? clientY + h : clientY;
  const width = Math.abs(w);
  const height = Math.abs(h);
  return { x, y, width, height };
};

const moving$ = downData => {
  const $pageClicked = $(downData.srcElement).closest("div.pc.w0.h0");

  const isHTMLElement = $pageClicked[0] instanceof HTMLElement;
  const pageClientRect = isHTMLElement
    ? $pageClicked[0].getBoundingClientRect()
    : {};
  const down = getDragSelect(downData);
  dragSelect = { x: down.x, y: down.y, width: 1, height: 1 };
  $pageClicked.css("background-color", "lightgrey");
  const $rect = newRect();
  const $drawnRect = $rect
    .addClass("selectionRect")
    .css("top", dragSelect.y + pageClientRect.top)
    .css("left", dragSelect.x - pageClientRect.left)
    .css("width", dragSelect.width)
    .css("height", dragSelect.height)
    .css("will-change", "all");
  $pageClicked.prepend($drawnRect);

  return mouseMove$.pipe(
    takeUntil(mouseUp$),
    tap(moveData => {
      const prev = dragSelect;
      dragSelect = getDragSelect(downData, moveData);
      const diffs = ["x", "y", "width", "height"].reduce((state, key) => {
        if (["x", "y"].includes(key)) {
          return { ...state, [key]: dragSelect[key] - prev[key] };
        } else {
          return { ...state, [key]: dragSelect[key] / prev[key] };
        }
      }, {});

      $drawnRect.velocity(
        // velcoity suppose to be faster
        {
          top: dragSelect.y - pageClientRect.top,
          left: dragSelect.x + pageClientRect.left,
          width: dragSelect.width,
          height: dragSelect.height
        },
        0,
        "linear"
      );

      $("body").css("userSelect", "none");
    }),
    finalize(moveData => {
      let rectPos = getPosition($drawnRect);
      rectPos.height *= 4; // since we added this rect unscaled
      rectPos.width *= 4;
      // get elements in the rect
      const selectedElements = $pageClicked
        .children("div")
        .filter((ix, item) => {
          // heigher is heigher
          const pos = getPosition(item);
          const aboveBottom = pos.bottom > rectPos.bottom;
          const bellowTop =
            pos.height + pos.bottom < rectPos.height + rectPos.bottom;
          const withinLeft = pos.left > rectPos.left;
          const withinRight =
            pos.left + pos.width < rectPos.left + rectPos.width;
          // return aboveBottom && bellowTop && withinLeft && withinRight
          return aboveBottom && bellowTop && withinLeft && withinRight;
        })
        .toArray();

      if (selectedElements.length > 0) {
        const topElement = getPosition(selectedElements[0]);
        const bottomElement = getPosition(
          selectedElements[selectedElements.length - 1]
        );
        const topRight = topElement.left + topElement.width;
        const bottomRight = bottomElement.left + bottomElement.width;
        const left = Math.min(topElement.left, bottomElement.left);
        const width =
          topRight > bottomRight ? topElement.width : bottomElement.width;
        const height =
          topElement.height + topElement.bottom - bottomElement.bottom;
        const $rect = newRect();

        const text = selectedElements.reduce((state, item, ix) => {
          return state + " " + getFixText($(item));
        }, "");

        $rect
          .css({
            bottom: bottomElement.bottom,
            left: left + 400,
            width: width,
            height: height,
            "font-size": "8px",
            "z-index": 200
          })
          .text(text);
        $pageClicked.append($rect);
      }

      $("body").css("userSelect", "auto");
      $("body").css("cursor", "auto");
    })
  );
};

let dragSelect = { x: null, y: null, width: null, height: null };
const dragSelect$ = mouseDown$.pipe(
  filter(e => e.ctrlKey),
  mergeMap(downData => {
    dragSelect = { x: null, y: null, width: null, height: null };
    return moving$(downData);
  })
);

dragSelect$.subscribe();

// function positionDiffs(item1, item2) {
//   var left = Math.round(item1.pos.left - item2.pos.left);
//   var bottom = Math.round(item1.pos.bottom - item2.pos.bottom);
//   return { left: left, bottom: bottom };
// }

// function updateSlidingWindow(
//   index,
//   item,
//   middle,
//   windowSize,
//   slidingWindow,
//   diffs
// ) {
//   // const middle = 1;
//   const makeFirstDiff = index === 1;
//   const makeSecondDiff = index === 2;
//   const canDiffsSafely = index >= windowSize - 1;
//   const windowFull = index > windowSize - 1;

//   if (windowFull) {
//     slidingWindow.shift();
//     slidingWindow.push({ pos: getPosition(item), $item: $(item) });
//   } else {
//     slidingWindow.push({ pos: getPosition(item), $item: $(item) });
//   }

//   if (makeFirstDiff) {
//     diffs.push(positionDiffs(slidingWindow[0], slidingWindow[middle]));
//   } else if (makeSecondDiff) {
//     diffs.push(positionDiffs(slidingWindow[middle], slidingWindow[middle + 1]));
//   } else if (canDiffsSafely) {
//     diffs.shift();
//     diffs.push(positionDiffs(slidingWindow[middle], slidingWindow[middle + 1]));
//   }

//   return [slidingWindow, diffs, canDiffsSafely];
// }

// function getFixText($item) {
//   // deals with random spaces and dashes at line end
//   let strOut = "";
//   let endsInDash = false;
//   $item.contents().each(function() {
//     const isText = this.nodeType === 3; //Node.TEXT_NODE
//     const isSpan = this.nodeType === 1;
//     if (isText) {
//       strOut += this.nodeValue.replace(" ", "");
//     } else if (isSpan) {
//       strOut += $(this).text();
//     }
//   });
//   return strOut;
// }

// //todo: numbered lists, bullet points
// function features(diffs, text, $item, slidingWindow) {
//   var isIndented = diffs[1].left > 7 && diffs[1].left < 15;
//   var isNormalLine = diffs[1].bottom <= 12;
//   var prevLineFartherUp = diffs[0].bottom >= 16; // previous 16. click title + next p
//   var prevIsTitle = slidingWindow[0].$item.hasClass("h8") //todo: param.
//   var hasHeadClasses = $item.hasClass("h7") //todo: param. || $item.hasClass("h10");
//   var isNewParagraph = (prevLineFartherUp || isIndented) || (!hasHeadClasses && prevIsTitle); //todo or prev is title
//   var isTitleDist =
//     (diffs[0].bottom > 22 && diffs[0].bottom < 25) //todo: param
//   var re = /^\d\./; // todo: param. previous: ^[A-Z]
//   var sectionTitleLike = re.test(text);
//   var notInNotSections = !notSections.includes(text);
//   var isPageEnd =
//     diffs[1].left > 20 && diffs[1].left < 1000 && diffs[1].bottom < 0;

//   if (isPageEnd) {
//     $item.css("background-color", "lightblue");
//   }
//   var isSuperScript = $item.hasClass("h11");
//   var isColEnd =
//     diffs[1].left < -20 && diffs[1].left > -1000 && diffs[1].bottom < 0;

//   if (isColEnd) {
//     $item.css("background-color", "lightgreen");
//   }
//   return [
//     isIndented,
//     isNormalLine,
//     prevLineFartherUp,
//     isNewParagraph,
//     isTitleDist,
//     sectionTitleLike,
//     hasHeadClasses,
//     notInNotSections
//   ];
// }

// $(document).ready(function() {

//   $("#page-container").scrollTop(1000);
//   const classes = $('div').toArray().reduce((acc, item, ix, array)=> {
//     return acc.concat(...$(item)[0].classList)
//   },[])
//   const counts = _.countBy(classes.filter(x=>x.includes('h')))
//   console.log(counts)
//   const mostCommonClass = '.' + _.maxBy(_.keys(counts), function (o) { return counts[o]; }) + ', .h7' //todo: list of classes
//    var headersAndParagraphs = $(mostCommonClass).toArray();

//   var state = ""; // title or p
//   var titleCount = 0;
//   var pCount = 0; // paragraph
//   var count = 0;
//   var aTag = ""; // build tags here
//   var xmlOut = ""; // entire output
//   var windowSize = 3; //last, middle, front
//   var slidingWindow = [];
//   var diffs = [];
//   var lines = [];
//   var canDiffsSafely = false;
//   console.log("Removing super scripts.");
//   $(".h11").remove();

//   let elementInfo = headersAndParagraphs.map((item, index, array) => {
//     return {numbers: getPosition(item), classes: $(item)[0].classList, index}
//   });
//   let differences = elementInfo.reduce((state, item, i, array) => {
//     const length = array.length;
//     const keys = _.keys(array[0].numbers)

//     if (i < length - 2) {
//       const diff = keys.reduce((state_, key) => {
//         return {...state_, [key]: array[i].numbers[key] - array[i+1].numbers[key]}
//       }, {})
//       return state.concat({...diff, indexes: [i, i+1]})
//     } else {
//       return state
//     }
//   }, [])

//   console.log(differences)

//   headersAndParagraphs.forEach((item, index, array) => {
//     const middle = 1;
//     [slidingWindow, diffs, canDiffsSafely] = updateSlidingWindow(
//       index,
//       item,
//       middle,
//       windowSize,
//       slidingWindow,
//       diffs
//     );

//     if (canDiffsSafely) {
//       let $item = slidingWindow[middle].$item;
//       // FIRST LINE HACK
//       if (index === windowSize - 1) {
//         slidingWindow[0].$item.addClass(
//           "section_title " + "titleCount" + titleCount
//         );
//         titleCount += 1;
//         count += 1;
//         slidingWindow[0].$item.css("background-color", "pink");
//         state = "h3";
//         lines.push({
//           state: state,
//           class: "order" + count,
//           text: slidingWindow[0].$item.text()
//         });
//       }

//       $item.children("._._1").remove(); // also adds in random spaces, maybe can remove now?
//       let text = getFixText($item);

//       var [
//         isIndented,
//         isNormalLine,
//         prevLineFartherUp,
//         isNewParagraph,
//         isTitleDist,
//         sectionTitleLike,
//         hasHeadClasses,
//         notInNotSections
//       ] = features(diffs, text, $item, slidingWindow);

//       if (isNewParagraph && isNormalLine) {
//         state = "p";
//         pCount += 1;
//         count += 1;
//       }

//       if (sectionTitleLike && hasHeadClasses && prevLineFartherUp) {
//         state = "h3";
//         titleCount += 1;
//         count += 1;
//         $item.css("background-color", "pink");
//       }

//       if (state === "p") {
//         const colors = ["lightgreen", "LightCyan", "lightyellow", "lightgrey"];
//         $item.css("background-color", colors[pCount % colors.length]);
//       }

//       if (state === "h3") {
//         $item.addClass("section_title " + "titleCount" + titleCount);
//         $item.css("background-color", "pink");
//       } else {
//         $item.addClass("ptext " + "pCount" + pCount);
//       }
//       $item.addClass("order" + count);
//       lines.push({ state: state, class: "order" + count, text: text });
//     }
//     window.lines = lines;
//   });

//   const fixTrailingDash = text => {
//     if (text[text.length - 1] === "-") {
//       return text.slice(0, text.length - 1);
//     } else {
//       return text + "\n";
//     }
//   };
//   const combinedLines = lines => {
//     var combined = [];
//     var elementType = "";
//     var s = { elementNumber: 0, tag: "" };
//     var xml = "";
//     lines.forEach((line, i) => {
//       const isNewElement = elementType !== line.class;
//       elementType = line.class;

//       if (isNewElement) {
//         if (i !== 0) s.elementNumber += 1;
//         combined[s.elementNumber] = {
//           text: fixTrailingDash(line.text),
//           tag: line.state
//         };
//       } else {
//         combined[s.elementNumber].text += fixTrailingDash(line.text);
//       }
//     });
//     return combined;
//   };
//   var combined = combinedLines(lines);

//   var xml = combined.reduce((state, textChunk, i) => {
//     const tag = `<${textChunk.tag}>\n${textChunk.text}</${textChunk.tag}>\n\n`;
//     return state + tag;
//   }, "");

//   window.combined = combined;
//   window.xml = xml;
//   // $(".h2,.h7").css("background-color", "orange");
//   // $(mostCommonClass) // replace spans with spaces
//   //   .toArray()
//   //   .forEach((item, index, array) => {
//   //     const t = getFixText($(item));
//   //     // const width = $(item).width()
//   //     // const spaceSize = (t.split(' ').length / 10) * .3
//   //     $(item)
//   //       .html(t)
//   //       .removeClass("ws0")
//   //       .css("word-spacing", ".2rem");
//   //     // .css('width', width)
//   //     // .css('display','flex')
//   //     // .css('justify-content','space-between')
//   //     // .css('flex-direction','row')
//   //   });

//   $("body").append($rect)[(slidingWindow, diffs, canDiffsSafely)] = [0, 0, 0];
//   const tableStart = /^[tT]able.*[\d]/;
//   const figStart = /^[Ff]ig.*[\d]/;
//   const figOrTableStart = /(^[Ff]ig.{0,10}[\d]|^[tT]able.{0,10}[\d])/

//   $('.fs3')
//     .toArray()
//     .forEach((item, index, array) => {
//       const middle = 1;
//       [slidingWindow, diffs, canDiffsSafely] = updateSlidingWindow(
//         index,
//         item,
//         middle,
//         windowSize,
//         slidingWindow,
//         diffs
//       );

//       const text = getFixText($(item));
//       // const isTableStart = tableStart.test(text)
//       const isFigStart = figOrTableStart.test(text);

//       if (isFigStart) {
//         const id = figOrTableStart.exec(text)[0].replace(' ', '').replace('.','')
//         var nAhead = 0;
//         var win = [];
//         var doMore = true;
//         win.push(getPosition($(item)));

//         $(array[index + nAhead]).css("background-color", "thistle").attr('id', id)
//         while (index + nAhead < array.length - 2 && doMore) {
//           //look ahead
//           nAhead += 1;
//           if (array[index + nAhead] === undefined) console.log(index,nAhead, array.length)
//           win.push(getPosition($(array[index + nAhead])));

//           if (win.length > 2) win.shift();
//           const vertDiff = Math.round(win[0].bottom - win[1].bottom);
//           const horDiff = Math.round(win[0].left - win[1].left);
//           if (Math.abs(vertDiff) > 25 || Math.abs(horDiff) > 160 || nAhead > 100) {
//             doMore = false;
//           } else {
//             $(array[index + nAhead]).css("background-color", "thistle");
//           }
//         }
//       }
//     });

//     // console.log($('#Fig1').show().offset())
// }); // on window ready

// // $(window).mouseup(()=> {
// //   console.log(getSelectionTextAndContainerElement())
// // })

// // from http://jsfiddle.net/timdown/Q9VZT/
// function getSelectionTextAndContainerElement() {
//   var text = "",
//     containerElement = null;
//   if (typeof window.getSelection != "undefined") {
//     var sel = window.getSelection();
//     if (sel.rangeCount) {
//       var node = sel.getRangeAt(0).commonAncestorContainer;
//       containerElement = node.nodeType == 1 ? node : node.parentNode;
//       text = sel.toString();
//     }
//   } else if (
//     typeof document.selection != "undefined" &&
//     document.selection.type != "Control"
//   ) {
//     var textRange = document.selection.createRange();
//     containerElement = textRange.parentElement();
//     text = textRange.text;
//   }
//   return {
//     text: text,
//     containerElement: $(containerElement)
//   };
// }

// $(window).mouseup(function() {
//   console.log(getSelectionTextAndContainerElement());
// });

// $(window).mousedown(function() {
//   console.log(getSelectionTextAndContainerElement());
// });
