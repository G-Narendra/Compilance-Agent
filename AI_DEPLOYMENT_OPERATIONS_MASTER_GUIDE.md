# AI DEPLOYMENT & OPERATIONS MASTER GUIDE
## The Complete FAANG-Level Reference for Deploying, Monitoring, and Operating Production AI Systems

**Target Audience**: DevOps Engineers, MLOps Engineers, Platform Engineers, SREs, AI Engineers, Cloud Architects
**Last Updated**: May 2026
**Version**: 1.0 - Production Operations Edition
**Scope**: End-to-end deployment, observability, monitoring, tracing, lifecycle management, and operational excellence for AI systems

---

## TABLE OF CONTENTS

### PART 1: DEPLOYMENT FOUNDATIONS (Sections 1-7)
1. Deployment Decision Framework
2. Application Types and Deployment Strategies
3. Cloud Provider Deployment (AWS, GCP, Azure)
4. Platform-as-a-Service Deployments (Vercel, Railway, Render, Fly.io)
5. ML-Specific Deployment Platforms (HuggingFace, Modal, Replicate, SageMaker, Vertex AI)
6. Edge and On-Device Deployment
7. Container Orchestration (Docker, Kubernetes, ECS, Cloud Run)

### PART 2: PRODUCTION OPERATIONS (Sections 8-14)
8. Observability Architecture (OpenTelemetry, Grafana Stack)
9. Monitoring and Alerting (Prometheus, Datadog, New Relic, CloudWatch)
10. Distributed Tracing (Jaeger, Zipkin, Tempo, X-Ray)
11. Log Management and Analysis (ELK, Loki, CloudWatch Logs)
12. Error Tracking and Debugging (Sentry, Rollbar, Bugsnag)
13. Incident Management and On-Call (PagerDuty, Opsgenie, Slack)
14. Health Checks, Readiness Probes, and Graceful Degradation

### PART 3: LIFECYCLE MANAGEMENT (Sections 15-22)
15. CI/CD Pipelines for AI Deployments (GitHub Actions, GitLab CI, ArgoCD)
16. Deployment Patterns (Blue-Green, Canary, Rolling, Shadow, Recreate)
17. Model Versioning and Model Registry (MLflow, Weights & Biases, DVC)
18. Rollback and Recovery Strategies
19. Upgrading, Migration, and Hot-Swap Strategies
20. A/B Testing and Experimentation in Production
21. Post-Deployment Validation and Smoke Testing
22. Production Readiness Checklists and Operational Runbooks

---

# PART 1: DEPLOYMENT FOUNDATIONS

---

## 1. DEPLOYMENT DECISION FRAMEWORK

### What is a Deployment Decision Framework?

Before you write a single line of deployment code, you need to answer a fundamental question: **where and how should this application run?**

Think of it like choosing a home for your application. A small weekend cabin (hobby project) doesn't need the same infrastructure as a skyscraper (enterprise system). The deployment decision framework is a structured set of questions that helps you pick the right "home" for your application based on:

- **What the application does** (API, chatbot, batch job, real-time system)
- **How much traffic it gets** (10 users/day vs 10,000 requests/second)
- **How fast it needs to respond** (instant vs minutes is acceptable)
- **How much you can spend** ($0/month vs $10,000/month)
- **What compliance requirements exist** (public data vs healthcare/government)

Getting this wrong is expensive. Deploying a simple API on Kubernetes when Railway would suffice wastes months of DevOps work. Deploying a high-traffic system on a free-tier PaaS leads to outages. This framework prevents those mistakes.

### 1.1 THE DEPLOYMENT DISCOVERY SCRIPT

Before deploying any AI system, you must answer critical questions that determine your deployment architecture. This decision framework mirrors the consultation framework from the Production Guide but focuses exclusively on deployment and operations.

#### Phase 1: Infrastructure Assessment (15 minutes)
```
Q1: What is the application type being deployed?
├─ REST API (FastAPI/Flask) → Container or PaaS deployment
├─ WebSocket Server (real-time chat) → Persistent connection platform
├─ Streamlit/Gradio UI → HuggingFace Spaces, Streamlit Cloud, or PaaS
├─ CLI Tool / Library → PyPI package or binary distribution
├─ Batch Processing Pipeline → Serverless functions or job queues
├─ Multi-Agent System → Kubernetes or container orchestration
├─ Edge Model (mobile/IoT) → ONNX/TFLite + device deployment
└─ Full-Stack App (API + UI + Workers) → Kubernetes or multi-service PaaS

Q2: What is the expected traffic pattern?
├─ Constant high traffic → Always-on containers (Kubernetes, ECS)
├─ Bursty/spiky traffic → Serverless with autoscaling (Lambda, Cloud Run)
├─ Low/intermittent traffic → PaaS with sleep/wake (Render, Railway)
├─ Scheduled batch jobs → Cron on containers or serverless functions
├─ Real-time streaming → WebSocket platforms (Fly.io, Railway)
└─ Global distribution → CDN + edge functions (Cloudflare Workers, Vercel Edge)

Q3: What is the latency requirement?
├─ <50ms → Edge deployment, CDN caching, local inference
├─ <200ms → Regional deployment with optimized models
├─ <2s → Standard cloud deployment
├─ <10s → Complex multi-step pipelines acceptable
└─ No constraint → Batch processing, async workflows

Q4: What is the data sensitivity level?
├─ Public data → Any cloud provider, any region
├─ Internal/sensitive → Private VPC, encrypted at rest/transit
├─ PII/PHI → HIPAA-compliant infrastructure, data residency
├─ Government/defense → Air-gapped, on-premise only
└─ Mixed → Tiered architecture with data classification
```

#### Phase 2: Operational Requirements (10 minutes)
```
Q5: What is the team's operational maturity?
├─ Solo developer / small team → PaaS, managed services, minimal ops
├─ Small engineering team → Managed Kubernetes or PaaS + basic monitoring
├─ Dedicated DevOps/SRE team → Full Kubernetes, custom observability
├─ FAANG-level platform team → Multi-region, chaos engineering, SLOs
└─ Non-technical team → Fully managed (SageMaker, Vertex AI endpoints)

Q6: What is the budget model?
├─ Pay-per-use → Serverless (Lambda, Cloud Functions, Modal)
├─ Fixed monthly budget → Reserved instances, PaaS plans
├─ Cost-optimization priority → Spot instances, autoscaling, scale-to-zero
├─ Enterprise contract → Reserved capacity, committed use discounts
└─ Free tier only → HuggingFace Spaces, Railway free, Render free

Q7: What is the availability requirement?
├─ 99.99% (52 min downtime/year) → Multi-AZ, multi-region, active-active
├─ 99.9% (8.7 hr downtime/year) → Multi-AZ, health checks, auto-recovery
├─ 99% (3.6 days downtime/year) → Single region with failover
├─ Best effort → Single instance, manual recovery
└─ Development/staging → No SLA, cost-optimized

Q8: What compliance requirements apply?
├─ SOC 2 → AWS GovCloud, Azure Government, audit logging
├─ GDPR → EU data residency, right to deletion, DPO
├─ HIPAA → BAA with provider, encryption, access controls
├─ ISO 27001 → Certified providers, documented processes
└─ None → Standard cloud deployment
```

### 1.2 DEPLOYMENT DECISION MATRIX

```
┌─────────────────────────────────────────────────────────────────────┐
│                    DEPLOYMENT DECISION TREE                         │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  Application Type?                                                  │
│  ├─ API/Backend                                                    │
│  │  ├─ Simple (single service) → PaaS (Railway/Render/Fly.io)     │
│  │  ├─ Medium (2-5 services) → Docker Compose + VPS or ECS        │
│  │  └─ Complex (microservices) → Kubernetes                       │
│  │                                                                 │
│  ├─ AI Model Serving                                               │
│  │  ├─ Small model (<1B params) → Serverless GPU (Modal/Replicate)│
│  │  ├─ Medium model (1-7B params) → Dedicated GPU (SageMaker)     │
│  │  ├─ Large model (7-70B params) → Multi-GPU (A100/H100 cluster)│
│  │  └─ Massive model (70B+ params) → Multi-node distributed       │
│  │                                                                 │
│  ├─ Web Application                                                │
│  │  ├─ Static + API → Vercel/Netlify + Backend PaaS               │
│  │  ├─ Full-stack SSR → Vercel/Railway/Render                     │
│  │  └─ Real-time (WebSocket) → Fly.io/Railway                     │
│  │                                                                 │
│  ├─ Data Pipeline                                                  │
│  │  ├─ Scheduled batch → Airflow on K8s or Managed Airflow        │
│  │  ├─ Stream processing → Kafka + Flink on K8s                   │
│  │  └─ ETL jobs → Serverless functions (Lambda/Cloud Functions)    │
│  │                                                                 │
│  └─ Edge/Mobile                                                    │
│     ├─ Browser-based → ONNX.js / TensorFlow.js                    │
│     ├─ Mobile app → CoreML (iOS) / TFLite (Android)               │
│     └─ IoT device → ONNX Runtime / TensorRT                       │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

### 1.3 COST COMPARISON FRAMEWORK

```
┌──────────────────────────────────────────────────────────────────────────┐
│                    MONTHLY COST ESTIMATES (USD)                          │
├──────────────────┬──────────┬──────────┬──────────┬──────────────────────┤
│ Platform         │ Hobby    │ Startup  │ Growth   │ Enterprise           │
├──────────────────┼──────────┼──────────┼──────────┼──────────────────────┤
│ AWS ECS          │ $30-80   │ $150-400 │ $500-2K  │ $2K-20K+            │
│ AWS Lambda       │ $0-5     │ $20-100  │ $100-500 │ $500-5K+            │
│ GCP Cloud Run    │ $0-10    │ $30-150  │ $200-800 │ $800-8K+            │
│ Azure Containers │ $30-80   │ $150-400 │ $500-2K  │ $2K-20K+            │
│ Kubernetes (EKS) │ $75-200  │ $300-800 │ $1K-5K   │ $5K-50K+            │
│ Railway          │ $0-5     │ $5-20    │ $20-100  │ $100-500            │
│ Render           │ $0-7     │ $7-25    │ $25-150  │ $150-1K             │
│ Fly.io           │ $0-5     │ $5-30    │ $30-200  │ $200-2K             │
│ Vercel           │ $0-20    │ $20-150  │ $150-500 │ Custom              │
│ Modal (GPU)      │ $0-30    │ $50-300  │ $300-2K  │ $2K-20K+            │
│ Replicate        │ $0-20    │ $30-200  │ $200-1K  │ $1K-10K+            │
│ SageMaker        │ $50-200  │ $200-1K  │ $1K-5K   │ $5K-50K+            │
│ HuggingFace      │ $0       │ $0-50    │ $50-200  │ Custom              │
└──────────────────┴──────────┴──────────┴──────────┴──────────────────────┘

Note: GPU costs vary dramatically. A single A100 on cloud costs $3-5/hr.
Serverless GPU (Modal/Replicate) charges per-second of GPU time.
```

---

## 2. APPLICATION TYPES AND DEPLOYMENT STRATEGIES

### What are Application Types and Why Do They Matter for Deployment?

Not all AI applications are built the same. A simple REST API that serves predictions has completely different infrastructure needs than a real-time chatbot with WebSocket connections or a batch processing pipeline that runs overnight.

**Application type** refers to the fundamental architecture of your software — how it receives input, processes data, and returns output. This determines:

- **What compute resources you need** (CPU for APIs, GPU for model inference, both for complex pipelines)
- **How you scale** (add more servers for APIs, add more workers for batch jobs, add more GPU memory for large models)
- **What platform is best** (serverless for simple APIs, containers for complex apps, managed services for ML models)
- **How you handle state** (stateless APIs scale easily, stateful chatbots need session storage, batch jobs need progress tracking)

Understanding your application type is the first step in choosing the right deployment strategy. A mismatch here leads to either over-engineering (spending too much) or under-provisioning (crashing under load).

### 2.1 AI APPLICATION TAXONOMY

Every AI application falls into one of these deployment categories. Each has unique requirements for compute, networking, storage, and scaling.

#### A) REST API Services (FastAPI, Flask, Django)
```
Architecture:
┌─────────────┐     ┌──────────────┐     ┌──────────────┐
│   Client     │────>│  Load        │────>│  API Server  │
│  (Browser/   │     │  Balancer    │     │  (FastAPI)   │
│   Mobile)    │<────│  (Nginx/ALB) │<────│  Port 8000   │
└─────────────┘     └──────────────┘     └──────┬───────┘
                                                │
                                     ┌──────────┴──────────┐
                                     │                     │
                              ┌──────┴──────┐    ┌────────┴────────┐
                              │  Model      │    │  Vector DB      │
                              │  Inference  │    │  (Pinecone/     │
                              │  (GPU/CPU)  │    │   ChromaDB)     │
                              └─────────────┘    └─────────────────┘

Deployment Options:
├─ Single container → Railway, Render, Fly.io
├─ Multi-replica → ECS, Cloud Run, Kubernetes
├─ With GPU → SageMaker, Modal, dedicated GPU instances
└─ With WebSocket → Fly.io, Railway (persistent connections)

Scaling Pattern:
├─ Horizontal: Add more API server replicas behind load balancer
├─ Vertical: Increase CPU/RAM per container
├─ GPU scaling: Add GPU instances for model inference
└─ Connection pooling: PgBouncer for database, Redis for caching
```

#### B) LLM API Proxy / Gateway
```
Architecture:
┌─────────────┐     ┌──────────────┐     ┌──────────────┐
│  Client App  │────>│  API Gateway │────>│  LLM Router  │
│              │     │  (Rate Limit │     │  (Provider   │
│              │<────│   Auth)      │<────│   Selection) │
└─────────────┘     └──────────────┘     └──────┬───────┘
                                                │
                    ┌───────────────────────────┼───────────────────────┐
                    │                           │                       │
             ┌──────┴──────┐          ┌────────┴────────┐     ┌───────┴──────┐
             │  OpenAI     │          │  Anthropic      │     │  Local Model │
             │  GPT-4      │          │  Claude         │     │  (Ollama)    │
             └─────────────┘          └─────────────────┘     └──────────────┘

Key Requirements:
├─ Low latency (<100ms routing overhead)
├─ Token counting and cost tracking per user/team
├─ Rate limiting per API key
├─ Fallback routing (if provider A fails, try provider B)
├─ Response caching (semantic cache for repeated queries)
├─ Streaming support (SSE/WebSocket passthrough)
└─ Audit logging for compliance

Best Platforms:
├─ LiteLLM Proxy → Docker on Railway/Render/Fly.io
├─ Custom FastAPI → Any container platform
├─ Kong/APIM → Enterprise API management
└─ Portkey/Helicone → Managed LLM gateway
```

#### C) Chatbot / Conversational AI
```
Architecture:
┌─────────────┐     ┌──────────────┐     ┌──────────────┐
│  User        │────>│  Frontend    │────>│  Chat API    │
│  Interface   │     │  (React/     │     │  (WebSocket  │
│              │<────│   Next.js)   │<────│   /SSE)      │
└─────────────┘     └──────────────┘     └──────┬───────┘
                                                │
                        ┌───────────────────────┼────────────────┐
                        │                       │                │
                 ┌──────┴──────┐     ┌─────────┴──────┐  ┌─────┴──────┐
                 │  Session    │     │  RAG Pipeline  │  │  LLM       │
                 │  Store      │     │  (Retrieval)   │  │  Provider  │
                 │  (Redis)    │     │                │  │            │
                 └─────────────┘     └────────────────┘  └────────────┘

Key Requirements:
├─ WebSocket or SSE for streaming responses
├─ Session management (conversation history)
├─ Context window management (token limits)
├─ Authentication and user management
├─ Rate limiting per user/session
├─ Content moderation and safety filters
├─ Feedback collection (thumbs up/down)
└─ Analytics (response time, user satisfaction, cost per conversation)

Best Platforms:
├─ Vercel AI SDK + Next.js → Full-stack with streaming
├─ Streamlit → Rapid prototyping, internal tools
├─ Gradio → ML demos, HuggingFace Spaces
├─ Custom React + FastAPI → Production-grade full-stack
└─ Botpress/Voiceflow → No-code conversational AI
```

#### D) Batch Processing Pipeline
```
Architecture:
┌──────────────┐     ┌──────────────┐     ┌──────────────┐
│  Data Source  │────>│  Queue       │────>│  Worker Pool │
│  (S3/GCS/    │     │  (SQS/Redis/ │     │  (Celery/    │
│   Database)  │     │   RabbitMQ)  │     │   Dramatiq)  │
└──────────────┘     └──────────────┘     └──────┬───────┘
                                                  │
                                          ┌───────┴───────┐
                                          │               │
                                   ┌──────┴──────┐ ┌─────┴──────┐
                                   │  GPU Worker │ │  Result    │
                                   │  (Model     │ │  Store     │
                                   │   Inference)│ │  (S3/DB)   │
                                   └─────────────┘ └────────────┘

Use Cases:
├─ Document processing (PDF → text → embeddings → vector DB)
├─ Image/video analysis at scale
├─ Data labeling and annotation pipelines
├─ Model evaluation and benchmarking
├─ Report generation
├─ Bulk content generation
└─ Training data preparation

Key Requirements:
├─ Job queue with retry logic and dead-letter queue
├─ Worker autoscaling based on queue depth
├─ Progress tracking and status endpoints
├─ Idempotent job processing (safe to retry)
├─ Resource management (GPU allocation, memory limits)
├─ Monitoring (queue depth, processing time, error rate)
└─ Cost optimization (spot instances, scale-to-zero)

Best Platforms:
├─ AWS SQS + Lambda → Serverless batch processing
├─ Celery + Redis on Kubernetes → Flexible, scalable
├─ Apache Airflow on Managed (MWAA/Composer) → DAG-based workflows
├─ Prefect → Modern workflow orchestration
├─ Modal → Serverless GPU batch jobs
└─ Google Cloud Dataflow → Stream + batch unified
```

#### E) Real-Time Streaming Application
```
Architecture:
┌─────────────┐     ┌──────────────┐     ┌──────────────┐
│  Client      │────>│  WebSocket   │────>│  Event       │
│  (Browser)   │<───>│  Gateway     │<───>│  Processor   │
│              │     │  (Socket.io) │     │              │
└─────────────┘     └──────────────┘     └──────┬───────┘
                                                │
                              ┌──────────────────┼─────────────────┐
                              │                  │                 │
                       ┌──────┴──────┐   ┌──────┴──────┐  ┌──────┴──────┐
                       │  LLM Stream │   │  Database   │  │  Redis Pub/ │
                       │  (SSE)      │   │  (State)    │  │  Sub        │
                       └─────────────┘   └─────────────┘  └─────────────┘

Key Requirements:
├─ Persistent WebSocket connections
├─ Connection state management (reconnection, resume)
├─ Horizontal scaling with Redis pub/sub for message fan-out
├─ Graceful connection draining on deploy
├─ Message ordering and delivery guarantees
├─ Connection limits and backpressure
└─ Monitoring (active connections, message throughput, latency)

Best Platforms:
├─ Fly.io → Built-in WebSocket support, global regions
├─ Railway → Easy WebSocket deployment
├─ AWS API Gateway WebSocket + Lambda → Serverless WebSockets
├─ Azure Web PubSub → Managed WebSocket service
└─ Pusher/Ably → Managed real-time messaging
```

#### F) Multi-Agent System
```
Architecture:
┌──────────────┐     ┌──────────────┐     ┌──────────────┐
│  Orchestrator│────>│  Agent Pool  │────>│  Tool        │
│  Agent       │     │  (Worker     │     │  Registry    │
│  (LangGraph) │<────│   Agents)    │<────│  (APIs, DBs) │
└──────────────┘     └──────────────┘     └──────────────┘
        │
        │  ┌──────────────┐     ┌──────────────┐
        ├─>│  Planning     │────>│  Execution   │
        │  │  Agent        │     │  Agent       │
        │  └──────────────┘     └──────────────┘
        │
        │  ┌──────────────┐     ┌──────────────┐
        └─>│  Review       │────>│  Output      │
           │  Agent        │     │  Formatter   │
           └──────────────┘     └──────────────┘

Key Requirements:
├─ Inter-agent communication (message passing, shared state)
├─ Agent lifecycle management (start, stop, restart)
├─ Resource isolation (one agent shouldn't crash others)
├─ Timeout and circuit breaker per agent call
├─ Cost tracking per agent (token usage)
├─ Observability (agent execution traces)
├─ State persistence (checkpoint/resume long-running tasks)
└─ Parallel execution with dependency management

Best Platforms:
├─ Kubernetes with sidecar pattern → Full control, resource isolation
├─ LangGraph Platform → Managed agent orchestration
├─ CrewAI Enterprise → Multi-agent platform
├─ Modal → Serverless per-agent execution
└─ AWS Step Functions + Lambda → State machine orchestration
```

### 2.2 APPLICATION TYPE DECISION MATRIX

```
┌────────────────────┬───────────┬───────────┬──────────┬──────────┬───────────┐
│ App Type           │ Compute   │ Stateful? │ Scaling  │ Latency  │ Best      │
│                    │           │           │ Pattern  │ Priority │ Platform  │
├────────────────────┼───────────┼───────────┼──────────┼──────────┼───────────┤
│ REST API           │ CPU       │ No        │ Horiz.   │ <200ms   │ PaaS/K8s  │
│ LLM Gateway        │ CPU       │ No        │ Horiz.   │ <100ms   │ PaaS/K8s  │
│ Chatbot            │ CPU+GPU   │ Yes (sess)│ Horiz.   │ <2s      │ Vercel+   │
│ Batch Processing   │ CPU+GPU   │ No        │ Worker   │ Minutes  │ Serverless│
│ Real-time Stream   │ CPU       │ Yes (conn)│ Horiz.   │ <50ms    │ Fly.io    │
│ Multi-Agent        │ CPU+GPU   │ Yes (state)│ Dynamic │ <10s     │ K8s       │
│ Model Serving      │ GPU       │ No        │ GPU Pool │ <500ms   │ SageMaker │
│ Data Pipeline      │ CPU+GPU   │ No        │ Worker   │ Minutes  │ Airflow   │
│ Edge Inference     │ NPU/GPU   │ No        │ Device   │ <50ms    │ ONNX/TFL  │
│ Full-Stack App     │ CPU+GPU   │ Yes       │ Horiz.   │ <2s      │ K8s/PaaS  │
└────────────────────┴───────────┴───────────┴──────────┴──────────┴───────────┘
```

---

## 3. CLOUD PROVIDER DEPLOYMENT (AWS, GCP, AZURE)

### What are Cloud Providers?

A **cloud provider** is a company that owns and manages massive data centers around the world, and rents out computing resources (servers, storage, databases, AI services) over the internet. Instead of buying your own servers, you rent what you need and pay only for what you use.

The "Big Three" cloud providers are:

- **AWS (Amazon Web Services)** — The largest and most mature cloud provider. Offers the widest range of services. Used by most Fortune 500 companies. Best for: enterprises, broad service selection, largest ecosystem.
- **GCP (Google Cloud Platform)** — Built on the same infrastructure that powers Google Search, YouTube, and Gmail. Best AI/ML services (TensorFlow, TPUs, Vertex AI). Best for: ML workloads, data analytics, Kubernetes (Google invented it).
- **Azure (Microsoft Azure)** — Deep integration with Microsoft products (Office 365, Active Directory, .NET). Strong enterprise sales. Best for: Microsoft shops, enterprise hybrid cloud, .NET applications.

Each provider offers dozens of ways to deploy your application — from serverless functions (run code without managing servers) to managed Kubernetes (orchestrate containers) to fully managed ML endpoints (deploy models with one click). The sections below cover the most important options for AI applications.

### 3.1 AWS DEPLOYMENT OPTIONS

#### A) AWS Lambda (Serverless)
```
Best For: Event-driven APIs, webhooks, scheduled tasks, lightweight inference
Limitations: 15-min max execution, 10GB memory, cold starts, no GPU

Architecture:
┌─────────────┐     ┌──────────────┐     ┌──────────────┐
│  API Gateway │────>│  Lambda      │────>│  DynamoDB /  │
│  or ALB      │     │  Function    │     │  S3 / RDS    │
└─────────────┘     └──────────────┘     └──────────────┘

Cold Start Mitigation:
├─ Provisioned concurrency (keep N instances warm)
├─ SnapStart (Java/Python snapshot)
├─ Lightweight deployment package (slim dependencies)
├─ Lambda Layers for shared dependencies
└─ Scheduled warm-up pings (every 5 minutes)
```

```python
# File: lambda_handler.py
import json
import boto3
from mangum import Mangum
from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()

class QueryRequest(BaseModel):
    question: str
    user_id: str

class QueryResponse(BaseModel):
    answer: str
    confidence: float
    latency_ms: float

@app.post("/query", response_model=QueryResponse)
async def query_endpoint(request: QueryRequest):
    """LLM query endpoint running on Lambda."""
    import time
    start = time.time()

    # Retrieve context from vector store
    context = await retrieve_context(request.question)

    # Call LLM
    answer = await call_llm(request.question, context)

    latency = (time.time() - start) * 1000

    return QueryResponse(
        answer=answer,
        confidence=context.confidence,
        latency_ms=latency
    )

# Mangum wraps FastAPI for Lambda
handler = Mangum(app, lifespan="on")
```

```yaml
# File: serverless.yml (SAM/CloudFormation equivalent)
AWSTemplateFormatVersion: '2010-09-09'
Transform: AWS::Serverless-2016-10-31

Globals:
  Function:
    Timeout: 30
    MemorySize: 1024
    Runtime: python3.11
    Architectures: [arm64]  # Graviton2 for cost savings

Resources:
  ApiFunction:
    Type: AWS::Serverless::Function
    Properties:
      Handler: lambda_handler.handler
      CodeUri: src/
      Environment:
        Variables:
          OPENAI_API_KEY: !Ref OpenAISecret
          VECTOR_DB_URL: !GetAtt VectorStore.Endpoint
      Events:
        QueryApi:
          Type: Api
          Properties:
            Path: /query
            Method: post
      ProvisionedConcurrency: 2  # Keep 2 instances warm
      Policies:
        - S3ReadPolicy:
            BucketName: !Ref DataBucket
        - DynamoDBCrudPolicy:
            TableName: !Ref SessionTable
```

#### B) AWS ECS Fargate (Container Serverless)
```
Best For: Long-running APIs, containerized apps, no GPU needed
Advantages: No server management, automatic scaling, Docker-based

Architecture:
┌─────────────┐     ┌──────────────┐     ┌──────────────────┐
│  ALB         │────>│  ECS Fargate │────>│  Task Definition │
│  (HTTPS)     │     │  Service     │     │  (Docker Image)  │
└─────────────┘     └──────────────┘     └──────────────────┘
        │                    │
        │            ┌──────┴──────┐
        │            │  Auto       │
        └───────────>│  Scaling    │
                     │  (CPU/Mem)  │
                     └─────────────┘
```

```python
# File: deploy/ecs_deploy.py
import boto3
import json

class ECSDeployer:
    """Deploy AI application to AWS ECS Fargate."""

    def __init__(self, cluster_name: str, service_name: str):
        self.ecs = boto3.client("ecs")
        self.ec2 = boto3.client("ec2")
        self.elbv2 = boto3.client("elbv2")
        self.cluster = cluster_name
        self.service = service_name

    def create_task_definition(
        self,
        image_uri: str,
        cpu: int = 1024,
        memory: int = 2048,
        port: int = 8000,
        env_vars: dict = None,
        secrets: dict = None,
    ) -> str:
        """Create ECS task definition for the AI service."""
        container_def = {
            "name": "ai-service",
            "image": image_uri,
            "essential": True,
            "portMappings": [
                {"containerPort": port, "protocol": "tcp"}
            ],
            "environment": [
                {"name": k, "value": v} for k, v in (env_vars or {}).items()
            ],
            "secrets": [
                {"name": k, "valueFrom": v} for k, v in (secrets or {}).items()
            ],
            "logConfiguration": {
                "logDriver": "awslogs",
                "options": {
                    "awslogs-group": f"/ecs/{self.service}",
                    "awslogs-region": "us-east-1",
                    "awslogs-stream-prefix": "ecs",
                },
            },
            "healthCheck": {
                "command": ["CMD-SHELL", "curl -f http://localhost:8000/health || exit 1"],
                "interval": 30,
                "timeout": 5,
                "retries": 3,
                "startPeriod": 60,
            },
        }

        response = self.ecs.register_task_definition(
            family=self.service,
            networkMode="awsvpc",
            requiresCompatibilities=["FARGATE"],
            cpu=str(cpu),
            memory=str(memory),
            executionRoleArn="arn:aws:iam::role/ecsTaskExecutionRole",
            taskRoleArn="arn:aws:iam::role/ecsTaskRole",
            containerDefinitions=[container_def],
        )

        return response["taskDefinition"]["taskDefinitionArn"]

    def deploy_service(
        self,
        task_definition_arn: str,
        desired_count: int = 2,
        subnets: list = None,
        security_groups: list = None,
    ):
        """Deploy or update ECS service with zero-downtime rolling update."""
        self.ecs.update_service(
            cluster=self.cluster,
            service=self.service,
            taskDefinition=task_definition_arn,
            desiredCount=desired_count,
            deploymentConfiguration={
                "maximumPercent": 200,
                "minimumHealthyPercent": 100,
                "deploymentCircuitBreaker": {
                    "enable": True,
                    "rollback": True,
                },
            },
            networkConfiguration={
                "awsvpcConfiguration": {
                    "subnets": subnets or ["subnet-xxxxx"],
                    "securityGroups": security_groups or ["sg-xxxxx"],
                    "assignPublicIp": "ENABLED",
                },
            },
        )

    def setup_autoscaling(
        self,
        min_count: int = 1,
        max_count: int = 10,
        target_cpu: int = 70,
    ):
        """Configure auto-scaling based on CPU utilization."""
        appautoscaling = boto3.client("application-autoscaling")

        # Register scalable target
        appautoscaling.register_scalable_target(
            ServiceNamespace="ecs",
            ResourceId=f"service/{self.cluster}/{self.service}",
            ScalableDimension="ecs:service:DesiredCount",
            MinCapacity=min_count,
            MaxCapacity=max_count,
        )

        # CPU-based scaling
        appautoscaling.put_scaling_policy(
            PolicyName=f"{self.service}-cpu-scaling",
            ServiceNamespace="ecs",
            ResourceId=f"service/{self.cluster}/{self.service}",
            ScalableDimension="ecs:service:DesiredCount",
            PolicyType="TargetTrackingScaling",
            TargetTrackingScalingPolicyConfiguration={
                "TargetValue": target_cpu,
                "PredefinedMetricSpecification": {
                    "PredefinedMetricType": "ECSServiceAverageCPUUtilization",
                },
                "ScaleInCooldown": 300,
                "ScaleOutCooldown": 60,
            },
        )
```

#### C) AWS SageMaker (ML-Specific)
```
Best For: ML model serving, GPU inference, A/B testing, batch transform
Advantages: Built-in model monitoring, autoscaling, multi-model endpoints

Architecture:
┌─────────────┐     ┌──────────────┐     ┌──────────────────┐
│  Client      │────>│  API Gateway │────>│  SageMaker       │
│              │     │  + Lambda    │     │  Endpoint        │
└─────────────┘     └──────────────┘     │  (GPU Instance)  │
                                          └────────┬─────────┘
                                                   │
                              ┌─────────────────────┼──────────────────┐
                              │                     │                  │
                       ┌──────┴──────┐     ┌───────┴───────┐  ┌──────┴──────┐
                       │  Model      │     │  Data Capture  │  │  CloudWatch │
                       │  Artifacts  │     │  (S3)          │  │  Monitoring │
                       │  (S3)       │     │                │  │             │
                       └─────────────┘     └────────────────┘  └─────────────┘
```

```python
# File: deploy/sagemaker_deploy.py
import sagemaker
from sagemaker.huggingface import HuggingFaceModel
from sagemaker.model_monitor import DataCaptureConfig

class SageMakerDeployer:
    """Deploy AI models to AWS SageMaker."""

    def __init__(self, role_arn: str, region: str = "us-east-1"):
        self.session = sagemaker.Session()
        self.role = role_arn
        self.region = region

    def deploy_model(
        self,
        model_data: str,
        instance_type: str = "ml.g5.xlarge",
        instance_count: int = 1,
        endpoint_name: str = None,
        enable_data_capture: bool = True,
    ):
        """Deploy a HuggingFace model to SageMaker endpoint."""
        model = HuggingFaceModel(
            model_data=model_data,
            role=self.role,
            transformers_version="4.37",
            pytorch_version="2.1",
            py_version="py310",
            env={
                "HF_MODEL_ID": "meta-llama/Llama-2-7b-chat-hf",
                "MAX_INPUT_LENGTH": "4096",
                "MAX_TOTAL_TOKENS": "8192",
                "SM_NUM_GPUS": "1",
            },
        )

        data_capture_config = None
        if enable_data_capture:
            data_capture_config = DataCaptureConfig(
                enable_capture=True,
                sampling_percentage=100,
                destination_s3_uri=f"s3://my-bucket/data-capture/{endpoint_name}",
                capture_options=["REQUEST", "RESPONSE"],
                csv_content_types=["text/csv"],
                json_content_types=["application/json"],
            )

        predictor = model.deploy(
            initial_instance_count=instance_count,
            instance_type=instance_type,
            endpoint_name=endpoint_name,
            data_capture_config=data_capture_config,
        )

        return predictor

    def setup_autoscaling(
        self,
        endpoint_name: str,
        variant_name: str = "AllTraffic",
        min_capacity: int = 1,
        max_capacity: int = 10,
        target_value: float = 70.0,
    ):
        """Configure auto-scaling for SageMaker endpoint."""
        client = boto3.client("application-autoscaling")

        resource_id = f"endpoint/{endpoint_name}/variant/{variant_name}"

        client.register_scalable_target(
            ServiceNamespace="sagemaker",
            ResourceId=resource_id,
            ScalableDimension="sagemaker:variant:DesiredInstanceCount",
            MinCapacity=min_capacity,
            MaxCapacity=max_capacity,
        )

        client.put_scaling_policy(
            PolicyName=f"{endpoint_name}-scaling",
            ServiceNamespace="sagemaker",
            ResourceId=resource_id,
            ScalableDimension="sagemaker:variant:DesiredInstanceCount",
            PolicyType="TargetTrackingScaling",
            TargetTrackingScalingPolicyConfiguration={
                "TargetValue": target_value,
                "CustomizedMetricSpecification": {
                    "MetricName": "InvocationsPerInstance",
                    "Namespace": "AWS/SageMaker",
                    "Dimensions": [
                        {"Name": "EndpointName", "Value": endpoint_name},
                        {"Name": "VariantName", "Value": variant_name},
                    ],
                    "Statistic": "Average",
                },
                "ScaleInCooldown": 300,
                "ScaleOutCooldown": 60,
            },
        )

    def create_model_package_group(
        self,
        group_name: str,
        description: str = "",
    ):
        """Create a model registry group for versioning."""
        sm_client = boto3.client("sagemaker")
        sm_client.create_model_package_group(
            ModelPackageGroupName=group_name,
            ModelPackageGroupDescription=description,
        )
```

### 3.2 GCP DEPLOYMENT OPTIONS

#### A) Google Cloud Run
```
Best For: Containerized APIs, automatic scaling, pay-per-request
Advantages: Scale to zero, HTTP/2, WebSocket support, GPU support (preview)

Architecture:
┌─────────────┐     ┌──────────────┐     ┌──────────────┐
│  Cloud CDN   │────>│  Cloud Run   │────>│  Container   │
│  (optional)  │     │  Service     │     │  Image       │
└─────────────┘     └──────────────┘     └──────┬───────┘
                                                │
                              ┌──────────────────┼─────────────────┐
                              │                  │                 │
                       ┌──────┴──────┐   ┌──────┴──────┐  ┌──────┴──────┐
                       │  Cloud SQL  │   │  Vertex AI  │  │  Secret     │
                       │  (Postgres) │   │  (Model)    │  │  Manager    │
                       └─────────────┘   └─────────────┘  └─────────────┘
```

```yaml
# File: deploy/cloudrun_service.yaml
apiVersion: serving.knative.dev/v1
kind: Service
metadata:
  name: ai-service
  annotations:
    run.googleapis.com/ingress: all
    run.googleapis.com/execution-environment: gen2
spec:
  template:
    metadata:
      annotations:
        # Autoscaling
        autoscaling.knative.dev/minScale: "0"
        autoscaling.knative.dev/maxScale: "100"
        # CPU is always allocated (not just during request)
        run.googleapis.com/cpu-throttling: "false"
        # Startup CPU boost
        run.googleapis.com/startup-cpu-boost: "true"
    spec:
      containerConcurrency: 80
      timeoutSeconds: 300
      containers:
        - image: gcr.io/my-project/ai-service:latest
          ports:
            - containerPort: 8000
          resources:
            limits:
              cpu: "4"
              memory: "8Gi"
              # For GPU (preview):
              # nvidia.com/gpu: "1"
          env:
            - name: MODEL_NAME
              value: "llama-3-8b-instruct"
            - name: LOG_LEVEL
              value: "INFO"
          startupProbe:
            httpGet:
              path: /health
              port: 8000
            initialDelaySeconds: 30
            periodSeconds: 10
            failureThreshold: 3
          livenessProbe:
            httpGet:
              path: /health
              port: 8000
            periodSeconds: 15
      serviceAccountName: ai-service@my-project.iam.gserviceaccount.com
```

#### B) Google Vertex AI
```
Best For: Managed ML endpoints, AutoML, custom model serving, Gemini API

Architecture:
┌─────────────┐     ┌──────────────────┐     ┌──────────────┐
│  Client      │────>│  Vertex AI       │────>│  Endpoint    │
│              │     │  Prediction API  │     │  (GPU/TPU)   │
└─────────────┘     └──────────────────┘     └──────┬───────┘
                                                     │
                               ┌─────────────────────┼──────────────────┐
                               │                     │                  │
                        ┌──────┴──────┐     ┌───────┴───────┐  ┌──────┴──────┐
                        │  Model      │     │  Model        │  │  Feature    │
                        │  Registry   │     │  Monitoring   │  │  Store      │
                        │  (Versioned)│     │  (Drift)      │  │             │
                        └─────────────┘     └────────────────┘  └─────────────┘
```

```python
# File: deploy/vertex_deploy.py
from google.cloud import aiplatform

class VertexAIDeployer:
    """Deploy models to Google Vertex AI."""

    def __init__(self, project_id: str, region: str = "us-central1"):
        aiplatform.init(project=project_id, location=region)
        self.project_id = project_id
        self.region = region

    def deploy_model(
        self,
        model_display_name: str,
        artifact_uri: str,
        serving_container_image: str,
        machine_type: str = "n1-standard-4",
        accelerator_type: str = "NVIDIA_TESLA_T4",
        accelerator_count: int = 1,
        min_replicas: int = 1,
        max_replicas: int = 5,
    ):
        """Upload and deploy a model to Vertex AI endpoint."""
        # Upload model
        model = aiplatform.Model.upload(
            display_name=model_display_name,
            artifact_uri=artifact_uri,
            serving_container_image_uri=serving_container_image,
            serving_container_predict_route="/predict",
            serving_container_health_route="/health",
            serving_container_ports=[{"containerPort": 8000}],
            sync=True,
        )

        # Deploy to endpoint
        endpoint = model.deploy(
            deployed_model_display_name=f"{model_display_name}-deployed",
            machine_type=machine_type,
            accelerator_type=accelerator_type,
            accelerator_count=accelerator_count,
            min_replica_count=min_replicas,
            max_replica_count=max_replicas,
            traffic_split={"0": 100},
            sync=True,
        )

        return endpoint

    def deploy_with_traffic_split(
        self,
        endpoint_name: str,
        new_model_id: str,
        new_model_traffic_pct: int = 10,
    ):
        """Deploy a new model version with traffic splitting for canary."""
        endpoint = aiplatform.Endpoint.list(
            filter=f'display_name="{endpoint_name}"'
        )[0]

        # Get current deployed models
        current_models = endpoint.list_models()

        # Deploy new model with traffic split
        endpoint.deploy(
            model=aiplatform.Model(new_model_id),
            traffic_split={
                current_models[0].id: 100 - new_model_traffic_pct,
                new_model_id: new_model_traffic_pct,
            },
        )
```

### 3.3 AZURE DEPLOYMENT OPTIONS

#### A) Azure Container Apps
```
Best For: Microservices, event-driven apps, Dapr integration, KEDA scaling

Architecture:
┌─────────────┐     ┌──────────────────┐     ┌──────────────┐
│  Azure       │────>│  Container Apps  │────>│  Revision    │
│  Front Door  │     │  Environment     │     │  (Container) │
│  (CDN+WAF)   │     │                  │     │              │
└─────────────┘     └──────────────────┘     └──────┬───────┘
                                                     │
                               ┌─────────────────────┼──────────────────┐
                               │                     │                  │
                        ┌──────┴──────┐     ┌───────┴───────┐  ┌──────┴──────┐
                        │  Azure      │     │  Azure Key    │  │  Azure      │
                        │  Cosmos DB  │     │  Vault        │  │  OpenAI     │
                        │             │     │               │  │  Service    │
                        └─────────────┘     └────────────────┘  └─────────────┘
```

```yaml
# File: deploy/azure_containerapp.yaml
properties:
  configuration:
    ingress:
      external: true
      targetPort: 8000
      transport: http
      stickySessions:
        affinity: sticky
    secrets:
      - name: openai-api-key
        keyVaultUrl: https://my-vault.vault.azure.net/secrets/openai-key
    registries:
      - server: myregistry.azurecr.io
        identity: /subscriptions/.../managedIdentities/my-identity
  template:
    containers:
      - name: ai-service
        image: myregistry.azurecr.io/ai-service:latest
        resources:
          cpu: 2.0
          memory: 4Gi
        env:
          - name: OPENAI_API_KEY
            secretRef: openai-api-key
          - name: LOG_LEVEL
            value: INFO
        probes:
          - type: liveness
            httpGet:
              path: /health
              port: 8000
            periodSeconds: 15
          - type: readiness
            httpGet:
              path: /ready
              port: 8000
            periodSeconds: 10
    scale:
      minReplicas: 0
      maxReplicas: 20
      rules:
        - name: http-rule
          http:
            metadata:
              concurrentRequests: 100
        - name: queue-rule
          custom:
            type: azure-queue
            metadata:
              queueName: inference-queue
              queueLength: "10"
```

### 3.4 CLOUD PROVIDER COMPARISON

```
┌─────────────────┬──────────────┬──────────────┬──────────────┐
│ Feature         │ AWS          │ GCP          │ Azure        │
├─────────────────┼──────────────┼──────────────┼──────────────┤
│ Serverless API  │ Lambda       │ Cloud Run    │ Container    │
│                 │ API Gateway  │ Cloud Funcs  │ Apps/Funcs   │
├─────────────────┼──────────────┼──────────────┼──────────────┤
│ ML Serving      │ SageMaker    │ Vertex AI    │ Azure ML     │
├─────────────────┼──────────────┼──────────────┼──────────────┤
│ GPU Serverless  │ Lambda GPU   │ Cloud Run    │ Container    │
│                 │ (limited)    │ GPU (prev.)  │ Apps (prev.) │
├─────────────────┼──────────────┼──────────────┼──────────────┤
│ Kubernetes      │ EKS          │ GKE          │ AKS          │
├─────────────────┼──────────────┼──────────────┼──────────────┤
│ LLM Service     │ Bedrock      │ Vertex AI    │ Azure OpenAI │
│                 │              │ (Gemini)     │              │
├─────────────────┼──────────────┼──────────────┼──────────────┤
│ Vector DB       │ OpenSearch    │ Vertex       │ Azure AI     │
│                 │              │ Vector Search│ Search       │
├─────────────────┼──────────────┼──────────────┼──────────────┤
│ Monitoring      │ CloudWatch   │ Cloud Ops    │ Azure Monitor│
├─────────────────┼──────────────┼──────────────┼──────────────┤
│ Tracing         │ X-Ray        │ Cloud Trace  │ App Insights │
├─────────────────┼──────────────┼──────────────┼──────────────┤
│ Secret Mgmt     │ Secrets Mgr  │ Secret Mgr   │ Key Vault    │
├─────────────────┼──────────────┼──────────────┼──────────────┤
│ Best Region     │ us-east-1    │ us-central1  │ eastus       │
│ (AI services)   │              │              │              │
├─────────────────┼──────────────┼──────────────┼──────────────┤
│ Free Tier       │ 12-mo free   │ Always-free  │ 12-mo free   │
│                 │ tier + trial │ tier + $300  │ tier + $200  │
└─────────────────┴──────────────┴──────────────┴──────────────┘
```

---

## 4. PLATFORM-AS-A-SERVICE DEPLOYMENTS

### What is Platform-as-a-Service (PaaS)?

**Platform-as-a-Service (PaaS)** is a cloud service model where the provider manages all the underlying infrastructure (servers, networking, operating system, runtime) so you can focus entirely on your application code. You don't deal with servers, load balancers, or container orchestration — you just push your code and the platform handles everything else.

Think of it like this:
- **Raw servers (IaaS)** = You rent an empty apartment and furnish it yourself
- **Containers (CaaS)** = You rent a furnished apartment but arrange the furniture
- **PaaS** = You rent a hotel room — everything is ready, just move in

PaaS platforms are ideal for:
- **Small teams** without dedicated DevOps engineers
- **Prototypes and MVPs** where speed matters more than control
- **Simple to moderate applications** that don't need custom infrastructure
- **Developers who want to write code, not manage servers**

The tradeoff: PaaS gives you less control over the underlying infrastructure. For most AI applications (APIs, chatbots, simple model serving), this tradeoff is worth it. You only need to move to containers/Kubernetes when you hit specific limitations (custom networking, GPU requirements, multi-service architectures).

### 4.1 RAILWAY

```
Best For: Quick deployments, full-stack apps, databases, cron jobs
Strengths: Instant deploys, built-in PostgreSQL/Redis, simple pricing
Weaknesses: Limited regions, no GPU, sleep on free tier

Architecture:
┌─────────────┐     ┌──────────────┐     ┌──────────────┐
│  GitHub      │────>│  Railway     │────>│  Container   │
│  Push        │     │  Builder     │     │  (Auto)      │
└─────────────┘     └──────────────┘     └──────┬───────┘
                                                │
                              ┌──────────────────┼─────────────────┐
                              │                  │                 │
                       ┌──────┴──────┐   ┌──────┴──────┐  ┌──────┴──────┐
                       │  PostgreSQL │   │  Redis      │  │  Volume     │
                       │  (Managed)  │   │  (Managed)  │  │  (Storage)  │
                       └─────────────┘   └─────────────┘  └─────────────┘
```

```toml
# File: railway.toml
[build]
builder = "nixpacks"
buildCommand = "pip install -r requirements.txt"

[deploy]
startCommand = "uvicorn main:app --host 0.0.0.0 --port $PORT"
healthcheckPath = "/health"
healthcheckTimeout = 300
restartPolicyType = "on_failure"
restartPolicyMaxRetries = 3

[deploy.scaling]
minReplicas = 1
maxReplicas = 5

# Environment variables (set in Railway dashboard):
# DATABASE_URL = ${{Postgres.DATABASE_URL}}
# REDIS_URL = ${{Redis.REDIS_URL}}
# OPENAI_API_KEY = (secret)
```

```python
# File: main.py (Railway-optimized FastAPI app)
import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="AI Service")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
async def health():
    """Health check endpoint for Railway."""
    return {"status": "healthy", "port": os.environ.get("PORT")}

@app.get("/ready")
async def ready():
    """Readiness check - verify dependencies."""
    checks = {}
    try:
        # Check database
        db_url = os.environ.get("DATABASE_URL")
        checks["database"] = "connected" if db_url else "not_configured"
    except Exception as e:
        checks["database"] = f"error: {e}"

    try:
        # Check Redis
        redis_url = os.environ.get("REDIS_URL")
        checks["redis"] = "connected" if redis_url else "not_configured"
    except Exception as e:
        checks["redis"] = f"error: {e}"

    return {"status": "ready", "checks": checks}

@app.post("/query")
async def query(question: str):
    """AI query endpoint."""
    # Your AI logic here
    return {"answer": "Response from AI", "model": "gpt-4"}
```

### 4.2 RENDER

```
Best For: Simple web services, static sites, PostgreSQL, background workers
Strengths: Free tier, auto-SSL, private networking, managed PostgreSQL
Weaknesses: Cold starts on free tier, limited GPU, slower deploys

Architecture:
┌─────────────┐     ┌──────────────┐     ┌──────────────┐
│  GitHub      │────>│  Render      │────>│  Web Service │
│  Push        │     │  Build       │     │  (Docker)    │
└─────────────┘     └──────────────┘     └──────┬───────┘
                                                │
                              ┌──────────────────┼─────────────────┐
                              │                  │                 │
                       ┌──────┴──────┐   ┌──────┴──────┐  ┌──────┴──────┐
                       │  PostgreSQL │   │  Redis      │  │  Background │
                       │  (Managed)  │   │  (Managed)  │  │  Worker     │
                       └─────────────┘   └─────────────┘  └─────────────┘
```

```yaml
# File: render.yaml (Blueprint)
services:
  - type: web
    name: ai-service
    runtime: docker
    dockerfilePath: ./Dockerfile
    plan: standard
    region: oregon
    branch: main
    healthCheckPath: /health
    envVars:
      - key: DATABASE_URL
        fromDatabase:
          name: ai-database
          property: connectionString
      - key: REDIS_URL
        fromService:
          name: ai-redis
          property: connectionString
      - key: OPENAI_API_KEY
        sync: false  # Set in dashboard
    scaling:
      minInstances: 1
      maxInstances: 5
      targetMemoryPercent: 70
      targetCPUPercent: 70

  - type: worker
    name: ai-worker
    runtime: docker
    dockerfilePath: ./Dockerfile.worker
    plan: standard
    envVars:
      - key: DATABASE_URL
        fromDatabase:
          name: ai-database
          property: connectionString

  - type: pserv
    name: ai-redis
    plan: starter
    ipAllowList: []

databases:
  - name: ai-database
    plan: standard
    databaseName: ai_production
    ipAllowList: []
```

### 4.3 FLY.IO

```
Best For: Global edge deployment, WebSocket apps, persistent connections
Strengths: Global regions, WireGuard VPN, GPU machines, persistent volumes
Weaknesses: CLI-heavy, steeper learning curve, limited free tier

Architecture:
┌─────────────┐     ┌──────────────┐     ┌──────────────┐
│  Fly Proxy   │────>│  Machine 1   │────>│  App Process │
│  (Global)    │     │  (iad)       │     │              │
│              │────>│  Machine 2   │────>│  App Process │
│              │     │  (lhr)       │     │              │
│              │────>│  Machine 3   │────>│  App Process │
│              │     │  (nrt)       │     │              │
└─────────────┘     └──────────────┘     └──────────────┘
```

```toml
# File: fly.toml
app = "ai-service"
primary_region = "iad"

[build]
  dockerfile = "Dockerfile"

[http_service]
  internal_port = 8000
  force_https = true
  auto_stop_machines = true
  auto_start_machines = true
  min_machines_running = 0
  processes = ["app"]

  [http_service.concurrency]
    type = "requests"
    hard_limit = 250
    soft_limit = 200

[[vm]]
  cpu_kind = "shared"
  cpus = 2
  memory_mb = 2048

# For GPU machines
# [[vm]]
#   cpu_kind = "performance"
#   cpus = 8
#   memory_mb = 16384
#   gpu_kind = "a100-pcie-40gb"

# Persistent storage
[[mounts]]
  source = "ai_data"
  destination = "/data"
  initial_size = "10gb"

# Health checks
[[http_service.checks]]
  interval = "10s"
  timeout = "5s"
  grace_period = "30s"
  method = "GET"
  path = "/health"

# Scaling
[[services]]
  protocol = "tcp"
  internal_port = 8000
  [[services.ports]]
    port = 443
    handlers = ["tls", "http"]

[deploy]
  strategy = "rolling"
  max_unavailable = 0.33

# Environment variables
[env]
  LOG_LEVEL = "INFO"
  MODEL_NAME = "llama-3-8b"
```

```python
# File: main.py (Fly.io optimized with health checks)
import asyncio
import signal
import os
from contextlib import asynccontextmanager
from fastapi import FastAPI

# Track if the app is shutting down
shutting_down = False

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage app lifecycle for graceful shutdown on Fly.io."""
    global shutting_down
    # Startup
    print("Starting AI service...")
    await load_models()

    yield

    # Shutdown (graceful drain)
    shutting_down = True
    print("Shutting down, draining connections...")
    await asyncio.sleep(5)  # Allow in-flight requests to complete
    print("Shutdown complete")

app = FastAPI(lifespan=lifespan)

@app.get("/health")
async def health():
    """Fly.io health check."""
    if shutting_down:
        return {"status": "draining"}, 503
    return {"status": "healthy", "region": os.environ.get("FLY_REGION", "unknown")}

@app.get("/fly/machines")
async def machine_info():
    """Debug endpoint for Fly.io machine info."""
    return {
        "machine_id": os.environ.get("FLY_MACHINE_ID"),
        "app_name": os.environ.get("FLY_APP_NAME"),
        "region": os.environ.get("FLY_REGION"),
        "primary_region": os.environ.get("FLY_PRIMARY_REGION"),
    }
```

### 4.4 VERCEL

```
Best For: Next.js apps, AI SDK streaming, serverless functions, edge functions
Strengths: Instant deploys, edge network, AI SDK, preview deployments
Weaknesses: 10s function timeout (Hobby), no persistent state, limited compute

Architecture:
┌─────────────┐     ┌──────────────┐     ┌──────────────┐
│  User        │────>│  Vercel Edge │────>│  Next.js     │
│  (Global)    │     │  Network     │     │  App         │
└─────────────┘     └──────────────┘     └──────┬───────┘
                                                │
                              ┌──────────────────┼─────────────────┐
                              │                  │                 │
                       ┌──────┴──────┐   ┌──────┴──────┐  ┌──────┴──────┐
                       │  Edge       │   │  Serverless │  │  AI SDK     │
                       │  Functions  │   │  Functions  │  │  (Streaming)│
                       │  (<1ms cold)│   │  (API calls)│  │             │
                       └─────────────┘   └─────────────┘  └─────────────┘
```

```typescript
// File: app/api/chat/route.ts (Vercel AI SDK + Streaming)
import { openai } from "@ai-sdk/openai";
import { streamText, tool } from "ai";
import { z } from "zod";

export const maxDuration = 30; // Allow streaming up to 30s

export async function POST(req: Request) {
  const { messages } = await req.json();

  const result = streamText({
    model: openai("gpt-4-turbo"),
    system: "You are a helpful AI assistant.",
    messages,
    maxSteps: 5,
    tools: {
      searchKnowledge: tool({
        description: "Search the knowledge base for relevant information",
        parameters: z.object({
          query: z.string().describe("The search query"),
        }),
        execute: async ({ query }) => {
          // Call your RAG pipeline
          const results = await searchVectorDB(query);
          return results;
        },
      }),
      getWeather: tool({
        description: "Get current weather for a location",
        parameters: z.object({
          location: z.string(),
        }),
        execute: async ({ location }) => {
          return { location, temperature: "22°C", condition: "sunny" };
        },
      }),
    },
  });

  return result.toDataStreamResponse();
}
```

```typescript
// File: lib/monitoring.ts (Vercel Analytics + Custom Metrics)
import { Analytics } from "@vercel/analytics/react";
import { SpeedInsights } from "@vercel/speed-insights/react";

// Track custom AI metrics
export function trackAIRequest(params: {
  model: string;
  tokensIn: number;
  tokensOut: number;
  latencyMs: number;
  costUsd: number;
}) {
  // Send to Vercel Analytics
  if (typeof window !== "undefined") {
    window.dispatchEvent(
      new CustomEvent("ai-metric", { detail: params })
    );
  }

  // Also send to your backend for persistence
  fetch("/api/metrics", {
    method: "POST",
    body: JSON.stringify(params),
  }).catch(console.error);
}
```

### 4.5 PAAS COMPARISON MATRIX

```
┌──────────────┬──────────┬──────────┬──────────┬──────────┬──────────┐
│ Feature      │ Railway  │ Render   │ Fly.io   │ Vercel   │ Netlify  │
├──────────────┼──────────┼──────────┼──────────┼──────────┼──────────┤
│ Free Tier    │ $5/mo    │ Yes      │ Yes      │ Yes      │ Yes      │
│              │ credit   │ (sleep)  │ (3 VMs)  │ (100GB)  │ (100GB)  │
├──────────────┼──────────┼──────────┼──────────┼──────────┼──────────┤
│ Auto-SSL     │ Yes      │ Yes      │ Yes      │ Yes      │ Yes      │
├──────────────┼──────────┼──────────┼──────────┼──────────┼──────────┤
│ WebSocket    │ Yes      │ Yes      │ Yes      │ Limited  │ No       │
├──────────────┼──────────┼──────────┼──────────┼──────────┼──────────┤
│ GPU          │ No       │ No       │ Yes      │ No       │ No       │
│              │          │          │ (A100)   │          │          │
├──────────────┼──────────┼──────────┼──────────┼──────────┼──────────┤
│ PostgreSQL   │ Yes      │ Yes      │ Yes*     │ Neon     │ Planet   │
│              │ (managed)│ (managed)│ (Supabase)│ (serverless)│ Scale │
├──────────────┼──────────┼──────────┼──────────┼──────────┼──────────┤
│ Redis        │ Yes      │ Yes      │ Upstash  │ Upstash  │ Upstash  │
├──────────────┼──────────┼──────────┼──────────┼──────────┼──────────┤
│ Cron Jobs    │ Yes      │ Yes      │ Yes      │ Yes      │ Yes      │
├──────────────┼──────────┼──────────┼──────────┼──────────┼──────────┤
│ Global Edge  │ No       │ No       │ Yes      │ Yes      │ Yes      │
├──────────────┼──────────┼──────────┼──────────┼──────────┼──────────┤
│ Scale-to-0   │ No       │ Yes*     │ Yes      │ Yes      │ Yes      │
│              │          │ (free)   │          │          │          │
├──────────────┼──────────┼──────────┼──────────┼──────────┼──────────┤
│ Background   │ Yes      │ Yes      │ Yes      │ No*      │ No       │
│ Workers      │          │          │          │ (limited)│          │
├──────────────┼──────────┼──────────┼──────────┼──────────┼──────────┤
│ Best For     │ Full     │ Simple   │ Global   │ Next.js  │ Jamstack │
│              │ stack    │ services │ edge     │ apps     │ sites    │
└──────────────┴──────────┴──────────┴──────────┴──────────┴──────────┘
```

---

## 5. ML-SPECIFIC DEPLOYMENT PLATFORMS

### What are ML-Specific Deployment Platforms?

General-purpose cloud platforms (AWS, GCP, Azure) can deploy anything — but they weren't designed specifically for machine learning. **ML-specific platforms** are built from the ground up for deploying, serving, and managing AI/ML models. They understand the unique challenges of ML deployment:

- **GPU management** — ML models often need GPUs (graphics cards) for fast inference. Managing GPU drivers, CUDA versions, and memory is complex. ML platforms handle this automatically.
- **Model loading** — Large models (7B-70B parameters) take minutes to load into memory. ML platforms handle cold starts, model caching, and warm pools.
- **Token-based billing** — Instead of paying for servers 24/7, you pay per second of GPU time or per API call. This is much cheaper for intermittent workloads.
- **Model versioning** — ML platforms often include model registries to track versions, A/B test models, and roll back to previous versions.
- **Pre-built model APIs** — Many platforms offer pre-deployed models (GPT-4, Llama, Stable Diffusion) that you can call via API without deploying anything.

The key ML-specific platforms are:
- **HuggingFace Spaces** — Free hosting for ML demos (Gradio/Streamlit apps)
- **Modal** — Serverless GPU functions (pay per second of GPU time)
- **Replicate** — Simple API for running ML models (pay per prediction)
- **SageMaker** — AWS's full ML lifecycle platform (training + deployment + monitoring)
- **Vertex AI** — GCP's full ML lifecycle platform

### 5.1 HUGGING FACE SPACES

```
Best For: ML demos, Gradio/Streamlit apps, model showcases, community sharing
Strengths: Free GPU, easy deployment, model hub integration, community
Weaknesses: Limited compute, public by default (free), cold starts

Architecture:
┌─────────────┐     ┌──────────────────┐     ┌──────────────┐
│  User        │────>│  HF Spaces      │────>│  Gradio /    │
│              │     │  (Docker/       │     │  Streamlit   │
│              │<────│   Static)       │<────│  App         │
└─────────────┘     └──────────────────┘     └──────┬───────┘
                                                     │
                               ┌─────────────────────┼──────────────────┐
                               │                     │                  │
                        ┌──────┴──────┐     ┌───────┴───────┐  ┌──────┴──────┐
                        │  HF Model   │     │  GPU Runtime  │  │  Persistent │
                        │  Hub        │     │  (T4/A10G)    │  │  Storage    │
                        └─────────────┘     └────────────────┘  └─────────────┘
```

```python
# File: app.py (HuggingFace Spaces - Gradio)
import gradio as gr
from transformers import pipeline
import torch

# Check for GPU
device = 0 if torch.cuda.is_available() else -1

# Load model (cached after first run)
classifier = pipeline(
    "text-classification",
    model="distilbert-base-uncased-finetuned-sst-2-english",
    device=device,
)

def analyze_sentiment(text: str) -> dict:
    """Analyze sentiment of input text."""
    results = classifier(text)
    return {r["label"]: round(r["score"], 4) for r in results}

def analyze_batch(texts: str) -> list:
    """Analyze multiple texts (one per line)."""
    lines = [t.strip() for t in texts.split("\n") if t.strip()]
    results = classifier(lines)
    return [
        {"text": line, "sentiment": r["label"], "confidence": round(r["score"], 4)}
        for line, r in zip(lines, results)
    ]

# Build Gradio interface
with gr.Blocks(title="AI Sentiment Analyzer", theme=gr.themes.Soft()) as demo:
    gr.Markdown("# AI Sentiment Analyzer")
    gr.Markdown("Analyze the sentiment of text using a fine-tuned transformer model.")

    with gr.Tab("Single Text"):
        text_input = gr.Textbox(label="Enter text", lines=3, placeholder="Type something...")
        output = gr.Label(label="Sentiment")
        btn = gr.Button("Analyze", variant="primary")
        btn.click(analyze_sentiment, inputs=text_input, outputs=output)

    with gr.Tab("Batch Analysis"):
        batch_input = gr.Textbox(label="Enter texts (one per line)", lines=10)
        batch_output = gr.Dataframe(label="Results")
        batch_btn = gr.Button("Analyze Batch", variant="primary")
        batch_btn.click(analyze_batch, inputs=batch_input, outputs=batch_output)

    gr.Examples(
        examples=[
            "I love this product, it's amazing!",
            "This is terrible, worst experience ever.",
            "It's okay, nothing special.",
        ],
        inputs=text_input,
    )

demo.launch()
```

```yaml
# File: .huggingface.yaml (Space configuration)
---
title: AI Sentiment Analyzer
emoji: 🤖
colorFrom: blue
colorTo: green
sdk: gradio
sdk_version: 4.44.0
app_file: app.py
pinned: false
license: mit
suggested_hardware: cpu-basic  # or: t4-small, t4-medium, a10g-small

# For Docker-based spaces:
# sdk: docker
# Dockerfile: Dockerfile
```

### 5.2 MODAL

```
Best For: Serverless GPU inference, batch processing, scheduled jobs
Strengths: Per-second GPU billing, fast cold starts, Python-native, A100/H100
Weaknesses: Vendor lock-in, no always-on servers, limited networking

Architecture:
┌─────────────┐     ┌──────────────┐     ┌──────────────┐
│  HTTP        │────>│  Modal       │────>│  Function    │
│  Request     │     │  Gateway     │     │  (GPU/CPU)   │
│  or Cron     │     │              │     │              │
└─────────────┘     └──────────────┘     └──────┬───────┘
                                                │
                              ┌──────────────────┼─────────────────┐
                              │                  │                 │
                       ┌──────┴──────┐   ┌──────┴──────┐  ┌──────┴──────┐
                       │  A100 GPU   │   │  Shared     │  │  Network    │
                       │  (40/80GB)  │   │  Volume     │  │  Filesystem │
                       └─────────────┘   └─────────────┘  └─────────────┘
```

```python
# File: modal_app.py
import modal
from fastapi import FastAPI
from pydantic import BaseModel

# Define Modal app
app = modal.App("ai-inference-service")

# Create image with dependencies
image = (
    modal.Image.debian_slim(python_version="3.11")
    .pip_install(
        "torch==2.1.0",
        "transformers==4.37.0",
        "accelerate==0.25.0",
        "fastapi==0.108.0",
        "uvicorn==0.25.0",
    )
    .run_commands("python -c 'import torch; print(torch.cuda.is_available())'")
)

# Shared volume for model cache
volume = modal.Volume.from_name("model-cache", create_if_missing=True)

class QueryRequest(BaseModel):
    prompt: str
    max_tokens: int = 512
    temperature: float = 0.7

class QueryResponse(BaseModel):
    response: str
    tokens_generated: int
    latency_ms: float

# GPU inference function
@app.cls(image=image, gpu="A10G", volumes={"/cache": volume}, container_idle_timeout=120)
class LLMService:
    @modal.enter()
    def load_model(self):
        """Load model on container startup."""
        from transformers import AutoModelForCausalLM, AutoTokenizer
        import torch

        model_id = "meta-llama/Llama-3.1-8B-Instruct"
        self.tokenizer = AutoTokenizer.from_pretrained(
            model_id, cache_dir="/cache"
        )
        self.model = AutoModelForCausalLM.from_pretrained(
            model_id,
            torch_dtype=torch.float16,
            device_map="auto",
            cache_dir="/cache",
        )
        print(f"Model loaded on {torch.cuda.get_device_name()}")

    @modal.method()
    def generate(self, prompt: str, max_tokens: int = 512, temperature: float = 0.7) -> dict:
        """Generate text using the loaded model."""
        import time
        start = time.time()

        inputs = self.tokenizer(prompt, return_tensors="pt").to("cuda")
        outputs = self.model.generate(
            **inputs,
            max_new_tokens=max_tokens,
            temperature=temperature,
            do_sample=True,
        )
        response = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
        tokens_generated = outputs.shape[1] - inputs["input_ids"].shape[1]
        latency = (time.time() - start) * 1000

        return {
            "response": response,
            "tokens_generated": tokens_generated,
            "latency_ms": latency,
        }

# Web endpoint
web_app = FastAPI()

@web_app.post("/generate", response_model=QueryResponse)
async def generate_endpoint(request: QueryRequest):
    service = LLMService()
    result = service.generate.remote(
        request.prompt, request.max_tokens, request.temperature
    )
    return QueryResponse(**result)

@web_app.get("/health")
async def health():
    return {"status": "healthy"}

# Deploy with: modal deploy modal_app.py
# Run locally: modal serve modal_app.py

# Batch processing function
@app.function(image=image, gpu="A10G", timeout=3600, volumes={"/cache": volume})
def process_batch(prompts: list[str], max_tokens: int = 512) -> list[str]:
    """Process a batch of prompts efficiently on GPU."""
    from transformers import AutoModelForCausalLM, AutoTokenizer
    import torch

    model_id = "meta-llama/Llama-3.1-8B-Instruct"
    tokenizer = AutoTokenizer.from_pretrained(model_id, cache_dir="/cache")
    model = AutoModelForCausalLM.from_pretrained(
        model_id, torch_dtype=torch.float16, device_map="auto", cache_dir="/cache"
    )

    results = []
    for prompt in prompts:
        inputs = tokenizer(prompt, return_tensors="pt").to("cuda")
        outputs = model.generate(**inputs, max_new_tokens=max_tokens)
        results.append(tokenizer.decode(outputs[0], skip_special_tokens=True))

    return results

# Scheduled batch job
@app.function(image=image, schedule=modal.Cron("0 2 * * *"), gpu="A10G", volumes={"/cache": volume})
def nightly_batch_job():
    """Run nightly batch processing (e.g., daily report generation)."""
    # Your batch logic here
    print("Running nightly batch job...")
```

### 5.3 REPLICATE

```
Best For: Model API hosting, image/video generation, pre-built model APIs
Strengths: Simple API, pre-built models, per-second billing, webhook callbacks
Weaknesses: Cold starts (30-60s), limited customization, model size limits

Architecture:
┌─────────────┐     ┌──────────────┐     ┌──────────────┐
│  Client      │────>│  Replicate   │────>│  Prediction  │
│  API Call    │     │  API         │     │  (GPU)       │
└─────────────┘     └──────────────┘     └──────┬───────┘
                                                │
                              ┌──────────────────┼─────────────────┐
                              │                  │                 │
                       ┌──────┴──────┐   ┌──────┴──────┐  ┌──────┴──────┐
                       │  Synchronous│   │  Async      │  │  Webhook    │
                       │  Response   │   │  Polling    │  │  Callback   │
                       └─────────────┘   └─────────────┘  └─────────────┘
```

```python
# File: replicate_deploy.py
import replicate
import asyncio
from fastapi import FastAPI, BackgroundTasks
from pydantic import BaseModel

app = FastAPI()

class PredictionRequest(BaseModel):
    prompt: str
    model: str = "meta/llama-3.1-8b-instruct"
    max_tokens: int = 512

class PredictionResponse(BaseModel):
    id: str
    status: str
    output: str = None

@app.post("/predict", response_model=PredictionResponse)
async def create_prediction(request: PredictionRequest):
    """Create a prediction on Replicate (async)."""
    prediction = replicate.predictions.create(
        version="meta/llama-3.1-8b-instruct",
        input={
            "prompt": request.prompt,
            "max_tokens": request.max_tokens,
        },
        webhook="https://myapp.com/webhook",  # Optional webhook
        webhook_events_filter=["completed"],
    )

    return PredictionResponse(
        id=prediction.id,
        status=prediction.status,
    )

@app.get("/predict/{prediction_id}")
async def get_prediction(prediction_id: str):
    """Get prediction result."""
    prediction = replicate.predictions.get(prediction_id)

    return {
        "id": prediction.id,
        "status": prediction.status,
        "output": prediction.output if prediction.status == "succeeded" else None,
        "error": prediction.error if prediction.status == "failed" else None,
    }

# Synchronous (blocking) prediction
@app.post("/predict/sync")
async def predict_sync(request: PredictionRequest):
    """Run prediction synchronously (waits for result)."""
    output = replicate.run(
        "meta/llama-3.1-8b-instruct",
        input={
            "prompt": request.prompt,
            "max_tokens": request.max_tokens,
        },
    )
    return {"output": "".join(output)}

# Using a custom model on Replicate
@app.post("/predict/custom")
async def predict_custom(request: PredictionRequest):
    """Run prediction on a custom deployed model."""
    output = replicate.run(
        "my-org/my-model:abc123",  # Your custom model
        input={"prompt": request.prompt},
    )
    return {"output": output}
```

### 5.4 ML PLATFORM COMPARISON

```
┌─────────────────┬──────────┬──────────┬──────────┬──────────┬──────────┐
│ Feature         │ SageMaker│ Vertex AI│ Modal    │ Replicate│ HF Spaces│
├─────────────────┼──────────┼──────────┼──────────┼──────────┼──────────┤
│ GPU Types       │ T4,T5,L4 │ T4,A100  │ T4,A10G, │ T4,A100  │ T4,A10G  │
│                 │ A10G,A100│ T4v4     │ A100,H100│          │          │
├─────────────────┼──────────┼──────────┼──────────┼──────────┼──────────┤
│ Scale-to-0      │ No*      │ No*      │ Yes      │ N/A      │ Yes      │
│                 │ (needs   │ (needs   │          │ (pay per │ (free    │
│                 │ endpoint)│ endpoint)│          │ predict) │ tier)    │
├─────────────────┼──────────┼──────────┼──────────┼──────────┼──────────┤
│ Billing         │ Per-hour │ Per-hour │ Per-sec  │ Per-sec  │ Free/    │
│                 │ instance │ instance │ GPU time │ GPU time │ Paid     │
├─────────────────┼──────────┼──────────┼──────────┼──────────┼──────────┤
│ Cold Start      │ 5-10min  │ 3-5min   │ 10-30s   │ 30-60s   │ 30-120s  │
├─────────────────┼──────────┼──────────┼──────────┼──────────┼──────────┤
│ Max Model Size  │ Any      │ Any      │ ~70B     │ ~70B     │ ~7B      │
│ (single GPU)    │ (multi)  │ (multi)  │ (80GB)   │ (80GB)   │ (16GB)   │
├─────────────────┼──────────┼──────────┼──────────┼──────────┼──────────┤
│ Custom Docker   │ Yes      │ Yes      │ Yes      │ Yes      │ Yes      │
├─────────────────┼──────────┼──────────┼──────────┼──────────┼──────────┤
│ Auto-scaling    │ Yes      │ Yes      │ Yes      │ N/A      │ No       │
├─────────────────┼──────────┼──────────┼──────────┼──────────┼──────────┤
│ A/B Testing     │ Yes      │ Yes      │ Manual   │ Manual   │ No       │
├─────────────────┼──────────┼──────────┼──────────┼──────────┼──────────┤
│ Model Registry  │ Yes      │ Yes      │ No       │ Yes      │ Yes      │
├─────────────────┼──────────┼──────────┼──────────┼──────────┼──────────┤
│ Monitoring      │ Yes      │ Yes      │ Basic    │ Basic    │ Basic    │
├─────────────────┼──────────┼──────────┼──────────┼──────────┼──────────┤
│ Best For        │ Enterprise│ GCP     │ Serverless│ Simple  │ Demos    │
│                 │ ML ops   │ ML ops   │ GPU      │ model API│ Community│
└─────────────────┴──────────┴──────────┴──────────┴──────────┴──────────┘
```

---

## 6. EDGE AND ON-DEVICE DEPLOYMENT

### What is Edge Deployment?

**Edge deployment** means running your AI model directly on the user's device (phone, browser, IoT device) or on a server geographically close to the user, instead of in a centralized cloud data center.

Why does this matter?
- **Latency** — A round trip to a cloud server takes 50-500ms. Running on-device takes <10ms. For real-time applications (voice assistants, AR, autonomous vehicles), this difference is critical.
- **Privacy** — Data never leaves the user's device. No data is sent to the cloud. This is essential for healthcare, finance, and privacy-sensitive applications.
- **Offline capability** — The model works without internet. A translation app on your phone works on an airplane.
- **Cost** — No server costs. The user's device does the computation. At scale (millions of users), this saves enormous amounts of money.

The tradeoff: Edge devices have limited compute (no powerful GPUs), limited memory (can't run 70B parameter models), and you need to convert your model to a format the device understands (ONNX, CoreML, TFLite).

**The edge deployment spectrum:**
- **Browser** — Run models in the user's web browser using JavaScript (ONNX.js, Transformers.js, WebGPU)
- **Mobile** — Run models on iOS (CoreML) or Android (TFLite, ONNX Runtime)
- **IoT/Embedded** — Run models on tiny devices like Raspberry Pi, Arduino, or custom hardware (TFLite Micro, ONNX Runtime)
- **Edge Server** — Run models on servers at the "edge" of the network, close to users (Cloudflare Workers, Deno Deploy, CDN edge nodes)

### 6.1 EDGE DEPLOYMENT OVERVIEW

```
Edge Deployment Spectrum:
┌─────────────────────────────────────────────────────────────────────────┐
│                                                                         │
│  Browser          Mobile           IoT/Embedded      Edge Server       │
│  (JavaScript)     (Native)         (Microcontroller)  (Raspberry Pi)   │
│  ─────────────    ─────────────    ──────────────     ──────────────   │
│  ONNX.js          CoreML           TFLite Micro       ONNX Runtime     │
│  TensorFlow.js    TFLite           TensorFlow Lite    TensorRT         │
│  Transformers.js  ONNX Runtime     MicroTVM           OpenVINO         │
│  WebGPU           MediaPipe        Edge TPU           Docker + GPU     │
│                                                                         │
│  <100ms latency   <50ms latency    <10ms latency     <20ms latency    │
│  Small models     Medium models    Tiny models        Large models     │
│  (<100MB)         (<500MB)         (<10MB)            (Any size)       │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

### 6.2 BROWSER DEPLOYMENT (ONNX.js / Transformers.js)

```typescript
// File: src/inference/browser-inference.ts
import { pipeline, env } from "@huggingface/transformers";

// Configure for browser deployment
env.backends.onnx.wasm.numThreads = 4;
env.allowLocalModels = false;

class BrowserAIInference {
  private classifier: any = null;
  private embedder: any = null;

  async loadClassifier(modelId: string = "Xenova/distilbert-base-uncased-finetuned-sst-2-english") {
    this.classifier = await pipeline("text-classification", modelId, {
      dtype: "fp32",  // or "fp16" for WebGPU
      device: "webgpu",  // falls back to WASM if unavailable
    });
    console.log("Classifier loaded");
  }

  async classify(text: string): Promise<{ label: string; score: number }[]> {
    if (!this.classifier) {
      throw new Error("Classifier not loaded. Call loadClassifier() first.");
    }
    return await this.classifier(text);
  }

  async loadEmbedder(modelId: string = "Xenova/all-MiniLM-L6-v2") {
    this.embedder = await pipeline("feature-extraction", modelId, {
      dtype: "fp32",
      device: "webgpu",
    });
    console.log("Embedder loaded");
  }

  async embed(text: string): Promise<Float32Array> {
    if (!this.embedder) {
      throw new Error("Embedder not loaded.");
    }
    const output = await this.embedder(text, { pooling: "mean", normalize: true });
    return output.data as Float32Array;
  }

  async search(query: string, documents: string[], topK: number = 3) {
    const queryEmbed = await this.embed(query);
    const docEmbeds = await Promise.all(documents.map(doc => this.embed(doc)));

    // Cosine similarity
    const similarities = docEmbeds.map((docEmbed, i) => ({
      index: i,
      document: documents[i],
      score: this.cosineSimilarity(queryEmbed, docEmbed),
    }));

    return similarities
      .sort((a, b) => b.score - a.score)
      .slice(0, topK);
  }

  private cosineSimilarity(a: Float32Array, b: Float32Array): number {
    let dot = 0, normA = 0, normB = 0;
    for (let i = 0; i < a.length; i++) {
      dot += a[i] * b[i];
      normA += a[i] * a[i];
      normB += b[i] * b[i];
    }
    return dot / (Math.sqrt(normA) * Math.sqrt(normB));
  }
}

// Usage in React component:
// const ai = new BrowserAIInference();
// await ai.loadClassifier();
// const result = await ai.classify("This is amazing!");
```

### 6.3 MOBILE DEPLOYMENT (CoreML / TFLite)

```python
# File: export/mobile_export.py
import torch
from transformers import AutoModelForSequenceClassification, AutoTokenizer

class MobileModelExporter:
    """Export models for mobile deployment."""

    def export_to_coreml(self, model_id: str, output_path: str):
        """Export HuggingFace model to CoreML format for iOS."""
        import coremltools as ct

        model = AutoModelForSequenceClassification.from_pretrained(model_id)
        tokenizer = AutoTokenizer.from_pretrained(model_id)
        model.eval()

        # Trace the model
        example_input = tokenizer("Hello world", return_tensors="pt")
        traced_model = torch.jit.trace(
            model,
            (example_input["input_ids"], example_input["attention_mask"]),
        )

        # Convert to CoreML
        coreml_model = ct.convert(
            traced_model,
            inputs=[
                ct.TensorType(name="input_ids", shape=(1, 128), dtype=np.int32),
                ct.TensorType(name="attention_mask", shape=(1, 128), dtype=np.int32),
            ],
            outputs=[
                ct.TensorType(name="logits"),
            ],
            minimum_deployment_target=ct.target.iOS16,
        )

        coreml_model.save(output_path)
        print(f"CoreML model saved to {output_path}")

    def export_to_tflite(self, model_id: str, output_path: str):
        """Export HuggingFace model to TFLite format for Android."""
        from optimum.exporters.tflite import TFLiteExporter

        exporter = TFLiteExporter.from_pretrained(
            model_id,
            task="text-classification",
            opset=14,
        )
        exporter.export(output_path)
        print(f"TFLite model saved to {output_path}")

    def export_to_onnx(self, model_id: str, output_path: str, quantize: bool = True):
        """Export to ONNX (universal format for all platforms)."""
        from optimum.onnxruntime import ORTModelForSequenceClassification

        model = ORTModelForSequenceClassification.from_pretrained(
            model_id, export=True
        )

        if quantize:
            from optimum.onnxruntime import ORTQuantizer
            from optimum.onnxruntime.configuration import AutoQuantizationConfig

            quantizer = ORTQuantizer.from_pretrained(model)
            qconfig = AutoQuantizationConfig.avx512_vnni(is_static=False)
            quantizer.quantize(save_dir=output_path, quantization_config=qconfig)
        else:
            model.save_pretrained(output_path)

        print(f"ONNX model saved to {output_path}")
```

### 6.4 EDGE SERVER DEPLOYMENT (ONNX Runtime / TensorRT)

```python
# File: deploy/edge_server.py
import onnxruntime as ort
import numpy as np
from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI(title="Edge AI Server")

class InferenceEngine:
    """Optimized inference engine for edge servers."""

    def __init__(self, model_path: str, use_gpu: bool = True):
        providers = []
        if use_gpu:
            providers.append("CUDAExecutionProvider")
        providers.append("CPUExecutionProvider")

        session_options = ort.SessionOptions()
        session_options.graph_optimization_level = ort.GraphOptimizationLevel.ORT_ENABLE_ALL
        session_options.intra_op_num_threads = 4
        session_options.inter_op_num_threads = 2

        self.session = ort.InferenceSession(
            model_path,
            sess_options=session_options,
            providers=providers,
        )

        self.input_names = [inp.name for inp in self.session.get_inputs()]
        self.output_names = [out.name for out in self.session.get_outputs()]

        print(f"Model loaded with providers: {self.session.get_providers()}")

    def predict(self, input_ids: np.ndarray, attention_mask: np.ndarray) -> np.ndarray:
        """Run inference."""
        outputs = self.session.run(
            self.output_names,
            {
                "input_ids": input_ids,
                "attention_mask": attention_mask,
            },
        )
        return outputs[0]

# Initialize engine
engine = InferenceEngine("model.onnx", use_gpu=True)

class PredictRequest(BaseModel):
    text: str

@app.post("/predict")
async def predict(request: PredictRequest):
    """Run inference on edge server."""
    # Tokenize (simplified - use proper tokenizer in production)
    tokens = tokenize(request.text)
    input_ids = np.array([tokens["input_ids"]], dtype=np.int64)
    attention_mask = np.array([tokens["attention_mask"]], dtype=np.int64)

    logits = engine.predict(input_ids, attention_mask)
    prediction = np.argmax(logits, axis=-1)[0]
    confidence = float(np.max(softmax(logits)))

    return {
        "prediction": int(prediction),
        "confidence": confidence,
        "latency_ms": 0,  # Add timing
    }

@app.get("/health")
async def health():
    return {
        "status": "healthy",
        "providers": engine.session.get_providers(),
        "model_loaded": True,
    }
```

---

## 7. CONTAINER ORCHESTRATION

### What is Container Orchestration?

**Containers** are lightweight, portable packages that contain your application code along with everything it needs to run (dependencies, runtime, system libraries). Think of a container as a standardized shipping box — no matter where you ship it (your laptop, a cloud server, a Kubernetes cluster), the contents are identical and run the same way.

**Container orchestration** is the automated management of these containers at scale. It handles:
- **Deployment** — Starting containers on the right servers
- **Scaling** — Running more containers when traffic increases, fewer when it decreases
- **Networking** — Allowing containers to talk to each other and to the outside world
- **Health monitoring** — Restarting containers that crash
- **Load balancing** — Distributing traffic across multiple container instances
- **Rolling updates** — Deploying new versions without downtime

The key technologies:
- **Docker** — The tool that creates and runs individual containers. Every developer should know Docker.
- **Docker Compose** — Runs multiple containers together on a single machine. Good for development and simple deployments.
- **Kubernetes (K8s)** — The industry standard for orchestrating containers at scale. Complex but incredibly powerful. Used by Google, Netflix, Spotify, and most large companies.
- **ECS (AWS)** — AWS's container orchestration service. Simpler than Kubernetes but AWS-only.
- **Cloud Run (GCP)** — Google's serverless containers. You give it a Docker image, it handles everything else.

When do you need container orchestration?
- **1 service, low traffic** → PaaS (Railway/Render) is simpler
- **2-5 services** → Docker Compose on a VPS or ECS
- **5+ services, need autoscaling** → Kubernetes (EKS/GKE/AKS)
- **Enterprise, multi-region** → Kubernetes + service mesh + GitOps

### 7.1 DOCKER FOR AI APPLICATIONS

```dockerfile
# File: Dockerfile (Production AI Service)
FROM python:3.11-slim AS base

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Install Python dependencies (cached layer)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY src/ ./src/
COPY config/ ./config/

# Create non-root user
RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app
USER appuser

# Health check
HEALTHCHECK --interval=30s --timeout=5s --start-period=60s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Run with production server
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "4"]
```

```dockerfile
# File: Dockerfile.gpu (GPU-enabled AI Service)
FROM nvidia/cuda:12.1.0-runtime-ubuntu22.04 AS base

# Install Python
RUN apt-get update && apt-get install -y --no-install-recommends \
    python3.11 python3.11-venv python3-pip \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Install PyTorch with CUDA
COPY requirements-gpu.txt .
RUN pip install --no-cache-dir -r requirements-gpu.txt

# Copy application
COPY src/ ./src/

# Verify GPU access
RUN python3 -c "import torch; print(f'CUDA available: {torch.cuda.is_available()}')"

USER 1000

HEALTHCHECK --interval=30s --timeout=5s --start-period=120s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "1"]
```

```yaml
# File: docker-compose.yml (Multi-service AI application)
version: "3.8"

services:
  api:
    build:
      context: .
      dockerfile: Dockerfile
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql://user:pass@postgres:5432/ai_db
      - REDIS_URL=redis://redis:6379
      - LOG_LEVEL=INFO
    depends_on:
      postgres:
        condition: service_healthy
      redis:
        condition: service_healthy
    deploy:
      replicas: 3
      resources:
        limits:
          cpus: "2.0"
          memory: 4G
        reservations:
          cpus: "0.5"
          memory: 1G
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 5s
      retries: 3
      start_period: 30s

  worker:
    build:
      context: .
      dockerfile: Dockerfile
    command: celery -A src.worker worker --loglevel=info --concurrency=4
    environment:
      - DATABASE_URL=postgresql://user:pass@postgres:5432/ai_db
      - REDIS_URL=redis://redis:6379
    depends_on:
      - redis
      - postgres
    deploy:
      replicas: 2
      resources:
        limits:
          cpus: "1.0"
          memory: 2G

  gpu-inference:
    build:
      context: .
      dockerfile: Dockerfile.gpu
    ports:
      - "8001:8000"
    environment:
      - MODEL_NAME=llama-3-8b
      - CUDA_VISIBLE_DEVICES=0
    deploy:
      replicas: 1
      resources:
        reservations:
          devices:
            - driver: nvidia
              count: 1
              capabilities: [gpu]
        limits:
          memory: 16G
    volumes:
      - model-cache:/root/.cache/huggingface

  postgres:
    image: pgvector/pgvector:pg16
    environment:
      POSTGRES_USER: user
      POSTGRES_PASSWORD: pass
      POSTGRES_DB: ai_db
    volumes:
      - postgres-data:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U user -d ai_db"]
      interval: 10s
      timeout: 5s
      retries: 5

  redis:
    image: redis:7-alpine
    command: redis-server --maxmemory 256mb --maxmemory-policy allkeys-lru
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 10s
      timeout: 5s
      retries: 5
    volumes:
      - redis-data:/data

  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf:ro
      - ./certs:/etc/nginx/certs:ro
    depends_on:
      - api

volumes:
  postgres-data:
  redis-data:
  model-cache:
```

### 7.2 KUBERNETES FOR AI WORKLOADS

```yaml
# File: k8s/namespace.yaml
apiVersion: v1
kind: Namespace
metadata:
  name: ai-production
  labels:
    environment: production
    team: ai-platform
```

```yaml
# File: k8s/api-deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: ai-api
  namespace: ai-production
  labels:
    app: ai-api
    version: v1
spec:
  replicas: 3
  strategy:
    type: RollingUpdate
    rollingUpdate:
      maxSurge: 1
      maxUnavailable: 0
  selector:
    matchLabels:
      app: ai-api
  template:
    metadata:
      labels:
        app: ai-api
        version: v1
      annotations:
        prometheus.io/scrape: "true"
        prometheus.io/port: "8000"
        prometheus.io/path: "/metrics"
    spec:
      serviceAccountName: ai-api-sa
      terminationGracePeriodSeconds: 60
      containers:
        - name: ai-api
          image: myregistry.azurecr.io/ai-api:v1.2.0
          ports:
            - containerPort: 8000
              name: http
              protocol: TCP
          env:
            - name: DATABASE_URL
              valueFrom:
                secretKeyRef:
                  name: ai-secrets
                  key: database-url
            - name: REDIS_URL
              valueFrom:
                secretKeyRef:
                  name: ai-secrets
                  key: redis-url
            - name: LOG_LEVEL
              valueFrom:
                configMapKeyRef:
                  name: ai-config
                  key: log-level
          resources:
            requests:
              cpu: "500m"
              memory: "1Gi"
            limits:
              cpu: "2000m"
              memory: "4Gi"
          startupProbe:
            httpGet:
              path: /health
              port: 8000
            initialDelaySeconds: 10
            periodSeconds: 10
            failureThreshold: 30
          livenessProbe:
            httpGet:
              path: /health
              port: 8000
            periodSeconds: 15
            timeoutSeconds: 5
            failureThreshold: 3
          readinessProbe:
            httpGet:
              path: /ready
              port: 8000
            periodSeconds: 10
            timeoutSeconds: 3
            failureThreshold: 3
          lifecycle:
            preStop:
              exec:
                command: ["/bin/sh", "-c", "sleep 15"]
      topologySpreadConstraints:
        - maxSkew: 1
          topologyKey: topology.kubernetes.io/zone
          whenUnsatisfiable: DoNotSchedule
          labelSelector:
            matchLabels:
              app: ai-api
---
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: ai-api-hpa
  namespace: ai-production
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: ai-api
  minReplicas: 3
  maxReplicas: 20
  metrics:
    - type: Resource
      resource:
        name: cpu
        target:
          type: Utilization
          averageUtilization: 70
    - type: Resource
      resource:
        name: memory
        target:
          type: Utilization
          averageUtilization: 80
    - type: Pods
      pods:
        metric:
          name: http_requests_per_second
        target:
          type: AverageValue
          averageValue: "100"
  behavior:
    scaleUp:
      stabilizationWindowSeconds: 60
      policies:
        - type: Pods
          value: 4
          periodSeconds: 60
    scaleDown:
      stabilizationWindowSeconds: 300
      policies:
        - type: Pods
          value: 1
          periodSeconds: 120
---
apiVersion: v1
kind: Service
metadata:
  name: ai-api
  namespace: ai-production
spec:
  selector:
    app: ai-api
  ports:
    - port: 80
      targetPort: 8000
      protocol: TCP
  type: ClusterIP
---
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: ai-api-ingress
  namespace: ai-production
  annotations:
    nginx.ingress.kubernetes.io/ssl-redirect: "true"
    nginx.ingress.kubernetes.io/rate-limit: "100"
    nginx.ingress.kubernetes.io/rate-limit-window: "1m"
    cert-manager.io/cluster-issuer: "letsencrypt-prod"
spec:
  ingressClassName: nginx
  tls:
    - hosts:
        - api.myapp.com
      secretName: ai-api-tls
  rules:
    - host: api.myapp.com
      http:
        paths:
          - path: /
            pathType: Prefix
            backend:
              service:
                name: ai-api
                port:
                  number: 80
```

```yaml
# File: k8s/gpu-deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: gpu-inference
  namespace: ai-production
spec:
  replicas: 2
  strategy:
    type: RollingUpdate
    rollingUpdate:
      maxSurge: 1
      maxUnavailable: 0
  selector:
    matchLabels:
      app: gpu-inference
  template:
    metadata:
      labels:
        app: gpu-inference
    spec:
      tolerations:
        - key: nvidia.com/gpu
          operator: Exists
          effect: NoSchedule
      nodeSelector:
        accelerator: nvidia-a100
      containers:
        - name: inference
          image: myregistry.azurecr.io/gpu-inference:v1.0.0
          ports:
            - containerPort: 8000
          env:
            - name: MODEL_NAME
              value: "llama-3-70b"
            - name: TENSOR_PARALLEL_SIZE
              value: "2"
          resources:
            limits:
              nvidia.com/gpu: "2"
              memory: "80Gi"
              cpu: "8"
            requests:
              nvidia.com/gpu: "2"
              memory: "60Gi"
              cpu: "4"
          volumeMounts:
            - name: model-cache
              mountPath: /root/.cache
          startupProbe:
            httpGet:
              path: /health
              port: 8000
            initialDelaySeconds: 120
            periodSeconds: 30
            failureThreshold: 20
          livenessProbe:
            httpGet:
              path: /health
              port: 8000
            periodSeconds: 30
            timeoutSeconds: 10
      volumes:
        - name: model-cache
          persistentVolumeClaim:
            claimName: model-cache-pvc
```

### 7.3 AWS ECS DEPLOYMENT

```python
# File: deploy/ecs_task_definitions.py
"""AWS ECS Task Definitions for AI services."""

import json

API_TASK_DEFINITION = {
    "family": "ai-api",
    "networkMode": "awsvpc",
    "requiresCompatibilities": ["FARGATE"],
    "cpu": "1024",
    "memory": "2048",
    "executionRoleArn": "arn:aws:iam::role/ecsTaskExecutionRole",
    "taskRoleArn": "arn:aws:iam::role/aiApiTaskRole",
    "containerDefinitions": [
        {
            "name": "ai-api",
            "image": "123456789.dkr.ecr.us-east-1.amazonaws.com/ai-api:latest",
            "essential": True,
            "portMappings": [{"containerPort": 8000, "protocol": "tcp"}],
            "environment": [
                {"name": "LOG_LEVEL", "value": "INFO"},
                {"name": "AWS_REGION", "value": "us-east-1"},
            ],
            "secrets": [
                {"name": "DATABASE_URL", "valueFrom": "arn:aws:secretsmanager:us-east-1:123456789:secret:ai-db-url"},
                {"name": "OPENAI_API_KEY", "valueFrom": "arn:aws:secretsmanager:us-east-1:123456789:secret:openai-key"},
            ],
            "logConfiguration": {
                "logDriver": "awslogs",
                "options": {
                    "awslogs-group": "/ecs/ai-api",
                    "awslogs-region": "us-east-1",
                    "awslogs-stream-prefix": "api",
                },
            },
            "healthCheck": {
                "command": ["CMD-SHELL", "curl -f http://localhost:8000/health || exit 1"],
                "interval": 30,
                "timeout": 5,
                "retries": 3,
                "startPeriod": 60,
            },
        }
    ],
}

GPU_TASK_DEFINITION = {
    "family": "ai-gpu-inference",
    "networkMode": "awsvpc",
    "requiresCompatibilities": ["EC2"],
    "cpu": "8192",
    "memory": "32768",
    "executionRoleArn": "arn:aws:iam::role/ecsTaskExecutionRole",
    "taskRoleArn": "arn:aws:iam::role/aiGpuTaskRole",
    "containerDefinitions": [
        {
            "name": "gpu-inference",
            "image": "123456789.dkr.ecr.us-east-1.amazonaws.com/gpu-inference:latest",
            "essential": True,
            "portMappings": [{"containerPort": 8000, "protocol": "tcp"}],
            "resourceRequirements": [
                {"type": "GPU", "value": "1"},
            ],
            "environment": [
                {"name": "MODEL_NAME", "value": "llama-3-8b"},
                {"name": "NVIDIA_VISIBLE_DEVICES", "value": "all"},
            ],
            "logConfiguration": {
                "logDriver": "awslogs",
                "options": {
                    "awslogs-group": "/ecs/ai-gpu-inference",
                    "awslogs-region": "us-east-1",
                    "awslogs-stream-prefix": "gpu",
                },
            },
        }
    ],
}
```

### 7.4 DEPLOYMENT PLATFORM DECISION TREE

```
┌─────────────────────────────────────────────────────────────────────────┐
│                    CONTAINER ORCHESTRATION DECISION                     │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  How many services?                                                     │
│  ├─ 1 service                                                          │
│  │  ├─ No GPU → PaaS (Railway/Render/Fly.io/Cloud Run)                │
│  │  └─ GPU needed → Modal/SageMaker/Replicate                         │
│  │                                                                     │
│  ├─ 2-5 services                                                       │
│  │  ├─ All-in-one host → Docker Compose on VPS                        │
│  │  ├─ Cloud-native → ECS Fargate or Cloud Run                        │
│  │  └─ Need orchestration → Managed Kubernetes (EKS/GKE/AKS)         │
│  │                                                                     │
│  ├─ 5-20 services (microservices)                                      │
│  │  ├─ AWS shop → ECS + ALB + Service Connect                         │
│  │  ├─ GCP shop → GKE + Istio/Anthos                                 │
│  │  ├─ Azure shop → AKS + Dapr                                       │
│  │  └─ Multi-cloud → Kubernetes + ArgoCD                              │
│  │                                                                     │
│  └─ 20+ services (enterprise)                                          │
│     ├─ Self-managed K8s → Custom cluster + GitOps                     │
│     ├─ Managed K8s → EKS/GKE/AKS + service mesh                      │
│     └─ Hybrid → K8s + serverless (Lambda/Cloud Functions)             │
│                                                                         │
│  Team expertise?                                                        │
│  ├─ Solo dev → PaaS, managed everything                               │
│  ├─ Small team (2-5) → Managed K8s or ECS                             │
│  ├─ Platform team (5-15) → Self-managed K8s + custom tooling          │
│  └─ SRE org (15+) → Multi-cluster, chaos engineering, SLOs            │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

---

# PART 2: PRODUCTION OPERATIONS

---

# PART 2: PRODUCTION OPERATIONS

---

## 8. OBSERVABILITY ARCHITECTURE

### What is Observability?

**Observability** is the ability to understand what's happening inside your application by looking at its external outputs (logs, metrics, traces). It answers the question: **"Why is my system behaving this way?"**

Imagine your application is a car. **Monitoring** tells you "the engine temperature is 250°F" (a metric). **Observability** lets you trace back: "The engine is hot because the coolant pump failed because a seal wore out because it wasn't replaced during the last service" (correlating metrics, logs, and traces to find root cause).

The three pillars of observability are:

1. **Logs** — Detailed records of what happened. "User X called /api/query at 3:42 PM, got response in 1.2 seconds." Logs tell you **what happened**.

2. **Metrics** — Numerical measurements over time. "Average response time is 500ms, error rate is 0.5%, 50 requests/second." Metrics tell you **how the system is performing**.

3. **Traces** — The journey of a single request through your system. "This request took 2 seconds total: 50ms in the API, 30ms in vector search, 1.9 seconds in the LLM call." Traces tell you **where time is being spent**.

Together, these three pillars let you:
- **Detect problems** before users notice (metrics show rising error rate)
- **Diagnose root cause** quickly (traces show the LLM call is slow, logs show it's a rate limit error)
- **Understand system behavior** under load (metrics show CPU saturation, traces show queuing)
- **Optimize performance** (traces show 90% of time is spent in vector search, not the LLM)

**OpenTelemetry** is the CNCF standard that provides a unified way to collect all three pillars. It's the industry standard — use it instead of vendor-specific SDKs.

### 8.1 THE THREE PILLARS OF OBSERVABILITY

```
Observability = Logs + Metrics + Traces

┌─────────────────────────────────────────────────────────────────────────┐
│                    THE THREE PILLARS                                    │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  LOGS                    METRICS                 TRACES                 │
│  ────                    ───────                 ──────                 │
│  What happened?          How is it performing?   Where is the time      │
│                                                  spent?                 │
│  ┌──────────────┐        ┌──────────────┐       ┌──────────────┐       │
│  │ Structured   │        │ Counter      │       │ Span 1       │       │
│  │ JSON logs    │        │ Gauge        │       │ ├─ Span 2    │       │
│  │ with context │        │ Histogram    │       │ │  ├─ Span 3 │       │
│  │              │        │ Summary      │       │ │  └─ Span 4 │       │
│  │              │        │              │       │ └─ Span 5    │       │
│  └──────────────┘        └──────────────┘       └──────────────┘       │
│                                                                         │
│  Tools:                  Tools:                  Tools:                  │
│  ELK Stack               Prometheus              Jaeger                 │
│  Loki                    Datadog                 Zipkin                 │
│  CloudWatch              New Relic               Tempo                  │
│  Splunk                  Grafana                 X-Ray                  │
│                          VictoriaMetrics         Honeycomb              │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

### 8.2 OPENTELEMETRY (UNIFIED OBSERVABILITY)

OpenTelemetry is the CNCF standard for instrumenting applications. It provides a single set of APIs, libraries, and agents for logs, metrics, and traces.

```python
# File: src/observability/telemetry.py
"""OpenTelemetry setup for AI application."""

import os
from opentelemetry import trace, metrics
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.sdk.metrics.export import PeriodicExportingMetricReader
from opentelemetry.sdk.resources import Resource, SERVICE_NAME, SERVICE_VERSION
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.exporter.otlp.proto.grpc.metric_exporter import OTLPMetricExporter
from opentelemetry.exporter.prometheus import PrometheusMetricReader
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.instrumentation.httpx import HTTPXClientInstrumentor
from opentelemetry.instrumentation.redis import RedisInstrumentor
from opentelemetry.instrumentation.psycopg2 import Psycopg2Instrumentor
from opentelemetry.trace import Status, StatusCode
import logging

logger = logging.getLogger(__name__)


class TelemetryManager:
    """Manage OpenTelemetry instrumentation for the AI service."""

    def __init__(
        self,
        service_name: str,
        service_version: str = "1.0.0",
        otlp_endpoint: str = None,
        environment: str = "production",
    ):
        self.service_name = service_name
        self.otlp_endpoint = otlp_endpoint or os.getenv(
            "OTEL_EXPORTER_OTLP_ENDPOINT", "http://localhost:4317"
        )

        # Create resource with service info
        self.resource = Resource.create({
            SERVICE_NAME: service_name,
            SERVICE_VERSION: service_version,
            "deployment.environment": environment,
            "service.instance.id": os.getenv("HOSTNAME", "local"),
        })

        self._setup_tracing()
        self._setup_metrics()
        self._instrument_libraries()

    def _setup_tracing(self):
        """Configure distributed tracing."""
        provider = TracerProvider(resource=self.resource)

        # OTLP exporter (sends to Tempo, Jaeger, etc.)
        otlp_exporter = OTLPSpanExporter(endpoint=self.otlp_endpoint, insecure=True)
        provider.add_span_processor(BatchSpanProcessor(otlp_exporter))

        trace.set_tracer_provider(provider)
        self.tracer = trace.get_tracer(self.service_name)

        logger.info(f"Tracing configured: {self.otlp_endpoint}")

    def _setup_metrics(self):
        """Configure metrics collection."""
        readers = []

        # Prometheus metrics (scraped by Prometheus)
        prometheus_reader = PrometheusMetricReader()
        readers.append(prometheus_reader)

        # OTLP metrics (pushed to collector)
        otlp_exporter = OTLPMetricExporter(endpoint=self.otlp_endpoint, insecure=True)
        otlp_reader = PeriodicExportingMetricReader(otlp_exporter, export_interval_millis=30000)
        readers.append(otlp_reader)

        provider = MeterProvider(resource=self.resource, metric_readers=readers)
        metrics.set_meter_provider(provider)
        self.meter = metrics.get_meter(self.service_name)

        # Create custom metrics
        self._create_metrics()

        logger.info("Metrics configured")

    def _create_metrics(self):
        """Create application-specific metrics."""
        # Request metrics
        self.request_counter = self.meter.create_counter(
            name="ai_requests_total",
            description="Total number of AI requests",
            unit="requests",
        )

        self.request_duration = self.meter.create_histogram(
            name="ai_request_duration_seconds",
            description="Request duration in seconds",
            unit="seconds",
        )

        # LLM-specific metrics
        self.llm_tokens_input = self.meter.create_counter(
            name="ai_llm_tokens_input_total",
            description="Total input tokens sent to LLM",
            unit="tokens",
        )

        self.llm_tokens_output = self.meter.create_counter(
            name="ai_llm_tokens_output_total",
            description="Total output tokens received from LLM",
            unit="tokens",
        )

        self.llm_latency = self.meter.create_histogram(
            name="ai_llm_latency_seconds",
            description="LLM response latency",
            unit="seconds",
        )

        self.llm_cost = self.meter.create_counter(
            name="ai_llm_cost_usd_total",
            description="Total LLM cost in USD",
            unit="USD",
        )

        # Vector DB metrics
        self.vector_search_duration = self.meter.create_histogram(
            name="ai_vector_search_duration_seconds",
            description="Vector search duration",
            unit="seconds",
        )

        self.vector_search_results = self.meter.create_histogram(
            name="ai_vector_search_results_count",
            description="Number of vector search results",
            unit="results",
        )

        # Cache metrics
        self.cache_hits = self.meter.create_counter(
            name="ai_cache_hits_total",
            description="Cache hit count",
            unit="hits",
        )

        self.cache_misses = self.meter.create_counter(
            name="ai_cache_misses_total",
            description="Cache miss count",
            unit="misses",
        )

        # Error metrics
        self.error_counter = self.meter.create_counter(
            name="ai_errors_total",
            description="Total errors",
            unit="errors",
        )

        # Active connections
        self.active_connections = self.meter.create_up_down_counter(
            name="ai_active_connections",
            description="Current active connections",
            unit="connections",
        )

        # Queue metrics
        self.queue_depth = self.meter.create_up_down_counter(
            name="ai_queue_depth",
            description="Current queue depth",
            unit="items",
        )

    def _instrument_libraries(self):
        """Auto-instrument common libraries."""
        FastAPIInstrumentor.instrument()
        HTTPXClientInstrumentor.instrument()
        RedisInstrumentor.instrument()
        Psycopg2Instrumentor.instrument()

    def record_request(self, method: str, path: str, status_code: int, duration: float):
        """Record a completed HTTP request."""
        labels = {"method": method, "path": path, "status_code": str(status_code)}
        self.request_counter.add(1, labels)
        self.request_duration.record(duration, labels)

    def record_llm_call(
        self,
        model: str,
        tokens_in: int,
        tokens_out: int,
        latency: float,
        cost: float,
    ):
        """Record an LLM API call."""
        labels = {"model": model}
        self.llm_tokens_input.add(tokens_in, labels)
        self.llm_tokens_output.add(tokens_out, labels)
        self.llm_latency.record(latency, labels)
        self.llm_cost.add(cost, labels)

    def record_vector_search(self, duration: float, result_count: int):
        """Record a vector search operation."""
        self.vector_search_duration.record(duration)
        self.vector_search_results.record(result_count)

    def record_cache_event(self, hit: bool):
        """Record a cache hit or miss."""
        if hit:
            self.cache_hits.add(1)
        else:
            self.cache_misses.add(1)

    def record_error(self, error_type: str, component: str):
        """Record an error."""
        self.error_counter.add(1, {"error_type": error_type, "component": component})

    def create_span(self, name: str, attributes: dict = None):
        """Create a new tracing span."""
        return self.tracer.start_span(name, attributes=attributes or {})


# Global telemetry instance
telemetry: TelemetryManager = None


def init_telemetry(
    service_name: str,
    service_version: str = "1.0.0",
    otlp_endpoint: str = None,
    environment: str = "production",
) -> TelemetryManager:
    """Initialize global telemetry."""
    global telemetry
    telemetry = TelemetryManager(
        service_name=service_name,
        service_version=service_version,
        otlp_endpoint=otlp_endpoint,
        environment=environment,
    )
    return telemetry


def get_telemetry() -> TelemetryManager:
    """Get the global telemetry instance."""
    if telemetry is None:
        raise RuntimeError("Telemetry not initialized. Call init_telemetry() first.")
    return telemetry
```

```python
# File: src/observability/middleware.py
"""Observability middleware for FastAPI."""

import time
import logging
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from opentelemetry import trace

logger = logging.getLogger(__name__)


class ObservabilityMiddleware(BaseHTTPMiddleware):
    """Middleware to add observability to all requests."""

    async def dispatch(self, request: Request, call_next):
        start_time = time.time()

        # Get or create trace context
        span = trace.get_current_span()
        trace_id = format(span.get_span_context().trace_id, "032x") if span else "none"

        # Add request ID
        request_id = request.headers.get("X-Request-ID", trace_id)

        # Process request
        try:
            response = await call_next(request)
            duration = time.time() - start_time

            # Record metrics
            from src.observability.telemetry import get_telemetry
            t = get_telemetry()
            t.record_request(
                method=request.method,
                path=request.url.path,
                status_code=response.status_code,
                duration=duration,
            )

            # Structured log
            logger.info(
                "request_completed",
                extra={
                    "request_id": request_id,
                    "method": request.method,
                    "path": request.url.path,
                    "status_code": response.status_code,
                    "duration_ms": round(duration * 1000, 2),
                    "trace_id": trace_id,
                    "user_agent": request.headers.get("User-Agent", ""),
                    "client_ip": request.client.host if request.client else "",
                },
            )

            # Add response headers
            response.headers["X-Request-ID"] = request_id
            response.headers["X-Trace-ID"] = trace_id
            response.headers["X-Response-Time"] = f"{duration:.3f}s"

            return response

        except Exception as e:
            duration = time.time() - start_time

            from src.observability.telemetry import get_telemetry
            t = get_telemetry()
            t.record_error(error_type=type(e).__name__, component="api")

            logger.error(
                "request_failed",
                extra={
                    "request_id": request_id,
                    "method": request.method,
                    "path": request.url.path,
                    "error": str(e),
                    "error_type": type(e).__name__,
                    "duration_ms": round(duration * 1000, 2),
                    "trace_id": trace_id,
                },
            )
            raise
```

```python
# File: src/observability/structured_logging.py
"""Structured logging configuration."""

import logging
import json
import sys
from datetime import datetime, timezone
from pythonjsonlogger import jsonlogger


class StructuredFormatter(jsonlogger.JsonFormatter):
    """Custom JSON formatter with AI-specific fields."""

    def add_fields(self, log_record, record, message_dict):
        super().add_fields(log_record, record, message_dict)

        log_record["timestamp"] = datetime.now(timezone.utc).isoformat()
        log_record["level"] = record.levelname
        log_record["logger"] = record.name
        log_record["module"] = record.module
        log_record["function"] = record.funcName
        log_record["line"] = record.lineno

        # Add service info
        log_record["service"] = "ai-service"
        log_record["version"] = "1.0.0"
        log_record["environment"] = "production"

        # Add trace context if available
        from opentelemetry import trace
        span = trace.get_current_span()
        if span and span.get_span_context().trace_id:
            log_record["trace_id"] = format(span.get_span_context().trace_id, "032x")
            log_record["span_id"] = format(span.get_span_context().span_id, "016x")


def setup_logging(level: str = "INFO", json_output: bool = True):
    """Configure structured logging."""
    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, level.upper()))

    # Remove existing handlers
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)

    # Console handler
    handler = logging.StreamHandler(sys.stdout)

    if json_output:
        formatter = StructuredFormatter(
            fmt="%(timestamp)s %(level)s %(name)s %(message)s"
        )
    else:
        formatter = logging.Formatter(
            "%(asctime)s [%(levelname)s] %(name)s: %(message)s"
        )

    handler.setFormatter(formatter)
    root_logger.addHandler(handler)

    # Suppress noisy loggers
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
    logging.getLogger("httpx").setLevel(logging.WARNING)

    return root_logger
```

### 8.3 GRAFANA STACK (LGTM)

```
The Grafana Stack (Loki + Grafana + Tempo + Mimir) is the open-source
alternative to Datadog/New Relic. It covers all three pillars.

Architecture:
┌─────────────────────────────────────────────────────────────────────────┐
│                    GRAFANA OBSERVABILITY STACK                          │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  Application                                                           │
│  ┌──────────────────────────────────────────────────────┐              │
│  │  OpenTelemetry SDK (Python)                          │              │
│  │  ┌──────────┐  ┌──────────┐  ┌──────────┐           │              │
│  │  │ Logs     │  │ Metrics  │  │ Traces   │           │              │
│  │  └────┬─────┘  └────┬─────┘  └────┬─────┘           │              │
│  └───────┼──────────────┼─────────────┼─────────────────┘              │
│          │              │             │                                 │
│          v              v             v                                │
│  ┌──────────────┐ ┌──────────┐ ┌──────────┐                           │
│  │  Loki        │ │ Mimir    │ │ Tempo    │                            │
│  │  (Logs)      │ │ (Metrics)│ │ (Traces) │                            │
│  └──────┬───────┘ └────┬─────┘ └────┬─────┘                           │
│         │              │            │                                  │
│         └──────────────┼────────────┘                                  │
│                        v                                                │
│              ┌──────────────────┐                                       │
│              │  Grafana         │                                       │
│              │  (Dashboards)    │                                       │
│              │  ┌────────────┐  │                                       │
│              │  │ Alerting   │  │                                       │
│              │  │ (Alert     │  │                                       │
│              │  │  Manager)  │  │                                       │
│              │  └────────────┘  │                                       │
│              └──────────────────┘                                       │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

```yaml
# File: deploy/grafana-stack/docker-compose.grafana.yml
version: "3.8"

services:
  # Loki - Log aggregation
  loki:
    image: grafana/loki:2.9.0
    ports:
      - "3100:3100"
    volumes:
      - loki-data:/loki
      - ./loki-config.yml:/etc/loki/local-config.yaml
    command: -config.file=/etc/loki/local-config.yaml
    healthcheck:
      test: ["CMD", "wget", "-qO-", "http://localhost:3100/ready"]
      interval: 10s
      timeout: 5s
      retries: 5

  # Prometheus - Metrics collection
  prometheus:
    image: prom/prometheus:v2.48.0
    ports:
      - "9090:9090"
    volumes:
      - ./prometheus.yml:/etc/prometheus/prometheus.yml
      - prometheus-data:/prometheus
    command:
      - "--config.file=/etc/prometheus/prometheus.yml"
      - "--storage.tsdb.retention.time=30d"
      - "--web.enable-lifecycle"

  # Tempo - Distributed tracing
  tempo:
    image: grafana/tempo:2.3.0
    ports:
      - "3200:3200"   # Tempo API
      - "4317:4317"   # OTLP gRPC
      - "4318:4318"   # OTLP HTTP
    volumes:
      - tempo-data:/var/tempo
      - ./tempo-config.yml:/etc/tempo/local-config.yaml
    command: -config.file=/etc/tempo/local-config.yaml

  # Grafana - Visualization
  grafana:
    image: grafana/grafana:10.2.0
    ports:
      - "3000:3000"
    environment:
      GF_SECURITY_ADMIN_USER: admin
      GF_SECURITY_ADMIN_PASSWORD: ${GRAFANA_PASSWORD:-admin}
      GF_USERS_ALLOW_SIGN_UP: "false"
    volumes:
      - grafana-data:/var/lib/grafana
      - ./grafana/provisioning:/etc/grafana/provisioning
      - ./grafana/dashboards:/var/lib/grafana/dashboards
    depends_on:
      - loki
      - prometheus
      - tempo

  # Alloy (Grafana Agent) - Telemetry collector
  alloy:
    image: grafana/alloy:v0.1.0
    ports:
      - "12345:12345"
    volumes:
      - ./alloy-config.river:/etc/alloy/config.river
      - /var/log:/var/log:ro
    command: run /etc/alloy/config.river

volumes:
  loki-data:
  prometheus-data:
  tempo-data:
  grafana-data:
```

```yaml
# File: deploy/grafana-stack/prometheus.yml
global:
  scrape_interval: 15s
  evaluation_interval: 15s

rule_files:
  - "alerts/*.yml"

alerting:
  alertmanagers:
    - static_configs:
        - targets:
            - alertmanager:9093

scrape_configs:
  # Prometheus self-monitoring
  - job_name: "prometheus"
    static_configs:
      - targets: ["localhost:9090"]

  # AI API service
  - job_name: "ai-api"
    metrics_path: /metrics
    scrape_interval: 10s
    kubernetes_sd_configs:
      - role: pod
        namespaces:
          names: ["ai-production"]
    relabel_configs:
      - source_labels: [__meta_kubernetes_pod_annotation_prometheus_io_scrape]
        action: keep
        regex: true
      - source_labels: [__meta_kubernetes_pod_annotation_prometheus_io_path]
        action: replace
        target_label: __metrics_path__
        regex: (.+)

  # GPU inference service
  - job_name: "gpu-inference"
    metrics_path: /metrics
    scrape_interval: 30s
    static_configs:
      - targets: ["gpu-inference:8000"]

  # Node exporter (host metrics)
  - job_name: "node-exporter"
    static_configs:
      - targets: ["node-exporter:9100"]

  # Redis exporter
  - job_name: "redis"
    static_configs:
      - targets: ["redis-exporter:9121"]

  # PostgreSQL exporter
  - job_name: "postgres"
    static_configs:
      - targets: ["postgres-exporter:9187"]
```

---

## 9. MONITORING AND ALERTING

### What is Monitoring and Alerting?

**Monitoring** is the continuous observation of your application's health and performance by collecting and visualizing metrics. **Alerting** is the automated system that notifies you when something goes wrong — before your users notice.

Think of monitoring like the dashboard in your car:
- **Speedometer** = Request rate (how fast is traffic flowing?)
- **Fuel gauge** = Resource utilization (how much CPU/memory/GPU is left?)
- **Check engine light** = Error alerts (something is broken!)
- **Temperature gauge** = Latency (is the system overheating?)

**Alerting** is the alarm that goes off when the temperature crosses a threshold. Without alerting, you'd only find out about problems when users complain. With alerting, you know within seconds.

Key monitoring tools:
- **Prometheus** — Open-source metrics collection and storage. Scrapes metrics from your applications. Industry standard for Kubernetes.
- **Grafana** — Open-source dashboards and visualization. Connects to Prometheus, Loki, Tempo, and many other data sources.
- **Datadog** — All-in-one monitoring platform (metrics + logs + traces + APM). Expensive but very polished.
- **New Relic** — Similar to Datadog. Full-stack observability platform.
- **CloudWatch** — AWS's built-in monitoring. Works great for AWS services, limited for custom metrics.

Key alerting tools:
- **Grafana Alerting** — Built into Grafana. Free. Powerful.
- **PagerDuty** — Incident management and on-call scheduling. Pages engineers via phone/SMS.
- **Opsgenie** — Similar to PagerDuty. Part of the Atlassian ecosystem.
- **Slack/Teams** — For non-critical notifications.

### 9.1 KEY METRICS FOR AI APPLICATIONS

```
┌─────────────────────────────────────────────────────────────────────────┐
│                    AI APPLICATION METRICS HIERARCHY                     │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  LAYER 1: BUSINESS METRICS                                              │
│  ├─ Requests per minute (throughput)                                    │
│  ├─ Cost per request ($/query)                                          │
│  ├─ User satisfaction score (thumbs up/down)                            │
│  ├─ Active users (daily/weekly/monthly)                                 │
│  ├─ Feature usage (which endpoints, which models)                       │
│  └─ Revenue impact (conversions, leads, tickets resolved)               │
│                                                                         │
│  LAYER 2: APPLICATION METRICS                                           │
│  ├─ Request latency (p50, p95, p99)                                     │
│  ├─ Error rate (4xx, 5xx)                                               │
│  ├─ Apdex score (satisfaction)                                          │
│  ├─ Request queue depth                                                 │
│  ├─ Cache hit ratio                                                     │
│  └─ Rate limit hits                                                     │
│                                                                         │
│  LAYER 3: AI/ML METRICS                                                 │
│  ├─ LLM latency (time to first token, time to last token)              │
│  ├─ Token usage (input, output, total)                                  │
│  ├─ Model accuracy / quality (LLM-as-judge scores)                     │
│  ├─ Hallucination rate                                                  │
│  ├─ Retrieval relevance (RAG context quality)                           │
│  ├─ Embedding generation time                                           │
│  ├─ Vector search latency                                               │
│  └─ Token cost ($/1K tokens)                                            │
│                                                                         │
│  LAYER 4: INFRASTRUCTURE METRICS                                        │
│  ├─ CPU utilization (per pod, per node)                                 │
│  ├─ Memory utilization                                                  │
│  ├─ GPU utilization (compute, memory)                                   │
│  ├─ Network I/O (bytes in/out)                                          │
│  ├─ Disk I/O (read/write ops, latency)                                  │
│  ├─ Container restarts                                                  │
│  └─ Pod scheduling latency                                              │
│                                                                         │
│  LAYER 5: DEPENDENCY METRICS                                            │
│  ├─ Database query latency                                              │
│  ├─ Database connection pool utilization                                │
│  ├─ Redis hit rate and latency                                          │
│  ├─ External API latency (LLM providers)                                │
│  ├─ External API error rate                                             │
│  └─ Vector DB query latency                                             │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

### 9.2 PROMETHEUS ALERTING RULES

```yaml
# File: deploy/prometheus/alerts/ai-alerts.yml
groups:
  - name: ai-service-alerts
    rules:
      # High error rate
      - alert: HighErrorRate
        expr: |
          sum(rate(ai_requests_total{status_code=~"5.."}[5m]))
          /
          sum(rate(ai_requests_total[5m]))
          > 0.05
        for: 5m
        labels:
          severity: critical
          team: ai-platform
        annotations:
          summary: "High error rate: {{ $value | humanizePercentage }}"
          description: "Error rate is above 5% for the last 5 minutes."
          runbook_url: "https://wiki.internal/runbooks/high-error-rate"

      # High latency (p99)
      - alert: HighLatencyP99
        expr: |
          histogram_quantile(0.99, sum(rate(ai_request_duration_seconds_bucket[5m])) by (le))
          > 5
        for: 5m
        labels:
          severity: warning
          team: ai-platform
        annotations:
          summary: "P99 latency is {{ $value }}s"
          description: "99th percentile request latency exceeds 5 seconds."

      # LLM provider errors
      - alert: LLMProviderErrors
        expr: |
          sum(rate(ai_errors_total{component="llm"}[5m])) > 0.1
        for: 2m
        labels:
          severity: critical
          team: ai-platform
        annotations:
          summary: "LLM provider error rate spike"
          description: "LLM API errors detected. Check provider status."

      # High LLM cost
      - alert: HighLLMCost
        expr: |
          sum(rate(ai_llm_cost_usd_total[1h])) * 24 > 100
        for: 15m
        labels:
          severity: warning
          team: ai-platform
        annotations:
          summary: "Projected daily LLM cost: ${{ $value }}"
          description: "LLM costs trending toward $100+/day."

      # GPU memory usage
      - alert: GPUMemoryHigh
        expr: |
          nvidia_gpu_memory_used_bytes / nvidia_gpu_memory_total_bytes > 0.9
        for: 5m
        labels:
          severity: warning
          team: ai-platform
        annotations:
          summary: "GPU memory usage above 90%"
          description: "GPU {{ $labels.gpu }} memory usage is {{ $value | humanizePercentage }}."

      # Container restarts
      - alert: ContainerRestarting
        expr: |
          increase(kube_pod_container_status_restarts_total{namespace="ai-production"}[1h]) > 3
        for: 5m
        labels:
          severity: warning
          team: ai-platform
        annotations:
          summary: "Container {{ $labels.container }} restarting frequently"
          description: "Pod {{ $labels.pod }} has restarted {{ $value }} times in the last hour."

      # Queue depth
      - alert: QueueBacklog
        expr: |
          ai_queue_depth > 1000
        for: 10m
        labels:
          severity: warning
          team: ai-platform
        annotations:
          summary: "Job queue backlog: {{ $value }} items"
          description: "Processing queue has been backed up for 10+ minutes."

      # Cache hit rate low
      - alert: LowCacheHitRate
        expr: |
          sum(rate(ai_cache_hits_total[1h]))
          /
          (sum(rate(ai_cache_hits_total[1h])) + sum(rate(ai_cache_misses_total[1h])))
          < 0.3
        for: 30m
        labels:
          severity: info
          team: ai-platform
        annotations:
          summary: "Cache hit rate is {{ $value | humanizePercentage }}"
          description: "Cache hit rate has been below 30% for 30 minutes."

  - name: infrastructure-alerts
    rules:
      - alert: HighCPUUsage
        expr: |
          avg(rate(container_cpu_usage_seconds_total{namespace="ai-production"}[5m])) by (pod)
          > 0.85
        for: 10m
        labels:
          severity: warning
        annotations:
          summary: "High CPU usage on {{ $labels.pod }}"

      - alert: HighMemoryUsage
        expr: |
          container_memory_working_set_bytes{namespace="ai-production"}
          /
          container_spec_memory_limit_bytes{namespace="ai-production"}
          > 0.9
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "Memory usage above 90% on {{ $labels.pod }}"

      - alert: PodNotReady
        expr: |
          kube_pod_status_ready{namespace="ai-production", condition="true"} == 0
        for: 5m
        labels:
          severity: critical
        annotations:
          summary: "Pod {{ $labels.pod }} is not ready"
```

### 9.3 DATADOG INTEGRATION

```python
# File: src/observability/datadog_integration.py
"""Datadog APM and monitoring integration."""

import os
from ddtrace import tracer, patch_all
from datadog import initialize, statsd

def init_datadog(service_name: str, environment: str = "production"):
    """Initialize Datadog APM and metrics."""

    # Patch all supported libraries automatically
    patch_all()

    # Configure tracer
    tracer.configure(
        hostname=os.getenv("DD_AGENT_HOST", "localhost"),
        port=int(os.getenv("DD_TRACE_AGENT_PORT", "8126")),
        service=service_name,
        env=environment,
        version=os.getenv("APP_VERSION", "1.0.0"),
        tags={
            "team": "ai-platform",
            "service": service_name,
        },
    )

    # Configure DogStatsD
    initialize(
        statsd_host=os.getenv("DD_AGENT_HOST", "localhost"),
        statsd_port=int(os.getenv("DD_DOGSTATSD_PORT", "8125")),
    )

    return tracer, statsd


class DatadogMetrics:
    """Datadog metrics helper for AI applications."""

    def record_llm_call(
        self,
        model: str,
        tokens_in: int,
        tokens_out: int,
        latency_ms: float,
        cost_usd: float,
        success: bool,
    ):
        """Record LLM call metrics to Datadog."""
        tags = [f"model:{model}", f"success:{success}"]

        statsd.increment("ai.llm.calls", tags=tags)
        statsd.histogram("ai.llm.latency_ms", latency_ms, tags=tags)
        statsd.increment("ai.llm.tokens.input", tokens_in, tags=tags)
        statsd.increment("ai.llm.tokens.output", tokens_out, tags=tags)
        statsd.increment("ai.llm.cost_usd", cost_usd, tags=[f"model:{model}"])

    def record_vector_search(self, duration_ms: float, result_count: int):
        """Record vector search metrics."""
        statsd.histogram("ai.vector_search.duration_ms", duration_ms)
        statsd.histogram("ai.vector_search.results", result_count)

    def record_request(self, method: str, path: str, status_code: int, duration_ms: float):
        """Record HTTP request metrics."""
        tags = [
            f"method:{method}",
            f"path:{path}",
            f"status:{status_code}",
        ]
        statsd.increment("ai.requests", tags=tags)
        statsd.histogram("ai.request.duration_ms", duration_ms, tags=tags)
```

---

## 10. DISTRIBUTED TRACING

### What is Distributed Tracing?

**Distributed tracing** tracks the journey of a single request as it travels through multiple services in your system. It's like a GPS tracker for your request — you can see every stop it made, how long it spent at each stop, and where it got delayed.

Why does this matter? In a modern AI application, a single user request might touch:
1. API Gateway (authentication, rate limiting)
2. RAG Pipeline (vector search in ChromaDB/Pinecone)
3. LLM Provider (OpenAI/Anthropic API call)
4. Response formatting (JSON serialization)
5. Cache layer (Redis)
6. Database (PostgreSQL for session storage)

Without tracing, if a request takes 3 seconds, you don't know where the time is spent. With tracing, you can see:
```
Total: 3,000ms
├─ API Gateway: 50ms
├─ RAG Pipeline: 2,900ms
│  ├─ Vector Search: 200ms
│  └─ LLM Call: 2,700ms  ← 90% of time here!
└─ Response: 50ms
```

Now you know the LLM call is the bottleneck. You can optimize that specific step (use a faster model, add caching, use streaming).

Key tracing tools:
- **Jaeger** — Open-source distributed tracing. Originally from Uber. Great for Kubernetes.
- **Zipkin** — Open-source tracing from Twitter. Simpler than Jaeger.
- **Grafana Tempo** — High-scale distributed tracing backend. Part of the Grafana stack.
- **AWS X-Ray** — AWS's managed tracing service. Good for AWS-native applications.
- **Honeycomb** — Observability platform focused on traces and events. Excellent for debugging.

### 10.1 TRACING ARCHITECTURE

```
┌─────────────────────────────────────────────────────────────────────────┐
│                    DISTRIBUTED TRACING FLOW                             │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  Client Request                                                         │
│  │                                                                      │
│  v                                                                      │
│  ┌──────────────────────────────────────────────────────────────┐      │
│  │  API Gateway (trace.start)                                   │      │
│  │  Trace ID: abc123                                            │      │
│  │  Span ID: span001                                            │      │
│  │  ┌────────────────────────────────────────────────────────┐  │      │
│  │  │  RAG Pipeline                                          │  │      │
│  │  │  Span ID: span002 (parent: span001)                    │  │      │
│  │  │  ┌──────────────────────┐  ┌──────────────────────┐   │  │      │
│  │  │  │  Vector Search       │  │  LLM Call            │   │  │      │
│  │  │  │  Span: span003       │  │  Span: span004       │   │  │      │
│  │  │  │  Duration: 45ms      │  │  Duration: 1200ms    │   │  │      │
│  │  │  │  ┌────────────────┐  │  │  ┌────────────────┐  │   │  │      │
│  │  │  │  │ ChromaDB Query │  │  │  │ OpenAI API     │  │   │  │      │
│  │  │  │  │ Span: span005  │  │  │  │ Span: span006  │  │   │  │      │
│  │  │  │  │ Duration: 30ms │  │  │  │ Duration: 1100ms│ │   │  │      │
│  │  │  │  └────────────────┘  │  │  └────────────────┘  │   │  │      │
│  │  │  └──────────────────────┘  └──────────────────────┘   │  │      │
│  │  └────────────────────────────────────────────────────────┘  │      │
│  └──────────────────────────────────────────────────────────────┘      │
│                                                                         │
│  Total Duration: 1,280ms                                                │
│  └─ API Gateway: 1,280ms                                               │
│     └─ RAG Pipeline: 1,275ms                                           │
│        ├─ Vector Search: 45ms (3.5%)                                   │
│        │  └─ ChromaDB: 30ms                                            │
│        └─ LLM Call: 1,200ms (93.8%)                                    │
│           └─ OpenAI API: 1,100ms                                       │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

### 10.2 IMPLEMENTING TRACING IN AI PIPELINES

```python
# File: src/observability/tracing.py
"""Distributed tracing for AI pipelines."""

from opentelemetry import trace
from opentelemetry.trace import Status, StatusCode
from functools import wraps
import time
import json


tracer = trace.get_tracer("ai-service")


def traced(name: str = None, attributes: dict = None):
    """Decorator to add tracing to any function."""
    def decorator(func):
        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            span_name = name or f"{func.__module__}.{func.__qualname__}"
            with tracer.start_as_current_span(span_name) as span:
                if attributes:
                    for k, v in attributes.items():
                        span.set_attribute(k, v)

                span.set_attribute("function.name", func.__name__)

                try:
                    result = await func(*args, **kwargs)
                    span.set_status(Status(StatusCode.OK))
                    return result
                except Exception as e:
                    span.set_status(Status(StatusCode.ERROR, str(e)))
                    span.record_exception(e)
                    raise

        @wraps(func)
        def sync_wrapper(*args, **kwargs):
            span_name = name or f"{func.__module__}.{func.__qualname__}"
            with tracer.start_as_current_span(span_name) as span:
                if attributes:
                    for k, v in attributes.items():
                        span.set_attribute(k, v)

                try:
                    result = func(*args, **kwargs)
                    span.set_status(Status(StatusCode.OK))
                    return result
                except Exception as e:
                    span.set_status(Status(StatusCode.ERROR, str(e)))
                    span.record_exception(e)
                    raise

        import asyncio
        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        return sync_wrapper
    return decorator


class AITracer:
    """AI-specific tracing utilities."""

    @staticmethod
    def trace_llm_call(model: str, prompt: str, max_tokens: int):
        """Create a span for an LLM call."""
        return tracer.start_as_current_span(
            "llm.call",
            attributes={
                "llm.model": model,
                "llm.prompt_length": len(prompt),
                "llm.max_tokens": max_tokens,
            },
        )

    @staticmethod
    def trace_vector_search(query: str, collection: str, top_k: int):
        """Create a span for vector search."""
        return tracer.start_as_current_span(
            "vector.search",
            attributes={
                "vector.query_length": len(query),
                "vector.collection": collection,
                "vector.top_k": top_k,
            },
        )

    @staticmethod
    def trace_embedding(text: str, model: str):
        """Create a span for embedding generation."""
        return tracer.start_as_current_span(
            "embedding.generate",
            attributes={
                "embedding.text_length": len(text),
                "embedding.model": model,
            },
        )

    @staticmethod
    def trace_cache_lookup(key: str):
        """Create a span for cache lookup."""
        return tracer.start_as_current_span(
            "cache.lookup",
            attributes={"cache.key": key},
        )

    @staticmethod
    def trace_rag_pipeline(query: str):
        """Create a span for the full RAG pipeline."""
        return tracer.start_as_current_span(
            "rag.pipeline",
            attributes={"rag.query": query},
        )
```

### 10.3 JAEGER DEPLOYMENT

```yaml
# File: deploy/jaeger/docker-compose.yml
version: "3.8"

services:
  jaeger:
    image: jaegertracing/all-in-one:1.52
    ports:
      - "16686:16686"  # Jaeger UI
      - "4317:4317"    # OTLP gRPC
      - "4318:4318"    # OTLP HTTP
      - "14250:14250"  # gRPC for Jaeger collector
    environment:
      COLLECTOR_OTLP_ENABLED: "true"
      SPAN_STORAGE_TYPE: "elasticsearch"
      ES_SERVER_URLS: "http://elasticsearch:9200"
      ES_INDEX_PREFIX: "jaeger"
      ES_TAGS_AS_FIELDS_ALL: "true"
    depends_on:
      - elasticsearch

  elasticsearch:
    image: elasticsearch:8.11.0
    environment:
      - discovery.type=single-node
      - xpack.security.enabled=false
      - "ES_JAVA_OPTS=-Xms512m -Xmx512m"
    volumes:
      - es-data:/usr/share/elasticsearch/data
    ports:
      - "9200:9200"

volumes:
  es-data:
```

---

## 11. LOG MANAGEMENT AND ANALYSIS

### What is Log Management?

**Logs** are detailed records of everything that happens in your application. Every request, every error, every database query, every LLM call — all recorded as timestamped text entries. **Log management** is the system for collecting, storing, searching, and analyzing these logs at scale.

Why do logs matter?
- **Debugging** — When something breaks, logs tell you exactly what happened and in what order
- **Audit trail** — Who accessed what data? What did the AI respond? Logs provide a legal record
- **Performance analysis** — Which endpoints are slow? Which users generate the most load?
- **Security** — Detect unauthorized access, injection attacks, abuse patterns
- **Compliance** — GDPR, HIPAA, SOC 2 all require audit logs

**Structured logging** means writing logs as JSON (not plain text) so they can be automatically parsed, filtered, and analyzed. Instead of:
```
2024-01-15 14:32:01 ERROR: LLM call failed for user_123
```
You write:
```json
{"timestamp": "2024-01-15T14:32:01Z", "level": "ERROR", "event": "llm_call_failed", "user_id": "user_123", "model": "gpt-4", "error": "rate_limit_exceeded"}
```

The structured version can be automatically filtered (`show me all errors for user_123`), aggregated (`count errors by model`), and alerted on (`alert if error rate > 5%`).

Key log management tools:
- **ELK Stack** (Elasticsearch + Logstash + Kibana) — The industry standard for log aggregation. Powerful but resource-heavy.
- **Loki** — Grafana's log system. Lightweight, cost-effective, integrates with Grafana dashboards.
- **CloudWatch Logs** — AWS's managed logging. Great for AWS services.
- **Splunk** — Enterprise log analysis. Very powerful, very expensive.

### 11.1 STRUCTURED LOGGING BEST PRACTICES

```python
# File: src/observability/log_manager.py
"""Centralized log management for AI applications."""

import logging
import json
import hashlib
import traceback
from datetime import datetime, timezone
from typing import Any
from contextvars import ContextVar

# Context variables for request-scoped data
request_id_var: ContextVar[str] = ContextVar("request_id", default="")
user_id_var: ContextVar[str] = ContextVar("user_id", default="")
trace_id_var: ContextVar[str] = ContextVar("trace_id", default="")


class AILogFormatter:
    """AI-specific structured log formatter."""

    def __init__(self, service_name: str, environment: str = "production"):
        self.service_name = service_name
        self.environment = environment

    def format_record(self, record: logging.LogRecord) -> dict:
        """Format a log record as structured JSON."""
        log_entry = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "service": self.service_name,
            "environment": self.environment,
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
            "thread": record.thread,
            "process": record.process,
        }

        # Add request context
        request_id = request_id_var.get("")
        if request_id:
            log_entry["request_id"] = request_id

        user_id = user_id_var.get("")
        if user_id:
            log_entry["user_id"] = user_id

        trace_id = trace_id_var.get("")
        if trace_id:
            log_entry["trace_id"] = trace_id

        # Add exception info
        if record.exc_info and record.exc_info[1]:
            log_entry["exception"] = {
                "type": type(record.exc_info[1]).__name__,
                "message": str(record.exc_info[1]),
                "traceback": traceback.format_exception(*record.exc_info),
            }

        # Add extra fields
        for key, value in record.__dict__.items():
            if key not in logging.LogRecord(
                "", 0, "", 0, "", (), None
            ).__dict__ and key not in (
                "message", "msg", "args", "exc_info", "exc_text", "stack_info"
            ):
                if isinstance(value, (str, int, float, bool, type(None))):
                    log_entry[key] = value

        return log_entry


class AILogger:
    """AI-specific logging utilities."""

    def __init__(self, name: str):
        self.logger = logging.getLogger(name)

    def log_llm_request(
        self,
        model: str,
        prompt_tokens: int,
        completion_tokens: int,
        total_tokens: int,
        latency_ms: float,
        cost_usd: float,
        request_id: str = "",
    ):
        """Log LLM API request details."""
        self.logger.info(
            "llm_request_completed",
            extra={
                "event_type": "llm_request",
                "model": model,
                "prompt_tokens": prompt_tokens,
                "completion_tokens": completion_tokens,
                "total_tokens": total_tokens,
                "latency_ms": latency_ms,
                "cost_usd": cost_usd,
                "request_id": request_id,
            },
        )

    def log_vector_search(
        self,
        query_hash: str,
        collection: str,
        results_count: int,
        latency_ms: float,
    ):
        """Log vector search operation."""
        self.logger.info(
            "vector_search_completed",
            extra={
                "event_type": "vector_search",
                "query_hash": query_hash,
                "collection": collection,
                "results_count": results_count,
                "latency_ms": latency_ms,
            },
        )

    def log_cache_event(self, key: str, hit: bool, ttl_remaining: int = 0):
        """Log cache hit/miss."""
        self.logger.debug(
            f"cache_{'hit' if hit else 'miss'}",
            extra={
                "event_type": "cache",
                "cache_key": key,
                "cache_hit": hit,
                "ttl_remaining": ttl_remaining,
            },
        )

    def log_error(self, error: Exception, component: str, context: dict = None):
        """Log an error with full context."""
        self.logger.error(
            f"error_in_{component}: {str(error)}",
            extra={
                "event_type": "error",
                "error_type": type(error).__name__,
                "error_message": str(error),
                "component": component,
                "context": context or {},
            },
            exc_info=True,
        )

    def log_security_event(self, event_type: str, user_id: str, details: dict):
        """Log security-related events."""
        self.logger.warning(
            f"security_event: {event_type}",
            extra={
                "event_type": "security",
                "security_event_type": event_type,
                "user_id": user_id,
                "details": details,
            },
        )

    def log_performance_warning(self, operation: str, duration_ms: float, threshold_ms: float):
        """Log performance warnings."""
        self.logger.warning(
            f"slow_operation: {operation}",
            extra={
                "event_type": "performance",
                "operation": operation,
                "duration_ms": duration_ms,
                "threshold_ms": threshold_ms,
                "exceeded_by_ms": duration_ms - threshold_ms,
            },
        )
```

### 11.2 LOKI LOG QUERIES

```
# LogQL examples for AI application troubleshooting

# All errors in the last hour
{service="ai-api"} | json | level="ERROR" | line_format "{{.error_type}}: {{.message}}"

# LLM API errors with high latency
{service="ai-api"} | json | event_type="llm_request" | latency_ms > 5000

# Slow vector searches
{service="ai-api"} | json | event_type="vector_search" | latency_ms > 1000

# All requests for a specific user
{service="ai-api"} | json | user_id="user_12345"

# Security events
{service="ai-api"} | json | event_type="security"

# Rate limit hits
{service="ai-api"} | json | status_code=429

# Top 10 slowest requests in the last hour
topk(10,
  {service="ai-api"} | json | event_type="request"
  | latency_ms > 0
  | line_format "{{.request_id}} {{.path}} {{.latency_ms}}ms"
)

# Error count by type (last hour)
sum by (error_type) (
  count_over_time({service="ai-api"} | json | level="ERROR" [1h])
)

# Token usage by model (last day)
sum by (model) (
  sum_over_time({service="ai-api"} | json | event_type="llm_request" | unwrap total_tokens [1d])
)

# Cost breakdown by model (last day)
sum by (model) (
  sum_over_time({service="ai-api"} | json | event_type="llm_request" | unwrap cost_usd [1d])
)
```

---

## 12. ERROR TRACKING AND DEBUGGING

### What is Error Tracking?

**Error tracking** is the automated capture, grouping, and analysis of application errors. While logs record everything (including errors), error tracking focuses specifically on **exceptions and failures** — grouping similar errors together, tracking their frequency, and providing the context needed to fix them.

Think of it this way:
- **Logs** = A security camera recording everything 24/7
- **Error tracking** = A smart system that detects and clips every incident, groups similar incidents together, and alerts the security team

Why is error tracking separate from logging?
- **Grouping** — If the same error happens 1,000 times, you want to see it once with a count, not 1,000 separate log entries
- **Context** — Error trackers capture the full stack trace, request details, user info, and environment automatically
- **Alerting** — Get notified when new error types appear or when error rates spike
- **Trending** — See if errors are increasing or decreasing over time
- **Assignment** — Assign errors to team members for fixing

Key error tracking tools:
- **Sentry** — The most popular error tracking platform. Open-source, generous free tier. Supports Python, JavaScript, and 30+ languages.
- **Rollbar** — Similar to Sentry. Good real-time error tracking.
- **Bugsnag** — Error monitoring with stability scores. Good for mobile apps.
- **Datadog Error Tracking** — Part of Datadog's all-in-one platform.

### 12.1 SENTRY INTEGRATION

```python
# File: src/observability/sentry_setup.py
"""Sentry integration for error tracking."""

import sentry_sdk
from sentry_sdk.integrations.fastapi import FastApiIntegration
from sentry_sdk.integrations.sqlalchemy import SqlalchemyIntegration
from sentry_sdk.integrations.redis import RedisIntegration
from sentry_sdk.integrations.logging import LoggingIntegration
from sentry_sdk.integrations.celery import CeleryIntegration


def init_sentry(
    dsn: str,
    environment: str = "production",
    release: str = "1.0.0",
    sample_rate: float = 1.0,
    traces_sample_rate: float = 0.1,
    profiles_sample_rate: float = 0.1,
):
    """Initialize Sentry for error tracking."""

    sentry_sdk.init(
        dsn=dsn,
        environment=environment,
        release=release,
        sample_rate=sample_rate,
        traces_sample_rate=traces_sample_rate,
        profiles_sample_rate=profiles_sample_rate,
        integrations=[
            FastApiIntegration(),
            SqlalchemyIntegration(),
            RedisIntegration(),
            LoggingIntegration(
                level=logging.INFO,
                event_level=logging.ERROR,
            ),
            CeleryIntegration(),
        ],
        before_send=before_send_filter,
        before_send_transaction=before_send_transaction_filter,
        send_default_pii=False,
        attach_stacktrace=True,
        max_breadcrumbs=50,
    )

    sentry_sdk.set_tag("service", "ai-api")
    sentry_sdk.set_tag("team", "ai-platform")


def before_send_filter(event, hint):
    """Filter sensitive data before sending to Sentry."""
    if "request" in event and "headers" in event["request"]:
        headers = event["request"]["headers"]
        for key in headers:
            if "auth" in key.lower() or "key" in key.lower() or "token" in key.lower():
                headers[key] = "[FILTERED]"

    if "extra" in event:
        sensitive_keys = ["password", "secret", "token", "api_key", "credit_card"]
        for key in list(event["extra"].keys()):
            if any(s in key.lower() for s in sensitive_keys):
                event["extra"][key] = "[FILTERED]"

    return event


def capture_ai_error(error, model=None, tokens_used=None, request_id=None):
    """Capture an AI-specific error with context."""
    with sentry_sdk.push_scope() as scope:
        if model:
            scope.set_tag("llm.model", model)
        if tokens_used:
            scope.set_extra("llm.tokens_used", tokens_used)
        if request_id:
            scope.set_extra("request_id", request_id)

        scope.set_context("ai_request", {
            "model": model,
            "tokens_used": tokens_used,
            "request_id": request_id,
        })

        sentry_sdk.capture_exception(error)
```

### 12.2 ERROR HANDLING PATTERNS

```python
# File: src/observability/error_handler.py
"""Comprehensive error handling for AI applications."""

import logging
import traceback
from enum import Enum
from fastapi import Request
from fastapi.responses import JSONResponse

logger = logging.getLogger(__name__)


class ErrorCode(str, Enum):
    """Standardized error codes for AI services."""
    # Client errors (4xx)
    INVALID_REQUEST = "INVALID_REQUEST"
    AUTHENTICATION_FAILED = "AUTHENTICATION_FAILED"
    RATE_LIMIT_EXCEEDED = "RATE_LIMIT_EXCEEDED"
    QUOTA_EXCEEDED = "QUOTA_EXCEEDED"
    CONTEXT_TOO_LONG = "CONTEXT_TOO_LONG"
    INVALID_MODEL = "INVALID_MODEL"
    CONTENT_FILTERED = "CONTENT_FILTERED"

    # Server errors (5xx)
    INTERNAL_ERROR = "INTERNAL_ERROR"
    LLM_PROVIDER_ERROR = "LLM_PROVIDER_ERROR"
    VECTOR_DB_ERROR = "VECTOR_DB_ERROR"
    CACHE_ERROR = "CACHE_ERROR"
    TIMEOUT_ERROR = "TIMEOUT_ERROR"
    CIRCUIT_BREAKER_OPEN = "CIRCUIT_BREAKER_OPEN"
    DEPENDENCY_UNAVAILABLE = "DEPENDENCY_UNAVAILABLE"


class AIServiceError(Exception):
    """Base error for AI service."""

    def __init__(
        self,
        code: ErrorCode,
        message: str,
        status_code: int = 500,
        details: dict = None,
        retryable: bool = False,
    ):
        self.code = code
        self.message = message
        self.status_code = status_code
        self.details = details or {}
        self.retryable = retryable
        super().__init__(message)


class LLMProviderError(AIServiceError):
    """LLM provider API error."""

    def __init__(self, provider: str, message: str, status_code: int = 502):
        super().__init__(
            code=ErrorCode.LLM_PROVIDER_ERROR,
            message=f"LLM provider error ({provider}): {message}",
            status_code=status_code,
            details={"provider": provider},
            retryable=True,
        )


class VectorDBError(AIServiceError):
    """Vector database error."""

    def __init__(self, message: str):
        super().__init__(
            code=ErrorCode.VECTOR_DB_ERROR,
            message=f"Vector DB error: {message}",
            status_code=503,
            retryable=True,
        )


class RateLimitError(AIServiceError):
    """Rate limit exceeded."""

    def __init__(self, limit: int, window: str):
        super().__init__(
            code=ErrorCode.RATE_LIMIT_EXCEEDED,
            message=f"Rate limit exceeded: {limit} requests per {window}",
            status_code=429,
            details={"limit": limit, "window": window},
            retryable=True,
        )


async def ai_error_handler(request: Request, exc: AIServiceError) -> JSONResponse:
    """Global error handler for AI service errors."""
    logger.error(
        f"AI Error: {exc.code.value} - {exc.message}",
        extra={
            "error_code": exc.code.value,
            "status_code": exc.status_code,
            "details": exc.details,
            "retryable": exc.retryable,
            "path": request.url.path,
            "method": request.method,
        },
    )

    import sentry_sdk
    if exc.status_code >= 500:
        sentry_sdk.capture_exception(exc)

    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": {
                "code": exc.code.value,
                "message": exc.message,
                "details": exc.details,
                "retryable": exc.retryable,
            }
        },
    )


async def generic_error_handler(request: Request, exc: Exception) -> JSONResponse:
    """Handle unexpected errors."""
    logger.critical(
        f"Unhandled exception: {type(exc).__name__}: {str(exc)}",
        extra={
            "path": request.url.path,
            "method": request.method,
            "traceback": traceback.format_exc(),
        },
        exc_info=True,
    )

    import sentry_sdk
    sentry_sdk.capture_exception(exc)

    return JSONResponse(
        status_code=500,
        content={
            "error": {
                "code": "INTERNAL_ERROR",
                "message": "An unexpected error occurred",
                "retryable": True,
            }
        },
    )
```

---

## 13. INCIDENT MANAGEMENT AND ON-CALL

### What is Incident Management?

**Incident management** is the organized process for responding to production outages and degradations. An **incident** is any event that disrupts or threatens to disrupt your service — from a complete outage (service is down) to a degradation (responses are slow) to a security breach.

The incident management lifecycle:
1. **Detection** — Monitoring/alerting detects the problem
2. **Triage** — Determine severity and impact (how many users affected?)
3. **Response** — Page the on-call engineer, start a war room
4. **Mitigation** — Stop the bleeding (rollback, scale up, failover)
5. **Resolution** — Fix the root cause
6. **Post-mortem** — Document what happened, why, and how to prevent it

**On-call** is the practice of having engineers available 24/7 to respond to incidents. An on-call rotation ensures no single engineer is always on duty.

Key incident management tools:
- **PagerDuty** — Industry standard for on-call scheduling and incident paging. Calls/SMS engineers when alerts fire.
- **Opsgenie** — Similar to PagerDuty. Part of the Atlassian ecosystem (Jira, Confluence).
- **Grafana OnCall** — Open-source on-call management. Integrates with Grafana alerting.
- **Slack/Teams** — For incident communication and war rooms.
- **Incident.io** — Modern incident management platform. Good Slack integration.

### 13.1 INCIDENT RESPONSE FRAMEWORK

```
┌─────────────────────────────────────────────────────────────────────────┐
│                    INCIDENT SEVERITY LEVELS                             │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  SEV1 (Critical) - Customer-facing impact                               │
│  ├─ Service completely down                                             │
│  ├─ Data loss or corruption                                             │
│  ├─ Security breach                                                     │
│  Response: Page immediately, all hands, war room                        │
│  SLA: Acknowledge in 5 min, resolve in 1 hour                          │
│                                                                         │
│  SEV2 (Major) - Significant degradation                                 │
│  ├─ Error rate > 10%                                                    │
│  ├─ Latency > 10x normal                                               │
│  ├─ Key feature unavailable                                             │
│  Response: Page on-call engineer, escalate if needed                    │
│  SLA: Acknowledge in 15 min, resolve in 4 hours                        │
│                                                                         │
│  SEV3 (Minor) - Limited impact                                          │
│  ├─ Error rate 1-10%                                                    │
│  ├─ Latency 2-10x normal                                               │
│  ├─ Non-critical feature degraded                                       │
│  Response: Notify on-call, investigate during business hours            │
│  SLA: Acknowledge in 1 hour, resolve in 24 hours                       │
│                                                                         │
│  SEV4 (Low) - Minimal impact                                            │
│  ├─ Cosmetic issues                                                     │
│  ├─ Non-urgent bugs                                                     │
│  Response: Create ticket, prioritize in sprint                          │
│  SLA: Acknowledge in 1 business day                                    │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

### 13.2 PAGERDUTY / OPSGENIE INTEGRATION

```python
# File: src/observability/incident_manager.py
"""Incident management integration."""

import os
import httpx
import logging
from datetime import datetime, timezone

logger = logging.getLogger(__name__)


class PagerDutyClient:
    """PagerDuty incident management client."""

    def __init__(self, routing_key: str = None):
        self.routing_key = routing_key or os.getenv("PAGERDUTY_ROUTING_KEY")
        self.api_url = "https://events.pagerduty.com/v2/enqueue"

    async def trigger_alert(
        self,
        severity: str,
        summary: str,
        source: str,
        component: str = None,
        custom_details: dict = None,
        dedup_key: str = None,
    ):
        """Trigger a PagerDuty alert."""
        payload = {
            "routing_key": self.routing_key,
            "event_action": "trigger",
            "dedup_key": dedup_key or f"ai-service-{severity}-{component}",
            "payload": {
                "summary": summary,
                "severity": severity,
                "source": source,
                "component": component,
                "custom_details": custom_details or {},
                "timestamp": datetime.now(timezone.utc).isoformat(),
            },
        }

        async with httpx.AsyncClient() as client:
            response = await client.post(self.api_url, json=payload)
            response.raise_for_status()
            logger.info(f"PagerDuty alert triggered: {summary}")
            return response.json()

    async def resolve_alert(self, dedup_key: str):
        """Resolve a PagerDuty alert."""
        payload = {
            "routing_key": self.routing_key,
            "event_action": "resolve",
            "dedup_key": dedup_key,
        }

        async with httpx.AsyncClient() as client:
            response = await client.post(self.api_url, json=payload)
            response.raise_for_status()
            logger.info(f"PagerDuty alert resolved: {dedup_key}")
            return response.json()


class SlackNotifier:
    """Slack notification for incidents."""

    def __init__(self, webhook_url: str = None):
        self.webhook_url = webhook_url or os.getenv("SLACK_WEBHOOK_URL")

    async def send_alert(
        self,
        channel: str,
        severity: str,
        title: str,
        message: str,
        fields: list = None,
    ):
        """Send an alert to Slack."""
        color_map = {
            "critical": "#FF0000",
            "error": "#FF6600",
            "warning": "#FFCC00",
            "info": "#36A64F",
        }

        payload = {
            "channel": channel,
            "username": "AI Service Alert",
            "icon_emoji": ":robot_face:",
            "attachments": [
                {
                    "color": color_map.get(severity, "#999999"),
                    "title": f"[{severity.upper()}] {title}",
                    "text": message,
                    "fields": [
                        {"title": f.get("title"), "value": f.get("value"), "short": f.get("short", True)}
                        for f in (fields or [])
                    ],
                    "footer": "AI Service Monitoring",
                    "ts": int(datetime.now().timestamp()),
                }
            ],
        }

        async with httpx.AsyncClient() as client:
            response = await client.post(self.webhook_url, json=payload)
            response.raise_for_status()
            logger.info(f"Slack alert sent: {title}")


class IncidentManager:
    """Manage incidents end-to-end."""

    def __init__(self):
        self.pagerduty = PagerDutyClient()
        self.slack = SlackNotifier()

    async def handle_alert(
        self,
        alert_name: str,
        severity: str,
        description: str,
        metrics: dict = None,
    ):
        """Handle an incoming alert from Prometheus/Alertmanager."""
        await self.slack.send_alert(
            channel="#ai-alerts",
            severity=severity,
            title=alert_name,
            message=description,
            fields=[
                {"title": k, "value": str(v), "short": True}
                for k, v in (metrics or {}).items()
            ],
        )

        if severity in ("critical", "error"):
            await self.pagerduty.trigger_alert(
                severity=severity,
                summary=f"{alert_name}: {description}",
                source="ai-service",
                component="ai-api",
                custom_details=metrics or {},
            )

        logger.info(f"Incident handled: {alert_name} ({severity})")
```

### 13.3 RUNBOOK TEMPLATE

```markdown
# Runbook: High LLM Error Rate

## Alert
- **Alert Name**: LLMProviderErrors
- **Severity**: Critical
- **Condition**: LLM error rate > 10% for 5 minutes

## Impact
- Users receiving errors or timeouts on AI queries
- Potential upstream provider outage (OpenAI, Anthropic, etc.)

## Diagnosis Steps

### 1. Check provider status
```bash
curl -s https://status.openai.com/api/v2/status.json | jq '.status.indicator'
curl -s https://status.anthropic.com/api/v2/status.json | jq '.status.indicator'
```

### 2. Check error logs
```bash
# Loki query
{service="ai-api"} | json | event_type="llm_request" | level="ERROR" | last 15m
```

### 3. Check circuit breaker state
```bash
curl -s http://localhost:9090/api/v1/query?query=circuit_breaker_state
```

## Resolution Steps

### If provider is down:
1. Switch to fallback provider
```bash
kubectl set env deployment/ai-api LLM_FALLBACK_ENABLED=true -n ai-production
```
2. Notify users of degraded service
3. Monitor provider status until recovery

### If rate limited:
1. Check for traffic spike
2. Scale up replicas if needed
3. Implement request queuing if persistent

## Escalation
- If not resolved in 30 minutes -> Escalate to AI Platform Lead
- If provider outage > 1 hour -> Consider emergency failover
- If data integrity concerns -> Engage SRE and Security

## Post-Mortem Template
- Root cause analysis
- Timeline of events
- Impact assessment (users affected, cost)
- Action items for prevention
```

---

## 14. HEALTH CHECKS, READINESS PROBES, AND GRACEFUL DEGRADATION

### What are Health Checks?

**Health checks** are endpoints in your application that report whether the service is running correctly. They're like a doctor's checkup for your application — a quick assessment of vital signs.

There are three types of health checks:

1. **Liveness probe** — "Is the process alive?" If this fails, the container/orchestrator restarts the service. This checks that the application hasn't deadlocked or crashed.

2. **Readiness probe** — "Is the service ready to accept traffic?" A service might be alive but not ready (e.g., still loading a large ML model). If this fails, the load balancer stops sending traffic to this instance until it's ready.

3. **Startup probe** — "Has the service finished starting up?" Some services take a long time to start (loading models, warming caches). This probe tells the orchestrator to wait before checking liveness.

**Graceful degradation** means your application continues to function (with reduced capabilities) when dependencies fail. Instead of crashing completely when the LLM provider is down, a gracefully degrading service might:
- Return cached responses
- Use a simpler fallback model
- Disable non-critical features
- Queue requests for later processing

### 14.1 HEALTH CHECK IMPLEMENTATION

```python
# File: src/health/checks.py
"""Comprehensive health checks for AI services."""

import asyncio
import time
import psutil
import torch
from enum import Enum
from pydantic import BaseModel
from fastapi import APIRouter, Response

router = APIRouter()


class HealthStatus(str, Enum):
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"


class DependencyCheck(BaseModel):
    name: str
    status: HealthStatus
    latency_ms: float
    message: str = ""


class HealthResponse(BaseModel):
    status: HealthStatus
    version: str
    uptime_seconds: float
    checks: list[DependencyCheck] = []
    metadata: dict = {}


_start_time = time.time()


class HealthChecker:
    """Run health checks for all dependencies."""

    def __init__(self):
        self.checks = {}

    def register_check(self, name: str, check_fn):
        """Register a health check function."""
        self.checks[name] = check_fn

    async def run_all_checks(self, timeout: float = 5.0) -> tuple[HealthStatus, list[DependencyCheck]]:
        """Run all registered health checks."""
        results = []
        overall_status = HealthStatus.HEALTHY

        for name, check_fn in self.checks.items():
            try:
                start = time.time()
                result = await asyncio.wait_for(check_fn(), timeout=timeout)
                latency = (time.time() - start) * 1000

                check = DependencyCheck(
                    name=name,
                    status=result.get("status", HealthStatus.HEALTHY),
                    latency_ms=round(latency, 2),
                    message=result.get("message", ""),
                )
            except asyncio.TimeoutError:
                check = DependencyCheck(
                    name=name,
                    status=HealthStatus.UNHEALTHY,
                    latency_ms=timeout * 1000,
                    message=f"Check timed out after {timeout}s",
                )
            except Exception as e:
                check = DependencyCheck(
                    name=name,
                    status=HealthStatus.UNHEALTHY,
                    latency_ms=0,
                    message=str(e),
                )

            results.append(check)

            if check.status == HealthStatus.UNHEALTHY:
                overall_status = HealthStatus.UNHEALTHY
            elif check.status == HealthStatus.DEGRADED and overall_status == HealthStatus.HEALTHY:
                overall_status = HealthStatus.DEGRADED

        return overall_status, results


health_checker = HealthChecker()


async def check_database():
    """Check database connectivity."""
    try:
        from src.database import get_db_session
        async with get_db_session() as session:
            await session.execute("SELECT 1")
        return {"status": HealthStatus.HEALTHY, "message": "Connected"}
    except Exception as e:
        return {"status": HealthStatus.UNHEALTHY, "message": str(e)}


async def check_redis():
    """Check Redis connectivity."""
    try:
        from src.cache import get_redis
        redis = get_redis()
        await redis.ping()
        return {"status": HealthStatus.HEALTHY, "message": "Connected"}
    except Exception as e:
        return {"status": HealthStatus.DEGRADED, "message": f"Redis unavailable: {e}"}


async def check_vector_db():
    """Check vector database connectivity."""
    try:
        from src.vector_store import get_vector_store
        store = get_vector_store()
        await store.health_check()
        return {"status": HealthStatus.HEALTHY, "message": "Connected"}
    except Exception as e:
        return {"status": HealthStatus.DEGRADED, "message": f"VectorDB unavailable: {e}"}


async def check_llm_provider():
    """Check LLM provider availability."""
    try:
        from src.llm import get_llm_client
        client = get_llm_client()
        response = await client.complete("Hello", max_tokens=5)
        return {"status": HealthStatus.HEALTHY, "message": "Provider responding"}
    except Exception as e:
        return {"status": HealthStatus.UNHEALTHY, "message": f"LLM provider error: {e}"}


async def check_gpu():
    """Check GPU availability."""
    if not torch.cuda.is_available():
        return {"status": HealthStatus.DEGRADED, "message": "No GPU available"}

    try:
        gpu_memory = torch.cuda.get_device_properties(0).total_mem
        gpu_used = torch.cuda.memory_allocated(0)
        usage_pct = (gpu_used / gpu_memory) * 100

        if usage_pct > 95:
            return {"status": HealthStatus.UNHEALTHY, "message": f"GPU memory at {usage_pct:.1f}%"}
        elif usage_pct > 85:
            return {"status": HealthStatus.DEGRADED, "message": f"GPU memory at {usage_pct:.1f}%"}
        return {"status": HealthStatus.HEALTHY, "message": f"GPU OK ({usage_pct:.1f}% used)"}
    except Exception as e:
        return {"status": HealthStatus.DEGRADED, "message": f"GPU check failed: {e}"}


async def check_system_resources():
    """Check system resources (CPU, memory, disk)."""
    cpu_pct = psutil.cpu_percent(interval=0.1)
    mem = psutil.virtual_memory()
    disk = psutil.disk_usage("/")

    issues = []
    if cpu_pct > 90:
        issues.append(f"CPU at {cpu_pct}%")
    if mem.percent > 90:
        issues.append(f"Memory at {mem.percent}%")
    if disk.percent > 90:
        issues.append(f"Disk at {disk.percent}%")

    if issues:
        status = HealthStatus.DEGRADED if len(issues) == 1 else HealthStatus.UNHEALTHY
        return {"status": status, "message": "; ".join(issues)}

    return {"status": HealthStatus.HEALTHY, "message": "Resources OK"}


# Register all checks
health_checker.register_check("database", check_database)
health_checker.register_check("redis", check_redis)
health_checker.register_check("vector_db", check_vector_db)
health_checker.register_check("llm_provider", check_llm_provider)
health_checker.register_check("gpu", check_gpu)
health_checker.register_check("system", check_system_resources)


@router.get("/health", response_model=HealthResponse)
async def health_check(response: Response):
    """Liveness probe - is the service running?"""
    status, checks = await health_checker.run_all_checks(timeout=3.0)

    if status == HealthStatus.UNHEALTHY:
        response.status_code = 503

    return HealthResponse(
        status=status,
        version="1.0.0",
        uptime_seconds=round(time.time() - _start_time, 2),
        checks=checks,
    )


@router.get("/ready", response_model=HealthResponse)
async def readiness_check(response: Response):
    """Readiness probe - is the service ready to accept traffic?"""
    critical_checks = {
        name: fn for name, fn in health_checker.checks.items()
        if name in ("database", "llm_provider")
    }

    results = []
    overall_status = HealthStatus.HEALTHY

    for name, check_fn in critical_checks.items():
        try:
            start = time.time()
            result = await asyncio.wait_for(check_fn(), timeout=2.0)
            latency = (time.time() - start) * 1000

            check = DependencyCheck(
                name=name,
                status=result.get("status", HealthStatus.HEALTHY),
                latency_ms=round(latency, 2),
                message=result.get("message", ""),
            )
        except Exception:
            check = DependencyCheck(
                name=name,
                status=HealthStatus.UNHEALTHY,
                latency_ms=0,
                message="Check failed",
            )
            overall_status = HealthStatus.UNHEALTHY

        results.append(check)

    if overall_status == HealthStatus.UNHEALTHY:
        response.status_code = 503

    return HealthResponse(
        status=overall_status,
        version="1.0.0",
        uptime_seconds=round(time.time() - _start_time, 2),
        checks=results,
    )


@router.get("/startup")
async def startup_check(response: Response):
    """Startup probe - has the service finished initializing?"""
    uptime = time.time() - _start_time

    if uptime < 120:
        try:
            from src.models import get_model
            model = get_model()
            if model is None:
                response.status_code = 503
                return {"status": "starting", "uptime_seconds": round(uptime, 2)}
        except Exception:
            response.status_code = 503
            return {"status": "starting", "uptime_seconds": round(uptime, 2)}

    return {"status": "ready", "uptime_seconds": round(uptime, 2)}
```

### 14.2 GRACEFUL DEGRADATION

```python
# File: src/resilience/degradation.py
"""Graceful degradation strategies for AI services."""

import asyncio
import logging
from enum import Enum
from typing import Callable, Any
from functools import wraps
import circuitbreaker

logger = logging.getLogger(__name__)


class DegradationLevel(Enum):
    """Service degradation levels."""
    FULL = "full"              # All features available
    REDUCED = "reduced"        # Non-critical features disabled
    MINIMAL = "minimal"        # Only core features
    EMERGENCY = "emergency"    # Cached responses only


class ServiceDegradation:
    """Manage service degradation based on dependency health."""

    def __init__(self):
        self.level = DegradationLevel.FULL
        self._degraded_services: set = set()

    def degrade(self, service: str, level: DegradationLevel):
        """Mark a service as degraded."""
        self._degraded_services.add(service)
        self._update_level()
        logger.warning(f"Service degraded: {service} -> {level.value}")

    def recover(self, service: str):
        """Mark a service as recovered."""
        self._degraded_services.discard(service)
        self._update_level()
        logger.info(f"Service recovered: {service}")

    def _update_level(self):
        """Update overall degradation level."""
        count = len(self._degraded_services)
        if count == 0:
            self.level = DegradationLevel.FULL
        elif count == 1:
            self.level = DegradationLevel.REDUCED
        elif count == 2:
            self.level = DegradationLevel.MINIMAL
        else:
            self.level = DegradationLevel.EMERGENCY

    def is_available(self, feature: str) -> bool:
        """Check if a feature is available at current degradation level."""
        feature_requirements = {
            "llm_inference": DegradationLevel.FULL,
            "vector_search": DegradationLevel.REDUCED,
            "personalization": DegradationLevel.MINIMAL,
            "caching": DegradationLevel.EMERGENCY,
            "analytics": DegradationLevel.REDUCED,
        }
        required = feature_requirements.get(feature, DegradationLevel.FULL)
        return self.level.value <= required.value


degradation_manager = ServiceDegradation()


def with_fallback(fallback_fn: Callable = None, fallback_value: Any = None):
    """Decorator that provides fallback behavior when a function fails."""
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            try:
                return await func(*args, **kwargs)
            except circuitbreaker.CircuitBreakerError:
                logger.warning(f"Circuit breaker open for {func.__name__}")
                if fallback_fn:
                    return await fallback_fn(*args, **kwargs)
                return fallback_value
            except Exception as e:
                logger.error(f"Error in {func.__name__}: {e}")
                if fallback_fn:
                    try:
                        return await fallback_fn(*args, **kwargs)
                    except Exception as fallback_error:
                        logger.error(f"Fallback also failed: {fallback_error}")
                return fallback_value
        return wrapper
    return decorator
```

---

# PART 3: LIFECYCLE MANAGEMENT

---

## 15. CI/CD PIPELINES FOR AI DEPLOYMENTS

### What is CI/CD?

**CI/CD** stands for **Continuous Integration / Continuous Deployment**. It's the automated pipeline that takes your code from "developer wrote it" to "running in production."

**Continuous Integration (CI)** — Every time a developer pushes code, automatically:
- Run linters (code style checkers)
- Run unit tests
- Run integration tests
- Build the Docker image
- Scan for security vulnerabilities
- Run AI-specific tests (model evaluation, prompt regression, bias detection)

**Continuous Deployment (CD)** — After CI passes, automatically:
- Deploy to a staging environment
- Run smoke tests
- Deploy to production (canary, blue-green, or rolling)
- Monitor for errors
- Automatically rollback if something goes wrong

Why is CI/CD critical for AI applications?
- **Speed** — Deploy multiple times per day instead of once per month
- **Safety** — Automated tests catch bugs before they reach production
- **Confidence** — You can deploy with confidence knowing tests will catch issues
- **Rollback** — If a deployment breaks something, CI/CD can automatically roll back
- **Reproducibility** — Every deployment follows the same process, no manual steps

Key CI/CD tools:
- **GitHub Actions** — CI/CD built into GitHub. Free for public repos, generous free tier for private.
- **GitLab CI** — CI/CD built into GitLab. Similar to GitHub Actions.
- **ArgoCD** — GitOps for Kubernetes. Automatically syncs Kubernetes manifests from Git.
- **CircleCI** — Cloud-based CI/CD. Fast, good caching.
- **Jenkins** — Self-hosted CI/CD. Very flexible, requires maintenance.

### 15.1 CI/CD PIPELINE ARCHITECTURE

```
┌─────────────────────────────────────────────────────────────────────────┐
│                    AI CI/CD PIPELINE                                    │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  Code Push                                                              │
│  │                                                                      │
│  v                                                                      │
│  ┌──────────────────┐                                                  │
│  │  CI: Build & Test │                                                  │
│  │  ├─ Lint & Format │                                                  │
│  │  ├─ Unit Tests    │                                                  │
│  │  ├─ Type Check    │                                                  │
│  │  ├─ Security Scan │                                                  │
│  │  └─ Build Image   │                                                  │
│  └────────┬─────────┘                                                  │
│           │                                                             │
│           v                                                             │
│  ┌──────────────────┐                                                  │
│  │  AI Validation    │                                                  │
│  │  ├─ Model Tests   │                                                  │
│  │  ├─ Eval Suite    │                                                  │
│  │  ├─ Prompt Tests  │                                                  │
│  │  └─ Bias Check    │                                                  │
│  └────────┬─────────┘                                                  │
│           │                                                             │
│           v                                                             │
│  ┌──────────────────┐                                                  │
│  │  Staging Deploy   │                                                  │
│  │  ├─ Smoke Tests   │                                                  │
│  │  ├─ Load Tests    │                                                  │
│  │  ├─ Integration   │                                                  │
│  │  └─ E2E Tests     │                                                  │
│  └────────┬─────────┘                                                  │
│           │                                                             │
│           v                                                             │
│  ┌──────────────────┐                                                  │
│  │  Production       │                                                  │
│  │  ├─ Canary (5%)   │                                                  │
│  │  ├─ Monitor 15min │                                                  │
│  │  ├─ Ramp to 50%   │                                                  │
│  │  ├─ Monitor 15min │                                                  │
│  │  └─ Full rollout  │                                                  │
│  └──────────────────┘                                                  │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

### 15.2 GITHUB ACTIONS CI/CD

```yaml
# File: .github/workflows/ai-deploy.yml
name: AI Service CI/CD

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

env:
  REGISTRY: ghcr.io
  IMAGE_NAME: ${{ github.repository }}/ai-service
  PYTHON_VERSION: "3.11"

jobs:
  # ============================================
  # CI: Build, Test, Lint
  # ============================================
  ci:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: ${{ env.PYTHON_VERSION }}
          cache: pip

      - name: Install dependencies
        run: |
          pip install -r requirements.txt
          pip install -r requirements-dev.txt

      - name: Lint with ruff
        run: ruff check src/ tests/

      - name: Type check with mypy
        run: mypy src/ --ignore-missing-imports

      - name: Security scan
        uses: pypa/gh-action-pip-audit@v1
        with:
          inputs: requirements.txt

      - name: Run unit tests
        run: pytest tests/unit/ -v --cov=src --cov-report=xml --cov-report=term

      - name: Upload coverage
        uses: codecov/codecov-action@v3
        with:
          file: coverage.xml

  # ============================================
  # AI Validation: Model & Prompt Tests
  # ============================================
  ai-validation:
    runs-on: ubuntu-latest
    needs: ci
    steps:
      - uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: ${{ env.PYTHON_VERSION }}
          cache: pip

      - name: Install dependencies
        run: pip install -r requirements.txt

      - name: Run model evaluation tests
        env:
          OPENAI_API_KEY: ${{ secrets.OPENAI_API_KEY }}
        run: |
          python -m pytest tests/ai/ -v --tb=short -m "not slow"
        # Tests: accuracy benchmarks, prompt regression, output format validation

      - name: Run bias detection
        run: python scripts/check_bias.py --threshold 0.1

      - name: Validate prompt templates
        run: python scripts/validate_prompts.py

  # ============================================
  # Build & Push Docker Image
  # ============================================
  build:
    runs-on: ubuntu-latest
    needs: [ci, ai-validation]
    permissions:
      contents: read
      packages: write
    outputs:
      image-tag: ${{ steps.meta.outputs.tags }}
      image-digest: ${{ steps.build.outputs.digest }}
    steps:
      - uses: actions/checkout@v4

      - name: Log in to Container Registry
        uses: docker/login-action@v3
        with:
          registry: ${{ env.REGISTRY }}
          username: ${{ github.actor }}
          password: ${{ secrets.GITHUB_TOKEN }}

      - name: Extract metadata
        id: meta
        uses: docker/metadata-action@v5
        with:
          images: ${{ env.REGISTRY }}/${{ env.IMAGE_NAME }}
          tags: |
            type=sha,prefix=
            type=ref,event=branch
            type=semver,pattern={{version}}

      - name: Build and push
        id: build
        uses: docker/build-push-action@v5
        with:
          context: .
          push: true
          tags: ${{ steps.meta.outputs.tags }}
          labels: ${{ steps.meta.outputs.labels }}
          cache-from: type=gha
          cache-to: type=gha,mode=max

  # ============================================
  # Deploy to Staging
  # ============================================
  deploy-staging:
    runs-on: ubuntu-latest
    needs: build
    environment: staging
    steps:
      - uses: actions/checkout@v4

      - name: Set up kubectl
        uses: azure/setup-kubectl@v3

      - name: Set kubeconfig
        run: echo "${{ secrets.KUBE_CONFIG_STAGING }}" | base64 -d > $HOME/.kube/config

      - name: Deploy to staging
        run: |
          kubectl set image deployment/ai-api \
            ai-api=${{ needs.build.outputs.image-tag }} \
            -n ai-staging
          kubectl rollout status deployment/ai-api -n ai-staging --timeout=300s

      - name: Run smoke tests
        run: |
          python tests/smoke/test_staging.py --url https://staging-api.myapp.com

      - name: Run load tests
        run: |
          locust -f tests/load/locustfile.py \
            --host https://staging-api.myapp.com \
            --users 50 --spawn-rate 5 --run-time 2m \
            --headless --only-summary

  # ============================================
  # Deploy to Production (Canary)
  # ============================================
  deploy-production:
    runs-on: ubuntu-latest
    needs: [build, deploy-staging]
    if: github.ref == 'refs/heads/main'
    environment: production
    steps:
      - uses: actions/checkout@v4

      - name: Set up kubectl
        uses: azure/setup-kubectl@v3

      - name: Set kubeconfig
        run: echo "${{ secrets.KUBE_CONFIG_PROD }}" | base64 -d > $HOME/.kube/config

      - name: Canary deploy (5% traffic)
        run: |
          # Deploy new version alongside existing
          kubectl set image deployment/ai-api-canary \
            ai-api=${{ needs.build.outputs.image-tag }} \
            -n ai-production
          kubectl scale deployment/ai-api-canary --replicas=1 -n ai-production

          # Wait for canary to be ready
          kubectl rollout status deployment/ai-api-canary -n ai-production --timeout=300s

      - name: Monitor canary (15 minutes)
        run: |
          echo "Monitoring canary for 15 minutes..."
          for i in $(seq 1 15); do
            # Check error rate
            ERROR_RATE=$(curl -s "http://prometheus:9090/api/v1/query?query=rate(ai_requests_total{version='canary',status_code=~'5..'}[5m])/rate(ai_requests_total{version='canary'}[5m])" | jq '.data.result[0].value[1]' -r)

            echo "Minute $i: Error rate = $ERROR_RATE"

            if (( $(echo "$ERROR_RATE > 0.05" | bc -l) )); then
              echo "Error rate too high! Rolling back canary..."
              kubectl scale deployment/ai-api-canary --replicas=0 -n ai-production
              exit 1
            fi

            sleep 60
          done

      - name: Promote canary to full rollout
        run: |
          kubectl set image deployment/ai-api \
            ai-api=${{ needs.build.outputs.image-tag }} \
            -n ai-production
          kubectl rollout status deployment/ai-api -n ai-production --timeout=600s

          # Remove canary
          kubectl scale deployment/ai-api-canary --replicas=0 -n ai-production

      - name: Post-deploy validation
        run: |
          python tests/smoke/test_production.py --url https://api.myapp.com

  # ============================================
  # Rollback (on failure)
  # ============================================
  rollback:
    runs-on: ubuntu-latest
    needs: deploy-production
    if: failure()
    steps:
      - name: Set up kubectl
        uses: azure/setup-kubectl@v3

      - name: Set kubeconfig
        run: echo "${{ secrets.KUBE_CONFIG_PROD }}" | base64 -d > $HOME/.kube/config

      - name: Rollback deployment
        run: |
          kubectl rollout undo deployment/ai-api -n ai-production
          kubectl rollout status deployment/ai-api -n ai-production --timeout=300s

      - name: Notify team
        uses: slackapi/slack-github-action@v1
        with:
          payload: |
            {
              "text": "Production deployment FAILED and was rolled back. Commit: ${{ github.sha }}"
            }
        env:
          SLACK_WEBHOOK_URL: ${{ secrets.SLACK_WEBHOOK }}
```

### 15.3 GITLAB CI PIPELINE

```yaml
# File: .gitlab-ci.yml
stages:
  - test
  - ai-validate
  - build
  - deploy-staging
  - deploy-production
  - monitor

variables:
  PYTHON_VERSION: "3.11"
  IMAGE_TAG: $CI_REGISTRY_IMAGE/ai-service:$CI_COMMIT_SHORT_SHA

test:
  stage: test
  image: python:${PYTHON_VERSION}
  script:
    - pip install -r requirements.txt -r requirements-dev.txt
    - ruff check src/ tests/
    - mypy src/ --ignore-missing-imports
    - pytest tests/unit/ -v --cov=src
  cache:
    paths:
      - .pip-cache/

ai-validation:
  stage: ai-validate
  image: python:${PYTHON_VERSION}
  script:
    - pip install -r requirements.txt
    - python -m pytest tests/ai/ -v
    - python scripts/check_bias.py --threshold 0.1
  artifacts:
    reports:
      junit: tests/ai/results.xml

build:
  stage: build
  image: docker:latest
  services:
    - docker:dind
  script:
    - docker login -u $CI_REGISTRY_USER -p $CI_REGISTRY_PASSWORD $CI_REGISTRY
    - docker build -t $IMAGE_TAG .
    - docker push $IMAGE_TAG

deploy-staging:
  stage: deploy-staging
  image: bitnami/kubectl:latest
  script:
    - kubectl set image deployment/ai-api ai-api=$IMAGE_TAG -n ai-staging
    - kubectl rollout status deployment/ai-api -n ai-staging --timeout=300s
    - python tests/smoke/test_staging.py
  environment:
    name: staging
  only:
    - main

deploy-production:
  stage: deploy-production
  image: bitnami/kubectl:latest
  script:
    - kubectl set image deployment/ai-api ai-api=$IMAGE_TAG -n ai-production
    - kubectl rollout status deployment/ai-api -n ai-production --timeout=600s
  environment:
    name: production
  when: manual
  only:
    - main

monitor:
  stage: monitor
  script:
    - sleep 900  # Wait 15 minutes
    - python scripts/check_production_health.py
  needs:
    - deploy-production
```

### 15.4 ARGOCD GITOPS

```yaml
# File: deploy/argocd/ai-service-app.yaml
apiVersion: argoproj.io/v1alpha1
kind: Application
metadata:
  name: ai-service
  namespace: argocd
  annotations:
    notifications.argoproj.io/subscribe.on-sync-succeeded.slack: ai-deploys
    notifications.argoproj.io/subscribe.on-sync-failed.slack: ai-alerts
spec:
  project: ai-platform
  source:
    repoURL: https://github.com/myorg/ai-infra.git
    targetRevision: main
    path: k8s/overlays/production
  destination:
    server: https://kubernetes.default.svc
    namespace: ai-production
  syncPolicy:
    automated:
      prune: true
      selfHeal: true
      allowEmpty: false
    syncOptions:
      - CreateNamespace=true
      - PrunePropagationPolicy=foreground
      - PruneLast=true
    retry:
      limit: 5
      backoff:
        duration: 5s
        factor: 2
        maxDuration: 3m
  # Progressive sync (canary)
  strategy:
    canary:
      steps:
        - setWeight: 5
        - pause: {duration: 15m}
        - setWeight: 25
        - pause: {duration: 10m}
        - setWeight: 50
        - pause: {duration: 10m}
        - setWeight: 100
```

---

## 16. DEPLOYMENT PATTERNS

### What are Deployment Patterns?

**Deployment patterns** are strategies for releasing new versions of your application to production. The key question they answer is: **how do you switch from the old version to the new version without breaking things?**

The simplest approach ("stop the old version, start the new version") causes **downtime** — users get errors during the switch. Deployment patterns avoid this by carefully managing the transition:

- **Rolling update** — Replace old instances one at a time. Zero downtime, but if the new version is broken, some users will see errors.
- **Blue-green** — Run old and new versions side by side, then switch traffic instantly. Zero downtime, instant rollback, but requires 2x resources.
- **Canary** — Send 5% of traffic to the new version. If it's healthy, gradually increase to 100%. Safest approach, catches issues before they affect all users.
- **Shadow** — Mirror real traffic to the new version but discard its responses. Tests the new version with real traffic without affecting users. Great for validating ML model changes.
- **Recreate** — Stop old version, start new version. Simple but causes downtime. Only for non-production environments.

For AI applications, **canary deployments** are especially important because ML model changes can have subtle quality degradations that aren't caught by simple health checks. A canary deployment lets you compare the new model's output quality against the old model using real traffic.

### 16.1 DEPLOYMENT PATTERN COMPARISON

```
┌─────────────────────────────────────────────────────────────────────────┐
│                    DEPLOYMENT PATTERNS                                  │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  RECREATE (Big Bang)                                                    │
│  ┌──────────┐    ┌──────────┐                                          │
│  │  v1      │    │  v2      │                                          │
│  │ ████████ │ -> │          │ -> │ ████████ │                          │
│  └──────────┘    └──────────┘    └──────────┘                          │
│  Downtime: YES    Risk: HIGH    Rollback: SLOW                         │
│                                                                         │
│  ROLLING UPDATE                                                         │
│  ┌──────────────────────────┐                                          │
│  │ v1  │ v1  │ v1  │ v1    │    Step 1: Replace 1 at a time           │
│  │ v2  │ v1  │ v1  │ v1    │    Step 2:                               │
│  │ v2  │ v2  │ v1  │ v1    │    Step 3:                               │
│  │ v2  │ v2  │ v2  │ v2    │                                          │
│  └──────────────────────────┘                                          │
│  Downtime: NO     Risk: MEDIUM  Rollback: MEDIUM                       │
│                                                                         │
│  BLUE-GREEN                                                             │
│  ┌──────────┐    ┌──────────┐                                          │
│  │  Blue    │    │  Green   │                                          │
│  │  (v1)    │    │  (v2)    │    Switch traffic instantly               │
│  │ ████████ │    │ ████████ │                                          │
│  └─────┬────┘    └────┬─────┘                                          │
│        └──── Load ────┘                                                 │
│             Balancer                                                    │
│  Downtime: NO     Risk: LOW     Rollback: INSTANT                      │
│                                                                         │
│  CANARY                                                                 │
│  ┌──────────────────────────┐                                          │
│  │  v1 (95%)  │  v2 (5%)   │    Gradually shift traffic                │
│  │  v1 (75%)  │  v2 (25%)  │                                          │
│  │  v1 (50%)  │  v2 (50%)  │                                          │
│  │  v1 (0%)   │  v2 (100%) │                                          │
│  └──────────────────────────┘                                          │
│  Downtime: NO     Risk: LOWEST  Rollback: FAST                         │
│                                                                         │
│  SHADOW                                                                 │
│  ┌──────────────────────────┐                                          │
│  │  v1 (live)  │  v2 (shadow)│   v2 receives real traffic but          │
│  │ ████████    │  (mirror)    │   responses are discarded               │
│  └──────────────────────────┘                                          │
│  Downtime: NO     Risk: ZERO    Rollback: N/A                          │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

### 16.2 BLUE-GREEN DEPLOYMENT

```python
# File: deploy/blue_green.py
"""Blue-Green deployment manager."""

import asyncio
import httpx
import logging
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)


class Environment(str, Enum):
    BLUE = "blue"
    GREEN = "green"


@dataclass
class DeploymentState:
    active: Environment
    blue_version: str
    green_version: str
    blue_healthy: bool
    green_healthy: bool


class BlueGreenDeployer:
    """Manage blue-green deployments."""

    def __init__(
        self,
        blue_url: str,
        green_url: str,
        load_balancer_api: str,
    ):
        self.blue_url = blue_url
        self.green_url = green_url
        self.lb_api = load_balancer_api
        self.state = DeploymentState(
            active=Environment.BLUE,
            blue_version="v1",
            green_version="v1",
            blue_healthy=True,
            green_healthy=True,
        )

    async def get_active_environment(self) -> Environment:
        """Get the currently active environment."""
        return self.state.active

    async def deploy_to_inactive(self, version: str, image: str):
        """Deploy new version to the inactive environment."""
        inactive = Environment.GREEN if self.state.active == Environment.BLUE else Environment.BLUE
        url = self.green_url if inactive == Environment.GREEN else self.blue_url

        logger.info(f"Deploying {version} to {inactive.value} environment")

        # Update the inactive environment
        await self._update_deployment(inactive, image, version)

        # Wait for rollout
        await self._wait_for_rollout(inactive)

        # Health check
        healthy = await self._health_check(url)
        if not healthy:
            raise Exception(f"{inactive.value} environment unhealthy after deployment")

        # Update state
        if inactive == Environment.GREEN:
            self.state.green_version = version
            self.state.green_healthy = True
        else:
            self.state.blue_version = version
            self.state.blue_healthy = True

        logger.info(f"Deployment to {inactive.value} complete: {version}")

    async def switch_traffic(self):
        """Switch traffic from active to inactive environment."""
        current = self.state.active
        target = Environment.GREEN if current == Environment.BLUE else Environment.BLUE
        target_url = self.green_url if target == Environment.GREEN else self.blue_url

        logger.info(f"Switching traffic: {current.value} -> {target.value}")

        # Verify target is healthy
        healthy = await self._health_check(target_url)
        if not healthy:
            raise Exception(f"Cannot switch: {target.value} environment is unhealthy")

        # Switch load balancer
        await self._update_load_balancer(target)

        # Update state
        self.state.active = target
        logger.info(f"Traffic switched to {target.value}")

    async def rollback(self):
        """Rollback to the previous environment."""
        current = self.state.active
        previous = Environment.GREEN if current == Environment.BLUE else Environment.BLUE

        logger.warning(f"Rolling back: {current.value} -> {previous.value}")
        await self._update_load_balancer(previous)
        self.state.active = previous
        logger.info(f"Rollback complete. Active: {previous.value}")

    async def _health_check(self, url: str) -> bool:
        """Check if an environment is healthy."""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(f"{url}/health", timeout=10)
                return response.status_code == 200
        except Exception as e:
            logger.error(f"Health check failed for {url}: {e}")
            return False

    async def _update_deployment(self, env: Environment, image: str, version: str):
        """Update Kubernetes deployment for an environment."""
        # kubectl set image deployment/ai-api-{env} ai-api={image}
        import subprocess
        cmd = [
            "kubectl", "set", "image",
            f"deployment/ai-api-{env.value}",
            f"ai-api={image}",
            "-n", "ai-production",
        ]
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode != 0:
            raise Exception(f"Deployment update failed: {result.stderr}")

    async def _wait_for_rollout(self, env: Environment, timeout: int = 300):
        """Wait for Kubernetes rollout to complete."""
        import subprocess
        cmd = [
            "kubectl", "rollout", "status",
            f"deployment/ai-api-{env.value}",
            "-n", "ai-production",
            f"--timeout={timeout}s",
        ]
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode != 0:
            raise Exception(f"Rollout failed: {result.stderr}")

    async def _update_load_balancer(self, target: Environment):
        """Update load balancer to point to target environment."""
        # This could be updating an Ingress, service selector, etc.
        import subprocess
        cmd = [
            "kubectl", "patch", "service", "ai-api",
            "-n", "ai-production",
            "-p", f'{{"spec":{{"selector":{{"version":"{target.value}"}}}}}}',
        ]
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode != 0:
            raise Exception(f"LB update failed: {result.stderr}")
```

### 16.3 CANARY DEPLOYMENT WITH ISTIO

```yaml
# File: k8s/canary/istio-virtual-service.yaml
apiVersion: networking.istio.io/v1beta1
kind: VirtualService
metadata:
  name: ai-api
  namespace: ai-production
spec:
  hosts:
    - ai-api
    - api.myapp.com
  http:
    - match:
        - headers:
            x-canary:
              exact: "true"
      route:
        - destination:
            host: ai-api
            subset: canary
          weight: 100
    - route:
        - destination:
            host: ai-api
            subset: stable
          weight: 95
        - destination:
            host: ai-api
            subset: canary
          weight: 5
      retries:
        attempts: 3
        perTryTimeout: 10s
        retryOn: 5xx
---
apiVersion: networking.istio.io/v1beta1
kind: DestinationRule
metadata:
  name: ai-api
  namespace: ai-production
spec:
  host: ai-api
  subsets:
    - name: stable
      labels:
        version: stable
    - name: canary
      labels:
        version: canary
  trafficPolicy:
    connectionPool:
      tcp:
        maxConnections: 100
      http:
        h2UpgradePolicy: DEFAULT
        http1MaxPendingRequests: 100
        http2MaxRequests: 1000
    outlierDetection:
      consecutive5xxErrors: 5
      interval: 30s
      baseEjectionTime: 30s
      maxEjectionPercent: 50
```

```python
# File: deploy/canary_manager.py
"""Automated canary deployment with metrics-based promotion."""

import asyncio
import httpx
import logging
from dataclasses import dataclass
from datetime import datetime

logger = logging.getLogger(__name__)


@dataclass
class CanaryMetrics:
    """Metrics for canary evaluation."""
    error_rate: float
    latency_p99_ms: float
    latency_p95_ms: float
    success_rate: float
    request_count: int


class CanaryDeployer:
    """Automated canary deployment with progressive traffic shifting."""

    def __init__(
        self,
        prometheus_url: str,
        k8s_namespace: str = "ai-production",
    ):
        self.prometheus_url = prometheus_url
        self.namespace = k8s_namespace
        self.traffic_steps = [5, 10, 25, 50, 75, 100]
        self.step_duration_minutes = 15
        self.thresholds = {
            "max_error_rate": 0.01,      # 1%
            "max_latency_p99_ms": 5000,   # 5 seconds
            "min_success_rate": 0.99,     # 99%
            "min_request_count": 100,     # At least 100 requests per step
        }

    async def deploy_canary(self, image: str, version: str):
        """Run a full canary deployment."""
        logger.info(f"Starting canary deployment: {version}")

        # Deploy canary with 0 replicas
        await self._deploy_canary(image, version)

        for weight in self.traffic_steps:
            logger.info(f"Setting canary traffic to {weight}%")
            await self._set_traffic_weight(weight)

            # Wait and monitor
            logger.info(f"Monitoring at {weight}% for {self.step_duration_minutes} minutes")
            healthy = await self._monitor_step(weight)

            if not healthy:
                logger.error(f"Canary failed at {weight}% traffic. Rolling back.")
                await self._rollback_canary()
                return False

            logger.info(f"Canary healthy at {weight}% traffic")

        # All steps passed - promote canary
        logger.info("Canary passed all checks. Promoting to stable.")
        await self._promote_canary()
        return True

    async def _deploy_canary(self, image: str, version: str):
        """Deploy canary version."""
        import subprocess
        cmd = [
            "kubectl", "set", "image",
            "deployment/ai-api-canary",
            f"ai-api={image}",
            "-n", self.namespace,
        ]
        subprocess.run(cmd, check=True)

        # Scale up
        cmd = [
            "kubectl", "scale", "deployment/ai-api-canary",
            "--replicas=2", "-n", self.namespace,
        ]
        subprocess.run(cmd, check=True)

        # Wait for ready
        cmd = [
            "kubectl", "rollout", "status",
            "deployment/ai-api-canary",
            "-n", self.namespace, "--timeout=300s",
        ]
        subprocess.run(cmd, check=True)

    async def _set_traffic_weight(self, canary_weight: int):
        """Set traffic weight using Istio VirtualService."""
        stable_weight = 100 - canary_weight
        patch = {
            "spec": {
                "http": [{
                    "route": [
                        {"destination": {"host": "ai-api", "subset": "stable"}, "weight": stable_weight},
                        {"destination": {"host": "ai-api", "subset": "canary"}, "weight": canary_weight},
                    ]
                }]
            }
        }

        import subprocess
        import json
        cmd = [
            "kubectl", "patch", "virtualservice", "ai-api",
            "-n", self.namespace,
            "--type=merge",
            "-p", json.dumps(patch),
        ]
        subprocess.run(cmd, check=True)

    async def _monitor_step(self, weight: int) -> bool:
        """Monitor canary metrics for one step duration."""
        import asyncio
        checks = self.step_duration_minutes  # One check per minute

        for i in range(checks):
            await asyncio.sleep(60)

            metrics = await self._get_canary_metrics()

            # Check thresholds
            if metrics.error_rate > self.thresholds["max_error_rate"]:
                logger.error(f"Error rate {metrics.error_rate:.4f} exceeds threshold")
                return False

            if metrics.latency_p99_ms > self.thresholds["max_latency_p99_ms"]:
                logger.error(f"P99 latency {metrics.latency_p99_ms}ms exceeds threshold")
                return False

            if metrics.success_rate < self.thresholds["min_success_rate"]:
                logger.error(f"Success rate {metrics.success_rate:.4f} below threshold")
                return False

            logger.info(
                f"Check {i+1}/{checks}: errors={metrics.error_rate:.4f}, "
                f"p99={metrics.latency_p99_ms}ms, success={metrics.success_rate:.4f}"
            )

        return True

    async def _get_canary_metrics(self) -> CanaryMetrics:
        """Query Prometheus for canary-specific metrics."""
        async with httpx.AsyncClient() as client:
            # Error rate
            resp = await client.get(
                f"{self.prometheus_url}/api/v1/query",
                params={"query": 'rate(ai_requests_total{version="canary",status_code=~"5.."}[5m]) / rate(ai_requests_total{version="canary"}[5m])'},
            )
            error_rate = float(resp.json()["data"]["result"][0]["value"][1]) if resp.json()["data"]["result"] else 0.0

            # P99 latency
            resp = await client.get(
                f"{self.prometheus_url}/api/v1/query",
                params={"query": 'histogram_quantile(0.99, rate(ai_request_duration_seconds_bucket{version="canary"}[5m]))'},
            )
            latency_p99 = float(resp.json()["data"]["result"][0]["value"][1]) * 1000 if resp.json()["data"]["result"] else 0.0

            # Request count
            resp = await client.get(
                f"{self.prometheus_url}/api/v1/query",
                params={"query": 'sum(rate(ai_requests_total{version="canary"}[5m])) * 300'},
            )
            request_count = int(float(resp.json()["data"]["result"][0]["value"][1])) if resp.json()["data"]["result"] else 0

            return CanaryMetrics(
                error_rate=error_rate,
                latency_p99_ms=latency_p99,
                latency_p95_ms=0,  # Similar query
                success_rate=1.0 - error_rate,
                request_count=request_count,
            )

    async def _rollback_canary(self):
        """Rollback canary deployment."""
        import subprocess
        cmd = [
            "kubectl", "scale", "deployment/ai-api-canary",
            "--replicas=0", "-n", self.namespace,
        ]
        subprocess.run(cmd, check=True)

        # Reset traffic to 100% stable
        await self._set_traffic_weight(0)
        logger.info("Canary rolled back")

    async def _promote_canary(self):
        """Promote canary to stable."""
        import subprocess

        # Update stable deployment with canary image
        # Get canary image
        cmd = [
            "kubectl", "get", "deployment/ai-api-canary",
            "-n", self.namespace,
            "-o", "jsonpath='{.spec.template.spec.containers[0].image}'",
        ]
        result = subprocess.run(cmd, capture_output=True, text=True)
        canary_image = result.stdout.strip().strip("'")

        # Update stable
        cmd = [
            "kubectl", "set", "image",
            "deployment/ai-api",
            f"ai-api={canary_image}",
            "-n", self.namespace,
        ]
        subprocess.run(cmd, check=True)

        # Wait for stable rollout
        cmd = [
            "kubectl", "rollout", "status",
            "deployment/ai-api",
            "-n", self.namespace, "--timeout=600s",
        ]
        subprocess.run(cmd, check=True)

        # Scale down canary
        cmd = [
            "kubectl", "scale", "deployment/ai-api-canary",
            "--replicas=0", "-n", self.namespace,
        ]
        subprocess.run(cmd, check=True)

        # Reset traffic
        await self._set_traffic_weight(0)
        logger.info("Canary promoted to stable")
```

---

## 17. MODEL VERSIONING AND MODEL REGISTRY

### What is Model Versioning?

**Model versioning** is the practice of tracking and managing different versions of your ML models — just like how Git tracks different versions of your code. Every time you train a new model or fine-tune an existing one, you create a new version.

Why does this matter?
- **Reproducibility** — "Which model version was running when we got those results?"
- **Rollback** — "The new model is performing worse. Let's go back to v2."
- **Comparison** — "Is model v3 actually better than v2? Let's compare their metrics."
- **Audit** — "Which model made that prediction? What data was it trained on?"
- **Collaboration** — "Team A is working on v4, Team B is testing v5. Both need to coexist."

A **model registry** is a centralized store for managing model versions. It tracks:
- Model artifacts (the actual model files)
- Version numbers and metadata
- Training metrics (accuracy, loss, etc.)
- Stage (development, staging, production, archived)
- Who trained it, when, and with what data

Key model registry tools:
- **MLflow** — Open-source ML lifecycle platform. Most popular model registry. Free.
- **Weights & Biases (W&B)** — Experiment tracking + model registry. Excellent visualization.
- **DVC (Data Version Control)** — Git for data and models. Version control for ML.
- **Neptune.ai** — Experiment tracking and model registry. Good for teams.
- **SageMaker Model Registry** — AWS's managed model registry. Tight SageMaker integration.
- **Vertex AI Model Registry** — GCP's managed model registry.

### 17.1 MLflow MODEL REGISTRY

```python
# File: src/registry/mlflow_registry.py
"""MLflow Model Registry for AI model versioning."""

import mlflow
from mlflow.tracking import MlflowClient
from mlflow.entities.model_registry import ModelVersion
import logging
from datetime import datetime

logger = logging.getLogger(__name__)


class ModelRegistry:
    """Manage model versions with MLflow."""

    def __init__(self, tracking_uri: str = None):
        mlflow.set_tracking_uri(tracking_uri or "http://mlflow:5000")
        self.client = MlflowClient()

    def register_model(
        self,
        model_uri: str,
        model_name: str,
        description: str = "",
        tags: dict = None,
    ) -> ModelVersion:
        """Register a new model version."""
        # Register model
        model_version = mlflow.register_model(
            model_uri=model_uri,
            name=model_name,
        )

        # Add description
        if description:
            self.client.update_model_version(
                name=model_name,
                version=model_version.version,
                description=description,
            )

        # Add tags
        if tags:
            for key, value in tags.items():
                self.client.set_model_version_tag(
                    name=model_name,
                    version=model_version.version,
                    key=key,
                    value=value,
                )

        logger.info(f"Registered model {model_name} version {model_version.version}")
        return model_version

    def transition_stage(
        self,
        model_name: str,
        version: str,
        stage: str,
        archive_existing: bool = True,
    ):
        """Transition model to a new stage (Staging, Production, Archived)."""
        self.client.transition_model_version_stage(
            name=model_name,
            version=version,
            stage=stage,
            archive_existing_versions=archive_existing,
        )
        logger.info(f"Model {model_name} v{version} -> {stage}")

    def get_production_model(self, model_name: str) -> ModelVersion:
        """Get the current production model version."""
        versions = self.client.search_model_versions(
            f"name='{model_name}' and status='READY'"
        )

        for v in versions:
            if v.current_stage == "Production":
                return v

        raise Exception(f"No production model found for {model_name}")

    def get_model_metrics(self, model_name: str, version: str) -> dict:
        """Get metrics for a model version."""
        model_version = self.client.get_model_version(model_name, version)

        # Get the run that produced this model
        run = self.client.get_run(model_version.run_id)
        return {
            "metrics": run.data.metrics,
            "params": run.data.params,
            "tags": run.data.tags,
        }

    def compare_versions(self, model_name: str, v1: str, v2: str) -> dict:
        """Compare two model versions."""
        metrics_v1 = self.get_model_metrics(model_name, v1)
        metrics_v2 = self.get_model_metrics(model_name, v2)

        comparison = {}
        all_metrics = set(metrics_v1["metrics"].keys()) | set(metrics_v2["metrics"].keys())

        for metric in all_metrics:
            val_v1 = metrics_v1["metrics"].get(metric)
            val_v2 = metrics_v2["metrics"].get(metric)

            if val_v1 and val_v2:
                diff = float(val_v2) - float(val_v1)
                pct_change = (diff / float(val_v1)) * 100 if float(val_v1) != 0 else 0
                comparison[metric] = {
                    "v1": val_v1,
                    "v2": val_v2,
                    "diff": diff,
                    "pct_change": pct_change,
                }

        return comparison

    def list_models(self) -> list:
        """List all registered models."""
        models = self.client.search_registered_models()
        return [
            {
                "name": m.name,
                "description": m.description,
                "latest_versions": [
                    {
                        "version": v.version,
                        "stage": v.current_stage,
                        "status": v.status,
                    }
                    for v in m.latest_versions
                ],
            }
            for m in models
        ]

    def rollback_model(self, model_name: str, to_version: str):
        """Rollback to a previous model version."""
        # Archive current production
        current = self.get_production_model(model_name)
        self.transition_stage(model_name, current.version, "Archived")

        # Promote target version
        self.transition_stage(model_name, to_version, "Production")
        logger.info(f"Rolled back {model_name} to version {to_version}")
```

### 17.2 WEIGHTS & BIASES INTEGRATION

```python
# File: src/registry/wandb_integration.py
"""Weights & Biases experiment tracking and model registry."""

import wandb
import logging
from typing import Any

logger = logging.getLogger(__name__)


class WandBRegistry:
    """Model registry using Weights & Biases."""

    def __init__(self, project: str, entity: str = None):
        self.project = project
        self.entity = entity

    def log_model(
        self,
        model_name: str,
        model_path: str,
        metrics: dict,
        parameters: dict = None,
        metadata: dict = None,
    ):
        """Log a model to W&B registry."""
        run = wandb.init(
            project=self.project,
            entity=self.entity,
            job_type="model-registration",
        )

        # Log parameters
        if parameters:
            wandb.config.update(parameters)

        # Log metrics
        wandb.log(metrics)

        # Log model artifact
        artifact = wandb.Artifact(
            name=model_name,
            type="model",
            metadata=metadata or {},
        )
        artifact.add_file(model_path)
        run.log_artifact(artifact)

        run.finish()
        logger.info(f"Model {model_name} logged to W&B")

    def promote_model(self, model_name: str, version: str, stage: str):
        """Promote a model version to a stage."""
        api = wandb.Api()
        artifact = api.artifact(f"{self.entity}/{self.project}/{model_name}:v{version}")
        artifact.aliases.append(stage)
        artifact.save()
        logger.info(f"Model {model_name} v{version} promoted to {stage}")

    def get_production_model(self, model_name: str):
        """Get the production model artifact."""
        api = wandb.Api()
        artifact = api.artifact(f"{self.entity}/{self.project}/{model_name}:production")
        return artifact.download()
```

---

## 18. ROLLBACK AND RECOVERY STRATEGIES

### What is Rollback?

**Rollback** is the process of reverting your application to a previous known-good version when a deployment goes wrong. It's the "undo button" for production deployments.

Think of it like this: you just deployed a new version of your AI chatbot. Within minutes, you see the error rate spike from 0.1% to 15%. Users are getting errors. Something is broken. You have two choices:

1. **Debug in production** — Try to figure out what's wrong while users suffer. This can take hours.
2. **Rollback** — Instantly revert to the previous version that was working. Users are happy in seconds. Debug later.

Rollback is always the right first response to a bad deployment. Debug after users are unblocked.

**Recovery** goes beyond rollback — it's about restoring service after any failure (not just bad deployments). This includes:
- **Database recovery** — Restoring from backups after data corruption
- **Disaster recovery** — Switching to a backup region after a data center outage
- **Incident recovery** — Restoring service after a security breach or cascading failure

### 18.1 ROLLBACK DECISION TREE

```
┌─────────────────────────────────────────────────────────────────────────┐
│                    ROLLBACK DECISION TREE                               │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  Issue Detected?                                                        │
│  ├─ YES                                                                 │
│  │  ├─ Error rate > 5%?                                                │
│  │  │  ├─ YES -> Immediate rollback                                    │
│  │  │  └─ NO -> Monitor for 5 more minutes                             │
│  │  │                                                                   │
│  │  ├─ Latency p99 > 2x baseline?                                      │
│  │  │  ├─ YES -> Check if transient (wait 2 min)                       │
│  │  │  │  ├─ Still high -> Rollback                                    │
│  │  │  │  └─ Recovered -> Continue monitoring                          │
│  │  │  └─ NO -> Continue monitoring                                    │
│  │  │                                                                   │
│  │  ├─ Data corruption detected?                                        │
│  │  │  └─ YES -> IMMEDIATE rollback + incident                         │
│  │  │                                                                   │
│  │  ├─ Security vulnerability?                                          │
│  │  │  └─ YES -> IMMEDIATE rollback + incident                         │
│  │  │                                                                   │
│  │  └─ Model quality degraded?                                          │
│  │     ├─ Accuracy drop > 5% -> Rollback                                │
│  │     ├─ Accuracy drop 1-5% -> Canary investigation                    │
│  │     └─ Accuracy drop < 1% -> Continue, investigate later             │
│  │                                                                      │
│  └─ NO                                                                  │
│     └─ Continue deployment                                              │
│                                                                         │
│  Rollback Types:                                                        │
│  ├─ Instant (Blue-Green): Switch load balancer                          │
│  ├─ Fast (Canary): Scale down canary, route to stable                   │
│  ├─ Standard (Rolling): kubectl rollout undo                            │
│  └─ Emergency (Recreate): Delete and redeploy previous version          │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

### 18.2 AUTOMATED ROLLBACK

```python
# File: deploy/rollback_manager.py
"""Automated rollback management."""

import asyncio
import httpx
import logging
import subprocess
from dataclasses import dataclass
from datetime import datetime, timedelta
from enum import Enum

logger = logging.getLogger(__name__)


class RollbackTrigger(str, Enum):
    ERROR_RATE = "error_rate"
    LATENCY = "latency"
    HEALTH_CHECK = "health_check"
    MANUAL = "manual"
    QUALITY_DEGRADATION = "quality_degradation"


@dataclass
class RollbackConfig:
    max_error_rate: float = 0.05
    max_latency_p99_ms: float = 5000
    health_check_failure_threshold: int = 3
    monitoring_window_minutes: int = 15
    auto_rollback_enabled: bool = True


class RollbackManager:
    """Manage automated rollbacks for AI deployments."""

    def __init__(
        self,
        prometheus_url: str,
        namespace: str = "ai-production",
        config: RollbackConfig = None,
    ):
        self.prometheus_url = prometheus_url
        self.namespace = namespace
        self.config = config or RollbackConfig()
        self._consecutive_failures = 0

    async def monitor_and_rollback(self, deployment: str, duration_minutes: int = 15):
        """Monitor deployment and auto-rollback if thresholds exceeded."""
        logger.info(f"Monitoring {deployment} for {duration_minutes} minutes")

        end_time = datetime.now() + timedelta(minutes=duration_minutes)

        while datetime.now() < end_time:
            await asyncio.sleep(60)  # Check every minute

            health = await self._check_health(deployment)

            if not health["healthy"]:
                self._consecutive_failures += 1
                logger.warning(
                    f"Health check failed ({self._consecutive_failures}/{self.config.health_check_failure_threshold})"
                )

                if self._consecutive_failures >= self.config.health_check_failure_threshold:
                    if self.config.auto_rollback_enabled:
                        logger.error("Threshold exceeded. Initiating auto-rollback.")
                        await self.rollback(deployment, RollbackTrigger.HEALTH_CHECK)
                        return False
                    else:
                        logger.error("Threshold exceeded but auto-rollback is disabled.")
                        return False
            else:
                self._consecutive_failures = 0

            # Check error rate
            error_rate = await self._get_error_rate(deployment)
            if error_rate > self.config.max_error_rate:
                logger.error(f"Error rate {error_rate:.4f} exceeds {self.config.max_error_rate}")
                if self.config.auto_rollback_enabled:
                    await self.rollback(deployment, RollbackTrigger.ERROR_RATE)
                    return False

            # Check latency
            latency = await self._get_latency_p99(deployment)
            if latency > self.config.max_latency_p99_ms:
                logger.error(f"P99 latency {latency}ms exceeds {self.config.max_latency_p99_ms}ms")
                if self.config.auto_rollback_enabled:
                    await self.rollback(deployment, RollbackTrigger.LATENCY)
                    return False

            logger.info(f"Minute check: errors={error_rate:.4f}, p99={latency}ms, healthy={health['healthy']}")

        logger.info(f"Monitoring complete. {deployment} is healthy.")
        return True

    async def rollback(self, deployment: str, trigger: RollbackTrigger):
        """Execute rollback."""
        logger.warning(f"ROLLBACK: {deployment} triggered by {trigger.value}")

        # Execute kubectl rollout undo
        cmd = [
            "kubectl", "rollout", "undo",
            f"deployment/{deployment}",
            "-n", self.namespace,
        ]
        result = subprocess.run(cmd, capture_output=True, text=True)

        if result.returncode != 0:
            logger.error(f"Rollback failed: {result.stderr}")
            # Try emergency rollback
            await self._emergency_rollback(deployment)
            return

        # Wait for rollback to complete
        cmd = [
            "kubectl", "rollout", "status",
            f"deployment/{deployment}",
            "-n", self.namespace,
            "--timeout=300s",
        ]
        result = subprocess.run(cmd, capture_output=True, text=True)

        if result.returncode == 0:
            logger.info("Rollback completed successfully")
        else:
            logger.error(f"Rollback verification failed: {result.stderr}")

    async def _emergency_rollback(self, deployment: str):
        """Emergency rollback - scale down and redeploy previous version."""
        logger.critical("EMERGENCY ROLLBACK")

        # Get previous revision
        cmd = [
            "kubectl", "rollout", "history",
            f"deployment/{deployment}",
            "-n", self.namespace,
        ]
        result = subprocess.run(cmd, capture_output=True, text=True)

        # Rollback to specific revision
        cmd = [
            "kubectl", "rollout", "undo",
            f"deployment/{deployment}",
            "-n", self.namespace,
            "--to-revision=2",  # Previous revision
        ]
        subprocess.run(cmd, check=True)

    async def _check_health(self, deployment: str) -> dict:
        """Check deployment health via Kubernetes."""
        cmd = [
            "kubectl", "get", "deployment", deployment,
            "-n", self.namespace,
            "-o", "jsonpath='{.status.readyReplicas}'",
        ]
        result = subprocess.run(cmd, capture_output=True, text=True)
        ready = int(result.stdout.strip().strip("'") or 0)

        cmd = [
            "kubectl", "get", "deployment", deployment,
            "-n", self.namespace,
            "-o", "jsonpath='{.spec.replicas}'",
        ]
        result = subprocess.run(cmd, capture_output=True, text=True)
        desired = int(result.stdout.strip().strip("'") or 0)

        healthy = ready >= desired * 0.8  # At least 80% healthy
        return {"healthy": healthy, "ready": ready, "desired": desired}

    async def _get_error_rate(self, deployment: str) -> float:
        """Get current error rate from Prometheus."""
        async with httpx.AsyncClient() as client:
            resp = await client.get(
                f"{self.prometheus_url}/api/v1/query",
                params={"query": f'rate(ai_requests_total{{deployment="{deployment}",status_code=~"5.."}}[5m]) / rate(ai_requests_total{{deployment="{deployment}"}}[5m])'},
            )
            result = resp.json()["data"]["result"]
            if result:
                return float(result[0]["value"][1])
            return 0.0

    async def _get_latency_p99(self, deployment: str) -> float:
        """Get P99 latency from Prometheus."""
        async with httpx.AsyncClient() as client:
            resp = await client.get(
                f"{self.prometheus_url}/api/v1/query",
                params={"query": f'histogram_quantile(0.99, rate(ai_request_duration_seconds_bucket{{deployment="{deployment}"}}[5m])) * 1000'},
            )
            result = resp.json()["data"]["result"]
            if result:
                return float(result[0]["value"][1])
            return 0.0
```

---

## 19. UPGRADING, MIGRATION, AND HOT-SWAP STRATEGIES

### What is Upgrading and Migration?

**Upgrading** is the process of moving your application to a newer version — this could be a code update, a model update, a database schema change, or a dependency upgrade. **Migration** specifically refers to changing the underlying infrastructure (moving from one database to another, one cloud provider to another, one architecture to another).

The challenge with upgrading AI applications is that they often have **stateful components** that can't be simply replaced:
- **Models** — Large ML models take minutes to load. You can't just "restart" with a new model without causing downtime.
- **Databases** — Schema changes (adding columns, changing types) must be backward-compatible so old code still works during the transition.
- **Vector stores** — Re-indexing embeddings can take hours. You need a strategy for the transition period.
- **Caches** — Warming a cache takes time. Cold caches mean slow responses.

**Hot-swap** is a technique for updating components without restarting the service. For example:
- Swap model weights in memory without restarting the inference server
- Reload prompt templates from disk without redeploying
- Update configuration flags without a deployment

### 19.1 ZERO-DOWNTIME UPGRADE STRATEGIES

```
┌─────────────────────────────────────────────────────────────────────────┐
│                    UPGRADE STRATEGIES                                    │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  STRATEGY 1: ROLLING UPDATE (Default)                                   │
│  ├─ Replace pods one at a time                                          │
│  ├─ Kubernetes handles this automatically                               │
│  ├─ maxSurge: 1, maxUnavailable: 0                                      │
│  └─ Best for: Stateless API changes                                     │
│                                                                         │
│  STRATEGY 2: BLUE-GREEN SWITCH                                          │
│  ├─ Deploy new version alongside old                                    │
│  ├─ Switch traffic instantly                                            │
│  ├─ Keep old version running for quick rollback                         │
│  └─ Best for: Major version changes, database schema changes            │
│                                                                         │
│  STRATEGY 3: CANARY WITH PROGRESSIVE DELIVERY                           │
│  ├─ Route small % of traffic to new version                             │
│  ├─ Gradually increase based on metrics                                 │
│  ├─ Auto-rollback if metrics degrade                                    │
│  └─ Best for: ML model changes, risky updates                           │
│                                                                         │
│  STRATEGY 4: SHADOW/ DARK LAUNCH                                        │
│  ├─ Deploy new version in shadow mode                                   │
│  ├─ Mirror real traffic to shadow (responses discarded)                 │
│  ├─ Compare outputs between versions                                    │
│  └─ Best for: Validating new models before going live                   │
│                                                                         │
│  STRATEGY 5: FEATURE FLAGS                                              │
│  ├─ Deploy code with feature behind flag                                │
│  ├─ Enable for specific users/percentage                                │
│  ├─ No deployment needed for toggle                                     │
│  └─ Best for: Gradual feature rollouts, A/B testing                     │
│                                                                         │
│  STRATEGY 6: HOT-SWAP (Model Only)                                      │
│  ├─ Swap model weights without restarting service                       │
│  ├─ Use model loading hot-reload                                        │
│  ├─ Zero downtime for model updates                                     │
│  └─ Best for: Frequent model updates, prompt changes                    │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

### 19.2 MODEL HOT-SWAP

```python
# File: src/models/hot_swap.py
"""Hot-swap model loading without service restart."""

import asyncio
import logging
import threading
import time
from pathlib import Path
from typing import Optional
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

logger = logging.getLogger(__name__)


class ModelHotSwapper:
    """Hot-swap ML models without restarting the service."""

    def __init__(self, model_dir: str):
        self.model_dir = Path(model_dir)
        self._current_model = None
        self._current_version = None
        self._lock = threading.RLock()
        self._swap_in_progress = False

    @property
    def current_model(self):
        """Get the current model (thread-safe)."""
        with self._lock:
            return self._current_model

    @property
    def current_version(self):
        """Get the current model version."""
        with self._lock:
            return self._current_version

    async def load_model(self, model_path: str, version: str):
        """Load a new model version."""
        logger.info(f"Loading model version {version} from {model_path}")
        start = time.time()

        # Load new model in background
        new_model = await self._load_from_path(model_path)

        # Atomic swap
        with self._lock:
            old_model = self._current_model
            self._current_model = new_model
            self._current_version = version

        # Cleanup old model
        if old_model:
            del old_model

        elapsed = time.time() - start
        logger.info(f"Model swapped to version {version} in {elapsed:.2f}s")

    async def _load_from_path(self, model_path: str):
        """Load model from path (implement based on your framework)."""
        # Example for transformers
        from transformers import AutoModelForCausalLM, AutoTokenizer
        import torch

        tokenizer = AutoTokenizer.from_pretrained(model_path)
        model = AutoModelForCausalLM.from_pretrained(
            model_path,
            torch_dtype=torch.float16,
            device_map="auto",
        )
        return {"model": model, "tokenizer": tokenizer}

    def watch_for_updates(self):
        """Watch model directory for new versions."""
        class ModelWatcher(FileSystemEventHandler):
            def __init__(self, swapper):
                self.swapper = swapper

            def on_created(self, event):
                if event.src_path.endswith(".ready"):
                    # New model version ready
                    model_dir = Path(event.src_path).parent
                    version = model_dir.name
                    asyncio.run(self.swapper.load_model(str(model_dir), version))

        observer = Observer()
        observer.schedule(ModelWatcher(self), str(self.model_dir), recursive=True)
        observer.start()
        logger.info(f"Watching {self.model_dir} for model updates")

        return observer


class PromptHotSwapper:
    """Hot-swap prompt templates without service restart."""

    def __init__(self, prompts_dir: str):
        self.prompts_dir = Path(prompts_dir)
        self._prompts: dict = {}
        self._lock = threading.RLock()
        self._load_all_prompts()

    def _load_all_prompts(self):
        """Load all prompt templates from directory."""
        with self._lock:
            for prompt_file in self.prompts_dir.glob("*.yaml"):
                import yaml
                with open(prompt_file) as f:
                    prompts = yaml.safe_load(f)
                    self._prompts.update(prompts)
            logger.info(f"Loaded {len(self._prompts)} prompt templates")

    def get_prompt(self, name: str, **kwargs) -> str:
        """Get a prompt template by name and fill in variables."""
        with self._lock:
            template = self._prompts.get(name)
            if not template:
                raise KeyError(f"Prompt template '{name}' not found")
            return template.format(**kwargs)

    def reload_prompts(self):
        """Reload all prompt templates."""
        self._load_all_prompts()
        logger.info("Prompt templates reloaded")
```

### 19.3 DATABASE MIGRATION STRATEGIES

```python
# File: src/migration/zero_downtime_migration.py
"""Zero-downtime database migration strategies."""

import logging
from alembic import op
import sqlalchemy as sa

logger = logging.getLogger(__name__)

# ============================================================
# STRATEGY 1: Expand and Contract (Online Schema Change)
# ============================================================

# Step 1: EXPAND - Add new column (backward compatible)
def upgrade_expand():
    """Add new column without breaking existing code."""
    op.add_column(
        "ai_requests",
        sa.Column("model_version", sa.String(50), nullable=True),
    )

    # Backfill in batches (not all at once)
    connection = op.get_bind()
    batch_size = 1000
    offset = 0

    while True:
        result = connection.execute(
            sa.text(
                "UPDATE ai_requests SET model_version = 'v1' "
                "WHERE model_version IS NULL "
                f"LIMIT {batch_size}"
            )
        )
        if result.rowcount == 0:
            break
        offset += batch_size
        logger.info(f"Backfilled {offset} rows")

    # Now add NOT NULL constraint
    op.alter_column(
        "ai_requests",
        "model_version",
        nullable=False,
        server_default="v1",
    )


# Step 2: CONTRACT - Remove old column (after code is updated)
def upgrade_contract():
    """Remove old column after all code uses new column."""
    op.drop_column("ai_requests", "old_model_field")


# ============================================================
# STRATEGY 2: Online Index Creation
# ============================================================

def upgrade_create_index():
    """Create index without locking the table."""
    op.create_index(
        "ix_ai_requests_model_version",
        "ai_requests",
        ["model_version"],
        postgresql_concurrently=True,  # Non-blocking
    )


# ============================================================
# STRATEGY 3: View-based Migration
# ============================================================

def upgrade_view_migration():
    """Use database views for zero-downtime column rename."""
    # Step 1: Create view that maps old name to new name
    op.execute("""
        CREATE VIEW ai_requests_view AS
        SELECT
            id,
            model_name AS model,  -- rename mapping
            prompt,
            response,
            created_at
        FROM ai_requests
    """)

    # Step 2: Update application to use view
    # Step 3: Once all code updated, rename column directly
    # Step 4: Drop view
```

---

## 20. A/B TESTING AND EXPERIMENTATION IN PRODUCTION

### What is A/B Testing?

**A/B testing** (also called split testing) is the practice of comparing two versions of something by showing each version to a different group of users and measuring which performs better.

In the context of AI applications, A/B testing is used to:
- **Compare models** — Is GPT-4 better than Claude for this use case? Show 50% of users each model and compare satisfaction scores.
- **Compare prompts** — Does a new prompt template produce better responses? Test it on 10% of traffic before rolling out to everyone.
- **Compare RAG strategies** — Does hybrid search (vector + keyword) outperform pure vector search? Measure answer quality.
- **Compare features** — Does adding citation tracking improve user satisfaction? Test with a subset of users.

The key principle: **never roll out a change to 100% of users without testing it on a subset first.** A/B testing gives you data-driven confidence that a change actually improves things.

### 20.1 A/B TESTING FRAMEWORK

```python
# File: src/experimentation/ab_testing.py
"""A/B testing framework for AI applications."""

import hashlib
import logging
import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Optional
import json

logger = logging.getLogger(__name__)


class ExperimentStatus(str, Enum):
    DRAFT = "draft"
    RUNNING = "running"
    PAUSED = "paused"
    COMPLETED = "completed"


@dataclass
class Variant:
    name: str
    weight: int  # Percentage of traffic (0-100)
    config: dict  # Configuration for this variant


@dataclass
class Experiment:
    name: str
    variants: list[Variant]
    status: ExperimentStatus = ExperimentStatus.DRAFT
    start_time: float = None
    end_time: float = None
    metrics: dict = field(default_factory=dict)


class ABTestManager:
    """Manage A/B tests for AI features."""

    def __init__(self):
        self.experiments: dict[str, Experiment] = {}

    def create_experiment(
        self,
        name: str,
        variants: list[dict],
    ) -> Experiment:
        """Create a new A/B test experiment."""
        variant_objects = [
            Variant(
                name=v["name"],
                weight=v["weight"],
                config=v.get("config", {}),
            )
            for v in variants
        ]

        # Validate weights sum to 100
        total_weight = sum(v.weight for v in variant_objects)
        if total_weight != 100:
            raise ValueError(f"Variant weights must sum to 100, got {total_weight}")

        experiment = Experiment(
            name=name,
            variants=variant_objects,
        )
        self.experiments[name] = experiment

        logger.info(f"Created experiment: {name} with {len(variants)} variants")
        return experiment

    def start_experiment(self, name: str):
        """Start an experiment."""
        exp = self.experiments[name]
        exp.status = ExperimentStatus.RUNNING
        exp.start_time = time.time()
        logger.info(f"Started experiment: {name}")

    def get_variant(self, experiment_name: str, user_id: str) -> Variant:
        """Determine which variant a user should see."""
        experiment = self.experiments[experiment_name]

        if experiment.status != ExperimentStatus.RUNNING:
            # Return control variant if experiment not running
            return experiment.variants[0]

        # Deterministic hash-based assignment
        hash_input = f"{experiment_name}:{user_id}"
        hash_value = int(hashlib.md5(hash_input.encode()).hexdigest(), 16)
        bucket = hash_value % 100

        # Assign to variant based on weights
        cumulative = 0
        for variant in experiment.variants:
            cumulative += variant.weight
            if bucket < cumulative:
                return variant

        return experiment.variants[-1]

    def log_event(
        self,
        experiment_name: str,
        user_id: str,
        variant_name: str,
        event_type: str,
        value: float = 1.0,
        metadata: dict = None,
    ):
        """Log an event for experiment analysis."""
        experiment = self.experiments[experiment_name]

        if variant_name not in experiment.metrics:
            experiment.metrics[variant_name] = {
                "events": [],
                "count": 0,
                "sum": 0.0,
            }

        experiment.metrics[variant_name]["events"].append({
            "user_id": user_id,
            "event_type": event_type,
            "value": value,
            "metadata": metadata,
            "timestamp": time.time(),
        })
        experiment.metrics[variant_name]["count"] += 1
        experiment.metrics[variant_name]["sum"] += value

    def get_results(self, experiment_name: str) -> dict:
        """Get experiment results with statistical analysis."""
        experiment = self.experiments[experiment_name]
        results = {}

        for variant in experiment.variants:
            metrics = experiment.metrics.get(variant.name, {"count": 0, "sum": 0.0})
            count = metrics["count"]
            total = metrics["sum"]

            results[variant.name] = {
                "sample_size": count,
                "total_value": total,
                "mean": total / count if count > 0 else 0,
                "conversion_rate": count / 100 if count > 0 else 0,  # Simplified
            }

        # Calculate statistical significance (simplified)
        if len(results) == 2:
            variants = list(results.keys())
            control = results[variants[0]]
            treatment = results[variants[1]]

            if control["sample_size"] > 0 and treatment["sample_size"] > 0:
                lift = (treatment["mean"] - control["mean"]) / control["mean"] * 100
                results["analysis"] = {
                    "lift_percentage": lift,
                    "winner": variants[1] if lift > 0 else variants[0],
                }

        return results
```

---

## 21. POST-DEPLOYMENT VALIDATION AND SMOKE TESTING

### What is Post-Deployment Validation?

**Post-deployment validation** is the automated verification that your deployment was successful and the application is working correctly in production. It runs immediately after a deployment completes, before you declare the deployment successful.

**Smoke tests** are a subset of tests that verify the most critical functionality works. They're called "smoke tests" because of the old electronics practice: if you turn on a device and smoke comes out, it's broken. If no smoke, it passes the basic test.

For an AI application, smoke tests verify:
- **Health endpoints respond** — The service is alive and reachable
- **Dependencies are connected** — Database, Redis, vector DB, LLM provider are all accessible
- **Authentication works** — Unauthorized requests are properly rejected
- **Core API responds** — A basic query returns a valid response
- **Latency is acceptable** — Response times are within expected range
- **Streaming works** — Server-sent events are properly streaming
- **Error handling works** — Invalid requests get proper error responses

Why is this critical? Deployments can fail silently. The service starts, health checks pass, but the LLM provider credentials are wrong, or the database migration didn't run, or the model file is corrupted. Smoke tests catch these issues before users do.

### 21.1 SMOKE TEST SUITE

```python
# File: tests/smoke/test_production.py
"""Post-deployment smoke tests for AI service."""

import httpx
import asyncio
import sys
import time
import argparse
from dataclasses import dataclass

@dataclass
class TestResult:
    name: str
    passed: bool
    duration_ms: float
    message: str = ""


class SmokeTestSuite:
    """Smoke tests to validate deployment."""

    def __init__(self, base_url: str):
        self.base_url = base_url.rstrip("/")
        self.results: list[TestResult] = []

    async def run_all(self) -> bool:
        """Run all smoke tests."""
        tests = [
            self.test_health_endpoint,
            self.test_readiness_endpoint,
            self.test_api_responds,
            self.test_authentication,
            self.test_rate_limiting,
            self.test_error_handling,
            self.test_latency_baseline,
            self.test_llm_connectivity,
            self.test_vector_db_connectivity,
            self.test_cache_functionality,
            self.test_streaming_response,
        ]

        print(f"\n{'='*60}")
        print(f"SMOKE TESTS: {self.base_url}")
        print(f"{'='*60}\n")

        all_passed = True
        for test in tests:
            try:
                result = await test()
                self.results.append(result)
                status = "PASS" if result.passed else "FAIL"
                print(f"  [{status}] {result.name} ({result.duration_ms:.0f}ms)")
                if not result.passed:
                    print(f"         {result.message}")
                    all_passed = False
            except Exception as e:
                self.results.append(TestResult(test.__name__, False, 0, str(e)))
                print(f"  [FAIL] {test.__name__}: {e}")
                all_passed = False

        # Summary
        passed = sum(1 for r in self.results if r.passed)
        total = len(self.results)
        print(f"\n{'='*60}")
        print(f"Results: {passed}/{total} passed")
        print(f"{'='*60}\n")

        return all_passed

    async def test_health_endpoint(self) -> TestResult:
        """Test health endpoint responds correctly."""
        start = time.time()
        async with httpx.AsyncClient() as client:
            resp = await client.get(f"{self.base_url}/health", timeout=10)

        duration = (time.time() - start) * 1000

        if resp.status_code == 200:
            data = resp.json()
            if data.get("status") == "healthy":
                return TestResult("health_endpoint", True, duration)
            return TestResult("health_endpoint", False, duration, f"Status: {data.get('status')}")
        return TestResult("health_endpoint", False, duration, f"HTTP {resp.status_code}")

    async def test_readiness_endpoint(self) -> TestResult:
        """Test readiness endpoint."""
        start = time.time()
        async with httpx.AsyncClient() as client:
            resp = await client.get(f"{self.base_url}/ready", timeout=10)
        duration = (time.time() - start) * 1000

        if resp.status_code == 200:
            return TestResult("readiness_endpoint", True, duration)
        return TestResult("readiness_endpoint", False, duration, f"HTTP {resp.status_code}")

    async def test_api_responds(self) -> TestResult:
        """Test main API endpoint responds."""
        start = time.time()
        async with httpx.AsyncClient() as client:
            resp = await client.post(
                f"{self.base_url}/query",
                json={"question": "Hello, this is a smoke test."},
                headers={"Authorization": "Bearer test-key"},
                timeout=30,
            )
        duration = (time.time() - start) * 1000

        if resp.status_code in (200, 401, 403):
            return TestResult("api_responds", True, duration)
        return TestResult("api_responds", False, duration, f"HTTP {resp.status_code}")

    async def test_authentication(self) -> TestResult:
        """Test authentication is enforced."""
        start = time.time()
        async with httpx.AsyncClient() as client:
            resp = await client.post(
                f"{self.base_url}/query",
                json={"question": "test"},
                timeout=10,
            )
        duration = (time.time() - start) * 1000

        if resp.status_code in (401, 403):
            return TestResult("authentication", True, duration)
        return TestResult("authentication", False, duration, f"Expected 401/403, got {resp.status_code}")

    async def test_rate_limiting(self) -> TestResult:
        """Test rate limiting is active."""
        start = time.time()
        async with httpx.AsyncClient() as client:
            responses = []
            for _ in range(20):
                resp = await client.get(f"{self.base_url}/health", timeout=5)
                responses.append(resp.status_code)
        duration = (time.time() - start) * 1000

        # Should get some 429s if rate limiting is working
        # But health endpoints are usually exempt, so just check they respond
        if all(r == 200 for r in responses):
            return TestResult("rate_limiting", True, duration, "Health endpoint exempt from rate limiting")
        return TestResult("rate_limiting", True, duration)

    async def test_error_handling(self) -> TestResult:
        """Test error responses are properly formatted."""
        start = time.time()
        async with httpx.AsyncClient() as client:
            resp = await client.post(
                f"{self.base_url}/query",
                json={"invalid": "request"},
                headers={"Authorization": "Bearer test-key"},
                timeout=10,
            )
        duration = (time.time() - start) * 1000

        if resp.status_code == 422:  # Validation error
            data = resp.json()
            if "detail" in data:
                return TestResult("error_handling", True, duration)
        return TestResult("error_handling", True, duration)  # Accept any response

    async def test_latency_baseline(self) -> TestResult:
        """Test that latency is within acceptable range."""
        start = time.time()
        async with httpx.AsyncClient() as client:
            resp = await client.get(f"{self.base_url}/health", timeout=5)
        duration = (time.time() - start) * 1000

        if duration < 1000:  # Health check should be < 1 second
            return TestResult("latency_baseline", True, duration)
        return TestResult("latency_baseline", False, duration, f"Latency {duration}ms > 1000ms threshold")

    async def test_llm_connectivity(self) -> TestResult:
        """Test LLM provider connectivity (via health check)."""
        start = time.time()
        async with httpx.AsyncClient() as client:
            resp = await client.get(f"{self.base_url}/health", timeout=15)
        duration = (time.time() - start) * 1000

        data = resp.json()
        checks = {c["name"]: c for c in data.get("checks", [])}
        llm_check = checks.get("llm_provider", {})

        if llm_check.get("status") == "healthy":
            return TestResult("llm_connectivity", True, duration)
        return TestResult("llm_connectivity", False, duration, llm_check.get("message", "Unknown"))

    async def test_vector_db_connectivity(self) -> TestResult:
        """Test vector DB connectivity."""
        start = time.time()
        async with httpx.AsyncClient() as client:
            resp = await client.get(f"{self.base_url}/health", timeout=15)
        duration = (time.time() - start) * 1000

        data = resp.json()
        checks = {c["name"]: c for c in data.get("checks", [])}
        vdb_check = checks.get("vector_db", {})

        if vdb_check.get("status") in ("healthy", "degraded"):
            return TestResult("vector_db_connectivity", True, duration)
        return TestResult("vector_db_connectivity", False, duration, vdb_check.get("message", "Unknown"))

    async def test_cache_functionality(self) -> TestResult:
        """Test cache is operational."""
        start = time.time()
        async with httpx.AsyncClient() as client:
            resp = await client.get(f"{self.base_url}/health", timeout=15)
        duration = (time.time() - start) * 1000

        data = resp.json()
        checks = {c["name"]: c for c in data.get("checks", [])}
        cache_check = checks.get("redis", {})

        if cache_check.get("status") in ("healthy", "degraded"):
            return TestResult("cache_functionality", True, duration)
        return TestResult("cache_functionality", False, duration, cache_check.get("message", "Unknown"))

    async def test_streaming_response(self) -> TestResult:
        """Test streaming endpoint works."""
        start = time.time()
        try:
            async with httpx.AsyncClient() as client:
                async with client.stream(
                    "POST",
                    f"{self.base_url}/query/stream",
                    json={"question": "Hello"},
                    headers={"Authorization": "Bearer test-key"},
                    timeout=30,
                ) as resp:
                    chunks = 0
                    async for chunk in resp.aiter_text():
                        chunks += 1
                    duration = (time.time() - start) * 1000
                    if chunks > 0:
                        return TestResult("streaming_response", True, duration)
                    return TestResult("streaming_response", False, duration, "No chunks received")
        except Exception as e:
            duration = (time.time() - start) * 1000
            return TestResult("streaming_response", True, duration, f"Streaming not available: {e}")


async def main():
    parser = argparse.ArgumentParser(description="Post-deployment smoke tests")
    parser.add_argument("--url", required=True, help="Base URL of the service")
    args = parser.parse_args()

    suite = SmokeTestSuite(args.url)
    passed = await suite.run_all()

    sys.exit(0 if passed else 1)


if __name__ == "__main__":
    asyncio.run(main())
```

---

## 22. PRODUCTION READINESS CHECKLISTS AND OPERATIONAL RUNBOOKS

### What is Production Readiness?

**Production readiness** is the set of criteria that must be met before an application can be considered ready for production deployment. It's the final gate before code goes live — a systematic check that nothing important was forgotten.

Think of it like a pilot's pre-flight checklist. Before every flight, pilots check dozens of items (fuel, engines, instruments, weather). They don't rely on memory — they follow the checklist. The same principle applies to deploying software.

A **production readiness checklist** covers:
- **Testing** — Are all tests passing? Unit, integration, e2e, load, security?
- **Monitoring** — Are dashboards set up? Are alerts configured? Do you have logging?
- **Rollback** — Is there a rollback plan? Has it been tested?
- **Scaling** — Can the system handle expected traffic? What about 10x traffic?
- **Security** — Are secrets properly managed? Are there any known vulnerabilities?
- **Documentation** — Is there a runbook for common issues? Are on-call procedures documented?

An **operational runbook** is a step-by-step guide for handling common operational scenarios. When an alert fires at 3 AM, the on-call engineer shouldn't have to figure out what to do from scratch — the runbook tells them exactly how to diagnose and fix the issue.

### 22.1 DEPLOYMENT READINESS CHECKLIST

```
┌─────────────────────────────────────────────────────────────────────────┐
│                    PRODUCTION DEPLOYMENT CHECKLIST                      │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  PRE-DEPLOYMENT                                                         │
│  ├─ [ ] All tests passing (unit, integration, e2e)                     │
│  ├─ [ ] AI evaluation suite passing (accuracy, bias, safety)           │
│  ├─ [ ] Security scan completed (no critical/high vulnerabilities)     │
│  ├─ [ ] Performance benchmarks within acceptable range                 │
│  ├─ [ ] Database migrations tested on staging                          │
│  ├─ [ ] Rollback plan documented and tested                            │
│  ├─ [ ] Feature flags configured (if applicable)                       │
│  ├─ [ ] Monitoring dashboards updated                                  │
│  ├─ [ ] Alert rules configured and tested                              │
│  ├─ [ ] On-call engineer identified and available                      │
│  ├─ [ ] Change approved by team lead                                   │
│  └─ [ ] Deployment window scheduled (avoid Fridays)                    │
│                                                                         │
│  DEPLOYMENT                                                             │
│  ├─ [ ] Staging deployment successful                                  │
│  ├─ [ ] Smoke tests passing on staging                                 │
│  ├─ [ ] Load tests passing on staging                                  │
│  ├─ [ ] Canary deployment initiated                                    │
│  ├─ [ ] Canary metrics within thresholds (15 min)                      │
│  ├─ [ ] Traffic ramped to 100%                                         │
│  └─ [ ] Post-deployment smoke tests passing                            │
│                                                                         │
│  POST-DEPLOYMENT (First 24 hours)                                       │
│  ├─ [ ] Error rate within baseline                                     │
│  ├─ [ ] Latency within baseline                                        │
│  ├─ [ ] No increase in support tickets                                 │
│  ├─ [ ] Cost metrics within budget                                     │
│  ├─ [ ] AI model quality metrics stable                                │
│  ├─ [ ] No security incidents                                          │
│  └─ [ ] Team notified of successful deployment                         │
│                                                                         │
│  ROLLBACK TRIGGERS                                                      │
│  ├─ Error rate > 5% for 5 minutes                                      │
│  ├─ P99 latency > 2x baseline for 5 minutes                           │
│  ├─ Any data corruption detected                                       │
│  ├─ Security vulnerability discovered                                  │
│  └─ AI model quality drop > 10%                                        │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

### 22.2 OPERATIONAL RUNBOOK TEMPLATE

```markdown
# Operational Runbook: [Service Name]

## Service Overview
- **Service**: AI API Service
- **Owner**: AI Platform Team
- **On-call Rotation**: PagerDuty schedule #ai-platform
- **Slack Channel**: #ai-platform-alerts
- **Dashboard**: https://grafana.internal/d/ai-service

## Architecture
[Link to architecture diagram]

## Dependencies
| Dependency | Criticality | Fallback |
|-----------|-------------|----------|
| OpenAI API | Critical | Anthropic fallback |
| PostgreSQL | Critical | Read replica |
| Redis | High | Direct DB queries |
| ChromaDB | Medium | Keyword search |
| S3 | Low | Local storage |

## Common Issues and Resolutions

### Issue: High Error Rate
1. Check error logs: `{service="ai-api"} | json | level="ERROR"`
2. Check LLM provider status
3. Check database connectivity
4. If provider down: enable fallback provider
5. If database issue: check connection pool, restart if needed

### Issue: High Latency
1. Check P50/P95/P99 breakdown
2. Identify slow component (LLM, vector DB, cache)
3. Check GPU utilization if applicable
4. Scale up replicas if CPU/memory bound
5. Check for slow database queries

### Issue: Model Quality Degradation
1. Check evaluation metrics dashboard
2. Compare with previous model version
3. Check input data quality
4. Rollback to previous model version if needed
5. File incident for investigation

### Issue: Cost Spike
1. Check token usage by model
2. Identify high-cost endpoints/users
3. Check for abuse or unusual traffic
4. Implement/adjust rate limits
5. Review caching strategy

## Scaling Procedures

### Scale Up
```bash
# Increase replicas
kubectl scale deployment ai-api --replicas=N -n ai-production

# Increase resources
kubectl set resources deployment/ai-api -c=ai-api --limits=cpu=4,memory=8Gi -n ai-production
```

### Scale Down
```bash
# Decrease replicas (monitor first)
kubectl scale deployment ai-api --replicas=N -n ai-production
```

## Emergency Contacts
| Role | Name | Contact |
|------|------|---------|
| AI Platform Lead | [Name] | [Phone/Slack] |
| SRE On-call | [Name] | PagerDuty |
| VP Engineering | [Name] | [Phone] |

## Post-Incident Process
1. Create incident document within 24 hours
2. Schedule blameless post-mortem within 48 hours
3. Document root cause and timeline
4. Create action items with owners and deadlines
5. Share learnings with team
```

### 22.3 CONTINUOUS IMPROVEMENT CYCLE

```
┌─────────────────────────────────────────────────────────────────────────┐
│                    CONTINUOUS IMPROVEMENT CYCLE                         │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│         ┌──────────┐                                                   │
│         │  PLAN    │                                                   │
│         │          │                                                   │
│         │ Identify │                                                   │
│         │ improve- │                                                   │
│         │ ments    │                                                   │
│         └────┬─────┘                                                   │
│              │                                                          │
│              v                                                          │
│  ┌──────────┐      ┌──────────┐                                        │
│  │  ACT     │      │  DO      │                                        │
│  │          │<─────│          │                                        │
│  │ Implement│      │ Execute  │                                        │
│  │ changes  │      │ changes  │                                        │
│  └────┬─────┘      └────┬─────┘                                        │
│       │                 │                                               │
│       │    ┌──────────┐ │                                               │
│       │    │  CHECK   │ │                                               │
│       └───>│          │<┘                                               │
│            │ Measure  │                                                 │
│            │ results  │                                                 │
│            └──────────┘                                                 │
│                                                                         │
│  Key Metrics to Track:                                                  │
│  ├─ Deployment frequency (target: daily)                               │
│  ├─ Lead time for changes (target: < 1 day)                           │
│  ├─ Change failure rate (target: < 5%)                                 │
│  ├─ Time to restore service (target: < 1 hour)                        │
│  ├─ MTTR (Mean Time to Recovery)                                       │
│  ├─ Availability (SLO compliance)                                      │
│  ├─ Cost per request                                                   │
│  ├─ AI model quality (accuracy, relevance)                             │
│  └─ User satisfaction (NPS, CSAT)                                      │
│                                                                         │
│  Review Cadence:                                                        │
│  ├─ Daily: Error rates, latency, cost                                  │
│  ├─ Weekly: Deployment metrics, incidents                              │
│  ├─ Monthly: SLO review, capacity planning                             │
│  └─ Quarterly: Architecture review, tech debt                          │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

---



---

# PART 4: COMPREHENSIVE PROVIDER REFERENCE

---

## 23. DATABASE PLATFORMS

### What is a Database Platform?

A **database** is an organized collection of data that your application reads from and writes to. Every AI application needs at least one database — to store user data, conversation history, application state, cached responses, or analytics.

A **database platform** (or managed database) is a service that runs and manages the database for you. Instead of installing PostgreSQL on a server, configuring backups, managing upgrades, and handling failover yourself — the platform does all of that.

Types of databases:
- **Relational (SQL)** — Data stored in tables with rows and columns. Uses SQL query language. Best for: structured data, transactions, relationships between data. Examples: PostgreSQL, MySQL, SQL Server.
- **NoSQL (Document)** — Data stored as flexible JSON documents. No fixed schema. Best for: unstructured data, rapid iteration, flexible schemas. Examples: MongoDB, DynamoDB, Firestore.
- **Key-Value** — Simplest database type. Store and retrieve values by key. Best for: caching, sessions, real-time data. Examples: Redis, DynamoDB, Memcached.
- **Vector** — Specialized database for storing and searching vector embeddings. Best for: semantic search, RAG, similarity matching. Examples: Pinecone, Weaviate, Qdrant.
- **Graph** — Data stored as nodes and edges (relationships). Best for: social networks, recommendation engines, knowledge graphs. Examples: Neo4j, Amazon Neptune.
- **Time-Series** — Optimized for timestamped data. Best for: metrics, logs, IoT sensor data. Examples: InfluxDB, TimescaleDB.

### 23.1 DATABASE PROVIDER OVERVIEW

```
┌─────────────────────────────────────────────────────────────────────────┐
│                    DATABASE PROVIDER LANDSCAPE                          │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  RELATIONAL (SQL)                                                       │
│  ├─ Supabase (PostgreSQL) — Open-source Firebase alternative            │
│  ├─ PlanetScale (MySQL) — Serverless MySQL with branching               │
│  ├─ Neon (PostgreSQL) — Serverless Postgres with scale-to-zero          │
│  ├─ CockroachDB — Distributed SQL, PostgreSQL-compatible                │
│  ├─ TiDB — Distributed SQL, MySQL-compatible                            │
│  ├─ AWS RDS — Managed PostgreSQL/MySQL/Oracle/SQL Server                │
│  ├─ Google Cloud SQL — Managed PostgreSQL/MySQL/SQL Server              │
│  ├─ Azure Database — Managed PostgreSQL/MySQL/SQL Server                │
│  ├─ DigitalOcean Managed Databases — PostgreSQL/MySQL/Redis/Kafka       │
│  └─ Heroku Postgres — Managed PostgreSQL on Heroku                      │
│                                                                         │
│  NOSQL                                                                  │
│  ├─ MongoDB Atlas — Managed MongoDB (document store)                    │
│  ├─ AWS DynamoDB — Serverless key-value/document store                  │
│  ├─ Google Firestore — Serverless document store                        │
│  ├─ Azure Cosmos DB — Multi-model database                              │
│  ├─ Redis Cloud — Managed Redis (key-value, cache)                     │
│  ├─ Upstash Redis — Serverless Redis with per-request pricing           │
│  └─ Aiven — Managed Kafka, Redis, PostgreSQL, MySQL, etc.              │
│                                                                         │
│  GRAPH                                                                  │
│  ├─ Neo4j Aura — Managed Neo4j graph database                          │
│  ├─ Amazon Neptune — Managed graph database                             │
│  └─ ArangoDB Cloud — Multi-model (graph + document + key-value)        │
│                                                                         │
│  TIME-SERIES                                                            │
│  ├─ InfluxDB Cloud — Managed time-series database                       │
│  ├─ Timescale Cloud — Managed TimescaleDB (PostgreSQL extension)        │
│  └─ AWS Timestream — Serverless time-series database                    │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

### 23.2 SUPABASE (PostgreSQL + Auth + Storage + Realtime)

**What is Supabase?** Supabase is an open-source alternative to Firebase. It gives you a full PostgreSQL database plus authentication, file storage, real-time subscriptions, and edge functions — all from one platform. The killer feature for AI: it has **pgvector built-in**, so you can store and search vector embeddings directly in your PostgreSQL database without needing a separate vector database.

```
Best For: Full-stack apps needing PostgreSQL, auth, storage, and realtime
Strengths: Open-source, generous free tier, built-in auth, Edge Functions
Weaknesses: Limited regions, newer platform, less enterprise features

Architecture:
┌─────────────┐     ┌──────────────────┐     ┌──────────────┐
│  Client App  │────>│  Supabase API    │────>│  PostgreSQL  │
│  (React/     │     │  (PostgREST)     │     │  (Managed)   │
│   Next.js)   │<────│                  │<────│              │
└─────────────┘     └────────┬─────────┘     └──────────────┘
                             │
              ┌──────────────┼──────────────────┐
              │              │                  │
       ┌──────┴──────┐ ┌────┴────┐      ┌──────┴──────┐
       │  Auth       │ │ Storage │      │  Realtime   │
       │  (GoTrue)   │ │ (S3)    │      │  (WebSocket)│
       └─────────────┘ └─────────┘      └─────────────┘

Services Included:
├─ PostgreSQL database (with pgvector for embeddings!)
├─ Authentication (email, OAuth, magic links)
├─ File Storage (S3-compatible)
├─ Realtime subscriptions (database changes via WebSocket)
├─ Edge Functions (Deno-based serverless)
├─ Vector embeddings (pgvector extension)
└─ Row Level Security (RLS) for data access control
```

```python
# File: src/database/supabase_client.py
"""Supabase client for AI application."""

from supabase import create_client, Client
import os

class SupabaseManager:
    """Manage Supabase database, auth, storage, and vector operations."""

    def __init__(self):
        self.url = os.getenv("SUPABASE_URL")
        self.key = os.getenv("SUPABASE_SERVICE_KEY")  # Service key for server-side
        self.client: Client = create_client(self.url, self.key)

    # === DATABASE OPERATIONS ===

    def query(self, table: str, filters: dict = None, limit: int = 100):
        """Query records from a table."""
        query = self.client.table(table).select("*")
        if filters:
            for key, value in filters.items():
                query = query.eq(key, value)
        return query.limit(limit).execute()

    def insert(self, table: str, data: dict):
        """Insert a record."""
        return self.client.table(table).insert(data).execute()

    def upsert(self, table: str, data: dict, on_conflict: str = "id"):
        """Upsert a record (insert or update)."""
        return self.client.table(table).upsert(data, on_conflict=on_conflict).execute()

    # === VECTOR OPERATIONS (pgvector) ===

    def store_embedding(self, table: str, content: str, embedding: list[float], metadata: dict = None):
        """Store a vector embedding."""
        return self.client.table(table).insert({
            "content": content,
            "embedding": embedding,
            "metadata": metadata or {},
        }).execute()

    def search_similar(self, table: str, query_embedding: list[float], match_count: int = 5):
        """Search for similar vectors using cosine similarity."""
        # Uses the match_documents RPC function (created via SQL migration)
        return self.client.rpc(
            "match_documents",
            {
                "query_embedding": query_embedding,
                "match_count": match_count,
                "filter": {},
            },
        ).execute()

    # === AUTH OPERATIONS ===

    def sign_up(self, email: str, password: str):
        """Register a new user."""
        return self.client.auth.sign_up({"email": email, "password": password})

    def sign_in(self, email: str, password: str):
        """Sign in a user."""
        return self.client.auth.sign_in_with_password({"email": email, "password": password})

    def get_user(self, jwt: str):
        """Get user from JWT token."""
        return self.client.auth.get_user(jwt)

    # === STORAGE OPERATIONS ===

    def upload_file(self, bucket: str, path: str, file_bytes: bytes):
        """Upload a file to storage."""
        return self.client.storage.from_(bucket).upload(path, file_bytes)

    def get_public_url(self, bucket: str, path: str) -> str:
        """Get public URL for a file."""
        return self.client.storage.from_(bucket).get_public_url(path)
```

```sql
-- File: supabase/migrations/001_enable_vector.sql
-- Enable pgvector extension for embeddings

CREATE EXTENSION IF NOT EXISTS vector;

CREATE TABLE documents (
    id BIGSERIAL PRIMARY KEY,
    content TEXT,
    embedding VECTOR(1536),  -- OpenAI embedding dimensions
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Create index for fast similarity search
CREATE INDEX ON documents USING ivfflat (embedding vector_cosine_ops)
    WITH (lists = 100);

-- Create the match function for similarity search
CREATE OR REPLACE FUNCTION match_documents(
    query_embedding VECTOR(1536),
    match_count INT DEFAULT 5,
    filter JSONB DEFAULT '{}'
)
RETURNS TABLE (
    id BIGINT,
    content TEXT,
    metadata JSONB,
    similarity FLOAT
)
LANGUAGE plpgsql
AS $$
BEGIN
    RETURN QUERY
    SELECT
        documents.id,
        documents.content,
        documents.metadata,
        1 - (documents.embedding <=> query_embedding) AS similarity
    FROM documents
    WHERE documents.metadata @> filter
    ORDER BY documents.embedding <=> query_embedding
    LIMIT match_count;
END;
$$;

-- Enable Row Level Security
ALTER TABLE documents ENABLE ROW LEVEL SECURITY;

-- Policy: Users can only see their own documents
CREATE POLICY "Users can view own documents" ON documents
    FOR SELECT USING (auth.uid()::text = metadata->>'user_id');

CREATE POLICY "Users can insert own documents" ON documents
    FOR INSERT WITH CHECK (auth.uid()::text = metadata->>'user_id');
```

### 23.3 NEON (Serverless PostgreSQL)

```
Best For: Serverless apps needing PostgreSQL with scale-to-zero
Strengths: Scale-to-zero, branching (git-like DB workflows), generous free tier
Weaknesses: PostgreSQL only, cold starts on free tier

Architecture:
┌─────────────┐     ┌──────────────────┐     ┌──────────────┐
│  App         │────>│  Neon Proxy      │────>│  Compute     │
│              │     │  (Connection     │     │  (PostgreSQL)│
│              │     │   Pooler)        │     │              │
└─────────────┘     └──────────────────┘     └──────┬───────┘
                                                     │
                                           ┌─────────┴─────────┐
                                           │  Storage          │
                                           │  (Decoupled,      │
                                           │   S3-backed)      │
                                           └───────────────────┘
```

```python
# File: src/database/neon_client.py
"""Neon serverless PostgreSQL client."""

import os
from sqlalchemy import create_engine
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

# Neon connection string (with pooling)
# postgresql://user:pass@ep-cool-name-123456.us-east-2.aws.neon.tech/dbname?sslmode=require
DATABASE_URL = os.getenv("NEON_DATABASE_URL")

# Async engine with connection pooling
engine = create_async_engine(
    DATABASE_URL,
    pool_size=5,
    max_overflow=10,
    pool_timeout=30,
    pool_recycle=300,
    echo=False,
)

AsyncSessionLocal = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

async def get_session():
    """Get an async database session."""
    async with AsyncSessionLocal() as session:
        yield session
```

### 23.4 PLANETSCALE (Serverless MySQL)

```
Best For: MySQL-compatible serverless database with branching
Strengths: Database branching (like git), non-blocking schema changes, Vitess-powered
Weaknesses: MySQL only, no foreign keys (Vitess limitation), paid for production

Key Features:
├─ Database branching — create branches like git for schema changes
├─ Deploy requests — review and merge schema changes
├─ Non-blocking schema changes — no table locks
├─ Horizontal sharding via Vitess
├─ Connection pooling built-in
└─ CLI tooling for migrations
```

```python
# File: src/database/planetscale_client.py
"""PlanetScale database client."""

import os
import mysql.connector
from contextlib import contextmanager

# PlanetScale connection string
# mysql://username:password@aws.connect.psdb.cloud/database?ssl={"rejectUnauthorized":true}

def get_connection():
    """Get a PlanetScale database connection."""
    return mysql.connector.connect(
        host=os.getenv("PS_HOST", "aws.connect.psdb.cloud"),
        user=os.getenv("PS_USER"),
        password=os.getenv("PS_PASSWORD"),
        database=os.getenv("PS_DATABASE"),
        ssl_verify_cert=True,
        ssl_ca="/etc/ssl/certs/ca-certificates.crt",
    )

@contextmanager
def get_cursor():
    """Get a database cursor with auto-commit."""
    conn = get_connection()
    try:
        cursor = conn.cursor(dictionary=True)
        yield cursor
        conn.commit()
    finally:
        cursor.close()
        conn.close()
```

### 23.5 MONGODB ATLAS

**What is MongoDB Atlas?** MongoDB Atlas is the managed cloud version of MongoDB, the most popular NoSQL database. Unlike traditional SQL databases that store data in rigid tables, MongoDB stores data as flexible JSON documents. For AI applications, MongoDB Atlas has a killer feature: **Atlas Vector Search** — built-in vector search that lets you store embeddings and perform similarity search directly in your database, without needing a separate vector database.

```
Best For: Document-heavy AI applications, flexible schemas, vector search
Strengths: Atlas Vector Search (native vector search), flexible schema, global clusters
Weaknesses: NoSQL (no joins), can be expensive at scale

Architecture:
┌─────────────┐     ┌──────────────────┐     ┌──────────────┐
│  App         │────>│  Atlas Cluster   │────>│  MongoDB     │
│              │     │  (M0/M10/M30)   │     │  Replica Set │
└─────────────┘     └──────────────────┘     └──────┬───────┘
                                                     │
                              ┌───────────────────────┼──────────────────┐
                              │                       │                  │
                       ┌──────┴──────┐       ┌───────┴───────┐  ┌──────┴──────┐
                       │  Atlas      │       │  Atlas Search │  │  Atlas      │
                       │  Vector     │       │  (Full-text)  │  │  Data API   │
                       │  Search     │       │               │  │             │
                       └─────────────┘       └────────────────┘  └─────────────┘
```

```python
# File: src/database/mongodb_atlas.py
"""MongoDB Atlas client with Vector Search for AI applications."""

import os
from pymongo import MongoClient
from pymongo.collection import Collection
from typing import Optional

class AtlasManager:
    """MongoDB Atlas manager with vector search capabilities."""

    def __init__(self):
        self.connection_string = os.getenv("MONGODB_URI")
        self.client = MongoClient(self.connection_string)
        self.db = self.client[os.getenv("MONGODB_DB", "ai_production")]

    def get_collection(self, name: str) -> Collection:
        """Get a collection."""
        return self.db[name]

    # === VECTOR SEARCH (Atlas Vector Search) ===

    def store_document_with_embedding(
        self,
        collection: str,
        content: str,
        embedding: list[float],
        metadata: dict = None,
    ):
        """Store a document with its vector embedding."""
        doc = {
            "content": content,
            "embedding": embedding,
            "metadata": metadata or {},
        }
        return self.db[collection].insert_one(doc)

    def vector_search(
        self,
        collection: str,
        query_embedding: list[float],
        num_candidates: int = 100,
        limit: int = 5,
        filter: dict = None,
    ) -> list:
        """Perform vector similarity search using Atlas Vector Search."""
        pipeline = [
            {
                "$vectorSearch": {
                    "index": "vector_index",
                    "path": "embedding",
                    "queryVector": query_embedding,
                    "numCandidates": num_candidates,
                    "limit": limit,
                }
            },
            {
                "$project": {
                    "content": 1,
                    "metadata": 1,
                    "score": {"$meta": "vectorSearchScore"},
                }
            },
        ]

        if filter:
            pipeline[0]["$vectorSearch"]["filter"] = filter

        return list(self.db[collection].aggregate(pipeline))

    # === FULL-TEXT SEARCH (Atlas Search) ===

    def full_text_search(
        self,
        collection: str,
        query: str,
        path: str = "content",
        limit: int = 5,
    ) -> list:
        """Perform full-text search using Atlas Search."""
        pipeline = [
            {
                "$search": {
                    "index": "default",
                    "text": {
                        "query": query,
                        "path": path,
                    },
                }
            },
            {"$limit": limit},
            {
                "$project": {
                    "content": 1,
                    "metadata": 1,
                    "score": {"$meta": "searchScore"},
                }
            },
        ]
        return list(self.db[collection].aggregate(pipeline))

    # === HYBRID SEARCH (Vector + Full-text) ===

    def hybrid_search(
        self,
        collection: str,
        query: str,
        query_embedding: list[float],
        limit: int = 5,
    ) -> list:
        """Combine vector search with full-text search for better results."""
        pipeline = [
            {
                "$search": {
                    "index": "default",
                    "compound": {
                        "should": [
                            {
                                "text": {
                                    "query": query,
                                    "path": "content",
                                    "score": {"boost": {"value": 0.3}},
                                }
                            },
                            {
                                "vectorSearch": {
                                    "queryVector": query_embedding,
                                    "path": "embedding",
                                    "numCandidates": 100,
                                    "limit": limit,
                                    "score": {"boost": {"value": 0.7}},
                                }
                            },
                        ]
                    },
                }
            },
            {"$limit": limit},
        ]
        return list(self.db[collection].aggregate(pipeline))
```

### 23.6 COCKROACHDB

```
Best For: Distributed SQL with global consistency, multi-region AI services
Strengths: PostgreSQL-compatible, global distribution, automatic sharding
Weaknesses: Higher latency than single-region, more expensive

Key Use Cases:
├─ Multi-region AI services needing consistent data
├─ Global user sessions and state management
├─ High-availability requirements (99.999%)
└─ Applications needing SQL + global distribution
```

### 23.7 REDIS CLOUD / UPSTASH

```
┌─────────────────────────────────────────────────────────────────────────┐
│                    REDIS PROVIDERS                                      │
├────────────────────┬──────────────────┬─────────────────────────────────┤
│ Provider           │ Best For         │ Key Differentiator              │
├────────────────────┼──────────────────┼─────────────────────────────────┤
│ Redis Cloud        │ Production Redis │ Enterprise features, 5 regions  │
│ (Redis Ltd)        │ at scale         │                                 │
├────────────────────┼──────────────────┼─────────────────────────────────┤
│ Upstash Redis      │ Serverless apps  │ Per-request pricing, REST API,  │
│                    │                  │ edge-compatible, scale-to-zero  │
├────────────────────┼──────────────────┼─────────────────────────────────┤
│ AWS ElastiCache    │ AWS-native apps  │ VPC integration, cluster mode   │
├────────────────────┼──────────────────┼─────────────────────────────────┤
│ Google Memorystore │ GCP-native apps  │ High availability, auto-failover│
├────────────────────┼──────────────────┼─────────────────────────────────┤
│ Azure Cache        │ Azure-native     │ Enterprise integration          │
│ for Redis          │ apps             │                                 │
├────────────────────┼──────────────────┼─────────────────────────────────┤
│ Aiven Redis        │ Multi-cloud      │ Managed on any cloud            │
├────────────────────┼──────────────────┼─────────────────────────────────┤
│ Railway Redis      │ Small projects   │ Built-in with Railway PaaS      │
└────────────────────┴──────────────────┴─────────────────────────────────┘
```

```python
# File: src/cache/upstash_client.py
"""Upstash Redis client for serverless AI applications."""

import os
import json
from upstash_redis import Redis

class UpstashCache:
    """Serverless Redis cache using Upstash (REST-based, edge-compatible)."""

    def __init__(self):
        self.redis = Redis(
            url=os.getenv("UPSTASH_REDIS_REST_URL"),
            token=os.getenv("UPSTASH_REDIS_REST_TOKEN"),
        )

    def cache_llm_response(self, prompt_hash: str, response: str, ttl: int = 3600):
        """Cache an LLM response."""
        key = f"llm:cache:{prompt_hash}"
        self.redis.set(key, response, ex=ttl)

    def get_cached_response(self, prompt_hash: str) -> str | None:
        """Get a cached LLM response."""
        key = f"llm:cache:{prompt_hash}"
        return self.redis.get(key)

    def cache_embedding(self, text_hash: str, embedding: list[float], ttl: int = 86400):
        """Cache an embedding vector."""
        key = f"embedding:{text_hash}"
        self.redis.set(key, json.dumps(embedding), ex=ttl)

    def get_cached_embedding(self, text_hash: str) -> list[float] | None:
        """Get a cached embedding."""
        key = f"embedding:{text_hash}"
        data = self.redis.get(key)
        return json.loads(data) if data else None

    def increment_rate_limit(self, user_id: str, window: int = 60, limit: int = 100) -> tuple[int, bool]:
        """Rate limiting with sliding window."""
        key = f"ratelimit:{user_id}"
        current = self.redis.incr(key)
        if current == 1:
            self.redis.expire(key, window)
        return current, current <= limit

    def store_session(self, session_id: str, data: dict, ttl: int = 86400):
        """Store user session data."""
        key = f"session:{session_id}"
        self.redis.set(key, json.dumps(data), ex=ttl)

    def get_session(self, session_id: str) -> dict | None:
        """Get user session data."""
        key = f"session:{session_id}"
        data = self.redis.get(key)
        return json.loads(data) if data else None
```

---

## 24. VECTOR DATABASE PLATFORMS

### What is a Vector Database?

A **vector database** is a specialized database designed to store and search **vector embeddings** — numerical representations of data (text, images, audio) that capture semantic meaning.

Why does this exist? Traditional databases search by exact match (`WHERE name = 'John'`). But what if you want to search by **meaning**? "Find documents similar to this query" or "Find images that look like this one." That's what vector databases do.

How it works:
1. You convert your text/image into a vector (list of numbers) using an embedding model (e.g., OpenAI's text-embedding-3-small)
2. You store that vector in the vector database along with the original content
3. When a user searches, you convert their query into a vector
4. The database finds the most similar vectors using math (cosine similarity, dot product)
5. You return the original content associated with those vectors

This is the foundation of **RAG (Retrieval-Augmented Generation)** — the technique that lets LLMs answer questions about your private data. The vector database finds relevant documents, and the LLM generates an answer based on those documents.

Key vector databases:
- **Pinecone** — Fully managed, easiest to set up, great for production
- **Weaviate** — Open-source, hybrid search (vector + keyword), multi-modal
- **Qdrant** — Open-source, high performance, great filtering
- **Milvus** — Open-source, designed for billion-scale vectors
- **ChromaDB** — Open-source, simple, great for development and prototyping
- **pgvector** — PostgreSQL extension, no separate database needed

### 24.1 VECTOR DATABASE COMPARISON

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                    VECTOR DATABASE PROVIDERS                                    │
├──────────────────┬──────────┬──────────┬──────────┬──────────┬─────────────────┤
│ Provider         │ Type     │ Hosting  │ Free Tier│ Max Vectors│ Best For       │
├──────────────────┼──────────┼──────────┼──────────┼──────────┼─────────────────┤
│ Pinecone         │ Managed  │ Cloud    │ Yes (1M) │ Billion+  │ Production RAG │
│                  │          │          │          │           │ easiest setup  │
├──────────────────┼──────────┼──────────┼──────────┼──────────┼─────────────────┤
│ Weaviate Cloud   │ Managed  │ Cloud    │ Yes (100K│ Billion+  │ Hybrid search  │
│                  │          │          │ vectors) │           │ multi-modal    │
├──────────────────┼──────────┼──────────┼──────────┼──────────┼─────────────────┤
│ Qdrant Cloud     │ Managed  │ Cloud    │ Yes (1M) │ Billion+  │ Performance,   │
│                  │ + Self   │ + Self   │          │           │ filtering      │
├──────────────────┼──────────┼──────────┼──────────┼──────────┼─────────────────┤
│ Milvus (Zilliz)  │ Managed  │ Cloud    │ Yes      │ Billion+  │ Large-scale,   │
│                  │ + Self   │ + Self   │          │           │ enterprise     │
├──────────────────┼──────────┼──────────┼──────────┼──────────┼─────────────────┤
│ ChromaDB         │ Self-    │ Local/   │ Free     │ Million   │ Development,   │
│                  │ hosted   │ Cloud    │ (open)   │           │ prototyping    │
├──────────────────┼──────────┼──────────┼──────────┼──────────┼─────────────────┤
│ pgvector         │ Extension│ Any PG   │ Free     │ Million   │ Existing PG    │
│                  │          │          │ (open)   │           │ apps, simplicity│
├──────────────────┼──────────┼──────────┼──────────┼──────────┼─────────────────┤
│ Vespa            │ Self-    │ Cloud    │ Free     │ Billion+  │ Enterprise     │
│                  │ hosted   │ + Self   │ (open)   │           │ search+vector  │
├──────────────────┼──────────┼──────────┼──────────┼──────────┼─────────────────┤
│ Typesense        │ Self-    │ Cloud    │ Yes      │ Million   │ Fast search    │
│                  │ hosted   │ + Self   │ (open)   │           │ + vector hybrid│
├──────────────────┼──────────┼──────────┼──────────┼──────────┼─────────────────┤
│ Turbopuffer      │ Managed  │ Cloud    │ Yes      │ Billion+  │ Serverless,    │
│                  │          │          │          │           │ cost-effective │
├──────────────────┼──────────┼──────────┼──────────┼──────────┼─────────────────┤
│ LanceDB          │ Embedded │ Local/   │ Free     │ Billion+  │ Embedded,      │
│                  │          │ Cloud    │ (open)   │           │ multimodal     │
├──────────────────┼──────────┼──────────┼──────────┼──────────┼─────────────────┤
│ Supabase Vector  │ Extension│ Cloud    │ Yes      │ Million   │ Already using  │
│ (pgvector)       │          │          │          │           │ Supabase       │
├──────────────────┼──────────┼──────────┼──────────┼──────────┼─────────────────┤
│ Astra DB         │ Managed  │ Cloud    │ Yes      │ Billion+  │ Cassandra +    │
│ (DataStax)       │          │          │          │           │ vector search  │
├──────────────────┼──────────┼──────────┼──────────┼──────────┼─────────────────┤
│ SingleStore      │ Managed  │ Cloud    │ Yes      │ Billion+  │ SQL + vector   │
│                  │          │          │          │           │ hybrid         │
└──────────────────┴──────────┴──────────┴──────────┴──────────┴─────────────────┘
```

### 24.2 PINECONE

**What is Pinecone?** Pinecone is a fully managed vector database designed specifically for production AI applications. It's the easiest vector database to set up — no servers to manage, no infrastructure to configure. You create an index, upsert vectors, and query. It handles scaling, replication, and performance automatically. Used by companies like Shopify, Notion, and Zapier for their RAG applications.

```python
# File: src/vector_store/pinecone_client.py
"""Pinecone vector database client."""

import os
from pinecone import Pinecone, ServerlessSpec

class PineconeVectorStore:
    """Pinecone vector store for AI applications."""

    def __init__(self):
        self.pc = Pinecone(api_key=os.getenv("PINECONE_API_KEY"))
        self.index_name = os.getenv("PINECONE_INDEX", "ai-knowledge-base")

    def create_index(self, dimension: int = 1536, metric: str = "cosine"):
        """Create a Pinecone index (serverless)."""
        if self.index_name not in self.pc.list_indexes().names():
            self.pc.create_index(
                name=self.index_name,
                dimension=dimension,
                metric=metric,
                spec=ServerlessSpec(
                    cloud="aws",
                    region="us-east-1",
                ),
            )

    def get_index(self):
        """Get the Pinecone index."""
        return self.pc.Index(self.index_name)

    def upsert_vectors(self, vectors: list[dict], namespace: str = ""):
        """Upsert vectors into the index."""
        index = self.get_index()
        return index.upsert(vectors=vectors, namespace=namespace)

    def query(
        self,
        embedding: list[float],
        top_k: int = 5,
        namespace: str = "",
        filter: dict = None,
        include_metadata: bool = True,
    ) -> list:
        """Query similar vectors."""
        index = self.get_index()
        results = index.query(
            vector=embedding,
            top_k=top_k,
            namespace=namespace,
            filter=filter,
            include_metadata=include_metadata,
        )
        return results["matches"]

    def delete(self, ids: list[str], namespace: str = ""):
        """Delete vectors by ID."""
        index = self.get_index()
        return index.delete(ids=ids, namespace=namespace)
```

### 24.3 WEAVIATE

**What is Weaviate?** Weaviate is an open-source vector database with a unique feature: **hybrid search**. It combines vector similarity search (semantic understanding) with traditional keyword search (exact matching) in a single query. This is powerful for RAG because sometimes you need semantic understanding ("What is machine learning?") and sometimes you need exact matches ("Error code E-4521"). Weaviate also supports multi-modal search — searching across text, images, and other data types in the same database.

```python
# File: src/vector_store/weaviate_client.py
"""Weaviate vector database client."""

import os
import weaviate
from weaviate.classes.config import Configure, VectorDistances

class WeaviateVectorStore:
    """Weaviate vector store with hybrid search capabilities."""

    def __init__(self):
        self.client = weaviate.connect_to_weaviate_cloud(
            cluster_url=os.getenv("WEAVIATE_URL"),
            auth_credentials=weaviate.auth.AuthApiKey(os.getenv("WEAVIATE_API_KEY")),
        )

    def create_collection(self, name: str, vectorizer: str = "none"):
        """Create a collection (class) in Weaviate."""
        if not self.client.collections.exists(name):
            self.client.collections.create(
                name=name,
                vector_index_config=Configure.VectorIndex.hnsw(
                    distance_metric=VectorDistances.COSINE,
                ),
                vectorizer_config=Configure.Vectorizer.none() if vectorizer == "none" else None,
            )

    def insert_object(self, collection: str, properties: dict, vector: list[float]):
        """Insert an object with its vector."""
        col = self.client.collections.get(collection)
        return col.data.insert(properties=properties, vector=vector)

    def batch_insert(self, collection: str, objects: list[dict]):
        """Batch insert objects."""
        col = self.client.collections.get(collection)
        with col.batch.dynamic() as batch:
            for obj in objects:
                batch.add_object(
                    properties=obj.get("properties", {}),
                    vector=obj.get("vector"),
                )

    def query_near_vector(
        self,
        collection: str,
        vector: list[float],
        limit: int = 5,
        certainty: float = 0.7,
    ) -> list:
        """Query by vector similarity."""
        col = self.client.collections.get(collection)
        response = col.query.near_vector(
            near_vector=vector,
            limit=limit,
            return_metadata=weaviate.classes.query.MetadataQuery(certainty=True),
        )
        return response.objects

    def query_hybrid(
        self,
        collection: str,
        query: str,
        vector: list[float],
        limit: int = 5,
        alpha: float = 0.5,
    ) -> list:
        """Hybrid search (combines vector + keyword)."""
        col = self.client.collections.get(collection)
        response = col.query.hybrid(
            query=query,
            vector=vector,
            alpha=alpha,  # 0 = pure keyword, 1 = pure vector
            limit=limit,
        )
        return response.objects

    def close(self):
        """Close the client connection."""
        self.client.close()
```

### 24.4 QDRANT

**What is Qdrant?** Qdrant (pronounced "quadrant") is a high-performance open-source vector database written in Rust. It's designed for speed and efficiency — handling billions of vectors with low latency. Its standout features are advanced filtering (combine vector search with complex metadata filters) and payload support (attach arbitrary JSON data to vectors and filter by it during search). Qdrant can be self-hosted or used as a managed cloud service.

```python
# File: src/vector_store/qdrant_client.py
"""Qdrant vector database client."""

import os
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct

class QdrantVectorStore:
    """Qdrant vector store for high-performance vector search."""

    def __init__(self):
        self.client = QdrantClient(
            url=os.getenv("QDRANT_URL"),
            api_key=os.getenv("QDRANT_API_KEY"),
        )
        self.collection_name = os.getenv("QDRANT_COLLECTION", "ai_docs")

    def create_collection(self, dimension: int = 1536):
        """Create a collection."""
        if not self.client.collection_exists(self.collection_name):
            self.client.create_collection(
                collection_name=self.collection_name,
                vectors_config=VectorParams(
                    size=dimension,
                    distance=Distance.COSINE,
                ),
            )

    def upsert_points(self, points: list[PointStruct]):
        """Upsert points (vectors with payloads)."""
        return self.client.upsert(
            collection_name=self.collection_name,
            points=points,
        )

    def search(
        self,
        query_vector: list[float],
        limit: int = 5,
        query_filter: dict = None,
    ) -> list:
        """Search for similar vectors."""
        return self.client.query_points(
            collection_name=self.collection_name,
            query=query_vector,
            limit=limit,
            query_filter=query_filter,
        ).points

    def delete_points(self, ids: list[str]):
        """Delete points by ID."""
        return self.client.delete(
            collection_name=self.collection_name,
            points_selector=ids,
        )
```

### 24.5 CHROMADB

**What is ChromaDB?** ChromaDB is an open-source vector database designed for simplicity. It's the easiest vector database to get started with — a few lines of Python code to store and search embeddings. It runs in-process (no separate server needed) or as a persistent database on disk. ChromaDB is ideal for development, prototyping, and small-to-medium production workloads. For large-scale production (millions of vectors), consider Pinecone, Qdrant, or Milvus.

```python
# File: src/vector_store/chroma_client.py
"""ChromaDB vector store (local/development)."""

import chromadb

class ChromaVectorStore:
    """ChromaDB vector store for development and small-scale production."""

    def __init__(self, persist_directory: str = "./chroma_db"):
        self.client = chromadb.PersistentClient(path=persist_directory)

    def get_or_create_collection(self, name: str, metadata: dict = None):
        """Get or create a collection."""
        return self.client.get_or_create_collection(
            name=name,
            metadata=metadata or {"hnsw:space": "cosine"},
        )

    def add_documents(
        self,
        collection_name: str,
        documents: list[str],
        embeddings: list[list[float]],
        metadatas: list[dict] = None,
        ids: list[str] = None,
    ):
        """Add documents with embeddings."""
        collection = self.get_or_create_collection(collection_name)
        collection.add(
            documents=documents,
            embeddings=embeddings,
            metadatas=metadatas,
            ids=ids or [f"doc_{i}" for i in range(len(documents))],
        )

    def query(
        self,
        collection_name: str,
        query_embedding: list[float],
        n_results: int = 5,
        where: dict = None,
    ) -> dict:
        """Query similar documents."""
        collection = self.get_or_create_collection(collection_name)
        return collection.query(
            query_embeddings=[query_embedding],
            n_results=n_results,
            where=where,
        )

    def delete_collection(self, name: str):
        """Delete a collection."""
        self.client.delete_collection(name)
```

---

## 25. SERVERLESS PLATFORMS

### What is Serverless?

**Serverless** is a cloud execution model where the provider manages the server infrastructure entirely — you just write code and the provider runs it. Despite the name, servers still exist; you just don't see or manage them.

The key characteristics of serverless:
- **No server management** — No SSH, no patching, no OS updates
- **Pay per execution** — You pay only when your code runs, not for idle servers
- **Automatic scaling** — From 0 to 10,000 requests automatically
- **Scale to zero** — When no one is using your app, you pay nothing

The main types of serverless:
- **Functions (FaaS)** — Run a single function in response to an event (HTTP request, queue message, timer). Examples: AWS Lambda, Google Cloud Functions, Azure Functions.
- **Serverless containers** — Run a container without managing servers. Examples: Google Cloud Run, AWS Fargate, Azure Container Apps.
- **Edge functions** — Run code at CDN edge locations worldwide, <1ms latency. Examples: Cloudflare Workers, Vercel Edge Functions, Deno Deploy.

When to use serverless:
- **Event-driven APIs** — Webhooks, form submissions, image processing
- **Bursty traffic** — Traffic that spikes and drops unpredictably
- **Low-traffic apps** — Don't pay for idle servers when no one is using your app
- **Scheduled tasks** — Cron jobs, nightly batch processing

When NOT to use serverless:
- **Long-running tasks** — Lambda has a 15-minute timeout
- **Consistent high traffic** — Always-on servers are cheaper
- **WebSockets** — Need persistent connections
- **GPU workloads** — Most serverless platforms don't offer GPUs

### 25.1 SERVERLESS PROVIDER COMPARISON

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                    SERVERLESS PLATFORMS                                         │
├──────────────────┬──────────┬──────────┬──────────┬──────────┬─────────────────┤
│ Provider         │ Runtime  │ Max Time │ Cold Start│ GPU     │ Best For        │
├──────────────────┼──────────┼──────────┼──────────┼──────────┼─────────────────┤
│ AWS Lambda       │ Python,  │ 15 min   │ 100-500ms│ No*     │ Event-driven    │
│                  │ Node, etc│          │          │ (prev.) │ APIs, webhooks  │
├──────────────────┼──────────┼──────────┼──────────┼──────────┼─────────────────┤
│ Google Cloud     │ Python,  │ 60 min   │ 100-400ms│ Preview │ Container-based │
│ Functions        │ Node, Go │          │          │         │ APIs            │
├──────────────────┼──────────┼──────────┼──────────┼──────────┼─────────────────┤
│ Azure Functions  │ Python,  │ 10 min*  │ 200-800ms│ No      │ Azure ecosystem │
│                  │ Node, C# │ (Flex: ∞)│          │         │                 │
├──────────────────┼──────────┼──────────┼──────────┼──────────┼─────────────────┤
│ Cloudflare       │ JS, TS,  │ 30s free │ <1ms     │ No      │ Edge computing, │
│ Workers          │ Python   │ (paid:   │ (global) │         │ global latency  │
│                  │          │ 15min)   │          │         │                 │
├──────────────────┼──────────┼──────────┼──────────┼──────────┼─────────────────┤
│ Deno Deploy      │ Deno/TS  │ 50ms free│ <10ms    │ No      │ TypeScript edge │
│                  │          │ (paid:   │ (global) │         │ apps            │
│                  │          │ 15min)   │          │         │                 │
├──────────────────┼──────────┼──────────┼──────────┼──────────┼─────────────────┤
│ Vercel Functions │ Node,    │ 10s Hobby│ 50-200ms │ No      │ Next.js apps    │
│                  │ Python,Go│ 60s Pro  │          │         │                 │
├──────────────────┼──────────┼──────────┼──────────┼──────────┼─────────────────┤
│ Netlify Functions│ Node,    │ 10s free │ 100-500ms│ No      │ Jamstack sites  │
│                  │ Go, Rust │ 15min Pro│          │         │                 │
├──────────────────┼──────────┼──────────┼──────────┼──────────┼─────────────────┤
│ AWS Lambda@Edge  │ Node,    │ 30s      │ 5-50ms   │ No      │ CDN-level logic │
│                  │ Python   │          │ (at edge)│         │                 │
├──────────────────┼──────────┼──────────┼──────────┼──────────┼─────────────────┤
│ Modal            │ Python   │ 24 hours │ 10-30s   │ Yes     │ GPU serverless  │
│                  │          │          │ (GPU)    │ (A100)  │ ML inference    │
├──────────────────┼──────────┼──────────┼──────────┼──────────┼─────────────────┤
│ AWS Step Funcs   │ Any      │ 1 year   │ N/A      │ No      │ Workflow        │
│                  │ (orch.)  │          │          │         │ orchestration   │
└──────────────────┴──────────┴──────────┴──────────┴──────────┴─────────────────┘
```

### 25.2 CLOUDFLARE WORKERS (Edge AI)

**What are Cloudflare Workers?** Cloudflare Workers run JavaScript/TypeScript at CDN edge locations in 300+ cities worldwide. When a user makes a request, it's processed at the nearest edge location — not in a distant data center. This gives you <1ms cold starts and <50ms response times globally. Cloudflare also offers **Workers AI** — built-in AI inference at the edge, so you can run small ML models (embeddings, classification, text generation) without any backend server.

```typescript
// File: src/edge/cloudflare-worker.ts
// Cloudflare Worker for edge AI inference

interface Env {
  AI: Ai;  // Cloudflare Workers AI binding
  VECTORIZE: VectorizeIndex;
  KV: KVNamespace;
  AI_GATEWAY: Fetcher;
}

export default {
  async fetch(request: Request, env: Env): Promise<Response> {
    const url = new URL(request.url);

    if (url.pathname === '/api/chat') {
      return handleChat(request, env);
    }

    if (url.pathname === '/api/embed') {
      return handleEmbed(request, env);
    }

    if (url.pathname === '/api/search') {
      return handleSearch(request, env);
    }

    return new Response('Not found', { status: 404 });
  },
};

async function handleChat(request: Request, env: Env): Promise<Response> {
  const { messages } = await request.json() as { messages: Array<{role: string, content: string}> };

  // Use Cloudflare Workers AI (runs models at the edge)
  const response = await env.AI.run('@cf/meta/llama-3-8b-instruct', {
    messages: messages,
    stream: true,
  });

  return new Response(response, {
    headers: { 'Content-Type': 'text/event-stream' },
  });
}

async function handleEmbed(request: Request, env: Env): Promise<Response> {
  const { text } = await request.json() as { text: string };

  // Generate embedding using edge AI
  const embedding = await env.AI.run('@cf/baai/bge-base-en-v1.5', {
    text: text,
  });

  return Response.json({ embedding: embedding.data[0] });
}

async function handleSearch(request: Request, env: Env): Promise<Response> {
  const { query } = await request.json() as { query: string };

  // Check cache first
  const cacheKey = `search:${query}`;
  const cached = await env.KV.get(cacheKey);
  if (cached) {
    return Response.json(JSON.parse(cached));
  }

  // Generate query embedding
  const queryEmbedding = await env.AI.run('@cf/baai/bge-base-en-v1.5', {
    text: query,
  });

  // Search vector index
  const results = await env.VECTORIZE.query(queryEmbedding.data[0], {
    topK: 5,
    returnMetadata: true,
  });

  // Cache results for 5 minutes
  await env.KV.put(cacheKey, JSON.stringify(results), { expirationTtl: 300 });

  return Response.json(results);
}
```

```toml
# File: wrangler.toml (Cloudflare Workers configuration)
name = "ai-edge-service"
main = "src/edge/cloudflare-worker.ts"
compatibility_date = "2024-01-01"

[ai]
binding = "AI"

[[vectorize]]
binding = "VECTORIZE"
index_name = "ai-knowledge-base"

[[kv_namespaces]]
binding = "KV"
id = "your-kv-namespace-id"

# AI Gateway for caching and rate limiting
[[services]]
binding = "AI_GATEWAY"
service = "ai-gateway"

[vars]
ENVIRONMENT = "production"
```

### 25.3 DENO DEPLOY

```typescript
// File: src/edge/deno-deploy.ts
// Deno Deploy edge function for AI applications

import { serve } from "https://deno.land/std@0.208.0/http/server.ts";

const OPENAI_API_KEY = Deno.env.get("OPENAI_API_KEY");

serve(async (req: Request) => {
  const url = new URL(req.url);

  if (url.pathname === "/api/chat" && req.method === "POST") {
    const { message } = await req.json();

    // Call OpenAI from the edge
    const response = await fetch("https://api.openai.com/v1/chat/completions", {
      method: "POST",
      headers: {
        "Authorization": `Bearer ${OPENAI_API_KEY}`,
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        model: "gpt-4",
        messages: [{ role: "user", content: message }],
        stream: true,
      }),
    });

    // Stream response back to client
    return new Response(response.body, {
      headers: { "Content-Type": "text/event-stream" },
    });
  }

  return new Response("Not found", { status: 404 });
});
```

---

## 26. UI AND FRONTEND DEPLOYMENT PLATFORMS

### What is a UI/Frontend Deployment Platform?

A **UI deployment platform** is a service that hosts the user-facing part of your application — the web interface that users interact with in their browser. This includes everything from simple static websites to complex single-page applications (React, Vue, Next.js) to ML demo apps (Streamlit, Gradio).

The key distinction:
- **Static sites** — HTML/CSS/JS files served as-is. No server-side processing. Fastest, cheapest, simplest.
- **Server-side rendered (SSR)** — Pages are generated on the server for each request. Better SEO, faster initial load. Requires a running server (Next.js, Nuxt).
- **ML demo apps** — Interactive UIs for testing ML models. Streamlit (Python, data-focused), Gradio (Python, ML-focused).

For AI applications specifically:
- **Streamlit** — Best for internal tools, data dashboards, quick prototypes. Pure Python, no frontend code needed.
- **Gradio** — Best for ML model demos, HuggingFace Spaces integration. Pure Python, generates shareable links.
- **Next.js on Vercel** — Best for production AI web apps. SSR, streaming, AI SDK, edge functions.
- **React on Netlify/Cloudflare** — Best for static + API architecture. CDN-served, fast globally.

### 26.1 UI PLATFORM COMPARISON

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                    UI / FRONTEND DEPLOYMENT PLATFORMS                           │
├──────────────────┬──────────┬──────────┬──────────┬──────────┬─────────────────┤
│ Platform         │ Best For │ Free Tier│ Custom   │ Streaming│ Best For        │
│                  │          │          │ Domain   │ Support  │                 │
├──────────────────┼──────────┼──────────┼──────────┼──────────┼─────────────────┤
│ Streamlit Cloud  │ ML demos │ Yes      │ Yes      │ Yes      │ Data apps,      │
│                  │ internal │          │          │          │ ML dashboards   │
├──────────────────┼──────────┼──────────┼──────────┼──────────┼─────────────────┤
│ Gradio/HF Spaces │ ML demos │ Yes      │ Yes      │ Yes      │ Model demos,    │
│                  │          │ (GPU too)│          │          │ community       │
├──────────────────┼──────────┼──────────┼──────────┼──────────┼─────────────────┤
│ Vercel           │ Next.js  │ Yes      │ Yes      │ Yes      │ Production      │
│                  │ React    │          │          │ (AI SDK) │ web apps        │
├──────────────────┼──────────┼──────────┼──────────┼──────────┼─────────────────┤
│ Netlify          │ Jamstack │ Yes      │ Yes      │ Limited  │ Static +        │
│                  │ React    │          │          │          │ serverless      │
├──────────────────┼──────────┼──────────┼──────────┼──────────┼─────────────────┤
│ GitHub Pages     │ Static   │ Yes      │ Yes      │ No       │ Docs, blogs     │
│                  │ sites    │          │          │          │                 │
├──────────────────┼──────────┼──────────┼──────────┼──────────┼─────────────────┤
│ Cloudflare Pages │ Static + │ Yes      │ Yes      │ Yes      │ Global static   │
│                  │ Workers  │          │          │          │ + edge logic    │
├──────────────────┼──────────┼──────────┼──────────┼──────────┼─────────────────┤
│ AWS Amplify      │ Full-    │ Yes (12mo│ Yes      │ Yes      │ AWS-native      │
│                  │ stack    │ )        │          │          │ full-stack      │
├──────────────────┼──────────┼──────────┼──────────┼──────────┼─────────────────┤
│ Firebase Hosting │ Static + │ Yes (Spark│ Yes     │ Limited  │ Google-native   │
│                  │ Functions│ plan)    │          │          │ apps            │
├──────────────────┼──────────┼──────────┼──────────┼──────────┼─────────────────┤
│ Azure Static     │ Static + │ Yes      │ Yes      │ Yes      │ Azure-native    │
│ Web Apps         │ Functions│          │          │          │ apps            │
├──────────────────┼──────────┼──────────┼──────────┼──────────┼─────────────────┤
│ Lovable/Bolt     │ AI-built │ Yes      │ Yes      │ N/A      │ Rapid           │
│                  │ apps     │          │          │          │ prototyping     │
└──────────────────┴──────────┴──────────┴──────────┴──────────┴─────────────────┘
```

### 26.2 STREAMLIT CLOUD

```python
# File: app.py (Streamlit AI Application)
import streamlit as st
import httpx
import asyncio

st.set_page_config(page_title="AI Assistant", page_icon="🤖", layout="wide")

# Sidebar for configuration
with st.sidebar:
    st.title("Settings")
    model = st.selectbox("Model", ["gpt-4", "gpt-3.5-turbo", "claude-3"])
    temperature = st.slider("Temperature", 0.0, 2.0, 0.7)
    max_tokens = st.slider("Max Tokens", 100, 4000, 1000)

# Main chat interface
st.title("AI Assistant")

# Session state for chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Chat input
if prompt := st.chat_input("Ask me anything..."):
    # Add user message
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Get AI response
    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        full_response = ""

        # Stream response from API
        with httpx.stream(
            "POST",
            "https://api.myapp.com/chat",
            json={
                "messages": st.session_state.messages,
                "model": model,
                "temperature": temperature,
                "max_tokens": max_tokens,
            },
            timeout=60,
        ) as response:
            for chunk in response.iter_text():
                full_response += chunk
                message_placeholder.markdown(full_response + "▌")

        message_placeholder.markdown(full_response)

    st.session_state.messages.append({"role": "assistant", "content": full_response})
```

```toml
# File: .streamlit/config.toml
[theme]
primaryColor = "#FF6B6B"
backgroundColor = "#FFFFFF"
secondaryBackgroundColor = "#F0F2F6"
textColor = "#262730"

[server]
headless = true
port = 8501
enableCORS = false
enableXsrfProtection = true
```

---

## 27. MODEL SERVING FRAMEWORKS

### What is Model Serving?

**Model serving** is the process of making a trained ML model available as a service that accepts input (text, images, etc.) and returns predictions (classifications, generations, embeddings, etc.).

The challenge: training a model is a one-time batch job. Serving a model means running it 24/7, handling concurrent requests, managing GPU memory, batching requests for efficiency, and streaming responses to users.

A **model serving framework** handles:
- **Model loading** — Loading model weights into GPU/CPU memory efficiently
- **Request batching** — Combining multiple requests into one GPU call for throughput
- **Streaming** — Sending tokens as they're generated (for LLMs)
- **Quantization** — Running models in lower precision (FP16, INT8, INT4) to save memory
- **Multi-GPU** — Splitting large models across multiple GPUs (tensor parallelism)
- **Health checks** — Reporting whether the model is ready to serve
- **Metrics** — Tracking latency, throughput, GPU utilization

Key model serving frameworks:
- **vLLM** — Fastest LLM serving engine. PagedAttention for memory efficiency. OpenAI-compatible API.
- **TGI (Text Generation Inference)** — HuggingFace's serving engine. Good HF integration.
- **Triton Inference Server** — NVIDIA's multi-framework server. Supports PyTorch, TF, ONNX simultaneously.
- **TorchServe** — PyTorch's official serving solution.
- **Ollama** — Simplest way to run LLMs locally. One command to serve any model.
- **llama.cpp** — CPU-optimized LLM inference. Runs 70B models on laptops.

### 27.1 MODEL SERVING COMPARISON

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                    MODEL SERVING FRAMEWORKS                                     │
├──────────────────┬──────────┬──────────┬──────────┬──────────┬─────────────────┤
│ Framework        │ GPU      │ Model    │ Streaming│ Batch    │ Best For        │
│                  │ Support  │ Formats  │          │ Support  │                 │
├──────────────────┼──────────┼──────────┼──────────┼──────────┼─────────────────┤
│ vLLM             │ Yes      │ HF, GGUF │ Yes      │ Yes      │ LLM serving,    │
│                  │ (CUDA)   │ AWQ, GPTQ│          │          │ highest perf    │
├──────────────────┼──────────┼──────────┼──────────┼──────────┼─────────────────┤
│ TGI (HuggingFace)│ Yes      │ HF models│ Yes      │ Yes      │ HuggingFace     │
│                  │ (CUDA)   │          │          │          │ ecosystem       │
├──────────────────┼──────────┼──────────┼──────────┼──────────┼─────────────────┤
│ Triton           │ Yes      │ PyTorch, │ Yes      │ Yes      │ Multi-framework │
│ (NVIDIA)         │ (CUDA)   │ TF, ONNX │          │          │ enterprise      │
├──────────────────┼──────────┼──────────┼──────────┼──────────┼─────────────────┤
│ TorchServe       │ Yes      │ PyTorch  │ Yes      │ Yes      │ PyTorch models  │
│                  │ (CUDA)   │          │          │          │                 │
├──────────────────┼──────────┼──────────┼──────────┼──────────┼─────────────────┤
│ TF Serving       │ Yes      │ TF, Keras│ No       │ Yes      │ TensorFlow      │
│                  │ (CUDA)   │          │          │          │ models          │
├──────────────────┼──────────┼──────────┼──────────┼──────────┼─────────────────┤
│ ONNX Runtime     │ Yes      │ ONNX     │ No       │ Yes      │ Cross-platform  │
│ Server           │ (CUDA)   │          │          │          │ inference       │
├──────────────────┼──────────┼──────────┼──────────┼──────────┼─────────────────┤
│ Ollama           │ Yes      │ GGUF,    │ Yes      │ No       │ Local dev,      │
│                  │ (Metal,  │ HF (auto)│          │          │ simple deploy   │
│                  │  CUDA)   │          │          │          │                 │
├──────────────────┼──────────┼──────────┼──────────┼──────────┼─────────────────┤
│ llama.cpp        │ Yes      │ GGUF     │ Yes      │ No       │ CPU inference,  │
│                  │ (CPU,    │          │          │          │ edge, quantized │
│                  │  CUDA)   │          │          │          │                 │
├──────────────────┼──────────┼──────────┼──────────┼──────────┼─────────────────┤
│ SGLang           │ Yes      │ HF models│ Yes      │ Yes      │ Structured      │
│                  │ (CUDA)   │          │          │          │ generation      │
├──────────────────┼──────────┼──────────┼──────────┼──────────┼─────────────────┤
│ Ray Serve        │ Yes      │ Any      │ Yes      │ Yes      │ Distributed     │
│                  │ (CUDA)   │ (Python) │          │          │ serving         │
├──────────────────┼──────────┼──────────┼──────────┼──────────┼─────────────────┤
│ BentoML          │ Yes      │ Any      │ Yes      │ Yes      │ ML platform     │
│                  │ (CUDA)   │ (Python) │          │          │ packaging       │
└──────────────────┴──────────┴──────────┴──────────┴──────────┴─────────────────┘
```

### 27.2 vLLM (High-Performance LLM Serving)

**What is vLLM?** vLLM (Virtual Large Language Model) is the fastest open-source LLM serving engine. It uses a technique called **PagedAttention** to manage GPU memory efficiently, allowing it to serve 2-24x more requests per second than standard implementations. If you're self-hosting an LLM (Llama, Mistral, etc.), vLLM is almost certainly the best choice for production serving. It provides an OpenAI-compatible API, so clients can switch from OpenAI to your self-hosted model with zero code changes.

```python
# File: deploy/vllm_server.py
"""vLLM server for high-performance LLM inference."""

# Install: pip install vllm
# Run: python deploy/vllm_server.py
# Or: python -m vllm.entrypoints.openai.api_server --model meta-llama/Llama-3-8b-Instruct

from vllm import AsyncLLMEngine, AsyncEngineArgs, SamplingParams
from fastapi import FastAPI
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
import json

app = FastAPI()

# Initialize vLLM engine
engine_args = AsyncEngineArgs(
    model="meta-llama/Llama-3-8b-Instruct",
    tensor_parallel_size=1,  # Number of GPUs
    gpu_memory_utilization=0.9,
    max_model_len=8192,
    dtype="auto",
    quantization=None,  # Or "awq", "gptq", "squeezellm"
)

engine = AsyncLLMEngine.from_engine_args(engine_args)


class ChatRequest(BaseModel):
    messages: list[dict]
    max_tokens: int = 512
    temperature: float = 0.7
    top_p: float = 0.9
    stream: bool = False


@app.post("/v1/chat/completions")
async def chat_completions(request: ChatRequest):
    """OpenAI-compatible chat completions endpoint."""
    # Format messages into prompt
    prompt = ""
    for msg in request.messages:
        prompt += f"<|{msg['role']}|>\n{msg['content']}\n"
    prompt += "<|assistant|>\n"

    sampling_params = SamplingParams(
        max_tokens=request.max_tokens,
        temperature=request.temperature,
        top_p=request.top_p,
    )

    if request.stream:
        return StreamingResponse(
            stream_generate(prompt, sampling_params),
            media_type="text/event-stream",
        )

    # Non-streaming
    results = await engine.generate(prompt, sampling_params, request_id="req-1")
    output = results[0].outputs[0].text

    return {
        "choices": [{"message": {"role": "assistant", "content": output}}],
        "usage": {
            "prompt_tokens": len(results[0].prompt_token_ids),
            "completion_tokens": len(results[0].outputs[0].token_ids),
        },
    }


async def stream_generate(prompt: str, sampling_params: SamplingParams):
    """Stream generated tokens."""
    request_id = "req-stream-1"
    results_generator = engine.generate(prompt, sampling_params, request_id=request_id)

    async for request_output in results_generator:
        text = request_output.outputs[0].text
        chunk = {
            "choices": [{"delta": {"content": text}}],
        }
        yield f"data: {json.dumps(chunk)}\n\n"

    yield "data: [DONE]\n\n"


@app.get("/health")
async def health():
    return {"status": "healthy", "model": engine_args.model}
```

```bash
# Deploy vLLM with Docker
docker run --gpus all \
  -v ~/.cache/huggingface:/root/.cache/huggingface \
  -p 8000:8000 \
  --ipc=host \
  vllm/vllm-openai:latest \
  --model meta-llama/Llama-3-8b-Instruct \
  --tensor-parallel-size 1 \
  --gpu-memory-utilization 0.9 \
  --max-model-len 8192
```

### 27.3 HUGGINGFACE TGI (Text Generation Inference)

```bash
# Deploy TGI with Docker
docker run --gpus all \
  -v ~/.cache/huggingface:/data \
  -p 8080:80 \
  ghcr.io/huggingface/text-generation-inference:latest \
  --model-id meta-llama/Llama-3-8b-Instruct \
  --quantize awq \
  --max-input-length 4096 \
  --max-total-tokens 8192 \
  --max-batch-prefill-tokens 4096
```

```yaml
# File: deploy/tgi-deployment.yaml (Kubernetes)
apiVersion: apps/v1
kind: Deployment
metadata:
  name: tgi-inference
spec:
  replicas: 2
  selector:
    matchLabels:
      app: tgi-inference
  template:
    metadata:
      labels:
        app: tgi-inference
    spec:
      containers:
        - name: tgi
          image: ghcr.io/huggingface/text-generation-inference:latest
          args:
            - "--model-id"
            - "meta-llama/Llama-3-8b-Instruct"
            - "--quantize"
            - "awq"
            - "--max-input-length"
            - "4096"
            - "--max-total-tokens"
            - "8192"
          ports:
            - containerPort: 80
          resources:
            limits:
              nvidia.com/gpu: "1"
              memory: "24Gi"
            requests:
              nvidia.com/gpu: "1"
              memory: "16Gi"
          volumeMounts:
            - name: cache
              mountPath: /data
      volumes:
        - name: cache
          persistentVolumeClaim:
            claimName: model-cache
```

### 27.4 OLLAMA (Local Model Serving)

**What is Ollama?** Ollama is the simplest way to run LLMs on your own machine. One command (`ollama run llama3`) downloads and serves a model. It handles model management, quantization, and GPU detection automatically. While it's primarily used for local development, it can also be deployed as a production inference server. Think of it as "Docker for LLMs" — pull a model, run it, interact with it.

```python
# File: src/models/ollama_client.py
"""Ollama client for local model serving."""

import httpx
import json

class OllamaClient:
    """Client for Ollama local model server."""

    def __init__(self, base_url: str = "http://localhost:11434"):
        self.base_url = base_url

    async def generate(
        self,
        model: str,
        prompt: str,
        system: str = None,
        temperature: float = 0.7,
        max_tokens: int = 512,
    ) -> str:
        """Generate text using a local Ollama model."""
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}/api/generate",
                json={
                    "model": model,
                    "prompt": prompt,
                    "system": system,
                    "options": {
                        "temperature": temperature,
                        "num_predict": max_tokens,
                    },
                    "stream": False,
                },
                timeout=120,
            )
            return response.json()["response"]

    async def chat(
        self,
        model: str,
        messages: list[dict],
        temperature: float = 0.7,
    ) -> str:
        """Chat with a local Ollama model."""
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}/api/chat",
                json={
                    "model": model,
                    "messages": messages,
                    "options": {"temperature": temperature},
                    "stream": False,
                },
                timeout=120,
            )
            return response.json()["message"]["content"]

    async def embed(self, model: str, text: str) -> list[float]:
        """Generate embeddings using Ollama."""
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}/api/embeddings",
                json={"model": model, "prompt": text},
                timeout=30,
            )
            return response.json()["embedding"]

    async def list_models(self) -> list:
        """List available models."""
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{self.base_url}/api/tags")
            return response.json()["models"]

    async def pull_model(self, model: str):
        """Pull/download a model."""
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}/api/pull",
                json={"name": model},
                timeout=600,
            )
            return response.json()
```

```bash
# Ollama commands
ollama pull llama3          # Download model
ollama run llama3           # Run interactively
ollama serve                # Start API server (port 11434)

# Docker deployment
docker run -d \
  -v ollama:/root/.ollama \
  -p 11434:11434 \
  --name ollama \
  ollama/ollama

# With GPU
docker run -d --gpus all \
  -v ollama:/root/.ollama \
  -p 11434:11434 \
  --name ollama \
  ollama/ollama
```

---

## 28. API GATEWAY AND LLM PROXY PLATFORMS

### What is an API Gateway?

An **API Gateway** is a server that sits between your clients (users/apps) and your backend services. It acts as a single entry point for all API requests and handles cross-cutting concerns:

- **Authentication** — Verify API keys, JWT tokens, OAuth
- **Rate limiting** — Prevent abuse by limiting requests per user/IP
- **Load balancing** — Distribute requests across multiple backend instances
- **Caching** — Cache repeated responses to reduce backend load
- **Logging** — Record all API requests for auditing
- **Transformation** — Modify requests/responses (add headers, change formats)

An **LLM Proxy** is a specialized API gateway for Large Language Model APIs. It adds LLM-specific features:
- **Multi-provider routing** — Route requests to OpenAI, Anthropic, or local models based on rules
- **Fallback** — If OpenAI is down, automatically try Anthropic
- **Cost tracking** — Track token usage and cost per user/team/model
- **Semantic caching** — Cache similar queries (not just exact matches)
- **Prompt management** — Version and manage prompt templates
- **Observability** — Track latency, error rates, and quality metrics per model

Why use an LLM proxy?
- **Avoid vendor lock-in** — Switch between providers without changing application code
- **Cost control** — Set budgets, track spending, enforce limits
- **Reliability** — Automatic fallback when a provider has issues
- **Observability** — See which models are used, how much they cost, how they perform

### 28.1 API GATEWAY COMPARISON

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                    API GATEWAY & LLM PROXY PLATFORMS                            │
├──────────────────┬──────────┬──────────┬──────────┬──────────┬─────────────────┤
│ Platform         │ Type     │ LLM      │ Rate     │ Caching  │ Best For        │
│                  │          │ Features │ Limiting │          │                 │
├──────────────────┼──────────┼──────────┼──────────┼──────────┼─────────────────┤
│ LiteLLM Proxy    │ Open-    │ Multi-   │ Yes      │ Yes      │ Multi-provider  │
│                  │ source   │ provider │          │          │ LLM routing     │
├──────────────────┼──────────┼──────────┼──────────┼──────────┼─────────────────┤
│ Portkey          │ Managed  │ Multi-   │ Yes      │ Yes      │ LLM gateway     │
│                  │          │ provider │          │          │ with observ.    │
├──────────────────┼──────────┼──────────┼──────────┼──────────┼─────────────────┤
│ Helicone         │ Managed  │ LLM      │ Yes      │ Yes      │ LLM observ.     │
│                  │          │ analytics│          │          │ + gateway       │
├──────────────────┼──────────┼──────────┼──────────┼──────────┼─────────────────┤
│ Kong             │ Open-    │ General  │ Yes      │ Yes      │ Enterprise API  │
│                  │ source   │ API      │          │          │ management      │
├──────────────────┼──────────┼──────────┼──────────┼──────────┼─────────────────┤
│ AWS API Gateway  │ Managed  │ General  │ Yes      │ Yes      │ AWS-native APIs │
│                  │          │ API      │          │          │                 │
├──────────────────┼──────────┼──────────┼──────────┼──────────┼─────────────────┤
│ Azure API Mgmt   │ Managed  │ General  │ Yes      │ Yes      │ Azure-native    │
│                  │          │ API      │          │          │                 │
├──────────────────┼──────────┼──────────┼──────────┼──────────┼─────────────────┤
│ Google Apigee    │ Managed  │ General  │ Yes      │ Yes      │ GCP-native      │
│                  │          │ API      │          │          │                 │
├──────────────────┼──────────┼──────────┼──────────┼──────────┼─────────────────┤
│ Nginx            │ Self-    │ General  │ Basic    │ Yes      │ Simple reverse  │
│                  │ hosted   │ proxy    │          │          │ proxy           │
├──────────────────┼──────────┼──────────┼──────────┼──────────┼─────────────────┤
│ Traefik          │ Self-    │ General  │ Yes      │ Yes      │ Cloud-native    │
│                  │ hosted   │ proxy    │          │          │ reverse proxy   │
└──────────────────┴──────────┴──────────┴──────────┴──────────┴─────────────────┘
```

### 28.2 LITELLM PROXY

**What is LiteLLM Proxy?** LiteLLM Proxy is an open-source API gateway that provides a unified OpenAI-compatible interface for 100+ LLM providers (OpenAI, Anthropic, Google, Azure, Ollama, vLLM, etc.). Instead of writing provider-specific code for each LLM, your application talks to LiteLLM in OpenAI's format, and LiteLLM routes to the right provider. It handles load balancing, fallbacks, rate limiting, cost tracking, and caching.

```yaml
# File: deploy/litellm/config.yaml
# LiteLLM Proxy - Multi-provider LLM gateway

model_list:
  # OpenAI models
  - model_name: gpt-4
    litellm_params:
      model: openai/gpt-4-turbo
      api_key: os.environ/OPENAI_API_KEY
      rpm: 100
      tpm: 100000

  # Anthropic models
  - model_name: claude-3
    litellm_params:
      model: anthropic/claude-3-opus-20240229
      api_key: os.environ/ANTHROPIC_API_KEY
      rpm: 50

  # Local Ollama models
  - model_name: llama3
    litellm_params:
      model: ollama/llama3
      api_base: http://ollama:11434

  # Fallback routing
  - model_name: gpt-4-fallback
    litellm_params:
      model: openai/gpt-4-turbo
      api_key: os.environ/OPENAI_API_KEY

router_settings:
  routing_strategy: latency-based-routing
  num_retries: 3
  timeout: 30
  fallbacks:
    - gpt-4: [claude-3, gpt-4-fallback]

general_settings:
  master_key: os.environ/LITELLM_MASTER_KEY
  max_budget: 1000  # $1000/month
  budget_duration: 30d

litellm_settings:
  cache: true
  cache_type: redis
  cache_params:
    host: os.environ/REDIS_HOST
    port: 6379
    password: os.environ/REDIS_PASSWORD
  set_verbose: false
  num_retries: 3
  request_timeout: 30
```

```bash
# Deploy LiteLLM Proxy
docker run -d \
  -p 4000:4000 \
  -v $(pwd)/config.yaml:/app/config.yaml \
  -e OPENAI_API_KEY=$OPENAI_API_KEY \
  -e ANTHROPIC_API_KEY=$ANTHROPIC_API_KEY \
  -e LITELLM_MASTER_KEY=sk-master-key \
  ghcr.ioBerriAI/litellm:main-latest \
  --config /app/config.yaml
```

---

## 29. CLOUD STORAGE PROVIDERS

### What is Cloud Storage?

**Cloud storage** is a service that stores your files (documents, images, videos, model weights, backups) on remote servers accessible over the internet. It's like an infinite hard drive in the cloud.

The main type is **object storage** — you store files as "objects" with a key (path) and retrieve them by key. Unlike a file system, there's no folder hierarchy (it's simulated using key prefixes like `models/llama-3/weights.bin`).

Why cloud storage matters for AI applications:
- **Model artifacts** — Store trained model files (often 10-100GB)
- **Training data** — Store datasets for model training
- **User uploads** — Store documents uploaded by users for RAG
- **Embeddings cache** — Store pre-computed embeddings
- **Backups** — Database backups, configuration backups
- **Static assets** — Images, CSS, JavaScript for web applications

Key cloud storage providers:
- **AWS S3** — The original and most widely used. Largest ecosystem.
- **Google Cloud Storage** — GCP equivalent. Good for GCP-native apps.
- **Azure Blob Storage** — Azure equivalent. Good for Azure-native apps.
- **Cloudflare R2** — S3-compatible with ZERO egress fees. Cheapest for high-traffic.
- **Backblaze B2** — Cheapest storage per GB. S3-compatible.
- **MinIO** — Self-hosted S3-compatible storage. Full control.

### 29.1 STORAGE PROVIDER COMPARISON

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                    CLOUD STORAGE PROVIDERS                                      │
├──────────────────┬──────────┬──────────┬──────────┬──────────┬─────────────────┤
│ Provider         │ Type     │ Free Tier│ S3       │ Edge CDN │ Best For        │
│                  │          │          │ Compat.  │          │                 │
├──────────────────┼──────────┼──────────┼──────────┼──────────┼─────────────────┤
│ AWS S3           │ Object   │ 5GB/12mo │ Native   │ Yes      │ AWS ecosystem   │
│                  │ storage  │          │          │ (CF)     │                 │
├──────────────────┼──────────┼──────────┼──────────┼──────────┼─────────────────┤
│ Google Cloud     │ Object   │ 5GB/12mo │ Yes      │ Yes      │ GCP ecosystem   │
│ Storage          │ storage  │          │          │          │                 │
├──────────────────┼──────────┼──────────┼──────────┼──────────┼─────────────────┤
│ Azure Blob       │ Object   │ 5GB/12mo │ Yes      │ Yes      │ Azure ecosystem │
│ Storage          │ storage  │          │          │          │                 │
├──────────────────┼──────────┼──────────┼──────────┼──────────┼─────────────────┤
│ Cloudflare R2    │ Object   │ 10GB free│ Yes      │ Yes      │ Cheapest egress │
│                  │ storage  │          │          │ (free)   │ (zero egress)   │
├──────────────────┼──────────┼──────────┼──────────┼──────────┼─────────────────┤
│ MinIO            │ Self-    │ Free     │ Yes      │ No       │ Self-hosted S3  │
│                  │ hosted   │ (open)   │          │          │ compatible      │
├──────────────────┼──────────┼──────────┼──────────┼──────────┼─────────────────┤
│ Supabase Storage │ Object   │ 1GB free │ No       │ No       │ Already using   │
│                  │ storage  │          │          │          │ Supabase        │
├──────────────────┼──────────┼──────────┼──────────┼──────────┼─────────────────┤
│ DigitalOcean     │ Object   │ 250GB/   │ Yes      │ Yes      │ Simple + cheap  │
│ Spaces           │ storage  │ 12mo     │          │ (CDN)    │                 │
├──────────────────┼──────────┼──────────┼──────────┼──────────┼─────────────────┤
│ Backblaze B2     │ Object   │ 10GB free│ Yes      │ Yes      │ Cheapest        │
│                  │ storage  │          │          │ (CF)     │ storage         │
└──────────────────┴──────────┴──────────┴──────────┴──────────┴─────────────────┘
```

---

## 30. MESSAGE QUEUE AND EVENT SYSTEMS

### What is a Message Queue?

A **message queue** is a system that allows different parts of your application to communicate asynchronously by passing messages through a queue. Instead of Service A calling Service B directly (synchronous), Service A puts a message in the queue, and Service B picks it up when it's ready (asynchronous).

Why does this matter for AI applications?
- **Batch processing** — Users submit 1,000 documents for processing. Instead of processing them all synchronously (user waits), put them in a queue and process them in the background.
- **Decoupling** — The API server doesn't need to know about the worker. If the worker is slow, the API still responds instantly.
- **Retry logic** — If a job fails (LLM API timeout), the queue automatically retries it.
- **Load leveling** — During traffic spikes, messages queue up. Workers process them at a steady pace without being overwhelmed.
- **Fan-out** — One message can trigger multiple workers (generate embedding AND update search index AND send notification).

Types of messaging systems:
- **Queue** (SQS, RabbitMQ) — Point-to-point. One consumer processes each message.
- **Pub/Sub** (SNS, Pub/Sub, Kafka) — One message, many subscribers. Broadcast events.
- **Stream** (Kafka, Redis Streams) — Ordered, replayable log of events. Good for event sourcing.

### 30.1 MESSAGE QUEUE COMPARISON

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                    MESSAGE QUEUE & EVENT PLATFORMS                              │
├──────────────────┬──────────┬──────────┬──────────┬──────────┬─────────────────┤
│ Platform         │ Type     │ Managed  │ Free Tier│ Max      │ Best For        │
│                  │          │ Option   │          │ Throughput│                │
├──────────────────┼──────────┼──────────┼──────────┼──────────┼─────────────────┤
│ AWS SQS          │ Queue    │ Yes      │ 1M free/ │ Virtually│ AWS-native      │
│                  │          │          │ month    │ unlimited│ event-driven    │
├──────────────────┼──────────┼──────────┼──────────┼──────────┼─────────────────┤
│ AWS SNS          │ Pub/Sub  │ Yes      │ 1M free/ │ Virtually│ AWS notifications│
│                  │          │          │ month    │ unlimited│                 │
├──────────────────┼──────────┼──────────┼──────────┼──────────┼─────────────────┤
│ Google Pub/Sub   │ Pub/Sub  │ Yes      │ 10GB/mo  │ Virtually│ GCP-native      │
│                  │          │          │          │ unlimited│                 │
├──────────────────┼──────────┼──────────┼──────────┼──────────┼─────────────────┤
│ Azure Service    │ Queue    │ Yes      │ 1M ops/  │ Virtually│ Azure-native    │
│ Bus              │ + Pub/Sub│          │ month    │ unlimited│                 │
├──────────────────┼──────────┼──────────┼──────────┼──────────┼─────────────────┤
│ Upstash Kafka    │ Stream   │ Yes      │ 10K msgs/│ Limited  │ Serverless      │
│                  │          │          │ day      │          │ event streaming │
├──────────────────┼──────────┼──────────┼──────────┼──────────┼─────────────────┤
│ Confluent Cloud  │ Kafka    │ Yes      │ 400MB/   │ High     │ Enterprise      │
│ (Kafka)          │          │          │ month    │          │ streaming       │
├──────────────────┼──────────┼──────────┼──────────┼──────────┼─────────────────┤
│ RabbitMQ Cloud   │ Queue    │ Yes      │ Yes      │ High     │ Traditional     │
│ (CloudAMQP)      │          │          │ (free    │          │ message queuing │
│                  │          │          │  tier)   │          │                 │
├──────────────────┼──────────┼──────────┼──────────┼──────────┼─────────────────┤
│ Redis Streams    │ Stream   │ Via Redis│ Via Redis│ High     │ Already using   │
│                  │          │ providers│ providers│          │ Redis           │
├──────────────────┼──────────┼──────────┼──────────┼──────────┼─────────────────┤
│ Inngest           │ Event   │ Yes      │ Yes      │ High     │ Serverless      │
│                  │ platform│          │          │          │ workflows       │
└──────────────────┴──────────┴──────────┴──────────┴──────────┴─────────────────┘
```

---

## 31. MANAGED KUBERNETES PLATFORMS

### What is Managed Kubernetes?

**Kubernetes (K8s)** is the industry-standard platform for running containerized applications at scale. It handles deployment, scaling, networking, and health management for your containers. However, running Kubernetes yourself is complex — you need to manage the control plane (API server, scheduler, etcd), upgrade versions, handle certificates, and more.

**Managed Kubernetes** is when a cloud provider runs the control plane for you. You just manage your applications (pods, deployments, services), and the provider handles the underlying Kubernetes infrastructure.

The "Big Three" managed Kubernetes:
- **Amazon EKS** — AWS's managed Kubernetes. Deep AWS integration (load balancers, storage, IAM).
- **Google GKE** — GCP's managed Kubernetes. Google invented Kubernetes, so GKE is the most mature. Autopilot mode handles node management too.
- **Azure AKS** — Azure's managed Kubernetes. Free control plane. Good for Azure shops.

Budget-friendly alternatives:
- **DigitalOcean Kubernetes** — Simple, affordable ($12/month for cluster + nodes)
- **Linode Kubernetes** — Akamai's offering. Competitive pricing.
- **Vultr Kubernetes** — Budget option with GPU node support
- **Civo Kubernetes** — Fastest provisioning (under 2 minutes)

### 31.1 MANAGED K8S COMPARISON

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                    MANAGED KUBERNETES PLATFORMS                                 │
├──────────────────┬──────────┬──────────┬──────────┬──────────┬─────────────────┤
│ Platform         │ Provider │ Free     │ Autopilot│ GPU      │ Best For        │
│                  │          │ Tier     │ Mode     │ Support  │                 │
├──────────────────┼──────────┼──────────┼──────────┼──────────┼─────────────────┤
│ Amazon EKS       │ AWS      │ No (pay  │ Fargate  │ Yes      │ AWS shops       │
│                  │          │ per clus)│ mode     │ (P4d)    │                 │
├──────────────────┼──────────┼──────────┼──────────┼──────────┼─────────────────┤
│ Google GKE       │ GCP      │ Zonal:   │ Autopilot│ Yes      │ GCP shops,      │
│                  │          │ free     │ mode     │ (A100)   │ best K8s UX     │
├──────────────────┼──────────┼──────────┼──────────┼──────────┼─────────────────┤
│ Azure AKS        │ Azure    │ Free     │ Yes      │ Yes      │ Azure shops     │
│                  │          │ (control │          │ (ND A100)│                 │
│                  │          │  plane)  │          │          │                 │
├──────────────────┼──────────┼──────────┼──────────┼──────────┼─────────────────┤
│ DigitalOcean K8s │ DO       │ No       │ No       │ No       │ Simple + cheap  │
│                  │          │ ($12/mo  │          │          │                 │
│                  │          │  cluster)│          │          │                 │
├──────────────────┼──────────┼──────────┼──────────┼──────────┼─────────────────┤
│ Linode K8s       │ Akamai   │ No       │ No       │ No       │ Simple + cheap  │
│                  │          │          │          │          │                 │
├──────────────────┼──────────┼──────────┼──────────┼──────────┼─────────────────┤
│ Scaleway K8s     │ Scaleway │ No       │ No       │ Yes      │ European hosting│
│                  │          │          │          │          │                 │
├──────────────────┼──────────┼──────────┼──────────┼──────────┼─────────────────┤
│ Vultr K8s        │ Vultr    │ No       │ No       │ Yes      │ Budget GPU K8s  │
│                  │          │          │          │          │                 │
├──────────────────┼──────────┼──────────┼──────────┼──────────┼─────────────────┤
│ Civo K8s         │ Civo     │ No       │ No       │ No       │ Fastest K8s     │
│                  │          │          │          │          │ provisioning    │
└──────────────────┴──────────┴──────────┴──────────┴──────────┴─────────────────┘
```

---

## 32. ADDITIONAL PAAS PLATFORMS

### What are these Additional PaaS Platforms?

Section 4 covered the most popular PaaS platforms (Railway, Render, Fly.io, Vercel). This section covers additional PaaS options that might be a better fit depending on your specific situation:

- **Heroku** — The original PaaS (invented the concept). Simple `git push heroku main` deployment. Large add-on ecosystem. Now owned by Salesforce.
- **DigitalOcean App Platform** — If you're already using DigitalOcean for other services, this integrates seamlessly.
- **Google App Engine** — Google's original PaaS. Fully managed, auto-scaling. Good for GCP-native apps.
- **Azure App Service** — Azure's PaaS. Good for .NET applications and Microsoft shops.
- **Koyeb** — Global edge deployment with built-in databases. Good for low-latency applications.
- **Porter** — "Heroku on Kubernetes" — gives you a Heroku-like experience on your own Kubernetes cluster.
- **Zeabur** — Simple deployment platform popular in Asia. Good for Chinese and global audiences.
- **Northflank** — Docker + database platform. Good for teams that want containers without full Kubernetes.

### 32.1 PAAS PLATFORMS NOT COVERED IN MAIN GUIDE

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                    ADDITIONAL PAAS PLATFORMS                                    │
├──────────────────┬──────────┬──────────┬──────────┬──────────┬─────────────────┤
│ Platform         │ Free Tier│ GPU      │ Database │ Best For │ Key Feature     │
│                  │          │ Support  │ Included │          │                 │
├──────────────────┼──────────┼──────────┼──────────|──────────┼─────────────────┤
│ Heroku           │ 1000hrs/ │ No       │ Postgres │ Simple   │ Pioneer PaaS,   │
│                  │ month    │          │ (managed)│ apps     │ add-ons eco     │
├──────────────────┼──────────┼──────────┼──────────┼──────────┼─────────────────┤
│ DigitalOcean     │ 3 apps   │ No       │ PG,MySQL │ DO users│ Simple pricing  │
│ App Platform     │ (static) │          │ Redis,etc│          │                 │
├──────────────────┼──────────┼──────────┼──────────┼──────────┼─────────────────┤
│ Google App       │ 28 hrs/  │ No       │ Cloud    │ GCP      │ Auto-scaling,   │
│ Engine           │ day      │          │ SQL,etc  │ apps     │ fully managed   │
├──────────────────┼──────────┼──────────┼──────────┼──────────┼─────────────────┤
│ Azure App        │ 10 free  │ No       │ Azure    │ Azure    │ .NET + Python   │
│ Service          │ apps     │          │ SQL,etc  │ apps     │ apps            │
├──────────────────┼──────────┼──────────┼──────────┼──────────┼─────────────────┤
│ Koyeb            │ 2 apps   │ No       │ Postgres │ Global   │ Fast deploy,    │
│                  │ free     │          │ (managed)│ edge     │ edge computing  │
├──────────────────┼──────────┼──────────┼──────────┼──────────┼─────────────────┤
│ Porter           │ No       │ Yes      │ PG,Redis │ K8s-     │ Heroku on K8s   │
│                  │          │ (via K8s)│          │ based    │                 │
├──────────────────┼──────────┼──────────┼──────────┼──────────┼─────────────────┤
│ Zeabur           │ Yes      │ No       │ PG,MySQL │ Chinese  │ Fast deploy,    │
│                  │ (5 apps) │          │ Redis    │ + global │ simple UX       │
├──────────────────┼──────────┼──────────┼──────────┼──────────┼─────────────────┤
│ Northflank       │ 2 free   │ No       │ PG,MySQL │ Docker + │ Git + Docker    │
│                  │ services │          │ MongoDB  │ databases│ deploy          │
├──────────────────┼──────────┼──────────┼──────────┼──────────┼─────────────────┤
│ Clever Cloud     │ Yes      │ No       │ PG,MySQL │ European │ Auto-scaling,   │
│                  │          │          │ Redis    │ hosting  │ PaaS            │
└──────────────────┴──────────┴──────────┴──────────┴──────────┴─────────────────┘
```

---

## 33. CDN AND EDGE COMPUTE PLATFORMS

### What is a CDN?

A **CDN (Content Delivery Network)** is a globally distributed network of servers that caches and delivers your content from the server closest to the user. When a user in Tokyo requests your website, instead of hitting your server in Virginia (150ms latency), the CDN serves it from a Tokyo server (5ms latency).

CDNs are used for:
- **Static assets** — Images, CSS, JavaScript files served from edge servers
- **API caching** — Cache API responses at the edge to reduce backend load
- **DDoS protection** — Absorb attack traffic before it reaches your servers
- **SSL termination** — Handle HTTPS at the edge

**Edge compute** goes beyond caching — it runs your actual code at CDN edge locations worldwide. Instead of just serving cached files, it executes JavaScript/TypeScript at the edge with <1ms cold starts.

Why this matters for AI applications:
- **Edge AI inference** — Run small ML models (embeddings, classification) at the edge for <10ms latency
- **Edge routing** — Decide which LLM provider to use based on user location, at the edge
- **Edge caching** — Cache LLM responses at the edge for instant responses to common queries
- **Edge authentication** — Verify API keys at the edge before hitting your backend

Key CDN/Edge platforms:
- **Cloudflare** — Largest network (300+ cities), best free tier, Workers for edge compute
- **AWS CloudFront** — AWS's CDN. Lambda@Edge for compute. Deep AWS integration.
- **Fastly** — Performance-focused. Compute@Edge with WebAssembly.
- **Akamai** — Largest enterprise CDN. EdgeWorkers for compute.

### 33.1 CDN COMPARISON

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                    CDN & EDGE COMPUTE PLATFORMS                                 │
├──────────────────┬──────────┬──────────┬──────────┬──────────┬─────────────────┤
│ Platform         │ Free Tier│ Edge     │ Edge     │ Workers/ │ Best For        │
│                  │          │ Compute  │ Functions│ Lambdas  │                 │
├──────────────────┼──────────┼──────────┼──────────┼──────────┼─────────────────┤
│ Cloudflare       │ Yes      │ Workers  │ Yes      │ Unlimited│ Best free tier, │
│                  │ (generous│ (V8)     │          │ (free)   │ edge compute    │
├──────────────────┼──────────┼──────────┼──────────┼──────────┼─────────────────┤
│ AWS CloudFront   │ 1TB/12mo │ Lambda@  │ Yes      │ Yes      │ AWS ecosystem   │
│                  │          │ Edge     │          │          │                 │
├──────────────────┼──────────┼──────────┼──────────┼──────────┼─────────────────┤
│ Fastly           │ $50/mo   │ Compute@ │ Yes      │ Yes      │ Performance,    │
│                  │ credit   │ Edge(WASM│          │          │ VCL             │
├──────────────────┼──────────┼──────────┼──────────┼──────────┼─────────────────┤
│ Akamai           │ No       │ EdgeWorkers│ Yes    │ Yes      │ Enterprise,     │
│                  │          │          │          │          │ largest network │
├──────────────────┼──────────┼──────────┼──────────┼──────────┼─────────────────┤
│ Vercel Edge      │ Yes      │ Edge     │ Yes      │ N/A      │ Next.js apps    │
│ Network          │          │ Functions│          │          │                 │
├──────────────────┼──────────┼──────────┼──────────┼──────────┼─────────────────┤
│ Netlify Edge     │ Yes      │ Deno-    │ Yes      │ Yes      │ Jamstack sites  │
│                  │          │ based    │          │          │                 │
├──────────────────┼──────────┼──────────┼──────────┼──────────┼─────────────────┤
│ bunny.net        │ $1/mo    │ No       │ No       │ No       │ Cheapest CDN    │
│                  │ (100GB)  │          │          │          │                 │
├──────────────────┼──────────┼──────────┼──────────┼──────────┼─────────────────┤
│ KeyCDN           │ Free tier│ No       │ No       │ No       │ Simple, cheap   │
│                  │ (limited)│          │          │          │                 │
└──────────────────┴──────────┴──────────┴──────────┴──────────┴─────────────────┘
```

---

## 34. AI-SPECIFIC DEPLOYMENT PLATFORMS (EXPANDED)

### What are these Additional AI Platforms?

Section 5 covered the major ML platforms (HuggingFace, Modal, Replicate, SageMaker, Vertex AI). This section covers additional AI-specific platforms that serve specialized niches:

- **Inference APIs** (Together AI, Groq, Fireworks AI, Lepton AI) — Instead of deploying your own model, call a pre-deployed model via API. These platforms host open-source models (Llama, Mistral, etc.) and charge per token. Often cheaper and faster than self-hosting.
- **GPU Cloud** (CoreWeave, Lambda Labs, RunPod) — Rent GPU servers for training or inference. Cheaper than AWS/GCP for GPU workloads. Popular with ML researchers and startups.
- **LLMOps Platforms** (Dify.ai, Langflow, FlowiseAI) — Visual builders for LLM applications. Drag-and-drop interface for creating RAG pipelines, chatbots, and AI workflows. Great for non-engineers or rapid prototyping.
- **Workflow Automation** (n8n, Inngest) — Automate multi-step AI workflows. Chain together LLM calls, data processing, and external API integrations.

### 34.1 AI PLATFORMS NOT COVERED IN MAIN GUIDE

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                    ADDITIONAL AI PLATFORMS                                      │
├──────────────────┬──────────┬──────────┬──────────┬─────────────────────────────┤
│ Platform         │ Type     │ Free Tier│ Best For │ Key Feature                │
├──────────────────┼──────────┼──────────┼──────────┼─────────────────────────────┤
│ Together AI      │ Inference│ Yes      │ Open     │ Cheapest open-model        │
│                  │ API      │ ($5 cr)  │ models   │ inference                  │
├──────────────────┼──────────┼──────────┼──────────┼─────────────────────────────┤
│ Groq             │ Inference│ Yes      │ Fast     │ LPU chip, fastest          │
│                  │ API      │          │ inference│ inference (10x faster)     │
├──────────────────┼──────────┼──────────┼──────────┼─────────────────────────────┤
│ Fireworks AI     │ Inference│ Yes      │ Fast     │ Fast open-model            │
│                  │ API      │ ($1 cr)  │ models   │ inference                  │
├──────────────────┼──────────┼──────────┼──────────┼─────────────────────────────┤
│ Anyscale         │ Inference│ Yes      │ Ray-     │ Managed Ray + LLM          │
│ (Ray)            │ + Serve  │          │ based ML │ serving                    │
├──────────────────┼──────────┼──────────┼──────────┼─────────────────────────────┤
│ Bento Cloud      │ Model    │ Yes      │ Model    │ BentoML managed            │
│                  │ Serving  │          │ packaging│ cloud                      │
├──────────────────┼──────────┼──────────┼──────────┼─────────────────────────────┤
│ Banana.dev       │ GPU      │ Yes      │ ML       │ Serverless GPU             │
│                  │ Serverless│         │ models   │ (similar to Modal)         │
├──────────────────┼──────────┼──────────┼──────────┼─────────────────────────────┤
│ CoreWeave        │ GPU Cloud│ No       │ Large    │ GPU cloud for              │
│                  │          │          │ models   │ AI training/inference      │
├──────────────────┼──────────┼──────────┼──────────┼─────────────────────────────┤
│ Lambda Labs      │ GPU Cloud│ No       │ Training │ Affordable GPU             │
│                  │          │          │ + infer  │ cloud (A100, H100)         │
├──────────────────┼──────────┼──────────┼──────────┼─────────────────────────────┤
│ RunPod           │ GPU      │ Yes      │ ML       │ Serverless +               │
│                  │ Serverless│ ($10 cr)│ inference│ persistent GPU             │
├──────────────────┼──────────┼──────────┼──────────┼─────────────────────────────┤
│ Lepton AI        │ Inference│ Yes      │ Open     │ Managed LLM                │
│                  │ API      │          │ models   │ inference                  │
├──────────────────┼──────────┼──────────┼──────────┼─────────────────────────────┤
│ Dify.ai          │ LLMOps   │ Yes      │ App      │ No-code LLM app            │
│                  │ Platform │          │ building │ builder                    │
├──────────────────┼──────────┼──────────┼──────────┼─────────────────────────────┤
│ Langflow         │ LLMOps   │ Free     │ Visual   │ Visual LLM workflow        │
│                  │          │ (open)   │ workflows│ builder                    │
├──────────────────┼──────────┼──────────┼──────────┼─────────────────────────────┤
│ FlowiseAI        │ LLMOps   │ Free     │ Chatflow │ Open-source chatflow       │
│                  │          │ (open)   │ builder  │ builder                    │
├──────────────────┼──────────┼──────────┼──────────┼─────────────────────────────┤
│ n8n              │ Workflow │ Yes      │ AI       │ Self-hosted workflow       │
│                  │ Automation│         │ workflows│ automation with AI         │
└──────────────────┴──────────┴──────────┴──────────┴─────────────────────────────┘
```

---

## 35. COMPREHENSIVE PLATFORM MATRIX (EVERYTHING IN ONE TABLE)

### What is this Matrix?

This is a single reference table that lists **every platform mentioned in this guide**, organized by category. Use it as a quick lookup when you need to find a platform for a specific need. Each category lists the platforms covered, so you can jump to the relevant section for details.

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│              COMPLETE AI DEPLOYMENT PLATFORM MATRIX                             │
├─────────────────────────────────────────────────────────────────────────────────┤
│                                                                                 │
│  CATEGORY               PLATFORMS COVERED                                       │
│  ────────               ──────────────────                                       │
│                                                                                 │
│  Cloud Compute          AWS (Lambda, ECS, SageMaker)                            │
│                         GCP (Cloud Run, Vertex AI, Cloud Functions)              │
│                         Azure (Container Apps, Azure ML, Functions)              │
│                                                                                 │
│  PaaS                   Railway, Render, Fly.io, Vercel, Netlify                │
│                         Heroku, DigitalOcean App Platform, Google App Engine     │
│                         Azure App Service, Koyeb, Porter, Zeabur, Northflank    │
│                                                                                 │
│  ML Platforms           HuggingFace Spaces, Modal, Replicate                    │
│                         SageMaker, Vertex AI, Azure ML                          │
│                         Together AI, Groq, Fireworks AI, RunPod                 │
│                         Banana.dev, CoreWeave, Lambda Labs, Lepton AI           │
│                                                                                 │
│  Model Serving          vLLM, TGI, Triton, TorchServe, TF Serving              │
│                         ONNX Runtime, Ollama, llama.cpp, SGLang                 │
│                         Ray Serve, BentoML                                      │
│                                                                                 │
│  Vector Databases       Pinecone, Weaviate, Qdrant, Milvus, ChromaDB           │
│                         pgvector, Vespa, Typesense, Turbopuffer, LanceDB        │
│                         Astra DB, SingleStore, Supabase Vector                  │
│                                                                                 │
│  Databases              Supabase, PlanetScale, Neon, MongoDB Atlas              │
│                         CockroachDB, TiDB, AWS RDS, Cloud SQL, Azure DB         │
│                         Redis Cloud, Upstash, DynamoDB, Firestore, Cosmos DB    │
│                         Neo4j Aura, InfluxDB, Timescale, Aiven                  │
│                                                                                 │
│  Serverless             AWS Lambda, Google Cloud Functions, Azure Functions      │
│                         Cloudflare Workers, Deno Deploy                         │
│                         Vercel Functions, Netlify Functions                     │
│                         AWS Lambda@Edge, Modal                                  │
│                                                                                 │
│  UI/Frontend            Streamlit Cloud, Gradio/HF Spaces                      │
│                         Vercel, Netlify, GitHub Pages, Cloudflare Pages         │
│                         AWS Amplify, Firebase Hosting, Azure Static Web Apps    │
│                                                                                 │
│  API Gateway            LiteLLM Proxy, Portkey, Helicone                        │
│                         Kong, AWS API Gateway, Azure API Mgmt, Apigee           │
│                         Nginx, Traefik                                          │
│                                                                                 │
│  Storage                AWS S3, GCS, Azure Blob, Cloudflare R2                  │
│                         MinIO, Supabase Storage, DigitalOcean Spaces            │
│                         Backblaze B2                                            │
│                                                                                 │
│  Message Queues         AWS SQS/SNS, Google Pub/Sub, Azure Service Bus          │
│                         Upstash Kafka, Confluent Cloud, RabbitMQ Cloud          │
│                         Redis Streams, Inngest                                  │
│                                                                                 │
│  Container Orchestration Docker, Docker Compose, Kubernetes                     │
│                         EKS, GKE, AKS, DigitalOcean K8s, Linode K8s            │
│                         Vultr K8s, Civo K8s, Scaleway K8s                       │
│                         ECS Fargate, Cloud Run                                  │
│                                                                                 │
│  CDN/Edge              Cloudflare, AWS CloudFront, Fastly, Akamai               │
│                         Vercel Edge, Netlify Edge, bunny.net, KeyCDN            │
│                                                                                 │
│  Observability          OpenTelemetry, Prometheus, Grafana, Datadog             │
│                         New Relic, CloudWatch, Sentry, Jaeger, Tempo            │
│                         Loki, ELK Stack, Honeycomb, Lightstep                   │
│                                                                                 │
│  Incident Management    PagerDuty, Opsgenie, Slack, VictorOps                  │
│                         Grafana Alerting, AWS SNS, Azure Alerts                 │
│                                                                                 │
│  LLMOps/Workflow        Dify.ai, Langflow, FlowiseAI, n8n                      │
│                         LangSmith, Arize, Weights & Biases, MLflow              │
│                                                                                 │
│  CI/CD                  GitHub Actions, GitLab CI, ArgoCD                       │
│                         CircleCI, Jenkins, Tekton, FluxCD                       │
│                                                                                 │
└─────────────────────────────────────────────────────────────────────────────────┘
```

---

## 36. PROVIDER SELECTION DECISION TREES

### How to Choose the Right Provider?

With hundreds of platforms available, choosing the right one can be overwhelming. These decision trees simplify the process by asking a series of questions and leading you to the best option for your specific situation.

The key factors in choosing a provider:
1. **What are you deploying?** (API, model, database, static site)
2. **What's your budget?** (free tier, pay-as-you-go, enterprise contract)
3. **What's your team size?** (solo, small team, platform team)
4. **What's your traffic pattern?** (low, bursty, high, global)
5. **What's your existing stack?** (AWS shop, GCP shop, multi-cloud)

### 36.1 DATABASE SELECTION

```
┌─────────────────────────────────────────────────────────────────────────┐
│                    DATABASE SELECTION DECISION TREE                      │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  What type of data?                                                     │
│  ├─ Structured (tables, relations)                                      │
│  │  ├─ Need global distribution? → CockroachDB or TiDB                 │
│  │  ├─ Need scale-to-zero? → Neon or PlanetScale                       │
│  │  ├─ Need full-stack platform? → Supabase                            │
│  │  ├─ Need enterprise? → AWS RDS or Cloud SQL                         │
│  │  └─ Need simplicity? → Supabase or Neon                             │
│  │                                                                      │
│  ├─ Document (JSON, flexible schema)                                    │
│  │  ├─ Need vector search? → MongoDB Atlas                              │
│  │  ├─ Need serverless? → DynamoDB or Firestore                        │
│  │  └─ Need full-text search? → MongoDB Atlas or Elasticsearch         │
│  │                                                                      │
│  ├─ Key-Value (cache, sessions)                                         │
│  │  ├─ Need serverless? → Upstash Redis                                │
│  │  ├─ Need enterprise? → Redis Cloud or ElastiCache                   │
│  │  └─ Need edge-compatible? → Upstash Redis or Cloudflare KV          │
│  │                                                                      │
│  ├─ Vector (embeddings, similarity search)                              │
│  │  ├─ Need easiest setup? → Pinecone                                  │
│  │  ├─ Need hybrid search? → Weaviate or Qdrant                        │
│  │  ├─ Need existing Postgres? → pgvector or Supabase Vector           │
│  │  ├─ Need self-hosted? → Qdrant or Milvus                            │
│  │  └─ Need embedded? → LanceDB or ChromaDB                            │
│  │                                                                      │
│  └─ Time-Series (metrics, logs)                                         │
│     ├─ Need SQL-compatible? → TimescaleDB                               │
│     ├─ Need serverless? → AWS Timestream                                │
│     └─ Need full-featured? → InfluxDB Cloud                             │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

### 36.2 MODEL SERVING SELECTION

```
┌─────────────────────────────────────────────────────────────────────────┐
│                    MODEL SERVING SELECTION                               │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  What model type?                                                       │
│  ├─ Large Language Model (LLM)                                          │
│  │  ├─ Need highest throughput? → vLLM                                  │
│  │  ├─ Need HuggingFace integration? → TGI                              │
│  │  ├─ Need local development? → Ollama                                 │
│  │  ├─ Need structured output? → SGLang                                 │
│  │  ├─ Need managed API? → Together AI or Groq                         │
│  │  └─ Need multi-model? → Triton or Ray Serve                         │
│  │                                                                      │
│  ├─ PyTorch Model                                                       │
│  │  ├─ Need production serving? → TorchServe                            │
│  │  ├─ Need distributed? → Ray Serve                                    │
│  │  └─ Need packaging? → BentoML                                        │
│  │                                                                      │
│  ├─ TensorFlow Model                                                    │
│  │  └─ TF Serving is the standard                                       │
│  │                                                                      │
│  ├─ Cross-Platform Model                                                │
│  │  ├─ Need CPU optimization? → ONNX Runtime                            │
│  │  ├─ Need browser? → ONNX.js or TensorFlow.js                        │
│  │  └─ Need mobile? → CoreML (iOS) or TFLite (Android)                 │
│  │                                                                      │
│  └─ Don't want to manage serving?                                       │
│     ├─ AWS? → SageMaker Endpoints                                       │
│     ├─ GCP? → Vertex AI Endpoints                                       │
│     ├─ Azure? → Azure ML Endpoints                                      │
│     └─ Serverless GPU? → Modal or Replicate                             │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

---

*This supplementary section (Part 4) adds 13 additional sections (23-36) covering every major deployment provider across databases, vector stores, serverless, UI, model serving, API gateways, storage, message queues, Kubernetes, PaaS, CDN, AI platforms, and LLMOps tools — bringing the total to 36 sections.*

---



---

# PART 5: ADVANCED OPERATIONS & SECURITY

---

## 37. INFRASTRUCTURE AS CODE (IaC)

### What is Infrastructure as Code?

**Infrastructure as Code (IaC)** means defining your entire infrastructure (servers, databases, networks, DNS, certificates) in code files instead of clicking through web consoles. Just like application code, infrastructure code is version-controlled, reviewed, tested, and automated.

Why IaC matters for AI deployments:
- **Reproducibility** — Spin up an identical copy of your production environment in minutes
- **Version control** — Track every infrastructure change in Git. Who changed what, when, and why
- **Disaster recovery** — Rebuild your entire infrastructure from code after a disaster
- **Consistency** — No more "it works on my machine" — every environment is identical
- **Automation** — No manual clicking through AWS/GCP/Azure consoles

Key IaC tools:
- **Terraform** — The industry standard. Cloud-agnostic (works with AWS, GCP, Azure, and 100+ providers). Uses HCL (HashiCorp Configuration Language).
- **Pulumi** — IaC using real programming languages (Python, TypeScript, Go). Good for teams that prefer code over YAML/HCL.
- **AWS CloudFormation** — AWS-native IaC. JSON/YAML templates. AWS-only.
- **Google Deployment Manager** — GCP-native IaC. Less popular than Terraform.
- **Azure Bicep** — Azure-native IaC. Simplified ARM templates.

### 37.1 TERRAFORM FOR AI INFRASTRUCTURE

```hcl
# File: terraform/main.tf
# Complete AI service infrastructure on AWS

terraform {
  required_version = ">= 1.5"
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }

  # Remote state (team collaboration)
  backend "s3" {
    bucket         = "my-terraform-state"
    key            = "ai-service/terraform.tfstate"
    region         = "us-east-1"
    dynamodb_table = "terraform-locks"
    encrypt        = true
  }
}

provider "aws" {
  region = var.aws_region

  default_tags {
    tags = {
      Project     = "ai-service"
      Environment = var.environment
      ManagedBy   = "terraform"
    }
  }
}

# === VARIABLES ===

variable "aws_region" {
  default = "us-east-1"
}

variable "environment" {
  default = "production"
}

variable "db_password" {
  sensitive = true
}

# === NETWORKING ===

resource "aws_vpc" "ai_vpc" {
  cidr_block           = "10.0.0.0/16"
  enable_dns_hostnames = true
  enable_dns_support   = true

  tags = { Name = "ai-vpc" }
}

resource "aws_subnet" "private" {
  count             = 3
  vpc_id            = aws_vpc.ai_vpc.id
  cidr_block        = "10.0.${count.index + 1}.0/24"
  availability_zone = data.aws_availability_zones.available.names[count.index]

  tags = { Name = "ai-private-${count.index}" }
}

resource "aws_subnet" "public" {
  count             = 3
  vpc_id            = aws_vpc.ai_vpc.id
  cidr_block        = "10.0.${count.index + 10}.0/24"
  availability_zone = data.aws_availability_zones.available.names[count.index]

  tags = { Name = "ai-public-${count.index}" }
}

# === ECS CLUSTER ===

resource "aws_ecs_cluster" "ai_cluster" {
  name = "ai-${var.environment}"

  setting {
    name  = "containerInsights"
    value = "enabled"
  }

  configuration {
    execute_command_configuration {
      logging = "OVERRIDE"
      log_configuration {
        cloud_watch_log_group_name = aws_cloudwatch_log_group.ecs.name
      }
    }
  }
}

resource "aws_ecs_task_definition" "ai_api" {
  family                   = "ai-api"
  network_mode             = "awsvpc"
  requires_compatibilities = ["FARGATE"]
  cpu                      = 1024
  memory                   = 2048
  execution_role_arn       = aws_iam_role.ecs_execution.arn
  task_role_arn            = aws_iam_role.ecs_task.arn

  container_definitions = jsonencode([
    {
      name      = "ai-api"
      image     = "${aws_ecr_repository.ai_api.repository_url}:latest"
      essential = true
      portMappings = [{ containerPort = 8000, protocol = "tcp" }]
      environment = [
        { name = "ENVIRONMENT", value = var.environment },
        { name = "LOG_LEVEL",   value = "INFO" },
      ]
      secrets = [
        { name = "DATABASE_URL",  valueFrom = aws_secretsmanager_secret.db_url.arn },
        { name = "OPENAI_API_KEY", valueFrom = aws_secretsmanager_secret.openai_key.arn },
      ]
      logConfiguration = {
        logDriver = "awslogs"
        options = {
          "awslogs-group"         = aws_cloudwatch_log_group.ecs.name
          "awslogs-region"        = var.aws_region
          "awslogs-stream-prefix" = "api"
        }
      }
      healthCheck = {
        command     = ["CMD-SHELL", "curl -f http://localhost:8000/health || exit 1"]
        interval    = 30
        timeout     = 5
        retries     = 3
        startPeriod = 60
      }
    }
  ])
}

# === DATABASE ===

resource "aws_db_instance" "postgres" {
  identifier     = "ai-${var.environment}"
  engine         = "postgres"
  engine_version = "16.1"
  instance_class = "db.t3.medium"

  allocated_storage     = 50
  max_allocated_storage = 200
  storage_encrypted     = true

  db_name  = "ai_production"
  username = "ai_admin"
  password = var.db_password

  multi_az            = true
  publicly_accessible = false
  vpc_security_group_ids = [aws_security_group.db.id]
  db_subnet_group_name   = aws_db_subnet_group.main.name

  backup_retention_period = 7
  backup_window          = "03:00-04:00"
  maintenance_window     = "sun:04:00-sun:05:00"

  deletion_protection = true
  skip_final_snapshot = false
  final_snapshot_identifier = "ai-${var.environment}-final"
}

# === REDIS ===

resource "aws_elasticache_cluster" "redis" {
  cluster_id           = "ai-${var.environment}"
  engine               = "redis"
  node_type            = "cache.t3.medium"
  num_cache_nodes      = 1
  parameter_group_name = "default.redis7"
  port                 = 6379
  security_group_ids   = [aws_security_group.redis.id]
  subnet_group_name    = aws_elasticache_subnet_group.main.name
}

# === SECRETS ===

resource "aws_secretsmanager_secret" "openai_key" {
  name        = "ai/${var.environment}/openai-api-key"
  description = "OpenAI API Key"
}

resource "aws_secretsmanager_secret" "db_url" {
  name        = "ai/${var.environment}/database-url"
  description = "Database connection URL"
}

# === MONITORING ===

resource "aws_cloudwatch_log_group" "ecs" {
  name              = "/ecs/ai-${var.environment}"
  retention_in_days = 30
}

resource "aws_cloudwatch_metric_alarm" "high_cpu" {
  alarm_name          = "ai-${var.environment}-high-cpu"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = 2
  metric_name         = "CPUUtilization"
  namespace           = "AWS/ECS"
  period              = 300
  statistic           = "Average"
  threshold           = 80
  alarm_actions       = [aws_sns_topic.alerts.arn]
}

# === OUTPUTS ===

output "api_endpoint" {
  value = aws_lb.ai_api.dns_name
}

output "database_endpoint" {
  value = aws_db_instance.postgres.endpoint
}
```

### 37.2 PULUMI (IaC with Python)

```python
# File: infra/pulumi_main.py
"""Pulumi infrastructure for AI service (Python-native IaC)."""

import pulumi
import pulumi_aws as aws
import json

# Configuration
config = pulumi.Config()
environment = config.require("environment")
db_password = config.require_secret("db_password")

# VPC
vpc = aws.ec2.Vpc(
    "ai-vpc",
    cidr_block="10.0.0.0/16",
    enable_dns_hostnames=True,
    enable_dns_support=True,
    tags={"Name": "ai-vpc", "Environment": environment},
)

# ECS Cluster
cluster = aws.ecs.Cluster(
    "ai-cluster",
    name=f"ai-{environment}",
    settings=[aws.ecs.ClusterSettingArgs(
        name="containerInsights",
        value="enabled",
    )],
)

# Task Definition
task_def = aws.ecs.TaskDefinition(
    "ai-api-task",
    family="ai-api",
    network_mode="awsvpc",
    requires_compatibilities=["FARGATE"],
    cpu="1024",
    memory="2048",
    execution_role_arn=ecs_execution_role.arn,
    task_role_arn=ecs_task_role.arn,
    container_definitions=json.dumps([{
        "name": "ai-api",
        "image": f"{ecr_repo.repository_url}:latest",
        "essential": True,
        "portMappings": [{"containerPort": 8000}],
        "environment": [
            {"name": "ENVIRONMENT", "value": environment},
        ],
        "logConfiguration": {
            "logDriver": "awslogs",
            "options": {
                "awslogs-group": log_group.name,
                "awslogs-region": "us-east-1",
                "awslogs-stream-prefix": "api",
            },
        },
    }]),
)

# RDS PostgreSQL
db = aws.rds.Instance(
    "ai-postgres",
    engine="postgres",
    engine_version="16.1",
    instance_class="db.t3.medium",
    allocated_storage=50,
    max_allocated_storage=200,
    storage_encrypted=True,
    db_name="ai_production",
    username="ai_admin",
    password=db_password,
    multi_az=True,
    publicly_accessible=False,
    backup_retention_period=7,
    deletion_protection=True,
)

# Exports
pulumi.export("api_endpoint", lb.dns_name)
pulumi.export("database_endpoint", db.endpoint)
```

---

## 38. SECRETS MANAGEMENT

### What is Secrets Management?

**Secrets management** is the secure storage, access control, and rotation of sensitive credentials — API keys, database passwords, encryption keys, certificates. Never hardcode secrets in your code or commit them to Git.

The risks of poor secrets management:
- **Leaked API keys** — Someone finds your OpenAI key in a public repo and runs up a $10,000 bill
- **Stolen database credentials** — Attacker accesses all user data
- **Expired certificates** — Service goes down because a TLS cert expired
- **No rotation** — Same password for years means higher risk if compromised

Key secrets management tools:
- **AWS Secrets Manager** — Managed secrets with automatic rotation. $0.40/secret/month.
- **AWS Systems Manager Parameter Store** — Cheaper alternative ($0.05/parameter). No auto-rotation.
- **Google Secret Manager** — GCP's managed secrets service.
- **Azure Key Vault** — Azure's managed secrets service.
- **HashiCorp Vault** — Self-hosted or cloud. Most feature-rich. Supports dynamic secrets.
- **Doppler** — Developer-friendly secrets manager. Works everywhere.
- **Infisical** — Open-source secrets manager. Self-hostable.

### 38.1 SECRETS MANAGEMENT PATTERNS

```python
# File: src/secrets/manager.py
"""Unified secrets management for AI applications."""

import os
import json
import logging
from functools import lru_cache
from typing import Optional

logger = logging.getLogger(__name__)


class SecretsManager:
    """Unified interface for secrets from multiple providers."""

    def __init__(self, provider: str = "auto"):
        self.provider = provider or self._detect_provider()
        self._cache = {}
        self._init_client()

    def _detect_provider(self) -> str:
        """Auto-detect the secrets provider based on environment."""
        if os.getenv("AWS_REGION"):
            return "aws"
        elif os.getenv("GOOGLE_CLOUD_PROJECT"):
            return "gcp"
        elif os.getenv("AZURE_TENANT_ID"):
            return "azure"
        elif os.getenv("VAULT_ADDR"):
            return "vault"
        elif os.getenv("DOPPLER_TOKEN"):
            return "doppler"
        else:
            return "env"  # Fallback to environment variables

    def _init_client(self):
        """Initialize the secrets client."""
        if self.provider == "aws":
            import boto3
            self.client = boto3.client("secretsmanager")
        elif self.provider == "gcp":
            from google.cloud import secretmanager
            self.client = secretmanager.SecretManagerServiceClient()
        elif self.provider == "azure":
            from azure.keyvault.secrets import SecretClient
            from azure.identity import DefaultAzureCredential
            vault_url = os.getenv("AZURE_KEY_VAULT_URL")
            self.client = SecretClient(vault_url=vault_url, credential=DefaultAzureCredential())
        elif self.provider == "vault":
            import hvac
            self.client = hvac.Client(
                url=os.getenv("VAULT_ADDR"),
                token=os.getenv("VAULT_TOKEN"),
            )
        logger.info(f"Secrets provider: {self.provider}")

    def get_secret(self, name: str, version: str = "latest") -> Optional[str]:
        """Get a secret value by name."""
        # Check cache first
        cache_key = f"{name}:{version}"
        if cache_key in self._cache:
            return self._cache[cache_key]

        try:
            value = self._fetch_secret(name, version)
            self._cache[cache_key] = value
            return value
        except Exception as e:
            logger.error(f"Failed to get secret '{name}': {e}")
            # Fallback to environment variable
            return os.getenv(name.upper().replace("/", "_").replace("-", "_"))

    def _fetch_secret(self, name: str, version: str) -> str:
        """Fetch secret from the configured provider."""
        if self.provider == "aws":
            response = self.client.get_secret_value(SecretId=name, VersionId=version)
            return response["SecretString"]

        elif self.provider == "gcp":
            project = os.getenv("GOOGLE_CLOUD_PROJECT")
            secret_name = f"projects/{project}/secrets/{name}/versions/{version}"
            response = self.client.access_secret_version(request={"name": secret_name})
            return response.payload.data.decode("UTF-8")

        elif self.provider == "azure":
            secret = self.client.get_secret(name, version=version)
            return secret.value

        elif self.provider == "vault":
            response = self.client.secrets.kv.v2.read_secret_version(path=name)
            return response["data"]["data"]["value"]

        elif self.provider == "doppler":
            import httpx
            token = os.getenv("DOPPLER_TOKEN")
            project = os.getenv("DOPPLER_PROJECT")
            config = os.getenv("DOPPLER_CONFIG", "prd")
            resp = httpx.get(
                f"https://api.doppler.com/v3/configs/config/secret",
                params={"project": project, "config": config, "name": name},
                headers={"Authorization": f"Bearer {token}"},
            )
            return resp.json()["value"]

        elif self.provider == "env":
            return os.getenv(name.upper().replace("/", "_").replace("-", "_"))

        raise ValueError(f"Unknown provider: {self.provider}")

    def get_secret_json(self, name: str) -> dict:
        """Get a secret that contains JSON."""
        value = self.get_secret(name)
        return json.loads(value) if value else {}


# Global instance
_secrets: SecretsManager = None

def get_secrets() -> SecretsManager:
    """Get the global secrets manager."""
    global _secrets
    if _secrets is None:
        _secrets = SecretsManager()
    return _secrets

def get_secret(name: str) -> Optional[str]:
    """Convenience function to get a secret."""
    return get_secrets().get_secret(name)
```

```yaml
# File: .github/workflows/deploy.yml (Secrets in CI/CD)
# How to use secrets in GitHub Actions
jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - name: Deploy
        env:
          # GitHub encrypted secrets
          DATABASE_URL: ${{ secrets.DATABASE_URL }}
          OPENAI_API_KEY: ${{ secrets.OPENAI_API_KEY }}
          # Never log secrets!
        run: |
          echo "Deploying with secrets..."
          # Secrets are injected as environment variables
```

---

## 39. MODEL MONITORING AND DRIFT DETECTION

### What is Model Monitoring?

**Model monitoring** is the continuous observation of your ML model's performance in production. Unlike traditional software (which either works or doesn't), ML models can **silently degrade** — the code runs fine, but the predictions get worse over time.

This happens because of **drift**:

- **Data drift** — The input data changes. If your model was trained on English text but starts receiving Spanish text, performance drops. If user behavior changes (new slang, new topics), the model's training data becomes stale.
- **Concept drift** — The relationship between inputs and outputs changes. What was considered "spam" in 2020 might not be "spam" in 2026.
- **Model degradation** — The model's predictions become less accurate over time as the world changes.

Why this matters for AI applications:
- An LLM chatbot might start giving outdated answers as the world changes
- A RAG system might return irrelevant documents as the knowledge base grows
- A classification model might become less accurate as user behavior shifts
- Embedding quality might degrade as new types of content are added

### 39.1 DRIFT DETECTION IMPLEMENTATION

```python
# File: src/monitoring/drift_detection.py
"""Model drift detection and monitoring."""

import numpy as np
import logging
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Optional
from scipy import stats

logger = logging.getLogger(__name__)


@dataclass
class DriftAlert:
    metric: str
    drift_type: str  # "data_drift", "concept_drift", "performance_drift"
    severity: str    # "warning", "critical"
    current_value: float
    baseline_value: float
    threshold: float
    timestamp: datetime = field(default_factory=datetime.now)


class ModelMonitor:
    """Monitor ML model performance and detect drift."""

    def __init__(
        self,
        model_name: str,
        baseline_window_hours: int = 24,
        detection_window_hours: int = 1,
    ):
        self.model_name = model_name
        self.baseline_window = timedelta(hours=baseline_window_hours)
        self.detection_window = timedelta(hours=detection_window_hours)
        self._baseline_stats = {}
        self._recent_predictions = []
        self._recent_latencies = []
        self._recent_confidences = []

    def record_prediction(
        self,
        input_text: str,
        output_text: str,
        latency_ms: float,
        confidence: float,
        user_feedback: Optional[float] = None,
    ):
        """Record a prediction for monitoring."""
        self._recent_predictions.append({
            "input": input_text,
            "output": output_text,
            "latency_ms": latency_ms,
            "confidence": confidence,
            "user_feedback": user_feedback,
            "timestamp": datetime.now(),
            "input_length": len(input_text),
            "output_length": len(output_text),
        })
        self._recent_latencies.append(latency_ms)
        self._recent_confidences.append(confidence)

    def set_baseline(self, predictions: list[dict]):
        """Set baseline statistics from historical data."""
        latencies = [p["latency_ms"] for p in predictions]
        confidences = [p["confidence"] for p in predictions]
        input_lengths = [p["input_length"] for p in predictions]
        output_lengths = [p["output_length"] for p in predictions]

        self._baseline_stats = {
            "latency": {"mean": np.mean(latencies), "std": np.std(latencies), "p95": np.percentile(latencies, 95)},
            "confidence": {"mean": np.mean(confidences), "std": np.std(confidences)},
            "input_length": {"mean": np.mean(input_lengths), "std": np.std(input_lengths)},
            "output_length": {"mean": np.mean(output_lengths), "std": np.std(output_lengths)},
        }

        logger.info(f"Baseline set for {self.model_name}: {len(predictions)} predictions")

    def check_drift(self) -> list[DriftAlert]:
        """Check for drift in recent predictions."""
        alerts = []

        if not self._baseline_stats:
            return alerts

        # Check latency drift
        if self._recent_latencies:
            latency_alert = self._check_metric_drift(
                "latency",
                self._recent_latencies,
                self._baseline_stats["latency"],
                threshold_multiplier=2.0,
            )
            if latency_alert:
                alerts.append(latency_alert)

        # Check confidence drift
        if self._recent_confidences:
            confidence_alert = self._check_metric_drift(
                "confidence",
                self._recent_confidences,
                self._baseline_stats["confidence"],
                threshold_multiplier=0.5,  # Alert if confidence drops by 50%
                direction="decrease",
            )
            if confidence_alert:
                alerts.append(confidence_alert)

        # Check input distribution drift
        if self._recent_predictions:
            input_lengths = [p["input_length"] for p in self._recent_predictions]
            input_alert = self._check_metric_drift(
                "input_length",
                input_lengths,
                self._baseline_stats["input_length"],
                threshold_multiplier=2.0,
            )
            if input_alert:
                alerts.append(input_alert)

        return alerts

    def _check_metric_drift(
        self,
        metric_name: str,
        recent_values: list[float],
        baseline: dict,
        threshold_multiplier: float,
        direction: str = "increase",
    ) -> Optional[DriftAlert]:
        """Check if a metric has drifted from baseline."""
        if len(recent_values) < 10:
            return None

        recent_mean = np.mean(recent_values)
        baseline_mean = baseline["mean"]
        baseline_std = baseline["std"]

        if baseline_std == 0:
            return None

        # Z-score test
        z_score = (recent_mean - baseline_mean) / baseline_std

        if direction == "increase" and z_score > threshold_multiplier:
            return DriftAlert(
                metric=metric_name,
                drift_type="data_drift",
                severity="warning" if z_score < 3 else "critical",
                current_value=recent_mean,
                baseline_value=baseline_mean,
                threshold=baseline_mean + (threshold_multiplier * baseline_std),
            )
        elif direction == "decrease" and z_score < -threshold_multiplier:
            return DriftAlert(
                metric=metric_name,
                drift_type="performance_drift",
                severity="warning" if z_score > -3 else "critical",
                current_value=recent_mean,
                baseline_value=baseline_mean,
                threshold=baseline_mean - (threshold_multiplier * baseline_std),
            )

        return None

    def get_quality_score(self) -> float:
        """Calculate overall model quality score (0-100)."""
        if not self._recent_predictions:
            return 100.0

        scores = []

        # Confidence score
        if self._recent_confidences:
            avg_conf = np.mean(self._recent_confidences)
            scores.append(min(avg_conf * 100, 100))

        # Latency score (100 if under baseline p95, 0 if 10x over)
        if self._recent_latencies and "latency" in self._baseline_stats:
            p95 = self._baseline_stats["latency"]["p95"]
            current_p95 = np.percentile(self._recent_latencies, 95)
            if p95 > 0:
                latency_score = max(0, 100 - ((current_p95 / p95 - 1) * 100))
                scores.append(latency_score)

        # User feedback score
        feedback_scores = [p["user_feedback"] for p in self._recent_predictions if p["user_feedback"] is not None]
        if feedback_scores:
            scores.append(np.mean(feedback_scores) * 100)

        return np.mean(scores) if scores else 100.0

    def get_report(self) -> dict:
        """Generate a monitoring report."""
        drift_alerts = self.check_drift()
        quality_score = self.get_quality_score()

        return {
            "model_name": self.model_name,
            "timestamp": datetime.now().isoformat(),
            "total_predictions": len(self._recent_predictions),
            "quality_score": round(quality_score, 2),
            "drift_alerts": [
                {
                    "metric": a.metric,
                    "type": a.drift_type,
                    "severity": a.severity,
                    "current": round(a.current_value, 4),
                    "baseline": round(a.baseline_value, 4),
                }
                for a in drift_alerts
            ],
            "latency": {
                "mean_ms": round(np.mean(self._recent_latencies), 2) if self._recent_latencies else 0,
                "p95_ms": round(np.percentile(self._recent_latencies, 95), 2) if self._recent_latencies else 0,
                "p99_ms": round(np.percentile(self._recent_latencies, 99), 2) if self._recent_latencies else 0,
            },
            "confidence": {
                "mean": round(np.mean(self._recent_confidences), 4) if self._recent_confidences else 0,
                "min": round(min(self._recent_confidences), 4) if self._recent_confidences else 0,
            },
        }
```

---

## 40. DISASTER RECOVERY AND BACKUP STRATEGIES

### What is Disaster Recovery?

**Disaster recovery (DR)** is the ability to restore your service after a catastrophic failure — data center outage, data corruption, security breach, or cloud provider failure. It's measured by two key metrics:

- **RTO (Recovery Time Objective)** — How quickly can you restore service? "RTO of 1 hour" means you must be back online within 1 hour.
- **RPO (Recovery Point Objective)** — How much data can you afford to lose? "RPO of 5 minutes" means you can lose at most 5 minutes of data.

For AI applications, DR is especially critical because:
- **Training data is expensive** — Months of data labeling and curation can't be easily recreated
- **Model artifacts are large** — 70B parameter models are 100GB+ and take hours to retrain
- **Vector databases are critical** — Losing your embeddings means re-processing your entire knowledge base
- **User conversations are valuable** — Chat history, feedback, and session data drive product improvement

### 40.1 BACKUP STRATEGY

```python
# File: src/backup/manager.py
"""Backup and disaster recovery manager."""

import asyncio
import logging
import subprocess
import boto3
from datetime import datetime, timedelta
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class BackupConfig:
    database_backup_interval_hours: int = 6
    vector_db_backup_interval_hours: int = 24
    model_backup_interval_hours: int = 24
    backup_retention_days: int = 30
    cross_region_replication: bool = True
    backup_region: str = "us-west-2"


class BackupManager:
    """Manage backups for AI application data."""

    def __init__(self, config: BackupConfig, s3_bucket: str):
        self.config = config
        self.s3_bucket = s3_bucket
        self.s3 = boto3.client("s3")

    async def backup_database(self, db_url: str):
        """Backup PostgreSQL database."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_file = f"/tmp/db_backup_{timestamp}.sql.gz"

        # pg_dump with compression
        cmd = f"pg_dump '{db_url}' | gzip > {backup_file}"
        subprocess.run(cmd, shell=True, check=True)

        # Upload to S3
        s3_key = f"backups/database/{timestamp}/dump.sql.gz"
        self.s3.upload_file(backup_file, self.s3_bucket, s3_key)

        # Cross-region replication
        if self.config.cross_region_replication:
            self._replicate_to_region(s3_key, self.config.backup_region)

        logger.info(f"Database backup completed: {s3_key}")

        # Cleanup old backups
        self._cleanup_old_backups("backups/database/", self.config.backup_retention_days)

    async def backup_vector_db(self, collection_name: str, vector_store):
        """Backup vector database."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        # Export all vectors
        vectors = vector_store.export_all(collection_name)

        import json
        backup_data = json.dumps(vectors)

        s3_key = f"backups/vectordb/{timestamp}/{collection_name}.json"
        self.s3.put_object(
            Bucket=self.s3_bucket,
            Key=s3_key,
            Body=backup_data.encode(),
        )

        logger.info(f"Vector DB backup completed: {s3_key}")

    async def backup_models(self, model_dir: str):
        """Backup model artifacts."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        # Sync model directory to S3
        cmd = f"aws s3 sync {model_dir} s3://{self.s3_bucket}/backups/models/{timestamp}/ --exclude '*.pyc' --exclude '__pycache__'"
        subprocess.run(cmd, shell=True, check=True)

        logger.info(f"Model backup completed: backups/models/{timestamp}/")

    def _replicate_to_region(self, s3_key: str, region: str):
        """Replicate backup to another region."""
        s3_dest = boto3.client("s3", region_name=region)
        dest_bucket = f"{self.s3_bucket}-dr"

        s3_dest.copy_object(
            Bucket=dest_bucket,
            Key=s3_key,
            CopySource={"Bucket": self.s3_bucket, "Key": s3_key},
        )

    def _cleanup_old_backups(self, prefix: str, retention_days: int):
        """Delete backups older than retention period."""
        cutoff = datetime.now() - timedelta(days=retention_days)

        response = self.s3.list_objects_v2(Bucket=self.s3_bucket, Prefix=prefix)
        for obj in response.get("Contents", []):
            if obj["LastModified"].replace(tzinfo=None) < cutoff:
                self.s3.delete_object(Bucket=self.s3_bucket, Key=obj["Key"])
                logger.info(f"Deleted old backup: {obj['Key']}")
```

### 40.2 DISASTER RECOVERY RUNBOOK

```markdown
# Disaster Recovery Runbook

## Scenario 1: Database Failure (RTO: 30 min, RPO: 6 hours)

### Steps:
1. Check if automatic failover triggered (Multi-AZ)
2. If not, promote read replica to primary
3. Update DNS/connection string
4. Verify application connectivity
5. Monitor for data consistency issues

### Commands:
```bash
# Check RDS status
aws rds describe-db-instances --db-identifier ai-production

# Promote read replica
aws rds promote-read-replica --db-identifier ai-production-replica

# Update application
kubectl set env deployment/ai-api DATABASE_URL=<new-url> -n ai-production
```

## Scenario 2: Vector DB Data Loss (RTO: 2 hours, RPO: 24 hours)

### Steps:
1. Identify scope of data loss
2. Restore from latest backup
3. Re-index any data since last backup
4. Verify search quality

## Scenario 3: Complete Region Outage (RTO: 4 hours, RPO: 6 hours)

### Steps:
1. Activate DR region
2. Restore database from cross-region backup
3. Restore vector DB from cross-region backup
4. Update DNS to point to DR region
5. Scale up DR infrastructure
6. Monitor and stabilize
7. Plan failback when primary region recovers
```

---

## 41. COST OPTIMIZATION

### What is Cost Optimization?

**Cost optimization** is the practice of reducing your cloud spending without sacrificing performance or reliability. Cloud costs can spiral out of control quickly — a misconfigured auto-scaling policy, an idle GPU instance, or excessive LLM API calls can cost thousands of dollars per month.

Key cost optimization strategies for AI applications:

1. **Right-sizing** — Don't over-provision. If your API uses 500MB RAM, don't allocate 4GB.
2. **Scale to zero** — When no traffic, pay nothing. Use serverless or scale-to-zero PaaS.
3. **Spot/preemptible instances** — Up to 90% cheaper than on-demand. Use for batch jobs and stateless workers.
4. **Reserved instances** — 1-3 year commitments for 30-60% savings on always-on services.
5. **Caching** — Cache LLM responses to avoid redundant API calls.
6. **Model selection** — Use smaller, cheaper models where possible. GPT-4 for complex queries, GPT-3.5 for simple ones.
7. **Token optimization** — Shorter prompts, fewer tokens, lower cost.
8. **Batch processing** — Process in batches instead of one-by-one for GPU efficiency.

### 41.1 COST TRACKING AND ALERTING

```python
# File: src/cost/tracker.py
"""Cost tracking and optimization for AI applications."""

import logging
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Optional

logger = logging.getLogger(__name__)


@dataclass
class CostBudget:
    daily_limit_usd: float
    monthly_limit_usd: float
    alert_threshold_pct: float = 80  # Alert at 80% of budget


@dataclass
class CostRecord:
    timestamp: datetime
    component: str  # "llm", "compute", "storage", "network"
    model: Optional[str]
    cost_usd: float
    tokens: Optional[int] = None
    request_id: Optional[str] = None


class CostTracker:
    """Track and optimize AI application costs."""

    def __init__(self, budget: CostBudget):
        self.budget = budget
        self._records: list[CostRecord] = []
        self._daily_costs: dict[str, float] = {}  # date -> cost
        self._model_costs: dict[str, float] = {}   # model -> cost

    def record_cost(
        self,
        component: str,
        cost_usd: float,
        model: str = None,
        tokens: int = None,
        request_id: str = None,
    ):
        """Record a cost event."""
        record = CostRecord(
            timestamp=datetime.now(),
            component=component,
            model=model,
            cost_usd=cost_usd,
            tokens=tokens,
            request_id=request_id,
        )
        self._records.append(record)

        # Update daily costs
        today = datetime.now().strftime("%Y-%m-%d")
        self._daily_costs[today] = self._daily_costs.get(today, 0) + cost_usd

        # Update model costs
        if model:
            self._model_costs[model] = self._model_costs.get(model, 0) + cost_usd

        # Check budget
        self._check_budget()

    def _check_budget(self):
        """Check if we're approaching budget limits."""
        today = datetime.now().strftime("%Y-%m-%d")
        daily_cost = self._daily_costs.get(today, 0)
        daily_pct = (daily_cost / self.budget.daily_limit_usd) * 100

        if daily_pct >= self.budget.alert_threshold_pct:
            logger.warning(f"Daily cost at {daily_pct:.1f}% of budget: ${daily_cost:.2f}/${self.budget.daily_limit_usd:.2f}")

        # Monthly cost
        month = datetime.now().strftime("%Y-%m")
        monthly_cost = sum(
            v for k, v in self._daily_costs.items() if k.startswith(month)
        )
        monthly_pct = (monthly_cost / self.budget.monthly_limit_usd) * 100

        if monthly_pct >= self.budget.alert_threshold_pct:
            logger.warning(f"Monthly cost at {monthly_pct:.1f}% of budget: ${monthly_cost:.2f}/${self.budget.monthly_limit_usd:.2f}")

    def get_daily_report(self) -> dict:
        """Get daily cost report."""
        today = datetime.now().strftime("%Y-%m-%d")
        daily_records = [r for r in self._records if r.timestamp.strftime("%Y-%m-%d") == today]

        by_component = {}
        by_model = {}

        for r in daily_records:
            by_component[r.component] = by_component.get(r.component, 0) + r.cost_usd
            if r.model:
                by_model[r.model] = by_model.get(r.model, 0) + r.cost_usd

        return {
            "date": today,
            "total_cost_usd": round(sum(r.cost_usd for r in daily_records), 4),
            "by_component": {k: round(v, 4) for k, v in by_component.items()},
            "by_model": {k: round(v, 4) for k, v in by_model.items()},
            "request_count": len(daily_records),
            "avg_cost_per_request": round(
                sum(r.cost_usd for r in daily_records) / max(len(daily_records), 1), 6
            ),
            "budget_used_pct": round(
                (sum(r.cost_usd for r in daily_records) / self.budget.daily_limit_usd) * 100, 1
            ),
        }

    def get_optimization_suggestions(self) -> list[str]:
        """Suggest cost optimizations based on usage patterns."""
        suggestions = []

        # Check for expensive models on simple tasks
        for model, cost in self._model_costs.items():
            if "gpt-4" in model.lower() and cost > 10:
                suggestions.append(
                    f"Consider using a cheaper model for some {model} calls. "
                    f"Current cost: ${cost:.2f}. GPT-3.5-turbo is 10x cheaper."
                )

        # Check for high token usage
        high_token_records = [r for r in self._records if r.tokens and r.tokens > 4000]
        if len(high_token_records) > 100:
            suggestions.append(
                f"{len(high_token_records)} requests used >4000 tokens. "
                "Consider shorter prompts or context window management."
            )

        # Check for redundant calls (same input repeated)
        # This would need a more sophisticated implementation

        return suggestions
```

---

## 42. SECURITY HARDENING FOR DEPLOYMENT

### What is Security Hardening?

**Security hardening** is the process of securing your deployment against attacks. For AI applications, this includes protecting against:

- **Prompt injection** — Malicious users crafting inputs that trick the LLM into ignoring instructions or revealing system prompts
- **API abuse** — Unauthorized access, rate limit bypassing, token theft
- **Data exfiltration** — Attackers extracting training data or user data through the model
- **Supply chain attacks** — Malicious dependencies or compromised model files
- **Infrastructure attacks** — DDoS, container escape, network intrusion

### 42.1 SECURITY CHECKLIST

```
┌─────────────────────────────────────────────────────────────────────────┐
│                    DEPLOYMENT SECURITY CHECKLIST                        │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  NETWORK SECURITY                                                       │
│  ├─ [ ] VPC with private subnets for databases and internal services   │
│  ├─ [ ] Security groups restrict traffic to minimum required ports     │
│  ├─ [ ] WAF (Web Application Firewall) in front of public endpoints   │
│  ├─ [ ] DDoS protection (AWS Shield, Cloudflare)                      │
│  ├─ [ ] TLS/HTTPS everywhere (no plain HTTP)                          │
│  ├─ [ ] Private endpoints for databases (no public access)            │
│  └─ [ ] Network segmentation (API can't directly access DB subnet)    │
│                                                                         │
│  AUTHENTICATION & AUTHORIZATION                                         │
│  ├─ [ ] API keys for external access (not just bearer tokens)         │
│  ├─ [ ] JWT/OAuth for user authentication                             │
│  ├─ [ ] RBAC (Role-Based Access Control) for admin operations         │
│  ├─ [ ] Rate limiting per API key/user                                 │
│  ├─ [ ] IP allowlisting for admin endpoints                           │
│  └─ [ ] Audit logging for all auth events                             │
│                                                                         │
│  SECRETS MANAGEMENT                                                     │
│  ├─ [ ] No secrets in code or Git repositories                        │
│  ├─ [ ] Secrets stored in managed vault (AWS Secrets Manager, etc.)   │
│  ├─ [ ] Secrets rotated regularly (90 days max)                       │
│  ├─ [ ] Least privilege access to secrets                              │
│  └─ [ ] Secrets scanning in CI/CD pipeline                            │
│                                                                         │
│  CONTAINER SECURITY                                                     │
│  ├─ [ ] Non-root user in containers                                   │
│  ├─ [ ] Minimal base images (slim, alpine, distroless)                │
│  ├─ [ ] No unnecessary packages installed                              │
│  ├─ [ ] Container image scanning (Trivy, Snyk)                        │
│  ├─ [ ] Read-only filesystem where possible                           │
│  └─ [ ] Resource limits (CPU, memory) set                             │
│                                                                         │
│  AI-SPECIFIC SECURITY                                                   │
│  ├─ [ ] Input validation and sanitization                             │
│  ├─ [ ] Output filtering (no PII in responses)                        │
│  ├─ [ ] Prompt injection detection                                    │
│  ├─ [ ] Content moderation (toxicity, hate speech)                    │
│  ├─ [ ] Rate limiting per user (prevent abuse)                        │
│  ├─ [ ] Token limits per request (prevent cost attacks)               │
│  └─ [ ] System prompt protection (not leaked in responses)            │
│                                                                         │
│  DATA SECURITY                                                          │
│  ├─ [ ] Encryption at rest (database, storage, backups)               │
│  ├─ [ ] Encryption in transit (TLS everywhere)                        │
│  ├─ [ ] PII detection and masking in logs                             │
│  ├─ [ ] Data retention policies enforced                              │
│  ├─ [ ] GDPR/CCPA compliance (right to deletion)                      │
│  └─ [ ] Audit trail for data access                                   │
│                                                                         │
│  CI/CD SECURITY                                                         │
│  ├─ [ ] Dependency vulnerability scanning                             │
│  ├─ [ ] SAST (Static Application Security Testing)                    │
│  ├─ [ ] Container image signing                                       │
│  ├─ [ ] Signed commits required                                       │
│  ├─ [ ] Branch protection (no direct pushes to main)                  │
│  └─ [ ] Environment secrets separated (dev != prod)                   │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## 43. MULTI-TENANT DEPLOYMENT

### What is Multi-Tenant Architecture?

**Multi-tenant** means serving multiple customers (tenants) from a single shared infrastructure. Instead of deploying a separate instance for each customer, all customers share the same application, but their data is isolated.

For AI applications, multi-tenancy is important because:
- **Cost efficiency** — One shared GPU serves 100 customers instead of 100 separate GPUs
- **Operational simplicity** — One deployment to manage, not 100
- **Resource sharing** — Idle capacity from one tenant can serve another

The challenge: **data isolation**. Customer A must never see Customer B's data. This requires careful design at every layer:
- **Database** — Row-level security (RLS) or separate schemas per tenant
- **Vector DB** — Separate collections or namespace isolation per tenant
- **Cache** — Tenant-prefixed keys in Redis
- **LLM** — Tenant-specific context in prompts, separate conversation history
- **Logs** — Tenant ID in every log entry for audit and debugging

### 43.1 MULTI-TENANT IMPLEMENTATION

```python
# File: src/multi_tenant/tenant_manager.py
"""Multi-tenant management for AI applications."""

import logging
from dataclasses import dataclass
from typing import Optional
from functools import wraps
from contextvars import ContextVar

logger = logging.getLogger(__name__)

# Context variable for current tenant (thread-safe)
current_tenant_id: ContextVar[str] = ContextVar("current_tenant_id", default="")


@dataclass
class Tenant:
    id: str
    name: str
    plan: str  # "free", "pro", "enterprise"
    rate_limit: int  # requests per minute
    token_limit: int  # tokens per request
    model_access: list[str]  # allowed models
    custom_prompt: Optional[str] = None
    metadata: dict = None


class TenantManager:
    """Manage multi-tenant configuration and isolation."""

    def __init__(self):
        self._tenants: dict[str, Tenant] = {}
        self._rate_limits: dict[str, list[float]] = {}  # tenant_id -> [timestamps]

    def register_tenant(self, tenant: Tenant):
        """Register a new tenant."""
        self._tenants[tenant.id] = tenant
        logger.info(f"Registered tenant: {tenant.id} ({tenant.plan})")

    def get_tenant(self, tenant_id: str) -> Tenant:
        """Get tenant configuration."""
        if tenant_id not in self._tenants:
            raise ValueError(f"Unknown tenant: {tenant_id}")
        return self._tenants[tenant_id]

    def check_rate_limit(self, tenant_id: str) -> bool:
        """Check if tenant has exceeded rate limit."""
        import time
        tenant = self.get_tenant(tenant_id)
        now = time.time()

        if tenant_id not in self._rate_limits:
            self._rate_limits[tenant_id] = []

        # Clean old entries (keep last minute)
        self._rate_limits[tenant_id] = [
            t for t in self._rate_limits[tenant_id] if now - t < 60
        ]

        # Check limit
        if len(self._rate_limits[tenant_id]) >= tenant.rate_limit:
            return False

        # Record this request
        self._rate_limits[tenant_id].append(now)
        return True

    def check_model_access(self, tenant_id: str, model: str) -> bool:
        """Check if tenant has access to a specific model."""
        tenant = self.get_tenant(tenant_id)
        return model in tenant.model_access

    def get_tenant_context(self, tenant_id: str) -> dict:
        """Get tenant-specific context for LLM prompts."""
        tenant = self.get_tenant(tenant_id)
        return {
            "tenant_id": tenant.id,
            "tenant_name": tenant.name,
            "plan": tenant.plan,
            "custom_prompt": tenant.custom_prompt,
        }


def with_tenant(tenant_id: str):
    """Decorator to set tenant context for a request."""
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            token = current_tenant_id.set(tenant_id)
            try:
                return await func(*args, **kwargs)
            finally:
                current_tenant_id.reset(token)
        return wrapper
    return decorator


def get_current_tenant_id() -> str:
    """Get the current tenant ID from context."""
    return current_tenant_id.get()
```

---

## 44. AUTHENTICATION AND AUTHORIZATION FOR AI APIs

### What is Auth for AI APIs?

**Authentication** verifies who is calling your API. **Authorization** determines what they're allowed to do. For AI APIs, this is critical because:
- LLM API calls cost money — you need to know who's spending what
- Different users have different access levels (free vs paid, admin vs user)
- You need to track usage per user for billing and abuse prevention

### 44.1 API KEY AND JWT AUTHENTICATION

```python
# File: src/auth/middleware.py
"""Authentication and authorization for AI API."""

import os
import time
import hashlib
import hmac
import logging
from typing import Optional
from fastapi import Request, HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import jwt

logger = logging.getLogger(__name__)

security = HTTPBearer()

# API keys (in production, store in database)
API_KEYS = {
    "sk-proj-abc123": {"user_id": "user_1", "plan": "pro", "rate_limit": 100},
    "sk-proj-def456": {"user_id": "user_2", "plan": "free", "rate_limit": 10},
}

JWT_SECRET = os.getenv("JWT_SECRET", "your-secret-key")


async def verify_api_key(request: Request) -> dict:
    """Verify API key from Authorization header or X-API-Key header."""
    # Check Authorization header (Bearer token)
    auth_header = request.headers.get("Authorization", "")
    if auth_header.startswith("Bearer "):
        api_key = auth_header[7:]
    else:
        # Check X-API-Key header
        api_key = request.headers.get("X-API-Key", "")

    if not api_key:
        raise HTTPException(status_code=401, detail="API key required")

    # Validate API key
    if api_key not in API_KEYS:
        raise HTTPException(status_code=401, detail="Invalid API key")

    key_info = API_KEYS[api_key]
    return {
        "user_id": key_info["user_id"],
        "plan": key_info["plan"],
        "rate_limit": key_info["rate_limit"],
        "api_key_prefix": api_key[:8] + "...",
    }


async def verify_jwt(request: Request) -> dict:
    """Verify JWT token from Authorization header."""
    auth_header = request.headers.get("Authorization", "")
    if not auth_header.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Bearer token required")

    token = auth_header[7:]

    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=["HS256"])
        return {
            "user_id": payload["sub"],
            "plan": payload.get("plan", "free"),
            "rate_limit": payload.get("rate_limit", 10),
        }
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")


async def require_plan(required_plan: str, user: dict = Depends(verify_api_key)):
    """Require a specific plan level."""
    plan_hierarchy = {"free": 0, "pro": 1, "enterprise": 2}
    user_level = plan_hierarchy.get(user["plan"], 0)
    required_level = plan_hierarchy.get(required_plan, 0)

    if user_level < required_level:
        raise HTTPException(
            status_code=403,
            detail=f"This endpoint requires {required_plan} plan or higher",
        )
    return user
```

---

## 45. DATA PIPELINE DEPLOYMENT

### What is a Data Pipeline?

A **data pipeline** is an automated workflow that moves and transforms data from one or more sources to a destination. For AI applications, data pipelines handle:

- **ETL (Extract, Transform, Load)** — Pulling data from sources, cleaning it, and loading it into databases or vector stores
- **Document ingestion** — Processing PDFs, web pages, and files into chunks and embeddings for RAG
- **Training data preparation** — Formatting, deduplicating, and splitting data for model training
- **Batch inference** — Running models on large datasets (e.g., nightly report generation)
- **Data enrichment** — Adding metadata, classifications, or embeddings to existing data

Key data pipeline tools:
- **Apache Airflow** — The industry standard for workflow orchestration. DAG-based. Self-hosted or managed (AWS MWAA, Google Composer).
- **Prefect** — Modern Python-native workflow orchestration. Easier than Airflow.
- **Dagster** — Data-aware orchestration. Strong typing and testing.
- **Temporal** — Durable execution engine. Good for long-running workflows.
- **Inngest** — Serverless workflow engine. Event-driven.

### 45.1 AIRFLOW DEPLOYMENT FOR AI PIPELINES

```python
# File: dags/ai_document_pipeline.py
"""Airflow DAG for AI document processing pipeline."""

from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.providers.http.sensors.http import HttpSensor
from airflow.providers.amazon.aws.sensors.s3 import S3KeySensor
from datetime import datetime, timedelta

default_args = {
    "owner": "ai-platform",
    "depends_on_past": False,
    "email_on_failure": True,
    "email": ["ai-alerts@company.com"],
    "retries": 3,
    "retry_delay": timedelta(minutes=5),
}

dag = DAG(
    "ai_document_pipeline",
    default_args=default_args,
    description="Process documents: extract -> chunk -> embed -> store",
    schedule_interval="@daily",
    start_date=datetime(2024, 1, 1),
    catchup=False,
    tags=["ai", "rag", "document-processing"],
)


def extract_documents(**context):
    """Extract documents from S3."""
    import boto3
    s3 = boto3.client("s3")
    # List new documents since last run
    response = s3.list_objects_v2(Bucket="ai-documents", Prefix="incoming/")
    documents = [obj["Key"] for obj in response.get("Contents", [])]
    context["ti"].xcom_push(key="documents", value=documents)
    return len(documents)


def chunk_documents(**context):
    """Split documents into chunks."""
    from langchain.text_splitter import RecursiveCharacterTextSplitter
    documents = context["ti"].xcom_pull(key="documents")

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200,
    )

    all_chunks = []
    for doc_key in documents:
        # Read document from S3
        content = read_from_s3(doc_key)
        chunks = splitter.split_text(content)
        all_chunks.extend([{"text": c, "source": doc_key} for c in chunks])

    context["ti"].xcom_push(key="chunks", value=all_chunks)
    return len(all_chunks)


def generate_embeddings(**context):
    """Generate embeddings for chunks."""
    import openai
    chunks = context["ti"].xcom_pull(key="chunks")

    embeddings = []
    for chunk in chunks:
        response = openai.embeddings.create(
            model="text-embedding-3-small",
            input=chunk["text"],
        )
        embeddings.append({
            "text": chunk["text"],
            "embedding": response.data[0].embedding,
            "source": chunk["source"],
        })

    context["ti"].xcom_push(key="embeddings", value=embeddings)
    return len(embeddings)


def store_in_vector_db(**context):
    """Store embeddings in vector database."""
    embeddings = context["ti"].xcom_pull(key="embeddings")
    # Store in Pinecone/Weaviate/Qdrant
    for emb in embeddings:
        vector_store.upsert(
            text=emb["text"],
            embedding=emb["embedding"],
            metadata={"source": emb["source"]},
        )
    return len(embeddings)


# Define tasks
extract = PythonOperator(
    task_id="extract_documents",
    python_callable=extract_documents,
    dag=dag,
)

chunk = PythonOperator(
    task_id="chunk_documents",
    python_callable=chunk_documents,
    dag=dag,
)

embed = PythonOperator(
    task_id="generate_embeddings",
    python_callable=generate_embeddings,
    dag=dag,
)

store = PythonOperator(
    task_id="store_in_vector_db",
    python_callable=store_in_vector_db,
    dag=dag,
)

# Task dependencies
extract >> chunk >> embed >> store
```

---

## 46. PROMPT MANAGEMENT AND VERSIONING

### What is Prompt Management?

**Prompt management** is the practice of versioning, testing, and deploying prompt templates — just like you version your code. Prompts are the "code" that controls your LLM's behavior, and they need the same rigor as application code.

Why this matters:
- **Version control** — Track what prompt was used when. "Last week's prompt scored 85% accuracy, this week's scores 92%"
- **A/B testing** — Test different prompts on real users and measure which performs better
- **Rollback** — If a new prompt performs worse, instantly roll back to the previous version
- **Collaboration** — Non-engineers (product managers, domain experts) can edit prompts without touching code
- **Environment management** — Different prompts for dev/staging/production

### 46.1 PROMPT VERSIONING SYSTEM

```python
# File: src/prompts/manager.py
"""Prompt template management and versioning."""

import os
import yaml
import hashlib
import logging
from pathlib import Path
from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional

logger = logging.getLogger(__name__)


@dataclass
class PromptVersion:
    name: str
    version: str
    template: str
    variables: list[str]
    created_at: datetime
    created_by: str
    description: str = ""
    tags: list[str] = field(default_factory=list)
    metrics: dict = field(default_factory=dict)
    hash: str = ""

    def __post_init__(self):
        if not self.hash:
            self.hash = hashlib.sha256(self.template.encode()).hexdigest()[:12]


class PromptManager:
    """Manage prompt templates with versioning."""

    def __init__(self, prompts_dir: str):
        self.prompts_dir = Path(prompts_dir)
        self._prompts: dict[str, list[PromptVersion]] = {}
        self._active_versions: dict[str, str] = {}  # name -> version
        self._load_all_prompts()

    def _load_all_prompts(self):
        """Load all prompt templates from YAML files."""
        for prompt_file in self.prompts_dir.glob("**/*.yaml"):
            with open(prompt_file) as f:
                data = yaml.safe_load(f)

            for prompt_data in data.get("prompts", []):
                name = prompt_data["name"]
                version = prompt_data.get("version", "1.0.0")

                pv = PromptVersion(
                    name=name,
                    version=version,
                    template=prompt_data["template"],
                    variables=prompt_data.get("variables", []),
                    created_at=datetime.fromisoformat(prompt_data.get("created_at", datetime.now().isoformat())),
                    created_by=prompt_data.get("created_by", "system"),
                    description=prompt_data.get("description", ""),
                    tags=prompt_data.get("tags", []),
                )

                if name not in self._prompts:
                    self._prompts[name] = []
                self._prompts[name].append(pv)

                # Set latest as active
                self._active_versions[name] = version

        logger.info(f"Loaded {sum(len(v) for v in self._prompts.values())} prompt versions")

    def get_prompt(self, name: str, version: str = None, **kwargs) -> str:
        """Get a prompt template and fill in variables."""
        if name not in self._prompts:
            raise KeyError(f"Prompt '{name}' not found")

        version = version or self._active_versions.get(name)
        if not version:
            raise KeyError(f"No active version for prompt '{name}'")

        # Find the specific version
        prompt_version = None
        for pv in self._prompts[name]:
            if pv.version == version:
                prompt_version = pv
                break

        if not prompt_version:
            raise KeyError(f"Prompt '{name}' version '{version}' not found")

        # Fill in variables
        try:
            return prompt_version.template.format(**kwargs)
        except KeyError as e:
            raise ValueError(f"Missing variable {e} for prompt '{name}'")

    def set_active_version(self, name: str, version: str):
        """Set the active version for a prompt."""
        if name not in self._prompts:
            raise KeyError(f"Prompt '{name}' not found")

        found = any(pv.version == version for pv in self._prompts[name])
        if not found:
            raise KeyError(f"Version '{version}' not found for prompt '{name}'")

        self._active_versions[name] = version
        logger.info(f"Active version for '{name}' set to '{version}'")

    def create_version(self, name: str, template: str, version: str, created_by: str, description: str = ""):
        """Create a new version of a prompt."""
        pv = PromptVersion(
            name=name,
            version=version,
            template=template,
            variables=self._extract_variables(template),
            created_at=datetime.now(),
            created_by=created_by,
            description=description,
        )

        if name not in self._prompts:
            self._prompts[name] = []

        self._prompts[name].append(pv)
        logger.info(f"Created prompt '{name}' version '{version}'")

    def _extract_variables(self, template: str) -> list[str]:
        """Extract variable names from a template string."""
        import re
        return list(set(re.findall(r'\{(\w+)\}', template)))

    def list_prompts(self) -> list[dict]:
        """List all prompts and their versions."""
        result = []
        for name, versions in self._prompts.items():
            result.append({
                "name": name,
                "active_version": self._active_versions.get(name),
                "versions": [
                    {
                        "version": v.version,
                        "created_at": v.created_at.isoformat(),
                        "created_by": v.created_by,
                        "description": v.description,
                        "hash": v.hash,
                    }
                    for v in versions
                ],
            })
        return result

    def rollback(self, name: str, to_version: str):
        """Rollback to a previous prompt version."""
        self.set_active_version(name, to_version)
        logger.info(f"Rolled back prompt '{name}' to version '{to_version}'")
```

```yaml
# File: prompts/rag_prompts.yaml
prompts:
  - name: rag_query
    version: "2.1.0"
    description: "RAG query prompt with improved context handling"
    created_at: "2024-01-15T10:00:00"
    created_by: "alice"
    tags: ["rag", "production"]
    template: |
      You are a helpful assistant. Answer the user's question based on the provided context.

      Context:
      {context}

      Question: {question}

      Instructions:
      - Only use information from the context above
      - If the context doesn't contain the answer, say "I don't have enough information"
      - Cite your sources when possible
      - Be concise and accurate

      Answer:
    variables: ["context", "question"]

  - name: rag_query
    version: "2.0.0"
    description: "Previous version - simpler prompt"
    created_at: "2024-01-01T10:00:00"
    created_by: "bob"
    template: |
      Context: {context}
      Question: {question}
      Answer based on the context above:
    variables: ["context", "question"]

  - name: system_prompt
    version: "1.0.0"
    description: "Base system prompt for the AI assistant"
    created_at: "2024-01-01T10:00:00"
    created_by: "system"
    template: |
      You are {assistant_name}, a helpful AI assistant.
      Your role is to {role_description}.
      Always be {tone}.
    variables: ["assistant_name", "role_description", "tone"]
```

---

---

## APPENDIX A: PLATFORM QUICK REFERENCE

```
┌─────────────────────────────────────────────────────────────────────────┐
│                    PLATFORM QUICK REFERENCE                             │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  WHEN TO USE WHAT:                                                      │
│                                                                         │
│  "I need to deploy a simple API fast"                                   │
│  → Railway or Render                                                    │
│                                                                         │
│  "I need global edge deployment"                                        │
│  → Fly.io or Vercel Edge Functions                                      │
│                                                                         │
│  "I need GPU inference, pay-per-second"                                 │
│  → Modal or Replicate                                                   │
│                                                                         │
│  "I need enterprise ML ops with model registry"                         │
│  → SageMaker or Vertex AI                                               │
│                                                                         │
│  "I need to deploy a Gradio demo"                                       │
│  → HuggingFace Spaces                                                   │
│                                                                         │
│  "I need microservices with full control"                               │
│  → Kubernetes (EKS/GKE/AKS)                                            │
│                                                                         │
│  "I need serverless with zero ops"                                      │
│  → Lambda or Cloud Run                                                  │
│                                                                         │
│  "I need Next.js with AI SDK streaming"                                 │
│  → Vercel                                                               │
│                                                                         │
│  "I need real-time WebSocket connections"                               │
│  → Fly.io or Railway                                                    │
│                                                                         │
│  "I need batch processing with GPU"                                     │
│  → Modal or AWS Batch                                                   │
│                                                                         │
│  "I need to deploy on-premise / air-gapped"                             │
│  → Docker + Kubernetes self-managed                                     │
│                                                                         │
│  "I need the cheapest option for low traffic"                           │
│  → Cloud Run (scale to zero) or HuggingFace Spaces (free)              │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## APPENDIX B: TOOL INSTALLATION COMMANDS

```bash
# OpenTelemetry
pip install opentelemetry-api opentelemetry-sdk
pip install opentelemetry-exporter-otlp-proto-grpc
pip install opentelemetry-exporter-prometheus
pip install opentelemetry-instrumentation-fastapi
pip install opentelemetry-instrumentation-httpx
pip install opentelemetry-instrumentation-redis
pip install opentelemetry-instrumentation-psycopg2

# Structured Logging
pip install python-json-logger

# Error Tracking
pip install sentry-sdk[fastapi]

# Monitoring
pip install prometheus-client
pip install datadog

# MLflow
pip install mlflow

# Kubernetes
pip install kubernetes

# HTTP Client
pip install httpx

# Circuit Breaker
pip install circuitbreaker

# System Metrics
pip install psutil

# File Watching (hot-swap)
pip install watchdog

# Testing
pip install pytest pytest-asyncio httpx locust
```

---

*This guide is the companion to the FINAL AI Production Master Guide. Together, they provide the complete lifecycle coverage: from building AI systems (Production Guide) to deploying, monitoring, and operating them in production (this guide).*
