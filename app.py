
# coding: utf-8

# In[4]:

import requests
import pandas as pd
import simplejson as json
from bokeh.plotting import figure,show
from bokeh.palettes import Spectral11
from bokeh.embed import components
from bokeh.layouts import row, column,gridplot
from bokeh.models import ColumnDataSource, HoverTool, Legend
from flask import Flask,render_template,request,redirect,session


app = Flask(__name__)

app.vars={}

@app.route('/')
def main():
  return redirect('/index')

@app.route('/index', methods=['GET'])
def index():
    return render_template('index.html')
    
@app.route('/plot', methods=['POST'])
def plot(): 
    api_key = 'WtsnqndaKo-ZexTA5Jr2'
    tools = "pan,wheel_zoom,reset,hover,save"
    
    #Function which builds a data frame from input ticker
    def get_data(ticker):
        api_url = 'https://www.quandl.com/api/v1/datasets/WIKI/%s.json?api_key=%s' % (ticker, api_key)
        session = requests.Session()
        session.mount('http://', requests.adapters.HTTPAdapter(max_retries=3))
        raw_data = session.get(api_url)
        data = raw_data.json()
        df = pd.DataFrame(data['data'], columns=data['column_names'])
        df['Date'] = pd.to_datetime(df['Date'])
        return df
    
    #From the first ticker get the data and put it in a datafram
    app.vars['ticker1'] = request.form['ticker1']
    df = get_data(app.vars['ticker1'])
    
    #Check to see if we have custom dates
    if request.form['yesno'] == 'YES':
        custom_dates = True
        start_date = pd.to_datetime(request.form['start'])
        end_date = pd.to_datetime(request.form['end'])
        if start_date < df['Date'].iloc[-1]:
            start_date = df['Date'].iloc[-1]
        if end_date > df['Date'].iloc[0]:
            end_date = df['Date'].iloc[0]
        df = df[(df['Date'] >= start_date) & (df['Date'] <= end_date)]
    else:
        custom_dates = False
    

    
    if request.form['2stocks'] == "YES":
        app.vars['ticker2'] = request.form['ticker2']
        df2 = get_data(app.vars['ticker2'])
        if custom_dates:
            df2 = df2[(df2['Date'] >= start_date) & (df2['Date'] <= end_date)]
        
        s1 = figure(title='%s' % app.vars['ticker1'], plot_width = 420, plot_height = 220, tools = tools,
            x_axis_label='date',
            x_axis_type='datetime')
        s2 = figure(title='%s' % app.vars['ticker2'], plot_width = 420, plot_height = 220, tools = tools,
            x_axis_label='date',
            x_axis_type='datetime')
        s3 = figure(title='%s vs %s' % (app.vars['ticker1'],app.vars['ticker2']), plot_width = 900, plot_height = 200, tools = tools,
            x_axis_label='date',
            x_axis_type='datetime')
        
        s1.line(x=df['Date'].values, y=df['Close'].values,line_width=2, legend='Close')
        s2.line(x=df2['Date'].values, y=df2['Close'].values,line_width=2, legend='Close')
        if request.form.get('Close'):
            s3.line(x=df['Date'].values, y=df['Close'].values,line_width=2,line_color="RoyalBlue", legend='Close %s' %app.vars['ticker1'])
            s3.line(x=df2['Date'].values, y=df2['Close'].values,line_width=2,line_color="SkyBlue", legend='Close %s'%app.vars['ticker2'])
        if request.form.get('Adjusted close'):
            s3.line(x=df['Date'].values, y=df['Adj. Close'].values,line_width=2, line_color="Orange", legend='Adj. Close %s' %app.vars['ticker1'])
            s3.line(x=df2['Date'].values, y=df2['Adj. Close'].values,line_width=2, line_color="OrangeRed", legend='Adj. Close %s' %app.vars['ticker2'])
            
        if request.form.get('Open'):
            s3.line(x=df['Date'].values, y=df['Open'].values,line_width=2, line_color="Navy", legend='Open %s'%app.vars['ticker1'])
            s3.line(x=df2['Date'].values, y=df2['Open'].values,line_width=2, line_color="Purple", legend='Open %s' %app.vars['ticker2'])
 
        if request.form.get('Adjusted open'):
            s3.line(x=df['Date'].values, y=df['Adj. Open'].values,line_width=2, line_color="Teal", legend='Adj. Open %s'%app.vars['ticker1'])
            s3.line(x=df2['Date'].values, y=df2['Adj. Open'].values,line_width=2, line_color="Turquoise", legend='Adj. Open %s' %app.vars['ticker2'])
        
        s1.legend.location = 'top_left'
        s2.legend.location = 'top_left'
        s3.legend.location = 'top_left'
        hover1 = s1.select_one(HoverTool)
        hover1.tooltips = [("Price", "$y{0.2f}")]
        hover2 = s2.select_one(HoverTool)
        hover2.tooltips = [("Price", "$y{0.2f}")]
        hover3 = s3.select_one(HoverTool)
        hover3.tooltips = [("Price", "$y{0.2f}")]
        p = gridplot([[s1, s2], [s3]])
        
        script, div = components(p)
        return render_template('plot.html', script=script, div=div)
    
    else:
    
        p = figure(title='%s' % app.vars['ticker1'], plot_width = 900, plot_height = 200, tools = tools,
                x_axis_label='Date',
                x_axis_type='datetime')

        if request.form.get('Close'):
            p.line(x=df['Date'].values, y=df['Close'].values,line_width=2, legend='Close')
        if request.form.get('Adjusted close'):
            p.line(x=df['Date'].values, y=df['Adj. Close'].values,line_width=2, line_color="green", legend='Adj. Close')
        if request.form.get('Open'):
            p.line(x=df['Date'].values, y=df['Open'].values,line_width=2, line_color="red", legend='Open')
        if request.form.get('Adjusted open'): 
            p.line(x=df['Date'].values, y=df['Adj. Open'].values,line_width=2, line_color="purple", legend='Adj. Open')
        
        hover = p.select_one(HoverTool)
        hover.tooltips = [("Price", "$y{0.2f}")]
        p.legend.location = "top_left"   
        script, div = components(p)
        return render_template('plot.html', script=script, div=div)



    
if __name__ == '__main__':
    app.run(port=33507)









