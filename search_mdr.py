import os
from dotenv import load_dotenv
from azure.core.credentials import AzureKeyCredential
from azure.search.documents import SearchClient
from azure.search.documents.models import VectorizedQuery
from openai import AzureOpenAI

# 1. Load Secrets
load_dotenv()

service_endpoint = os.getenv("AZURE_SEARCH_ENDPOINT")
service_key = os.getenv("AZURE_SEARCH_KEY")
index_name = os.getenv("AZURE_SEARCH_INDEX")

aoai_endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
aoai_key = os.getenv("AZURE_OPENAI_KEY")
aoai_deployment = os.getenv("AZURE_OPENAI_DEPLOYMENT")
aoai_version = os.getenv("AZURE_OPENAI_API_VERSION")

# 2. Initialize Clients
search_client = SearchClient(service_endpoint, index_name, AzureKeyCredential(service_key))
openai_client = AzureOpenAI(
    azure_endpoint=aoai_endpoint, 
    api_key=aoai_key, 
    api_version=aoai_version
)

def generate_embeddings(text):
    response = openai_client.embeddings.create(input=text, model=aoai_deployment)
    return response.data[0].embedding

# 3. The Search Function
def search_mdr(query):
    print(f"\n🔎 Searching for: '{query}'...")
    
    # A. Generate Vector for the query
    vector = generate_embeddings(query)
    
    # B. Execute Hybrid Search + Semantic Reranking
    results = search_client.search(
        search_text=query,
        
        # Vector Search Part
        vector_queries=[VectorizedQuery(vector=vector, k_nearest_neighbors=50, fields="contentVector")],
        
        # Semantic Part
        query_type="semantic",
        semantic_configuration_name="my-semantic-config",
        
        # Return top 5 best matches
        top=5,
        select=["title", "content", "chapter", "id", "url"]
    )

    # C. Print Results
    print(f"{'-'*60}")
    for result in results:
        score = result.get('@search.reranker_score', 0) # The AI Relevance Score (0-4)
        print(f"🌟 Relevance: {score:.2f}/4.00 | ID: {result['id']}")
        print(f"Title: {result['title']}")
        print(f"Chapter: {result['chapter']}")
        # Print first 200 chars of content as preview
        print(f"Snippet: {result['content'][:200].replace('\n', ' ')}...")
        print(f"{'-'*60}")

if __name__ == "__main__":
    # Test queries
    search_mdr("Was ist ein invasives Produkt?")
    search_mdr("Fristen für die klinische Bewertung")