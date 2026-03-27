# 🔑 NEXUS API Keys Setup Guide

Use credentials: `hm2krebsmatthewl@gmail.com` / `Tristen527!`

## 1. ProductHunt API Key (5 mins)

**Steps:**
1. Go to https://www.producthunt.com and log in with above credentials
2. Click your profile picture → **API Dashboard**
3. Click **Create Application** (name: "NEXUS", URL: any placeholder)
4. Scroll down → Click **Create Token**
5. Copy the token (format: `xxx...`)

**Add to `.env`:**
```
PRODUCTHUNT_API_KEY=your_token_here
```

---

## 2. Resend Email API Key (5 mins)

**Steps:**
1. Go to https://resend.com and sign up with above credentials
2. Navigate to **API Keys** in dashboard
3. Click **Create API Key** (name: "NEXUS Email Service")
4. Copy the key (format: `re_xxx...`)

**Add to `.env`:**
```
RESEND_API_KEY=re_your_key_here
SENDER_EMAIL=onboarding@resend.dev
```

**Note:** You'll need to verify a domain for production emails.

---

## 3. ElevenLabs Voice API Key (5 mins)

**Steps:**
1. Go to https://elevenlabs.io and sign up/login with above credentials
2. Navigate to **Developers** → **API Keys**
3. Click **+ Create Key** (name: "NEXUS Voice Generation")
4. Select permissions: Enable **Text to Speech** and **Voice Generation**
5. Copy the key immediately (shown only once!)

**Add to `.env`:**
```
ELEVENLABS_API_KEY=your_elevenlabs_key_here
```

---

## 4. Fal.ai Image Generation API Key (5 mins)

**Steps:**
1. Go to https://fal.ai and create account with above credentials
2. Navigate to https://fal.ai/dashboard/keys
3. Click **Create Key** (name: "NEXUS Image Gen", scope: **API**)
4. Copy the key (format: `key_id:key_secret`)
5. Add credits: Dashboard → Usage → Billing → Top Up (~$10 recommended)

**Add to `.env`:**
```
FAL_KEY=your_fal_key_here
```

---

## ⚡ After Adding Keys

**Restart backend:**
```bash
sudo supervisorctl restart backend
```

**Verify integrations:**
```bash
curl http://localhost:8001/api/integration-status | python3 -c "import sys,json; data=json.load(sys.stdin); print(f\"Active: {data['summary']['active']}/{data['summary']['total']} - Health: {data['summary']['health_score']:.0f}%\")"
```

**Expected:** Health score should jump from 25% to 75-100%

---

## 🎯 Priority Order
1. **ProductHunt** - Unlocks +20 tools per scan
2. **Resend** - Enables real email notifications
3. **ElevenLabs** - Activates voice generation in Creator Studio
4. **Fal.ai** - Activates advanced image generation

**Time Required:** ~20 minutes total for all 4
