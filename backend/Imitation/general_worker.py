from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnableParallel, RunnablePassthrough
from DB_creator.worker import Worker as VectorDBWorker
from utils.config import Config
import os

class Worker:
    def __init__(self, vdb_client: VectorDBWorker, logger):
        self.logger = logger
        self.vdb_client = vdb_client
        self.llm = None
        self.api_key = Config.get_api_key()

    def conversation_context_retriever(self, character: str, input: str):
        context_retriever = self.vdb_client.get_context_retriever(character)
        context_lines = context_retriever.get_relevant_documents(input)
        for context_line_doc in context_lines:
            page_content = context_line_doc.page_content
            metadata = context_line_doc.metadata
            self.logger.debug(f"Context line: {page_content}, Metadata: {metadata}")
        return context_lines


    def imitate(
        self,
        input_text: str,
        character: str
    ) -> str:
        
        if not self.vdb_client.get_personal_retriever():
            retrieved_data = RunnableParallel({
                "character_context": self.vdb_client.get_character_retriever(character),
                "input": RunnablePassthrough()
            }).invoke(input_text)

        else:
            retrieved_data = RunnableParallel({
                "character_context": self.vdb_client.get_character_retriever(character),
                "personal_context": self.vdb_client.get_personal_retriever(),
                "input": RunnablePassthrough()
            }).invoke(input_text)

        context_retriever = self.vdb_client.get_context_retriever(character)
        relevant_docs = context_retriever.get_relevant_documents(input_text)

        # Step 3: Extract surrounding lines using metadata
        surrounding_lines = []
        for doc in relevant_docs:
            metadata = doc.metadata
            if "index" in metadata:
                index = metadata["index"]
                # Retrieve surrounding lines from the original dataframe
                character_df = self.vdb_client.df[self.vdb_client.df['speaker'] == character]
                start_index = max(0, index - 2)  # Get 2 lines before
                end_index = min(len(character_df), index + 3)  # Get 2 lines after
                surrounding_lines.extend(character_df.iloc[start_index:end_index]['text'].tolist())

        # Combine surrounding lines into a single string
        surrounding_lines_text = "\n".join(surrounding_lines)

        # Step 4: Add the surrounding lines to the retrieved data
        retrieved_data["surrounding_lines"] = surrounding_lines

        if not self.api_key:
            raise ValueError("API key is required for Gemini backend.")
        else:
            self.llm = ChatGoogleGenerativeAI(
                model="gemini-2.0-flash-001",
                temperature=0.5,
                max_tokens=512,
                max_retries=2,
                api_key=self.api_key
            )
        
        try:
            if not self.vdb_client.get_personal_retriever():
                prompt_template = """Respond by mimicking the speech style shown by the STYLE EXAMPLES while incorporating relevant personal details. Try to avoid reusing the style examples.
        
                <STYLE EXAMPLES>
                {character_context}
                {surrounding_lines}
                </STYLE EXAMPLES>
                
                <INPUT>
                {input}
                </INPUT>
                
                Response:"""
            else:
                prompt_template = """Respond by mimicking the speech style shown by the STYLE EXAMPLES while incorporating relevant personal details. Try to avoid reusing the style examples.
            
                <STYLE EXAMPLES>
                {character_context}
                {surrounding_lines}
                </STYLE EXAMPLES>
                
                
                <PERSONAL KNOWLEDGE>
                {personal_context}
                </PERSONAL KNOWLEDGE>

                
                <INPUT>
                {input}
                </INPUT>
                
                Response:"""
            
            # print(f"Prompt template: {prompt_template}")
            chain = (
                ChatPromptTemplate.from_template(prompt_template)
                | self.llm
            )

            response = {
                'Retrieved Data': retrieved_data,
                'Generated Response': chain.invoke({**retrieved_data, "character": character}).text()
            }
            return response
            
        except Exception as e:
            self.logger.error(f"Generation failed: {str(e)}")
            response = {
                'Error Response': f"Apologies, I couldn't generate a response. Error: {str(e)}"
            }
            return response
            