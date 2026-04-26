from llama_cpp import Llama
from app.config import settings
import os
import gc
import psutil


def _log_memory():
    mem = psutil.virtual_memory()
    print(f"  RAM: {mem.percent:.1f}% used ({mem.used / 1e9:.1f}GB / {mem.total / 1e9:.1f}GB)")


class LLMService:
    def __init__(self):
        self.model = None
        self.load_model()

    def load_model(self):
        """
        Load GGUF model optimised for Ryzen 4500U (6 cores, AVX2, no GPU).
        Settings chosen:
          n_threads=5  — leaves 1 core free for OS/Docker overhead
          n_batch=32   — Ryzen handles 32 tokens/batch comfortably
          n_ctx=512    — enough for RAG prompts, keeps RAM low
          n_gpu_layers=0 — no GPU present
          f16_kv=False — CPU doesn't benefit from float16 KV cache
          use_mlock=False — avoids memory pressure under Docker
        """
        try:
            model_path = settings.MODEL_PATH

            if not os.path.exists(model_path):
                print(f"⚠️  Model not found at {model_path}")
                print("    Place your .gguf file there and restart.")
                return

            print(f"🔄 Loading model from {model_path}...")
            _log_memory()

            self.model = Llama(
                model_path=model_path,
                n_ctx=settings.LLM_CONTEXT_SIZE,   # 512
                n_threads=settings.LLM_THREADS,     # 5
                n_batch=settings.LLM_BATCH_SIZE,    # 32
                n_gpu_layers=0,
                f16_kv=False,
                use_mlock=False,
                verbose=False,
            )

            print("✅ Model loaded successfully")
            _log_memory()

        except Exception as e:
            print(f"❌ Error loading model: {e}")
            self.model = None

    def generate_response(self, prompt: str, max_tokens: int = None) -> str:
        """Generate response using GGUF model."""
        if not self.model:
            return self._fallback_response()

        tokens = max_tokens or settings.LLM_MAX_TOKENS

        try:
            response = self.model(
                prompt,
                max_tokens=tokens,
                temperature=0.1,
                top_p=0.9,
                top_k=40,
                repeat_penalty=1.1,
                stop=["</s>", "User:", "\n\n\n"],
            )
            text = response["choices"][0]["text"].strip()

            # Free intermediate objects to keep memory tidy on long sessions
            gc.collect()
            return text

        except Exception as e:
            print(f"Generation error: {e}")
            return self._fallback_response()

    def _fallback_response(self) -> str:
        return (
            "I apologize, but the AI model is currently unavailable. "
            "Please consult a registered healthcare professional for accurate medicine information."
        )


llm_service = LLMService()
