#!/usr/bin/env python3
"""Streamlit UI for Indian GK Video Generator."""

import streamlit as st
import json
import os
from pathlib import Path
from dotenv import load_dotenv
import requests

from src.question_database import QuestionDatabase

# Load environment variables
load_dotenv()

# Page config
st.set_page_config(
    page_title="🇮🇳 Indian GK Video Generator",
    page_icon="🎬",
    layout="wide"
)

# Initialize session state
if 'db' not in st.session_state:
    st.session_state.db = QuestionDatabase()

if 'generated_questions' not in st.session_state:
    st.session_state.generated_questions = None

if 'last_saved_file' not in st.session_state:
    st.session_state.last_saved_file = None

# Indian GK Categories
INDIAN_CATEGORIES = {
    "Indian History": ["Ancient India", "Medieval India", "Freedom Struggle", "Independence Movement", "Post-Independence"],
    "Indian Geography": ["Rivers", "Mountains", "States & Capitals", "National Parks", "Climate", "Agriculture"],
    "Indian Politics & Constitution": ["Constitution", "Government", "Fundamental Rights", "Elections", "Parliament"],
    "Indian Culture & Heritage": ["Festivals", "Dance Forms", "Music", "Art", "Architecture", "UNESCO Sites", "Languages"],
    "Indian Economy": ["Banking", "Currency", "Budget", "Five Year Plans", "Industries", "Trade", "Economic Reforms"],
    "Indian Science & Technology": ["ISRO", "Space Missions", "Scientists", "Nuclear Program", "IT Industry", "Digital India"],
    "Indian Sports": ["Cricket", "Hockey", "Olympics", "Athletes", "National Games", "Sports Awards"],
    "Indian National Symbols": ["National Flag", "National Anthem", "National Emblem", "National Animal", "National Bird"],
    "Indian Personalities": ["Freedom Fighters", "Presidents", "Prime Ministers", "Scientists", "Artists", "Social Reformers"],
    "Current Affairs India": ["Recent Events", "Government Schemes", "International Relations", "Economic Developments"],
    "Indian States & Union Territories": ["State Capitals", "Chief Ministers", "Governors", "State Symbols", "Tourist Places"],
    "Indian Armed Forces": ["Army", "Navy", "Air Force", "Wars", "Military Operations", "Ranks", "Medals"],
    "Mixed Indian GK": ["All Topics Combined"]
}


def fetch_questions_from_gemini(topic, count, language, difficulty):
    """Fetch questions from Gemini API."""
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        st.error("❌ GEMINI_API_KEY not found in .env file")
        return None

    topics_str = ", ".join(INDIAN_CATEGORIES.get(topic, [topic]))

    prompt = f"""Generate {count} multiple-choice quiz questions about {topic} for an Indian audience.

Focus on these topics: {topics_str}

Requirements:
- All questions should be India-specific and relevant to Indian audience
- Difficulty level: {difficulty}
- Language: {language}
- Each question must have exactly 4 options
- Options should be plausible but only one correct
- Mix of factual and analytical questions

Return ONLY valid JSON in this exact format (no markdown, no code blocks):
{{
  "title": "{topic} Quiz",
  "language": "{language}",
  "questions": [
    {{
      "question": "Question text here?",
      "options": ["Option A", "Option B", "Option C", "Option D"],
      "correct": 0,
      "image": "auto"
    }}
  ]
}}

IMPORTANT: Return ONLY the JSON object, nothing else."""

    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={api_key}"

    payload = {
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {
            "temperature": 0.8,
            "topK": 40,
            "topP": 0.95,
            "maxOutputTokens": 8192,
        }
    }

    try:
        response = requests.post(url, json=payload, timeout=30)

        if response.status_code != 200:
            st.error(f"API Error: {response.status_code}")
            return None

        result = response.json()
        text = result["candidates"][0]["content"]["parts"][0]["text"]

        # Clean response
        text = text.strip()
        if text.startswith("```json"):
            text = text[7:]
        elif text.startswith("```"):
            text = text[3:]
        if text.endswith("```"):
            text = text[:-3]
        text = text.strip()

        quiz_data = json.loads(text)
        return quiz_data

    except Exception as e:
        st.error(f"Error: {e}")
        return None


# Header
st.title("🇮🇳 Indian GK Video Generator")
st.markdown("Generate quiz videos with AI-powered questions + automatic duplicate detection")

# Tabs
tab1, tab2, tab3, tab4 = st.tabs(["📝 Generate Questions", "📊 Database Stats", "🎬 Generate Videos", "📤 YouTube Upload"])

# TAB 1: Generate Questions
with tab1:
    st.header("Generate Indian GK Questions")

    col1, col2 = st.columns([2, 1])

    with col1:
        # Category selection
        category = st.selectbox(
            "Select Category",
            options=list(INDIAN_CATEGORIES.keys()),
            help="Choose the topic for your questions"
        )

        # Show topics for selected category
        st.caption(f"Topics: {', '.join(INDIAN_CATEGORIES[category])}")

    with col2:
        # Number of questions
        count = st.number_input(
            "Number of Questions",
            min_value=1,
            max_value=50,
            value=10,
            help="How many questions to generate (1-50)"
        )

    col3, col4 = st.columns(2)

    with col3:
        # Language (Tamil only)
        st.text_input("Language", value="tamil", disabled=True)
        language = "tamil"

    with col4:
        # Difficulty
        difficulty = st.selectbox(
            "Difficulty Level",
            options=["easy", "medium", "hard"],
            index=1,
            help="Question difficulty level"
        )

    # Generate button
    if st.button("🔮 Generate Questions", type="primary", use_container_width=True):
        with st.spinner(f"Generating {count} questions about {category}..."):
            quiz_data = fetch_questions_from_gemini(category, count, language, difficulty)

            if quiz_data:
                # Filter duplicates
                unique, duplicates = st.session_state.db.filter_duplicates(quiz_data["questions"])

                if duplicates:
                    st.warning(f"⚠️ Found {len(duplicates)} duplicate questions (already in database)")

                if unique:
                    quiz_data["questions"] = unique
                    st.session_state.generated_questions = quiz_data
                    st.success(f"✅ Generated {len(unique)} unique questions!")
                else:
                    st.error("❌ All questions were duplicates. Try generating again.")

    # Display generated questions
    if st.session_state.generated_questions:
        st.divider()
        st.subheader("📋 Generated Questions Preview")

        quiz_data = st.session_state.generated_questions

        for i, q in enumerate(quiz_data["questions"], 1):
            with st.expander(f"Question {i}: {q['question'][:60]}..."):
                st.markdown(f"**Q{i}. {q['question']}**")

                for j, opt in enumerate(q["options"]):
                    if j == q["correct"]:
                        st.markdown(f"✅ **{chr(65+j)}. {opt}** (Correct)")
                    else:
                        st.markdown(f"   {chr(65+j)}. {opt}")

        # Save options
        st.divider()
        col_save1, col_save2 = st.columns([3, 1])

        with col_save1:
            filename = st.text_input(
                "Filename (without .json)",
                value=quiz_data.get("title", "quiz").replace(" ", "_").lower(),
                help="Enter filename to save the questions"
            )

        with col_save2:
            st.write("")  # Spacing
            st.write("")
            if st.button("💾 Save Questions", type="primary"):
                # Save to database
                added, duplicates = st.session_state.db.save_quiz_batch(
                    questions=quiz_data["questions"],
                    title=quiz_data.get("title", "Quiz"),
                    category=category,
                    language=language,
                    difficulty=difficulty
                )

                # Save to file
                input_dir = Path("input")
                input_dir.mkdir(exist_ok=True)
                filepath = input_dir / f"{filename}.json"

                with open(filepath, "w", encoding="utf-8") as f:
                    json.dump(quiz_data, f, indent=2, ensure_ascii=False)

                st.session_state.last_saved_file = str(filepath)

                st.success(f"✅ Saved {added} questions to database and file!")
                if duplicates > 0:
                    st.info(f"ℹ️ Skipped {duplicates} duplicates")

                st.code(f"File saved: {filepath}")

# TAB 2: Database Stats
with tab2:
    st.header("📊 Question Database Statistics")

    if st.button("🔄 Refresh Stats"):
        st.rerun()

    stats = st.session_state.db.get_statistics()

    # Summary metrics
    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric("Total Questions", stats["total_questions"])

    with col2:
        st.metric("Categories", len(stats["by_category"]))

    with col3:
        st.metric("Languages", len(stats["by_language"]))

    st.divider()

    # Category breakdown
    col_cat, col_lang = st.columns(2)

    with col_cat:
        st.subheader("Questions by Category")
        if stats["by_category"]:
            for category, count in stats["by_category"].items():
                st.write(f"**{category}**: {count} questions")
        else:
            st.info("No questions yet")

    with col_lang:
        st.subheader("Questions by Language")
        if stats["by_language"]:
            for lang, count in stats["by_language"].items():
                st.write(f"**{lang.title()}**: {count} questions")
        else:
            st.info("No questions yet")

    # Recent questions
    st.divider()
    st.subheader("Recent Questions")

    if stats["recent_questions"]:
        for q_text, q_cat, q_time in stats["recent_questions"]:
            st.text(f"[{q_cat}] {q_text[:80]}...")
    else:
        st.info("No questions yet")

    # Danger zone
    st.divider()
    st.subheader("⚠️ Danger Zone")

    with st.expander("Clear All Questions"):
        st.warning("This will delete ALL questions from the database. This cannot be undone!")
        confirm = st.text_input("Type 'DELETE ALL' to confirm")
        if st.button("🗑️ Clear Database", type="secondary"):
            if confirm == "DELETE ALL":
                st.session_state.db.clear_database()
                st.success("Database cleared!")
                st.rerun()
            else:
                st.error("Please type 'DELETE ALL' to confirm")

# TAB 3: Generate Videos
with tab3:
    st.header("🎬 Generate Videos")

    # List saved question files
    input_dir = Path("input")
    json_files = list(input_dir.glob("*.json")) if input_dir.exists() else []

    if not json_files:
        st.warning("📁 No question files found. Generate and save questions first!")
    else:
        selected_file = st.selectbox(
            "Select Question File",
            options=json_files,
            format_func=lambda x: x.name
        )

        col_format, col_lang = st.columns(2)

        with col_format:
            video_format = st.selectbox(
                "Video Format",
                options=["shorts", "full"],
                format_func=lambda x: "YouTube Shorts (9:16)" if x == "shorts" else "Full Video (16:9)"
            )

        with col_lang:
            st.text_input("Video Language", value="tamil", disabled=True)
            video_lang = "tamil"

        if video_format == "full":
            questions_per_video = st.number_input(
                "Questions per Video",
                min_value=1,
                max_value=50,
                value=10
            )

        # Command preview
        st.divider()
        st.subheader("Command to Run")

        if video_format == "shorts":
            cmd = f"python generate.py {selected_file} --format shorts --lang {video_lang}"
        else:
            cmd = f"python generate.py {selected_file} --format full --lang {video_lang} --count {questions_per_video}"

        st.code(cmd, language="bash")

        st.info("💡 Copy and run this command in your terminal to generate the videos")

        # Quick stats
        try:
            with open(selected_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                total_q = len(data.get("questions", []))
                st.write(f"📊 This file contains **{total_q} questions**")

                if video_format == "shorts":
                    st.write(f"Will generate **{total_q} video files** (one per question)")
                else:
                    videos = (total_q + questions_per_video - 1) // questions_per_video
                    st.write(f"Will generate **{videos} video file(s)**")
        except:
            pass

# TAB 4: YouTube Upload
with tab4:
    st.header("📤 Upload Videos to YouTube")

    # Setup status
    secrets_path = Path("client_secret.json")
    token_path = Path("youtube_token.json")

    if not secrets_path.exists():
        st.error("❌ `client_secret.json` not found.")
        st.markdown("""
**Setup Instructions:**
1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a project (or select existing)
3. Enable **YouTube Data API v3**
4. Go to **Credentials** → Create **OAuth 2.0 Client ID** (Desktop app)
5. Download JSON and save as `client_secrets.json` in the project root
        """)
    else:
        st.success("✅ `client_secrets.json` found")

        if token_path.exists():
            st.success("✅ YouTube account authorized (token found)")
        else:
            st.warning("⚠️ Not yet authorized. Click **Authorize YouTube** below to open browser login.")

        if st.button("🔑 Authorize YouTube Account"):
            try:
                from src.youtube_uploader import get_authenticated_service
                get_authenticated_service()
                st.success("✅ Authorization successful! Token saved.")
                st.rerun()
            except Exception as e:
                st.error(f"Authorization failed: {e}")

    st.divider()
    st.subheader("Upload Video Files")

    # Scan output folder for videos
    output_dir = Path("output")
    video_files = sorted(output_dir.glob("**/*.mp4")) if output_dir.exists() else []

    if not video_files:
        st.info("📁 No videos found in output/ folder. Generate videos first.")
    else:
        # Select videos
        video_names = [str(v.relative_to(output_dir)) for v in video_files]
        selected_videos = st.multiselect(
            "Select videos to upload",
            options=video_names,
            default=video_names[:1] if video_names else [],
        )

        col_u1, col_u2 = st.columns(2)

        with col_u1:
            upload_title = st.text_input(
                "Title Prefix",
                value="Indian GK Quiz",
                help="Base title. For multiple videos, number is appended automatically.",
            )
            upload_privacy = st.selectbox(
                "Privacy",
                options=["public", "unlisted", "private"],
                index=0,
            )

        with col_u2:
            upload_category = st.selectbox(
                "Category",
                options=["Education", "Entertainment", "People & Blogs"],
                index=0,
            )
            is_shorts = st.checkbox("These are YouTube Shorts", value=True)

        upload_desc = st.text_area(
            "Description",
            value="Test your Indian General Knowledge!\n\n🔔 Subscribe for daily quizzes!\n👍 Like if you enjoyed!\n💬 Comment your score!\n\n#GKQuiz #IndianGK #K2Quiz",
            height=120,
        )

        upload_tags = st.text_input(
            "Tags (comma-separated)",
            value="GK Quiz, Indian GK, General Knowledge, Quiz, K2Quiz, India Quiz",
        )

        if st.button("🚀 Upload to YouTube", type="primary", disabled=not selected_videos or not secrets_path.exists()):
            from src.youtube_uploader import upload_video, CATEGORY_EDUCATION, CATEGORY_ENTERTAINMENT, CATEGORY_PEOPLE_BLOGS

            cat_map = {
                "Education": CATEGORY_EDUCATION,
                "Entertainment": CATEGORY_ENTERTAINMENT,
                "People & Blogs": CATEGORY_PEOPLE_BLOGS,
            }
            category_id = cat_map[upload_category]
            tags_list = [t.strip() for t in upload_tags.split(",") if t.strip()]

            progress = st.progress(0)
            status_area = st.empty()
            results_log = []

            for idx, vname in enumerate(selected_videos):
                vpath = output_dir / vname
                title = upload_title if len(selected_videos) == 1 else f"{upload_title} #{idx + 1}"

                status_area.info(f"Uploading {idx + 1}/{len(selected_videos)}: {vname}...")
                try:
                    result = upload_video(
                        video_path=vpath,
                        title=title,
                        description=upload_desc,
                        tags=tags_list,
                        category_id=category_id,
                        privacy=upload_privacy,
                        is_shorts=is_shorts,
                    )
                    results_log.append(f"✅ [{result['privacy']}] {result['video_url']} — {result['title']}")
                except Exception as e:
                    results_log.append(f"❌ FAILED {vname}: {e}")

                progress.progress((idx + 1) / len(selected_videos))

            status_area.success(f"Done! Uploaded {len([r for r in results_log if r.startswith('✅')])}/{len(selected_videos)} videos.")
            for line in results_log:
                st.write(line)

# Footer
st.divider()
st.caption("🇮🇳 Indian GK Video Generator | Powered by Gemini AI + MoviePy")
