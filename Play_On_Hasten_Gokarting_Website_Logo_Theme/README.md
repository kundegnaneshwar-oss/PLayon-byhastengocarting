# Play On – By Hasten Gokarting

A responsive Flask website starter with a Hasten-logo-inspired green/white/blue racing design, booking request form, SQLite storage, and protected admin dashboard.

## Included
- Home page with racing-themed sections, packages, contact/location details.
- Booking request form with validation and booking reference number.
- SQLite database for saved booking requests.
- Admin login and dashboard to review bookings and update statuses.
- Google Maps directions link for the supplied Gurram Guda address.
- Ready-to-deploy `Procfile` for platforms that support Python web services.

## Run locally on macOS / VS Code

1. Install Python 3.11 or 3.12 if possible.
2. Open this folder in VS Code.
3. In the VS Code terminal run:

   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   pip install -r requirements.txt
   ```

4. Set local admin credentials before starting:

   ```bash
   export SECRET_KEY="replace-with-a-long-random-value"
   export ADMIN_USERNAME="admin"
   export ADMIN_PASSWORD="choose-a-strong-password"
   python app.py
   ```

5. Open `http://127.0.0.1:5000`.
6. Admin page: `http://127.0.0.1:5000/admin/login`.

Default credentials are intentionally not suitable for production. Always set a strong password and secret key.

## Publish online

This project is deployable, but it has not been published from this package: publishing requires access to your hosting account and a persistent database setup.

Typical deployment flow:
1. Upload this folder to a GitHub repository.
2. Create a Python web service on a host that supports Flask/Gunicorn.
3. Set the start command to `gunicorn app:app` (or use the included Procfile).
4. Add environment variables: `SECRET_KEY`, `ADMIN_USERNAME`, `ADMIN_PASSWORD`, `BUSINESS_PHONE`, `BUSINESS_EMAIL`.
5. Configure a persistent disk and set `DATABASE_PATH` to a file on that disk. Without persistent storage, SQLite data may be lost during redeploy/restart.
6. Deploy and test a booking request and admin login.

## Important before launch
- Replace the placeholder phone number and email using environment variables.
- Confirm real session durations, prices, hours, participant rules, age/height limits and cancellation policy.
- Add a real payment provider only after you have a verified merchant account. This starter does **not** collect online payments, send OTPs, send email notifications, or confirm real-time availability.
- Add an explicit privacy notice and terms before collecting customer information publicly.
- Use HTTPS and strong admin credentials. Do not share admin passwords in public repositories.
- For a production site with multiple workers or high traffic, consider PostgreSQL instead of SQLite.
