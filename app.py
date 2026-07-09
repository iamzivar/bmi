from flask import Flask, render_template

app = Flask(__name__, template_folder='.')

@app.route('/')
def index():
    return render_template('index.html', lang='fa', tr={'title': 'تست', 'age': 'سن', 'height': 'قد', 'weight': 'وزن', 'submit': 'ادامه'})

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000)
