from raganything import RAGAnything, RAGAnythingConfig
from lightrag.llm.openai import openai_complete_if_cache, openai_embed
from lightrag.utils import EmbeddingFunc
import config

async def local_llm_complete(prompt, system_prompt=None, history=[], **kwargs):
    try:
        return await openai_complete_if_cache(
            model=config.LLM_MODEL,
            prompt=prompt,
            system_prompt=system_prompt,
            history=history,
            api_key=config.OLLAMA_API_KEY,
            base_url=config.OLLAMA_BASE_URL,
            **kwargs
        )
    except Exception as e:
        print(f"\n❌ Lỗi kết nối LLM (Ollama): {e}")
        print(f"💡 Hãy chắc chắn Ollama đang chạy model: {config.LLM_MODEL}")
        raise e

async def local_embedding(texts: list[str]) -> list[list[float]]:
    try:
        return await openai_embed(
            texts,
            model=config.EMBEDDING_MODEL,
            api_key=config.OLLAMA_API_KEY,
            base_url=config.OLLAMA_BASE_URL
        )
    except Exception as e:
        print(f"\n❌ Lỗi kết nối Embedding (Ollama): {e}")
        print(f"💡 Hãy chắc chắn bạn đã kéo model: `ollama pull {config.EMBEDDING_MODEL}`")
        raise e

embedding_func = EmbeddingFunc(
    embedding_dim=config.EMBEDDING_DIM,
    max_token_size=8192,
    func=local_embedding
)

def get_rag_instance():
    rag_config = RAGAnythingConfig(
        working_dir=config.STORAGE_DIR,
        parser="mineru",
        parse_method="auto",
        enable_image_processing=True,
        enable_table_processing=True,
    )
    return RAGAnything(
        config=rag_config,
        llm_model_func=local_llm_complete,
        vision_model_func=local_llm_complete,
        embedding_func=embedding_func
    )
