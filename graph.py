from langgraph.graph import StateGraph
from typing import TypedDict
from agents.extractor import extract_task

class State(TypedDict):
    text: str
    task: str

def extractor_node(state):
    result = extract_task(state["text"])
    return {"task": result}

graph = StateGraph(State)

graph.add_node("extract", extractor_node)

graph.set_entry_point("extract")

workflow = graph.compile()