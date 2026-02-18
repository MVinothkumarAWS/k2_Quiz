# 🖼️ Image Fetching Setup Guide

## ✅ **Current Status: WORKING!**

Your image fetching is **already functional** using **Wikimedia Commons** (free, no setup required)!

---

## 🎯 How Image Fetching Works

### **Multi-Source Fallback System**

The system tries multiple sources in order:

```
1. Pexels       → High quality, needs API key (200 req/hour)
2. Unsplash     → High quality, needs API key (50 req/hour)
3. Pixabay      → Good quality, needs API key (100 req/min)
4. Wikimedia    → FREE, NO KEY, Educational images ✅ CURRENTLY WORKING
5. Lorem Picsum → FREE, NO KEY, Random placeholders (fallback)
```

---

## 🚀 Quick Test

Your image fetcher is already working! Test it:

```bash
cd D:\K2_Quiz_Youtube\K2_Quiz_Youtube

# Test with Python
python -c "from src.image_fetcher import fetch_image; print(fetch_image('India Gate'))"

# Check the images folder
dir images\
```

**Result:**
- ✅ Images are downloaded to `images/` folder
- ✅ Cached for reuse (no repeated downloads)
- ✅ Uses Wikimedia Commons by default

---

## 📊 Current Setup

### **Working (No Setup Required):**

✅ **Wikimedia Commons** - FREE, search-based, educational images
- No API key needed
- Great for Indian GK topics
- Examples: Historical sites, personalities, geography
- Quality: Good to Excellent
- Limitations: Educational/documentary style photos

✅ **Lorem Picsum** - FREE, random images (fallback only)
- No API key needed
- Random stock photos
- Used only if Wikimedia fails
- Quality: Good, but not relevant to topic

---

## 🔑 Optional: Premium Image APIs

Want **higher quality** or **more diverse** images? Add these FREE API keys:

### **Option 1: Pexels (Recommended)**

**Best for: General topics, high-quality stock photos**

1. **Sign up:** https://www.pexels.com/api/
2. **Get API key** (instant, free)
3. **Add to .env:**
   ```bash
   PEXELS_API_KEY=your_key_here
   ```

**Limits:**
- 200 requests per hour
- 20,000 requests per month
- Free forever!

**Example:**
```bash
# .env
PEXELS_API_KEY=563492ad6f9170000100000188bdf1d2e9f44a8c8e3c8a8a8a8a8a8a
```

---

### **Option 2: Unsplash**

**Best for: Artistic photos, modern aesthetics**

1. **Sign up:** https://unsplash.com/developers
2. **Create app** (takes 2 minutes)
3. **Get Access Key**
4. **Add to .env:**
   ```bash
   UNSPLASH_API_KEY=your_access_key_here
   ```

**Limits:**
- 50 requests per hour
- 5,000 requests per month (demo)
- Free tier available

**Example:**
```bash
# .env
UNSPLASH_API_KEY=xK_0VxSm4rZAbcDeFgHiJkLmNoPqRsTuVwXyZ123
```

---

### **Option 3: Pixabay**

**Best for: Illustrations, vectors, icons**

1. **Sign up:** https://pixabay.com/api/docs/
2. **Get API key** (instant, free)
3. **Add to .env:**
   ```bash
   PIXABAY_API_KEY=your_key_here
   ```

**Limits:**
- 100 requests per minute
- 5,000 requests per hour
- Free forever!

**Example:**
```bash
# .env
PIXABAY_API_KEY=12345678-abc1234def5678ghi901234
```

---

## 🔧 Complete .env File Example

```bash
# Gemini AI (Required - Already configured)
GEMINI_API_KEY=AIzaSyAU9il3XWMIFxWDgW2A9h39ebD4aZX6OSs

# Image APIs (All Optional - Wikimedia works without these)
# Pexels: https://www.pexels.com/api/ (200 requests/hour)
PEXELS_API_KEY=

# Unsplash: https://unsplash.com/developers (50 requests/hour)
UNSPLASH_API_KEY=

# Pixabay: https://pixabay.com/api/docs/ (100 requests/minute)
PIXABAY_API_KEY=
```

---

## 📝 Step-by-Step: Adding Pexels API (Recommended)

### **1. Visit Pexels API Page**
```
https://www.pexels.com/api/
```

### **2. Click "Get Started"**
- Create free account
- Or log in with Google

### **3. Generate API Key**
- Go to: https://www.pexels.com/api/documentation/
- Scroll to "Your API Key"
- Copy the key (starts with 563492...)

### **4. Add to .env File**

Open: `D:\K2_Quiz_Youtube\K2_Quiz_Youtube\.env`

Add the line:
```bash
PEXELS_API_KEY=your_actual_key_here
```

### **5. Test It**
```bash
cd D:\K2_Quiz_Youtube\K2_Quiz_Youtube
python -c "from src.image_fetcher import fetch_image; print(fetch_image('Sunset', force_download=True))"
```

You should see:
```
Found on Pexels
Saved: sunset.jpg
```

---

## 🧪 Testing Image Sources

### **Test Script:**

Create `test_my_images.py`:
```python
from src.image_fetcher import fetch_image

# Test queries
queries = [
    "Taj Mahal",
    "India Gate",
    "Mahatma Gandhi",
    "Indian Flag",
    "Himalayas"
]

print("\n" + "="*60)
print("TESTING IMAGE FETCHER")
print("="*60 + "\n")

for query in queries:
    print(f"\nSearching: {query}")
    result = fetch_image(query)
    if result:
        print(f"  SUCCESS: {result}")
    else:
        print(f"  FAILED")
    print("-" * 60)
```

### **Run Test:**
```bash
python test_my_images.py
```

---

## 📊 Source Comparison

| Source | Quality | Relevance | Setup | Limits |
|--------|---------|-----------|-------|--------|
| **Wikimedia** | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ✅ None | Unlimited |
| **Pexels** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | API key | 200/hour |
| **Unsplash** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | API key | 50/hour |
| **Pixabay** | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ | API key | 100/min |
| **Lorem Picsum** | ⭐⭐⭐ | ⭐ | ✅ None | Unlimited |

---

## 🎯 Recommendations by Use Case

### **For Indian GK Quiz Videos (Your Project):**

**Best Setup:**
```
1st: Wikimedia Commons (already working) ← Perfect for Indian topics
2nd: Pexels (if you want more variety)
```

**Why Wikimedia is Great for Indian GK:**
- ✅ Accurate historical images
- ✅ Photos of Indian landmarks
- ✅ Portraits of Indian personalities
- ✅ Maps and geography
- ✅ Cultural and heritage photos
- ✅ Free and unlimited

**When to Add Pexels:**
- You want modern, stylized photos
- Need generic concepts (sunset, mountains, etc.)
- Want backup when Wikimedia doesn't have the image

### **For General Topics:**

**Best Setup:**
```
1st: Pexels or Unsplash (high quality stock)
2nd: Wikimedia (educational backup)
3rd: Pixabay (more options)
```

---

## 🔍 How the System Chooses Images

### **Priority Order:**

```python
# From image_fetcher.py (lines 200-206)

sources = [
    ("Pexels", fetch_from_pexels),      # If API key exists
    ("Unsplash", fetch_from_unsplash),  # If API key exists
    ("Pixabay", fetch_from_pixabay),    # If API key exists
    ("Wikimedia", fetch_from_wikimedia), # Always available ✅
    ("Placeholder", fetch_placeholder_image), # Last resort
]
```

### **Behavior:**

1. **Checks cache first** - If image already downloaded, reuse it
2. **Tries each source** - In order, until one succeeds
3. **Downloads & saves** - Caches to `images/` folder
4. **Returns path** - Or None if all fail

---

## 📁 Image Cache

### **Location:**
```
D:\K2_Quiz_Youtube\K2_Quiz_Youtube\images\
```

### **How Caching Works:**
```python
# Example
query = "Taj Mahal"
# Saved as: images/taj_mahal.jpg

query = "What is the capital of India?"
# Saved as: images/what_is_the_capital_of_india.jpg
```

### **Benefits:**
- ✅ Faster video generation (no re-download)
- ✅ Saves API quota
- ✅ Works offline after first download
- ✅ Consistent images across videos

### **Clear Cache:**
```bash
# Delete all cached images
rm -rf images/*

# Or on Windows
del /Q images\*
```

---

## 🚨 Troubleshooting

### **Issue 1: "No images found"**

**Cause:** All sources failed

**Solutions:**
1. Check internet connection
2. Try a different query (simpler/more common term)
3. Add a premium API key (Pexels recommended)

### **Issue 2: "Placeholder images used"**

**Cause:** Wikimedia didn't find relevant image

**Solutions:**
1. Add Pexels API key for better coverage
2. Simplify query (e.g., "Gandhi" instead of "Mahatma Gandhi ji")
3. Use manual images (see below)

### **Issue 3: "Rate limit exceeded"**

**Cause:** Too many API requests

**Solutions:**
1. Wait 1 hour (free tiers reset hourly)
2. Use cached images (already downloaded)
3. Add multiple API keys to spread load

### **Issue 4: "Irrelevant images"**

**Cause:** Query too vague or generic

**Solutions:**
1. Use more specific queries
2. Manually specify image paths (see below)
3. Add Wikimedia search, best for specific topics

---

## 🎨 Manual Image Override

### **Method 1: Use Local Images**

```python
# In your quiz JSON
{
  "question": "Who is this person?",
  "options": [...],
  "correct": 0,
  "image": "images/gandhi.jpg"  # ← Use local path
}
```

### **Method 2: Use URLs**

```python
# In your quiz JSON
{
  "question": "What is this place?",
  "options": [...],
  "correct": 0,
  "image": "https://example.com/tajmahal.jpg"  # ← Direct URL
}
```

### **Method 3: Disable Images**

```python
# In your quiz JSON
{
  "question": "What is 2+2?",
  "options": [...],
  "correct": 1,
  "image": null  # ← No image for this question
}
```

---

## 📊 API Quota Management

### **Current Setup (No Premium Keys):**
```
Wikimedia:      Unlimited ✅
Lorem Picsum:   Unlimited ✅
```

### **With Premium Keys:**
```
Pexels:    200/hour  = ~13 videos/hour (15 questions each)
Unsplash:  50/hour   = ~3 videos/hour
Pixabay:   100/min   = ~400 videos/hour!
```

### **Best Practice:**
1. Cache images after first fetch
2. Reuse cached images when possible
3. Delete cache only when you want fresh images

---

## ✅ Summary

### **Current Status:**
- ✅ Image fetching is **WORKING**
- ✅ Using **Wikimedia Commons** (free, unlimited)
- ✅ Perfect for **Indian GK topics**
- ✅ No setup required!

### **Optional Improvements:**
- Add **Pexels API** for more variety (free, 200/hour)
- Add **Unsplash API** for artistic photos (free, 50/hour)
- Add **Pixabay API** for illustrations (free, 100/min)

### **Recommendation:**
**Keep it as is!** Wikimedia Commons works perfectly for your Indian GK quiz videos. Only add premium APIs if you:
- Need more modern/stylized photos
- Want backup sources
- Plan to scale to 100+ videos/day

---

## 🎯 Quick Start

### **Generate Tamil Quiz with Images (Working Now):**

```bash
# 1. Start UI
cd D:\K2_Quiz_Youtube\K2_Quiz_Youtube
start.bat

# 2. Generate Tamil questions with images
# Browser: http://localhost:8501
# - Category: Indian History
# - Language: Tamil
# - Images: Auto (uses Wikimedia)

# 3. Create video
python generate.py input/tamil_history.json --format shorts --lang tamil

# Images will be fetched automatically! ✅
```

---

## 📞 Need Help?

### **Check Logs:**
```bash
# When generating video, watch console output:
# "Found on Wikimedia" = Success!
# "Found on Placeholder" = No relevant image found
```

### **Test Specific Query:**
```bash
python -c "from src.image_fetcher import fetch_image; fetch_image('Your Query Here', force_download=True)"
```

---

**Your image fetching is ready to use! 🎉**

*Last updated: 2026-02-13*
