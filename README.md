# DocBot Platform

An AI-powered interactive documentation chatbot platform that transforms technical documentation into conversational, guided experiences.

## What It Does

DocBot takes complex technical documentation and creates an intelligent chatbot that:
- Guides users through workflows step-by-step
- Answers questions in natural language
- Generates interactive visualizations (flowcharts, diagrams)
- Provides code examples and explanations
- Embeds as a widget on any website

## Architecture

- **Backend**: FastAPI + RAG (Retrieval Augmented Generation)
- **Frontend**: React embeddable chat widget
- **Database**: PostgreSQL for conversation history
- **LLM**: Claude/GPT for conversational AI
- **Visualization**: Mermaid.js for dynamic diagrams
- **Deployment**: Docker Compose

## Project Structure
```
docbot-platform/
├── backend/          # FastAPI service (RAG, chat logic, APIs)
├── frontend/         # React chat widget (embeddable)
├── database/         # Database schema and initialization
├── examples/         # Client-specific implementations
│   ├── maveric/      # Maveric RADP implementation
│   └── demo/         # Generic demo
└── docs/             # Platform documentation
```

## Current Implementations

### Maveric MiniPilot
Interactive guide for the Maveric RIC Algorithm Development Platform (RADP). Explains Digital Twin training, RF Prediction, UE Tracks, and simulation orchestration.

## Getting Started

### Prerequisites
- Python 3.9+
- Node.js 16+
- Docker & Docker Compose

### Quick Start

1. Clone the repository
```bash
git clone <repo-url>
cd docbot-platform
```

2. Set up environment
```bash
cp .env.example .env
# Edit .env with your API keys
```

3. Run with Docker
```bash
docker-compose up --build
```

4. Access the chatbot
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs

## Development

### Backend Development
```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn main:app --reload
```

### Frontend Development
```bash
cd frontend
npm install
npm start
```

## Configuration

Each client implementation has its own configuration in `examples/{client}/config/config.json`:
```json
{
  "client_name": "maveric",
  "docs_path": "examples/maveric/docs/",
  "system_prompt": "You are an expert guide for...",
  "modules": ["Module1", "Module2"],
  "enable_visualizations": true
}
```

## Roadmap

- [x] Core RAG engine
- [x] FastAPI backend
- [ ] React frontend widget
- [ ] Mermaid.js visualization generation
- [ ] Multi-client support
- [ ] Embeddable widget export
- [ ] Docker deployment

## License

MIT

## Author

Built by Bryan S. Barrett | AI Native Developer