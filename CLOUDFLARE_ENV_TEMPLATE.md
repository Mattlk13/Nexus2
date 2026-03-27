# Environment Variables for Cloudflare Integration

# Add these to your backend/.env file

# Cloudflare R2 Storage (S3-compatible)
R2_ENDPOINT_URL=https://[account-id].r2.cloudflarestorage.com
R2_ACCESS_KEY_ID=your_r2_access_key_here
R2_SECRET_ACCESS_KEY=your_r2_secret_key_here
R2_BUCKET_NAME=nexus-storage
R2_PUBLIC_URL=https://storage.nexus.com  # Your custom domain for R2

# Cloudflare Images
CLOUDFLARE_ACCOUNT_ID=your_account_id_here
CLOUDFLARE_IMAGES_TOKEN=your_images_api_token_here
CLOUDFLARE_ACCOUNT_HASH=your_account_hash_here

# Cloudflare Pages (Frontend)
# Add in Cloudflare Pages dashboard:
# REACT_APP_BACKEND_URL=https://your-backend.com

# Optional: Cloudflare Workers KV (for caching)
CLOUDFLARE_KV_NAMESPACE_ID=your_kv_namespace_id
CLOUDFLARE_API_TOKEN=your_api_token_here

---

## How to Get These Credentials:

### 1. R2 Storage:
- Go to: https://dash.cloudflare.com/ → R2
- Create bucket: "nexus-storage"
- Go to "Manage R2 API Tokens"
- Create token with "Object Read & Write"
- Copy: Access Key ID, Secret Access Key, Endpoint URL

### 2. Cloudflare Images:
- Go to: https://dash.cloudflare.com/ → Images
- Enable Cloudflare Images
- Go to API Tokens
- Create token with "Cloudflare Images Edit"
- Copy: Account ID, API Token, Account Hash

### 3. Cloudflare Pages:
- Go to: https://dash.cloudflare.com/ → Pages
- Connect GitHub repo
- Set environment variables in dashboard

---

## Testing Locally:

1. Add credentials to backend/.env
2. Install boto3: `pip install boto3`
3. Restart backend: `sudo supervisorctl restart backend`
4. Test upload at: http://localhost:3000/test-upload
