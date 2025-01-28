import os
import json
import logging
import azure.functions as func
from openai import AzureOpenAI  
from azure.search.documents import SearchClient
from azure.core.credentials import AzureKeyCredential
from azure.search.documents.models import VectorizedQuery
from azure.search.documents.models import VectorFilterMode
import numpy as np

# Initialize the Azure OpenAI client
def initialize_openai_client():
    endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
    api_key = os.getenv("AZURE_OPENAI_API_KEY")
    api_version = os.getenv("AZURE_OPENAI_API_VERSION")

    if not endpoint or not api_key or not api_version:
        raise ValueError("One or more environment variables are missing or invalid.")

    embedding_client = AzureOpenAI(azure_endpoint=endpoint, api_key=api_key, api_version=api_version)
    return embedding_client

# Initialize Azure Cognitive Search client
def initialize_search_client():
    endpoint = os.getenv("AZURE_SEARCH_ENDPOINT")
    api_key = os.getenv("AZURE_SEARCH_KEY")
    index_name = os.getenv("AZURE_SEARCH_INDEX_NAME")

    if not endpoint or not api_key:
        raise ValueError("One or more environment variables for Azure Search are missing or invalid.")

    search_client = SearchClient(endpoint=endpoint, index_name=index_name, credential=AzureKeyCredential(api_key))
    return search_client

# Generate embeddings for the query using Azure OpenAI's embedding model
def generate_embedding(embedding_client, text):
    emb = embedding_client.embeddings.create(model="text-embedding-3-small", input=text)
    res = json.loads(emb.model_dump_json())
    logging.info(np.array(res["data"][0]["embedding"]))  
    return np.array(res["data"][0]["embedding"])  

# Perform vector similarity search in the Azure Cognitive Search index using KNN
def perform_vector_search(search_client, query_vector, index_name, department=None):
  
    vector_query = VectorizedQuery(vector=query_vector.tolist(), k_nearest_neighbors=50, fields="vector")

   
    search_filter = None
    if department:
        results = search_client.search(
        search_text=None,  
        vector_queries=[vector_query],
        vector_filter_mode=VectorFilterMode.PRE_FILTER,
        filter=f"department eq '{department}'",
        top=10  
    )
    else:
        results = search_client.search(
        search_text=None, 
        vector_queries=[vector_query],
        top=10
    )
    logging.info(f"Search filter applied: {search_filter}")

    return results

# Check if the content is relevant to the query
def is_content_relevant(content, query, embedding_client):
   
    content_embedding = generate_embedding(embedding_client, content)
    query_embedding = generate_embedding(embedding_client, query)
    
   
    similarity = np.dot(content_embedding, query_embedding) / (np.linalg.norm(content_embedding) * np.linalg.norm(query_embedding))
    

    similarity_threshold = 0.2
    logging.info(f"Cosine similarity: {similarity}")
    return similarity >= similarity_threshold


def create_system_message(content_chunks):
    total_length = 0
    MAX_TOTAL_LENGTH = 1500  
    truncated_chunks = []

    for chunk in content_chunks:
        if total_length + len(chunk) > MAX_TOTAL_LENGTH:
            truncated_chunks.append(chunk[:MAX_TOTAL_LENGTH - total_length])
            break
        truncated_chunks.append(chunk)
        total_length += len(chunk)

        system_message = (

        "You are an AI assistant that is tasked with providing responses based solely on the content you are given from an indexed knowledge base. Your response should only use the information available in the content chunks provided, which are the results retrieved from a document search index. You must not include any information that is not contained in the provided content. If the content does not sufficiently address the user's query, you should explicitly state that there is no relevant content available in the index.Additionally, for any small talk or greetings such as 'good morning,' 'good night,' 'hi,' 'hello,' etc., your response should strictly say: 'No relevant content found.'Do not generate or infer any information that is not directly included in the content provided. The content provided to you is the only basis for your response, and you should not reference any knowledge outside of these provided content chunks. Your response should be strictly grounded in the indexed documents only. If the query is unrelated to or not addressed by the indexed content, your response should strictly say: 'No relevant content found.'"
    )


    content_message = "\n".join(truncated_chunks)
    return f"{system_message}\n\nContent:\n{content_message}"


def generate_gpt_response(embedding_client, content_chunks, query):
   
    system_message = create_system_message(content_chunks)


    message_text = [{"role": "system", "content": system_message}, {"role": "user", "content": query}]
        
   
    try:
        response = embedding_client.chat.completions.create(
            model="gpt-35-turbo-16k",  
            messages=message_text,
            max_tokens=200,  
            temperature=0.3  
        )

    
        gpt_response = response.choices[0].message.content 
        
        
        if "No relevant content found" in gpt_response:
            return "No relevant content found."
        
        return gpt_response
    except Exception as e:
        logging.error(f"Error generating GPT response: {str(e)}")
        return "No relevant content found."


def main(req: func.HttpRequest) -> func.HttpResponse:
    try:
        
        if req.method != "GET":
            return func.HttpResponse(
                json.dumps({"response": None, "error": "Method Not Allowed"}),
                status_code=405,
                mimetype="application/json"
            )

    
        query = req.params.get("query")
        department = req.params.get("department")  
        index_name = os.getenv("AZURE_SEARCH_INDEX_NAME")  

  
        if not query or not index_name:
            return func.HttpResponse(
                json.dumps({"response": None, "error": "Missing required query parameters: 'query' and 'index_name'"}),
                status_code=400,
                mimetype="application/json"
            )

        embedding_client = initialize_openai_client()
        search_client = initialize_search_client()


        query_vector = generate_embedding(embedding_client, query)

       
        search_results = perform_vector_search(search_client, query_vector, index_name, department)

        if not search_results:
            return func.HttpResponse(
                json.dumps({"response": "No relevant content found.", "error": None}),
                status_code=200,
                
                mimetype="application/json",
                headers={"Access-Control-Allow-Origin": "*"}
            )

      
        results = []
        MAX_CONTENT_LENGTH = 800  

        content_chunks = []
        relevant_found = False
        for result in search_results:
            content = result.get("content", "No Content")[:MAX_CONTENT_LENGTH]  # Limit content length

            if is_content_relevant(content, query, embedding_client):
                relevant_found = True
                doc_url = result.get("URL", "No URL available")
                department = result.get("department", "No Department")
                content_chunks.append(content)
                
            
                results.append({
                    "document_url": doc_url,
                    "department": department,
                    "content": content
                })

        if not relevant_found:
            return func.HttpResponse(
                json.dumps({"response": "No relevant content found.", "error": None}),
                status_code=200,
                mimetype="application/json",
                headers={"Access-Control-Allow-Origin": "*"}
            )


        gpt_response = generate_gpt_response(embedding_client, content_chunks, query)
        
        logging.info(gpt_response)

        document_links = "\n\nHere are some related documents for your reference:\n"
        for result in results:
            department_text = f" (Department: {result['department']})" if result['department'] else " (Department: N/A)"
            document_links += f" - {result['document_url']}{department_text}\n"

   
        final_response = {
            "response": gpt_response,
            'documents_links': document_links,  
            "error": None
        }
        
        if gpt_response == "No relevant content found.":
            
            final_response["documents_links"] = ""
             
        


       
        return func.HttpResponse(
            json.dumps(final_response),
            status_code=200,
            mimetype="application/json",
            headers={"Access-Control-Allow-Origin": "*"}
        )

    except ValueError as ve:
        logging.error(f"Configuration error: {str(ve)}")
        return func.HttpResponse(
            json.dumps({"response": None, "error": str(ve)}),
            status_code=500,
            mimetype="application/json",
            headers={"Access-Control-Allow-Origin": "*"}
        )
    except Exception as e:
        logging.error(f"Error: {str(e)}")
        return func.HttpResponse(
            json.dumps({"response": None, "error": str(e)}),
            status_code=500,
            mimetype="application/json",
            headers={"Access-Control-Allow-Origin": "*"}
        )
