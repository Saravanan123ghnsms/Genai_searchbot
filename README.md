# Intelligent Bot Website with Azure Cognitive Search  

This project is an intelligent bot website designed to retrieve content from **PDF files** and **documents stored in SharePoint** using **Azure Cognitive Search with Vector Search**. The bot leverages **GPT models** to generate user-friendly responses based on the retrieved data, providing an enhanced semantic search experience.  

## Features  

- **Semantic Search**: Utilizes **vector search** in Azure Cognitive Search to fetch highly relevant content.  
- **PDF and SharePoint Integration**: Retrieves content directly from PDF documents and SharePoint repositories.  
- **Dynamic Query Handling**: Users can input queries and specify categories for targeted results.  
- **GPT Model Response Generation**: Provides meaningful and conversational answers based on retrieved data.  

## Technical Implementation  

1. **Azure Cognitive Search Setup**:
   - Created **Data Source** to connect to PDFs and SharePoint docs.  
   - Built an **Index** to store and structure the searchable content.  
   - Configured an **Indexer** to automatically extract and populate data into the index.  
   - Designed a **Skillset** to preprocess and enrich the content for semantic search.  

2. **Postman for Automation**:
   - Used **Postman** to automate the creation of Data Source, Index, Indexer, and Skillset via API calls.  

3. **Vector Search**:
   - Implemented **Azure Cognitive Search Vector Search** to enable retrieval of content based on embeddings for semantic relevance.  

4. **GPT Model Integration**:
   - Integrated a GPT model to interpret user queries and generate human-like responses based on the search results.  

## How It Works  

1. **User Query**:
   - The user inputs a query and selects a category.  
2. **Content Retrieval**:
   - The system performs a vector search over the indexed content to fetch relevant results from PDFs and SharePoint.  
3. **Response Generation**:
   - The GPT model uses the retrieved results to generate a conversational and informative response.  

## Tools and Technologies  

- **Azure Cognitive Search**: For vector search and content retrieval.  
- **Azure Cognitive Services**: For preprocessing and enrichment using Skillsets.  
- **Postman**: To automate API requests for creating Data Sources, Indexes, Indexers, and Skillsets.  
- **GPT Model**: For generating human-like responses.  
- **SharePoint**: As a content repository.  
- **PDF Documents**: Additional source of searchable content.  

## Setup Instructions  

### Prerequisites  
- Azure Cognitive Search instance.  
- Postman installed.  
- GPT API key for integration.  

### Steps  

1. **Clone the Repository**:  
   ```bash  
   git clone https://github.com/Saravanan123ghnsms/Genai_searchbot.git  
   cd  Genai_searchbot
