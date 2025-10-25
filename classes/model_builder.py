import os
from sentence_transformers import SentenceTransformer
import faiss

class ModelBuilder:
    CHUNKS_DIR = "chunk"
    MODEL_DIR = "model"

    def create_and_save_embeddings(chunks: list[str], model_filename: str, model_name: str = 'all-MiniLM-L6-v2'):
        """Converts text chunks into embeddings and saves them to a FAISS index."""

        # Ensure the target directories exist
        os.makedirs(ModelBuilder.CHUNKS_DIR, exist_ok=True)
        os.makedirs(ModelBuilder.MODEL_DIR, exist_ok=True)
        
        print("Loading embedding model...")
        # Load a general-purpose, fast embedding model
        model = SentenceTransformer(model_name)
        
        print("Creating embeddings...")
        # Generate embeddings for all text chunks
        embeddings = model.encode(chunks)
        
        # Create a FAISS index (a simple vector database)
        dimension = embeddings.shape[1]
        index = faiss.IndexFlatL2(dimension)
        
        # Add the embeddings to the index
        index.add(embeddings)
        
        print(f"Embeddings created and indexed. Dimension: {dimension}, Total Vectors: {index.ntotal}")
        
        # Save the index and the original text chunks for later retrieval
        model_path = f"model/{model_filename}_model.bin"
        faiss.write_index(index, model_path)
        print(f"FAISS index saved to {model_path}")
        
        # Save the chunks to a file so we can map vectors back to text
        chunks_path = os.path.join(ModelBuilder.CHUNKS_DIR, f"{model_filename}_chunks.txt")
        with open(chunks_path, "w", encoding="utf-8") as f:
            # Save chunks separated by a clear delimiter for easy reloading
            f.write('\n--ENTRY--\n'.join(chunks)) 
        print(f"Dictionary chunks saved to {chunks_path}")

        print("FAISS index and chunks saved successfully.")
        return model # Return the model for later use