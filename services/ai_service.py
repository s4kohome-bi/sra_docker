from PIL import Image
from services.db_service import F_STORE, F_INVOICE, F_DATE, F_AMOUNT

# =====================================================
# AI 辨識 
# =====================================================
def ai_read_invoice(image, model):
    prompt = f"""
        Extract receipt information and return ONLY valid JSON.

        Example:

        {{
          "{F_STORE}": "",
          "{F_INVOICE}": "",
          "{F_DATE}": "",
          "{F_AMOUNT}": ""
        }}

        Do not include markdown.
        Do not include explanation.
        """

    response = model.generate_content([prompt, image])
    #reponse.text is JSON format
    return response


