#!/usr/bin/python
# -*- coding: utf-8 -*-
#
#    Copyright 2015
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.


import os
import sys
import tempfile
import shutil
import json
from lxml import etree
import PyPDF2


def get_frames_from_json(name):
    '''load Sozi's json file and return list of frames'''
    jsonfn = name+'.sozi.json'
    if not os.path.exists(jsonfn):
        raise Exception('Error: File %s not found.'%jsonfn)
    jsonfile = open(jsonfn)
    jsonraw = jsonfile.read()
    objects = json.loads(jsonraw)
    jsonfile.close()
    return objects['frames']

def write_svg(frame, source, target):
    '''Write an svg with the content of that frame.'''
    camerastate = frame['cameraStates']['layer1']

    #load svg
    ET = etree.parse(source+'.svg')
    root = ET.getroot()

    defs = None
    layer1 = None
    for child in root.iterchildren():
        if 'defs' in child.tag:
            defs = child
        if child.get('id') == 'layer1':
            layer1 = child
    if defs is None:
        raise Exception('no defs found')
    if layer1 is None:
        raise Exception('no layer1 found')

    #resize page and translate
    root.set('width',str(camerastate['width'])+'px')
    root.set('height',str(camerastate['height'])+'px')
    root.set('viewBox'," ")

    translate_x, translate_y = 0,0
    if 'transform' in layer1.keys():
        transform = layer1.get('transform')
        if transform[:9]=='translate':
            translate_x, translate_y = eval(transform[9:])
        else:
            raise Exception('Error: This is not implemented.')
    translate_x = translate_x - camerastate['cx'] + 0.5*camerastate['width']
    translate_y = translate_y - camerastate['cy'] + 0.5*camerastate['height']
    layer1.set('transform','translate(%f,%f)'%(translate_x,translate_y))


    #clipping
    clip_width = camerastate['clipWidthFactor']*camerastate['width']
    clip_height = camerastate['clipHeightFactor']*camerastate['height']
    clip_x = 0.5*camerastate['width'] - 0.5*camerastate['clipWidthFactor']*camerastate['width'] + camerastate['clipWidthFactor']*camerastate['clipXOffset']-translate_x
    clip_y = 0.5*camerastate['height'] - 0.5*camerastate['clipHeightFactor']*camerastate['height'] + camerastate['clipHeightFactor']*camerastate['clipYOffset']-translate_y
    clippath = etree.fromstring("""
        <clipPath clipPathUnits="userSpaceOnUse" id="clipPath_for_visible_area">
          <rect style="color:#000000;clip-rule:nonzero;display:inline;overflow:visible;visibility:visible;opacity:0.58849553;isolation:auto;mix-blend-mode:normal;color-interpolation:sRGB;color-interpolation-filters:linearRGB;solid-color:#000000;solid-opacity:1;fill:#000000;fill-opacity:1;fill-rule:nonzero;stroke:#000000;stroke-width:5;stroke-linecap:butt;stroke-linejoin:miter;stroke-miterlimit:4;stroke-dasharray:none;stroke-dashoffset:0;stroke-opacity:1;color-rendering:auto;image-rendering:auto;shape-rendering:auto;text-rendering:auto;enable-background:accumulate"
           id="cliprect4139" 
           width="%f" 
           height="%f" 
           x="%f" 
           y="%f"/>
        </clipPath>
        """ % (clip_width, clip_height, clip_x, clip_y))
    defs.append(clippath)
    layer1.set('clip-path', "url(#%s)"%(clippath.get('id')))

    #save svg
    ET.write(target)


if __name__ == '__main__':
    filename = os.path.splitext(sys.argv[1])[0]
    frames = get_frames_from_json(filename)
    pdffiles = []
    tmpdir = tempfile.mkdtemp()
    for i,f in enumerate(frames):
        name = os.path.join(tmpdir,'%.4i'%(i))
        write_svg(f, filename, name+'.svg')
        pdffiles.append(name+'.pdf')
        os.system("inkscape %s.svg --export-area-page --export-pdf=%s.pdf" % (name,name))
    width = str(frames[0]['cameraStates']['layer1']['width'])+'px'
    height = str(frames[0]['cameraStates']['layer1']['height'])+'px'
    reader = PyPDF2.PdfFileReader(open(pdffiles[0],'rb'))
    page = reader.getPage(0)
    x1,y1,x2,y2 = page.mediaBox
    w,h = float(x2-x1), float(y2-y1)
    writer = PyPDF2.PdfFileWriter()
    for pdf in pdffiles:
        reader = PyPDF2.PdfFileReader(open(pdf,'rb'))
        page = reader.getPage(0)
        x1,y1,x2,y2 = page.mediaBox
        page.scaleBy(w/float(x2-x1))
        writer.addPage(page)
    writer.write(open(filename+'.pdf','wb'))
    shutil.rmtree(tmpdir)
