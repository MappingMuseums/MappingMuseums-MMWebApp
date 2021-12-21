from bokeh.plotting import figure, output_file, show
from bokeh.models import LabelSet, ColumnDataSource
from bokeh.embed import components
from . import bokutils
#   $$Author1$:Nick Larsson, Researcher, Dep. of Computer Science and Information Systems at Birkbeck University, London, England, email:nick@dcs.bbk.ac.uk, License:GNU GPLv3
#
#We acknowledge the use of the following software under the terms of the specified licences:
#

#Python Flask - https://flask.palletsprojects.com/en/0.12.x/license/
#
#Bokeh - https://github.com/bokeh/bokeh/blob/master/LICENSE.txt
#
#
#
# - # - # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
#- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
class BokehTree():


    @staticmethod
    def normalize_sizes(sizes, dx, dy):
        total_size = sum(sizes)
        total_area = dx * dy
        sizes = list(map(float, sizes))
        sizes = list(map(lambda size: size * total_area / total_size, sizes))
        return sizes
       
#- - - - - - - - - - - - -
    @staticmethod
    def layoutrow(sizes, x, y, dx, dy):
        covered_area = sum(sizes)
        width = covered_area / dy
        rects = []
        for size in sizes:
            rects.append({'x': x, 'y': y, 'dx': width, 'dy': size / width})
            y += size / width
        return rects

#- - - - - - - - - - - - -
    
    @staticmethod
    def layoutcol(sizes, x, y, dx, dy):
        covered_area = sum(sizes)
        height = covered_area / dx
        rects = []
        for size in sizes:
            rects.append({'x': x, 'y': y, 'dx': size / height, 'dy': height})
            x += size / height
        return rects

#- - - - - - - - - - - - -
    
    @staticmethod
    def layout(sizes, x, y, dx, dy):
        return BokehTree.layoutrow(sizes, x, y, dx, dy) if dx >= dy else BokehTree.layoutcol(sizes, x, y, dx, dy)

#- - - - - - - - - - - - -
    
    @staticmethod
    def leftoverrow(sizes, x, y, dx, dy):
        covered_area = sum(sizes)
        width = covered_area / dy
        leftover_x = x + width
        leftover_y = y
        leftover_dx = dx - width
        leftover_dy = dy
        return (leftover_x, leftover_y, leftover_dx, leftover_dy)

#- - - - - - - - - - - - -
    
    @staticmethod
    def leftovercol(sizes, x, y, dx, dy):
        covered_area = sum(sizes)
        height = covered_area / dx
        leftover_x = x
        leftover_y = y + height
        leftover_dx = dx
        leftover_dy = dy - height
        return (leftover_x, leftover_y, leftover_dx, leftover_dy)

#- - - - - - - - - - - - -
    
    @staticmethod
    def leftover(sizes, x, y, dx, dy):
        return BokehTree.leftoverrow(sizes, x, y, dx, dy) if dx >= dy else BokehTree.leftovercol(sizes, x, y, dx, dy)

#- - - - - - - - - - - - -
       
    @staticmethod
    def worst_ratio(sizes, x, y, dx, dy):
        return max([max(rect['dx'] / rect['dy'], rect['dy'] / rect['dx']) for rect in BokehTree.layout(sizes, x, y, dx, dy)])

#- - - - - - - - - - - - -
    
    @staticmethod
    def squarify(sizes, x, y, dx, dy):
        sizes = list(map(float, sizes))
        if len(sizes) == 0:
            return []
        if len(sizes) == 1:
            return BokehTree.layout(sizes, x, y, dx, dy)
        # figure out where 'split' should be
        i = 1
        while i < len(sizes) and BokehTree.worst_ratio(sizes[:i], x, y, dx, dy) >= BokehTree.worst_ratio(sizes[:(i+1)], x, y, dx, dy):
            i += 1
        current = sizes[:i]
        remaining = sizes[i:]
        (leftover_x, leftover_y, leftover_dx, leftover_dy) = BokehTree.leftover(current, x, y, dx, dy)
        return BokehTree.layout(current, x, y, dx, dy) + BokehTree.squarify(remaining, leftover_x, leftover_y, leftover_dx, leftover_dy)
    

#- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

    def createPlot(self):
       
        x = 0.
        y = 0.
        width = 1
        height = 1
        norm_x= 1
        norm_y= 1
                 
           
        #### Please input your data here
        source = ColumnDataSource(
        data=dict(
                Labels = ['Granny Smith', 'Pink Lady', 'MCIntosh', 'Golden', 'Bosc',
                          'Comice', 'Red Anjou', 'bananas', 'Passion Fruit', 'Avocado',
                          'Lychee'],
                Quantity = [7, 12, 10, 2, 18, 14, 13, 3, 5, 9, 17],
                CVitamin = [12, 4.8, 11.6, 17.4, 5.6, 8.0, 8.0, 10.2, 60, 12.5, 6.6],
                Colors = ['#001a70', '#003089', '#0045a2', '#005bbb', '#509e2f', '#8aba18',
                          '#c4d600', '#001a70', '#003089', '#0045a2', '#005bbb'],
                Units = [' mg/100g']*11
                )
        )  
        
        #### Select data to use as input for size of the rectangles (will be normalized)
        values = source.data['Quantity']
        
        #### Calculation of rects size, coords
        values.sort(reverse=True)
        
        values = BokehTree.normalize_sizes(source.data['Quantity'], width, height)
        
        rects = BokehTree.squarify(values, x, y, width, height)
        
        X = [rect['x'] for rect in rects]
        Y = [rect['y'] for rect in rects]
        dX = [rect['dx'] for rect in rects]
        dY = [ rect['dy'] for rect in rects]
        
        
        XdX = []
        YdY = []
        
        for i in range(len(X)):
            XdX.append(X[i]+dX[i])
            YdY.append(Y[i]+dY[i])
        
        #### Preparation of labels - compute rects centers in particular
        Xlab = []
        Ylab = []
        for r in rects:
            x, y, dx, dy = r['x'], r['y'], r['dx'], r['dy']
            Xlab.append(x+dx/2)
            Ylab.append(y+dy/2)
        
        #### Now we have everything ready, let's gather data for the treemap
        plotsource = ColumnDataSource(
            data=dict(
                Xlab = Xlab,
                Ylab = Ylab,
                CVitamin = source.data['CVitamin'],
                Colors = source.data['Colors'],
                Labels = source.data['Labels'],
                Units = source.data['Units']
            )
        )
        
        #### Bokeh figure :
        
        output_file("Bokeh Treemap.html", mode = 'inline')
        
        p = figure(plot_height=bokutils.PLOT_HEIGHT,plot_width=bokutils.PLOT_WIDTH, title = 'Fruit Inventory, plus Vitamin C content')
        p.quad(top=YdY, bottom=Y, left=X, right=XdX, color=plotsource.data['Colors'])
        
        p.axis.visible = False
        
        labels1 = LabelSet(x='Xlab', y='Ylab', text='Labels', level='glyph',
            text_font_style='bold', text_color='white', text_align = 'center',
            source=plotsource)
        
        labels2 = LabelSet(x='Xlab', y='Ylab', text='CVitamin', level='glyph',
        text_font_style='bold', text_color='white', text_align = 'right',
        y_offset = -20, source=plotsource)
        
        labels3 = LabelSet(x='Xlab', y='Ylab', text='Units', level='glyph',
        text_font_style='bold', text_color='white', text_align = 'left',
        y_offset = -20, source=plotsource)
        
        p.add_layout(labels1)
        p.add_layout(labels2)
        p.add_layout(labels3)
        return p
    
