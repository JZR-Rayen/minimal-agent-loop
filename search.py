
from ddgs import DDGS

def search_web(query):
    results = DDGS().text(query, max_results=3)
    return results

if __name__ == "__main__":
    print(search_web("LangGraph Python GitHub"))
