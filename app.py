from flask import Flask, render_template, request
import pandas as pd

app = Flask(__name__)
app.debug = True

@app.route('/')
def index():
    df = pd.DataFrame({'name':['a','b']
                   , 'value':[3,4]})

    # Chart js format
    chart_df = df.to_dict(orient='records')

    return render_template('index.html', chart_df = chart_df)

@app.route('/update', methods=['POST'])
def update():
    if request.method == 'POST':
        print('In POST!!!')
        user_input = int(request.form.get('text'))
    data = render_template('update.html', user_input = user_input)
    return data

if __name__ == '__main__':
    app.run()