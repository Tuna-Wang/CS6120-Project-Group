from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
from typing import Optional
from utils.const import InputDataTitles
import logging
import os
import getpass


class Worker:
    def __init__(
        self,
        logger: logging.Logger,
        
    ):
        """
        Unified worker supporting both Ollama and Gemini backends.
        
        Args:
            ollama_model: Model name for Ollama (e.g., "llama3", "mistral")
            gemini_model: Model name for Gemini
            temperature: Creativity control (0-1)
            max_tokens: Max tokens to generate
        """
        self.logger = logger
        self.llm = None
        
        

    def imitate(
        self,
        retriever,
        input_text: str,
        character: str = InputDataTitles.DEFAULT_CHARACTER,
        api_key: str = None
    ) -> str:
        """
        Generate character-styled response using RAG.
        
        Args:
            retriever: Vector store retriever
            input_text: User input
            character: Character to imitate
        """
        if not api_key:
            raise ValueError("API key is required for Gemini backend.")
        else:
            self.llm = ChatGoogleGenerativeAI(
                model="gemini-2.0-flash-001",
                temperature=0.5,
                max_tokens=512,
                max_retries=2,
                api_key=api_key
            )
        
        try:
            #Alternative prompt: You are my personal assistant, imitate the speech style of the given speech.
            prompt_template = f"""Pretend you are {character}. Respond using their style.
            
            Examples of their speech:
            {{context}}
            
            Input: {{input_text}}
            {character}:"""  # Modified prompt for better character alignment

            example_context = retriever.get_relevant_documents(input_text)
            print(f"Example context: {example_context}")

            chain = (
                {"context": retriever, "input_text": RunnablePassthrough()}
                | ChatPromptTemplate.from_template(prompt_template)
                | self.llm
            )

            return chain.invoke(input_text)
        
        except Exception as e:
            self.logger.error(f"Generation failed: {str(e)}")
            return f"Apologies, I couldn't generate a response. Error: {str(e)}"


