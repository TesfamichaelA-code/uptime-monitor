# Deployment Guide

This guide starts from Gmail SMTP setup and ends with a live HTTPS deployment on an Azure B2s Ubuntu VM.

Replace these placeholders before running commands:

- `YOUR_GITHUB_USERNAME`
- `YOUR_DOMAIN`
- `YOUR_VM_PUBLIC_IP`
- `YOUR_GMAIL_ADDRESS`
- `YOUR_GMAIL_APP_PASSWORD`

## 1. Set Up Gmail SMTP

The app sends downtime and recovery alerts with Gmail SMTP.

1. Open your Google Account.
2. Go to Security.
3. Enable 2-Step Verification if it is not already enabled.
4. Go to App Passwords.
5. Create a new app password for Mail.
6. Copy the generated app password.

Use these values in `.env`:

```env
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=YOUR_GMAIL_ADDRESS
SMTP_PASS=YOUR_GMAIL_APP_PASSWORD
```

Do not use your normal Gmail password. Use the generated app password.

## 2. Prepare the Azure VM

Create or use an Azure B2s Ubuntu VM.

In the Azure portal, make sure the VM network security group allows inbound traffic for:

- SSH: port 22
- HTTP: port 80
- HTTPS: port 443

Copy the public IP address of the VM. This is the value you will use for `YOUR_VM_PUBLIC_IP`.

## 3. SSH Into the VM

From your local machine:

```bash
ssh YOUR_AZURE_USERNAME@YOUR_VM_PUBLIC_IP
```

Example:

```bash
ssh azureuser@20.50.60.70
```

## 4. Install Server Dependencies

On the VM:

```bash
sudo apt update
sudo apt install -y docker.io docker-compose nginx certbot python3-certbot-nginx git
```

Enable and start Docker:

```bash
sudo systemctl enable docker
sudo systemctl start docker
```

Add your user to the Docker group:

```bash
sudo usermod -aG docker $USER
```

Log out and log back in:

```bash
exit
ssh YOUR_AZURE_USERNAME@YOUR_VM_PUBLIC_IP
```

Verify Docker works without `sudo`:

```bash
docker --version
docker-compose --version
```

## 5. Clone the Repository

On the VM:

```bash
git clone https://github.com/YOUR_GITHUB_USERNAME/uptime-monitor.git
cd uptime-monitor
```

## 6. Create the Production Environment File

Copy the example file:

```bash
cp .env.example .env
```

Generate a secret key:

```bash
python3 -c "import secrets; print(secrets.token_hex(32))"
```

Edit `.env`:

```bash
nano .env
```

Use this structure:

```env
DATABASE_URL=postgresql+asyncpg://postgres:yourpassword@postgres:5432/uptime
REDIS_URL=redis://redis:6379
SECRET_KEY=PASTE_THE_GENERATED_SECRET_KEY_HERE
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=YOUR_GMAIL_ADDRESS
SMTP_PASS=YOUR_GMAIL_APP_PASSWORD
```

Save and exit Nano:

- Press `Ctrl+O`
- Press `Enter`
- Press `Ctrl+X`

Security rule: never commit `.env`. If `.env` is accidentally pushed to GitHub, immediately rotate the Gmail app password and generate a new `SECRET_KEY`.

## 7. Build and Start the Application

From the repository directory on the VM:

```bash
docker-compose up -d --build
```

Verify all containers are running:

```bash
docker-compose ps
```

You should see:

- PostgreSQL container up
- Redis container up
- FastAPI container up

Check logs if something fails:

```bash
docker-compose logs fastapi-app
docker-compose logs postgres
docker-compose logs redis
```

Test the local app from the VM:

```bash
curl http://127.0.0.1:8000/health
```

Expected response:

```json
{"status":"ok"}
```

## 8. Point a Domain to the VM

You need a domain or subdomain pointing to the Azure VM public IP.

If you already have a domain:

1. Open your domain DNS settings.
2. Create an `A` record.
3. Set the host to your chosen subdomain, for example `monitor`.
4. Set the value to `YOUR_VM_PUBLIC_IP`.

If you do not have a domain, use DuckDNS:

1. Go to `https://www.duckdns.org`.
2. Sign in.
3. Create a subdomain, for example `myuptimemonitor`.
4. Set its IP address to `YOUR_VM_PUBLIC_IP`.
5. Your domain will look like `myuptimemonitor.duckdns.org`.

Wait 5-15 minutes for DNS propagation.

Check DNS from your local machine:

```bash
ping YOUR_DOMAIN
```

The domain should resolve to your Azure VM public IP.

You can also check propagation at:

```text
https://www.whatsmydns.net
```

## 9. Configure Nginx

On the VM, from the project directory:

```bash
sudo cp nginx/monitor /etc/nginx/sites-available/monitor
sudo nano /etc/nginx/sites-available/monitor
```

Change:

```nginx
server_name yourdomain.com;
```

to:

```nginx
server_name YOUR_DOMAIN;
```

The final file should look like:

```nginx
server {
    listen 80;
    server_name YOUR_DOMAIN;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

Enable the site:

```bash
sudo ln -s /etc/nginx/sites-available/monitor /etc/nginx/sites-enabled/
```

If the default Nginx site conflicts, remove the default symlink:

```bash
sudo rm /etc/nginx/sites-enabled/default
```

Validate Nginx:

```bash
sudo nginx -t
```

Restart Nginx:

```bash
sudo systemctl restart nginx
```

Test the HTTP version in a browser:

```text
http://YOUR_DOMAIN
```

The login page should load.

## 10. Add HTTPS With Certbot

Only run Certbot after DNS points to the VM. If DNS is not ready, the certificate challenge will fail.

Run:

```bash
sudo certbot --nginx -d YOUR_DOMAIN
```

When prompted:

1. Enter an email address.
2. Agree to the terms.
3. Choose the redirect option so HTTP redirects to HTTPS.

Test certificate renewal:

```bash
sudo certbot renew --dry-run
```

Open the live site:

```text
https://YOUR_DOMAIN
```

The browser should show the login page over HTTPS.

## 11. Production Test Flow

Use the browser at `https://YOUR_DOMAIN`.

1. Register a new account.
2. Add a real URL, for example `https://google.com`.
3. Add another real URL, for example `https://example.com`.
4. Add a URL that will fail, for example `http://127.0.0.1:9999`.
5. Wait at least 60-70 seconds.
6. Confirm status circles update:
   - green for up
   - red for down
   - gray for pending before the first check
7. Click a target card.
8. Confirm the detail panel shows uptime statistics, latency chart, and recent checks.

For email alert testing, remember:

- The first check never sends an alert.
- Alerts are sent only when status changes.
- To force a down alert, add a target that first succeeds, wait for it to show up, then create a later failure. For a demo, you can also explain that the first failing check is intentionally skipped to prevent false alerts.

## 12. Final Repository Safety Check

Before final submission:

```bash
git status
```

Make sure `.env` is not listed as tracked.

Confirm `.gitignore` includes:

```text
.env
__pycache__/
*.pyc
venv/
```

Confirm required files exist:

```text
README.md
docker-compose.yml
.env.example
backend/
backend/static/index.html
backend/monitor/worker.py
nginx/monitor
docs/DEMO_SCRIPT.md
docs/DEPLOYMENT_GUIDE.md
```

## 13. Troubleshooting

If Docker containers are not up:

```bash
docker-compose ps
docker-compose logs fastapi-app
```

If the site works on port 8000 but not through the domain:

```bash
sudo nginx -t
sudo systemctl status nginx
sudo systemctl restart nginx
```

If `https://YOUR_DOMAIN/docs` works but `https://YOUR_DOMAIN/` shows `{"detail":"Not Found"}`, the API is deployed but the frontend file is not being served by the running container. Push the latest repository changes first, then run this on the VM from the project directory:

```bash
git pull
docker-compose up -d --build
docker-compose exec fastapi-app test -f /app/static/index.html
curl -I http://127.0.0.1:8000/
sudo systemctl restart nginx
```

The local curl command should return `200 OK` for `/`. After that, open `https://YOUR_DOMAIN/` again.

If Certbot fails:

1. Confirm DNS resolves to the VM public IP.
2. Confirm Azure allows inbound port 80.
3. Confirm Nginx works over plain HTTP first.
4. Retry `sudo certbot --nginx -d YOUR_DOMAIN`.

If email alerts do not arrive:

1. Confirm `SMTP_USER` is the Gmail address.
2. Confirm `SMTP_PASS` is a Gmail app password, not the normal Gmail password.
3. Confirm the monitor status changed after the first check.
4. Check logs with `docker-compose logs fastapi-app`.

## 14. Final Submission Items

Submit:

1. Planning PDF.
2. Public GitHub repository URL.
3. Live HTTPS URL.
4. Demo video link.
