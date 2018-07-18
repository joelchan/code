const express = require('express')
var jsonfile = require('jsonfile')
var cors = require('cors')
var bodyParser = require('body-parser')
var file = __dirname + '/test.json'

const app = express()
app.use(cors())
app.use(bodyParser.json());
app.use(bodyParser.urlencoded({
  extended: true
}));

app.get('/', (req, res) => {
    res.sendFile(__dirname + '/index.html')
})

const dirRoot = 'E:/code/pdfToXml/processed_pdfs/'
const dirList = ['ExpertFacilitation', 'KnowledgeSharing', 'Sensemaking']

app.post('/:dirName', (req, res) => {
    const file = dirRoot + '/' + req.params.dirName + '/save.json'
    jsonfile.writeFile(file, req.body, function (err) {
        console.error(err)
      })
})

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