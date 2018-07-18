const express = require('express')
const app = express()

// ;
app.get('/', (req, res) => {
    res.sendFile(__dirname + '/index.html')
})

const dirRoot = 'E:/code/pdfToXml/processed_pdfs/'
const dirList = ['ExpertFacilitation', 'KnowledgeSharing', 'Sensemaking']

dirList.forEach(dirName => {
    app.use('/' + dirName, express.static(dirRoot + dirName, {
        index: 'index.html'
    }))
    app.get('/' + dirName, (req, res) => {
        res.sendFile('index.html', {root: staticDir})
    })
})


app.listen(5656, () => {
    console.log('http://localhost:5656')
})