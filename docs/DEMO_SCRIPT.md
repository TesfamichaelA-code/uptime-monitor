# Demo Video Script

Target length: 5-10 minutes.

Use this as a speaking script while recording with OBS. Replace placeholders with your real project links and domain.

## Before Recording

Prepare these tabs:

1. GitHub repository.
2. Live app at `https://YOUR_DOMAIN`.
3. Gmail inbox for alert email.
4. Optional: terminal connected to the Azure VM.

Make sure the app is running and HTTPS works before recording.

## 0:00 - Introduction

Hello, my name is YOUR_NAME. This is my Simple Uptime Monitoring Service project.

The purpose of this application is to let a user register, add websites or URLs to monitor, and see whether those targets are up or down. The system checks the targets in the background every 60 seconds, stores historical check data, calculates uptime statistics, shows latency history, and sends email alerts when a target changes from up to down or from down to back up.

The live application is deployed here:

```text
https://YOUR_DOMAIN
```

The source code is available here:

```text
https://github.com/YOUR_GITHUB_USERNAME/uptime-monitor
```

## 0:45 - Brief Architecture Overview

This project uses FastAPI for the backend API and for serving the static frontend.

It uses PostgreSQL to store users, targets, check records, and alert logs. It uses Redis to cache the latest status for each target so the dashboard can load current status quickly.

The monitor worker runs as a background async task inside the FastAPI application. Every 60 seconds it queries all active targets and checks them concurrently using aiohttp. Each attempt is stored in the database, including failed attempts.

The frontend is a single-page app built with plain HTML, CSS, JavaScript, and Chart.js. There is no separate frontend build step.

## 1:30 - Show Login and Register Screen

Now I am on the live HTTPS site.

You can see the login and register tabs. I will create a new account for the demonstration.

I am entering an email, password, and notification email. The notification email is where downtime and recovery alerts are sent.

After registration, the backend returns a JWT access token. The frontend stores that token only in a JavaScript variable for the current session. It does not store the token in localStorage.

## 2:15 - Add Targets

Now I am on the dashboard.

At the top there is an Add URL form. I will add two real URLs and one URL that should fail.

First target:

```text
Name: Google
URL: https://google.com
```

Second target:

```text
Name: Example
URL: https://example.com
```

Failing target:

```text
Name: Local Failure
URL: http://127.0.0.1:9999
```

After adding the targets, the dashboard initially shows gray pending status because the monitor has not checked them yet. This is intentional. A new target should not be shown as down before the first monitoring cycle runs.

## 3:15 - Explain Pending State and Monitor Cycle

The monitor runs every 60 seconds. For each active target, it sends a HEAD request with a 10-second timeout and follows redirects.

If the response status code is from 200 to 399, the target is considered up. If the request times out, has a DNS error, connection error, or any other exception, the target is considered down and the stored status code is zero.

The application writes every check result to PostgreSQL and writes the latest status to Redis using a key like `status:{target_id}`.

I will wait for the first monitoring cycle to complete.

Pause the recording here if needed, or keep recording for about 60-70 seconds.

## 4:15 - Show Dashboard Status Updates

Now the dashboard has refreshed.

The two real URLs show green status circles, meaning they are up. The failing URL shows a red status circle, meaning it is down.

Each card also shows the 24-hour uptime percentage and the last response time in milliseconds. The frontend refreshes automatically every 30 seconds, so the user does not need to reload the page.

This shows that the FastAPI API, Redis status cache, monitor worker, and frontend dashboard are working together.

## 5:00 - Show Target Detail View

I will click one of the target cards to open the detail view.

This panel shows:

- 24-hour uptime percentage.
- 7-day uptime percentage.
- Average 24-hour latency.
- A Chart.js latency line chart.
- A table of recent individual checks.

The chart and table are loaded from the history endpoint. The stats are calculated from PostgreSQL check records.

The backend verifies that the target belongs to the logged-in user before returning stats or history data. If another user tries to access the target, the API returns 403 Forbidden.

## 6:00 - Show Email Alert Behavior

The application sends email alerts when a target changes status.

It intentionally skips alerting on the first check for a target. This prevents false alerts when a new URL is first added.

When a target changes from up to down, the email subject is:

```text
DOWN: target name is unreachable
```

When a target changes from down to up, the email subject is:

```text
BACK UP: target name is responding again
```

Now I will show the Gmail inbox where the alert email arrives.

Show the inbox if you have a real alert email available.

If the first failing target did not send an email, say:

For this demonstration, the first failing check does not send an email because the project requirement says to skip the first check. This avoids sending a false down alert every time a new target is added. The email alert is sent on a later status change.

## 7:00 - Show API or Repository

Now I will briefly show the repository structure.

The backend folder contains the FastAPI application, SQLAlchemy models, database setup, authentication, routers, monitor worker, alerting code, and static frontend.

The Docker Compose file starts three services:

- PostgreSQL
- Redis
- FastAPI app

The Nginx folder contains the reverse proxy configuration used on the Azure VM.

The `.env.example` file lists the required environment variables, but the real `.env` file is not committed because it contains secrets.

## 8:00 - Closing

To summarize, this project implements a working uptime monitoring service with user authentication, target management, background monitoring, persistent check history, Redis status caching, uptime statistics, latency charts, email alerts, Docker deployment, Nginx reverse proxy, and HTTPS.

The final submission includes:

- The planning PDF.
- The public GitHub repository.
- The live HTTPS URL.
- This demo video.

Thank you.

## Quick Demo Checklist

Use this checklist during recording:

- Show live HTTPS URL.
- Show login/register screen.
- Register a new user.
- Add `https://google.com`.
- Add `https://example.com`.
- Add `http://127.0.0.1:9999`.
- Wait 60-70 seconds.
- Show green, green, red status circles.
- Open a target detail view.
- Show uptime stats.
- Show latency chart.
- Show recent checks table.
- Show Gmail alert if available.
- Show GitHub repository briefly.
