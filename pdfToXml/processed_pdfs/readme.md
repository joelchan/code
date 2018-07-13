
# from pdf to semantic html while preserving layout
pdf2htmlEX ExpertFacilitation/2016-cscw-ideagens-facexp.pdf --embed-external-font 1 --embed cfijo --embed-outline 0 --decompose-ligature 1 --optimize-text 1 --dest expert1
copy parse.js into --dest folder from other processed pdfs
remove fancy.css
add
```
<script src="https://code.jquery.com/jquery-3.3.1.min.js" integrity="sha256-FgpCb/KJQlLNfOu91ta32o/NMZxltwRo8QtmkMRdAu8="
crossorigin="anonymous"></script>
<script src="https://unpkg.com/rxjs@6.2.1/bundles/rxjs.umd.min.js"></script>
<script src="parse.js"></script>
```
browser-sync start --server --index 2016-cscw-ideagens-facexp.html --watch '*'