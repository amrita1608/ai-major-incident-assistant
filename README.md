# Incident AI Analyzer

An AI-assisted incident analysis tool that analyzes major IT incidents using incident summaries, alerts, logs, and knowledge base (KB) articles.

The goal is to help incident management and support teams quickly identify probable root causes, find relevant historical knowledge, recommend possible workarounds, and prepare stakeholder communication.

> **Project status:** Initial project structure / Proof of Concept

---

## Overview

During a major incident, support and operations teams often need to analyze information from multiple sources:

- Incident summary
- Monitoring alerts
- Application and infrastructure logs
- Historical knowledge base (KB) articles
- Previous incident information

This project brings these inputs together and uses AI-assisted analysis to produce a structured incident assessment.

### Expected analysis flow

```text
Incident Summary
       +
     Alerts
       +
      Logs
       |
       v
+---------------------+
| Symptom Extraction  |
+---------------------+
       |
       v
+---------------------+
| KB Search & Matching|
+---------------------+
       |
       v
+---------------------+
| Root Cause Analysis |
+---------------------+
       |
       +------------------+
       |                  |
       v                  v
  Workaround        Confidence Score
       |                  |
       +--------+---------+
                |
                v
     Stakeholder Communication
                |
                v
        Incident Summary
        Draft Email
```

---

## Key Capabilities

The planned system will provide:

1. **Incident ingestion**
   - Parse incident summaries and metadata.
   - Validate incident input against a defined schema.

2. **Alert analysis**
   - Process monitoring and system alerts.
   - Identify relevant alerts associated with the incident.

3. **Log analysis**
   - Process relevant log snippets.
   - Extract error messages, timestamps, and useful symptoms.

4. **Knowledge Base matching**
   - Search available KB articles.
   - Identify articles with symptoms matching the incident.
   - Rank potentially relevant KB articles.

5. **Root cause analysis**
   - Combine incident symptoms, alerts, logs, and KB evidence.
   - Generate a probable root cause.
   - Provide supporting evidence.

6. **Workaround analysis**
   - Identify possible workarounds from relevant KB information.
   - Clearly distinguish known workarounds from AI-generated recommendations.

7. **Confidence assessment**
   - Provide a confidence level for the analysis.
   - Identify situations where additional investigation is required.

8. **Stakeholder communication**
   - Generate a concise incident summary.
   - Draft stakeholder communication based on the available evidence.

---

## Important Design Principle

This project is intended to be an **AI-assisted decision-support tool**, not an autonomous incident-resolution system.

The AI should not blindly invent a root cause or workaround.

The analysis should be based on available evidence such as:

- Incident symptoms
- Monitoring alerts
- Log messages
- Matching KB articles
- Historical incident information

The generated result should clearly distinguish between:

- **Observed evidence**
- **Known information from KB**
- **Probable root cause**
- **AI inference**
- **Recommended workaround**
- **Confidence level**

Human validation should remain part of the incident-management process.

---

## Repository Structure

```text
incident-ai-analyzer/
│
├── README.md
├── LICENSE
├── .gitignore
├── .env.example
├── requirements.txt
├── pyproject.toml
│
├── config/
│   ├── config.yaml
│   └── kb_sources.yaml
│
├── prompts/
│   ├── symptom_matching.txt
│   ├── kb_analysis.txt
│   ├── root_cause_analysis.txt
│   ├── workaround_generation.txt
│   └── stakeholder_email.txt
│
├── src/
│   └── incident_analyzer/
│       ├── ingestion/
│       ├── kb/
│       ├── analysis/
│       ├── communication/
│       ├── llm/
│       ├── models/
│       ├── cli.py
│       └── pipeline.py
│
├── data/
│   ├── incidents/
│   ├── alerts/
│   ├── logs/
│   └── kb/
│
├── schemas/
│   ├── incident.schema.json
│   ├── alert.schema.json
│   ├── kb_article.schema.json
│   └── analysis_result.schema.json
│
├── tests/
│   ├── unit/
│   ├── integration/
│   └── fixtures/
│
├── evals/
│   ├── evaluation_cases/
│   ├── expected_results/
│   └── README.md
│
├── output/
│
├── docs/
│   ├── architecture.md
│   ├── workflow.md
│   ├── input-format.md
│   ├── kb-integration.md
│   ├── analysis-methodology.md
│   └── security.md
│
└── .github/
    └── workflows/
        ├── tests.yml
        └── incident-analysis.yml
```

---

## Input

The system is expected to accept structured incident information containing information such as:

```text
Incident ID
Incident title
Incident description
Impact
Start time
Affected service
Alerts
Log snippets
Environment
Severity
```

Example:

```json
{
  "incident_id": "INC001",
  "title": "Payment API failures",
  "severity": "SEV1",
  "service": "payment-api",
  "description": "Customers are receiving HTTP 500 errors during payment processing.",
  "environment": "production"
}
```

The exact input format is defined in:

```text
schemas/incident.schema.json
```

See `docs/input-format.md` for additional information.

---

## Knowledge Base

The initial proof of concept uses Markdown files as sample KB articles.

Example:

```text
data/kb/
├── kb_001.md
├── kb_002.md
└── kb_003.md
```

A KB article may contain:

```text
Title
Symptoms
Affected Service
Error Messages
Possible Cause
Resolution
Workaround
Environment
Related Alerts
```

The KB layer is designed so that it can eventually be extended to external knowledge sources.

Potential future integrations include:

- Internal knowledge repositories
- Service management platforms
- Documentation systems
- Incident history
- Wiki platforms

---

## Expected Output

The analyzer is expected to produce a structured result similar to:

```text
Incident: INC001

Symptoms:
- HTTP 500 errors
- Payment transactions failing
- Increased application error rate

Matching KB Articles:
1. KB-001 - Payment API database connection failures
2. KB-003 - Payment service timeout errors

Probable Root Cause:
Database connection pool exhaustion.

Evidence:
- Increased database connection errors
- Matching symptoms in KB-001
- Application logs showing connection failures

Recommended Workaround:
Restart affected application instances and increase available
database connections after validating database capacity.

Confidence:
High

Stakeholder Summary:
Payment transactions are currently impacted...

Stakeholder Email:
[Generated draft]
```

The actual output format will be defined in:

```text
schemas/analysis_result.schema.json
```

---

## Project Architecture

The project is organized into separate layers.

### Ingestion

Responsible for processing:

- Incident data
- Alerts
- Logs

### Knowledge Base

Responsible for:

- Loading KB articles
- Searching KB content
- Matching incident symptoms
- Ranking relevant articles

### Analysis

Responsible for:

- Symptom analysis
- Root cause analysis
- Workaround analysis
- Confidence scoring

### LLM

Responsible for:

- LLM API interaction
- Prompt management
- Structured AI responses

### Communication

Responsible for:

- Incident summaries
- Stakeholder email generation

### Pipeline

The pipeline orchestrates the complete analysis process.

---

## Development Roadmap

### Phase 1 — Project Setup

- [x] Define repository structure
- [ ] Add input schemas
- [ ] Add sample incident data
- [ ] Add sample alert data
- [ ] Add sample logs
- [ ] Add sample KB articles

### Phase 2 — Data Processing

- [ ] Implement incident parser
- [ ] Implement alert parser
- [ ] Implement log parser
- [ ] Validate input data

### Phase 3 — KB Analysis

- [ ] Implement KB loader
- [ ] Implement symptom matching
- [ ] Implement KB ranking
- [ ] Add KB integration interface

### Phase 4 — AI Analysis

- [ ] Implement LLM client
- [ ] Implement prompt manager
- [ ] Implement root cause analysis
- [ ] Implement workaround generation
- [ ] Implement confidence assessment

### Phase 5 — Communication

- [ ] Generate incident summary
- [ ] Generate stakeholder email
- [ ] Add structured output

### Phase 6 — Testing

- [ ] Unit tests
- [ ] Integration tests
- [ ] End-to-end test
- [ ] AI evaluation cases

### Phase 7 — GitHub Automation

- [ ] Run automated tests using GitHub Actions
- [ ] Run incident analysis using GitHub Actions
- [ ] Store analysis output as workflow artifacts
- [ ] Add configurable AI provider

---

## Security Considerations

Incident data may contain sensitive information.

Do not commit:

- API keys
- Passwords
- Access tokens
- Production credentials
- Personally identifiable information
- Confidential production logs
- Sensitive customer information

Use environment variables or GitHub Actions Secrets for credentials.

See:

```text
docs/security.md
```

for additional security guidelines.

---

## Disclaimer

This project is intended for incident-analysis assistance and experimentation.

AI-generated root causes, workarounds, and communications should be reviewed by an appropriate technical or incident-management team before being used in a production incident.

---

## License

This project is licensed under the MIT License.
See `LICENSE` for details.
