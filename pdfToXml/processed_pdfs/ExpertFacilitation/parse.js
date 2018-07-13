const dps2htmlexCss = {'_': 'display:.*?',
    'm': 'transform',
    'w': 'width',
    'h': 'height',
    'x': 'left',
    'y': 'bottom',
    'ff': 'font-family',
    'fs': 'font-size',
    'fc': 'color',
    'sc': 'text-shadow',
    'ls': 'letter-spacing',
    'ws': 'word-spacing'}

$(document).ready(function() {
  


 })

const notSections = ['']
function getPosition(el) {
  return {
    left: +$(el)
      .css("left")
      .replace("px", ""),
    bottom: +$(el)
      .css("bottom")
      .replace("px", ""),
    width: +$(el).width()
  };
}

function positionDiffs(item1, item2) {
  var left = Math.round(item1.pos.left - item2.pos.left);
  var bottom = Math.round(item1.pos.bottom - item2.pos.bottom);
  return { left: left, bottom: bottom };
}

function updateSlidingWindow(
  index,
  item,
  middle,
  windowSize,
  slidingWindow,
  diffs
) {
  // const middle = 1;
  const makeFirstDiff = index === 1;
  const makeSecondDiff = index === 2;
  const canDiffsSafely = index >= windowSize - 1;
  const windowFull = index > windowSize - 1;

  if (windowFull) {
    slidingWindow.shift();
    slidingWindow.push({ pos: getPosition(item), $item: $(item) });
  } else {
    slidingWindow.push({ pos: getPosition(item), $item: $(item) });
  }

  if (makeFirstDiff) {
    diffs.push(positionDiffs(slidingWindow[0], slidingWindow[middle]));
  } else if (makeSecondDiff) {
    diffs.push(positionDiffs(slidingWindow[middle], slidingWindow[middle + 1]));
  } else if (canDiffsSafely) {
    diffs.shift();
    diffs.push(positionDiffs(slidingWindow[middle], slidingWindow[middle + 1]));
  }

  return [slidingWindow, diffs, canDiffsSafely];
}

function getFixText($item) {
  // deals with random spaces and dashes at line end
  let strOut = "";
  let endsInDash = false;
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

//todo: numbered lists, bullet points
function features(diffs, text, $item, slidingWindow) {
  var isIndented = diffs[1].left > 7 && diffs[1].left < 15;
  var isNormalLine = diffs[1].bottom <= 12;
  var prevLineFartherUp = diffs[0].bottom >= 16;
  var prevIsTitle = slidingWindow[0].$item.hasClass("h8") //todo: param.  var currentIsP = $item
  var hasHeadClasses = $item.hasClass("h8") //todo: param. || $item.hasClass("h10");
  var isNewParagraph = (prevLineFartherUp || isIndented) || (!hasHeadClasses && prevIsTitle); //todo or prev is title
  var isTitleDist =
    (diffs[0].bottom > 22 && diffs[0].bottom < 25) //todo: param
  var re = /^[A-Z]/; // todo: param.
  var sectionTitleLike = re.test(text);
  var notInNotSections = !notSections.includes(text);
  var isPageEnd =
    diffs[1].left > 20 && diffs[1].left < 1000 && diffs[1].bottom < 0;

  if (isPageEnd) {
    $item.css("background-color", "lightblue");
  }
  var isSuperScript = $item.hasClass("h11");
  var isColEnd =
    diffs[1].left < -20 && diffs[1].left > -1000 && diffs[1].bottom < 0;

  if (isColEnd) {
    $item.css("background-color", "lightgreen");
  }
  return [
    isIndented,
    isNormalLine,
    prevLineFartherUp,
    isNewParagraph,
    isTitleDist,
    sectionTitleLike,
    hasHeadClasses,
    notInNotSections
  ];
}

$(document).ready(function() {
  

  $("#page-container").scrollTop(1000);
  const classes = $('div').toArray().reduce((acc, item, ix, array)=> {
    return acc.concat(...$(item)[0].classList)
  },[])
  const counts = _.countBy(classes.filter(x=>x.includes('fs')))
  const mostCommonClass = '.' + _.maxBy(_.keys(counts), function (o) { return counts[o]; }) + ', .fs3'
   var paragraphLines = $(mostCommonClass).toArray();

  var state = ""; // title or p
  var titleCount = 0;
  var pCount = 0; // paragraph
  var count = 0;
  var aTag = ""; // build tags here
  var xmlOut = ""; // entire output
  var windowSize = 3; //last, middle, front
  var slidingWindow = [];
  var diffs = [];
  var lines = [];
  var canDiffsSafely = false;
  console.log("Removing super scripts.");
  $(".h11").remove();

  // LOOP OVER LINES IN MAIN BODY
  paragraphLines.forEach((item, index, array) => {
    const middle = 1;
    [slidingWindow, diffs, canDiffsSafely] = updateSlidingWindow(
      index,
      item,
      middle,
      windowSize,
      slidingWindow,
      diffs
    );

    if (canDiffsSafely) {
      let $item = slidingWindow[middle].$item;
      // FIRST LINE HACK
      if (index === windowSize - 1) {
        slidingWindow[0].$item.addClass(
          "section_title " + "titleCount" + titleCount
        );
        titleCount += 1;
        count += 1;
        slidingWindow[0].$item.css("background-color", "pink");
        state = "h3";
        lines.push({
          state: state,
          class: "order" + count,
          text: slidingWindow[0].$item.text()
        });
      }

      $item.children("._._1").remove(); // also adds in random spaces, maybe can remove now?
      let text = getFixText($item);

      var [
        isIndented,
        isNormalLine,
        prevLineFartherUp,
        isNewParagraph,
        isTitleDist,
        sectionTitleLike,
        hasHeadClasses,
        notInNotSections
      ] = features(diffs, text, $item, slidingWindow);

      if (isNewParagraph && isNormalLine) {
        state = "p";
        pCount += 1;
        count += 1;
      }

      if (sectionTitleLike && hasHeadClasses && prevLineFartherUp) {
        state = "h3";
        titleCount += 1;
        count += 1;
        $item.css("background-color", "pink");
      }

      if (state === "p") {
        const colors = ["lightgreen", "LightCyan", "lightyellow", "lightgrey"];
        $item.css("background-color", colors[pCount % colors.length]);
      }

      if (state === "h3") {
        $item.addClass("section_title " + "titleCount" + titleCount);
        $item.css("background-color", "pink");
      } else {
        $item.addClass("ptext " + "pCount" + pCount);
      }
      $item.addClass("order" + count);
      lines.push({ state: state, class: "order" + count, text: text });
    }
    window.lines = lines;
  });

  const fixTrailingDash = text => {
    if (text[text.length - 1] === "-") {
      return text.slice(0, text.length - 1);
    } else {
      return text + "\n";
    }
  };
  const combinedLines = lines => {
    var combined = [];
    var elementType = "";
    var s = { elementNumber: 0, tag: "" };
    var xml = "";
    lines.forEach((line, i) => {
      const isNewElement = elementType !== line.class;
      elementType = line.class;

      if (isNewElement) {
        if (i !== 0) s.elementNumber += 1;
        combined[s.elementNumber] = {
          text: fixTrailingDash(line.text),
          tag: line.state
        };
      } else {
        combined[s.elementNumber].text += fixTrailingDash(line.text);
      }
    });
    return combined;
  };
  var combined = combinedLines(lines);

  var xml = combined.reduce((state, textChunk, i) => {
    const tag = `<${textChunk.tag}>\n${textChunk.text}</${textChunk.tag}>\n\n`;
    return state + tag;
  }, "");

  window.combined = combined;
  window.xml = xml;
  // $(".h2,.h7").css("background-color", "orange");
  // $(mostCommonClass) // replace spans with spaces
  //   .toArray()
  //   .forEach((item, index, array) => {
  //     const t = getFixText($(item));
  //     // const width = $(item).width()
  //     // const spaceSize = (t.split(' ').length / 10) * .3
  //     $(item)
  //       .html(t)
  //       .removeClass("ws0")
  //       .css("word-spacing", ".2rem");
  //     // .css('width', width)
  //     // .css('display','flex')
  //     // .css('justify-content','space-between')
  //     // .css('flex-direction','row')
  //   });

  $("img")
    .attr("draggable", "false")
    .attr("ondragstate", "return false");
  $rect = $("<div>&nbsp;</div>")
    .attr("id", "selectionRect")
    .css({
      position: "absolute",
      outline: "1px solid black"
    });
  $("body").append($rect)[(slidingWindow, diffs, canDiffsSafely)] = [0, 0, 0];
  const tableStart = /^[tT]able.*[\d]/;
  const figStart = /^[Ff]ig.*[\d]/;
  const figOrTableStart = /(^[Ff]ig.{0,10}[\d]|^[tT]able.{0,10}[\d])/

  $('.fs3')
    .toArray()
    .forEach((item, index, array) => {
      const middle = 1;
      [slidingWindow, diffs, canDiffsSafely] = updateSlidingWindow(
        index,
        item,
        middle,
        windowSize,
        slidingWindow,
        diffs
      );

      const text = getFixText($(item));
      // const isTableStart = tableStart.test(text)
      const isFigStart = figOrTableStart.test(text);
      
      if (isFigStart) {
        const id = figOrTableStart.exec(text)[0].replace(' ', '').replace('.','')
        var nAhead = 0;
        var win = [];
        var doMore = true;
        win.push(getPosition($(item)));
        
        $(array[index + nAhead]).css("background-color", "thistle").attr('id', id)
        while (index + nAhead < array.length - 2 && doMore) {
          //look ahead
          nAhead += 1;
          if (array[index + nAhead] === undefined) console.log(index,nAhead, array.length)
          win.push(getPosition($(array[index + nAhead])));

          if (win.length > 2) win.shift();
          const vertDiff = Math.round(win[0].bottom - win[1].bottom);
          const horDiff = Math.round(win[0].left - win[1].left);
          if (Math.abs(vertDiff) > 25 || Math.abs(horDiff) > 160 || nAhead > 100) {
            doMore = false;
          } else {
            $(array[index + nAhead]).css("background-color", "thistle");
          }
        }
      }
    });


    // console.log($('#Fig1').show().offset())
}); // on window ready

// $(window).mouseup(()=> {
//   console.log(getSelectionTextAndContainerElement())
// })

// from http://jsfiddle.net/timdown/Q9VZT/
function getSelectionTextAndContainerElement() {
  var text = "",
    containerElement = null;
  if (typeof window.getSelection != "undefined") {
    var sel = window.getSelection();
    if (sel.rangeCount) {
      var node = sel.getRangeAt(0).commonAncestorContainer;
      containerElement = node.nodeType == 1 ? node : node.parentNode;
      text = sel.toString();
    }
  } else if (
    typeof document.selection != "undefined" &&
    document.selection.type != "Control"
  ) {
    var textRange = document.selection.createRange();
    containerElement = textRange.parentElement();
    text = textRange.text;
  }
  return {
    text: text,
    containerElement: $(containerElement)
  };
}

function getScrollTop(el) {
  const $el = el instanceof jQuery ? el : $(el)
  const offsetFromPage = $el[0].offsetTop; //can also do offsetLeft
  const pageOffset = $el.closest('.pf.w0.h0')[0].offsetTop; //basicly a page container
  return pageOffset + offsetFromPage
}

// drawing rectanges to capture parts of the paper
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
const { skipUntil, takeUntil, mergeMap, take, tap, finalize } = rxjs.operators;
const mouseMove$ = fromEvent(document, "mousemove");
const mouseDown$ = fromEvent(document, "mousedown");
const mouseUp$ = fromEvent(document, "mouseup");

const moving$ = downData => {
  return mouseMove$.pipe(
    takeUntil(mouseUp$),
    tap(moveData => {
      const { offsetX, offsetY, clientX, clientY } = downData;
      const w = moveData.clientX - clientX; //dragging right positive
      const h = moveData.clientY - clientY; //dragging down positive
      const x = w < 0 ? clientX + w : clientX;
      const y = h < 0 ? clientY + h : clientY;
      const width = Math.abs(w);
      const height = Math.abs(h);
      dragSelect = { x, y, width, height };
      $("#selectionRect")
        .css("top", y)
        .css("left", x)
        .css("width", width)
        .css("height", height);
      $("body").css("userSelect", "none");
    }),
    finalize(moveData => {
      if (dragSelect.width > 10 && dragSelect.height > 10) {
        $("#selectionRect")
        .css("top", 0)
        .css("left", 0)
        .css("width", 0)
        .css("height", 0);
      }
      console.log(dragSelect)


      $("body").css("userSelect", "auto");
      $("body").css("cursor", "auto");
    })
  );
};

let dragSelect = { x: null, y: null, width: null, height: null };
const dragSelect$ = mouseDown$.pipe(
  mergeMap(downData => {
    dragSelect = { x: null, y: null, width: null, height: null };
    return moving$(downData);
  })
);

// dragSelect$.subscribe(x => console.log(x));

// $(window).mouseup(function() {
//   console.log(getSelectionTextAndContainerElement());
// });

// $(window).mousedown(function() {
//   console.log(getSelectionTextAndContainerElement());
// });

