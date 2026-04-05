import qrcode
from io import BytesIO
import base64

class QRCodeService:
    @staticmethod
    def generate_base64(data: str, size: int = 10, border: int = 2) -> str:
        """
        Génère un QR code et le retourne en base64 (format PNG).
        """
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=size,
            border=border,
        )
        qr.add_data(data)
        qr.make(fit=True)

        img = qr.make_image(fill_color="black", back_color="white")
        buffered = BytesIO()
        img.save(buffered, format="PNG")
        img_base64 = base64.b64encode(buffered.getvalue()).decode('utf-8')
        return f"data:image/png;base64,{img_base64}"