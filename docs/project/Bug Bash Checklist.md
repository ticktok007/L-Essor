# Bug Bash Checklist — Backend v1.0

| ID | Category | Item | Status |
|:---|:---|:---|:---|
| **1.0** | **Auth** | JWT Login returns access/refresh tokens | [ ] |
| 1.1 | Auth | Expired tokens return 401 Unauthorized | [ ] |
| 1.2 | Auth | IsStudentSelf prevents Student A editing Profile B | [ ] |
| **2.0** | **CRUD** | Profile update correctly updates `skills` JSON | [ ] |
| 2.1 | CRUD | Startup creation defaults to 'Idea' stage | [ ] |
| 2.2 | CRUD | Interaction creation triggers FK validation | [ ] |
| **3.0** | **Dash** | `/my/` returns personal metrics for Student | [ ] |
| 3.1 | Dash | `/my/` returns aggregate counts for Leadership | [ ] |
| **4.0** | **AI/ML** | Investor match returns pgvector similarity results | [ ] |
| 4.1 | AI/ML | Prediction endpoint handles null features gracefully | [ ] |
| **5.0** | **Graph** | `/graph/ecosystem/` returns valid Node/Edge list | [ ] |
| **6.0** | **Docs** | Swagger UI loads at `/api/docs/` | [ ] |
| 6.1 | Docs | All example payloads match current models | [ ] |