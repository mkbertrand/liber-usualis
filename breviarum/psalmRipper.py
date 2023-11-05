#!/usr/bin/env python3

#Goal: Transform the text files containing the psalm information
#into JSON files, formatted as per psalmExample.json

#Data from a 1888 Roman Breviary:

#Note: at certain points, the page numbering restarts ends; latter numbering is denoted in other ways
#PDF pg 29 = Breviary pg 1, 1pg to 1 pg; PDF pg 573 = Breviary pg [1]
#pg 980-981 ([409-410] of the official numbering) of Verna has a psalms index, following pages have canticles index
#Add 28 to the Breviary pg number to get the PDF pg to go to

from collections import defaultdict
import json
import logging
import pathlib
import re
import typing
import io
import os
hester='NovaVulgata1979'
#hester='liber-usualis/breviarum/psalmi1962'
#hester='~/liber-usualis/breviarum/psalmi1962'
#print('vincere')
#for root, dirs, files in os.walk(hester):
#    print(root)
#    for name in files:
#        print(name)
#        if name=='index.js' or name=='index.html':
#            l=1
#        else:
#            l=0
#        textLines=loadData(name)
#        textLines=ripper(textLines,l)
#        toFile(textLines, name)

def loadData(filename: str):
    #print(os.getcwd())
    with io.open(filename) as f:
        content=f.readlines()
    return content

def toFile(content, filename: str):
    file = io.open(filename, "w", encoding='utf_8', newline='\n')
    file.writelines(content)
    file.close()


    #generate filename
    #if x<10:
    #    filename='psalmi1962/00'+str(x)
    #elif x>=10 and x<100:
    #    filename='psalmi1962/0'+str(x)
    #elif x>=100:
    #    filename='psalmi1962/'+str(x)

def ripper(textLines, l):


    #strip trailing and leading whitespace, #add verse numbers
    verses=len(textLines)
    for i in range(verses):
        textLines[i].rstrip()
        if l==1:
            textLines[i].lstrip()
        #v=i+1
        #if v<10:
        #    ver='00'+str(v)
        #elif v>=10 and v<100:
        #    ver='0'+str(v)
        #elif v>=100:
        #    ver=str(v)
        #textLines[i]=ver+' '+textLines[i]
    return textLines
    #insert data

for root, dirs, files in os.walk(hester):
    for name in files:
        if name=='index.js' or name=='index.html':
            l=0
        else:
            l=1
        textLines=loadData(hester+'/'+name)
        textLines=ripper(textLines,l)
        toFile(textLines, hester+'/'+name)

#for i in $(seq 1 150);
#do
#    if [ $i -lt 10 ]; then
#        echo $i
#    elif [$i -lt 100 && $i -ge 10]; then
#        echo $i
#    elif [$i -lt 150 && $i -ge 100]; then
#        echo $i
#    else
#        break
#    fi
#done
