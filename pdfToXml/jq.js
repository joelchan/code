
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
      $('#page-container').scrollTop(300);

      var paragraphLines = $(".fs6").toArray()
      var pageWidth = $(document).width()


      //if title, start appending until indent, put in h1
      // todo: delete trailing -

      var acc = []
      var state = ''  // title or p
      titleCount = 1
      pCount = 1
      count = 1
      firstTitleIx = 0;
      firstPIndex = 1;

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
        const canDiffsSafely = index >= windowSize -1
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
          if (index === windowSize - 1) { // FIRST LINE HACK
            slidingWindow[0].$item.addClass('section_title ' + 'titleCount' + titleCount)
            titleCount += 1
            count +=1
            slidingWindow[0].$item.css('background-color', 'pink')  
            state = 'title'
            xmlOut = '<title> ' + slidingWindow[0].$item.text()
        }

          let $item = slidingWindow[middle].$item
            const getFixText = ($item) => {
              // deals with random spaces and dashes at line end
              let strOut = ''
              let endsInDash = false
              $item
              .contents()
              .each(function() {
                const isText = this.nodeType === 3; //Node.TEXT_NODE
                if (isText) {
                  strOut += this.nodeValue.replace(' ', '')
                } else {
                  strOut += ' '
                }
              })
              return strOut

            }
          
          $item.children('._._1').remove() // also adds in random spaces
          let text = getFixText($item)
          
          var isIndented = diffs[1].left > 7 && diffs[1].left < 15;
          var isNormalLine = diffs[1].bottom <= 12;
          var prevLineFartherUp = diffs[0].bottom >= 18
          var isNewParagraph = (prevLineFartherUp || isIndented)



          if (isNewParagraph && isNormalLine) {
            xmlOut += aTag
            if (state === 'p') aTag = '</p> \n\n <p>'
            if (state === 'title') aTag = '\n </title> \n\n <p> \n'
              //todo deal with dashes
              if (aTag[aTag.length-1] === '-') {
                aTag = strOut.slice(0,strOut.length-1)
                aTag += text
              } else {
                aTag += ' \n ' + text + '\n'
              }

            state = 'p';
            pCount += 1;
            count += 1;
            $item.css("background-color", "grey");
          } 
          if (!isNewParagraph && isNormalLine){
            if (aTag[aTag.length-1] === '-') {
                aTag = strOut.slice(0,strOut.length-1)
                aTag += text
              } else {
                aTag += ' \n ' + text + '\n'
              }
          }


          var isPageEnd = diffs[1].left > 20 && diffs[1].left < 1000 && diffs[1].bottom < 0
          
          if (isPageEnd) {
            $item.css("background-color", "lightblue");
          }

          var isSuperScript = $(slidingWindow[middle]).hasClass('h11')

          var isColEnd = diffs[1].left < -20 && diffs[1].left > -1000 && diffs[1].bottom < 0
          if (isColEnd) {
            $item.css("background-color", "lightgreen");
          }
           var isTitleDist = (diffs[0].bottom > 22 && diffs[0].bottom < 25) 
         || (diffs[0].bottom > 22 && diffs[0].bottom < 25)
        
        var sectionTitleLike = re.test(text)
        var hasHeadClasses = $item.hasClass('ha') || $item.hasClass('h10')
        var notInNotSections = !notSections.includes(text)

        if (sectionTitleLike && hasHeadClasses) {
            xmlOut += aTag
            if (state === 'p') aTag = '\n </p> \n <title> \n'
            if (state === 'title') aTag = '\n </title> \n <title> \n'
            aTag += ' \n ' + text + ' \n '
            state = 'title';
            titleCount += 1;
            count += 1;
            $item.css("background-color", "pink");
        }

        if (state === 'p') {
          const colors = ["lightgreen", "LightCyan","lightyellow", 'lightgrey']
          $item.css("background-color", colors[pCount%colors.length])
        }



        if (state === 'title'){
          $item.addClass('section_title ' + 'titleCount' + titleCount)
          $item.css("background-color", "pink");
          if (index===array.length-1) xmlOut += '\n ' + text + '\n</title>'
        } else {
          $item.addClass('ptext '+ 'pCount' + pCount)
          if (index===array.length-1) xmlOut += '\n  ' + text + '\n</p>'
        }
          $item.addClass('order' + count)
        }



      });
    });
xmlOut
    