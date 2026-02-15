"""Production-ready Gradio UI for RAG Complaint Chatbot."""

import gradio as gr
import logging
from pathlib import Path

from src.rag_pipeline import RAGSystem
from src.config import APIConfig
from src.utils.validation import validate_question
from src.session import SessionManager
from src.middleware.rate_limiter import RateLimiter

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('rag_chatbot.log')
    ]
)
logger = logging.getLogger(__name__)

print(" Loading Production RAG Chatbot...")

# Initialize components
try:
    rag = RAGSystem()
    session_manager = SessionManager()
    rate_limiter = RateLimiter(max_requests=30, window_seconds=60)
    logger.info("All components initialized successfully")
except Exception as e:
    logger.critical(f"Failed to initialize application: {e}")
    raise

def respond(message: str, history: list, session_id: str = None) -> list:
    """Process user message with production hardening."""
    
    # Rate limiting
    client_id = session_id or "anonymous"
    if not rate_limiter.is_allowed(client_id):
        error_msg = " Rate limit exceeded. Please wait a moment."
        return history + [{"role": "assistant", "content": error_msg}]
    
    try:
        # Validate input
        message = validate_question(message)
        logger.info(f"Processing question: {message[:50]}...")
        
        # Get or create session
        session = session_manager.get_or_create_session(session_id)
        
        # Add user message
        history = history + [{"role": "user", "content": message}]
        
        # Show thinking message
        yield history + [{"role": "assistant", "content": "🤔 Thinking..."}]
        
        # Get RAG answer
        answer, sources = rag.answer_question(message)
        
        # Format response
        response = f"##  Analysis\n{answer}\n\n"
        
        if sources:
            response += "##  Supporting Complaints\n"
            for i, src in enumerate(sources, 1):
                response += f"**{i}. {src.product}**"
                if src.company != "Unknown":
                    response += f" ({src.company})"
                response += f"\n*Relevance: {src.similarity:.2f}*\n"
                response += f"_{src.text[:100]}..._\n\n"
        
        # Store in session
        session.add_message(message, response)
        
        # Add assistant response
        history = history + [{"role": "assistant", "content": response}]
        yield history
        
    except ValueError as e:
        logger.warning(f"Invalid input: {e}")
        error_msg = f"⚠️ {e}"
        yield history + [{"role": "assistant", "content": error_msg}]
    except Exception as e:
        logger.exception(f"Error processing question: {e}")
        error_msg = "❌ An error occurred. Our team has been notified."
        yield history + [{"role": "assistant", "content": error_msg}]

def clear_chat() -> list:
    """Clear chat history."""
    return []

def export_chat(history: list) -> str:
    """Export chat history as markdown."""
    if not history:
        return "No chat history to export"
    
    content = "# CrediTrust Complaint Analysis Report\n\n"
    for i, msg in enumerate(history, 1):
        if msg["role"] == "user":
            content += f"## Q{i}: {msg['content']}\n\n"
        elif msg["role"] == "assistant" and "Thinking" not in msg["content"]:
            content += f"### Answer:\n{msg['content']}\n\n---\n\n"
    
    return content

# Create the chat interface
print("🖥️ Creating production chat interface...")

with gr.Blocks(title="CrediTrust Complaint Analyst", theme=gr.themes.Soft()) as demo:
    gr.Markdown("# 🏦 CrediTrust Financial Complaint Analysis")
    gr.Markdown("Ask questions about customer complaints. I'll analyze thousands of complaints to give you insights.")
    
    with gr.Row():
        with gr.Column(scale=1):
            gr.Markdown("### 💡 Example Questions")
            gr.Examples(
                examples=[
                    "What are the most common credit card complaints?",
                    "Tell me about money transfer delays",
                    "What fee issues do customers report?",
                    "Are there fraud-related complaints?",
                ],
                inputs=gr.Textbox(visible=False),
            )
            
            gr.Markdown("### ℹ️ About This Tool")
            gr.Markdown("""
            This production-ready chatbot analyzes **customer complaints** across:
            - Credit Cards
            - Savings Accounts  
            - Money Transfers
            - Personal Loans
            
            **Features:**
            -  Rate limiting (30 queries/minute)
            -  Session management
            -  Input validation
            -  Comprehensive logging
            -  Export functionality
            """)
        
        with gr.Column(scale=2):
            chatbot = gr.Chatbot(
                label="Complaint Analysis Chat",
                height=500,
                type="messages"
            )
            
            with gr.Row():
                msg = gr.Textbox(
                    label="Your Question",
                    placeholder="Type your question about customer complaints...",
                    scale=4
                )
                submit = gr.Button(" Ask", variant="primary", scale=1)
            
            with gr.Row():
                clear = gr.Button(" Clear Chat", variant="secondary")
                export = gr.Button(" Export Analysis", variant="secondary")
            
            # Hidden session ID
            session_id = gr.State(value=None)
    
    # Connect actions
    submit.click(respond, [msg, chatbot, session_id], [chatbot])
    msg.submit(respond, [msg, chatbot, session_id], [chatbot])
    clear.click(clear_chat, None, [chatbot])
    export.click(export_chat, [chatbot], gr.Textbox(label="Exported Report", lines=10))

print(" Production interface ready!")

if __name__ == "__main__":
    config = APIConfig.from_env()
    demo.launch(
        server_name=config.host,
        server_port=config.port,
        share=False,
        debug=config.debug
    )