# Recruitment Automation API

A FastAPI-based recruitment automation project that accepts a job description and multiple PDF resumes, extracts resume text, evaluates candidate relevance, and returns ranked results.

## Tech Stack

- Python 3.11
- FastAPI
- Uvicorn
- LangGraph
- LangChain OpenAI client
- PyPDF2
- OpenRouter API
- Docker / Docker Compose

## Features

- Upload one or more resume PDFs
- Submit a job description
- Extract text from resumes
- Parse job requirements
- Score candidates against the job description
- Generate a ranked shortlist report
- Serve frontend from static files
- Dockerized backend support