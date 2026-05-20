# sra_docker
smart receipt assistant - docker version

# smart-receipt-assistant
An AI-powered receipt assistant that extracts receipt data using OCR and organizes information automatically through AI workflows.
All results will be stored in SQLite database, it can be query and used in reports or dashboard.

this project includes 3 entry types:
1. web service
2. line webhook
3. api route (can be used in n8n)

Features：
- Receipt OCR recognition
- AI-powered data extraction
- SQLite storage
- LINE Bot integration
- duplicate 
- Expense record management

Tech Stack：
- Python
- Flask
- Gemini API
- SQLite
- HTML/CSS/Javascript

User uploads receipt image
→ OCR extracts text
→ AI organizes receipt data
→ Save to SQLite
→ LINE Bot replies with summary
