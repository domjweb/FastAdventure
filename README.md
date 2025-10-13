
# FastAdventure: AI-Powered Interactive Story Generator

FastAdventure is a full-stack application that leverages AI to generate interactive, choose-your-own-adventure stories. It demonstrates modern web development practices, seamless backend/frontend integration, and the use of generative AI in a real-world product.

## Project Overview

- **Purpose:**
  - Showcases the ability to design, build, and integrate a scalable AI-driven application from scratch.
  - Demonstrates proficiency in Python (FastAPI), JavaScript (React), API design, async job handling, and cloud-ready architecture.

- **Key Features:**
  - Users enter a theme (e.g., "pirates", "space", "fantasy") to generate a unique interactive story.
  - Backend uses OpenAI and LangChain to create a story tree with branching choices.
  - Asynchronous job system: story generation runs in the background, with real-time job status updates.
  - Frontend provides a smooth, responsive UI for story creation and navigation.
  - Clean separation of concerns, robust error handling, and modern code structure.

## Architecture & Technologies

- **Backend:**
  - **FastAPI**: High-performance Python web framework for API endpoints and async job management.
  - **SQLAlchemy**: ORM for relational data modeling (stories, nodes, jobs).
  - **Pydantic v2**: Data validation and serialization.
  - **LangChain & OpenAI API**: AI-driven story and choice generation.
  - **Uvicorn**: ASGI server for async performance.
  - **Job Queue**: Background task system for scalable story generation.

- **Frontend:**
  - **React (Vite)**: Modern, fast SPA with hooks and functional components.
  - **Axios**: API communication.
  - **React Router**: Client-side routing for story navigation.
  - **Responsive UI**: Clean, user-friendly interface for both desktop and mobile.

## User Experience

1. User lands on the homepage and enters a story theme.
2. The app submits the theme to the backend, which starts an async job.
3. The frontend polls for job status, showing a loading indicator.
4. When the story is ready, the user is redirected to an interactive story view.
5. The user reads the scenario and makes choices, navigating the AI-generated story tree.


