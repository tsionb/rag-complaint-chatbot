# TEST THE RAG SYSTEM

from src.rag_pipeline import ask_question

print(" STARTING RAG CHATBOT TEST")
print("="*50)

# Test with these simple questions
test_questions = [
    "What are problems with credit cards?",
    "Why are people complaining about money transfers?",
    "Tell me about billing issues",
    "What fees are customers unhappy about?",
    "Are there complaints about savings accounts?"
]

all_results = []

# Test each question
for i, question in enumerate(test_questions, 1):
    print(f"\n📝 TEST #{i}")
    
    answer, sources = ask_question(question)
    
    # Save results for evaluation
    all_results.append({
        'question': question,
        'answer': answer,
        'sources': len(sources)
    })
    
    # Pause between questions (optional)
    if i < len(test_questions):
        input("\nPress Enter to test next question...")

# Summary
print("\n" + "="*50)
print(" TEST SUMMARY")
print("="*50)
for result in all_results:
    print(f"\nQ: {result['question']}")
    print(f"A: {result['answer'][:100]}...")
    print(f"Sources: {result['sources']} complaints")