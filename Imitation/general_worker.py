from langchain_community.chat_models import ChatOllama
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnableParallel, RunnablePassthrough
from typing import Optional
from utils.const import InputDataTitles
import logging


class Worker:
    def __init__(
        self,
        logger: logging.Logger,
        
    ):
        
        self.logger = logger
        self.llm = None

    def imitate(
        self,
        input_text: str,
        character_retriever,
        personal_retriever,
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

        print("###### debugging ######")
        print(type(character_retriever))
        print(type(personal_retriever))
        print(personal_retriever)
        retrieved_data = RunnableParallel({
            "character_context": character_retriever,
            "personal_context": personal_retriever,
            "input": RunnablePassthrough()
        }).invoke(input_text)

        if not api_key:
            raise ValueError("API key is required for Gemini backend.")
        else:
            self.llm = ChatGoogleGenerativeAI(
                model="gemini-2.0-flash-001",
                temperature = 0.5,
                max_tokens = 512,
                max_retries=2,
                api_key=api_key
            )

        
        try:
            prompt_template = """Pretend you are {character}. Respond in their style while incorporating relevant personal details.
        
            <CHARACTER EXAMPLES>
            {character_context}
            </CHARACTER EXAMPLES>
            
            <PERSONAL KNOWLEDGE>
            {personal_context}
            </PERSONAL KNOWLEDGE>

            
            <INPUT>
            {input}
            </INPUT>
            
            Response:"""
            
            print(f"Prompt template: {prompt_template}")
            chain = (
                ChatPromptTemplate.from_template(prompt_template)
                | self.llm
            )
            return chain.invoke({
                **retrieved_data,
                "character": character
            })
            
        except Exception as e:
            self.logger.error(f"Generation failed: {str(e)}")
            return f"Apologies, I couldn't generate a response. Error: {str(e)}"