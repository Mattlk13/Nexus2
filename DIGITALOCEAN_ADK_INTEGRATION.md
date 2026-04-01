# DigitalOcean Agent Development Kit (ADK) Integration for NEXUS

## Overview

NEXUS now includes full integration with DigitalOcean's Agent Development Kit (ADK), enabling you to build, test, and deploy production-ready AI agents directly from the platform.

## Features

### 🤖 Agent Management
- **Create Agents**: Initialize new AI agents with LangGraph workflows
- **Test Locally**: Test agent responses before deployment
- **Deploy to DigitalOcean**: One-click deployment to managed infrastructure
- **Monitor Status**: Track agent status, deployments, and performance

### 🎯 Supported Models
- OpenAI GPT OSS 120B
- Meta Llama 3.1 405B Instruct
- Anthropic Claude 3.5 Sonnet
- Custom model support

### 🔧 Capabilities
- Multi-agent orchestration
- Knowledge base integration (RAG)
- Custom tools and functions
- Guardrails and safety
- Production-grade deployment

## Setup

### 1. Install ADK CLI (if not already installed)

```bash
# The gradient CLI is required for ADK
pip install gradient-sdk
```

### 2. Configure API Keys

Add these environment variables to `/app/backend/.env`:

```env
# DigitalOcean ADK Configuration
GRADIENT_MODEL_ACCESS_KEY=your_gradient_model_key
DIGITALOCEAN_API_TOKEN=your_do_api_token
```

#### Getting Your Keys:

**Gradient Model Access Key:**
1. Go to https://cloud.digitalocean.com/ai/serverless-inference
2. Scroll to "Model Access Keys"
3. Click "Create Access Key" or copy existing one

**DigitalOcean API Token:**
1. Go to https://cloud.digitalocean.com/account/api/tokens
2. Click "Generate New Token"
3. Configure scopes:
   - `genai`: create, read, update, delete
   - `project`: read
4. Name it "NEXUS ADK Integration"
5. Copy the token (shown only once!)

### 3. Restart Backend

```bash
sudo supervisorctl restart backend
```

## Usage

### Access Agent Studio

Navigate to: `http://localhost:3000/agent-studio`

Or in production: `https://your-domain.com/agent-studio`

### Create Your First Agent

1. **Click "Create Agent"**
2. **Fill in details:**
   - Agent Name: `my-first-agent`
   - Description: What your agent does
   - Model: Choose from available models
   - Deployment: `development` or `production`
3. **Click "Create Agent"**

The agent is created with:
- LangGraph workflow template
- FastAPI entrypoint
- Configuration files
- Environment setup

### Test Agent Locally

1. **Select your agent** from the list
2. **Enter a test prompt** in the input field
3. **Click "Test Agent"**
4. **View the response**

### Deploy to DigitalOcean

1. **Click the 🚀 Deploy button** on your agent
2. **Confirm deployment**
3. **Wait 1-5 minutes** for deployment
4. **Get your deployment URL**

Your agent is now live and accessible via API!

### Call Deployed Agent

```bash
curl -X POST \
  -H "Authorization: Bearer $DIGITALOCEAN_API_TOKEN" \
  -H "Content-Type: application/json" \
  "https://agents.do-ai.run/v1/abc123/development/run" \
  -d '{"prompt": "Hello agent!"}'
```

## API Endpoints

### Get ADK Status
```http
GET /api/adk/status
```

### Create Agent
```http
POST /api/adk/agents/create
Content-Type: application/json

{
  "agent_name": "my-agent",
  "deployment_name": "development",
  "description": "My custom AI agent",
  "model": "openai-gpt-oss-120b"
}
```

### List Agents
```http
GET /api/adk/agents
```

### Get Agent Details
```http
GET /api/adk/agents/{agent_name}
```

### Test Agent
```http
POST /api/adk/agents/test
Content-Type: application/json

{
  "agent_name": "my-agent",
  "prompt": "What can you do?"
}
```

### Deploy Agent
```http
POST /api/adk/agents/deploy
Content-Type: application/json

{
  "agent_name": "my-agent",
  "deployment_name": "production"
}
```

### Delete Agent
```http
DELETE /api/adk/agents/{agent_name}
```

## Agent Structure

Each agent is created with this structure:

```
agent_workspace/
└── my-agent/
    ├── main.py              # Entrypoint (modify this!)
    ├── .gradient/
    │   └── agent.yml        # Config
    ├── requirements.txt     # Dependencies
    ├── .env                 # API keys
    ├── agents/              # Custom agent code
    ├── tools/               # Custom tools
    └── agent_metadata.json  # NEXUS metadata
```

## Customizing Agents

### Edit Agent Code

1. **Locate agent:** `/app/backend/agent_workspace/{agent_name}/{agent_name}/main.py`
2. **Modify the workflow:**

```python
from langgraph.graph import StateGraph, START, END
from langchain_core.messages import HumanMessage, AIMessage

def process_input(state):
    """Add your custom logic here"""
    messages = state.get("messages", [])
    last_message = messages[-1]
    
    # Your agent logic
    response = "Custom response"
    
    messages.append(AIMessage(content=response))
    return {"messages": messages}

# Create workflow
workflow = StateGraph(AgentState)
workflow.add_node("process", process_input)
workflow.add_edge(START, "process")
workflow.add_edge("process", END)

agent = workflow.compile()
```

3. **Test locally** before deploying
4. **Deploy** when ready

### Add Custom Tools

Create tools in `tools/` directory:

```python
# tools/calculator.py
def calculate(expression: str) -> float:
    """Evaluate a mathematical expression"""
    return eval(expression)
```

Import and use in your agent:

```python
from tools.calculator import calculate

def process_with_tools(state):
    # Use custom tool
    result = calculate("2 + 2")
    # ...
```

## Advanced Features

### Multi-Agent Orchestration

```python
from langgraph.graph import StateGraph

# Create multiple agents
agent1 = create_analyst_agent()
agent2 = create_writer_agent()

# Orchestrate them
workflow = StateGraph(AgentState)
workflow.add_node("analyst", agent1)
workflow.add_node("writer", agent2)
workflow.add_edge("analyst", "writer")
```

### Knowledge Base (RAG)

```python
from langchain_community.vectorstores import FAISS
from langchain_openai import OpenAIEmbeddings

# Create knowledge base
embeddings = OpenAIEmbeddings()
vector_store = FAISS.from_documents(documents, embeddings)

def rag_process(state):
    query = state["messages"][-1].content
    docs = vector_store.similarity_search(query, k=3)
    # Use docs in your response
    pass
```

### Guardrails

```python
def check_safety(state):
    """Add safety checks"""
    message = state["messages"][-1].content
    
    if contains_sensitive_info(message):
        return {"error": "Sensitive information detected"}
    
    return state
```

## Monitoring & Logs

### View Logs
```http
GET /api/adk/agents/{agent_name}/logs
```

### DigitalOcean Dashboard

Monitor your deployed agents:
1. Go to https://cloud.digitalocean.com/ai/agents
2. View deployment status
3. Check metrics and logs
4. Manage scaling

## Cost Estimate

### Free Tier
- Development testing: FREE
- Local development: FREE

### Production
- **Model Inference**: Pay-per-use
  - ~$0.0001 per 1K tokens
- **Deployment**: Included in DigitalOcean plan
- **Bandwidth**: First 1TB free

### Typical Costs
- **Small agent** (1K requests/day): ~$1-5/month
- **Medium agent** (10K requests/day): ~$10-30/month
- **Large agent** (100K requests/day): ~$100-300/month

## Troubleshooting

### Agent Creation Fails
- **Check API keys** are configured in `.env`
- **Verify gradient CLI** is installed: `gradient --version`
- **Check workspace permissions**: `/app/backend/agent_workspace/`

### Deployment Fails
- **Verify DO API token** has correct scopes
- **Check agent code** for syntax errors
- **Review requirements.txt** for missing dependencies

### Agent Not Responding
- **Check logs**: `/api/adk/agents/{name}/logs`
- **Test locally** before deploying
- **Verify model availability** in DigitalOcean

### CORS Errors
- Add agent domain to CORS_ORIGINS in backend `.env`

## Best Practices

### 1. Development Workflow
```
Create Agent → Test Locally → Deploy to Dev → Test in Dev → Deploy to Prod
```

### 2. Version Control
- Use deployment names: `v1`, `v2`, `production`
- Keep development and production separate
- Test thoroughly before production deploy

### 3. Error Handling
```python
def safe_process(state):
    try:
        # Your logic
        result = process_input(state)
        return result
    except Exception as e:
        logger.error(f"Error: {e}")
        return {"error": str(e)}
```

### 4. Performance
- Cache frequently used data
- Optimize prompt lengths
- Use streaming for long responses
- Implement rate limiting

### 5. Security
- Never commit API keys
- Use environment variables
- Implement authentication
- Add input validation
- Use guardrails

## Integration Examples

### Slack Bot
```python
from slack_sdk import WebClient

def slack_agent(state):
    message = state["messages"][-1].content
    response = generate_response(message)
    
    slack_client.chat_postMessage(
        channel=channel_id,
        text=response
    )
```

### API Integration
```python
import requests

def api_agent(state):
    # Call external API
    data = requests.get("https://api.example.com/data").json()
    
    # Process with agent
    response = process_with_context(state, data)
    return response
```

### Database Integration
```python
from motor.motor_asyncio import AsyncIOMotorClient

async def db_agent(state):
    # Query database
    data = await db.collection.find_one({...})
    
    # Use in agent response
    response = generate_with_data(state, data)
    return response
```

## Resources

### Documentation
- **DigitalOcean ADK**: https://docs.digitalocean.com/products/ai-platform/adk/
- **LangGraph**: https://langchain-ai.github.io/langgraph/
- **LangChain**: https://python.langchain.com/

### Support
- **NEXUS Issues**: GitHub repository
- **DigitalOcean Support**: https://cloud.digitalocean.com/support

### Community
- **LangChain Discord**: Join for agent development help
- **DigitalOcean Community**: Forums and tutorials

## Next Steps

1. **Create your first agent** in Agent Studio
2. **Test it locally** with various prompts
3. **Deploy to development** environment
4. **Integrate with your app** via API
5. **Monitor and optimize** performance
6. **Scale to production** when ready

---

**🎉 You're ready to build production AI agents with NEXUS!**

For questions or issues, refer to the troubleshooting section or check the logs.
