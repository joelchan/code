$(".fs6")
  .toArray()
  .reduce((accumulator, item, index, array) => {
    if (array.length - 1 == index) return 1

    const getPos = (x, pos) => {return +$(x).css(pos).replace("px", "")}

    var left = getPos(item, 'left')
    var bottom = getPos(item, 'bottom')
    var nextLeft = getPos(array[index+1], 'left')
    var nextBottom = getPos(array[index+1], 'bottom')

    var leftDiff = Math.round(left - nextLeft);
    var bottomDiff = Math.round(bottom - nextBottom);
    var isIndented = leftDiff > 7 && leftDiff < 15;
    var isNormalLine = bottomDiff <= 12
    console.log(bottomDiff)
    if (isIndented && isNormalLine) {
      $(item).css("background-color", "green");
    }

    return left;
  }, 0);
