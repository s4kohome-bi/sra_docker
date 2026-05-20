import io
import os
import json
from PIL import Image

from services.ai_service import ai_read_invoice
from services.db_service import save_receipt, find_duplicate

import google.generativeai as genai
# =====================================================
# 環境變數 (請確保 Render 已設定)
# =====================================================
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")

genai.configure(api_key=GEMINI_API_KEY)
# 模型名稱回歸最穩定的字串
model = genai.GenerativeModel("gemini-2.5-flash")

from services.db_service import F_STORE, F_INVOICE, F_DATE, F_AMOUNT, F_SOURCE, F_UPLOADER
from unittest.mock import MagicMock
def getfakeresult():
    # 建立模擬物件
    mock_response = MagicMock()
    mock_response.candidates = [MagicMock()]
    mock_response.candidates[0].content.parts = [MagicMock(text="這是模擬的回傳內容。")]
    # 將 Python 字典轉換為標準 JSON 字串
    mock_response.text = json.dumps({
        F_STORE: "義美",
        F_INVOICE: "ZJ-40277996",
        F_DATE: "115-05-15",
        F_AMOUNT: 137
    }, ensure_ascii=False)   

    return mock_response

def preprocessImage(img):
    w, h = img.size
    if w >1600:
        max_size = (1280, 1280)
        img.thumbnail(max_size, Image.LANCZOS)
    #else keep original
        
def process_result(result, source, user_id):
    data = json.loads(result.text)
    data[F_UPLOADER] = str(user_id)
    data[F_SOURCE] = source       
    
    if F_INVOICE not in data or len(data[F_INVOICE]) < 10:
        data["status"] = "parse fail"
        data["message"] = "無法辨識發票號碼"
        return data
    elif find_duplicate(data[F_INVOICE]):
        data["status"] = "duplicate"
        data["message"] = data[F_INVOICE]
    else:
        print(data) # for debug
        save_receipt(data)
        data["status"] = "success"
    
    return data

def process_receipt_file(image_path, source, user_id):
    image = Image.open(image_path)
    # 這裡加入裁切優化，但回傳 Image 物件給 model
    preprocessImage(image)
    #測試用 result = getfakeresult()
    try:
        result = ai_read_invoice(image, model)
        #測試用 result = getfakeresult()
        return process_result(result, source, user_id)
    except Exception as e:
        return {
            F_UPLOADER: user_id,
            F_SOURCE: source,
            "status": "parse fail", 
            "message": str(e)
        }    

def process_receipt_bytes(image_bytes, source, user_id):
    img = Image.open(io.BytesIO(image_bytes))
    preprocessImage(img)
    try:
        result = ai_read_invoice(img, model)
        return process_result(result, source, user_id)
    except Exception as e:
        return {
            F_UPLOADER: user_id,
            F_SOURCE: source,        
            "status": "parse fail", 
            "message": str(e)
        }  

    
    

