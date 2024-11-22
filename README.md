PDF Reader
This project provides a web application to upload PDFs and interact with them via a chatbot interface.

Features
Upload PDF files for analysis.
Chat interface to ask questions based on the PDF content.
Built using FastAPI for backend and Streamlit for the frontend.
Installation
Clone the repository:

bash
Copy code
git clone https://github.com/hassen05/PDF-Reader.git
Install dependencies:

bash
Copy code
pip install -r requirements.txt
Run the backend:

bash
Copy code
uvicorn backend:app --reload
Run the frontend:

bash
Copy code
streamlit run AskSQL.py
Usage
Upload a PDF via the interface.
Ask questions about the PDF content in the chat.
This version covers the essentials while keeping it concise.