from bokeh.io import show, output_file
from bokeh.models import ColumnDataSource
from bokeh.palettes import brewer
from bokeh.plotting import figure
from bokeh.transform import factor_cmap
from bokeh.layouts import row
from bokeh.models import HoverTool, ColumnDataSource
from bokeh.palettes import Spectral10
from bokeh.palettes import Category20_20
from bokeh import palettes
from numpy import pi
from random import shuffle
import colorsys
from bokeh.layouts import layout 
from bokeh.models import ( 
  HoverTool, ColumnDataSource, Legend, LegendItem 
) 
from bokeh.plotting import figure 
from bokeh.palettes import brewer 
from bokeh.core.properties import value
import numpy as np
from numpy import pi
from random import shuffle
from math import sin,cos
from bokeh.plotting import ColumnDataSource,output_notebook,figure
from bokeh.models import HoverTool,Text
from bokeh import palettes
import pandas as pd

from bokeh.plotting import figure, show, output_file
from bokeh.palettes import brewer
from . import bokutils
#   $$Author1$:Nick Larsson, Researcher, Dep. of Computer Science and Information Systems at Birkbeck University, London, England, email:nick@dcs.bbk.ac.uk, License:GNU GPLv3

#We acknowledge the use of the following software under the terms of the specified licences:
#
#Python Flask - https://flask.palletsprojects.com/en/0.12.x/license/
#
#Bokeh - https://github.com/bokeh/bokeh/blob/master/LICENSE.txt
#
#
#
# - # - # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
# Thanks to Alex Fung 

class CustomPieBuilder:

    green ="#50ee70"
    red = "#ff7070"
    x_range = 1.1
    y_range = 1.1
# ## - - - -  - - - -
    def __init__(self,df,label_name,column_name,tools='hover',tooltips=None,
                 reverse_color=False,colors=None,random_color_order=False,
                 plot_width=bokutils.PLOT_WIDTH,plot_height=bokutils.PLOT_HEIGHT,title='Untitled',*args,**kwargs):
        p = self.setup_figure(tools,plot_width,plot_height,title)
        df = self.add_columns_for_pie_chart(df,column_name,colors,reverse_color,random_color_order)
        self.df = df
        self.plot_pie(p,df,label_name,*args,**kwargs)
        if tooltips:
            self.set_hover_tooltip(p,tooltips)

        self.add_text_label_on_pie(p,df,label_name)
        self.plot = p
# ## - - - -  - - - -
    def setup_figure(self,tools,plot_width,plot_height,title):
        p = figure(
            x_range=(-self.x_range, self.x_range),
            y_range=(-self.y_range, self.y_range),
            tools=tools,
            plot_width=plot_width,
            plot_height=plot_height,
            title=title,
        )
        p.axis.visible = False
        p.xgrid.grid_line_color = None
        p.ygrid.grid_line_color = None
        return p
# ## - - - -  - - - -
    @staticmethod
    def plot_pie(p,df,label_name,*args,**kwargs):
        for key, _df in df.groupby(label_name):
            source = ColumnDataSource(_df.to_dict(orient='list'))
            p.annular_wedge(
                x=0,
                y=0,
                inner_radius=0,
                outer_radius=1,
                start_angle='starts',
                end_angle='ends',
                color='colors',
                source=source,
                legend=key,
                *args,**kwargs)
# ## - - - -  - - - -
    @staticmethod
    def set_hover_tooltip(p,tooltips):
        hover = p.select({'type':HoverTool})
        hover.tooltips = tooltips
# ## - - - -  - - - -
    @staticmethod
    def add_columns_for_pie_chart(df,column_name,colors=None,reverse_color=False,random_color_order=False):
        r = 0.7
        df = df.copy()
        column_sum = df[column_name].sum()
        df['percentage'] = (df[column_name]/column_sum)
        percentages = [0]  + df['percentage'].cumsum().tolist()
        df['starts'] = [p * 2 * pi for p in percentages[:-1]]
        df['ends'] = [p * 2 * pi for p in percentages[1:]]

        df['middle'] = (df['starts'] + df['ends'])/2
        df['text_x'] = df['middle'].apply(cos)*r
        df['text_y'] =df['middle'].apply(sin)*r 
        df['text_angle'] = 0.0

        if colors:
            df['colors'] = colors
        else:
            if 'colors' not in df:
                reverse_color = -1 if reverse_color else 1
                colors = palettes.viridis(len(df))[::reverse_color]
                if random_color_order:
                    shuffle(colors)
                df['colors'] = colors
        return df
# ## - - - -  - - - -
    @staticmethod
    def add_text_label_on_pie(p,df,label_name):
        source=ColumnDataSource(df.to_dict(orient='list'))
        txt = Text(x="text_x", y="text_y", text=label_name, angle="text_angle",
               text_align="center", text_baseline="middle",
               text_font_size='10pt',)
        p.add_glyph(source,txt)
# ## - - - -  - - - -
def build_plot(df,label_name,column_name,tools='hover',tooltips=None,
	       reverse_color=False,colors=None,random_color_order=False,
	       plot_width=400,plot_height=400,title='Untitled',*args,**kwargs):

    pie = CustomPieBuilder(df,label_name,column_name,tools,tooltips,
			   reverse_color,colors,random_color_order,
			   plot_width,plot_height,title,*args,**kwargs)

    return pie.plot
# ## - - - -  - - - -
