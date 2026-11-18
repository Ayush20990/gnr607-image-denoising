"""Shared editorial styling for editable PowerPoint experiment slides."""
from pathlib import Path
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE_TYPE
from pptx.enum.text import PP_ALIGN

INK='16263D'; DARK='101E30'; PAPER='F8F6F2'; WHITE='FFFFFF'
CORAL='EB654C'; MUTED='667386'; PALE='B6C2D1'; LIGHT='EBE8E2'
def rgb(s):return RGBColor.from_string(s)
def box(s,x,y,w,h,value,size,color=INK,bold=False):
    sh=s.shapes.add_textbox(Inches(x),Inches(y),Inches(w),Inches(h))
    tf=sh.text_frame;tf.word_wrap=True;tf.margin_left=tf.margin_right=tf.margin_top=tf.margin_bottom=0
    for i,line in enumerate(value.split('\n')):
        p=tf.paragraphs[0] if i==0 else tf.add_paragraph();p.text=line
        p.font.name='Aptos';p.font.size=Pt(size);p.font.color.rgb=rgb(color);p.font.bold=bold;p.space_after=Pt(10)
    return sh

def polish(prs,root):
    satellite='Satellite' in root.name or 'satellite' in root.name
    total=len(prs.slides)
    for i,s in enumerate(prs.slides):
        labels=[sh.text for sh in s.shapes if sh.has_text_frame]
        section=labels[0] if labels else ''
        dark=section in ('VISUAL COMPARISON','FIXED CROP','CONCLUSIONS')
        s.background.fill.solid();s.background.fill.fore_color.rgb=rgb(DARK if dark else PAPER)
        for sh in s.shapes:
            if sh.has_text_frame:
                top=sh.top/Inches(1)
                for p in sh.text_frame.paragraphs:
                    p.font.name='Aptos'
                    if top<.6:p.font.color.rgb=rgb(CORAL);p.font.size=Pt(11);p.font.bold=True
                    elif top<1.7:p.font.color.rgb=rgb(WHITE if dark else INK);p.font.size=Pt(32);p.font.bold=True
                    elif top>7:p.font.color.rgb=rgb(PALE if dark else MUTED);p.font.size=Pt(9)
                    elif top>=6.1:p.font.color.rgb=rgb(PALE if dark else MUTED)
                    elif 'MSE:' in sh.text:p.font.color.rgb=rgb(CORAL)
                    else:p.font.color.rgb=rgb(WHITE if dark else INK)
                if sh.text.strip()==str(i+1) and top>7:
                    sh.text_frame.paragraphs[0].text=f'{i+1:02d} / {total:02d}'
                    sh.left=Inches(11.8);sh.width=Inches(.9)
            if sh.has_table:
                numerical=sh.table.cell(0,0).text=='48'
                for r,rr in enumerate(sh.table.rows):
                    for c,cell in enumerate(rr.cells):
                        bg=INK if r==0 and not numerical else (WHITE if r%2 else LIGHT)
                        fg=WHITE if r==0 and not numerical else INK
                        if numerical:
                            chosen=cell.text in ('48','49','50','51','52');bg=CORAL if chosen else LIGHT;fg=WHITE if chosen else MUTED
                        cell.fill.solid();cell.fill.fore_color.rgb=rgb(bg)
                        for p in cell.text_frame.paragraphs:p.font.name='Aptos';p.font.color.rgb=rgb(fg)
            if sh.has_chart:
                chart=sh.chart
                for series,clr in zip(chart.series,[MUTED,CORAL,'007F86']):
                    series.format.line.color.rgb=rgb(clr)
                    try:
                        series.marker.format.fill.solid();series.marker.format.fill.fore_color.rgb=rgb(clr);series.marker.format.line.color.rgb=rgb(clr)
                    except AttributeError:pass
        if section in ('VISUAL COMPARISON','FIXED CROP'):
            pics=[sh for sh in s.shapes if sh.shape_type==MSO_SHAPE_TYPE.PICTURE]
            for j,sh in enumerate(pics):sh.left=Inches(.6+j*3.15);sh.top=Inches(2.18);sh.width=sh.height=Inches(3.0)
            for sh in s.shapes:
                if sh.has_text_frame and 1.7<sh.top/Inches(1)<2.1:sh.top=Inches(1.72)
        if section=='CONCLUSIONS':
            for sh in s.shapes:
                if sh.has_text_frame and sh.top/Inches(1)==.88:sh.text_frame.paragraphs[0].text='What the experiment shows'
    # Editorial cover: full source image alongside a strong typographic block.
    s=prs.slides[0]
    for sh in list(s.shapes):sh._element.getparent().remove(sh._element)
    s.background.fill.solid();s.background.fill.fore_color.rgb=rgb(DARK)
    box(s,.7,.55,6,.4,'GNR 607  /  IMAGE PROCESSING',12,CORAL,True)
    box(s,.7,1.55,6.25,1.9,'Noise removal\nfrom satellite images' if satellite else 'Noise removal\nin everyday images',38,WHITE,True)
    box(s,.7,4.0,5.9,1.1,'K-nearest-neighbour smoothing\nversus simple averaging',24,PALE)
    box(s,.7,5.9,5.9,.6,'5%   /   10%   /   20%',30,CORAL,True)
    box(s,.7,6.65,5.9,.4,'Uniform-noise standard deviation',17,PALE)
    hero=root/'data'/('urban.png' if satellite else 'astronaut.png')
    s.shapes.add_picture(str(hero),Inches(7.25),Inches(.68),width=Inches(5.4),height=Inches(5.4))
    box(s,7.25,6.35,5.4,.65,'SENTINEL-2 · NETHERLANDS\n768 × 768 crops · false colour' if satellite else 'GRAYSCALE + RGB COLOUR\n512 × 512 reference photographs',16,PALE)
