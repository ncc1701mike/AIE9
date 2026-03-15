

## # Session 17: Model Context Protocol (MCP) & Agent-to-Agent (A2A) Protocol


| Session Sheet                                                         | Recording                                                                                                                                             | Slides                                                                                                                                                                             | Repo          | Homework                                                                                   | Feedback                                             |
| --------------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------- | ------------------------------------------------------------------------------------------ | ---------------------------------------------------- |
| [MCP Servers & A2A](../00_Docs/Session_Sheets/17_MCP_Servers_and_A2A) | [Recording!](https://us02web.zoom.us/rec/share/_iJT-kZiYacyz23fjU3N7w7mZIUFJqGXV48RDqCkCY3avsmngKtzK0SNs0I7k74.xICq6NSv6l6GqAFU) passcode: `fJ9tx4h.` | [Session 17 Slides](https://www.canva.com/design/DAG-ELapG4g/6vDMm63RBwKVsSZvheorVA/edit?utm_content=DAG-ELapG4g&utm_campaign=designshare&utm_medium=link2&utm_source=sharebutton) | You are here! | [(Optional) Session 17 Assignment: MCP Servers & A2A](https://forms.gle/qtjQFfoEF8aykTWy5) | [Feedback 3/12](https://forms.gle/sJwD1a6LLn9NU9s48) |


---

## 📚 Useful Resources

**MCP (Model Context Protocol)**

- [MCP Official Docs](https://modelcontextprotocol.io/) — Spec, tutorials, and guides
- [MCP-UI](https://mcpui.dev/) — Official standard for interactive UI in MCP
- [MCP Auth Guide (Auth0)](https://auth0.com/blog/mcp-specs-update-all-about-auth/) — Deep dive into MCP auth spec updates

**A2A (Agent-to-Agent Protocol)**

- [A2A Official Docs](https://a2a-protocol.org/latest/) — Spec and guides
- [A2A GitHub Repo](https://github.com/a2aproject/A2A) — Protocol spec and implementations
- [Announcing A2A (Google Blog)](https://developers.googleblog.com/en/a2a-a-new-era-of-agent-interoperability/) — Protocol vision and motivation

**MCP vs A2A**

- [A2A and MCP (Official)](https://a2a-protocol.org/latest/topics/a2a-and-mcp/) — How they complement each other

---

# Running the MCP Server

### 1. Install dependencies

```bash
uv sync
```

### 2. Set up environment variables

Copy the example env file and fill in your OpenAI API key:

```bash
cp .env.example .env
```

### 3. Run the MCP server locally

```bash
uv run server.py
```

The server will start on `http://localhost:8000`.

### 4. Expose the server with ngrok (for remote/Claude Desktop access)

In a separate terminal, start an ngrok tunnel:

```bash
ngrok http 8000
```

Copy the ngrok forwarding URL (e.g. `https://xxxx-xx-xx-xx-xx.ngrok-free.app`) and restart the server with it:

```bash
ISSUER_URL=https://xxxx-xx-xx-xx-xx.ngrok-free.app uv run server.py
```

> **Note:** The `ISSUER_URL` must match the public URL clients use to reach the server, otherwise OAuth authentication will fail.

---

# Build 🏗️

In today's assignment, we'll be building an MCP server with OAuth authentication — a cat shop application that exposes tools for browsing products, managing a cart, and checking out.

- 🤝 Breakout Room #1
  - Set up the MCP server with OAuth and the product database
  - Explore the MCP tools: `list_products`, `get_product`, `add_to_cart`, `view_cart`, `remove_from_cart`, `checkout`
- 🤝 Breakout Room #2
  - Connect an MCP client to the server
  - Build an end-to-end interaction flow using the MCP tools

# Ship 🚢

The completed MCP server and client integration!

### Deliverables

- A short Loom of either:
  - the MCP server you built and a demo of the client interacting with it; or
  - the notebook you created for the Advanced Build

# Share 🚀

Make a social media post about your final application!

### Deliverables

- Make a post on any social media platform about what you built!

Here's a template to get you started:

```
🚀 Exciting News! 🚀

I am thrilled to announce that I have just built and shipped an MCP server with OAuth authentication! 🎉🤖

🔍 Three Key Takeaways:
1️⃣
2️⃣
3️⃣

Let's continue pushing the boundaries of what's possible in the world of AI and tool integration. Here's to many more innovations! 🚀
Shout out to @AIMakerspace !

#MCP #ModelContextProtocol #OAuth #Innovation #AI #TechMilestone

Feel free to reach out if you're curious or would like to collaborate on similar projects! 🤝🔥
```

# Submitting Your Homework [OPTIONAL]

## Main Homework Assignment

Follow these steps to prepare and submit your homework assignment:

1. Review the MCP server code in `server.py` and the `app/` directory
2. Run the MCP server locally using `uv run server.py`
3. Connect to the server using an MCP client (e.g., Claude Desktop, or a custom client)
4. Test all available tools: browsing products, adding to cart, viewing cart, removing items, and checkout
5. Record a Loom video reviewing what you have learned from this session

## Questions

### ❓ Question #1:

Why is OAuth important for MCP servers, and what security considerations should you keep in mind when exposing tools to AI clients?

#### ✅ Answer:

OAuth matters for MCP servers because the tools that get exposed aren't passive data endpoints — they're dyanamic actions, e.g. they modify state on behalf of the user (checkout, add_to_cart, etc). Without OAuth, any client that sees an open ngrok URL could call those tools. OAuth ensures that tool calls are tied to an authenticated identity and that the client has been explicitly granted permission.

Key security considerations when exposing MCP tools to AI clients:

Scope limiting — only grant the minimum scope needed. Production systems should ideally have fine-grained scopes like cart:write or checkout:execute so a read-only client can't trigger purchases.

Token expiry — access tokens here expire in 1 hour, refresh tokens in 24 hours. Short-lived tokens limit the blast radius if a token gets leaked.

PKCE — This code challenge/verifier pair in the client prevents authorization code interception. Critical for public clients that can't store client secrets safely.

ISSUER_URL matching — The issuer URL must exactly match the public URL. A mismatch breaks token validation, which is an intended security feature to prevent token reuse across environments.

AI-specific risk: 
Prompt injection — AI clients could be manipulated by crafted tool responses to call destructive tools. Rate limiting and scope separation are the bulwark against this.

Ngrok in production — ngrok tunnels are fine for dev/prototyping but never for production. Real deployments should utlilize proper domains with TLS termination and reverse proxy.

### ❓ Question #2:

What is the Agent-to-Agent (A2A) protocol, and how does it differ from MCP in terms of purpose and architecture? When would you choose A2A over MCP?

#### ✅ Answer:

A2A (Agent-to-Agent protocol) is the format by which agents communitate with other agents. Essentially instead of implementing one model that calls a tool, multiple autonomous agents are implemented, where each agent can delegate tasks to each other, negotiate capabilities, and collaborate on multi-step workflows. Each agent advertises what it can do via an "agent card", and agents can discover and invoke each other dynamically.

MCP (Model Context Protocol) is the standardized format by which AI models are connected to tools and resources — databases, APIs, file systems, actions. At its most basic, a model acts as a single agent reaching out to external capabilities. The server is passive- it exposes tools and waits to be called. 

Key architectural differences:

```
                         MCP                  A2A
```

Primary relationship     Model ↔ Tool        Agent ↔ Agent           Communication style      Request/response    Task delegation, streaming, async Who initiates            Client model        Either agent
State                    Stateless tools     Agents maintain task state Discovery                Tool list           Agent cards

When to choose A2A over MCP:
A2A should be selected when agents with specialized roles are needed to collaborate, e.g. a research agent that delegates to a data analysis agent, which delegates to a visualization agent, where each has its own reasoning loop, memory, and capabilities. MCP would require one model to orchestrate everything itself, which doesn't scale well for complex multi-domain tasks.
MCP should be selected in the case of a single agent that needs to reach out to external tools or services, which is most common.
In practice, the two are complementary: an A2A agent network might use MCP internally so each individual agent can access tools.

## Activity 1: Extend the MCP Server

Add at least one new tool to the cat shop MCP server (e.g., `search_products`, `update_cart_quantity`, or `get_order_history`). Ensure the new tool integrates properly with the existing database and OAuth authentication. Demo the new tool through an MCP client and include it in your Loom video.

## Advanced Activity: Build a Custom MCP Client

Build a custom MCP client that connects to the cat shop server over Streamable HTTP, authenticates via OAuth, and orchestrates a multi-step shopping flow (browse → add to cart → checkout). Compare the developer experience of MCP-based tool integration vs. traditional REST API calls.

Include your findings and a demo in your Loom video.