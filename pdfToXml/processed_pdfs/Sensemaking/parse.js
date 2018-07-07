// todo: replace ligatures e.g. fi ﬁ
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

function features(diffs, text, $item) {
  var isIndented = diffs[1].left > 7 && diffs[1].left < 15;
  var isNormalLine = diffs[1].bottom <= 12;
  var prevLineFartherUp = diffs[0].bottom >= 18;
  var isNewParagraph = prevLineFartherUp || isIndented;
  var isTitleDist =
    (diffs[0].bottom > 22 && diffs[0].bottom < 25) ||
    (diffs[0].bottom > 22 && diffs[0].bottom < 25);
  var re = /^\d\./;
  var sectionTitleLike = re.test(text);
  var hasHeadClasses = $item.hasClass("ha") || $item.hasClass("h10");
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
  $("#page-container").scrollTop(300);

  var paragraphLines = $(".fs6").toArray();

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
        state = "title";
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
      ] = features(diffs, text, $item);

      if (isNewParagraph && isNormalLine) {
        state = "p";
        pCount += 1;
        count += 1;
      }

      if (sectionTitleLike && hasHeadClasses) {
        state = "title";
        titleCount += 1;
        count += 1;
        $item.css("background-color", "pink");
      }

      if (state === "p") {
        const colors = ["lightgreen", "LightCyan", "lightyellow", "lightgrey"];
        $item.css("background-color", colors[pCount % colors.length]);
      }

      if (state === "title") {
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
    return combined
  };
  var combined = combinedLines(lines)

  var xml = combined.reduce((state, textChunk, i) => {
      const tag = `<${textChunk.tag}>\n${textChunk.text}</${textChunk.tag}>\n\n`
      return state + tag
  }, '')

  window.combined = combined;
  window.xml = xml;
  //   $(".h2,.h7").css("background-color", "orange");
});

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
$(window).mouseup(function() {
  console.log(getSelectionTextAndContainerElement());
});
