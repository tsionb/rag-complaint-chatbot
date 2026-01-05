# rag-complaint-chatbot


##  Project Overview

This project is focused on building the foundations of a **Retrieval-Augmented Generation (RAG)** system using consumer complaint data.

##  Dataset Description

* **Source**: Consumer Financial Protection Bureau (CFPB)
* **Size**: Several GB (millions of records)
* **Key Fields Used**:

  * `Consumer complaint narrative`
  * `Product`
  * `Complaint ID`

Due to the large size of the dataset, **chunked processing and sampling** are used throughout the project.

---

##  Task 1: Data Preparation & Exploratory Data Analysis (EDA)

###  Objective

Prepare a clean, focused dataset containing only relevant complaints and narratives, suitable for downstream NLP and RAG tasks.

---

###  Steps Performed

1. **Data Access**

   * Raw data stored externally (e.g., Google Drive)
   * Loaded in chunks to avoid memory issues

2. **Initial Inspection**

   * Checked dataset structure, column names, and sample rows
   * Identified relevant columns for analysis

3. **Filtering**

   * Removed rows with missing complaint narratives
   * Filtered complaints to relevant financial products (e.g., credit cards, loans, money transfers)

4. **Exploratory Data Analysis**

   * Analyzed complaint distribution by product
   * Inspected narrative lengths and data quality
   * Identified imbalance across product categories

5. **Output**

   * A cleaned and filtered CSV file saved for later use:

```text
data/processed/cleaned_complaints.csv
```

---

###  Key Outcome of Task 1

* Reduced dataset size significantly
* Ensured all retained records contain meaningful text
* Produced a clean dataset ready for NLP processing

---

##  Task 2: Text Chunking, Embedding & Vector Storage

###  Objective

Transform complaint narratives into vector embeddings and store them in a vector database to enable semantic search for a RAG system.

---

###  Steps Performed

1. **Load Processed Data**

   * Loaded `filtered_complaints.csv` from Task 1

2. **Text Cleaning**

   * Converted text to lowercase
   * Removed punctuation and special characters
   * Normalized whitespace

3. **Sampling**

   * Limited the number of complaints per product category
   * Prevented memory overload on local machines

4. **Text Chunking**

   * Used `RecursiveCharacterTextSplitter`
   * Chunk size: 500 characters
   * Overlap: 50 characters
   * Ensured long narratives were broken into manageable pieces

5. **Embedding Generation**

   * Used HuggingFace sentence transformer:

     * `sentence-transformers/all-MiniLM-L6-v2`
   * Free, efficient, and suitable for semantic search

6. **Vector Storage**

   * Stored embeddings using **ChromaDB**
   * Added embeddings incrementally in small batches
   * Enabled automatic persistence to disk

7. **Verification**

   * Performed similarity search queries
   * Confirmed relevant complaint text was retrieved

---

###  Output of Task 2

```text
vectorstore/
├── chroma.sqlite3
└── index/
```

This directory contains all vector embeddings and metadata required for retrieval.

---

##  Tools & Libraries Used

* Python
* Pandas
* TQDM
* LangChain
* HuggingFace Sentence Transformers
* ChromaDB
* Jupyter Notebook / VS Code

---

##  Key Engineering Considerations

* Chunked processing to handle large datasets
* Sampling to accommodate limited hardware resources
* Batch embedding to prevent crashes
* Automatic persistence for fault tolerance
