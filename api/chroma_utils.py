from langchain_community.document_loaders import (
    PyPDFLoader,
    Docx2txtLoader,
    UnstructuredHTMLLoader,
)
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_chroma import Chroma
from typing import List
from langchain_core.documents import Document
import os
# from langchain_community.embeddings.sentence_transformer import (
#     SentenceTransformerEmbeddings,
# )
from langchain_huggingface import HuggingFaceEmbeddings


# Initialize text splitter and embedding function
text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=1000, chunk_overlap=200, length_function=len
)
embedding_function = HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-MiniLM-L6-v2"
)

# embedding_function = SentenceTransformerEmbeddings(model_name="all-MiniLM-L6-v2")


# Initialize Chroma vector store
vectorstore = Chroma(
    persist_directory="./chroma_db", embedding_function=embedding_function
)


def load_and_split_document(file_path: str) -> List[Document]:
    if file_path.endswith(".pdf"):
        loader = PyPDFLoader(file_path)
    elif file_path.endswith(".docx"):
        loader = Docx2txtLoader(file_path)
    elif file_path.endswith(".html"):
        loader = UnstructuredHTMLLoader(file_path)
    else:
        raise ValueError(f"Unsupported file type: {file_path}")

    documents = loader.load()
    return text_splitter.split_documents(documents)


def index_document_to_chroma(file_path: str, file_id: int) -> bool:
    try:
        splits = load_and_split_document(file_path)

        # Add metadata to each split
        for split in splits:
            split.metadata["file_id"] = file_id

        vectorstore.add_documents(splits)
        return True
    except Exception as e:
        print(f"Error indexing document: {e}")
        return False


def delete_doc_from_chroma(file_id: int):
    try:
        docs = vectorstore._collection.get(include=["metadata"])
        matched_ids = [
            doc_id for doc_id, metadata in zip(docs["ids"], docs["metadatas"]) if metadata.get("file_id") == file_id
        ]
        vectorstore._collection.delete(ids=matched_ids)
        print(f"Deleted all documents with file_id {file_id}")
        return True
    
    except Exception as e:
        print(f"Error deleting document with file_id {file_id} from Chroma: {str(e)}")
        
        return False
