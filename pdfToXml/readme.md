# on ubuntu in windows
pdf2htmlEX picf.pdf --optimize-text 1 # html that looks like original

# identify parts of the pdf on windows gitbash
java -cp cermine-impl-1.13-jar-with-dependencies.jar pl.edu.icm.cermine.ContentExtractor -path . -outputs "jats,text,zones,trueviz,images"

# how to grab main text with jquery
$('.fs6').find('*').addBack().css('background-color','green') //main text
$('.xd.fs6, .x2.fs6, .x14.fs6').css('background-color','white') //indents incomplete

var x = $('.fs6').each(function(){
var x = $(this).position()
console.log(x.left)

})

