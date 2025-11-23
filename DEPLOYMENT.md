# Deployment Guide

## Current Deployment

**Platform:** Railway (https://railway.app)
**Region:** us-west1
**Status:** ✅ Production

### Services
1. **Web Service** (FastAPI backend)
   - URL: https://web-production-9625a.up.railway.app
   - Auto-deploys from `main` branch
   - Pre-deploy: Creates database tables automatically

2. **PostgreSQL Database**
   - Version: PostgreSQL 16
   - Automatic backups enabled
   - Connected via DATABASE_URL environment variable

### Environment Variables (Production)
```
DATABASE_URL=postgresql://... (auto-configured by Railway)
SECRET_KEY=<secure-random-key>
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=10080
DEBUG=False
```

### Deployment Process
1. Push to `main` branch on GitHub
2. Railway automatically detects changes
3. Runs build (installs dependencies)
4. Runs pre-deploy step (creates tables if needed)
5. Deploys new version
6. Zero-downtime deployment

### Local to Production Migration
- ✅ SQLite → PostgreSQL (completed Nov 22, 2025)
- ✅ User.phone field extended to VARCHAR(20)
- ✅ All 5 tables migrated
- ✅ All 32+ endpoints tested

### Monitoring
- **Logs:** Railway dashboard → web service → Logs tab
- **Metrics:** Railway dashboard → web service → Metrics tab
- **Health Check:** GET https://web-production-9625a.up.railway.app/

### Cost
- **Free Trial:** ~26 days remaining
- **After Trial:** ~$5-10/month (hobby plan)
- **Includes:** PostgreSQL + Web hosting

### Rollback
If deployment fails:
1. Go to Railway → web service → Deployments
2. Find last successful deployment
3. Click "Redeploy"
