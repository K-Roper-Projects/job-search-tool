# Job Search Tool

**A Python-based job aggregation and career matching platform for the UK job market.**

A self-hosted application designed to automate job discovery, consolidate vacancies from multiple sources, and identify relevant career opportunities using configurable search criteria, professional experience, technical skills and project evidence.

The project focuses on **automation, modular architecture, security-by-design, data privacy and minimal operating costs**.

**Development status:** Phase 1A — Project Foundation & Reed API Integration (in progress).

---

## 1. Project Overview

Searching for suitable technical roles often involves repeatedly checking recruitment websites, reviewing duplicate advertisements and manually comparing job requirements against professional experience.

The Job Search Tool aims to reduce this repetitive work by bringing job discovery, filtering, candidate matching and reporting into a single automated workflow.

Initially focused on UK-based Cloud Engineering, DevOps, Platform Engineering and Infrastructure roles, the application is designed to support configurable searches across other career disciplines.

### Project Objectives

- **Centralised job discovery:** Retrieve vacancies from supported recruitment APIs and employer job boards.
- **Standardised job data:** Convert provider-specific responses into a consistent internal Python model.
- **Automated matching:** Evaluate opportunities against job preferences, professional experience, technical skills and project evidence.
- **Duplicate detection:** Identify vacancies advertised across multiple providers.
- **Persistent storage:** Maintain a local SQLite database of discovered vacancies.
- **Automated notifications:** Deliver ranked opportunities through configurable email reports.
- **CV tailoring:** Support evidence-based, role-specific CV drafts using verified candidate information.
- **Privacy and security:** Protect credentials, candidate records and application data.
- **Low-cost operation:** Prioritise free API access, open-source dependencies and existing self-hosted infrastructure.

The long-term objective is to develop a reliable, extensible job discovery platform that reduces manual searching while retaining transparency and control over candidate information.

---

## 2. System Architecture

The application follows a modular design, separating external data collection from processing, storage, matching and reporting.

### Planned Application Architecture

```text
                   EXTERNAL JOB SOURCES
                            |
          +-----------------+-----------------+
          |                 |                 |
       Reed API         Adzuna API       Employer ATS
                                           Boards
                                     Greenhouse / Lever
                                            Ashby
          |                 |                 |
          +-----------------+-----------------+
                            |
                            v
                    PROVIDER LAYER
                 Provider-specific adapters
                    Shared HTTP client
                 Timeouts / Retries / Limits
                            |
                            v
                    DATA NORMALISATION
                      Standard Job Model
                            |
                            v
                    DATA PROCESSING
                  Validation / Deduplication
                            |
                            v
                      SQLite Database
                            |
                            v
                      MATCHING ENGINE
                  Configured job criteria
                    Professional history
                    Skills / Project work
                            |
                            v
                     RANKED VACANCIES
                            |
                 +----------+----------+
                 |                     |
                 v                     v
           Email Reports          CV Tailoring
           Notifications          Draft Generation
```

All external providers return data through a common application model, allowing downstream components to operate independently of individual API structures.

### Architectural Components

| Component | Responsibility |
|---|---|
| Provider interfaces | Define contracts for external job data retrieval |
| Provider adapters | Translate individual API responses into standardised job records |
| Shared HTTP client | Manage external requests, timeouts, retries and rate-limit responses |
| Normalised Job model | Represent vacancies consistently across providers |
| Validation layer | Validate and safely process untrusted external data |
| SQLite storage | Persist job records and ingestion metadata |
| Deduplication engine | Identify duplicate vacancies across providers |
| Matching engine | Evaluate jobs against candidate criteria and professional evidence |
| Reporting engine | Generate ranked vacancy summaries |
| Notification service | Deliver scheduled email reports |
| Candidate profile | Maintain private CV, experience, skills and project records |
| CV tailoring | Generate role-specific drafts using verified information |

**Implementation status:** The normalised Job model and provider interfaces are complete. The remaining components are planned.

---

## 3. Job Data Sources

The platform supports two planned methods of vacancy discovery.

### Recruitment Search APIs

Search APIs accept criteria such as job title, location and other supported filters, returning advertisements from multiple employers.

Initial integrations:

- Reed
- Adzuna

### Employer Applicant Tracking Systems

Applicant Tracking Systems (ATS) provide recruitment infrastructure for individual employers.

Planned integrations:

- Greenhouse
- Lever
- Ashby

The application will retrieve vacancies from configured employer boards and perform its own filtering and matching.

### Provider Abstraction

The provider architecture defines three capabilities:

| Interface | Purpose |
|---|---|
| `SearchProvider` | Search vacancies using supplied criteria |
| `EmployerBoardProvider` | Retrieve vacancies from an employer's job board |
| `JobDetailProvider` | Retrieve additional information for an individual vacancy |

A provider may implement multiple capabilities depending on its API.

All retrieved vacancies are converted into the common `Job` model before further processing.

---

## 4. Technology Stack

### Current Technologies

| Technology | Purpose |
|---|---|
| Python 3.14 | Application development |
| Git / GitHub | Source control |
| Visual Studio Code | Development environment |
| Ubuntu VM | Primary application execution environment |
| Python virtual environment | Dependency isolation |

### Planned Technologies

| Technology | Purpose |
|---|---|
| SQLite | Local database |
| HTTP/JSON APIs | Job data ingestion |
| pytest | Automated testing |
| SMTP | Email notifications |
| Linux scheduling | Unattended execution |
| Docker | Optional future containerisation |
| CI workflows | Automated validation and security checks |

Additional dependencies will be introduced as implementation requirements are confirmed.

---

## 5. Development Roadmap

Development follows an incremental approach, with each stage producing a testable and documented outcome.

### Phase 1 — Foundation and Initial Job Ingestion

**Objective:** Establish the application foundation and retrieve real vacancies from the Reed API.

| Checkpoint | Deliverable | Status |
|---|---|---|
| 1A.1 | Python environment | Complete |
| 1A.2 | Project structure | Complete |
| 1A.3 | Git ignore rules and safe configuration foundation | Complete |
| 1A.4 | Normalised Job model | Complete |
| 1A.5 | Provider interfaces | Complete |
| 1A.6 | Shared HTTP client | Planned |
| 1A.7 | Reed API configuration | Planned |
| 1A.8 | Reed provider implementation | Planned |
| 1A.9 | First live API request | Planned |
| 1A.10 | SQLite persistence | Planned |
| 1A.11 | Query stored vacancies | Planned |
| 1A.12 | Testing and documentation | Planned |

**Milestone:** Retrieve, normalise, store and query real UK job advertisements.

Security considerations:
- HTTPS communication with certificate validation.
- API credentials stored outside source control.
- Timeouts and controlled retry behaviour.
- Validation of external API responses.
- Restricted local file permissions.
- No unnecessary inbound network services.

### Phase 2 — Additional Job Sources

**Objective:** Expand vacancy coverage using multiple independent providers.

Planned work:
- Adzuna integration.
- Greenhouse, Lever and Ashby employer-board integrations.
- Configurable search and employer watchlists.
- Pagination and API usage tracking.
- Cross-provider duplicate detection.
- Provider error handling and logging.

Security considerations:
- Provider-specific API usage policies.
- Input validation and response-size limits.
- Dependency vulnerability checks.
- Safe handling of untrusted external content.

**Milestone:** Consolidate vacancies from multiple providers into a consistent local dataset.

### Phase 3 — Candidate Profile and Matching Engine

**Objective:** Identify vacancies relevant to professional experience and career objectives.

Planned work:
- Configurable job preferences.
- Private master CV and candidate profile.
- Technical skills and project evidence mapping.
- Salary, location, employment type and workplace matching.
- Explainable matching scores.
- Identification of missing or uncertain job requirements.

Security considerations:
- Candidate records excluded from Git.
- Restricted filesystem permissions.
- Data minimisation and controlled retention.
- Separation of candidate information from public configuration.

**Milestone:** Generate ranked vacancy shortlists with transparent matching explanations.

### Phase 4 — Automated Reporting and Notifications

**Objective:** Deliver relevant job opportunities without repeated manual searching.

Planned work:
- Scheduled ingestion and matching.
- Daily or configurable job reports.
- Email notifications.
- Vacancy links and matching explanations.
- Duplicate notification suppression.
- Execution logging and reporting history.
- Optional Dad Joke of the Day in email summaries.

Security considerations:
- Protected SMTP credentials.
- Safe formatting of untrusted job descriptions.
- Prevention of accidental disclosure of candidate information.
- Avoidance of sensitive information in logs.

**Milestone:** Deliver ranked opportunities through automated notifications.

### Phase 5 — CV Tailoring and Application Support

**Objective:** Support accurate, role-specific application preparation.

Planned work:
- Job description analysis.
- Comparison against master CV and project evidence.
- Relevant skills and achievements identification.
- Tailored CV draft generation.
- Human review and approval.
- Optional AI-assisted drafting.

Security considerations:
- No fabricated qualifications or experience.
- Protection of candidate information.
- Treat job descriptions as untrusted input.
- Review data handling before using external AI services.
- Keep the core platform operational without paid AI services.

**Milestone:** Produce evidence-based application drafts.

### Phase 6 — Operational Improvements and Deployment

**Objective:** Improve reliability, maintainability and operational security.

Potential enhancements:
- Docker-based deployment.
- Automated tests and CI workflows.
- Monitoring and health checks.
- Backup and recovery procedures.
- Optional web dashboard.
- Application configuration improvements.
- Additional provider integrations.
- Infrastructure security review.

**Milestone:** Operate the application reliably as a self-hosted service.

Roadmap phases beyond Phase 1 remain provisional and may evolve as implementation progresses.

---

## 6. Repository Structure

Current and planned initial structure:

```text
job-search-tool/
├── app/
│   ├── __init__.py
│   ├── models/
│   │   ├── __init__.py
│   │   └── job.py
│   └── providers/
│       ├── __init__.py
│       └── base.py
├── config/
├── data/
├── tests/
├── .gitignore
└── README.md
```

Empty directories may not appear in GitHub until tracked files are added.

Additional modules will be introduced as development progresses.

---

## 7. Development Environment

The application is developed on an Ubuntu virtual machine, with Visual Studio Code running on a Windows workstation and connecting to the VM through Remote SSH.

The Ubuntu VM uses a bridged network adapter and receives its own IP address on the home network.

The application is intended to run locally without exposing a public application endpoint.

### Clone the Repository

```bash
git clone https://github.com/K-Roper-Projects/job-search-tool.git
cd job-search-tool
```

Public repositories can be viewed and cloned without authentication. Only authorised users can push changes to the repository.

### Create a Python Virtual Environment

```bash
python3 -m venv .venv
source .venv/bin/activate
```

Verify Python:

```bash
python --version
```

The current development environment uses Python 3.14.

### Current Validation

```bash
python -m py_compile app/models/job.py
python -m py_compile app/providers/base.py
```

These commands check Python compilation but do not replace automated functional testing.

Application execution instructions will be added once live API ingestion has been implemented.

---

## 8. Security Architecture and Data Privacy

Security is a core design requirement rather than a feature reserved for deployment.

The application will process external job information and eventually store private candidate records and service credentials.

These assets require protection at the network, operating-system, application and data layers.

### 8.1 Security Model

The initial application is designed to operate as a local, outbound-only client.

It will initiate HTTPS requests to external job providers and will not require a publicly accessible web server.

```text
                  INTERNET
                     |
              External Job APIs
                     |
                HTTPS / TLS
                     |
              Home Router
                     |
              Home Network
                     |
              Ubuntu VM
                     |
              Python Application
                     |
          +----------+----------+
          |                     |
       SQLite             Private Files
       Database            Credentials / CV
```

This diagram represents the current logical deployment model, not a guarantee that all traffic passes through a dedicated firewall.

### 8.2 Network Security

The Ubuntu VM currently uses bridged networking, giving it its own address on the local network.

Planned network protections include:

- No unnecessary inbound application ports.
- No router port forwarding to the application.
- Restricted SSH access.
- Host firewall rules appropriate to the VM's role.
- Network isolation where practical.
- Controlled outbound access to required external services.

A dedicated OPNsense firewall is being prepared as part of the wider HomeLab infrastructure.

**OPNsense status: Installed and initially commissioned; network integration and security policy configuration pending.**

Once deployed, the firewall may provide additional network segmentation, traffic filtering and visibility.

The network topology must ensure that relevant application traffic actually traverses OPNsense before its rules can provide protection.

### 8.3 Operating System and VM Security

The Ubuntu environment will follow least-privilege principles.

Planned controls:
- Execute the application as a non-root user.
- Keep the operating system and dependencies updated.
- Use SSH key-based authentication.
- Restrict sensitive file permissions.
- Avoid unnecessary services and privileged access.
- Maintain appropriate backups and recovery procedures.
- Avoid granting the application access to unrelated HomeLab services.

### 8.4 Application Security

External API responses and job descriptions are considered untrusted input.

Planned controls:
- HTTPS with certificate validation.
- Request timeouts.
- Controlled retries and rate-limit handling.
- Input and response validation.
- Response-size limits where practical.
- Parameterised SQLite queries.
- Safe error handling.
- Dependency vulnerability scanning.
- Automated security checks where appropriate.

Job advertisement content must never be treated as executable code or trusted instructions.

### 8.5 Credential Management

API keys, email credentials and other secrets will be stored outside version control.

The `.gitignore` configuration excludes environment files and other sensitive local paths.

Additional safeguards will include:
- Restricted filesystem permissions.
- No hard-coded credentials.
- No secrets in application logs.
- Credential rotation when necessary.
- Separate configuration templates containing placeholders only.

**Important:** `.gitignore` prevents accidental Git tracking of matching untracked files. It does not encrypt data or secure files against local access.

### 8.6 Candidate Data Protection

The application will eventually maintain private candidate information, including a master CV, employment history, skills and project evidence.

Planned protections include:
- Private local storage.
- Exclusion from public source control.
- Restricted filesystem access.
- Avoidance of unnecessary personal information in logs.
- Controlled data retention.
- Human review before application documents are generated or shared.

### 8.7 Defence in Depth

Security will be maintained through multiple independent layers:

1. Network and firewall controls.
2. Host and virtual machine hardening.
3. Application-level input and dependency security.
4. Credential and candidate-data protection.
5. Monitoring, backup and recovery procedures.

A compromise of one layer should not automatically provide unrestricted access to the others.

**Current security status:** Repository ignore rules and local development isolation are established. Additional application and infrastructure controls will be implemented and verified incrementally.

---

## 9. Design Principles

**Modularity:** Keep provider integrations, storage, matching and reporting independent.

**Extensibility:** Support additional APIs without redesigning the application.

**Security by design:** Consider threats, trust boundaries and sensitive data throughout development.

**Least privilege:** Grant processes and users only the permissions required.

**Data integrity:** Handle incomplete vacancy information without inventing missing details.

**Explainability:** Make job matching decisions understandable and evidence-based.

**Privacy:** Keep credentials and candidate information outside public source control.

**Cost awareness:** Prefer free API tiers, open-source components and existing infrastructure.

**Incremental delivery:** Implement, validate, document and commit each development milestone.

---

## 10. Current Project Status

**Phase 1A.5 — Complete**

Implemented:
- Python project foundation.
- Virtual environment.
- Git repository and ignore rules.
- Normalised `Job` dataclass.
- Employment and workplace type enumerations.
- Provider capability flags.
- Abstract provider interfaces.
- Initial provider contract validation.

**Next milestone: Phase 1A.6 — Shared HTTP Client.**

The application does not yet retrieve live vacancies, maintain a job database, calculate matching scores or send notifications.

These capabilities will be introduced through the development roadmap.

---

*This project is under active development. Architecture, security controls and roadmap priorities will evolve as new integrations and functionality are introduced.*