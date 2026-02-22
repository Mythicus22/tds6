# eShopCo Latency Check API

Serverless Python endpoint for monitoring deployment latency by region. Deploy to Vercel and call from dashboards to verify deployments stay under target latency.

## POST Endpoint

After deployment, your endpoint URL will be:

```
https://<your-project>.vercel.app/api/latency
```

## Request

- **Method:** `POST`
- **Content-Type:** `application/json`
- **Body:**
  ```json
  {
    "regions": ["amer", "apac"],
    "threshold_ms": 160
  }
  ```

## Response

Per-region metrics for each requested region:

| Field        | Description                                      |
|-------------|---------------------------------------------------|
| `avg_latency` | Mean latency (ms)                                |
| `p95_latency` | 95th percentile latency (ms)                     |
| `avg_uptime`  | Mean uptime percentage                           |
| `breaches`    | Count of records exceeding the threshold         |

Example:
```json
{
  "amer": {
    "avg_latency": 173.02,
    "p95_latency": 236.69,
    "avg_uptime": 97.82,
    "breaches": 7
  },
  "apac": {
    "avg_latency": 168.6,
    "p95_latency": 227.72,
    "avg_uptime": 98.19,
    "breaches": 6
  }
}
```

CORS is enabled for POST requests from any origin.

---

## Deploy to Vercel

### Prerequisites

1. [Node.js](https://nodejs.org/) installed (for Vercel CLI)
2. A [Vercel account](https://vercel.com/signup) (free tier works)

### Option A: Deploy via Vercel Dashboard (GitHub)

1. **Push your project to GitHub**
   - Create a new repository on [GitHub](https://github.com/new)
   - Initialize git and push:
     ```bash
     git init
     git add .
     git commit -m "eShopCo latency API"
     git branch -M main
     git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPO.git
     git push -u origin main
     ```

2. **Import and deploy on Vercel**
   - Go to [vercel.com/new](https://vercel.com/new)
   - Click **Import** next to your repository
   - Vercel will auto-detect the Python API
   - Click **Deploy**
   - After deployment, you'll get a URL like `https://your-project-xxx.vercel.app`

3. **Your POST endpoint:**
   ```
   https://your-project-xxx.vercel.app/api/latency
   ```

### Option B: Deploy via Vercel CLI

1. **Install Vercel CLI**
   ```bash
   npm install -g vercel
   ```

2. **Login**
   ```bash
   vercel login
   ```

3. **Deploy from project folder**
   ```bash
   cd d:\agneesh\new
   vercel
   ```
   - Follow prompts (link to existing project or create new)
   - For production: `vercel --prod`

4. **Your POST endpoint:**
   ```
   https://<your-project>.vercel.app/api/latency
   ```

### Test the endpoint

**Bash / Git Bash / WSL:**
```bash
curl -X POST https://<your-project>.vercel.app/api/latency \
  -H "Content-Type: application/json" \
  -d '{"regions":["amer","apac"],"threshold_ms":160}'
```

**PowerShell (Windows):**
```powershell
Invoke-RestMethod -Uri "https://<your-project>.vercel.app/api/latency" -Method POST -ContentType "application/json" -Body '{"regions":["amer","apac"],"threshold_ms":160}'
```

---

## Project structure

```
├── api/
│   └── latency.py        # Serverless function → /api/latency
├── q-vercel-latency.json # Telemetry data (bundled with deployment)
├── vercel.json           # Vercel config
├── requirements.txt      # Python dependencies (none required)
└── README.md
```
