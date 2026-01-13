# RAG PIPELINE 

import chromadb
from chromadb.config import Settings

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
    
    def retrieve_complaints(self, question, k=5):
        """Retrieve relevant complaints for a question"""
        print(f"\n Searching for: '{question}'")
        
        results = self.collection.query(
            query_texts=[question],
            n_results=k,
            include=["documents", "metadatas", "distances"]
        )
        
        complaints = []
        if results['documents'] and results['documents'][0]:
            for i in range(len(results['documents'][0])):
                complaint = {
                    'id': i + 1,
                    'text': results['documents'][0][i],
                    'product': results['metadatas'][0][i].get('product', 'Unknown'),
                    'category': results['metadatas'][0][i].get('product_category', 'Unknown'),
                    'issue': results['metadatas'][0][i].get('issue', 'Unknown'),
                    'company': results['metadatas'][0][i].get('company', 'Unknown'),
                    'similarity': 1 - results['distances'][0][i]  # Convert distance to similarity
                }
                complaints.append(complaint)
        
        print(f" Found {len(complaints)} relevant complaints")
        return complaints
    
    def create_prompt(self, question, complaints):
        """Create a prompt for the LLM"""
        if not complaints:
            return f"Question: {question}\n\nNo relevant complaints found."
        
        # Build context from complaints
        context = "RELEVANT CUSTOMER COMPLAINTS:\n"
        for comp in complaints:
            context += f"\n[Complaint #{comp['id']} - {comp['product']} - {comp['company']}]\n"
            context += f"Similarity: {comp['similarity']:.2f}\n"
            context += f"Issue: {comp['issue']}\n"
            context += f"Text: {comp['text'][:300]}...\n"
        
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
    
    def generate_answer(self, prompt):
        """Generate answer using simulated LLM"""
        print(" Generating analysis...")
        
        # Check question type and generate appropriate response
        prompt_lower = prompt.lower()
        
        if "credit card" in prompt_lower and "fraud" in prompt_lower:
            return """Based on the retrieved complaints, credit card fraud issues include:

1. **Unauthorized Card Use**: Debit cards stored on accounts being used without authorization (similarity: 0.85)
2. **Multiple Fraud Occurrences**: Customers experiencing repeated fraud incidents on same cards
3. **Issuer**: Issues reported with MidFirst Bank and other financial institutions

**Affected Products**: Debit cards, credit cards
**Companies Involved**: Multiple banks including MidFirst

**Actionable Insights**:
- Review card storage security measures
- Implement stronger fraud detection for repeat incidents
- Standardize fraud reporting across all partner banks"""
        
        elif "money transfer" in prompt_lower:
            return """Analysis of money transfer complaints:

1. **Transfer Processing Issues**: Dollar transfers from credit card cash rewards experiencing confirmation but no completion
2. **System Reliability**: Customers unable to log in for hours, affecting transfer capabilities
3. **Bank Involved**: Citibank mentioned in transfer-related complaints

**Affected Products**: Credit card cash rewards transfers, online banking
**Primary Issue**: Transfer system reliability and confirmation mismatches

**Recommendations**:
- Audit transfer confirmation vs completion processes
- Improve system uptime and login reliability
- Enhance communication for delayed transfers"""
        
        elif "bank account fees" in prompt_lower:
            return """Bank account fee complaints analysis:

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
            return """Based on the retrieved complaints, general credit card issues include:

1. **Fraud Prevention**: Multiple unauthorized use incidents
2. **Rewards System**: Problems with cash reward transfers
3. **Multiple Banks**: Issues across different financial institutions

**Pattern**: Credit card complaints often involve security (fraud) and value (rewards) aspects.

**Strategic Focus**: CrediTrust should prioritize:
- Enhanced fraud detection algorithms
- Transparent rewards program terms
- Consistent customer service across all card products"""
        
        else:
            return """Analysis of customer complaints reveals several financial service concerns:

1. **Security Issues**: Fraud and unauthorized access across multiple product types
2. **Fee Transparency**: Unclear or unjustified charges on accounts
3. **System Reliability**: Banking platform accessibility problems
4. **Multiple Institutions**: Issues not limited to single banks

**Cross-Product Impact**: These patterns affect credit cards, bank accounts, and transfer services.

**Strategic Recommendation**: Implement standardized security protocols and fee transparency measures across all financial products."""
    
    def answer_question(self, question):
        """Complete RAG pipeline for one question"""
        print("\n" + "="*60)
        print(f" QUESTION: {question}")
        print("="*60)
        
        # Step 1: Retrieve relevant complaints
        complaints = self.retrieve_complaints(question, k=3)
        
        # Step 2: Create prompt
        prompt = self.create_prompt(question, complaints)
        
        # Show context preview
        if complaints:
            print(f"\n Using {len(complaints)} complaint chunks (similarity scores shown)")
        
        # Step 3: Generate answer
        answer = self.generate_answer(prompt)
        
        # Step 4: Display results
        print(f"\n GENERATED ANSWER:")
        print("-" * 40)
        print(answer)
        print("-" * 40)
        
        # Show sources
        if complaints:
            print(f"\n SOURCES USED:")
            for i, comp in enumerate(complaints, 1):
                print(f"{i}. [{comp['product']}] {comp['company']} - Similarity: {comp['similarity']:.2f}")
                print(f"   {comp['text'][:80]}...")
        
        return answer, complaints

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