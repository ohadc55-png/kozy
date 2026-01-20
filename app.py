import streamlit as st
import sqlite3
import os
import uuid
import hashlib
from datetime import datetime, timedelta
from pathlib import Path
import json
import time

# ======================
# הגדרות בסיסיות
# ======================
st.set_page_config(
    page_title="Kozy Review | סקירת וידאו מקצועית",
    page_icon="🎬",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# נתיבים
UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)
DB_PATH = "kozy_review.db"

# תמונות
LOGO_URL = "https://i.postimg.cc/7LMZ1dLJ/קוזי.png"
MASCOT_URL = "https://i.postimg.cc/fbjR7pb0/רועי.png"

# קטגוריות ועדיפויות
CATEGORIES = {
    "video": {"label": "וידאו", "icon": "🎬", "color": "#6366F1"},
    "image": {"label": "תמונה", "icon": "🖼️", "color": "#8B5CF6"},
    "effect": {"label": "אפקט", "icon": "✨", "color": "#F59E0B"},
    "subtitles": {"label": "כתוביות", "icon": "💬", "color": "#10B981"},
    "transition": {"label": "מעבר", "icon": "🔄", "color": "#F97316"},
    "music": {"label": "מוזיקה", "icon": "🎵", "color": "#EC4899"},
    "sound": {"label": "סאונד", "icon": "🔊", "color": "#3B82F6"},
    "ai": {"label": "AI", "icon": "🤖", "color": "#06B6D4"},
    "bug": {"label": "באג", "icon": "🐛", "color": "#EF4444"},
}

PRIORITIES = {
    "low": {"label": "נמוכה", "color": "#10B981", "bg": "#D1FAE5"},
    "medium": {"label": "בינונית", "color": "#F59E0B", "bg": "#FEF3C7"},
    "high": {"label": "גבוהה", "color": "#EF4444", "bg": "#FEE2E2"},
}

# ======================
# CSS מקצועי
# ======================
st.markdown(f"""
<style>
    /* ייבוא פונט */
    @import url('https://fonts.googleapis.com/css2?family=Heebo:wght@300;400;500;600;700;800&display=swap');
    
    /* בסיס */
    * {{
        font-family: 'Heebo', sans-serif !important;
    }}
    
    .stApp {{
        direction: rtl;
        background: linear-gradient(180deg, #0F0F1A 0%, #1A1A2E 50%, #16213E 100%);
        min-height: 100vh;
    }}
    
    /* הסתרת אלמנטים של Streamlit */
    #MainMenu {{visibility: hidden;}}
    footer {{visibility: hidden;}}
    header {{visibility: hidden;}}
    .stDeployButton {{display: none;}}
    
    /* כותרות */
    h1, h2, h3, h4, h5, h6 {{
        text-align: right !important;
        color: #FFFFFF !important;
        font-weight: 700 !important;
    }}
    
    p, span, label, div {{
        color: #E2E8F0;
    }}
    
    /* Header מותאם */
    .main-header {{
        background: linear-gradient(135deg, rgba(99, 102, 241, 0.1) 0%, rgba(139, 92, 246, 0.1) 100%);
        backdrop-filter: blur(20px);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 24px;
        padding: 24px 32px;
        margin-bottom: 32px;
        display: flex;
        align-items: center;
        justify-content: space-between;
    }}
    
    .logo-section {{
        display: flex;
        align-items: center;
        gap: 16px;
    }}
    
    .logo-section img {{
        height: 60px;
        filter: drop-shadow(0 4px 12px rgba(99, 102, 241, 0.3));
    }}
    
    .brand-text {{
        font-size: 28px;
        font-weight: 800;
        background: linear-gradient(135deg, #6366F1 0%, #A855F7 50%, #EC4899 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
    }}
    
    /* Hero Section */
    .hero-section {{
        text-align: center;
        padding: 60px 20px;
        position: relative;
    }}
    
    .hero-title {{
        font-size: 48px;
        font-weight: 800;
        color: #FFFFFF;
        margin-bottom: 16px;
        text-shadow: 0 4px 20px rgba(99, 102, 241, 0.3);
    }}
    
    .hero-subtitle {{
        font-size: 20px;
        color: #94A3B8;
        margin-bottom: 40px;
    }}
    
    .mascot-container {{
        position: fixed;
        bottom: 20px;
        left: 20px;
        z-index: 1000;
        transition: all 0.3s ease;
    }}
    
    .mascot-container:hover {{
        transform: scale(1.05) translateY(-5px);
    }}
    
    .mascot-container img {{
        height: 120px;
        filter: drop-shadow(0 8px 24px rgba(0, 0, 0, 0.4));
        border-radius: 50%;
    }}
    
    .mascot-bubble {{
        position: absolute;
        bottom: 100%;
        left: 50%;
        transform: translateX(-50%);
        background: white;
        padding: 12px 16px;
        border-radius: 16px;
        font-size: 14px;
        color: #1E293B;
        white-space: nowrap;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.2);
        margin-bottom: 10px;
        opacity: 0;
        transition: opacity 0.3s ease;
    }}
    
    .mascot-container:hover .mascot-bubble {{
        opacity: 1;
    }}
    
    .mascot-bubble::after {{
        content: '';
        position: absolute;
        top: 100%;
        left: 50%;
        transform: translateX(-50%);
        border: 8px solid transparent;
        border-top-color: white;
    }}
    
    /* כרטיסים */
    .glass-card {{
        background: linear-gradient(135deg, rgba(255, 255, 255, 0.05) 0%, rgba(255, 255, 255, 0.02) 100%);
        backdrop-filter: blur(20px);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 20px;
        padding: 28px;
        margin-bottom: 20px;
        transition: all 0.3s ease;
    }}
    
    .glass-card:hover {{
        border-color: rgba(99, 102, 241, 0.3);
        box-shadow: 0 8px 32px rgba(99, 102, 241, 0.15);
        transform: translateY(-2px);
    }}
    
    /* טיימר */
    .timer-box {{
        background: linear-gradient(135deg, rgba(245, 158, 11, 0.2) 0%, rgba(251, 191, 36, 0.1) 100%);
        border: 1px solid rgba(245, 158, 11, 0.3);
        border-radius: 16px;
        padding: 20px;
        text-align: center;
    }}
    
    .timer-urgent {{
        background: linear-gradient(135deg, rgba(239, 68, 68, 0.2) 0%, rgba(248, 113, 113, 0.1) 100%);
        border-color: rgba(239, 68, 68, 0.3);
        animation: pulse 2s infinite;
    }}
    
    @keyframes pulse {{
        0%, 100% {{ opacity: 1; }}
        50% {{ opacity: 0.8; }}
    }}
    
    .timer-value {{
        font-size: 32px;
        font-weight: 800;
        color: #F59E0B;
    }}
    
    .timer-urgent .timer-value {{
        color: #EF4444;
    }}
    
    /* תגובות */
    .comment-card {{
        background: linear-gradient(135deg, rgba(255, 255, 255, 0.08) 0%, rgba(255, 255, 255, 0.03) 100%);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 16px;
        padding: 20px;
        margin-bottom: 16px;
        border-right: 4px solid #6366F1;
        transition: all 0.3s ease;
    }}
    
    .comment-card:hover {{
        background: linear-gradient(135deg, rgba(255, 255, 255, 0.12) 0%, rgba(255, 255, 255, 0.05) 100%);
    }}
    
    .comment-card.resolved {{
        opacity: 0.5;
        border-right-color: #475569;
    }}
    
    .comment-timestamp {{
        background: linear-gradient(135deg, #6366F1 0%, #8B5CF6 100%);
        color: white;
        padding: 6px 14px;
        border-radius: 10px;
        font-size: 13px;
        font-weight: 600;
        font-family: 'Monaco', monospace !important;
        display: inline-block;
    }}
    
    .comment-text {{
        color: #F1F5F9;
        font-size: 15px;
        line-height: 1.7;
        margin: 14px 0;
    }}
    
    .comment-author {{
        color: #64748B;
        font-size: 13px;
    }}
    
    /* תגיות */
    .tag {{
        display: inline-block;
        padding: 5px 14px;
        border-radius: 20px;
        font-size: 12px;
        font-weight: 600;
        margin-left: 8px;
    }}
    
    /* סטטיסטיקות */
    .stat-card {{
        background: linear-gradient(135deg, rgba(99, 102, 241, 0.15) 0%, rgba(139, 92, 246, 0.1) 100%);
        border: 1px solid rgba(99, 102, 241, 0.2);
        border-radius: 16px;
        padding: 20px;
        text-align: center;
    }}
    
    .stat-value {{
        font-size: 36px;
        font-weight: 800;
        color: #FFFFFF;
    }}
    
    .stat-label {{
        font-size: 14px;
        color: #94A3B8;
        margin-top: 4px;
    }}
    
    /* לינק */
    .link-box {{
        background: linear-gradient(135deg, rgba(16, 185, 129, 0.15) 0%, rgba(52, 211, 153, 0.1) 100%);
        border: 2px dashed rgba(16, 185, 129, 0.4);
        border-radius: 16px;
        padding: 20px;
        text-align: center;
    }}
    
    .link-box code {{
        background: rgba(255, 255, 255, 0.1);
        color: #34D399;
        padding: 10px 20px;
        border-radius: 10px;
        font-size: 14px;
        display: block;
        margin: 12px 0;
        word-break: break-all;
    }}
    
    /* Upload Area */
    .upload-area {{
        background: linear-gradient(135deg, rgba(99, 102, 241, 0.1) 0%, rgba(139, 92, 246, 0.05) 100%);
        border: 2px dashed rgba(99, 102, 241, 0.3);
        border-radius: 20px;
        padding: 40px;
        text-align: center;
        transition: all 0.3s ease;
    }}
    
    .upload-area:hover {{
        border-color: rgba(99, 102, 241, 0.6);
        background: linear-gradient(135deg, rgba(99, 102, 241, 0.15) 0%, rgba(139, 92, 246, 0.1) 100%);
    }}
    
    /* Inputs */
    .stTextInput > div > div > input,
    .stTextArea > div > div > textarea,
    .stSelectbox > div > div {{
        background: rgba(255, 255, 255, 0.05) !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
        border-radius: 12px !important;
        color: #F1F5F9 !important;
        font-size: 15px !important;
    }}
    
    .stTextInput > div > div > input:focus,
    .stTextArea > div > div > textarea:focus {{
        border-color: #6366F1 !important;
        box-shadow: 0 0 0 2px rgba(99, 102, 241, 0.2) !important;
    }}
    
    /* Buttons */
    .stButton > button {{
        background: linear-gradient(135deg, #6366F1 0%, #8B5CF6 100%) !important;
        color: white !important;
        border: none !important;
        border-radius: 12px !important;
        padding: 12px 28px !important;
        font-weight: 600 !important;
        font-size: 15px !important;
        transition: all 0.3s ease !important;
        box-shadow: 0 4px 15px rgba(99, 102, 241, 0.3) !important;
    }}
    
    .stButton > button:hover {{
        transform: translateY(-2px) !important;
        box-shadow: 0 6px 20px rgba(99, 102, 241, 0.4) !important;
    }}
    
    .stButton > button[kind="secondary"] {{
        background: rgba(255, 255, 255, 0.1) !important;
        box-shadow: none !important;
    }}
    
    /* Tabs */
    .stTabs [data-baseweb="tab-list"] {{
        background: rgba(255, 255, 255, 0.05);
        border-radius: 12px;
        padding: 4px;
        gap: 4px;
    }}
    
    .stTabs [data-baseweb="tab"] {{
        background: transparent;
        border-radius: 10px;
        color: #94A3B8;
        font-weight: 600;
    }}
    
    .stTabs [aria-selected="true"] {{
        background: linear-gradient(135deg, #6366F1 0%, #8B5CF6 100%) !important;
        color: white !important;
    }}
    
    /* Video Container */
    .video-container {{
        background: #000000;
        border-radius: 16px;
        overflow: hidden;
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.4);
    }}
    
    /* Metrics */
    [data-testid="stMetricValue"] {{
        color: #FFFFFF !important;
        font-size: 28px !important;
    }}
    
    [data-testid="stMetricLabel"] {{
        color: #94A3B8 !important;
    }}
    
    /* Divider */
    hr {{
        border-color: rgba(255, 255, 255, 0.1) !important;
        margin: 24px 0 !important;
    }}
    
    /* Welcome Box */
    .welcome-box {{
        background: linear-gradient(135deg, rgba(16, 185, 129, 0.15) 0%, rgba(52, 211, 153, 0.1) 100%);
        border: 1px solid rgba(16, 185, 129, 0.3);
        border-radius: 16px;
        padding: 20px;
        text-align: center;
        margin-bottom: 24px;
    }}
    
    .welcome-box span {{
        color: #34D399;
        font-size: 18px;
        font-weight: 600;
    }}
    
    /* Expander */
    .streamlit-expanderHeader {{
        background: rgba(255, 255, 255, 0.05) !important;
        border-radius: 12px !important;
        color: #F1F5F9 !important;
    }}
    
    /* Success/Error/Warning messages */
    .stSuccess, .stError, .stWarning, .stInfo {{
        border-radius: 12px !important;
    }}
    
</style>

<!-- Mascot -->
<div class="mascot-container">
    <div class="mascot-bubble">👋 צריך עזרה? אני כאן!</div>
    <img src="{MASCOT_URL}" alt="Kozy Mascot">
</div>
""", unsafe_allow_html=True)


# ======================
# Database Functions
# ======================
def init_db():
    """יצירת טבלאות אם לא קיימות"""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    
    c.execute('''
        CREATE TABLE IF NOT EXISTS projects (
            id TEXT PRIMARY KEY,
            title TEXT NOT NULL,
            description TEXT,
            video_filename TEXT NOT NULL,
            video_original_name TEXT,
            editor_token TEXT UNIQUE NOT NULL,
            client_token TEXT UNIQUE NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            expires_at TIMESTAMP NOT NULL,
            is_active INTEGER DEFAULT 1,
            view_count INTEGER DEFAULT 0,
            allow_download INTEGER DEFAULT 0
        )
    ''')
    
    c.execute('''
        CREATE TABLE IF NOT EXISTS comments (
            id TEXT PRIMARY KEY,
            project_id TEXT NOT NULL,
            timestamp_seconds REAL NOT NULL,
            text TEXT NOT NULL,
            author_name TEXT NOT NULL,
            author_type TEXT NOT NULL,
            category TEXT DEFAULT 'video',
            priority TEXT DEFAULT 'medium',
            resolved INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (project_id) REFERENCES projects (id)
        )
    ''')
    
    conn.commit()
    conn.close()


def generate_token(length=16):
    """יצירת טוקן ייחודי"""
    return hashlib.sha256(f"{uuid.uuid4()}{time.time()}".encode()).hexdigest()[:length]


def create_project(title, description, video_file):
    """יצירת פרויקט חדש"""
    project_id = str(uuid.uuid4())
    editor_token = generate_token(24)
    client_token = generate_token(16)
    
    # שמירת הקובץ
    video_filename = f"{project_id}_{video_file.name}"
    video_path = UPLOAD_DIR / video_filename
    
    with open(video_path, "wb") as f:
        f.write(video_file.getbuffer())
    
    # שמירה ב-DB
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    
    expires_at = datetime.now() + timedelta(hours=72)
    
    c.execute('''
        INSERT INTO projects (id, title, description, video_filename, video_original_name, 
                            editor_token, client_token, expires_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    ''', (project_id, title, description, video_filename, video_file.name, 
          editor_token, client_token, expires_at))
    
    conn.commit()
    conn.close()
    
    return project_id, editor_token, client_token


def get_project_by_editor_token(token):
    """קבלת פרויקט לפי טוקן עורך"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    
    c.execute('SELECT * FROM projects WHERE editor_token = ? AND is_active = 1', (token,))
    row = c.fetchone()
    conn.close()
    
    return dict(row) if row else None


def get_project_by_client_token(token):
    """קבלת פרויקט לפי טוקן לקוח"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    
    c.execute('SELECT * FROM projects WHERE client_token = ? AND is_active = 1', (token,))
    row = c.fetchone()
    
    if row:
        # עדכון מונה צפיות
        c.execute('UPDATE projects SET view_count = view_count + 1 WHERE client_token = ?', (token,))
        conn.commit()
    
    conn.close()
    return dict(row) if row else None


def delete_project(project_id):
    """מחיקת פרויקט"""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    
    # קבלת שם הקובץ למחיקה
    c.execute('SELECT video_filename FROM projects WHERE id = ?', (project_id,))
    row = c.fetchone()
    
    if row:
        video_path = UPLOAD_DIR / row[0]
        if video_path.exists():
            video_path.unlink()
    
    c.execute('UPDATE projects SET is_active = 0 WHERE id = ?', (project_id,))
    conn.commit()
    conn.close()


def add_comment(project_id, timestamp_seconds, text, author_name, author_type, category, priority):
    """הוספת תגובה"""
    comment_id = str(uuid.uuid4())
    
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    
    c.execute('''
        INSERT INTO comments (id, project_id, timestamp_seconds, text, author_name, 
                            author_type, category, priority)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    ''', (comment_id, project_id, timestamp_seconds, text, author_name, 
          author_type, category, priority))
    
    conn.commit()
    conn.close()
    
    return comment_id


def get_comments(project_id):
    """קבלת כל התגובות לפרויקט"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    
    c.execute('''
        SELECT * FROM comments WHERE project_id = ? 
        ORDER BY timestamp_seconds ASC
    ''', (project_id,))
    
    rows = c.fetchall()
    conn.close()
    
    return [dict(row) for row in rows]


def toggle_comment_resolved(comment_id):
    """החלפת סטטוס פתור"""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    
    c.execute('UPDATE comments SET resolved = NOT resolved WHERE id = ?', (comment_id,))
    conn.commit()
    conn.close()


def delete_comment(comment_id):
    """מחיקת תגובה"""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    
    c.execute('DELETE FROM comments WHERE id = ?', (comment_id,))
    conn.commit()
    conn.close()


def cleanup_expired_projects():
    """מחיקת פרויקטים שפג תוקפם"""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    
    # מציאת פרויקטים שפג תוקפם
    c.execute('''
        SELECT id, video_filename FROM projects 
        WHERE expires_at < ? AND is_active = 1
    ''', (datetime.now(),))
    
    expired = c.fetchall()
    
    for project_id, video_filename in expired:
        # מחיקת קובץ
        video_path = UPLOAD_DIR / video_filename
        if video_path.exists():
            video_path.unlink()
        
        # סימון כלא פעיל
        c.execute('UPDATE projects SET is_active = 0 WHERE id = ?', (project_id,))
    
    conn.commit()
    conn.close()
    
    return len(expired)


# ======================
# Helper Functions
# ======================
def format_time(seconds):
    """המרת שניות לפורמט MM:SS"""
    mins = int(seconds // 60)
    secs = int(seconds % 60)
    return f"{mins:02d}:{secs:02d}"


def get_time_remaining(expires_at):
    """חישוב זמן נותר"""
    if isinstance(expires_at, str):
        expires_at = datetime.fromisoformat(expires_at)
    
    remaining = expires_at - datetime.now()
    
    if remaining.total_seconds() <= 0:
        return None, "פג תוקף"
    
    hours = int(remaining.total_seconds() // 3600)
    minutes = int((remaining.total_seconds() % 3600) // 60)
    
    return remaining.total_seconds(), f"{hours} שעות ו-{minutes} דקות"


def get_base_url():
    """קבלת URL בסיסי של האפליקציה"""
    return "http://localhost:8501"


# ======================
# UI Components
# ======================
def render_header(title=None, show_back=False):
    """רנדור כותרת"""
    st.markdown(f"""
    <div class="main-header">
        <div class="logo-section">
            <img src="{LOGO_URL}" alt="Kozy Logo">
            <span class="brand-text">Kozy Review</span>
        </div>
        {f'<div style="color: #F1F5F9; font-size: 18px; font-weight: 600;">{title}</div>' if title else ''}
    </div>
    """, unsafe_allow_html=True)


def render_timer(expires_at):
    """רנדור טיימר ספירה לאחור"""
    remaining_seconds, remaining_text = get_time_remaining(expires_at)
    
    if remaining_seconds is None:
        st.error("⚠️ פג תוקף הפרויקט")
        return False
    
    is_urgent = remaining_seconds < 6 * 3600  # פחות מ-6 שעות
    
    css_class = "timer-urgent" if is_urgent else ""
    icon = "⚠️" if is_urgent else "⏱️"
    
    st.markdown(f"""
    <div class="timer-box {css_class}">
        <div style="font-size: 13px; color: #94A3B8; margin-bottom: 8px;">זמן נותר לצפייה</div>
        <div class="timer-value">{icon} {remaining_text}</div>
    </div>
    """, unsafe_allow_html=True)
    
    return True


def render_stats(comments):
    """רנדור סטטיסטיקות"""
    total = len(comments)
    resolved = len([c for c in comments if c['resolved']])
    high_priority = len([c for c in comments if c['priority'] == 'high' and not c['resolved']])
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown(f"""
        <div class="stat-card">
            <div class="stat-value">{total}</div>
            <div class="stat-label">סה״כ תגובות</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div class="stat-card" style="border-color: rgba(16, 185, 129, 0.3);">
            <div class="stat-value" style="color: #34D399;">{resolved}</div>
            <div class="stat-label">טופלו</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
        <div class="stat-card" style="border-color: rgba(239, 68, 68, 0.3);">
            <div class="stat-value" style="color: #F87171;">{high_priority}</div>
            <div class="stat-label">דחופות</div>
        </div>
        """, unsafe_allow_html=True)


def render_comment_card(comment, is_editor=False):
    """רנדור כרטיס תגובה"""
    cat = CATEGORIES.get(comment['category'], CATEGORIES['video'])
    pri = PRIORITIES.get(comment['priority'], PRIORITIES['medium'])
    
    resolved_class = "resolved" if comment['resolved'] else ""
    resolved_icon = "✅ " if comment['resolved'] else ""
    
    st.markdown(f"""
    <div class="comment-card {resolved_class}" style="border-right-color: {cat['color']};">
        <div style="display: flex; justify-content: space-between; align-items: start; flex-wrap: wrap; gap: 8px; margin-bottom: 12px;">
            <div style="display: flex; align-items: center; gap: 8px; flex-wrap: wrap;">
                <span class="comment-timestamp">⏱️ {format_time(comment['timestamp_seconds'])}</span>
                <span class="tag" style="background: {cat['color']}22; color: {cat['color']};">
                    {cat['icon']} {cat['label']}
                </span>
                <span class="tag" style="background: {pri['bg']}; color: {pri['color']};">
                    {pri['label']}
                </span>
            </div>
        </div>
        <p class="comment-text">{resolved_icon}{comment['text']}</p>
        <div class="comment-author">✍️ {comment['author_name']} • {('עורך' if comment['author_type'] == 'editor' else 'לקוח')}</div>
    </div>
    """, unsafe_allow_html=True)
    
    if is_editor:
        col1, col2 = st.columns([1, 1])
        with col1:
            if st.button(
                f"{'↩️ בטל סימון' if comment['resolved'] else '✅ סמן כטופל'}", 
                key=f"resolve_{comment['id']}",
                use_container_width=True
            ):
                toggle_comment_resolved(comment['id'])
                st.rerun()
        with col2:
            if st.button("🗑️ מחק", key=f"delete_{comment['id']}", use_container_width=True):
                delete_comment(comment['id'])
                st.rerun()


# ======================
# Pages
# ======================
def page_home():
    """עמוד בית - יצירת פרויקט או כניסה"""
    render_header()
    
    # Hero Section
    st.markdown(f"""
    <div class="hero-section">
        <h1 class="hero-title">סקירת וידאו מקצועית</h1>
        <p class="hero-subtitle">שתף סרטונים עם לקוחות וקבל פידבק מדויק עם חותמות זמן</p>
    </div>
    """, unsafe_allow_html=True)
    
    tab1, tab2 = st.tabs(["📤 העלאת פרויקט חדש", "🔗 כניסה עם לינק"])
    
    with tab1:
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        
        st.markdown("### 📝 פרטי הפרויקט")
        
        title = st.text_input("שם הפרויקט *", placeholder="לדוגמה: פרסומת חורף 2025")
        description = st.text_area("תיאור (אופציונלי)", placeholder="גרסה ראשונה לאישור...", height=80)
        
        st.markdown("### 🎬 העלאת וידאו")
        
        video_file = st.file_uploader(
            "גרור קובץ לכאן או לחץ לבחירה",
            type=["mp4", "mov", "webm", "avi", "mkv"],
            help="פורמטים נתמכים: MP4, MOV, WebM, AVI, MKV"
        )
        
        if video_file:
            st.video(video_file)
            file_size = video_file.size / (1024*1024)
            st.success(f"✅ **{video_file.name}** ({file_size:.1f} MB)")
        
        st.markdown("</div>", unsafe_allow_html=True)
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        if st.button("🚀 צור פרויקט ושלח ללקוח", type="primary", disabled=not (title and video_file), use_container_width=True):
            with st.spinner("⏳ מעלה את הסרטון..."):
                project_id, editor_token, client_token = create_project(title, description, video_file)
            
            st.success("✅ הפרויקט נוצר בהצלחה!")
            st.balloons()
            
            # שמירת הטוקן ב-session
            st.session_state['editor_token'] = editor_token
            
            base_url = get_base_url()
            client_link = f"{base_url}/?view={client_token}"
            editor_link = f"{base_url}/?edit={editor_token}"
            
            st.markdown("### 🔗 הלינקים שלך")
            
            st.markdown(f"""
            <div class="link-box">
                <div style="font-size: 14px; color: #94A3B8; margin-bottom: 8px;">📤 לינק ללקוח (שתף אותו!):</div>
                <code>{client_link}</code>
            </div>
            """, unsafe_allow_html=True)
            
            st.code(client_link, language=None)
            
            with st.expander("🔐 לינק עריכה (שמור לעצמך!)"):
                st.code(editor_link, language=None)
            
            st.warning("⏰ **שים לב:** הפרויקט יימחק אוטומטית בעוד **72 שעות**!")
    
    with tab2:
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        
        st.markdown("### 🔑 יש לך לינק?")
        st.markdown("הדבק את הלינק שקיבלת מהעורך")
        
        link_input = st.text_input("הדבק לינק כאן", placeholder="https://...", label_visibility="collapsed")
        
        if st.button("🔓 כניסה", use_container_width=True):
            if "view=" in link_input:
                token = link_input.split("view=")[-1].split("&")[0]
                st.query_params["view"] = token
                st.rerun()
            elif "edit=" in link_input:
                token = link_input.split("edit=")[-1].split("&")[0]
                st.query_params["edit"] = token
                st.rerun()
            else:
                st.error("❌ לינק לא תקין. וודא שהדבקת את הלינק המלא.")
        
        st.markdown("</div>", unsafe_allow_html=True)


def page_editor(project):
    """עמוד עריכה - לעורך"""
    render_header(project['title'])
    
    # Layout
    col_main, col_side = st.columns([2, 1])
    
    with col_side:
        # טיימר
        if not render_timer(project['expires_at']):
            return
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        # לינק ללקוח
        base_url = get_base_url()
        client_link = f"{base_url}/?view={project['client_token']}"
        
        st.markdown(f"""
        <div class="link-box">
            <div style="font-size: 13px; color: #94A3B8; margin-bottom: 8px;">🔗 לינק ללקוח:</div>
            <code style="font-size: 12px;">{client_link}</code>
        </div>
        """, unsafe_allow_html=True)
        
        st.code(client_link, language=None)
        
        st.markdown(f"<p style='text-align: center; color: #64748B; font-size: 13px;'>👁️ נצפה {project['view_count']} פעמים</p>", unsafe_allow_html=True)
        
        st.markdown("---")
        
        # סטטיסטיקות
        comments = get_comments(project['id'])
        render_stats(comments)
        
        st.markdown("---")
        
        # מחיקה
        with st.expander("⚠️ מחיקת פרויקט"):
            st.warning("פעולה זו תמחק את הפרויקט לצמיתות!")
            if st.button("🗑️ מחק פרויקט", type="secondary", use_container_width=True):
                delete_project(project['id'])
                st.query_params.clear()
                st.rerun()
    
    with col_main:
        # נגן וידאו
        video_path = UPLOAD_DIR / project['video_filename']
        if video_path.exists():
            st.video(str(video_path))
        else:
            st.error("❌ קובץ הוידאו לא נמצא")
            return
        
        # הוספת תגובה
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        st.markdown("### 💬 הוסף הערה חדשה")
        
        col_time, col_cat, col_pri = st.columns([1, 2, 2])
        
        with col_time:
            st.markdown("**⏱️ נקודת זמן:**")
            c1, c2 = st.columns(2)
            with c1:
                minutes = st.number_input("דקות", min_value=0, value=0, key="ed_min")
            with c2:
                seconds = st.number_input("שניות", min_value=0, max_value=59, value=0, key="ed_sec")
        
        with col_cat:
            category = st.selectbox(
                "🏷️ קטגוריה",
                options=list(CATEGORIES.keys()),
                format_func=lambda x: f"{CATEGORIES[x]['icon']} {CATEGORIES[x]['label']}"
            )
        
        with col_pri:
            priority = st.selectbox(
                "⚡ עדיפות",
                options=list(PRIORITIES.keys()),
                format_func=lambda x: PRIORITIES[x]['label']
            )
        
        comment_text = st.text_area("📝 תוכן ההערה", placeholder="כתוב את ההערה שלך...", height=100)
        
        if st.button("➕ הוסף הערה", disabled=not comment_text, use_container_width=True):
            timestamp = minutes * 60 + seconds
            add_comment(project['id'], timestamp, comment_text, "עורך", "editor", category, priority)
            st.success("✅ ההערה נוספה!")
            st.rerun()
        
        st.markdown("</div>", unsafe_allow_html=True)
        
        # רשימת תגובות
        st.markdown("---")
        st.markdown("### 📋 כל ההערות")
        
        comments = get_comments(project['id'])
        
        # סינון
        filter_option = st.selectbox(
            "🔍 סינון",
            ["הכל", "לא טופלו", "טופלו"] + [f"{c['icon']} {c['label']}" for c in CATEGORIES.values()]
        )
        
        if not comments:
            st.info("📭 עדיין אין הערות. הוסף את ההערה הראשונה!")
        
        for comment in comments:
            # סינון
            if filter_option == "לא טופלו" and comment['resolved']:
                continue
            if filter_option == "טופלו" and not comment['resolved']:
                continue
            if filter_option not in ["הכל", "לא טופלו", "טופלו"]:
                cat_label = f"{CATEGORIES[comment['category']]['icon']} {CATEGORIES[comment['category']]['label']}"
                if filter_option != cat_label:
                    continue
            
            render_comment_card(comment, is_editor=True)


def page_client(project):
    """עמוד צפייה - ללקוח"""
    render_header(project['title'])
    
    # הודעת ברוכים הבאים
    st.markdown(f"""
    <div class="welcome-box">
        <span>👋 שלום! צפה בסרטון והוסף את המשוב שלך</span>
    </div>
    """, unsafe_allow_html=True)
    
    # Layout
    col_main, col_side = st.columns([3, 1])
    
    with col_side:
        if not render_timer(project['expires_at']):
            st.error("⏰ הסרטון כבר לא זמין")
            return
    
    with col_main:
        # נגן וידאו
        video_path = UPLOAD_DIR / project['video_filename']
        if video_path.exists():
            st.video(str(video_path))
        else:
            st.error("❌ קובץ הוידאו לא נמצא")
            return
    
    # הוספת משוב
    st.markdown("---")
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    st.markdown("### 💬 הוסף משוב")
    
    col_name, col_time = st.columns([2, 1])
    
    with col_name:
        author_name = st.text_input("👤 השם שלך *", placeholder="הכנס את שמך...")
    
    with col_time:
        st.markdown("**⏱️ נקודת זמן:**")
        c1, c2 = st.columns(2)
        with c1:
            minutes = st.number_input("דקות", min_value=0, value=0, key="cl_min")
        with c2:
            seconds = st.number_input("שניות", min_value=0, max_value=59, value=0, key="cl_sec")
    
    col_cat, col_pri = st.columns(2)
    
    with col_cat:
        category = st.selectbox(
            "🏷️ קטגוריה",
            options=list(CATEGORIES.keys()),
            format_func=lambda x: f"{CATEGORIES[x]['icon']} {CATEGORIES[x]['label']}",
            key="cl_cat"
        )
    
    with col_pri:
        priority = st.selectbox(
            "⚡ עדיפות",
            options=list(PRIORITIES.keys()),
            format_func=lambda x: PRIORITIES[x]['label'],
            key="cl_pri"
        )
    
    comment_text = st.text_area("📝 המשוב שלך *", placeholder="כתוב את המשוב שלך כאן...", height=120)
    
    if st.button("📤 שלח משוב", type="primary", disabled=not (author_name and comment_text), use_container_width=True):
        timestamp = minutes * 60 + seconds
        add_comment(project['id'], timestamp, comment_text, author_name, "client", category, priority)
        st.success("✅ המשוב נשלח בהצלחה! תודה רבה!")
        st.balloons()
        st.rerun()
    
    st.markdown("</div>", unsafe_allow_html=True)
    
    # הצגת משובים קודמים
    st.markdown("---")
    st.markdown("### 📋 משובים שנשלחו")
    
    comments = get_comments(project['id'])
    
    if not comments:
        st.info("📭 עדיין אין משובים. היה הראשון! 🎉")
    else:
        for comment in comments:
            render_comment_card(comment, is_editor=False)


# ======================
# Main App
# ======================
def main():
    # אתחול DB
    init_db()
    
    # ניקוי פרויקטים שפג תוקפם
    cleanup_expired_projects()
    
    # בדיקת query params
    params = st.query_params
    
    if "edit" in params:
        # עמוד עריכה
        project = get_project_by_editor_token(params["edit"])
        if project:
            page_editor(project)
        else:
            st.error("❌ פרויקט לא נמצא או שפג תוקפו")
            if st.button("🏠 חזרה לדף הבית"):
                st.query_params.clear()
                st.rerun()
    
    elif "view" in params:
        # עמוד לקוח
        project = get_project_by_client_token(params["view"])
        if project:
            page_client(project)
        else:
            st.error("❌ הסרטון לא נמצא או שפג תוקפו")
            st.info("💡 ייתכן שעברו 72 שעות מאז העלאת הסרטון והוא נמחק אוטומטית.")
    
    else:
        # עמוד בית
        page_home()


if __name__ == "__main__":
    main()