# sozi2pdf
[Sozi](http://sozi.baierouge.fr/) is a great presentation editor to turn SVG files (e.g. created with Inkscape) into a html presentation which can be displayed in almost any modern web browser.
This is a tool to convert Sozi presentations to a PDF file. 

Note that there is another tool [sozi-to-pdf](https://github.com/senshu/Sozi-export) which can convert a Sozi presentation to PDF.
As of now (June 2016), 'sozi-to-pdf' renders each frame as a PNG image to produce the PDF. Instead, 'sozi2pdf' will produce a PDF with vector graphics. However, it is still experimental and does not yet support presentations with multiple layers. 


## How to use it?
If the SVG-file is ./presentation.svg and the Sozi JSON file ./presentation.sozi.json, then
```bash
./sozi2pdf.py presentation
```
will produce ./presentation.pdf.


## Requirements
* Inkscape
* Python
* PyPDF2

## Known problems:
* Presentations with multiple layers are not yet supported. 
* Very tiny objects might be missing in the PDF. This is due to a bug described [here](https://bugs.launchpad.net/inkscape/+bug/1174909). As a workaround, scaling of the whole document to increase the size of the tiny objects should help.



