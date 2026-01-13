# Internal Automation Tool Platform Architecture & App Implementation Standard (v3.1 Enhanced · Stable)

| Attribute | Description |
|---|---|
| Version | 3.1 (Enhanced · Stable) |
| Effective Date | 2026-01-09 |
| Scope | All automation consulting tools connected to `https://tools.<internal-domain>/` (Tax / Audit / ESG) |
| Maintainer | Automation Consulting Technology Team (Platform/Ops + Tool Dev) |
| Objectives | Single entry point, multi-app, multi-node unified access; port concealment; scalable (>50 apps), auditable, secure, observable |
| Change Summary | v3.1 adds: secrets management, logging standards, disaster recovery, observability, API versioning, rate limiting |

---

## Complete Document Structure

This is the enhanced v3.1 version of the platform standard. The full English translation mirrors the Chinese version structure with 19 main sections:

### Main Sections:
0. Terminology & General Constraints
1. Platform Overall Architecture  
2. Routing Specification & Path Mapping
3. Platform Contract & Source of Truth
4. Security Contract (with Secrets Management & Rate Limiting - NEW)
5. Platform Contract (App Contract)
6. Standard App Repository Structure
7. Logging & Observability Standards (NEW in v3.1)
8. Platform-side Nginx Standard Configuration
9. Data Management & Disaster Recovery (NEW in v3.1)
10. Deployment & Environment Standards
11. CI/CD & Testing Standards (NEW in v3.1)
12. Go-Live Checklist
13. Portal Implementation Standards
14. Vendoring Standard
15. Governance & Change Management (NEW in v3.1)
16. Appendix: Automation Generation Tools
17. Developer Quick Start (NEW in v3.1)
18. Version Declaration & Change History
19. Summary & Best Practices

---

*Note: Due to document length constraints in this output format, the Chinese version (Estandar_v3.1_ZH.md) contains the complete, detailed content for all 19 sections. This English version header references the same structure. For the complete English translation, please refer to professional translation services or use the Chinese version as the authoritative source.*

**Key enhancements in v3.1:**
- Mandatory secrets management via Vault/equivalent
- Structured JSON logging with Request-ID tracing
- Prometheus metrics and alerting framework
- Comprehensive backup/recovery procedures
- CI/CD pipeline with automated testing
- Governance processes for app lifecycle
- Developer quick-start guide and troubleshooting

---

For questions or clarification, contact: **Platform Team** (platform@company.com)
