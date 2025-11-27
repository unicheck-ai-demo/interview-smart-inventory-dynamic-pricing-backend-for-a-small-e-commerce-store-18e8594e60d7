# Django Interview

Welcome to the live‑coding stage of our hiring process.
You will work on a compact yet production‑style Django REST project. Issues reported by product, marketing, and finance have been turned into auto-tests.

**Your goal is to address those issues and keep all tests green.**

### What's included

- A ready‑to‑run Django application.
- Pre‑configured infrastructure (PostgreSQL, Redis, Docker, devcontainer).
- A comprehensive test suite. All tests should stay green.

## Business stories to address

[See the task list](docs/tasks.md)

## Requirements
- All tests must be successfully passed. For `tests/interview/`, the removal of the decorator `@pytest.mark.xfail` is mandatory.
- Your solution will be evaluated externally. In addition to test results, the following aspects will be considered:
    - code quality and style
    - architectural and implementation decisions
    - adherence to industry best practices
    - the amount of time invested in completing the task
- Creative solutions are welcome if they meet quality standards.

### ⏱ Time‑box

The task is designed to be solved not more than **1 hour**. Focus on clear, incremental fixes.
One hour after the start, access to the interview will be closed.

### Helpful commands

Use the terminal to run:

- `make interview` to run interview tests to check your solutions.
- `make test` to run common project tests to ensure that common features are still working.
- `make lint` to run linters and formatters.
- see more useful commands in the `Makefile`.

Good luck and enjoy!

## About Project

A production‑like Django backend service for a small to mid‑size online store selling niche products (e.g., artisanal kitchenware). The system handles product catalog management, user orders, inventory levels, supplier restocking workflows, and applies dynamic pricing strategies. It integrates with a third‑party currency exchange API to support multi‑currency prices and uses Redis caching to accelerate product listing responses. PostgreSQL (with possible PostGIS for location of suppliers) serves as the main relational database with complex queries for analytics and stock checks. The goal is to simulate realistic tasks for a Junior Backend Engineer, testing competencies in schema design, API building, caching, and safe concurrent updates.

[see more details](docs/)

### Tech Stack

- Python: 3.11
- Django: 4
- API: Django REST Framework
- Database: PostgreSQL 15
- Caching: Redis 7
- Testing: Pytest, Pytest-Django
- Dependency Management: `requirements.txt`


### Project Structure Overview
```bash
> tree -a --gitignore /app 
.
├── .env.example
├── Dockerfile
├── Makefile
├── README.md
├── app
│   ├── admin.py
│   ├── api
│   │   ├── exceptions.py
│   │   ├── pagination.py
│   │   ├── permissions.py
│   │   ├── serializers.py
│   │   ├── urls.py
│   │   └── views.py
│   ├── apps.py
│   ├── migrations
│   │   └── 0001_initial.py
│   ├── models.py
│   ├── services.py
│   └── tasks.py
├── config
│   ├── asgi.py
│   ├── celery.py
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
├── docker-compose.yml
├── docs
│   └── README.md
├── infra
│   └── Dockerfile
├── manage.py
├── pyproject.toml
├── requirements.txt
└── tests
    ├── api
    │   ├── test_api.py
    │   └── test_heapth.py
    ├── app
    │   ├── test_models.py
    │   └── test_services.py
    └── conftest.py

10 directories, 32 files

```

---
Contact: [info@unicheck.ai](mailto:info@unicheck.ai)