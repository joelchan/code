const getPos = (el) => {
    return {
      left: +$(el)
        .css('left')
        .replace("px", ""),
      bottom: +$(el)
        .css('bottom')
        .replace("px", ""),
      width: +$(el).width()
    }
  };
  let xmlOut = ''
  let aTag = ''


  $(document).ready(function () {
    console.log('asdf')
    $('#page-container').scrollTop(1000);

    var paragraphLines = $(".fs6").toArray()
    var pageWidth = $(document).width()


    //if header, start appending until indent, put in h1
    // todo: delete trailing -

    var acc = []
    var state = ''  // header or p
    headerCount = 1
    pCount = 1
    count = 1
    
    var tags = {header: ['<h1>', '</h1>'],
            p: ['<p>','</p>']}

    var slidingWindow = [];
    var windowSize = 3; //last, middle, front
    var diffs = [];

    console.log('Removing super scripts.')
    $('.h11').remove()

   function posDiffs (item1, item2)  {
      var left = Math.round(item1.pos.left - item2.pos.left);
      var bottom = Math.round(item1.pos.bottom - item2.pos.bottom);
      // return {left: left, bottom: bottom}
      return {left: left, bottom: bottom}
    }

    paragraphLines.forEach((item, index, array) => {
      const middle = 1;
      const makeFirstDiff  = index === 1
      const makeSecondDiff = index === 2
      const canDiffsSafely = index >= windowSize
      const windowFull = index > windowSize - 1
      if (windowFull) {
        slidingWindow.shift()
        slidingWindow.push({pos: getPos(item), $item: $(item)})
      } else {
        slidingWindow.push({pos: getPos(item), $item: $(item)})
      }

      if (makeFirstDiff) {
        diffs.push(posDiffs(slidingWindow[0],slidingWindow[middle]))
      } else if (makeSecondDiff) {
        diffs.push(posDiffs(slidingWindow[middle],slidingWindow[middle+1]))
      } else if (canDiffsSafely) {
        diffs.shift()
        diffs.push(posDiffs(slidingWindow[middle],slidingWindow[middle+1]))
        
      }

      var re = /^\d\./
      
      if (canDiffsSafely) {
        let $item = slidingWindow[middle].$item
        let text = slidingWindow[middle].$item.text()
        var isIndented = diffs[1].left > 7 && diffs[1].left < 15;
        var isNormalLine = diffs[1].bottom <= 12;
        if (isIndented && isNormalLine) {
          xmlOut += aTag
          if (state === 'p') aTag = '\n </p> \n <p> \n'
          if (state === 'header') aTag = '\n </h1> \n <p> \n'
          aTag += ' \n ' + aTag + ' \n ' + text + ' \n '
          state = 'p';
          pCount += 1;
          count += 1;
          $item.css("background-color", "grey");
        } 
        if (!isIndented && isNormalLine){
          aTag += text + '\n'
        }


        var isPageEnd = diffs[1].left > 20 && diffs[1].left < 1000 && diffs[1].bottom < 0
        
        if (isPageEnd) {
          $item.css("background-color", "lightblue");
        }

        var isSuperScript = $(slidingWindow[middle]).hasClass('.h11')

        var isColEnd = diffs[1].left < -20 && diffs[1].left > -1000 && diffs[1].bottom < 0
        if (isColEnd) {
          $item.css("background-color", "lightgreen");
        }
         var isHeaderDist = (diffs[0].bottom > 22 && diffs[0].bottom < 25) 
       || (diffs[0].bottom > 22 && diffs[0].bottom < 25)
      
      var sectionHeaderLike = re.test(text)
      var hasHeadClasses = $item.hasClass('.ff3, .ff4')
      var notInNotSections = !notSections.includes(text)

      if (sectionHeaderLike) console.log(text, isHeaderDist )
      /*
      h h h i p p p
          ^
      h1 + + 
      */

      if (sectionHeaderLike) {
          xmlOut += aTag
          if (state === 'p') aTag = '\n </p> \n <h1> \n'
          if (state === 'header') aTag = '\n </h1> \n <h1> \n'
          aTag += ' \n ' + aTag + ' \n ' + text + ' \n '
          state = 'header';
          headerCount += 1;
          count += 1;
          $item.css("background-color", "pink");
      }

      if (state === 'header'){
        $item.addClass('section_header ' + 'headerCount' + headerCount)
      } else {
        $item.addClass('ptext '+ 'pCount' + pCount)
      }
        $item.addClass('order' + count)

      }
    });
  });
