# How to Get Qdrant URL and API Key

## Option 1: Qdrant Cloud (Recommended - Easiest)

### Steps:
1. **Sign up for Qdrant Cloud**
   - Go to: https://cloud.qdrant.io/
   - Click "Sign Up" or "Get Started"
   - Create a free account (free tier available)

2. **Create a Cluster**
   - After logging in, click "Create Cluster"
   - Choose a cluster name
   - Select a region close to you
   - Choose the free tier (1GB storage, suitable for testing)

3. **Get Your Credentials**
   - Once the cluster is created, click on it
   - You'll see:
     - **Cluster URL**: Something like `https://xxxxx-xxxxx.us-east-1-0.aws.cloud.qdrant.io:6333`
     - **API Key**: A long string (click "Show" to reveal it)

4. **Use in the App**
   - **Qdrant Host URL**: Use the full URL (e.g., `https://xxxxx-xxxxx.us-east-1-0.aws.cloud.qdrant.io:6333`)
   - **Qdrant API Key**: Copy the API key from the dashboard

### Example:
```
Qdrant Host URL: https://abc123-def456.us-east-1-0.aws.cloud.qdrant.io:6333
Qdrant API Key: xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
```

---

## Option 2: Local Qdrant (For Development)

### Using Docker (Recommended):

1. **Install Docker**
   - Download from: https://www.docker.com/products/docker-desktop
   - Install and start Docker Desktop

2. **Run Qdrant Container**
   ```bash
   docker run -p 6333:6333 -p 6334:6334 \
     -v $(pwd)/qdrant_storage:/qdrant/storage:z \
     qdrant/qdrant
   ```

3. **Access Qdrant**
   - Qdrant will be available at: `http://localhost:6333`
   - No API key needed for local setup (use empty string or any value)

4. **Use in the App**
   - **Qdrant Host URL**: `http://localhost:6333`
   - **Qdrant API Key**: Leave empty or use any string (not required for local)

### Using Python (Alternative):

1. **Install Qdrant**
   ```bash
   pip install qdrant-client
   ```

2. **Run Qdrant Server**
   ```bash
   qdrant
   ```

3. **Access Qdrant**
   - URL: `http://localhost:6333`
   - No API key needed

---

## Quick Start Guide

### For Cloud (Recommended):
1. Sign up at https://cloud.qdrant.io/
2. Create a free cluster
3. Copy the Cluster URL and API Key
4. Paste them in the Streamlit app sidebar

### For Local Development:
1. Run: `docker run -p 6333:6333 qdrant/qdrant`
2. Use URL: `http://localhost:6333`
3. Use any API key (or leave empty)

---

## Troubleshooting

### Connection Issues:
- **Cloud**: Make sure you're using the full URL including `https://` and port `:6333`
- **Local**: Ensure Docker is running and port 6333 is not blocked
- **API Key**: For cloud, the API key is required. For local, it's optional.

### Testing Connection:
You can test your Qdrant connection by visiting:
- **Cloud**: `https://your-cluster-url:6333/dashboard` (if available)
- **Local**: `http://localhost:6333/dashboard`

---

## Notes

- **Free Tier Limits**: Qdrant Cloud free tier has 1GB storage, which is sufficient for testing
- **Local Storage**: Local Qdrant stores data in the `qdrant_storage` directory (if using Docker with volume mount)
- **Security**: Keep your API keys secure and never commit them to version control

