# Todo Evolution Project

A 5-phase evolution of a Todo List Manager, demonstrating Spec-Driven Development (SDD) principles with stateless architecture and AI integration.

## Project Overview

This project implements a Todo List Manager that evolves through 5 phases, from a simple console application to a cloud-native, event-driven system. Each phase builds upon the previous while maintaining strict adherence to stateless architecture principles.

### Phases

| Phase | Description | Status |
|-------|-------------|--------|
| I | In-Memory Console Application | ✅ Complete |
| II | Full-Stack Web Application with Authentication | ✅ Complete |
| III | AI Chatbot Integration (Stateless) | ✅ Complete |
| IV | Kubernetes Deployment | Planned |
| V | Cloud-Native with Event-Driven Architecture | Planned |

## Phase I - In-Memory Console Todo App

A console-based Todo List Manager with in-memory storage.

### Features

- Add new tasks with title and optional description
- List all tasks with completion status
- Update task title and description
- Delete tasks
- Mark tasks as complete/incomplete
- Menu-driven interface with input validation

### Installation

```bash
# No external dependencies required
# Requires Python 3.11+
```

### Running the Application

```bash
python todo_console/main.py
```

### Usage

1. Run the application
2. Choose from the menu:
   - 1: Add Task
   - 2: Update Task
   - 3: Delete Task
   - 4: List Tasks
   - 5: Mark Task as Complete
   - 6: Exit
3. Follow the prompts for each operation

### Project Structure

```
todo_console/
├── __init__.py
├── main.py                 # Application entry point
├── models/
│   ├── __init__.py
│   └── task.py            # Task data model
├── services/
│   ├── __init__.py
│   ├── storage.py         # In-memory task storage
│   └── operations.py      # Business logic layer
└── cli/
    ├── __init__.py
    ├── input.py           # Input validation
    ├── menu.py            # Menu display and navigation
    └── render.py          # Console output rendering
```

## Phase II - Full-Stack Web Application with Authentication

A full-stack web application with persistent data storage and user authentication.

### Features

- All Phase I functionality enhanced with persistence
- User authentication via Better Auth
- JWT token-based security model
- User-scoped task access control
- REST API with JSON data exchange
- Responsive web interface using Next.js
- PostgreSQL database with SQLModel ORM

### Architecture

- **Backend**: FastAPI with SQLModel ORM connecting to Neon PostgreSQL
- **Frontend**: Next.js with authentication context management
- **Security**: JWT token verification per-request
- **Data Isolation**: User-scoped access controls at API level
- **Stateless**: No server-side session storage

## Phase III - AI Chatbot Integration (Stateless)

A natural language interface for managing Todo tasks using AI agents and MCP tools.

### Stateless Architecture

The AI chatbot operates in **STRICT STATELESS MODE**:

- **No conversation memory**: Each request is processed independently
- **No session state**: No conversation history stored on server
- **No caching**: Each operation is executed fresh
- **Per-request authentication**: JWT tokens validated for each interaction
- **No filtering or search**: MCP tools return all user data without processing

All stateful behavior is explicitly deferred to Phase V.

### Security Model

- **JWT Per-Request Validation**: Authentication tokens verified for every AI interaction
- **User Isolation**: Strict enforcement of user boundaries via authentication
- **Token Propagation**: JWT tokens passed from frontend → agent → backend APIs
- **MCP Tools**: Secure backend operations with user-scoped validation

### Features

- Natural language task creation, listing, updating, deletion, and completion
- OpenAI Agent integration for intent detection and tool orchestration
- MCP tools for secure backend operations (create_task, list_tasks, update_task, delete_task, complete_task)
- JWT token-based authentication and user isolation
- Chat interface integrated into the web dashboard
- Error handling with clarification for ambiguous requests

### Architecture

- **Stateless Agent**: AI agent maintains no persistent data
- **MCP Tools**: All operations routed through MCP tools to Phase II backend
- **JWT Propagation**: Authentication tokens passed from frontend → agent → backend
- **User Isolation**: Strict enforcement of user boundaries via authentication

### Usage

1. Navigate to the dashboard
2. Click "AI Chat Assistant" to open the chat interface
3. Use natural language to manage tasks:
   - "Add a task to buy groceries"
   - "Show me my tasks"
   - "Mark the meeting preparation task as done"
   - "Update my project deadline task"

### Project Structure

```
backend/src/ai_chatbot/
├── agents/                 # OpenAI agent implementations
│   ├── openai_agent.py    # Main AI agent
│   └── tool_chain.py      # Tool chaining within a single request
├── tools/                 # MCP tool implementations
│   ├── create_task_tool.py
│   ├── list_tasks_tool.py
│   ├── update_task_tool.py
│   ├── delete_task_tool.py
│   ├── complete_task_tool.py
│   └── registration.py    # Tool registration manager
├── processors/            # Input/output processing
│   └── input_processor.py
├── services/              # Backend API clients
│   └── api_client.py
├── utils/                 # Utility functions
│   ├── nlp_utils.py       # Natural language processing
│   ├── response_formatter.py
│   ├── validation.py      # Parameter validation
│   ├── jwt_handler.py     # JWT token handling
│   └── logging.py         # Logging utilities
└── config.py              # Configuration settings

backend/src/api/
└── ai_chat.py             # API endpoints for chat functionality

frontend/src/components/chat/
└── chat-interface.js      # Frontend chat component
```

### MCP Tool Specifications

- **create_task**: Create new tasks with title and optional description only
- **list_tasks**: Return ALL user tasks (NO filtering, NO search)
- **update_task**: Update task details (title and/or description only)
- **delete_task**: Delete owned task
- **complete_task**: Toggle completion

## Phase IV - Kubernetes Deployment (Planned)

Containerized deployment using Kubernetes with Helm charts for orchestration.

## Phase V - Cloud-Native with Event-Driven Architecture (Planned)

Advanced cloud-native architecture with Kafka event streaming and Dapr for distributed systems patterns. All stateful intelligence and advanced features will be implemented in this phase.

## Governance

All code follows Spec-Driven Development principles:
- Code generated from specifications only
- Manual coding prohibited
- Constitution-first governance
- All phases must comply with project constitution
- Stateless System Rule enforced from Phase III onward

## Contributing

This project follows Spec-Driven Development:
1. All features must start with specification (`/sp.specify`)
2. Planning before implementation (`/sp.plan`)
3. Tasks generated from plan (`/sp.tasks`)
4. Implementation executed via `/sp.implement`

## License

Spec-Driven Development - Internal Project

---

**Built with Spec-Driven Development principles**
**Constitution-first governance**
**Stateless architecture with JWT authentication**
**Python 3.11+**
