from flask import Flask, render_template, request, flash, redirect, url_for, send_from_directory
from flask_mail import Mail, Message
import os
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY')

# ---------------- Flask-Mail Configuration ----------------
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USERNAME'] = os.getenv('EMAIL_USER')
app.config['MAIL_PASSWORD'] = os.getenv('EMAIL_PASS')
app.config['MAIL_USE_TLS'] = False
app.config['MAIL_USE_SSL'] = True

mail = Mail(app)

# ---------------- Routes ----------------

@app.route('/')
def index():
    return render_template('index.html')

# Contact form route
@app.route('/contact', methods=['POST'])
def contact():
    name = request.form.get('name')
    email = request.form.get('email')
    message = request.form.get('message')

    if not name or not email or not message:
        flash("All fields are required.", "error")
        return redirect(url_for('index'))

    msg = Message(
        subject=f"New message from {name}",
        sender=email,
        recipients=[os.getenv('EMAIL_USER')]
    )
    msg.body = f"Name: {name}\nEmail: {email}\n\nMessage:\n{message}"

    try:
        mail.send(msg)
        flash("Message sent successfully! ✅", "success")
    except Exception as e:
        flash(f"Error sending message: {e}", "error")

    return redirect(url_for('index'))

# Download CV route
@app.route('/download-cv')
def download_cv():
    return send_from_directory(
        directory=os.path.join(app.root_path, 'static', 'files'),
        path='Lisakhanya_CV.pdf',
        as_attachment=True
    )

# Download CCNA certificate route
@app.route('/download-ccna')
def download_ccna():
    return send_from_directory(
        directory=os.path.join(app.root_path, 'static', 'files'),
        path='CCNA_Certificate.pdf',
        as_attachment=True
    )

# ---------------- Run App ----------------
if __name__ == '__main__':
    app.run(debug=True)
