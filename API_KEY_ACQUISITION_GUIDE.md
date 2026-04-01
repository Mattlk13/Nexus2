# 🔑 API Key Acquisition Guide

## Overview
NEXUS uses the **Emergent Universal LLM Key** which covers OpenAI, Anthropic, and Google. Additional keys are needed for specialized services.

---

## ✅ Already Configured (No Action Needed)

### 1. Emergent Universal LLM Key
- **Status**: ✅ Active
- **Location**: `/app/backend/.env` → `EMERGENT_LLM_KEY`
- **Covers**: OpenAI (GPT-5.1, GPT Image 1), Anthropic (Claude Sonnet 4), Google (Gemini 2.5)
- **Used by**: Universal AI, Code Review, 20+ hybrid services
- **Cost**: Managed by Emergent platform

### 2. Stripe Test Key
- **Status**: ✅ Active (Test Mode)
- **Location**: Available in environment
- **Used by**: Payment processing hybrid
- **Note**: For production, get live keys at https://dashboard.stripe.com/apikeys

---

## ⚠️ Optional API Keys (Needed for Full Functionality)

### 3. ElevenLabs (Voice Generation)

**How to Get:**
1. Go to: https://elevenlabs.io/sign-up
2. Sign up with email
3. Verify email
4. Navigate to: https://elevenlabs.io/app/settings/api-keys
5. Click "Create API Key"
6. Copy the key

**Add to NEXUS:**
```bash
# Edit /app/backend/.env
ELEVENLABS_API_KEY=your_key_here
```

**Free Tier**: 10,000 characters/month

---

### 4. Fal.ai (Advanced Media Generation)

**How to Get:**
1. Go to: https://fal.ai/
2. Sign up with GitHub or Google
3. Navigate to: https://fal.ai/dashboard/keys
4. Create new API key
5. Copy the key

**Add to NEXUS:**
```bash
# Edit /app/backend/.env
FAL_KEY=your_key_here
```

**Free Tier**: $5 credits on signup

---

### 5. DigitalOcean (Agent Development Kit)

**How to Get:**
1. Go to: https://cloud.digitalocean.com/registrations/new
2. Sign up (requires credit card for verification)
3. Go to: https://cloud.digitalocean.com/account/api/tokens
4. Click "Generate New Token"
5. Name: "NEXUS Platform"
6. Scopes: Read + Write
7. Copy token

**Add to NEXUS:**
```bash
# Edit /app/backend/.env
DIGITALOCEAN_API_TOKEN=your_token_here
GRADIENT_MODEL_ACCESS_KEY=your_gradient_key_here
```

**Note**: Also need Gradient key from https://gradient.ai/

---

### 6. Cloudflare (Edge Computing, KV Storage, Workers)

**How to Get:**
1. Go to: https://dash.cloudflare.com/sign-up
2. Sign up with email
3. Verify email
4. Go to: https://dash.cloudflare.com/profile/api-tokens
5. Click "Create Token"
6. Template: "Edit Cloudflare Workers"
7. Add permissions:
   - Account > Workers Scripts > Edit
   - Account > Workers KV Storage > Edit
8. Copy token

**Add to NEXUS:**
```bash
# Edit /app/backend/.env
CLOUDFLARE_API_TOKEN=your_token_here
CLOUDFLARE_ACCOUNT_ID=your_account_id
```

---

## 🔧 How to Add API Keys to NEXUS

### Method 1: Environment Variables (Recommended)
```bash
# SSH into your server or edit locally
cd /app/backend
nano .env

# Add your keys:
ELEVENLABS_API_KEY=sk_xxxxx
FAL_KEY=xxxxx
DIGITALOCEAN_API_TOKEN=dop_xxxxx
CLOUDFLARE_API_TOKEN=xxxxx

# Save and restart backend
sudo supervisorctl restart backend
```

### Method 2: Via UI (Coming Soon)
Dashboard → Settings → API Keys → Add Key

---

## 💰 Cost Estimate

**With Emergent Universal Key:**
- ✅ OpenAI, Anthropic, Google: **Included** in Emergent platform

**Additional Optional Services:**
- ElevenLabs: **Free tier** (10k chars/month) or $5/month (30k chars)
- Fal.ai: **$5 free credits** then ~$0.05-0.50 per generation
- DigitalOcean: **Free $200 credit** for 60 days, then ~$5-20/month
- Cloudflare: **Free tier** (100k requests/day) or $5/month (10M requests)

**Total Monthly Cost (if you exceed free tiers)**: ~$15-35/month

---

## 🔒 Security Best Practices

1. **Never commit `.env` to git** (already in `.gitignore`)
2. **Use environment-specific keys** (test vs production)
3. **Rotate keys quarterly**
4. **Monitor usage** via provider dashboards
5. **Set up billing alerts** to avoid surprise charges

---

## 📊 Current API Key Status

| Service | Status | Used By | Free Tier |
|---------|--------|---------|-----------|
| **Emergent LLM Key** | ✅ Active | Universal AI, Code Review, 20+ hybrids | ✅ Included |
| **Stripe (Test)** | ✅ Active | Payments | ✅ Test mode |
| **ElevenLabs** | ⚠️ Optional | Voice generation | ✅ 10k chars/month |
| **Fal.ai** | ⚠️ Optional | Media generation | ✅ $5 credits |
| **DigitalOcean** | ⚠️ Optional | Agent Dev Kit | ✅ $200/60 days |
| **Cloudflare** | ⚠️ Optional | Edge computing | ✅ 100k req/day |

---

## ✅ Testing Your API Keys

After adding keys, test each service:

```bash
# Test ElevenLabs
curl -X POST "$API_URL/api/v2/hybrid/elevenlabs/generate" \
  -H "Content-Type: application/json" \
  -d '{"text": "Hello world", "voice": "default"}'

# Test Fal.ai
curl -X GET "$API_URL/api/v2/hybrid/media/capabilities"

# Test DigitalOcean ADK
curl -X GET "$API_URL/api/adk/init"

# Test Cloudflare
curl -X GET "$API_URL/api/v2/hybrid/cloudflare/capabilities"
```

---

## 🚨 I Cannot Auto-Acquire These Keys

**Why I can't do it:**
- Requires browser login with YOUR credentials
- Email verification needed
- Some need credit card info
- Terms of service acceptance required
- Security/privacy concerns

**What I CAN do:**
- ✅ Provide this detailed guide
- ✅ Set up configuration templates
- ✅ Test endpoints once you add keys
- ✅ Monitor usage and costs

---

## 🆘 Need Help?

If you encounter issues acquiring keys:
1. Check provider's documentation
2. Contact provider support
3. Use alternative services (NEXUS supports multiple providers for most features)

**Alternative Providers:**
- Voice: OpenAI TTS (via Emergent Key) instead of ElevenLabs
- Media: GPT Image 1 (via Emergent Key) instead of Fal.ai
- Edge: Self-hosted instead of Cloudflare

---

**Last Updated**: April 1, 2026
**NEXUS Version**: 6.0
