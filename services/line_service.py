import os

from linebot.v3 import WebhookHandler

from linebot.v3.messaging import (
    Configuration,
    ApiClient,
    MessagingApi,
    MessagingApiBlob,
    ReplyMessageRequest,
    TextMessage
)
from linebot.v3.webhooks import MessageEvent, ImageMessageContent, TextMessageContent
from linebot.v3.exceptions import InvalidSignatureError

from services.receipt_workflow import process_receipt_bytes

# =====================================================
# 環境變數 (請確保 Render 已設定)
# =====================================================
LINE_CHANNEL_SECRET = os.environ.get("LINE_CHANNEL_SECRET", "0000")
LINE_CHANNEL_ACCESS_TOKEN = os.environ.get("LINE_CHANNEL_ACCESS_TOKEN", "0000")

configuration = Configuration( access_token=LINE_CHANNEL_ACCESS_TOKEN)

handler = WebhookHandler(LINE_CHANNEL_SECRET)

def line_webhook(body, signature):
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        return False
    return True

def reply_text(reply_token, text):

    with ApiClient(configuration) as api_client:

        line_bot_api = MessagingApi(api_client)

        line_bot_api.reply_message_with_http_info(
            ReplyMessageRequest(
                reply_token=reply_token,
                messages=[
                    TextMessage(text=text)
                ]
            )
        )


@handler.add( MessageEvent, message=TextMessageContent)
def handle_text(event):

    reply_text(
        event.reply_token,
        f"收到訊息：{event.message.text}"
    )

@handler.add(MessageEvent, message=ImageMessageContent)
def handle_image(event):
    # 1. 預設回覆訊息（確保在邏輯崩潰時仍有初始內容）
    reply = "系統處理中，請稍候..."
    try:        
        # 【第一層 Try】：負責所有的業務邏輯（下載、AI、對獎）       
        # --- A. 下載圖片 ---
        with ApiClient(configuration) as api_client:
            blob_api = MessagingApiBlob(api_client)
            content = blob_api.get_message_content(event.message.id)
            if hasattr(content, "read"):
                image_bytes = content.read()
            else:
                image_bytes = bytes(content)

            # --- B. AI 辨識 ---
            result = process_receipt_bytes(image_bytes, "Line", event.source.user_id)
            reply = f"辨識內容: {result}"
    except Exception as e:
        # 如果上述邏輯任何地方出錯，捕捉並回傳錯誤訊息
        print(f"邏輯層錯誤: {str(e)}")
        reply = f"辨識失敗: {str(e)}"

    # 【第二層 Try】：專門負責「回覆訊息」
    # 放在最後面，確保無論成功或進到 except，最後都會執行發送
    try:        
        with ApiClient(configuration) as api_client:
            api = MessagingApi(api_client)
            api.reply_message(ReplyMessageRequest(
                reply_token=event.reply_token,
                messages=[TextMessage(text=reply)]
            ))
    except Exception as reply_error:
        # 如果連發送都失敗（通常是 Token 過期或網路斷線），則記錄到後台 Log
        print(f"發送回覆失敗: {reply_error}")
