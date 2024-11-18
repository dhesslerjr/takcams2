from flask import Flask,render_template,request,jsonify

app = Flask(__name__)

@app.route("/")
def hello_world():
    return "<p>Hello, World!</p>"
    
@app.route('/hello')
@app.route('/hello/<name>')
def hello(name=None):
    return render_template('main.html',person=name)
    
    
@app.route('/lvflow',methods=["GET","POST"])
def lvflow_received():
    content=request.json
    if content:
        print(content)
    return jsonify(content)
    
    
