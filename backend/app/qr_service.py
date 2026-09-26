import base64
import io

import qrcode


def generate_qr_data_uri(payload_url: str) -> str:
    img = qrcode.make(payload_url)
    buffer = io.BytesIO()
    img.save(buffer, format="PNG")
    encoded = base64.b64encode(buffer.getvalue()).decode("ascii")
    return f"data:image/png;base64,{encoded}"
