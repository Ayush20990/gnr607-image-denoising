from pathlib import Path
import csv,json
import numpy as np
from scipy.io import loadmat
from PIL import Image
from pptx import Presentation
from pptx.util import Inches,Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.chart.data import CategoryChartData
from pptx.enum.chart import XL_CHART_TYPE,XL_LEGEND_POSITION

NAVY='14243D';TEAL='007F86';ORANGE='C25E25';GRAY='526174';LIGHT='ECF2F5';WHITE='FFFFFF'
FONT='Aptos'
prs=Presentation();prs.slide_width=Inches(13.333333);prs.slide_height=Inches(7.5)
def color(h):return RGBColor.from_string(h)
def text(s,x,y,w,h,content,size=22,bold=False,clr=NAVY,align=PP_ALIGN.LEFT):
    sh=s.shapes.add_textbox(Inches(x),Inches(y),Inches(w),Inches(h));tf=sh.text_frame;tf.word_wrap=True
    tf.margin_left=tf.margin_right=0;tf.margin_top=tf.margin_bottom=0
    for i,line in enumerate(content.split('\n')):
        p=tf.paragraphs[0] if i==0 else tf.add_paragraph();p.text=line;p.font.name=FONT;p.font.size=Pt(size);p.font.bold=bold;p.font.color.rgb=color(clr);p.alignment=align;p.space_after=Pt(8)
    return sh
def slide(title,section,notes=''):
    s=prs.slides.add_slide(prs.slide_layouts[6]);s.background.fill.solid();s.background.fill.fore_color.rgb=color(WHITE)
    text(s,.6,.35,11,.3,section.upper(),11,True,TEAL)
    text(s,.6,.88,12.1,.8,title,32,True)
    text(s,.6,7.10,11,.22,'GNR 607 · Uniform-noise removal · 512 × 512 image experiment',10,False,GRAY)
    text(s,12.15,7.08,.5,.25,str(len(prs.slides)),11,False,GRAY,PP_ALIGN.RIGHT)
    s.notes_slide.notes_text_frame.text=notes
    return s
def para(s,x,y,w,title,body,size=21):
    text(s,x,y,w,.45,title,23,True,TEAL)
    text(s,x,y+.58,w,1.65,body,size)
def table(s,x,y,w,h,headers,rows,widths=None,size=20):
    sh=s.shapes.add_table(len(rows)+1,len(headers),Inches(x),Inches(y),Inches(w),Inches(h));t=sh.table
    if widths:
        for c,v in zip(t.columns,widths):c.width=Inches(v)
    for r,vals in enumerate([headers]+rows):
        for c,v in enumerate(vals):
            cell=t.cell(r,c);cell.text=str(v);cell.margin_left=Inches(.14);cell.margin_right=Inches(.1);cell.margin_top=Inches(.08);cell.margin_bottom=Inches(.06);cell.vertical_anchor=MSO_ANCHOR.MIDDLE
            cell.fill.solid();cell.fill.fore_color.rgb=color(NAVY if r==0 else (LIGHT if r%2 else WHITE))
            for p in cell.text_frame.paragraphs:
                p.font.name=FONT;p.font.size=Pt(size);p.font.bold=r==0;p.font.color.rgb=color(WHITE if r==0 else NAVY)
    return t
def photo(s,path,x,y,w,h=None):
    return s.shapes.add_picture(str(path),Inches(x),Inches(y),width=Inches(w),height=Inches(h or w))
