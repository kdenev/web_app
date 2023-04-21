# -*- coding: utf-8 -*-
"""
Created on Tue Oct 11 21:49:10 2022

@author: K&D
"""

from bokeh.resources import CDN
from bokeh.embed import components
from bokeh.plotting import figure
from bokeh.io import output_file, show
from bokeh.resources import INLINE
# from bokeh.sampledata.stocks import AAPL
from bokeh.models import (ColumnDataSource, CDSView, GroupFilter, 
                          HoverTool, PanTool, ZoomInTool, ZoomOutTool, 
                          ResetTool, DatetimeTickFormatter, CustomJS,
                          NumeralTickFormatter, CrosshairTool, TapTool,
                          MultiLine)
from bokeh.core.properties import Enum
from bokeh.models.annotations import Label
from concurrent.futures import ThreadPoolExecutor
import time

from datetime import datetime, timedelta
from yfinance import Ticker
import pandas as pd
import numpy as np

ticker_list = ['AAPL', 'BAC', 'NVDA']
# Split the returns in diff columns, so only 1 tooltip

def get_stock_chart_info(ticker_list, period = '3y'):
    
    output_df = pd.DataFrame()
    
    for i,t in enumerate(ticker_list):
        i_str = str(i)
        ticker_obj = Ticker(t)
        company_info = ticker_obj.stats()
        df = ticker_obj.history(period = period)
        df.reset_index(inplace=True)
        df[i_str+'_Close'] = df['Close']
        df['pct_change'] = df[i_str+'_Close'].pct_change()
        df[i_str+'_cum_return'] = (df['pct_change'] + 1).cumprod()
        # replace nan
        to_nparray = np.array(df[i_str+'_cum_return'])
        to_nparray[0] = 1
        df[i_str+'_cum_return'] = to_nparray - 1
        df[i_str+'_cum_return'] = df[i_str+'_cum_return']*100
        df[i_str+'_ticker'] = t
        df [i_str+'_name'] = company_info['price']['shortName']
        if i == 0:
            output_df = output_df.append(df[['Date', i_str+'_Close', 
                                             i_str+'_cum_return',
                                             i_str+'_ticker', i_str+'_name']])
        else:
            output_df = output_df.merge(df[['Date', i_str+'_Close',
                                            i_str+'_cum_return',
                                            i_str+'_ticker', i_str+'_name']], 
                                            how='inner', on='Date')
        
    return output_df

# start_time = time.time()
# get_stock_info(ticker_list)
# print("--- %s seconds ---" % (time.time() - start_time))


df = get_stock_chart_info(ticker_list)

# start_time = time.time()
# with ThreadPoolExecutor() as executor:
#     executor.map(get_stock_info, ticker_list)
# print("--- %s seconds ---" % (time.time() - start_time))


def create_stock_divs(COLORS_IN, ticker_list):
    
    COLORS = COLORS_IN
    
    text = ""    
    formaters = dict()
    formaters['@Date'] = 'datetime'
    
    for i in range(len(ticker_list)):
        
        text += f"""    <div>
                <span class="dot" 
                style = 
                "height: 10px;
                width: 10px;
                background-color: {COLORS[i]};
                border-radius: 50%;
                display: inline-block;"
                >
                </span>
                <span>@{i}_name: @{i}_Close{{0.2$}} (@{i}_cum_return{{%.2f %%}})</span>
            </div>""" 
        
        formaters[f'@{i}_cum_return'] = "printf"
        
    return text, formaters


def make_chart(df, ticker_list, plot_height=800, plot_width=1000):
    
    # Define the plot
    line_source = ColumnDataSource(df)
    circle_source = ColumnDataSource(df)
    stock_plot = figure(x_axis_type = 'datetime')
    stock_plot.width = plot_width
    stock_plot.height = plot_height
    
    # CONSTANTS
    COVID_START = datetime(2020,3, 20)
    FINANCIAL_CRISIS = datetime(2008, 11, 20)
    DOT_COM = datetime(2001, 5, 25)
    RECESSOION_DAYS = timedelta(days = 30)
    COLORS = ['#6495ED', '#000080', '#4169E1']
    # COLORS = ['#A9A9A9', '#2F4F4F', '#708090']
    # MAX_STOCK_PRICE = max(stock_data.data['Close'])
    # convert np.daytime64 to datetime.datetime
    MIN_STOCK_DATE = min(df['Date'])
    GRAPH_FONT = 'times'
    X_AXIS_LABEL = 'Date'
    Y_AXIS_LABEL = 'Price'
    AXIS_COLOR =  '#A9A9A9' #'#778899'
    X_Y_LABELS_SIZE = '20px'
    X_Y_LABELS_STYLE = 'bold italic'
    
    
    # Bokeh output
    # output_file("stock_plot.html")

    
    # Hover Tool Details
    hover = HoverTool()
    
    # hover.tooltips = [               
    #                 ("Date","@Date{%Y-%m-%d}")
    #                 # ,   ("Price","@Close{%0.2f}")
    #                 ,   ("@0_name", "@0_cum_return{%0.2f}")
    #                 ,   ("@1_name", "@1_cum_return{%0.2f}")
    #                 ,   ("@2_name", "@2_cum_return{%0.2f}")
    #                 # ,   ("Name","@name")
    #                 ]

    divs, formaters = create_stock_divs(COLORS, ticker_list)

    hover.tooltips = f"""
        
<div style = "font-family: 'Times New Roman', Times, serif;
              font-size: 16px;
              color: #778899;">
    
     <div>
         <span>@Date{{%d %B %Y}}</span>
     </div>
     
     {divs}
    
</div>

        
        """
    hover.formatters = formaters     
        
    hover.mode = 'vline'
    hover.show_arrow = False
    hover.names = ['0_line']

    
    hover2 = HoverTool()
    hover2.show_arrow = False
    hover2.tooltips = None
    hover2.names = ['0_circle']
    hover2.mode = 'vline'

    
    
    # Crosshair Tool Details
    crosshair = CrosshairTool()
    crosshair.line_color = AXIS_COLOR
    crosshair.dimensions = 'height'
    # crosshair.line_dash = 'dashed'
    
    
    # Plot lines
    
    
    # line_glyphs = []
    # circle_glyphs = []



    # stock_plot.line(x='Date', y='0_cum_return'
    #                 , line_dash="4 4", line_width=1
    #                 , color='gray'
    #                 , source = line_source)

    # cr = stock_plot.circle(x='Date', y='0_cum_return', size=20,
    #                 fill_color="grey", hover_fill_color="firebrick",
    #                 fill_alpha=0.05, hover_alpha=0.3,
    #                 line_color=None, hover_line_color="white"
    #                 , source = circle_source)   
    
    for i in range(len(ticker_list)):
        # Plot the stock Prices/Return
        
        stock_plot.line(
        x='Date'
        # , y=str(i)+'_cum_return'
        , y=str(i)+'_Close'
        # , legend_label = t
        , source = line_source
        , width = 2
        , color = COLORS[i]
        , name = str(i)+'_line'
        )

        
        # l = MultiLine(xs='Date', ys = str(i)+'_cum_return')
        
        # stock_plot.add_glyph(stock_data, l, name = str(i)+'_line')
                            

        stock_plot.circle(
        x='Date'
        , y=str(i)+'_Close'
        , fill_alpha=0
        , alpha = 0
        , size=15
        , source = circle_source
        , hover_fill_color= AXIS_COLOR
        , hover_alpha=0.7
        , hover_line_color="white"
        , name = str(i)+'_circle'
        )

            
        # if i%2 == 0:
        #     # horizontal, vertical, left, right, above or below
        #     hover.attachment = 'horizontal'
        # else:
        #     hover.attachment = 'vertical'
    
            
    # Plot Recession times
    
    if COVID_START > MIN_STOCK_DATE:
        stock_plot.rect(x = COVID_START, y=0
                        , width = [
                            RECESSOION_DAYS
                            , RECESSOION_DAYS*3
                            , RECESSOION_DAYS*4
                        ]
                        , height = 9999
                        , height_units="screen"
                        , color = 'pink'
                        , fill_alpha=0.3
                        , line_alpha=0
                        # , legend_label= 'COVID'
                        )
        
    if FINANCIAL_CRISIS > MIN_STOCK_DATE:
        stock_plot.rect(x = FINANCIAL_CRISIS, y=0
                        , width = [
                            RECESSOION_DAYS*2
                            , RECESSOION_DAYS*6
                            , RECESSOION_DAYS*12
                        ]
                        , height = 9999
                        , height_units="screen"
                        , color = 'pink'
                        , fill_alpha=0.3
                        , line_alpha=0
                        # , legend_label= 'COVID'
                        )
        
    if DOT_COM > MIN_STOCK_DATE:
        stock_plot.rect(x = DOT_COM, y=0
                        , width = [
                            RECESSOION_DAYS*3
                            , RECESSOION_DAYS*9
                            , RECESSOION_DAYS*16
                        ]
                        , height = 9999
                        , height_units="screen"
                        , color = 'pink'
                        , fill_alpha=0.3
                        , line_alpha=0
                        # , legend_label= 'COVID'
                        )
    
    # Label Annotation
    # description = Label(x=COVID_START
    #                     , y = .95 * MAX_STOCK_PRICE
    #                     , text="COVID-19"
    #                     , render_mode="css"
    #                     , text_align= 'center'
    #                     , text_font_style = 'italic'
    #                     , text_color = 'gray'
    #                     , text_font = GRAPH_FONT
    #                     )
    
    
    # Axis
    
    ######### X ##########
    
    
    stock_plot.xaxis.axis_label_text_font = GRAPH_FONT
    stock_plot.xaxis.axis_label = X_AXIS_LABEL
    stock_plot.xaxis.major_label_orientation = 'horizontal'
    stock_plot.xaxis.major_label_text_font = GRAPH_FONT
    stock_plot.xaxis[0].ticker.desired_num_ticks = 8
    stock_plot.xaxis.major_tick_in = 0
    stock_plot.xaxis.formatter=DatetimeTickFormatter(
            # hours=["%d %B %Y"],
            days=["%b %Y"],
            months=["%b %Y"],
            years=["%b %Y"],
        )
    stock_plot.xaxis.axis_label_text_font_size = X_Y_LABELS_SIZE
    stock_plot.xaxis.axis_label_text_font_style = X_Y_LABELS_STYLE
    stock_plot.xaxis.axis_label_text_color = AXIS_COLOR
    stock_plot.xaxis.axis_line_color = AXIS_COLOR
    stock_plot.xaxis.major_label_text_color = AXIS_COLOR
    stock_plot.xaxis.major_tick_line_color = AXIS_COLOR
    stock_plot.xaxis.minor_tick_line_color = AXIS_COLOR
    
    
    ######### Y ##########
    stock_plot.yaxis.axis_label_text_font_size = X_Y_LABELS_SIZE
    stock_plot.yaxis.formatter = NumeralTickFormatter(format='0.2')
    stock_plot.yaxis.axis_label_text_font = GRAPH_FONT
    stock_plot.yaxis.axis_label_text_font_style = X_Y_LABELS_STYLE
    stock_plot.yaxis.axis_label = Y_AXIS_LABEL
    stock_plot.yaxis.major_label_orientation = 'horizontal'
    stock_plot.yaxis.major_label_text_font = GRAPH_FONT
    stock_plot.yaxis.major_tick_in = 0
    stock_plot.yaxis.minor_tick_in = -5
    stock_plot.yaxis[0].ticker.desired_num_ticks = 8
    
    stock_plot.yaxis.axis_label_text_color = AXIS_COLOR
    stock_plot.yaxis.axis_line_color = AXIS_COLOR
    stock_plot.yaxis.major_label_text_color = AXIS_COLOR
    stock_plot.yaxis.major_tick_line_color = AXIS_COLOR
    stock_plot.yaxis.minor_tick_line_color = AXIS_COLOR
    
    # Background
    stock_plot.background_fill_color = None
    stock_plot.border_fill_color = None
    stock_plot.outline_line_alpha = 0
    # stock_plot.text_color = '#778899'
    # stock_plot.ygrid.grid_line_color = None
    # stock_plot.border_fill_alpha = 0
    
    # Grid
    stock_plot.xgrid.grid_line_color = None
    stock_plot.ygrid.grid_line_color = AXIS_COLOR
    stock_plot.ygrid.grid_line_alpha = .5
    # print(dir(stock_plot.ygrid))
    
    # Legend
    # stock_plot.legend.location = 'top_left'
    # stock_plot.legend.background_fill_color = None
    # stock_plot.legend.border_line_alpha = 0
    
    # Toolbar
    # stock_plot.toolbar_location = 'above'
    stock_plot.toolbar_location = None
    stock_plot.toolbar.logo = None
    
    # Tools
    # stock_plot.tools = [PanTool(), ResetTool()]
    
    stock_plot.add_tools(hover)
    stock_plot.add_tools(hover2)
    stock_plot.add_tools(crosshair)
    
    
    # Layouts
    # stock_plot.add_layout(description)
    
    return stock_plot


# df = get_stock_chart_info(ticker_list)
# show(make_chart(df, ticker_list))
