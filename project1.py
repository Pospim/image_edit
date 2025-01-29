from flask import Flask, render_template, request, flash, redirect, url_for, send_from_directory, session
from PIL import Image
from werkzeug.utils import secure_filename
from utils.image_edit import *
import numpy as np
import os, time
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)

app = Flask(__name__)
app.secret_key = os.urandom(24)

UPLOAD_FOLDER = 'static/uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['ALLOWED_EXTENSIONS'] = {'png', 'jpg', 'jpeg', 'gif'}

os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

@app.route('/upload', methods=['POST'])
def upload_image():
    if 'image' not in request.files:
        return redirect(url_for('home'))
    file = request.files['image']

    if file.filename == '':
        flash('No file selected.')
        return redirect(url_for('home'))
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        session['current_image'] = filename
        return redirect(url_for('edit_image'))
    else:
        flash('File type not allowed.')
        return redirect(url_for('home'))


@app.route('/edit')
def edit_image():
    if 'current_image' not in session:
        return redirect(url_for('home'))
    filename = session['current_image']
    image_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    image = Image.open(image_path)
    width, height = image.size
    brightness_val = session.get('brightness', 100)

    resize_w = session.get('resize_width', width)
    resize_h = session.get('resize_height', height)

    timestamp = str(time.time())
    image_url = url_for('uploaded_file', filename=filename) + f'?t={timestamp}'

    return render_template(
        'edit.html',
        image_url=image_url,
        brightness=brightness_val,
        resize_width=resize_w,
        resize_height=resize_h
    )

@app.route('/apply_edit', methods=['POST'])
def apply_edit():
    if 'current_image' not in session:
        return redirect(url_for('home'))
    filename = session['current_image']
    image_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    try:
        image = Image.open(image_path)
        if image.mode != 'RGB':
            image = image.convert('RGB')

        # Brightness
        brightness_val = request.form.get('brightness', type=int)
        if brightness_val is None:
            brightness_val = 100
        session['brightness'] = brightness_val
        brightness_factor = brightness_val / 100.0

        # Resize
        new_w = request.form.get('resize_width', type=int)
        new_h = request.form.get('resize_height', type=int)
        session['resize_width'] = new_w
        session['resize_height'] = new_h

        effect = request.form.get('effect', 'none')
        edited_image = adjust_brightness(np.array(image), brightness_factor)
        edited_array = np.array(edited_image)
        edited_image = resize_image(edited_array, new_size=(new_w, new_h))

        if effect == 'negative':
             edited_image = negative_image(edited_array)
        elif effect == 'solarize':
             edited_image = solarize_image(edited_array)
        elif effect == 'border':
            border_color = request.form.get('border_color', '#000000')
            border_size = request.form.get('border_size', 10, type=int)
            edited_image = add_border(edited_array, border_size, border_color)
        edited_image.save(image_path)
    except Exception as e:
        print(f"Error editing image: {e}")
    return redirect(url_for('edit_image'))

@app.route('/download')
def download_image():
    if 'current_image' not in session:
        return redirect(url_for('home'))
    filename = session['current_image']
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename, as_attachment=True)

@app.route('/reupload')
def reupload():
    session.pop('current_image', None)
    return redirect(url_for('home'))

if __name__ == '__main__':
    app.run(debug=True)