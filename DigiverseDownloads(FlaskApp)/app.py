from flask import Flask, render_template, jsonify
from getimages import get_images

app = Flask(__name__)

@app.route('/navmenu')
def navmenu():
    return render_template('NavMenu.html')

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/blog')
def blog():
    return render_template('blog.html')

@app.route('/demos')
def demos():
    return render_template('demos.html')

@app.route('/images')
def images():
    image_list = get_images()
    return jsonify(image_list)

@app.route('/demos/GridEx')
def gridex():
    return render_template('GridEx.html')

@app.route('/demos/slideshow')
def slideshow():
    return render_template('slideshow.html')

@app.route('/store')
def store():
    return render_template('store.html')

@app.route('/appstore')
def appstore():
    return render_template('appstore.html')

if __name__ == '__main__':
    app.run()