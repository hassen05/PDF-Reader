import os
import json
import logging
from datetime import datetime
import streamlit as st
import PyPDF2
from openai import OpenAI

class PDFChatApp:
    def __init__(self, chat_history_file="chat_history.json"):
        """Initialize the PDF Chat Application."""
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
        self.chat_history_file = chat_history_file

        # Initialize OpenAI client
        self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

        # Load existing chat history
        self.chat_history = self.load_chat_history()

    def load_chat_history(self):
        """Load chat history from JSON file."""
        try:
            if os.path.exists(self.chat_history_file):
                with open(self.chat_history_file, "r") as file:
                    return json.load(file)
        except Exception as e:
            self.logger.error(f"Error loading chat history: {e}")
        return {}

    def save_chat_history(self):
        """Save current chat history to JSON file."""
        try:
            with open(self.chat_history_file, "w") as file:
                json.dump(self.chat_history, file, indent=4)
        except Exception as e:
            self.logger.error(f"Error saving chat history: {e}")

    def extract_pdf_text(self, uploaded_file):
        """Extract text from uploaded PDF file."""
        try:
            pdf_reader = PyPDF2.PdfReader(uploaded_file)
            return " ".join(page.extract_text() or "" for page in pdf_reader.pages)
        except Exception as e:
            st.error(f"PDF extraction error: {e}")
            return None

    def generate_pdf_response(self, context, question):
        """Generate AI response for PDF content."""
        try:
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a helpful assistant answering questions based on PDF content."},
                    {"role": "user", "content": f"Context: {context[:4000]}\n\nQuestion: {question}"}
                ]
            )
            return response.choices[0].message.content
        except Exception as e:
            return f"Response generation error: {e}"

    def generate_chat_title(self, question):
        """Generate a title for the chat session."""
        try:
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "Create a concise and descriptive title for this input."},
                    {"role": "user", "content": question}
                ]
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            self.logger.error(f"Error generating chat title: {e}")
            return "Untitled Chat"

    def render_sidebar(self):
        """Render sidebar for session management."""
        st.sidebar.title("Chat Sessions")

        # Ensure selected_session exists in session state
        if 'selected_session' not in st.session_state:
            st.session_state.selected_session = "New Chat"

        # Prepare session names
        session_names = list(self.chat_history.keys())
        session_names.insert(0, "New Chat")

        # Select session
        selected_session = st.sidebar.selectbox(
            "Select a session",
            options=session_names,
            index=session_names.index(st.session_state.selected_session)
        )
        st.session_state.selected_session = selected_session

        # Handle session deletion
        if selected_session != "New Chat" and st.sidebar.button("Delete Chat"):
            del self.chat_history[selected_session]
            self.save_chat_history()
            st.session_state.selected_session = "New Chat"
            st.rerun()

        return selected_session

    def create_new_session(self):
        """Create a new chat session."""
        session_id = f"session_{len(self.chat_history) + 1}_{datetime.now().strftime('%Y%m%d%H%M%S')}"
        self.chat_history[session_id] = {
            "title": None,
            "pdf_content": None,
            "history": []
        }
        self.save_chat_history()
        return session_id

    def run(self):
        """Main application runner."""
        st.title("PDF Chat Assistant")

        # Sidebar session management
        selected_session = self.render_sidebar()

        # Determine current session
        if selected_session == "New Chat":
            st.sidebar.info("Click 'Start New Chat' to begin a session.")
            if st.sidebar.button("Start New Chat"):
                session_id = self.create_new_session()
                st.session_state.selected_session = session_id
                st.rerun()
            return

        session_id = selected_session
        session_data = self.chat_history.get(session_id, {
            "title": None,
            "pdf_content": None,
            "history": []
        })

        # Display current session title
        st.sidebar.markdown(f"**Current Chat:** {session_data['title'] or 'New Chat'}")

        # PDF upload
        uploaded_file = st.file_uploader("Upload a PDF file", type=["pdf"])
        if uploaded_file:
            session_data["pdf_content"] = self.extract_pdf_text(uploaded_file)
            if session_data["pdf_content"]:
                st.success("PDF uploaded and text extracted successfully!")
                self.chat_history[session_id] = session_data
                self.save_chat_history()

        # Question input and processing
        question = st.text_input("Ask a question about the PDF:")
        if st.button("Ask"):
            if question and session_data.get("pdf_content"):
                answer = self.generate_pdf_response(session_data["pdf_content"], question)

                # Update session history
                session_data["history"].append({"question": question, "answer": answer})
                if not session_data["title"]:
                    session_data["title"] = self.generate_chat_title(question)

                # Save updated session
                self.chat_history[session_id] = session_data
                self.save_chat_history()

                # Display Q&A
                st.write(f"**Q:** {question}")
                st.write(f"**A:** {answer}")

        # Display chat history
        if session_data["history"]:
            st.write(f"**Chat History ({session_data['title'] or 'New Chat'})**")
            for chat in session_data["history"]:
                st.write(f"**Q:** {chat['question']}")
                st.write(f"**A:** {chat['answer']}")

def main():
    """Run the Streamlit app."""
    app = PDFChatApp()
    app.run()

if __name__ == "__main__":
    main()