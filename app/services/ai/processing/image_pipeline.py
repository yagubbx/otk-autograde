# app/services/processing/image_pipeline.py
import base64

class ImagePipeline:
    @staticmethod
    def encode_image_to_base64(image_bytes: bytes) -> str:
        """
        Gələn şəkil baytlarını (bytes) AI-ın oxuya biləcəyi Base64 stringinə çevirir.
        """
        return base64.b64encode(image_bytes).decode('utf-8')