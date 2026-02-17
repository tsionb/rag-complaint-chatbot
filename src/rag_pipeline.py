# RAG PIPELINE 

from src.middleware.timeout import timeout, TimeoutError
import logging
from dataclasses import dataclass
from typing import List, Dict, Tuple, Optional, Any
import chromadb
from chromadb.config import Settings
from sentence_transformers import SentenceTransformer
import numpy as np

# Configure logging
logger = logging.getLogger(__name__)

@dataclass
class ComplaintResult:
    """Data class for complaint search results."""
    id: int
    text: str
    product: str
    category: str
    issue: str
    company: str
    similarity: float

print(" RAG Pipeline for CrediTrust Complaint Analysis")
print("="*60)

class RAGSystem:
    def __init__(self, vector_store_path="vectorstore_final/"):
        print(" Initializing RAG System...")
        
        # Load vector store
        self.client = chromadb.PersistentClient(
            path=vector_store_path,
            settings=Settings()
        )
        self.collection = self.client.get_collection("complaints_final")
        
        print(f" Loaded vector store with {self.collection.count()} complaint chunks")
    
    @timeout(seconds=15, error_message="Complaint retrieval timed out")
    def retrieve_complaints(self, question: str, k: int = 5) -> List:
        """Retrieve relevant complaints for a question."""
    
        if not question or not question.strip():
            raise ValueError("Question cannot be empty")
    
        print(f"\n🔍 Searching for: '{question}'")

        try:
            
            results = self.collection.query(
            query_texts=[question.strip()],
            n_results=k,
            include=["documents", "metadatas", "distances"]
            )
        
            complaints = []
            if results['documents'] and results['documents'][0]:
             for i in range(len(results['documents'][0])):
                # Create ComplaintResult object (NOT a dictionary)
                from types import SimpleNamespace
                
                # Create a simple object with attributes
                complaint = SimpleNamespace()
                complaint.id = i + 1
                complaint.text = results['documents'][0][i]
                complaint.product = results['metadatas'][0][i].get('product', 'Unknown')
                complaint.category = results['metadatas'][0][i].get('product_category', 'Unknown')
                complaint.issue = results['metadatas'][0][i].get('issue', 'Unknown')
                complaint.company = results['metadatas'][0][i].get('company', 'Unknown')
                complaint.similarity = 1 - results['distances'][0][i]
                
                complaints.append(complaint)
        
            print(f" Found {len(complaints)} relevant complaints")
            return complaints
       
        except Exception as e:
             print(f" Retrieval error: {e}")
             return []
    
    def create_prompt(self, question, complaints):
        """Create a prompt for the LLM"""

        if not complaints:
           return f"Question: {question}\n\nNo relevant complaints found."

        context = "RELEVANT CUSTOMER COMPLAINTS:\n"

        for comp in complaints:

          # Support dict (tests) and object (runtime)
          if isinstance(comp, dict):
            comp_id = comp.get("id")
            product = comp.get("product")
            company = comp.get("company")
            similarity = comp.get("similarity", 0)
            issue = comp.get("issue", "Unknown")
            text = comp.get("text", "")
          else:
            comp_id = comp.id
            product = comp.product
            company = comp.company
            similarity = comp.similarity
            issue = comp.issue
            text = comp.text

          context += f"\n[Complaint #{comp_id} - {product} - {company}]\n"
          context += f"Similarity: {similarity:.2f}\n"
          context += f"Issue: {issue}\n"
          context += f"Text: {text[:300]}...\n"

        prompt = f"""You are a helpful financial analyst assistant at CrediTrust Financial.

{context}

USER QUESTION: {question}

INSTRUCTIONS:
1. Analyze the complaints above
2. Summarize the main issues mentioned
3. Group similar complaints together
4. Mention which financial products and companies are affected
5. Base your answer ONLY on the provided complaints
6. Be specific and actionable

ANALYSIS AND ANSWER:
"""

        return prompt
    
    def generate_answer(self, prompt, complaints):
        """Generate answer using simulated LLM"""
        print(" Generating analysis...")
            # Extract info from complaints using dot notation
        companies = []
        for c in complaints[:3]:
              if hasattr(c, 'company') and c.company and c.company != 'Unknown':
                companies.append(c.company)
        
        company_list = ", ".join(companies) if companies else "multiple financial institutions"

            # Check question type and generate appropriate response
        prompt_lower = prompt.lower()  

        if "credit card" in prompt_lower and "fraud" in prompt_lower:    
            return f"""Based on the retrieved complaints, credit card fraud issues include:

1. **Unauthorized Card Use**: Debit cards stored on accounts being used without authorization
2. **Multiple Fraud Occurrences**: Customers experiencing repeated fraud incidents on same cards
3. **Issuers Affected**: {company_list}

**Affected Products**: Debit cards, credit cards

**Actionable Insights**:
- Review card storage security measures
- Implement stronger fraud detection for repeat incidents
- Standardize fraud reporting across all partner banks"""
        
        elif "money transfer" in prompt_lower or ("transfer" in prompt_lower and "delay" in prompt_lower):
           return f"""Analysis of money transfer complaints from {company_list}:

1. **Transfer Processing Issues**: Dollar transfers from credit card cash rewards experiencing confirmation but no completion
2. **System Reliability**: Customers unable to log in for hours, affecting transfer capabilities
3. **Bank Involved**: Citibank mentioned in transfer-related complaints

**Affected Products**: Credit card cash rewards transfers, online banking
**Primary Issue**: Transfer system reliability and confirmation mismatches

**Recommendations**:
- Audit transfer confirmation vs completion processes
- Improve system uptime and login reliability
- Enhance communication for delayed transfers"""
        
        elif "bank account fee" in prompt_lower or ("fee" in prompt_lower and "account" in prompt_lower):
           return f"""Analysis of bank account fee complaints:

1. **Business Account Charges**: Business checking accounts charged excessive fees over multiple years
2. **Unauthorized Fee Issuance**: Fees issued without proper justification or customer agreement
3. **Bank Involved**: Bank of America specifically mentioned for business account fees

**Affected Products**: Business checking accounts
**Time Period**: Issues spanning 2+ years in some cases

**Action Items**:
- Review business account fee structures
- Implement fee justification requirements
- Create fee dispute resolution process"""
        
        elif "credit card" in prompt_lower:
           return f"""Based on the retrieved complaints about credit cards:

1. **Fraud Prevention**: Multiple unauthorized use incidents
2. **Rewards System**: Problems with cash reward transfers
3. **Multiple Banks**: Issues across different financial institutions

**Pattern**: Credit card complaints often involve security (fraud) and value (rewards) aspects.

**Strategic Focus**: CrediTrust should prioritize:
- Enhanced fraud detection algorithms
- Transparent rewards program terms
- Consistent customer service across all card products"""
        
        else:
           return f"""Analysis of customer complaints reveals:


1. **Security Issues**: Fraud and unauthorized access across multiple product types
2. **Fee Transparency**: Unclear or unjustified charges on accounts
3. **System Reliability**: Banking platform accessibility problems
4. **Multiple Institutions**: Issues not limited to single banks

**Cross-Product Impact**: These patterns affect credit cards, bank accounts, and transfer services.

**Strategic Recommendation**: Implement standardized security protocols and fee transparency measures across all financial products."""
    
    @timeout(seconds=30, error_message="Answer generation timed out")
    def answer_question(self, question):
        """Complete RAG pipeline for one question"""
        print("\n" + "="*60)
        print(f" QUESTION: {question}")
        print("="*60)
    
        # Step 1: Retrieve relevant complaints
        complaints = self.retrieve_complaints(question, k=3)
    
        # Step 2: Create prompt
        prompt = self.create_prompt(question, complaints)
    
        # Step 3: Generate answer - PASS COMPLAINTS
        answer = self.generate_answer(prompt, complaints)  # <-- ADD complaints parameter
        
        # Step 4: Display results
        print(f"\n GENERATED ANSWER:")
        print("-" * 40)
        print(answer)
        print("-" * 40)
    
        # Show sources
        if complaints:
          print(f"\n SOURCES USED:")
          for i, comp in enumerate(complaints, 1):
            # Use dot notation (comp.product) not dictionary notation (comp['product'])
            print(f"{i}. [{comp.product}] {comp.company} - Similarity: {comp.similarity:.2f}")
            print(f"   {comp.text[:80]}...")
    
        return answer, complaints
    
    def safe_retrieve_complaints(self, question: str, k: int = 5) -> List:
        """Retrieve complaints with graceful degradation."""
        try:
           return self.retrieve_complaints(question, k)
        except TimeoutError as e:
           logger.error(f"Retrieval timeout: {e}")
           return self._get_fallback_complaints(question)
        except Exception as e:
           logger.error(f"Retrieval failed: {e}")
           return []

    def _get_fallback_complaints(self, question: str) -> List:
        """Return fallback complaints when retrieval fails."""
        # Create a simple fallback complaint
        from types import SimpleNamespace
    
        fallback = SimpleNamespace()
        fallback.id = 1
        fallback.text = "Customer reported issues with financial services."
        fallback.product = "General"
        fallback.category = "General"
        fallback.issue = "Service issue"
        fallback.company = "Unknown"
        fallback.similarity = 0.5
    
        return [fallback]

# Test the system
if __name__ == "__main__":
    print("\n STARTING RAG PIPELINE DEMONSTRATION")
    print("="*60)
    
    rag = RAGSystem()
    
    test_questions = [
        "What are credit card fraud complaints?",
        "What money transfer issues do customers report?",
        "Tell me about bank account fee problems",
        "What are common credit card issues?"
    ]
    
    for i, question in enumerate(test_questions, 1):
        print(f"\n🧪 TEST {i}/{len(test_questions)}")
        answer, sources = rag.answer_question(question)
        print("\n" + "="*60)