import os
from langchain_openai import OpenAIEmbeddings
from langchain_chroma import Chroma  # ✅ Corrected Import
from langchain_community.docstore.document import Document
from google_search import google_partselect_search
from langchain.memory import ConversationBufferMemory



class LivePartSelectMemory:
    def __init__(self):
        """
        Live vector store using Chroma (in-memory) that updates dynamically with PartSelect search results.
        """
        self.embedding_model = OpenAIEmbeddings(
            openai_api_key=os.getenv("OPENAI_API_KEY"),
            model="text-embedding-ada-002"
        )

        # ✅ Initialize Chroma without `from_documents` (avoiding the empty list issue)
        self.vector_store = Chroma(embedding_function=self.embedding_model)

        # ✅ Use a retriever to enable dynamic search
        self.memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True)

    def live_search_and_index(self, query: str, k=3):
        """
        1) Perform a live Google search for the query (restricted to PartSelect).
        2) Extract snippets & links.
        3) Convert them into embeddings and store dynamically in-memory.
        4) Returns indexed results for immediate semantic search.
        """
        results = google_partselect_search(query, num_results=k)
        if not results:
            print(f"❌ No search results found for: {query}")
            return "No results found on PartSelect for that query."

        documents = []
        for snippet, link in results:
            combined_text = f"Snippet: {snippet}\nURL: {link}"

            if combined_text.strip():  # ✅ Ensure valid text before embedding
                doc = Document(page_content=combined_text, metadata={"source": link})
                documents.append(doc)

        if not documents:
            print("❌ No valid documents found to index.")
            return "No valid data found to index."

        # ✅ Prevent Empty Embeddings Error
        try:
            # Generate embeddings and check if they are empty
            embeddings = [self.embedding_model.embed_query(doc.page_content) for doc in documents]
            if not embeddings or len(embeddings) == 0:
                print("❌ No embeddings were generated. Skipping indexing.")
                return "Error: OpenAI embeddings failed."

            # ✅ Index new documents live
            self.vector_store.add_documents(documents)
            return f"Live indexed {len(documents)} new items from PartSelect."
        except ValueError as e:
            print("❌ Error during embedding:", str(e))
            return "Error: Unable to index data."

    def semantic_search(self, query: str, top_k=3):
        """
        Perform a semantic similarity search on in-memory vector store for the given query.
        If no results exist, it first performs a live search and indexes the results.
        """
        results = self.vector_store.similarity_search(query, k=top_k)

        if not results:
            print(f"⚠️ No relevant results found for query: {query}. Running live search...")
            self.live_search_and_index(query, k=3)  # Automatically search & index
            results = self.vector_store.similarity_search(query, k=top_k)  # Try again after indexing

        if not results:
            return ["No relevant results found even after live indexing."]

        return [f"Snippet: {doc.page_content}\nSource: {doc.metadata.get('source')}" for doc in results]

# Create a single global instance for live search and indexing
live_store = LivePartSelectMemory()
