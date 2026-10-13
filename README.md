# BuildWise: Construction Cost Estimator & Contractor Matching

Homeowners often can't judge whether a construction quote is fair, and finding a
trustworthy contractor depends on word of mouth. BuildWise gives an itemised cost
estimate in seconds, then lets the homeowner request quotes from verified companies and
compare them side by side.

Supports **SDG 11: Sustainable Cities and Communities**.

  **Live demo:** [construction-estimator-01.netlify.app](https://construction-estimator-01.netlify.app)

## Screenshots

## Screenshots

### Home and cost estimator
![Home page](screenshots/m1.jpg)

### Itemised cost estimate
![Estimate result](screenshots/m2.png)

### Find verified companies and request quotes
![Company search](screenshots/m4.png)

### Compare quotes side by side
![Quote comparison](screenshots/m5.png)

### Company registration
![Register company](screenshots/m6.png)

### Admin analytics dashboard
![Admin dashboard](screenshots/m7.png)


```

## Features

**For homeowners**
- Cost estimator: plot size, floors and finish level give an itemised cost range
- PDF report: download the itemised estimate
- Verified company directory with city search
- Send one project to several companies at once and get a reference code
- Quote comparison: quotes side by side, with the lowest highlighted and the gap to the estimate shown

**For companies**
- Registration and login with token authentication
- Dashboard showing only the requests that company received
- Enter a quote amount and a note for each request

**For the admin**
- Verify companies and manage material and labour rates in the Django admin
- Analytics dashboard: estimates per week, quote response rate, average quotes per project, quote vs estimate gap, most requested companies

**Interface**
- Responsive Bootstrap 5 design with a navbar, hero section and footer

## Tech stack

| Layer | Technology |
|---|---|
| Backend | Python, Django, Django REST Framework |
| Database | PostgreSQL |
| Frontend | HTML, CSS, JavaScript, Bootstrap 5 |
| Auth | Token authentication |
| PDF | ReportLab |
| Charts | Chart.js |

## Project structure

```
construction-cost-estimator/
├── backend/
│   ├── config/        settings and URLs
│   ├── estimator/     cost rates, estimate API, PDF report, analytics
│   ├── companies/     companies, quote requests, login, comparison
│   ├── manage.py
│   └── requirements.txt
└── frontend/
    ├── index.html      estimator and company list
    ├── register.html   company registration
    ├── dashboard.html  company login and quote entry
    ├── compare.html    quote comparison
    ├── admin.html      analytics dashboard (staff only)
    ├── app.js, dashboard.js, admin.js
    └── style.css
```

## Run locally

**Requirements:** Python 3.12 or newer, PostgreSQL, VS Code with the Live Server extension.

1. Clone the repository:

```
git clone https://github.com/CodeWithMukesh01/construction-cost-estimator.git
cd construction-cost-estimator
```

2. Create a PostgreSQL database named `construction_db`.

3. Create `backend/.env`:

```
DB_NAME=construction_db
DB_USER=postgres
DB_PASSWORD=your_postgres_password
DB_HOST=localhost
DB_PORT=5432
```

4. Set up and start the backend (Windows, Command Prompt):

```
python -m venv venv
venv\Scripts\activate.bat
pip install -r backend\requirements.txt
cd backend
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

5. Open `http://127.0.0.1:8000/admin/`, log in, and add:
   - **Cost rates** for each item at the basic, standard and premium levels
   - **Companies**, with **Is verified** ticked so they appear in the directory

6. Start the frontend with Live Server (**Go Live**) and open
   `http://localhost:5500/frontend/index.html`.

## Pages

| Page | Who uses it |
|---|---|
| `index.html` | homeowners |
| `compare.html` | homeowners, with a reference code and phone number |
| `register.html`, `dashboard.html` | construction companies |
| `admin.html` | admin only |

## How the estimate works

Built-up area = plot size × 0.70 coverage × number of floors. Each cost item = built-up
area × the rate per sq ft for the chosen finish level. The range shown is ±10% around the
total. Rates are managed in the Django admin and should be kept current for each city.

## Security notes

- Passwords are hashed by Django; secrets live in `.env`, which is not committed.
- A company can read and update only its own requests.
- Quote comparison needs both the reference code and the phone number used.
- The analytics API is restricted to staff accounts.

## Limitations

- Estimates are indicative; the final cost depends on design and site conditions.
- Starter rates are placeholders until replaced with real local rates.
- No online payment yet.

## Roadmap

- Deployment (Render and Netlify)
- Accept a quote and customer reviews
- City-wise rates and room-level inputs
- Email or WhatsApp notifications

## Author

Mukesh · [GitHub](https://github.com/CodeWithMukesh01)
