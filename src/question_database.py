"""Question Database - Track and prevent duplicate questions."""

import sqlite3
import hashlib
from pathlib import Path
from typing import List, Dict, Optional
from datetime import datetime


class QuestionDatabase:
    """Manage question history and prevent duplicates."""

    def __init__(self, db_path: str = "data/questions.db"):
        """Initialize database connection."""
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self.conn = None
        self._create_tables()

    def _create_tables(self):
        """Create database tables if they don't exist."""
        conn = self._get_connection()
        cursor = conn.cursor()

        # Questions table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS questions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                question_hash TEXT UNIQUE NOT NULL,
                question_text TEXT NOT NULL,
                category TEXT,
                language TEXT,
                difficulty TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # Question options table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS question_options (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                question_id INTEGER,
                option_text TEXT,
                is_correct BOOLEAN,
                FOREIGN KEY (question_id) REFERENCES questions(id)
            )
        """)

        # Quiz batches table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS quiz_batches (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT,
                category TEXT,
                total_questions INTEGER,
                file_path TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        conn.commit()

    def _get_connection(self):
        """Get database connection."""
        if self.conn is None:
            self.conn = sqlite3.connect(str(self.db_path))
        return self.conn

    def _hash_question(self, question_text: str) -> str:
        """Create unique hash for a question."""
        # Normalize: lowercase, remove extra spaces
        normalized = " ".join(question_text.lower().strip().split())
        return hashlib.md5(normalized.encode()).hexdigest()

    def is_duplicate(self, question_text: str) -> bool:
        """Check if question already exists in database."""
        question_hash = self._hash_question(question_text)
        conn = self._get_connection()
        cursor = conn.cursor()

        cursor.execute(
            "SELECT COUNT(*) FROM questions WHERE question_hash = ?",
            (question_hash,)
        )
        count = cursor.fetchone()[0]
        return count > 0

    def add_question(
        self,
        question_text: str,
        options: List[str],
        correct_index: int,
        category: str = None,
        language: str = "english",
        difficulty: str = "medium"
    ) -> Optional[int]:
        """
        Add a question to the database.

        Returns:
            Question ID if added, None if duplicate
        """
        if self.is_duplicate(question_text):
            return None

        question_hash = self._hash_question(question_text)
        conn = self._get_connection()
        cursor = conn.cursor()

        # Insert question
        cursor.execute("""
            INSERT INTO questions (question_hash, question_text, category, language, difficulty)
            VALUES (?, ?, ?, ?, ?)
        """, (question_hash, question_text, category, language, difficulty))

        question_id = cursor.lastrowid

        # Insert options
        for i, option in enumerate(options):
            cursor.execute("""
                INSERT INTO question_options (question_id, option_text, is_correct)
                VALUES (?, ?, ?)
            """, (question_id, option, i == correct_index))

        conn.commit()
        return question_id

    def filter_duplicates(self, questions: List[Dict]) -> tuple[List[Dict], List[Dict]]:
        """
        Filter out duplicate questions from a list.

        Returns:
            (unique_questions, duplicate_questions)
        """
        unique = []
        duplicates = []

        for q in questions:
            if self.is_duplicate(q["question"]):
                duplicates.append(q)
            else:
                unique.append(q)

        return unique, duplicates

    def save_quiz_batch(
        self,
        questions: List[Dict],
        title: str,
        category: str,
        language: str = "english",
        difficulty: str = "medium"
    ) -> tuple[int, int]:
        """
        Save a batch of questions, filtering duplicates.

        Returns:
            (added_count, duplicate_count)
        """
        added = 0
        duplicates = 0

        for q in questions:
            question_id = self.add_question(
                question_text=q["question"],
                options=q["options"],
                correct_index=q["correct"],
                category=category,
                language=language,
                difficulty=difficulty
            )

            if question_id:
                added += 1
            else:
                duplicates += 1

        return added, duplicates

    def get_statistics(self) -> Dict:
        """Get database statistics."""
        conn = self._get_connection()
        cursor = conn.cursor()

        # Total questions
        cursor.execute("SELECT COUNT(*) FROM questions")
        total_questions = cursor.fetchone()[0]

        # Questions by category
        cursor.execute("""
            SELECT category, COUNT(*) as count
            FROM questions
            GROUP BY category
            ORDER BY count DESC
        """)
        by_category = dict(cursor.fetchall())

        # Questions by language
        cursor.execute("""
            SELECT language, COUNT(*) as count
            FROM questions
            GROUP BY language
        """)
        by_language = dict(cursor.fetchall())

        # Recent questions
        cursor.execute("""
            SELECT question_text, category, created_at
            FROM questions
            ORDER BY created_at DESC
            LIMIT 5
        """)
        recent = cursor.fetchall()

        return {
            "total_questions": total_questions,
            "by_category": by_category,
            "by_language": by_language,
            "recent_questions": recent
        }

    def clear_database(self):
        """Clear all questions (use with caution!)."""
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM question_options")
        cursor.execute("DELETE FROM questions")
        cursor.execute("DELETE FROM quiz_batches")
        conn.commit()

    def close(self):
        """Close database connection."""
        if self.conn:
            self.conn.close()
            self.conn = None


if __name__ == "__main__":
    # Test the database
    db = QuestionDatabase()

    # Add test question
    question_id = db.add_question(
        question_text="What is the capital of India?",
        options=["Mumbai", "New Delhi", "Kolkata", "Chennai"],
        correct_index=1,
        category="Indian Geography"
    )

    print(f"Added question ID: {question_id}")

    # Check duplicate
    is_dup = db.is_duplicate("What is the capital of India?")
    print(f"Is duplicate: {is_dup}")

    # Get stats
    stats = db.get_statistics()
    print(f"\nDatabase Statistics:")
    print(f"Total questions: {stats['total_questions']}")
    print(f"By category: {stats['by_category']}")
