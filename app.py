import streamlit as st
import sqlite3
import os
import uuid
import hashlib
from datetime import datetime, timedelta
from pathlib import Path
import time

# ======================
# הגדרות בסיסיות
# ======================
st.set_page_config(
    page_title="Kozy Review",
    page_icon="https://i.postimg.cc/7LMZ1dLJ/קוזי.png",
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
BG_IMAGE_URL = "https://i.postimg.cc/pTGtWyzv/Whats-App-Image-2026-01-21-at-01-16-53.jpg"

# ======================
# עיצוב - Design System
# ======================

# צבעים - פלטה מינימליסטית ומקצועית
COLORS = {
    # Primary - כחול-סגול עמוק ומקצועי
    "primary": "#6C5CE7",
    "primary_light": "#A29BFE",
    "primary_dark": "#5541D7",
    
    # Neutral - גווני אפור
    "bg_dark": "#0D0D12",
    "bg_card": "#16161D",
    "bg_elevated": "#1E1E28",
    "border": "#2A2A36",
    "text_primary": "#FFFFFF",
    "text_secondary": "#9CA3AF",
    "text_muted": "#6B7280",
    
    # Accent
    "success": "#10B981",
    "warning": "#F59E0B",
    "error": "#EF4444",
    "info": "#3B82F6",
}

# קטגוריות - צבעים מותאמים
CATEGORIES = {
    "video": {"label": "וידאו", "icon": "🎬", "color": "#818CF8"},
    "image": {"label": "תמונה", "icon": "🖼️", "color": "#C084FC"},
    "effect": {"label": "אפקט", "icon": "✨", "color": "#FBBF24"},
    "subtitles": {"label": "כתוביות", "icon": "💬", "color": "#34D399"},
    "transition": {"label": "מעבר", "icon": "🔄", "color": "#FB923C"},
    "music": {"label": "מוזיקה", "icon": "🎵", "color": "#F472B6"},
    "sound": {"label": "סאונד", "icon": "🔊", "color": "#60A5FA"},
    "ai": {"label": "AI", "icon": "🤖", "color": "#22D3EE"},
    "bug": {"label": "באג", "icon": "🐛", "color": "#F87171"},
}

PRIORITIES = {
    "low": {"label": "נמוכה", "color": "#10B981", "bg": "rgba(16, 185, 129, 0.15)"},
    "medium": {"label": "בינונית", "color": "#F59E0B", "bg": "rgba(245, 158, 11, 0.15)"},
    "high": {"label": "גבוהה", "color": "#EF4444", "bg": "rgba(239, 68, 68, 0.15)"},
}

# ======================
# CSS מקצועי - Design System
# ======================
def load_css():
    st.markdown(f"""
<style>
    /* ===== RESET & BASE ===== */
    @import url('https://fonts.googleapis.com/css2?family=Heebo:wght@300;400;500;600;700;800;900&display=swap');
    
    * {{
        font-family: 'Heebo', -apple-system, BlinkMacSystemFont, sans-serif !important;
        box-sizing: border-box;
    }}
    
    /* Main app container with background */
    .stApp {{
        direction: rtl;
        background-color: #0a0a0f;
        background-image: url('{BG_IMAGE_URL}');
        background-size: cover;
        background-position: center;
        background-repeat: no-repeat;
        background-attachment: fixed;
    }}
    
    /* Dark overlay for 45% opacity effect */
    .stApp > div:first-child {{
        background: rgba(10, 10, 15, 0.55);
        min-height: 100vh;
    }}
    
    [data-testid="stAppViewContainer"] {{
        background: rgba(10, 10, 15, 0.55);
    }}
    
    [data-testid="stHeader"] {{
        background: transparent;
    }}
    
    /* Hide Streamlit branding */
    #MainMenu, footer, header {{visibility: hidden;}}
    .stDeployButton {{display: none;}}
    
    /* ===== TYPOGRAPHY ===== */
    h1 {{
        font-size: 2.5rem !important;
        font-weight: 800 !important;
        color: #FFFFFF !important;
        letter-spacing: -0.02em !important;
        margin-bottom: 0.5rem !important;
        text-shadow: 0 2px 10px rgba(0,0,0,0.5);
    }}
    
    h2 {{
        font-size: 1.5rem !important;
        font-weight: 700 !important;
        color: #FFFFFF !important;
        letter-spacing: -0.01em !important;
        text-shadow: 0 2px 8px rgba(0,0,0,0.4);
    }}
    
    h3 {{
        font-size: 1.125rem !important;
        font-weight: 600 !important;
        color: #FFFFFF !important;
        text-shadow: 0 1px 6px rgba(0,0,0,0.3);
    }}
    
    p, span, div {{
        color: rgba(255,255,255,0.85);
        line-height: 1.6;
    }}
    
    /* ===== LAYOUT ===== */
    .block-container {{
        padding: 2rem 3rem !important;
        max-width: 1400px !important;
    }}
    
    /* ===== HEADER ===== */
    .kozy-header {{
        display: flex;
        align-items: center;
        justify-content: space-between;
        padding: 1.25rem 2rem;
        background: rgba(15, 15, 25, 0.85);
        backdrop-filter: blur(20px);
        -webkit-backdrop-filter: blur(20px);
        border: 1px solid rgba(255,255,255,0.1);
        border-radius: 16px;
        margin-bottom: 2rem;
        box-shadow: 0 8px 32px rgba(0,0,0,0.3);
    }}
    
    .kozy-logo {{
        display: flex;
        align-items: center;
        gap: 1rem;
    }}
    
    .kozy-logo img {{
        height: 48px;
        object-fit: contain;
    }}
    
    .kozy-logo-text {{
        font-size: 1.5rem;
        font-weight: 800;
        color: #FFFFFF;
        letter-spacing: -0.02em;
        text-shadow: 0 2px 8px rgba(0,0,0,0.3);
    }}
    
    /* ===== HERO SECTION ===== */
    .hero {{
        text-align: center;
        padding: 4rem 2rem;
        margin-bottom: 2rem;
        background: rgba(15, 15, 25, 0.6);
        backdrop-filter: blur(10px);
        -webkit-backdrop-filter: blur(10px);
        border-radius: 24px;
        border: 1px solid rgba(255,255,255,0.08);
    }}
    
    .hero-title {{
        font-size: 3rem;
        font-weight: 900;
        color: #FFFFFF;
        margin-bottom: 1rem;
        letter-spacing: -0.03em;
        text-shadow: 0 4px 20px rgba(0,0,0,0.5);
    }}
    
    .hero-subtitle {{
        font-size: 1.25rem;
        color: rgba(255,255,255,0.75);
        max-width: 500px;
        margin: 0 auto;
        line-height: 1.7;
    }}
    
    /* ===== CARDS - Glass Morphism ===== */
    .card {{
        background: rgba(15, 15, 25, 0.75);
        backdrop-filter: blur(16px);
        -webkit-backdrop-filter: blur(16px);
        border: 1px solid rgba(255,255,255,0.1);
        border-radius: 16px;
        padding: 1.5rem;
        transition: all 0.3s ease;
        box-shadow: 0 8px 32px rgba(0,0,0,0.2);
    }}
    
    .card:hover {{
        border-color: rgba(108, 92, 231, 0.5);
        box-shadow: 0 12px 40px rgba(108, 92, 231, 0.15);
        transform: translateY(-2px);
    }}
    
    .card-elevated {{
        background: rgba(20, 20, 35, 0.8);
        backdrop-filter: blur(20px);
        -webkit-backdrop-filter: blur(20px);
        border: 1px solid rgba(255,255,255,0.1);
        border-radius: 20px;
        padding: 2rem;
        box-shadow: 0 12px 40px rgba(0,0,0,0.25);
    }}
    
    /* ===== VIDEO CONTAINER ===== */
    .video-wrapper {{
        background: #000;
        border-radius: 16px;
        overflow: hidden;
        box-shadow: 0 25px 60px -12px rgba(0, 0, 0, 0.6);
        margin-bottom: 1.5rem;
        border: 1px solid rgba(255,255,255,0.1);
    }}
    
    .video-wrapper video {{
        width: 100%;
        display: block;
    }}
    
    /* ===== TIMER ===== */
    .timer {{
        background: rgba(20, 20, 35, 0.85);
        backdrop-filter: blur(16px);
        -webkit-backdrop-filter: blur(16px);
        border: 1px solid rgba(255,255,255,0.1);
        border-radius: 16px;
        padding: 1.5rem;
        text-align: center;
        box-shadow: 0 8px 32px rgba(0,0,0,0.2);
    }}
    
    .timer-label {{
        font-size: 0.75rem;
        font-weight: 600;
        color: rgba(255,255,255,0.5);
        text-transform: uppercase;
        letter-spacing: 0.05em;
        margin-bottom: 0.5rem;
    }}
    
    .timer-value {{
        font-size: 1.75rem;
        font-weight: 800;
        color: {COLORS['warning']};
        text-shadow: 0 2px 10px rgba(245, 158, 11, 0.3);
    }}
    
    .timer-urgent .timer-value {{
        color: {COLORS['error']};
        animation: pulse 1.5s ease-in-out infinite;
        text-shadow: 0 2px 10px rgba(239, 68, 68, 0.4);
    }}
    
    @keyframes pulse {{
        0%, 100% {{ opacity: 1; }}
        50% {{ opacity: 0.6; }}
    }}
    
    /* ===== STATS ===== */
    .stat-grid {{
        display: grid;
        grid-template-columns: repeat(3, 1fr);
        gap: 1rem;
        margin-bottom: 1.5rem;
    }}
    
    .stat-item {{
        background: rgba(20, 20, 35, 0.8);
        backdrop-filter: blur(12px);
        -webkit-backdrop-filter: blur(12px);
        border: 1px solid rgba(255,255,255,0.1);
        border-radius: 12px;
        padding: 1rem;
        text-align: center;
        box-shadow: 0 4px 16px rgba(0,0,0,0.15);
    }}
    
    .stat-value {{
        font-size: 2rem;
        font-weight: 800;
        color: #FFFFFF;
        line-height: 1;
        text-shadow: 0 2px 8px rgba(0,0,0,0.3);
    }}
    
    .stat-label {{
        font-size: 0.75rem;
        font-weight: 500;
        color: rgba(255,255,255,0.5);
        margin-top: 0.25rem;
    }}
    
    /* ===== LINK BOX ===== */
    .link-box {{
        background: rgba(108, 92, 231, 0.15);
        backdrop-filter: blur(12px);
        -webkit-backdrop-filter: blur(12px);
        border: 1px dashed rgba(108, 92, 231, 0.5);
        border-radius: 12px;
        padding: 1.25rem;
        text-align: center;
    }}
    
    .link-box-label {{
        font-size: 0.75rem;
        font-weight: 600;
        color: rgba(255,255,255,0.6);
        margin-bottom: 0.75rem;
    }}
    
    .link-box-url {{
        background: rgba(0,0,0,0.4);
        color: {COLORS['primary_light']};
        padding: 0.75rem 1rem;
        border-radius: 8px;
        font-size: 0.875rem;
        font-family: 'Monaco', monospace !important;
        word-break: break-all;
        display: block;
    }}
    
    /* ===== COMMENTS ===== */
    .comment {{
        background: rgba(20, 20, 35, 0.75);
        backdrop-filter: blur(12px);
        -webkit-backdrop-filter: blur(12px);
        border: 1px solid rgba(255,255,255,0.08);
        border-radius: 12px;
        padding: 1.25rem;
        margin-bottom: 1rem;
        border-right: 3px solid {COLORS['primary']};
        transition: all 0.3s ease;
        box-shadow: 0 4px 20px rgba(0,0,0,0.15);
    }}
    
    .comment:hover {{
        background: rgba(25, 25, 45, 0.85);
        border-color: rgba(255,255,255,0.15);
        transform: translateX(-4px);
    }}
    
    .comment.resolved {{
        opacity: 0.5;
        border-right-color: rgba(255,255,255,0.2);
    }}
    
    .comment-header {{
        display: flex;
        align-items: center;
        gap: 0.75rem;
        flex-wrap: wrap;
        margin-bottom: 0.75rem;
    }}
    
    .comment-time {{
        background: linear-gradient(135deg, {COLORS['primary']} 0%, {COLORS['primary_dark']} 100%);
        color: white;
        padding: 0.25rem 0.75rem;
        border-radius: 6px;
        font-size: 0.8125rem;
        font-weight: 600;
        font-family: 'Monaco', monospace !important;
        box-shadow: 0 2px 8px rgba(108, 92, 231, 0.3);
    }}
    
    .comment-tag {{
        padding: 0.25rem 0.625rem;
        border-radius: 6px;
        font-size: 0.75rem;
        font-weight: 600;
        backdrop-filter: blur(8px);
    }}
    
    .comment-text {{
        color: #FFFFFF;
        font-size: 0.9375rem;
        line-height: 1.6;
        margin-bottom: 0.75rem;
    }}
    
    .comment-meta {{
        font-size: 0.75rem;
        color: rgba(255,255,255,0.5);
    }}
    
    /* ===== WELCOME BOX (Client) ===== */
    .welcome {{
        background: rgba(108, 92, 231, 0.12);
        backdrop-filter: blur(16px);
        -webkit-backdrop-filter: blur(16px);
        border: 1px solid rgba(108, 92, 231, 0.25);
        border-radius: 16px;
        padding: 1.5rem 2rem;
        text-align: center;
        margin-bottom: 2rem;
        box-shadow: 0 8px 32px rgba(108, 92, 231, 0.1);
    }}
    
    .welcome-text {{
        font-size: 1.125rem;
        font-weight: 600;
        color: #FFFFFF;
        text-shadow: 0 2px 8px rgba(0,0,0,0.3);
    }}
    
    .welcome-subtext {{
        font-size: 0.875rem;
        color: rgba(255,255,255,0.7);
        margin-top: 0.5rem;
    }}
    
    /* ===== FORM INPUTS ===== */
    .stTextInput > div > div > input,
    .stTextArea > div > div > textarea {{
        background: rgba(20, 20, 35, 0.8) !important;
        backdrop-filter: blur(12px) !important;
        border: 1px solid rgba(255,255,255,0.12) !important;
        border-radius: 10px !important;
        color: #FFFFFF !important;
        font-size: 0.9375rem !important;
        padding: 0.75rem 1rem !important;
    }}
    
    .stTextInput > div > div > input:focus,
    .stTextArea > div > div > textarea:focus {{
        border-color: {COLORS['primary']} !important;
        box-shadow: 0 0 0 3px rgba(108, 92, 231, 0.2) !important;
    }}
    
    .stTextInput > div > div > input::placeholder,
    .stTextArea > div > div > textarea::placeholder {{
        color: rgba(255,255,255,0.4) !important;
    }}
    
    .stSelectbox > div > div {{
        background: rgba(20, 20, 35, 0.8) !important;
        border: 1px solid rgba(255,255,255,0.12) !important;
        border-radius: 10px !important;
    }}
    
    .stSelectbox > div > div > div {{
        color: #FFFFFF !important;
    }}
    
    .stNumberInput > div > div > input {{
        background: rgba(20, 20, 35, 0.8) !important;
        border: 1px solid rgba(255,255,255,0.12) !important;
        border-radius: 10px !important;
        color: #FFFFFF !important;
    }}
    
    /* Labels */
    .stTextInput > label,
    .stTextArea > label,
    .stSelectbox > label,
    .stNumberInput > label {{
        color: rgba(255,255,255,0.75) !important;
        font-weight: 500 !important;
        font-size: 0.875rem !important;
        margin-bottom: 0.5rem !important;
    }}
    
    /* ===== BUTTONS ===== */
    .stButton > button {{
        background: linear-gradient(135deg, {COLORS['primary']} 0%, {COLORS['primary_dark']} 100%) !important;
        color: white !important;
        border: none !important;
        border-radius: 10px !important;
        padding: 0.75rem 1.5rem !important;
        font-weight: 600 !important;
        font-size: 0.9375rem !important;
        transition: all 0.3s ease !important;
        box-shadow: 0 4px 20px rgba(108, 92, 231, 0.4) !important;
    }}
    
    .stButton > button:hover {{
        transform: translateY(-3px) !important;
        box-shadow: 0 8px 30px rgba(108, 92, 231, 0.5) !important;
    }}
    
    .stButton > button:active {{
        transform: translateY(0) !important;
    }}
    
    /* Secondary buttons */
    .stButton > button[kind="secondary"] {{
        background: rgba(20, 20, 35, 0.7) !important;
        backdrop-filter: blur(12px) !important;
        border: 1px solid rgba(255,255,255,0.15) !important;
        box-shadow: 0 4px 16px rgba(0,0,0,0.2) !important;
    }}
    
    .stButton > button[kind="secondary"]:hover {{
        background: rgba(30, 30, 50, 0.8) !important;
        border-color: {COLORS['primary']} !important;
    }}
    
    /* ===== TABS ===== */
    .stTabs [data-baseweb="tab-list"] {{
        background: rgba(15, 15, 25, 0.8);
        backdrop-filter: blur(16px);
        -webkit-backdrop-filter: blur(16px);
        border-radius: 12px;
        padding: 0.375rem;
        gap: 0.25rem;
        border: 1px solid rgba(255,255,255,0.1);
    }}
    
    .stTabs [data-baseweb="tab"] {{
        background: transparent;
        border-radius: 8px;
        color: rgba(255,255,255,0.6);
        font-weight: 500;
        padding: 0.625rem 1.25rem;
    }}
    
    .stTabs [aria-selected="true"] {{
        background: linear-gradient(135deg, {COLORS['primary']} 0%, {COLORS['primary_dark']} 100%) !important;
        color: white !important;
        box-shadow: 0 4px 12px rgba(108, 92, 231, 0.3);
    }}
    
    /* ===== DIVIDER ===== */
    hr {{
        border: none !important;
        height: 1px !important;
        background: rgba(255,255,255,0.1) !important;
        margin: 2rem 0 !important;
    }}
    
    /* ===== FILE UPLOADER ===== */
    .stFileUploader {{
        background: rgba(15, 15, 25, 0.7);
        backdrop-filter: blur(16px);
        -webkit-backdrop-filter: blur(16px);
        border: 2px dashed rgba(255,255,255,0.15);
        border-radius: 16px;
        padding: 2rem;
        transition: all 0.3s ease;
    }}
    
    .stFileUploader:hover {{
        border-color: {COLORS['primary']};
        background: rgba(108, 92, 231, 0.1);
    }}
    
    .stFileUploader > div {{
        color: rgba(255,255,255,0.7) !important;
    }}
    
    /* ===== ALERTS ===== */
    .stSuccess {{
        background: rgba(16, 185, 129, 0.15) !important;
        backdrop-filter: blur(12px) !important;
        border: 1px solid rgba(16, 185, 129, 0.3) !important;
        border-radius: 10px !important;
    }}
    
    .stError {{
        background: rgba(239, 68, 68, 0.15) !important;
        backdrop-filter: blur(12px) !important;
        border: 1px solid rgba(239, 68, 68, 0.3) !important;
        border-radius: 10px !important;
    }}
    
    .stWarning {{
        background: rgba(245, 158, 11, 0.15) !important;
        backdrop-filter: blur(12px) !important;
        border: 1px solid rgba(245, 158, 11, 0.3) !important;
        border-radius: 10px !important;
    }}
    
    .stInfo {{
        background: rgba(59, 130, 246, 0.15) !important;
        backdrop-filter: blur(12px) !important;
        border: 1px solid rgba(59, 130, 246, 0.3) !important;
        border-radius: 10px !important;
    }}
    
    /* ===== EXPANDER ===== */
    .streamlit-expanderHeader {{
        background: rgba(20, 20, 35, 0.8) !important;
        backdrop-filter: blur(12px) !important;
        border-radius: 10px !important;
        color: #FFFFFF !important;
        font-weight: 500 !important;
    }}
    
    /* ===== MASCOT ===== */
    .mascot {{
        position: fixed;
        bottom: 24px;
        left: 24px;
        z-index: 9999;
        transition: transform 0.3s ease;
    }}
    
    .mascot:hover {{
        transform: scale(1.1) translateY(-6px);
    }}
    
    .mascot img {{
        height: 100px;
        filter: drop-shadow(0 12px 32px rgba(0, 0, 0, 0.5));
        border-radius: 50%;
    }}
    
    /* ===== METRICS ===== */
    [data-testid="stMetricValue"] {{
        color: #FFFFFF !important;
        font-size: 1.75rem !important;
        font-weight: 800 !important;
        text-shadow: 0 2px 8px rgba(0,0,0,0.3);
    }}
    
    [data-testid="stMetricLabel"] {{
        color: rgba(255,255,255,0.5) !important;
        font-size: 0.75rem !important;
        font-weight: 600 !important;
        text-transform: uppercase !important;
        letter-spacing: 0.05em !important;
    }}
    
    /* ===== COMPLETED STATE ===== */
    .completed-box {{
        background: rgba(16, 185, 129, 0.15);
        backdrop-filter: blur(16px);
        -webkit-backdrop-filter: blur(16px);
        border: 1px solid rgba(16, 185, 129, 0.3);
        border-radius: 16px;
        padding: 2rem;
        text-align: center;
        box-shadow: 0 8px 32px rgba(16, 185, 129, 0.15);
    }}
    
    .completed-icon {{
        font-size: 3rem;
        margin-bottom: 1rem;
    }}
    
    .completed-title {{
        font-size: 1.25rem;
        font-weight: 700;
        color: {COLORS['success']};
        margin-bottom: 0.5rem;
        text-shadow: 0 2px 8px rgba(16, 185, 129, 0.3);
    }}
    
    .completed-text {{
        color: rgba(255,255,255,0.7);
        font-size: 0.9375rem;
    }}
    
</style>

<!-- Mascot -->
<div class="mascot">
    <img src="{MASCOT_URL}" alt="Kozy">
</div>
""", unsafe_allow_html=True)


# ======================
# Database Functions
# ======================
def init_db():
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
            view_count INTEGER DEFAULT 0
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
    return hashlib.sha256(f"{uuid.uuid4()}{time.time()}".encode()).hexdigest()[:length]


def create_project(title, description, video_file):
    project_id = str(uuid.uuid4())
    editor_token = generate_token(24)
    client_token = generate_token(16)
    
    video_filename = f"{project_id}_{video_file.name}"
    video_path = UPLOAD_DIR / video_filename
    
    with open(video_path, "wb") as f:
        f.write(video_file.getbuffer())
    
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
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    c.execute('SELECT * FROM projects WHERE editor_token = ? AND is_active = 1', (token,))
    row = c.fetchone()
    conn.close()
    return dict(row) if row else None


def get_project_by_client_token(token):
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    c.execute('SELECT * FROM projects WHERE client_token = ? AND is_active = 1', (token,))
    row = c.fetchone()
    if row:
        c.execute('UPDATE projects SET view_count = view_count + 1 WHERE client_token = ?', (token,))
        conn.commit()
    conn.close()
    return dict(row) if row else None


def delete_project(project_id):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
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
    comment_id = str(uuid.uuid4())
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''
        INSERT INTO comments (id, project_id, timestamp_seconds, text, author_name, 
                            author_type, category, priority)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    ''', (comment_id, project_id, timestamp_seconds, text, author_name, author_type, category, priority))
    conn.commit()
    conn.close()
    return comment_id


def get_comments(project_id):
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    c.execute('SELECT * FROM comments WHERE project_id = ? ORDER BY timestamp_seconds ASC', (project_id,))
    rows = c.fetchall()
    conn.close()
    return [dict(row) for row in rows]


def toggle_comment_resolved(comment_id):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('UPDATE comments SET resolved = NOT resolved WHERE id = ?', (comment_id,))
    conn.commit()
    conn.close()


def mark_review_complete(project_id, client_name):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    comment_id = str(uuid.uuid4())
    c.execute('''
        INSERT INTO comments (id, project_id, timestamp_seconds, text, author_name, 
                            author_type, category, priority)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    ''', (comment_id, project_id, 0, f"✅ {client_name} סיים/ה לתת משוב - אפשר להמשיך לעבוד!", 
          client_name, "client", "video", "high"))
    conn.commit()
    conn.close()


def delete_comment(comment_id):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('DELETE FROM comments WHERE id = ?', (comment_id,))
    conn.commit()
    conn.close()


def cleanup_expired_projects():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('SELECT id, video_filename FROM projects WHERE expires_at < ? AND is_active = 1', (datetime.now(),))
    expired = c.fetchall()
    for project_id, video_filename in expired:
        video_path = UPLOAD_DIR / video_filename
        if video_path.exists():
            video_path.unlink()
        c.execute('UPDATE projects SET is_active = 0 WHERE id = ?', (project_id,))
    conn.commit()
    conn.close()
    return len(expired)


# ======================
# Helper Functions
# ======================
def format_time(seconds):
    mins = int(seconds // 60)
    secs = int(seconds % 60)
    return f"{mins:02d}:{secs:02d}"


def get_time_remaining(expires_at):
    if isinstance(expires_at, str):
        expires_at = datetime.fromisoformat(expires_at)
    remaining = expires_at - datetime.now()
    if remaining.total_seconds() <= 0:
        return None, "פג תוקף"
    hours = int(remaining.total_seconds() // 3600)
    minutes = int((remaining.total_seconds() % 3600) // 60)
    return remaining.total_seconds(), f"{hours} שעות ו-{minutes} דקות"


def get_base_url():
    space_host = os.environ.get("SPACE_HOST")
    if space_host:
        return f"https://{space_host}"
    if "streamlit.app" in os.environ.get("HOSTNAME", ""):
        return "https://roy-kozy.streamlit.app"
    try:
        from streamlit.web.server.websocket_headers import _get_websocket_headers
        headers = _get_websocket_headers()
        if headers and "Host" in headers:
            host = headers["Host"]
            if "localhost" not in host:
                return f"https://{host}"
    except:
        pass
    return "https://roy-kozy.streamlit.app"


# ======================
# UI Components
# ======================
def render_header(project_title=None):
    title_html = f'<div style="color: {COLORS["text_secondary"]}; font-size: 0.9375rem;">{project_title}</div>' if project_title else ''
    st.markdown(f"""
    <div class="kozy-header">
        <div class="kozy-logo">
            <img src="{LOGO_URL}" alt="Kozy">
            <span class="kozy-logo-text">Kozy Review</span>
        </div>
        {title_html}
    </div>
    """, unsafe_allow_html=True)


def render_timer(expires_at):
    remaining_seconds, remaining_text = get_time_remaining(expires_at)
    if remaining_seconds is None:
        st.error("⏰ פג תוקף הפרויקט")
        return False
    
    is_urgent = remaining_seconds < 6 * 3600
    urgent_class = "timer-urgent" if is_urgent else ""
    
    st.markdown(f"""
    <div class="timer {urgent_class}">
        <div class="timer-label">זמן נותר</div>
        <div class="timer-value">{remaining_text}</div>
    </div>
    """, unsafe_allow_html=True)
    return True


def render_stats(comments):
    total = len(comments)
    resolved = len([c for c in comments if c['resolved']])
    high = len([c for c in comments if c['priority'] == 'high' and not c['resolved']])
    
    st.markdown(f"""
    <div class="stat-grid">
        <div class="stat-item">
            <div class="stat-value">{total}</div>
            <div class="stat-label">הערות</div>
        </div>
        <div class="stat-item">
            <div class="stat-value" style="color: {COLORS['success']};">{resolved}</div>
            <div class="stat-label">טופלו</div>
        </div>
        <div class="stat-item">
            <div class="stat-value" style="color: {COLORS['error']};">{high}</div>
            <div class="stat-label">דחופות</div>
        </div>
    </div>
    """, unsafe_allow_html=True)


def render_comment(comment, is_editor=False):
    cat = CATEGORIES.get(comment['category'], CATEGORIES['video'])
    pri = PRIORITIES.get(comment['priority'], PRIORITIES['medium'])
    resolved_class = "resolved" if comment['resolved'] else ""
    resolved_mark = "✓ " if comment['resolved'] else ""
    
    st.markdown(f"""
    <div class="comment {resolved_class}" style="border-right-color: {cat['color']};">
        <div class="comment-header">
            <span class="comment-time">⏱ {format_time(comment['timestamp_seconds'])}</span>
            <span class="comment-tag" style="background: {cat['color']}22; color: {cat['color']};">{cat['icon']} {cat['label']}</span>
            <span class="comment-tag" style="background: {pri['bg']}; color: {pri['color']};">{pri['label']}</span>
        </div>
        <div class="comment-text">{resolved_mark}{comment['text']}</div>
        <div class="comment-meta">✍️ {comment['author_name']} • {'עורך' if comment['author_type'] == 'editor' else 'לקוח'}</div>
    </div>
    """, unsafe_allow_html=True)
    
    if is_editor:
        col1, col2 = st.columns(2)
        with col1:
            btn_text = "↩️ בטל" if comment['resolved'] else "✓ טופל"
            if st.button(btn_text, key=f"r_{comment['id']}", use_container_width=True):
                toggle_comment_resolved(comment['id'])
                st.rerun()
        with col2:
            if st.button("🗑️ מחק", key=f"d_{comment['id']}", use_container_width=True):
                delete_comment(comment['id'])
                st.rerun()


# ======================
# Pages
# ======================
def page_home():
    render_header()
    
    # Hero
    st.markdown(f"""
    <div class="hero">
        <div class="hero-title">סקירת וידאו פשוטה ומקצועית</div>
        <div class="hero-subtitle">העלה סרטון, שתף עם הלקוח, קבל משוב מדויק עם חותמות זמן. פשוט ככה.</div>
    </div>
    """, unsafe_allow_html=True)
    
    tab1, tab2 = st.tabs(["📤 העלאת פרויקט", "🔗 יש לי לינק"])
    
    with tab1:
        st.markdown("### פרטי הפרויקט")
        
        title = st.text_input("שם הפרויקט", placeholder="לדוגמה: פרסומת חורף 2025")
        description = st.text_area("תיאור (אופציונלי)", placeholder="הערות לגבי הסרטון...", height=80)
        
        st.markdown("### קובץ וידאו")
        video_file = st.file_uploader(
            "גרור קובץ או לחץ לבחירה",
            type=["mp4", "mov", "webm", "avi", "mkv"],
            help="MP4, MOV, WebM, AVI, MKV • עד 200MB"
        )
        
        if video_file:
            st.video(video_file)
            size_mb = video_file.size / (1024*1024)
            st.success(f"✓ {video_file.name} ({size_mb:.1f} MB)")
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        if st.button("🚀 צור פרויקט", disabled=not (title and video_file), use_container_width=True):
            with st.spinner("מעלה..."):
                project_id, editor_token, client_token = create_project(title, description, video_file)
            
            st.success("✓ הפרויקט נוצר!")
            st.balloons()
            
            base_url = get_base_url()
            client_link = f"{base_url}/?view={client_token}"
            editor_link = f"{base_url}/?edit={editor_token}"
            
            st.markdown("### 🔗 הלינקים שלך")
            
            st.markdown(f"""
            <div class="link-box">
                <div class="link-box-label">לינק ללקוח (שתף אותו!)</div>
                <code class="link-box-url">{client_link}</code>
            </div>
            """, unsafe_allow_html=True)
            
            st.code(client_link, language=None)
            
            with st.expander("🔐 לינק עריכה (שמור!)"):
                st.code(editor_link, language=None)
            
            st.warning("⏰ הסרטון יימחק אוטומטית בעוד 72 שעות")
    
    with tab2:
        st.markdown("### הדבק את הלינק שקיבלת")
        
        link = st.text_input("לינק", placeholder="https://...", label_visibility="collapsed")
        
        if st.button("כניסה", use_container_width=True):
            if "view=" in link:
                token = link.split("view=")[-1].split("&")[0]
                st.query_params["view"] = token
                st.rerun()
            elif "edit=" in link:
                token = link.split("edit=")[-1].split("&")[0]
                st.query_params["edit"] = token
                st.rerun()
            else:
                st.error("לינק לא תקין")


def page_editor(project):
    render_header(project['title'])
    
    col_main, col_side = st.columns([2.5, 1])
    
    with col_side:
        # Timer
        if not render_timer(project['expires_at']):
            return
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        # Link
        base_url = get_base_url()
        client_link = f"{base_url}/?view={project['client_token']}"
        
        st.markdown(f"""
        <div class="link-box">
            <div class="link-box-label">🔗 לינק ללקוח</div>
            <code class="link-box-url" style="font-size: 0.75rem;">{client_link}</code>
        </div>
        """, unsafe_allow_html=True)
        
        st.code(client_link, language=None)
        
        st.markdown(f"<p style='text-align: center; color: {COLORS['text_muted']}; font-size: 0.75rem;'>👁 נצפה {project['view_count']} פעמים</p>", unsafe_allow_html=True)
        
        st.markdown("---")
        
        # Stats
        comments = get_comments(project['id'])
        render_stats(comments)
        
        st.markdown("---")
        
        # Delete
        with st.expander("⚠️ מחיקה"):
            if st.button("🗑️ מחק פרויקט", use_container_width=True):
                delete_project(project['id'])
                st.query_params.clear()
                st.rerun()
    
    with col_main:
        # Video
        video_path = UPLOAD_DIR / project['video_filename']
        if video_path.exists():
            st.markdown('<div class="video-wrapper">', unsafe_allow_html=True)
            st.video(str(video_path))
            st.markdown('</div>', unsafe_allow_html=True)
        else:
            st.error("קובץ לא נמצא")
            return
        
        # Add comment
        st.markdown("### 💬 הערה חדשה")
        
        col_min, col_sec, col_cat, col_pri = st.columns([1, 1, 2, 2])
        
        with col_min:
            minutes = st.number_input("דקות", min_value=0, value=0, key="ed_min")
        with col_sec:
            seconds = st.number_input("שניות", min_value=0, max_value=59, value=0, key="ed_sec")
        with col_cat:
            category = st.selectbox(
                "קטגוריה",
                options=list(CATEGORIES.keys()),
                format_func=lambda x: f"{CATEGORIES[x]['icon']} {CATEGORIES[x]['label']}"
            )
        with col_pri:
            priority = st.selectbox(
                "עדיפות",
                options=list(PRIORITIES.keys()),
                format_func=lambda x: PRIORITIES[x]['label']
            )
        
        comment_text = st.text_area("הערה", placeholder="כתוב את ההערה...", height=80)
        
        if st.button("➕ הוסף", disabled=not comment_text, use_container_width=True):
            add_comment(project['id'], minutes * 60 + seconds, comment_text, "עורך", "editor", category, priority)
            st.rerun()
        
        # Comments list
        st.markdown("---")
        st.markdown("### 📋 הערות")
        
        comments = get_comments(project['id'])
        
        filter_opt = st.selectbox(
            "סינון",
            ["הכל", "ממתינות", "טופלו"],
            label_visibility="collapsed"
        )
        
        if not comments:
            st.info("אין הערות עדיין")
        else:
            for c in comments:
                if filter_opt == "ממתינות" and c['resolved']:
                    continue
                if filter_opt == "טופלו" and not c['resolved']:
                    continue
                render_comment(c, is_editor=True)


def page_client(project):
    render_header()
    
    # Welcome
    st.markdown(f"""
    <div class="welcome">
        <div class="welcome-text">👋 שלום! כאן תוכל/י לצפות בסרטון ולשלוח משוב</div>
        <div class="welcome-subtext">עצור/י את הסרטון בנקודה הרצויה ורשום/י את ההערה</div>
    </div>
    """, unsafe_allow_html=True)
    
    col_main, col_side = st.columns([3, 1])
    
    with col_side:
        render_timer(project['expires_at'])
    
    with col_main:
        # Video
        video_path = UPLOAD_DIR / project['video_filename']
        if video_path.exists():
            st.markdown('<div class="video-wrapper">', unsafe_allow_html=True)
            st.video(str(video_path))
            st.markdown('</div>', unsafe_allow_html=True)
        else:
            st.error("הסרטון לא זמין")
            return
    
    # Add feedback
    st.markdown("---")
    st.markdown("### 💬 הוסף משוב")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        author_name = st.text_input("השם שלך", placeholder="איך קוראים לך?")
    
    with col2:
        st.markdown("**נקודת זמן**")
        c1, c2 = st.columns(2)
        with c1:
            minutes = st.number_input("דקות", min_value=0, value=0, key="cl_min")
        with c2:
            seconds = st.number_input("שניות", min_value=0, max_value=59, value=0, key="cl_sec")
    
    col_cat, col_pri = st.columns(2)
    with col_cat:
        category = st.selectbox(
            "קטגוריה",
            options=list(CATEGORIES.keys()),
            format_func=lambda x: f"{CATEGORIES[x]['icon']} {CATEGORIES[x]['label']}",
            key="cl_cat"
        )
    with col_pri:
        priority = st.selectbox(
            "עדיפות",
            options=list(PRIORITIES.keys()),
            format_func=lambda x: PRIORITIES[x]['label'],
            key="cl_pri"
        )
    
    comment_text = st.text_area("המשוב שלך", placeholder="מה לשנות או לתקן?", height=100)
    
    if st.button("📤 שלח משוב", disabled=not (author_name and comment_text), use_container_width=True):
        add_comment(project['id'], minutes * 60 + seconds, comment_text, author_name, "client", category, priority)
        st.success("✓ המשוב נשלח!")
        st.balloons()
        st.rerun()
    
    # Previous comments
    st.markdown("---")
    st.markdown("### 📋 משובים שנשלחו")
    
    comments = get_comments(project['id'])
    
    if not comments:
        st.info("עדיין אין משובים. היה/יי הראשון/ה! 🎉")
    else:
        for c in comments:
            render_comment(c, is_editor=False)
    
    # Complete button
    st.markdown("---")
    st.markdown("### ✅ סיימת?")
    
    if 'review_done' not in st.session_state:
        st.session_state.review_done = False
    
    if not st.session_state.review_done:
        confirm_name = st.text_input("השם שלך לאישור", placeholder="הכנס שם...", key="confirm")
        
        if st.button("🎉 סיימתי - אפשר להמשיך לעבוד!", disabled=not confirm_name, use_container_width=True):
            mark_review_complete(project['id'], confirm_name)
            st.session_state.review_done = True
            st.balloons()
            st.rerun()
    else:
        st.markdown(f"""
        <div class="completed-box">
            <div class="completed-icon">✅</div>
            <div class="completed-title">תודה רבה!</div>
            <div class="completed-text">העורך קיבל את המשוב ויתחיל לעבוד על התיקונים.</div>
        </div>
        """, unsafe_allow_html=True)


# ======================
# Main
# ======================
def main():
    init_db()
    cleanup_expired_projects()
    load_css()
    
    params = st.query_params
    
    if "edit" in params:
        project = get_project_by_editor_token(params["edit"])
        if project:
            page_editor(project)
        else:
            st.error("פרויקט לא נמצא או שפג תוקפו")
            if st.button("🏠 חזרה"):
                st.query_params.clear()
                st.rerun()
    
    elif "view" in params:
        project = get_project_by_client_token(params["view"])
        if project:
            page_client(project)
        else:
            st.error("הסרטון לא נמצא או שפג תוקפו")
            st.info("ייתכן שעברו 72 שעות והסרטון נמחק אוטומטית.")
    
    else:
        page_home()


if __name__ == "__main__":
    main()