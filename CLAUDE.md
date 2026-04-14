# 🤖 Microsoft Agent Framework — Learning Guide
> **Status:** v1.0 GA (released 2026-04-02) | **Stack:** C# / .NET 10 | **Your guide:** Claude Code

---

## 🗺️ Big Picture First

Think of the framework as a **three-layer cake**:

```
┌──────────────────────────────────────────────────────┐
│  WORKFLOWS  → Graph-based, multi-agent orchestration │  ← deterministic control
├──────────────────────────────────────────────────────┤
│  AGENTS     → Individual LLM-powered workers         │  ← reasoning + tool use
├──────────────────────────────────────────────────────┤
│  INFRA      → Model clients, sessions, middleware    │  ← plumbing
└──────────────────────────────────────────────────────┘
```

**Mental model:** An `AIAgent` = instructions + model client + optional tools.
A `Workflow` = a graph connecting multiple agents (and plain functions) with routing rules.

> 💡 If you can write a plain C# function to handle something, do that. Use an agent only when you need LLM reasoning.

---

## 🧬 Key Concepts (Glossary)

| Term | Plain English |
|---|---|
| `AIAgent` | The core class — wraps an LLM chat client with a role and tools |
| `AgentSession` | Conversation state — keeps multi-turn history between calls |
| `AIFunction` / `[Description]` | A C# method exposed to the LLM as a callable tool |
| `Middleware` | Intercepts agent inputs/outputs (logging, safety, retry) |
| `AgentWorkflowBuilder` | Fluent builder for connecting agents in graphs |
| `Handoff` | One agent transfers full control to the next (not just calling it) |
| `MCP Server` | External tool source via Model Context Protocol |
| `DefaultAzureCredential` | Azure Identity auth — works locally (`az login`) and in prod |

---

## 📦 Setup

### Prerequisites
- .NET 10 SDK
- Azure CLI (`az login`) OR a GitHub Personal Access Token

### Packages (choose your model provider)

```bash
# Option A: Azure OpenAI (enterprise)
dotnet add package Azure.AI.OpenAI --prerelease
dotnet add package Azure.Identity
dotnet add package Microsoft.Agents.AI.OpenAI --prerelease

# Option B: GitHub Models (free for dev — no Azure needed)
dotnet add package OpenAI
dotnet add package Microsoft.Extensions.AI.OpenAI --prerelease
dotnet add package Microsoft.Extensions.AI
dotnet add package Microsoft.Agents.AI --prerelease
```

### Environment Variables

```bash
# Azure OpenAI
AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com/

# GitHub Models
GITHUB_TOKEN=your_pat_token_here
```

> ⚠️ Agent Framework does NOT auto-load .env files. Set vars in your shell or use `dotnet user-secrets`.

---

## 1️⃣ Hello World — The Simplest Agent

**Goal:** One agent, one question, one answer.

```csharp
// HelloWorld/Program.cs
using Azure.AI.OpenAI;
using Azure.Identity;
using Microsoft.Agents.AI;

// 1. Create a model client pointing to Azure OpenAI
var azureClient = new AzureOpenAIClient(
    new Uri(Environment.GetEnvironmentVariable("AZURE_OPENAI_ENDPOINT")!),
    new AzureCliCredential());        // uses `az login` — no keys in code!

// 2. Wrap it as an AIAgent with a system prompt
AIAgent agent = azureClient
    .GetChatClient("gpt-4o-mini")    // your deployment name
    .AsAIAgent(instructions: "You are a friendly assistant. Keep answers brief.");

// 3. Run a single turn
string response = await agent.RunAsync("What is the largest city in France?");
Console.WriteLine(response);
// → "Paris is the largest city in France."
```

**What just happened:**
- `AzureOpenAIClient` = model provider connection
- `.AsAIAgent()` = wraps the chat client with the instructions as a system message
- `.RunAsync()` = one-shot call, returns the text response

---

## 2️⃣ Common Pattern #1 — Agent With Tools (Function Calling)

**When to use:** The agent needs to fetch data, run code, or call APIs. The LLM *decides* when to call your function.

```csharp
// ToolAgent/Program.cs
using System.ComponentModel;
using Microsoft.Agents.AI;
using Microsoft.Extensions.AI;

// --- Define a tool as a plain static method ---
// The [Description] attribute tells the LLM WHEN to use this function
[Description("Returns the current weather for a given city.")]
static string GetWeather(
    [Description("The city name, e.g. 'La Paz'")] string city)
{
    // In real life: call a weather API here
    return $"It is sunny and 18°C in {city}.";
}

// --- Build the agent with the tool attached ---
AIAgent agent = azureClient
    .GetChatClient("gpt-4o-mini")
    .AsAIAgent(
        instructions: "You are a helpful weather assistant.",
        tools: [AIFunctionFactory.Create(GetWeather)]   // register the tool
    );

// The LLM will automatically call GetWeather() when relevant
string response = await agent.RunAsync("What's the weather like in La Paz?");
Console.WriteLine(response);
// → "It's currently sunny and 18°C in La Paz!"
```

**Key Points:**
- `AIFunctionFactory.Create()` converts any C# method into a tool the LLM can invoke
- The LLM uses the `[Description]` attributes to decide *if* and *how* to call the tool
- You can register **multiple tools** in the array — the agent picks the right one
- The framework handles the full tool-call roundtrip automatically

---

## 3️⃣ Common Pattern #2 — Multi-Turn Conversation (Session State)

**When to use:** Chat interfaces, interview bots, anything needing memory across turns.

```csharp
// SessionChat/Program.cs
using Microsoft.Agents.AI;

AIAgent agent = azureClient
    .GetChatClient("gpt-4o-mini")
    .AsAIAgent(instructions: "You are a helpful data engineering tutor.");

// Create a session — this holds conversation history
var session = agent.CreateSession();

Console.WriteLine("Chat with the agent (type 'exit' to quit)");

while (true)
{
    Console.Write("You: ");
    string? input = Console.ReadLine();
    if (string.IsNullOrEmpty(input) || input == "exit") break;

    // Pass the session so the agent remembers context
    string response = await agent.RunAsync(input, session: session);
    Console.WriteLine($"Agent: {response}");
}

// Example conversation:
// You: What is PySpark?
// Agent: PySpark is the Python API for Apache Spark...
// You: How does it compare to pandas?
// Agent: Unlike pandas, PySpark... [knows we were talking about PySpark!]
```

**Key Points:**
- `CreateSession()` returns an `AgentSession` that accumulates message history
- Pass `session:` on every `RunAsync()` call to maintain context
- Sessions are in-memory by default — for persistence, configure a session store
- Each session is isolated — multiple users get separate sessions

---

## 4️⃣ Common Pattern #3 — Multi-Agent Handoff Workflow

**When to use:** Complex tasks where specialized agents handle different phases.
Think: triage → specialist → summarizer pipelines.

```csharp
// HandoffWorkflow/Program.cs
using Microsoft.Agents.AI;
using Microsoft.Agents.AI.Workflows;

// --- Define specialized agents ---
AIAgent triageAgent = azureClient
    .GetChatClient("gpt-4o-mini")
    .AsAIAgent(instructions: @"
        You are a triage agent. Determine if the user's question is about:
        - 'data': route to the Data Expert
        - 'code': route to the Code Reviewer
        Say 'HANDOFF:DataExpert' or 'HANDOFF:CodeReviewer' to transfer.");

AIAgent dataExpert = azureClient
    .GetChatClient("gpt-4o-mini")
    .AsAIAgent(instructions: "You are a senior Data Engineer. Answer data questions in depth.");

AIAgent codeReviewer = azureClient
    .GetChatClient("gpt-4o-mini")
    .AsAIAgent(instructions: "You are a code review expert. Analyze and improve code snippets.");

// --- Wire them into a handoff workflow ---
var workflow = AgentWorkflowBuilder
    .CreateHandoffBuilderWith(triageAgent)              // entry point
    .WithHandoffs(triageAgent, [dataExpert, codeReviewer])
    .Build();

// --- Run the workflow ---
string result = await workflow.RunAsync(
    "Can you review this PySpark join and tell me if it has performance issues?");
Console.WriteLine(result);
// The triage agent routes to codeReviewer, which responds in depth
```

**Key Points:**
- `AgentWorkflowBuilder` builds a **directed graph** of agent connections
- In a handoff, the receiving agent takes **full control** — it's not a subcall
- The triage agent acts as a router — it decides who handles what
- Supported patterns: Sequential, Concurrent (fan-out), Handoff, Group Chat, Magentic-One
- Workflows support **checkpointing** — long-running flows survive interruptions

---

## 🧭 Learning Path

Follow this order when experimenting:

```
1. Hello World           → confirm your auth and packages work
2. Add a Tool            → understand AIFunctionFactory + [Description]
3. Add a Session         → build a chat loop with memory
4. Two-Agent Handoff     → triage → specialist pattern
5. Parallel Workflow     → fan-out to multiple agents, merge results
6. Add Middleware        → logging, retry, safety filtering
7. MCP Integration       → connect to external MCP servers
8. YAML Declarative      → define agents in config files
```

---

## 🔧 Useful Commands

```bash
# Create a new console project
dotnet new console -o MyAgentProject
cd MyAgentProject

# Add core packages
dotnet add package Microsoft.Agents.AI.OpenAI --prerelease
dotnet add package Azure.AI.OpenAI --prerelease
dotnet add package Azure.Identity

# Authenticate locally
az login

# Run
dotnet run
```

---

## 📚 Key References

| Resource | URL |
|---|---|
| Official Docs | https://learn.microsoft.com/en-us/agent-framework/ |
| GitHub Repo | https://github.com/microsoft/agent-framework |
| Samples Repo | https://github.com/microsoft/Agent-Framework-Samples |
| Hello World Codespace | https://github.com/microsoft/agent-framework (open in Codespaces) |
| Awesome List | https://github.com/webmaxru/awesome-microsoft-agent-framework |
| .NET Blog Intro | https://devblogs.microsoft.com/dotnet/introducing-microsoft-agent-framework-preview/ |

---

## 💡 Tips & Gotchas

- **Preview APIs:** v1.0 is GA but some features still evolve — pin your package versions
- **No .env loading:** Set vars in shell or use `dotnet user-secrets`
- **DefaultAzureCredential in prod:** Swap for `ManagedIdentityCredential` to avoid latency
- **Tool descriptions matter:** The LLM uses `[Description]` text to decide when to call tools — be specific
- **Handoff ≠ Tool call:** Handoff transfers control entirely; agent-as-tool keeps the caller in charge
- **GitHub Models = free for dev:** Use `GITHUB_TOKEN` to avoid Azure costs while learning

---

*Generated with Claude Code — April 2026*