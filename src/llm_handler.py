"""
LLM Handler Module
Manages OpenAI API calls and response generation
"""

import logging
import os
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage

logger = logging.getLogger(__name__)


class LLMHandler:
    """Handles interaction with OpenAI LLMs"""

    def __init__(
        self,
        model: str = "gpt-4",
        temperature: float = 0.7,
        max_tokens: int = 1000,
    ):
        """Initialize LLM Handler"""
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OPENAI_API_KEY not found in environment")

        self.llm = ChatOpenAI(
            model=model,
            temperature=temperature,
            max_tokens=max_tokens,
            openai_api_key=api_key,
        )

        logger.info(f"LLM initialized: {model}")

    def generate_response(
        self,
        query: str,
        context: str,
        use_citations: bool = True,
    ) -> str:
        """Generate response using context from RAG"""
        
        if use_citations:
            prompt_text = """You are a helpful restaurant assistant. 
Use the provided context to answer the question accurately.
If the answer is not in the context, say "I don't have that information."
Always cite which document your answer comes from.

Context:
{context}

Question: {query}

Answer:"""
        else:
            prompt_text = """You are a helpful restaurant assistant.
Use the provided context to answer the question accurately.
If the answer is not in the context, say "I don't have that information."

Context:
{context}

Question: {query}

Answer:"""

        # Format the prompt with actual values
        formatted_prompt = prompt_text.format(context=context, query=query)

        logger.info(f"Generating response for query: {query[:50]}...")

        # Call LLM directly
        response = self.llm.invoke([HumanMessage(content=formatted_prompt)])

        return response.content.strip()

    def check_api_status(self) -> bool:
        """Check if API is working"""
        try:
            response = self.llm.invoke([HumanMessage(content="Hi")])
            logger.info("API status: OK")
            return True
        except Exception as e:
            logger.error(f"API status check failed: {str(e)}")
            return False

    def generate_followup_suggestions(self, query: str) -> list:
        """Generate suggested follow-up questions"""
        prompt_text = """Based on this restaurant question, suggest 3 relevant follow-up questions.
Format as a numbered list.

Original question: {query}

Follow-up questions:"""

        formatted_prompt = prompt_text.format(query=query)
        response = self.llm.invoke([HumanMessage(content=formatted_prompt)])

        # Parse response into list
        suggestions = [line.strip() for line in response.content.split('\n') if line.strip()]
        return suggestions[:3]