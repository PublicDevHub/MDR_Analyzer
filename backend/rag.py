import os
from typing import List, Tuple
from azure.core.credentials import AzureKeyCredential
from azure.search.documents.aio import SearchClient
from azure.search.documents.models import VectorizedQuery
from openai import AsyncAzureOpenAI
from backend.config import settings
from backend.models import Source

# Initialize Clients
# Note: Using Async SearchClient for non-blocking I/O
search_client = SearchClient(
    endpoint=settings.AZURE_SEARCH_ENDPOINT,
    index_name=settings.AZURE_SEARCH_INDEX_NAME,
    credential=AzureKeyCredential(settings.AZURE_SEARCH_KEY)
)

openai_client = AsyncAzureOpenAI(
    azure_endpoint=settings.AZURE_OPENAI_ENDPOINT,
    api_key=settings.AZURE_OPENAI_KEY,
    api_version="2024-02-15-preview"
)

async def retrieve_context(query: str) -> Tuple[List[Source], str]:
    """
    Queries Azure AI Search using Hybrid Search (Vector + Keyword).
    Returns a list of Source objects and the combined text content for the LLM context.
    """

    # Generate embedding for the query
    # Assuming the deployment name for embeddings is also needed or use a specific model
    # For now hardcoding a common model, but this might need to match an Azure Deployment
    embedding_response = await openai_client.embeddings.create(
        model=settings.AZURE_OPENAI_EMBEDDING_DEPLOYMENT,
        input=query
    )
    query_vector = embedding_response.data[0].embedding

    vector_query = VectorizedQuery(vector=query_vector, k_nearest_neighbors=3, fields="contentVector")

    # Perform Hybrid Search
    results = await search_client.search(
        search_text=query,
        vector_queries=[vector_query],
        select=["reference_id", "title", "filename", "content"],
        top=5
    )

    sources = []
    context_parts = []

    async for result in results:
        # Safely get fields
        ref_id = result.get("reference_id", "unknown")
        title = result.get("title", "Untitled")
        filename = result.get("filename", "unknown.pdf")
        content = result.get("content", "")

        sources.append(Source(reference_id=ref_id, title=title, filename=filename))
        context_parts.append(f"Source ({filename}): {content}")

    return sources, "\n\n".join(context_parts)

async def generate_answer(query: str, context: str):
    """
    Generates an answer from Azure OpenAI using the provided context.
    Returns an async generator.
    """
    system_prompt = (
        "You are a helpful assistant for MedTech QA managers. "
        "Use the provided context to answer the user's question. "
        "Enforce strict adherence to the provided context. "
        "If the answer is not in the context, state 'I don't know'."
    )

    user_prompt = f"Context:\n{context}\n\nQuestion: {query}"

    response = await openai_client.chat.completions.create(
        model=settings.AZURE_OPENAI_DEPLOYMENT_NAME,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ],
        stream=True
    )

    return response

async def close_clients():
    await search_client.close()
    await openai_client.close()
