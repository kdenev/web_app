# Flask
from flask import Flask, render_template, request, jsonify
# Data management
import pandas as pd
# Yahoo
from yahooquery import Ticker
# Bokeh
from bokeh.resources import CDN
from bokeh.embed import components
from bokeh.plotting import show, figure
from bokeh.models import ColumnDataSource  

# Grab CDN resources
cdn_js = CDN.js_files[0]

# Create Flask app
app = Flask(__name__)
app.debug = True

@app.route('/')
def index():
    return render_template('index.html'
                           , cdn_js = cdn_js)

@app.route('/update', methods=['GET', 'POST'])
def update():
    if request.method == 'POST':
        print('In POST!!!')
        user_input = request.form.get('text')
        print(user_input)
        # Extract stock info
        t = Ticker(user_input)
        stock_data = t.history("ytd").reset_index()
        # Plot Data
        plot_df = stock_data[['date', 'adjclose']]
        print(plot_df)
        source = ColumnDataSource(plot_df)
        p = figure()
        p.line(x='date'
               ,y='adjclose'
               ,source = source)
        plot_js, plot_div = components(p)

    data = render_template('update.html'
                           , cdn_js = cdn_js
                           , plot_js = plot_js
                           , plot_div = plot_div 
                        )
    return data

if __name__ == '__main__':
    app.run(debug=True)