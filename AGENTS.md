# Project: MedTech RAG MVP (Azure AI Search + OpenAI)

Act as a Senior Full Stack Engineer specializing in Enterprise SaaS. We are building a high-stakes MedTech MVP that helps QA managers navigate EU regulations.

## Architecture Overview
- **Pattern:** Retrieval Augmented Generation (RAG) with a focus on precision and source citation.
- **Infrastructure:** Azure AI Search (Vector + Keyword), Azure OpenAI (GPT-4o), Azure Blob Storage (Source Files).

## Tech Stack Requirements (Strict Adherence)

### 1. Backend (Python)
- **Framework:** FastAPI (latest stable).
- **Runtime:** Python 3.11+.
- **Libraries:** - `pydantic` (v2) for strict data validation.
  - `azure-search-documents` (latest) for retrieval.
  - `openai` (latest) for Azure OpenAI interaction.
  - `python-multipart` for handling file uploads (if needed later).
- **Standards:**
  - Type hints everywhere (`typing`).
  - Async/Await pattern.
  - 12-factor app principles (config via Environment Variables).

### 2. Frontend (React)
- **Framework:** Next.js 14/15 (App Router).
- **Language:** TypeScript (Strict mode).
- **Styling:** Tailwind CSS + shadcn/ui (or a clean custom implementation using Lucide React icons).
- **State Management:** React Hooks (`useState`, `useEffect`, custom hooks).
- **Communication:** Fetch API with support for Streaming Responses (NDJSON).

---

## Task Description

Create a monorepo structure with `/backend` and `/frontend`.

### Step 1: Backend Implementation (`/backend`)
Create a `main.py` and necessary modules implementing the following logic:

1.  **Configuration:** Load `AZURE_SEARCH_ENDPOINT`, `AZURE_SEARCH_KEY`, `AZURE_OPENAI_ENDPOINT`, `AZURE_OPENAI_KEY` from `.env`.
2.  **RAG Logic:**
    - Initialize `SearchClient` and `AzureOpenAI` client.
    - Implement a `retrieve_context(query: str)` function that queries Azure AI Search (Hybrid + Semantic Reranking).
    - It must return the content AND metadata (specifically `reference_id`, `title`, and `filename`).
3.  **Streaming Endpoint:** `POST /chat/stream`
    - Accepts JSON: `{"query": "User question...", "history": []}`.
    - **Crucial:** Use Server-Sent Events (SSE) or NDJSON (Newline Delimited JSON) format.
    - **Flow:**
      - First, yield a JSON object containing the retrieved **SOURCES** (so the UI can render citations immediately).
      - Second, yield the GPT-4o response token-by-token.
    - System Prompt: Enforce strict adherence to the provided context. If the answer is not in the context, state "I don't know".

### Step 2: Frontend Implementation (`/frontend`)
**Note: Frontend implementation is currently postponed. Interaction will be handled via a terminal client for now.**

Create a Next.js application:

1.  **Layout:** A "Split Screen" or "Sidebar" layout.
    - **Left/Main:** Chat Interface.
    - **Right/Side:** Source Viewer (Placeholder for now, displaying metadata of clicked sources).
2.  **Chat Interface:**
    - Input field at the bottom.
    - Message list (User vs. AI).
    - **Citation Rendering:** When the backend sends sources, display them as clickable "Chips" or "Cards" above or below the AI response.
3.  **Streaming Hook:**
    - Implement a robust `useChatStream` hook that handles the NDJSON stream.
    - It must distinguish between a "Source Event" (metadata) and a "Token Event" (text generation).
    - Update the UI in real-time (typewriter effect).

## Testing Strategy:

    All code must be accompanied by unit tests.
    
    Use `pytest` as the testing framework for python.
    Use **Vitest** + **React Testing Library** for the frontend.
    
    Create a `tests/` directory and ensure tests cover:
        - Parsing logic (identifying articles, extracting fields).
        - Schema validation (ensuring output matches the Pydantic model).
        - Error handling.
    
    Mock external requests (e.g., HTML fetching) to ensure tests are deterministic and fast.

## Output Expectations
- Do not use LangChain or LlamaIndex. Use native Azure SDKs to maintain full control.
- Provide the full file structure.
- Provide the `requirements.txt` for backend and `package.json` dependencies for frontend.
- Ensure CORS is configured in FastAPI to allow requests from `localhost:3000`.

Start by generating the project structure and the Backend code first.