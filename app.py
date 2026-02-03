from flask import Flask, render_template, request, send_file
from PIL import Image, ImageDraw, ImageFont
import os
from io import BytesIO
import smtplib
from email.message import EmailMessage

app = Flask(__name__)

# ================= CONFIG =================

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ASSETS_DIR = os.path.join(BASE_DIR, "static", "assets")
OUTPUT_DIR = os.path.join(BASE_DIR, "static", "output")
os.makedirs(OUTPUT_DIR, exist_ok=True)

BACKGROUND_IMAGE = os.path.join(ASSETS_DIR, "background.jpeg")
LOGO_IMAGE = os.path.join(ASSETS_DIR, "download.jpeg")

CARD_WIDTH = 1000
CARD_HEIGHT = 600
HEADER_HEIGHT = 120
GRAY = (80, 80, 80)
PHOTO_BORDER = 6

# Gmail App Password
SENDER_EMAIL = "lisakhanya5962@gmail.com"
SENDER_PASSWORD = "hocuaqytnuggqrku"  # <-- use your Gmail App Password

# ========================================

def send_email(receiver, filename, image_bytes):
    try:
        msg = EmailMessage()
        msg["Subject"] = "Your Staff ID Card"
        msg["From"] = SENDER_EMAIL
        msg["To"] = receiver
        msg.set_content("Hello,\n\nAttached is your Staff ID Card.\n\nFrontier Regional Hospital")

        msg.add_attachment(image_bytes,
                           maintype="image",
                           subtype="png",
                           filename=filename)

        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
            smtp.login(SENDER_EMAIL, SENDER_PASSWORD)
            smtp.send_message(msg)

        print(f"Email successfully sent to {receiver}")
    except Exception as e:
        print("Email sending failed:", e)

# ================== ROUTES ==================

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        name = request.form["name"].upper()
        position = request.form["position"].upper()
        department = request.form["department"].upper()
        email = request.form["email"]
        hospital = "FRONTIER REGIONAL HOSPITAL"
        photo = request.files["photo"]

        # Save uploaded photo temporarily
        temp_photo = os.path.join(OUTPUT_DIR, "temp.png")
        photo.save(temp_photo)

        # Load assets
        background = Image.open(BACKGROUND_IMAGE).resize((CARD_WIDTH, CARD_HEIGHT))
        logo = Image.open(LOGO_IMAGE).resize((150, 80))
        photo_img = Image.open(temp_photo).resize((250, 300))

        card = background.copy()
        draw = ImageDraw.Draw(card)

        # Gray header
        draw.rectangle([(0, 0), (CARD_WIDTH, HEADER_HEIGHT)], fill=GRAY)

        # Paste logo
        logo_y = (HEADER_HEIGHT - logo.height) // 2
        card.paste(logo, (30, logo_y), logo.convert("RGBA"))

        # Fonts for staff
        try:
            font_name = ImageFont.truetype("arialbd.ttf", 50)       # Name bigger & bold
            font_position = ImageFont.truetype("arial.ttf", 32)     # Position
            font_department = ImageFont.truetype("arial.ttf", 28)   # Department
        except:
            font_name = ImageFont.load_default()
            font_position = ImageFont.load_default()
            font_department = ImageFont.load_default()

        # Font for hospital (smaller to fit)
        try:
            font_hospital = ImageFont.truetype("arialbd.ttf", 36)
        except:
            font_hospital = ImageFont.load_default()

        # Center hospital name in header
        bbox = draw.textbbox((0, 0), hospital, font=font_hospital)
        w = bbox[2] - bbox[0]
        h = bbox[3] - bbox[1]
        x = (CARD_WIDTH - w) // 2
        y = (HEADER_HEIGHT - h) // 2
        draw.text((x, y), hospital, fill="white", font=font_hospital)

        # Photo with dark gray border
        photo_x = 50
        photo_y = HEADER_HEIGHT + 30
        draw.rectangle(
            [
                (photo_x - PHOTO_BORDER, photo_y - PHOTO_BORDER),
                (photo_x + photo_img.width + PHOTO_BORDER,
                 photo_y + photo_img.height + PHOTO_BORDER)
            ],
            fill=GRAY
        )
        card.paste(photo_img, (photo_x, photo_y))

        # Text details next to photo
        text_x = 350
        text_y = HEADER_HEIGHT + 80
        draw.text((text_x, text_y), name, fill="white", font=font_name)
        draw.text((text_x, text_y + 70), position, fill="white", font=font_position)
        draw.text((text_x, text_y + 120), department, fill="white", font=font_department)

        # Save file using user's name
        filename = name.replace(" ", "_") + ".png"
        output_path = os.path.join(OUTPUT_DIR, filename)
        card.save(output_path)

        # Save image to memory for email
        img_bytes = BytesIO()
        card.save(img_bytes, format="PNG")
        img_bytes.seek(0)

        # Send email
        if SENDER_PASSWORD:
            send_email(email, filename, img_bytes.read())

        # Render success page
        return render_template("success.html",
                               name=name,
                               filename=filename)

    return render_template("index.html")


# ======= RUN SERVER =======
if __name__ == "__main__":
    app.run(debug=True)
