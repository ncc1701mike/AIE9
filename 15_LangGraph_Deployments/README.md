## # Session 15: Build & Serve Agentic Graphs with LangGraph

### Prerequisites

Before starting, ensure you have the following:

- **Python 3.11+** installed
- An **OpenAI API Key**
- A **Tavily API Key**
- (Optional) **LangSmith** credentials for tracing

Create a `.env` file in this directory with your API keys:

1. Run `uv sync` to install dependencies.

# Build 🏗️

Run the repository and complete the following:

- 🤝 Breakout Room Part #1 — Building and serving your LangGraph Agent Graph
  - Task 1: Getting Dependencies & Environment
    - Configure `.env` (OpenAI, Tavily, optional LangSmith)
  - Task 2: Serve the Graph Locally
    - `uv run langgraph dev` (API on [http://localhost:2024](http://localhost:2024))
  - Task 3: Call the API from a different terminal
    - `uv run test_served_graph.py` (sync SDK example)
  - Task 4: Explore assistants (from `langgraph.json`)
    - `agent` → `simple_agent` (tool-using agent)
    - `agent_helpful` → `agent_with_helpfulness` (separate helpfulness node)
- 🤝 Breakout Room Part #2 — Using LangSmith Studio to visualize the graph
  - Task 1: Open Studio while the server is running
    - [https://smith.langchain.com/studio?baseUrl=http://localhost:2024](https://smith.langchain.com/studio?baseUrl=http://localhost:2024)
  - Task 2: Visualize & Stream
    - Start a run and observe node-by-node updates
  - Task 3: Compare Flows
    - Contrast `agent` vs `agent_helpful` (tool calls vs helpfulness decision)

🚧 Advanced Build 🚧 (OPTIONAL - *open this section for the requirements*)

> NOTE: This can be done in place of the Main Assignment

- Create and deploy a locally hosted MCP server with FastMCP.
- Extend your tools in `tools.py` to allow your LangGraph to consume the MCP Server.

When submitting, provide:

- Your Loom video link demonstrating the MCP server integration
- The GitHub URL to your completed Advanced Build

Have fun!

### Questions & Activities

#### Question 1:

What is the key architectural difference between the `simple_agent` and `agent_with_helpfulness` graphs? Specifically, explain how the helpfulness evaluation loop works and what mechanisms are in place to prevent it from running indefinitely.

##### Answer:

The Key architectural difference between simple_agent & agent_with_helpfulness is that simple_agent follows standard ReAct architecture, meaning the agent runs a loop between the model and the tool nodes until the model produces a final response after tool calls, or hits a recurssion/iteration limit.

By contrast, the agent_with_helpfulness wraps the core agent in an additional evaluation feedback loop, implementing what LangGraph calls the evaluator-optimizer workflow. This results in the LLM acting in two roles- a "Generator" which produces the agent's response, and an "Evaluator", which determines whether or not the agent has met the helpfulness threshold- then, a conditional edge node routes the response to the user if it was determined that the helpfulness threshold has been met, and if not the response is routed back to the Generator as context so the model can improve the response.  

There are two mechanisms LangGraph uses to prevent runaway looping- the first is called Conditional Termination, and is exactly the process described above where the conditional edge node evaluates the response as helpful or non-helpful and terminates or re-loops accordingly. The second is a LangGraph-provided configurable recurssion limit. 

#### Question 2:

What is the role of `langgraph.json` in the LangGraph Deployments? Describe each of its key fields and how the platform uses this file to discover and serve your graphs. 



Answer:

Langgraph.json is the deployment manifest for the entire app. It tells the platform what to build, how to build it, and what to make available for dev. It tells Langsmith where to find graphs and which runtime environment in which to build them. 

Key fields include 

Dependencies- Tells LangGraph where to find the python packages needed to run the graphs.

.Env- points to the environmental variables file used to access API Keys, model info, etc.

Python_version- specifies which Python version to use

Graphs- graphs are core. This is what Langsmith uses to locate and deploy compiled graphs.

Assistants- these are the instantiation of the agents themselves, and these represent the primary nodes in the deployed graphs.



#### Activity #1:

Create your own agent graph! Build a new graph in `app/graphs/` with a custom evaluation node (e.g., a vibe checker, a fact verifier, a summarizer — get creative!). Register it in `langgraph.json`, serve it with `uv run langgraph dev`

##### Answer:

# Ship 🚢

- The completed notebook.
- 5min. Loom Video

# Share 🚀

- Walk through your notebook and explain what you've completed in the Loom video
- Make a social media post about your final application and tag @AIMakerspace
- Share 3 lessons learned
- Share 3 lessons not learned

# Submitting Your Homework

### Main Homework Assignment

Follow these steps to prepare and submit your homework:

1. Pull the latest updates from upstream into the main branch of your AIE9 repo:
  - *(You should have completed this process already.)* For your initial repo setup, see [Initial_Setup](https://github.com/AI-Maker-Space/AIE9/tree/main/00_Docs/Prerequisites/Initial_Setup)
    - To get the latest updates from AI Makerspace into your own AIE9 repo, run the following commands:
    ```
    git checkout main
    git pull upstream main
    git push origin main
    ```
2. **IMPORTANT:** Start Cursor from the `15_LangGraph_Platform` folder (you can also use the *File -> Open Folder* menu option of an existing Cursor window)
3. Answer Questions 1 - 2 using the `##### Answer:` markdown cell below them in the README
4. Complete Activity #1 in the README
5. Add, commit and push your modified files to your GitHub repository.

When submitting your homework, provide:

- Your Loom video link
- The GitHub URL to the `15_LangGraph_Platform` folder on your assignment branch

