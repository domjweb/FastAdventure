from langchain_openai import ChatOpenAI
import uuid
from datetime import datetime
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import PydanticOutputParser
from backend.core.prompts import STORY_PROMPT
from backend.core.models import StoryLLMResponse, StoryNodeLLM
from dotenv import load_dotenv

load_dotenv()

class StoryGenerator:
    @classmethod
    def _get_llm(cls):
        return ChatOpenAI(model="gpt-4-turbo")
    
    @classmethod
    def generate_story(cls, db, session_id: str, theme: str = "fantasy") -> dict:
        llm = cls._get_llm()
        story_parser = PydanticOutputParser(pydantic_object=StoryLLMResponse)

        prompt = ChatPromptTemplate.from_messages([
            (
                "system",
                STORY_PROMPT
            ),
            (
                "human",
                f"Create the story with this theme: {theme}"
            )
        ]).partial(format_instructions=story_parser.get_format_instructions())

        # The correct way to invoke the LLM and prompt may depend on your langchain version
        # Here is a typical pattern:
        raw_response = llm.invoke(prompt.invoke({}))

        response_text = raw_response
        if hasattr(raw_response, "content"):
            response_text = raw_response.content

        story_structure = story_parser.parse(response_text)
        # Cosmos DB: Build story document as dict
        story_doc = {
            "id": str(uuid.uuid4()),
            "title": story_structure.title,
            "session_id": session_id,
            "created_at": datetime.now().isoformat(),
            "rootNode": story_structure.rootNode.model_dump() if hasattr(story_structure.rootNode, 'model_dump') else story_structure.rootNode,
        }
        # Optionally, save to Cosmos DB here if needed
        return story_doc
    