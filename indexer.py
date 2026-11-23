import time
import os
from dotenv import load_dotenv
from site_config import RESTRICTED_SITES
from scraping import scrape_fextralife
from openai import OpenAI
import ollama

load_dotenv()

LANGUAGE_MODEL = 'hf.co/bartowski/Llama-3.2-1B-Instruct-GGUF'
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL")

VECTOR_DB = []

oai = OpenAI(
    api_key=os.getenv("EMBEDDING_API_KEY") or "lm-studio",
    base_url=os.getenv("EMBEDDING_BASE_URL") or None,  # e.g. http://localhost:1234/v1 for LM Studio
)


def add_chunk_to_vector_db(chunk):
    embedding = oai.embeddings.create(
        input=chunk,
        model=EMBEDDING_MODEL,
    ).data[0].embedding

    VECTOR_DB.append((chunk, embedding))

# scraping
start = time.perf_counter()
for i, chunk in enumerate(RESTRICTED_SITES):
    chunk_text = scrape_fextralife(chunk["url"])
    add_chunk_to_vector_db(chunk_text)
end = time.perf_counter()
print(f"added all chunks to vector db in {end - start:.2f} seconds")

# similarity function
def cosine_similarity(a, b):
    dot_product = sum([x * y for x, y in zip(a, b)])
    norm_a = sum([x ** 2 for x in a]) ** 0.5
    norm_b = sum([x ** 2 for x in b]) ** 0.5
    return dot_product / (norm_a * norm_b)

# retrieval function to get the most relevant chunks based on the query
def retrieve(query, top_n=3):
    query_embedding = oai.embeddings.create(
        input=query,
        model=EMBEDDING_MODEL,
    ).data[0].embedding
    # temporary list to hold (chunk, similarity) tuples
    similarities = []
    for chunk, embedding in VECTOR_DB:
        similarity = cosine_similarity(query_embedding, embedding)
        similarities.append((chunk, similarity))
    # sort by similarity in descending order, higher similarity = more relevant
    similarities.sort(key=lambda x: x[1], reverse=True)
    return similarities[:top_n]




#generation
question = input("Ask me about Dark Souls 2: ")
retrieved_knowledge = retrieve(question)

print("Retrieved knowledge:")
for chunk, similarity in retrieved_knowledge:
    print(f" - (similarity: {similarity:.4f}) {chunk[:35]}...")  # print first 35 chars of each chunk

relevant_chunks = [chunk for chunk, similarity in retrieved_knowledge if similarity > 0.6] # adjust threshold as needed
formatted_context = "\n\n".join(
    [f"[Excerpt {i+1}]\n{chunk.strip()}" for i, chunk in enumerate(relevant_chunks)]
)


system_prompt = """You are a Dark Souls 2 expert assistant. Answer the user's question using ONLY the facts provided inside the <context> tags.

RULES:
1. Write complete, natural, and well-explained sentences (never reply with single words or fragments).
2. Gather and include ALL relevant facts, types, or details found across the excerpts—do not stop at the first detail you find.
3. State the answer directly as an established fact, without meta-commentary (never mention "context", "excerpts", "text", or "provided").
4. Answer in the exact same language as the user's question.
5. If the <context> does not contain the answer, reply strictly with: "I don't know."
"""

user_prompt = f"""<context>
{formatted_context}
</context>

Question: {question}"""

print(formatted_context[:500])

stream = ollama.chat(
    model=LANGUAGE_MODEL,
    messages=[
        {'role': 'system', 'content': system_prompt},
        {'role': 'user', 'content': user_prompt},
    ],
    options={
        'temperature': 0.2,
        'num_ctx': 8192,
    },
    stream=True,
)

print(f"user question: {question}") 
print("chatbot response:")
for chunk in stream:
    print(chunk['message']['content'], end='', flush=True)