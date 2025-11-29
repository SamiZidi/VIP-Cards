import qrcode
import os
import dotenv
dotenv.load_dotenv()

# create output folder if not exists
output_folder = "qr_codes"
os.makedirs(output_folder, exist_ok=True)

base_url = os.getenv("QR_BASE_URL", "https://vip.masmoudiweddingplanner.com/")

# توليد 100 QR code
for i in range(1, 1001):
    user_id = f"USER{i}"  # USER1, USER2 ...
    full_url = f"{base_url}AbX9TqVrKmN{user_id}4FjHsW2GyUeRc"
    
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=8,
        border=3,
    )
    qr.add_data(full_url)
    qr.make(fit=True)

    # create white QR code on transparent background
    img = qr.make_image(fill_color="white", back_color="transparent")
    img.save(os.path.join(output_folder, f"{user_id}.png"))


