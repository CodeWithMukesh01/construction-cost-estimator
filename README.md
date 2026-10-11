# Construction Cost Estimator & Contractor Matching

Homeowners often can't judge whether a construction quote is fair, and finding a
trustworthy contractor depends on word of mouth. This web app gives an itemised cost
estimate in seconds, then lets the homeowner request quotes from verified companies and
compare them side by side.

Supports **SDG 11: Sustainable Cities and Communities**.

## Features

- **Cost estimator:** plot size, floors and finish level give an itemised cost range
- **PDF report:** download the itemised estimate
- **Verified company directory** with city search; an admin verifies each company
- **Company accounts:** registration, login and a dashboard showing the requests received
- **Quote requests:** send one project to several companies at once
- **Quote comparison:** compare quotes side by side, with the lowest highlighted and the gap to the estimate shown
- **Admin analytics dashboard:** estimates per week, quote response rate, average quotes per project and more
- **Admin-managed rates:** material and labour rates are updated from the Django admin

## Tech stack

| Layer | Technology |
|---|---|
| Backend | Python, Django, Django REST Framework |
| Database | PostgreSQL |
| Frontend | HTML, CSS, JavaScript |
| Auth | Token authentication |
| PDF | ReportLab |
| Charts | Chart.js |

## Project structure

```
construction-estimator/
├── backend/
│   ├── config/        project settings and URLs
│   ├── estimator/     cost rates, estimate API, PDF, analytics
│   ├── companies/     companies, quote requests, login, comparison
│   └── manage.py
└── frontend/
    ├── index.html     estimator and company list
    ├── register.html  company registration
    ├── dashboard.html company login and quote entry
    ├── compare.html   quote comparison
    └── admin.html     analytics dashboard
