#  RAG CHATBOT UI with History

import gradio as gr
import time
from src.rag_pipeline import RAGSystem

print(" Loading Enhanced RAG Chatbot...")

# Initialize RAG system
rag = RAGSystem()

# Store chat history
chat_history = []

def respond(message, history):
    print(f" User: {message}")

    # Add user message
    history = history + [{"role": "user", "content": message}]

    # Show thinking message
    yield history + [{"role": "assistant", "content": " Thinking..."}]

    time.sleep(0.5)

    # Get RAG answer
    answer, sources = rag.answer_question(message)

    # Format response
    response = f"**Analysis:**\n{answer}\n\n"

    if sources:
        response += "** Supporting Complaints:**\n"
        for i, src in enumerate(sources, 1):
            response += f"\n**{i}. {src['product']}**"
            if src.get("company", "Unknown") != "Unknown":
                response += f" ({src['company']})"
            response += f"\nRelevance: {src['similarity']:.2f}\n"
            response += f"_{src['text'][:80]}..._\n"

    # Add assistant response
    history = history + [{"role": "assistant", "content": response}]

    yield history

# Create the chat interface
print(" Creating chat interface...")

with gr.Blocks(title="CrediTrust Complaint Analyst") as demo:
    gr.Markdown("#  CrediTrust Financial Complaint Analysis")
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
                    "Compare complaints between credit cards and savings accounts"
                ],
                inputs=gr.Textbox(visible=False),  # Not needed for new API
                label="Try these questions:"
            )
            
            gr.Markdown("###  About This Tool")
            gr.Markdown("""
            This chatbot analyzes **1,000+ customer complaints** across:
            - Credit Cards
            - Savings Accounts  
            - Money Transfers
            - Personal Loans
            
            **How it works:**
            1. Searches similar complaints
            2. Analyzes patterns
            3. Provides actionable insights
            """)
        
        with gr.Column(scale=2):
            chatbot = gr.Chatbot(
                label="Complaint Analysis Chat",
                height=500,
                
            )
            
            with gr.Row():
                msg = gr.Textbox(
                    label="Your Question",
                    placeholder="Type your question about customer complaints...",
                    scale=4
                )
                submit = gr.Button("Ask", variant="primary", scale=1)
            
            with gr.Row():
                clear = gr.Button("Clear Chat")
                export = gr.Button("Export Analysis")
    
    # Connect actions
    submit.click(respond, [msg, chatbot], [chatbot])
    msg.submit(respond, [msg, chatbot], [chatbot])
    
    clear.click(lambda: None, None, chatbot, queue=False)
    
    def export_chat():
        if chat_history:
            content = "# CrediTrust Complaint Analysis Report\n\n"
            for i, (q, a) in enumerate(chat_history, 1):
                content += f"## Q{i}: {q}\n\n{a}\n\n---\n\n"
            return content
        return "No chat history to export"
    
    export.click(export_chat, None, gr.Textbox(label="Exported Report"))

print(" Interface ready!")

if __name__ == "__main__":
    demo.launch(
        server_name="0.0.0.0",
        server_port=7860,
        share=False  # Set to True to get a public link
        
    )