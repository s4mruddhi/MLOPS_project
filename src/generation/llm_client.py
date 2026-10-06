"""
LLM Client Interface & Local Synthesizers.
Supports Ollama (Local LLM API at http://localhost:11434) and OpenAI API,
with zero Gemini API dependency and a deterministic Local Context Synthesizer fallback.
"""

import os
import time
import re
import json
import urllib.request
from typing import List, Dict, Any, Tuple

FALLBACK_MESSAGE = "I could not find sufficient information in the verified organizational documents."

class OllamaClient:
    """Client for local Ollama server (http://localhost:11434)."""
    
    def __init__(self, host: str = None, model: str = None):
        self.host = host or os.getenv("OLLAMA_HOST", "http://localhost:11434")
        self.model = model or os.getenv("OLLAMA_MODEL", "llama3")

    def is_available(self) -> bool:
        """Checks if local Ollama service is reachable."""
        try:
            url = f"{self.host.rstrip('/')}/api/tags"
            req = urllib.request.Request(url, method="GET")
            with urllib.request.urlopen(req, timeout=2) as resp:
                return resp.status == 200
        except Exception:
            return False

    def generate_completion(self, prompt: str, system_prompt: str = "") -> str:
        """Sends prompt to local Ollama /api/generate endpoint."""
        url = f"{self.host.rstrip('/')}/api/generate"
        payload_data = {
            "model": self.model,
            "prompt": prompt,
            "system": system_prompt,
            "stream": False,
            "options": {"temperature": 0.0}
        }
        payload = json.dumps(payload_data).encode("utf-8")
        req = urllib.request.Request(url, data=payload, headers={"Content-Type": "application/json"})
        timeout_sec = int(os.getenv("OLLAMA_TIMEOUT", "60"))
        with urllib.request.urlopen(req, timeout=timeout_sec) as response:
            res = json.loads(response.read().decode("utf-8"))
            return res.get("response", "")

class LocalContextSynthesizer:
    """
    Deterministic Local Extractive Synthesizer.
    Parses retrieved context chunks, extracts relevant factual sentences, 
    embeds chunk_id citations, and strictly enforces the unanswerable fallback.
    """

    @staticmethod
    def synthesize(query: str, retrieved_chunks: List[Dict[str, Any]]) -> Tuple[str, List[str]]:
        if not retrieved_chunks:
            return FALLBACK_MESSAGE, []

        valid_chunks = [c for c in retrieved_chunks if c.get("score", 0.0) >= 0.35]
        if not valid_chunks:
            return FALLBACK_MESSAGE, []

        query_words = set(re.findall(r"\w+", query.lower())) - {
            "what", "is", "the", "for", "how", "do", "i", "are", "a", "an", "in", "to", "of", "and", "or", "on", "with", "about"
        }
        
        extracted_sentences = []
        citations = []

        for chunk in valid_chunks:
            chunk_id = chunk["chunk_id"]
            text = chunk["text"]
            
            # Clean markdown headers (#, ##, ###) for smooth text flow
            clean_text = re.sub(r"#+\s*", "", text).strip()
            
            # Split into sentences
            sentences = [s.strip() for s in re.split(r"(?<=[.!?\n])\s+", clean_text) if s.strip()]
            matching_sentences = []
            
            for s in sentences:
                s_words = set(re.findall(r"\w+", s.lower()))
                if query_words & s_words:
                    matching_sentences.append(s)

            if matching_sentences:
                combined_snippet = " ".join(matching_sentences[:2])
                extracted_sentences.append(f"{combined_snippet} [{chunk_id}]")
                citations.append(chunk_id)
            elif clean_text and len(extracted_sentences) < 2:
                # Fallback to top sentence of valid chunk
                first_sentence = sentences[0] if sentences else clean_text[:150]
                extracted_sentences.append(f"{first_sentence} [{chunk_id}]")
                citations.append(chunk_id)

        if not extracted_sentences:
            return FALLBACK_MESSAGE, []

        answer = "\n\n".join(extracted_sentences[:3])
        unique_citations = list(dict.fromkeys(citations))
        return answer, unique_citations

class LLMClient:
    """Environment-driven LLM dispatch client (Ollama / Local Synthesizer / OpenAI)."""

    def __init__(self):
        self.ollama_host = os.getenv("OLLAMA_HOST", "http://localhost:11434")
        self.ollama_model = os.getenv("OLLAMA_MODEL", "llama3")
        self.ollama_client = OllamaClient(host=self.ollama_host, model=self.ollama_model)
        self.openai_key = os.getenv("OPENAI_API_KEY")

        # Prioritize Ollama local LLM server over external Gemini API
        if self.ollama_client.is_available():
            self.provider = "ollama"
        elif self.openai_key:
            self.provider = "openai"
        else:
            self.provider = "local_deterministic_synthesizer"

    def generate(self, query: str, retrieved_chunks: List[Dict[str, Any]], system_prompt: str, answer_template: str) -> Tuple[str, List[str], float, str]:
        start_time = time.time()
        
        # Check retrieval relevance threshold
        valid_chunks = [c for c in retrieved_chunks if c.get("score", 0.0) >= 0.35]
        if not valid_chunks:
            return FALLBACK_MESSAGE, [], 0.0, "system_guardrail"

        # 1. Ollama Local Model
        if self.provider == "ollama" or os.getenv("USE_OLLAMA", "0") == "1":
            try:
                formatted_context = "\n\n".join([f"[{c['chunk_id']}]: {c['text']}" for c in retrieved_chunks])
                user_prompt = answer_template.format(context_documents=formatted_context, user_question=query)
                answer = self.ollama_client.generate_completion(user_prompt, system_prompt=system_prompt)
                
                if "could not find sufficient information" in answer.lower():
                    return FALLBACK_MESSAGE, [], round(time.time() - start_time, 6), f"ollama ({self.ollama_model})"

                citations = re.findall(r"\[([A-Z0-9_-]+_chunk_\d+)\]", answer)
                if not citations:
                    citations = [c["chunk_id"] for c in retrieved_chunks if c.get("score", 0.0) >= 0.35]
                
                elapsed = time.time() - start_time
                return answer, list(set(citations)), round(elapsed, 6), f"ollama ({self.ollama_model})"
            except Exception as e:
                # Fallback to local deterministic synthesizer on connection error
                answer, citations = LocalContextSynthesizer.synthesize(query, retrieved_chunks)
                elapsed = time.time() - start_time
                return answer, citations, round(elapsed, 6), "local_deterministic_synthesizer (ollama_fallback)"

        # 2. OpenAI API
        if self.provider == "openai":
            try:
                import openai
                openai.api_key = self.openai_key
                formatted_context = "\n\n".join([f"[{c['chunk_id']}]: {c['text']}" for c in retrieved_chunks])
                user_content = answer_template.format(context_documents=formatted_context, user_question=query)
                
                response = openai.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_content}
                    ],
                    temperature=0.0
                )
                answer = response.choices[0].message.content
                citations = re.findall(r"\[([A-Z0-9_-]+_chunk_\d+)\]", answer)
                elapsed = time.time() - start_time
                return answer, list(set(citations)), round(elapsed, 6), "openai"
            except Exception as e:
                answer, citations = LocalContextSynthesizer.synthesize(query, retrieved_chunks)
                elapsed = time.time() - start_time
                return answer, citations, round(elapsed, 6), "local_deterministic_synthesizer (api_fallback)"

        # 3. Default Fast Deterministic Local Synthesizer
        answer, citations = LocalContextSynthesizer.synthesize(query, retrieved_chunks)
        elapsed = time.time() - start_time
        return answer, citations, round(elapsed, 6), self.provider
