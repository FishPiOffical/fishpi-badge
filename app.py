from flask import Flask, request, render_template, make_response

from static import handler
app = Flask(__name__)

@app.route('/gen')
def index():  # put application's code here
    t = handler.提取参数(request)
    text = handler.生(**t) 
    response = make_response(render_template("gen.html", svg=text))
    response.headers['cache-control'] = "max-age=86400"
    response.headers['content-type'] = "image/svg+xml"
    return response


if __name__ == '__main__':
    app.run(debug=True)
