
from langchain_openai import ChatOpenAI
import uuid
from datetime import datetime
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import PydanticOutputParser
from core.prompts import STORY_PROMPT
from core.models import StoryLLMResponse, StoryNodeLLM
from dotenv import load_dotenv

load_dotenv()

class StoryGenerator:
    @classmethod
    def _get_llm(cls):
        return ChatOpenAI(model="gpt-4-turbo")
    
    @classmethod
    def generate_story(cls, db, session_id: str, theme: str = "fantasy", story_id: str = None, user_id: str = None) -> dict:
        import copy
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

        raw_response = llm.invoke(prompt.invoke({}))

        response_text = raw_response
        if hasattr(raw_response, "content"):
            response_text = raw_response.content

        story_structure = story_parser.parse(response_text)

        # --- Flatten the story tree into all_nodes and assign unique IDs ---
        def flatten_nodes(node, all_nodes, parent_id=None):
            node_id = str(uuid.uuid4())
            node_dict = node.model_dump() if hasattr(node, 'model_dump') else copy.deepcopy(node)
            node_dict['id'] = node_id
            # Rename keys for frontend compatibility
            node_dict['is_ending'] = node_dict.pop('isEnding', False)
            node_dict['is_winning_ending'] = node_dict.pop('isWinningEnding', False)
            # Process options recursively
            options = node_dict.get('options')
            if options:
                new_options = []
                for opt in options:
                    opt_dict = opt.model_dump() if hasattr(opt, 'model_dump') else copy.deepcopy(opt)
                    next_node = opt_dict.get('nextNode')
                    if next_node:
                        next_node_id = flatten_nodes(next_node, all_nodes, parent_id=node_id)
                        opt_dict['node_id'] = next_node_id
                        del opt_dict['nextNode']
                    new_options.append(opt_dict)
                node_dict['options'] = new_options
            all_nodes[node_id] = node_dict
            return node_id

        all_nodes = {}
        root_node_id = flatten_nodes(story_structure.rootNode, all_nodes)

        # Cosmos DB: Build story document as dict
        story_doc = {
            "id": story_id or str(uuid.uuid4()),
            "title": story_structure.title,
            "session_id": session_id,
            "created_at": datetime.now().isoformat(),
            "root_node": all_nodes[root_node_id],
            "all_nodes": all_nodes,
        }
        if user_id:
            story_doc["user_id"] = user_id
        return story_doc

