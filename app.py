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
    page_title="Kozy Review",
    page_icon="🎬",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# נתיבים
UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)
DB_PATH = "kozy_review.db"

# קטגוריות ועדיפויות
CATEGORIES = {
    "video": {"label": "וידאו", "icon": "🎬", "color": "#3B82F6"},
    "image": {"label": "תמונה", "icon": "🖼️", "color": "#8B5CF6"},
    "effect": {"label": "אפקט", "icon": "✨", "color": "#EAB308"},
    "subtitles": {"label": "כתוביות", "icon": "💬", "color": "#22C55E"},
    "transition": {"label": "מעבר", "icon": "🔄", "color": "#F97316"},
    "music": {"label": "מוזיקה", "icon": "🎵", "color": "#EC4899"},
    "sound": {"label": "סאונד", "icon": "🔊", "color": "#6366F1"},
    "ai": {"label": "AI", "icon": "🤖", "color": "#06B6D4"},
    "bug": {"label": "באג", "icon": "🐛", "color": "#EF4444"},
}

PRIORITIES = {
    "low": {"label": "נמוכה", "color": "#22C55E"},
    "medium": {"label": "בינונית", "color": "#EAB308"},
    "high": {"label": "גבוהה", "color": "#EF4444"},
}

# ======================
# CSS מותאם
# ======================
st.markdown("""
<style>
    /* RTL וכללי */
    .stApp {
        direction: rtl;
    }
    
    /* כותרות */
    h1, h2, h3 {
        text-align: right !important;
    }
    
    /* כרטיסי פרויקט */
    .project-card {
        background: white;
        border-radius: 16px;
        padding: 20px;
        box-shadow: 0 4px 6px -1px rgba(0,0,0,0.1);
        border: 1px solid #E2E8F0;
        margin-bottom: 16px;
        transition: all 0.2s;
    }
    .project-card:hover {
        box-shadow: 0 10px 25px -5px rgba(0,0,0,0.1);
        transform: translateY(-2px);
    }
    
    /* תגובות */
    .comment-card {
        background: #F8FAFC;
        border-radius: 12px;
        padding: 16px;
        margin-bottom: 12px;
        border-right: 4px solid #10B981;
    }
    .comment-card.resolved {
        opacity: 0.6;
        border-right-color: #94A3B8;
    }
    
    /* תגיות */
    .tag {
        display: inline-block;
        padding: 4px 12px;
        border-radius: 20px;
        font-size: 12px;
        font-weight: 600;
        margin-left: 8px;
    }
    
    /* טיימר */
    .timer-box {
        background: linear-gradient(135deg, #FEF3C7 0%, #FDE68A 100%);
        border-radius: 12px;
        padding: 16px;
        text-align: center;
        border: 1px solid #F59E0B;
    }
    .timer-urgent {
        background: linear-gradient(135deg, #FEE2E2 0%, #FECACA 100%);
        border-color: #EF4444;
    }
    
    /* לינק להעתקה */
    .copy-link-box {
        background: #F0FDF4;
        border: 2px dashed #22C55E;
        border-radius: 12px;
        padding: 16px;
        text-align: center;
    }
    
    /* כפתורים */
    .stButton > button {
        border-radius: 12px !important;
        font-weight: 600 !important;
        transition: all 0.2s !important;
    }
    
    /* הסתרת אלמנטים */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
</style>
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


def get_all_projects_by_editor(editor_token):
    """קבלת כל הפרויקטים של עורך (לפי טוקן ראשון)"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    
    # בגרסה פשוטה - מחזיר את כל הפרויקטים הפעילים
    c.execute('SELECT * FROM projects WHERE is_active = 1 ORDER BY created_at DESC')
    rows = c.fetchall()
    conn.close()
    
    return [dict(row) for row in rows]


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
    # ב-Hugging Face Spaces זה יהיה אוטומטי
    # לפיתוח מקומי:
    return "http://localhost:8501"


# ======================
# UI Components
# ======================
def render_header(title="Kozy Review", show_back=False, back_url=None):
    """רנדור כותרת"""
    col1, col2 = st.columns([6, 1])
    
    with col1:
        st.markdown(f"""
        <div style="display: flex; align-items: center; gap: 16px; margin-bottom: 24px;">
            <div style="width: 50px; height: 50px; background: linear-gradient(135deg, #10B981 0%, #06B6D4 100%); 
                        border-radius: 12px; display: flex; align-items: center; justify-content: center;">
                <span style="font-size: 24px;">🎬</span>
            </div>
            <h1 style="margin: 0; font-size: 28px; color: #1E293B;">{title}</h1>
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
        <div style="font-size: 14px; color: #64748B; margin-bottom: 4px;">זמן נותר עד מחיקה</div>
        <div style="font-size: 24px; font-weight: 700; color: {'#EF4444' if is_urgent else '#F59E0B'};">
            {icon} {remaining_text}
        </div>
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
        st.metric("סה״כ תגובות", total)
    with col2:
        st.metric("טופלו", resolved)
    with col3:
        st.metric("דחופות", high_priority)


def render_comment_card(comment, is_editor=False):
    """רנדור כרטיס תגובה"""
    cat = CATEGORIES.get(comment['category'], CATEGORIES['video'])
    pri = PRIORITIES.get(comment['priority'], PRIORITIES['medium'])
    
    resolved_class = "resolved" if comment['resolved'] else ""
    resolved_icon = "✅ " if comment['resolved'] else ""
    
    st.markdown(f"""
    <div class="comment-card {resolved_class}" style="border-right-color: {cat['color']};">
        <div style="display: flex; justify-content: space-between; align-items: start; margin-bottom: 8px;">
            <div>
                <span style="background: #E0F2FE; color: #0369A1; padding: 4px 10px; border-radius: 8px; 
                            font-size: 13px; font-weight: 600; font-family: monospace;">
                    ⏱️ {format_time(comment['timestamp_seconds'])}
                </span>
                <span class="tag" style="background: {cat['color']}20; color: {cat['color']};">
                    {cat['icon']} {cat['label']}
                </span>
                <span class="tag" style="background: {pri['color']}20; color: {pri['color']};">
                    {pri['label']}
                </span>
            </div>
        </div>
        <p style="margin: 12px 0; font-size: 15px; color: #334155; line-height: 1.6;">
            {resolved_icon}{comment['text']}
        </p>
        <div style="font-size: 12px; color: #94A3B8;">
            {comment['author_name']} ({('עורך' if comment['author_type'] == 'editor' else 'לקוח')})
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    if is_editor:
        col1, col2 = st.columns([1, 1])
        with col1:
            if st.button(f"{'↩️ בטל' if comment['resolved'] else '✅ טופל'}", key=f"resolve_{comment['id']}"):
                toggle_comment_resolved(comment['id'])
                st.rerun()
        with col2:
            if st.button("🗑️ מחק", key=f"delete_{comment['id']}"):
                delete_comment(comment['id'])
                st.rerun()


# ======================
# Pages
# ======================
def page_home():
    """עמוד בית - יצירת פרויקט או כניסה"""
    render_header()
    
    st.markdown("""
    <div style="text-align: center; padding: 40px 0;">
        <h2 style="color: #1E293B; margin-bottom: 8px;">ברוכים הבאים ל-Kozy Review</h2>
        <p style="color: #64748B; font-size: 18px;">שתף סרטונים עם לקוחות וקבל פידבק מדויק</p>
    </div>
    """, unsafe_allow_html=True)
    
    tab1, tab2 = st.tabs(["📤 העלאת פרויקט חדש", "🔗 כניסה עם לינק"])
    
    with tab1:
        st.markdown("### פרטי הפרויקט")
        
        title = st.text_input("שם הפרויקט *", placeholder="לדוגמה: פרסומת חורף 2025")
        description = st.text_area("תיאור (אופציונלי)", placeholder="גרסה ראשונה לאישור...")
        
        st.markdown("### העלאת וידאו")
        video_file = st.file_uploader(
            "בחר קובץ וידאו",
            type=["mp4", "mov", "webm", "avi", "mkv"],
            help="עד 10GB - MP4, MOV, WebM, AVI, MKV"
        )
        
        if video_file:
            st.video(video_file)
            st.success(f"✅ {video_file.name} ({video_file.size / (1024*1024):.1f} MB)")
        
        st.markdown("---")
        
        if st.button("🚀 צור פרויקט ושלח ללקוח", type="primary", disabled=not (title and video_file)):
            with st.spinner("מעלה את הסרטון..."):
                project_id, editor_token, client_token = create_project(title, description, video_file)
            
            st.success("✅ הפרויקט נוצר בהצלחה!")
            
            # שמירת הטוקן ב-session
            st.session_state['editor_token'] = editor_token
            
            base_url = get_base_url()
            client_link = f"{base_url}/?view={client_token}"
            editor_link = f"{base_url}/?edit={editor_token}"
            
            st.markdown("### 🔗 לינקים")
            
            st.markdown(f"""
            <div class="copy-link-box">
                <div style="font-size: 14px; color: #64748B; margin-bottom: 8px;">לינק ללקוח (שתף אותו!):</div>
                <code style="font-size: 16px; color: #059669; background: white; padding: 8px 16px; 
                            border-radius: 8px; display: block; margin: 8px 0;">{client_link}</code>
            </div>
            """, unsafe_allow_html=True)
            
            st.code(client_link, language=None)
            
            st.info(f"🔐 לינק עריכה (שמור לעצמך!): `{editor_link}`")
            
            st.warning("⏰ הפרויקט יימחק אוטומטית בעוד 72 שעות!")
    
    with tab2:
        st.markdown("### יש לך לינק?")
        
        link_input = st.text_input("הדבק את הלינק כאן", placeholder="https://...")
        
        if st.button("🔓 כניסה"):
            # ניסיון לחלץ טוקן מהלינק
            if "view=" in link_input:
                token = link_input.split("view=")[-1].split("&")[0]
                st.query_params["view"] = token
                st.rerun()
            elif "edit=" in link_input:
                token = link_input.split("edit=")[-1].split("&")[0]
                st.query_params["edit"] = token
                st.rerun()
            else:
                st.error("לינק לא תקין")


def page_editor(project):
    """עמוד עריכה - לעורך"""
    render_header(f"✏️ {project['title']}")
    
    # טיימר
    col1, col2 = st.columns([2, 1])
    
    with col2:
        if not render_timer(project['expires_at']):
            return
        
        st.markdown("---")
        
        # לינק ללקוח
        base_url = get_base_url()
        client_link = f"{base_url}/?view={project['client_token']}"
        
        st.markdown("**🔗 לינק ללקוח:**")
        st.code(client_link, language=None)
        
        st.markdown(f"👁️ נצפה {project['view_count']} פעמים")
        
        st.markdown("---")
        
        # סטטיסטיקות
        comments = get_comments(project['id'])
        render_stats(comments)
        
        st.markdown("---")
        
        # מחיקה
        if st.button("🗑️ מחק פרויקט", type="secondary"):
            if st.button("⚠️ אישור מחיקה", type="primary"):
                delete_project(project['id'])
                st.query_params.clear()
                st.rerun()
    
    with col1:
        # נגן וידאו
        video_path = UPLOAD_DIR / project['video_filename']
        if video_path.exists():
            st.video(str(video_path))
        else:
            st.error("קובץ הוידאו לא נמצא")
            return
        
        # הוספת תגובה
        st.markdown("### 💬 הוסף הערה")
        
        col_time, col_cat, col_pri = st.columns([1, 2, 2])
        
        with col_time:
            minutes = st.number_input("דקות", min_value=0, value=0, key="ed_min")
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
        
        comment_text = st.text_area("תוכן ההערה", placeholder="כתוב את ההערה שלך...")
        
        if st.button("➕ הוסף הערה", disabled=not comment_text):
            timestamp = minutes * 60 + seconds
            add_comment(project['id'], timestamp, comment_text, "עורך", "editor", category, priority)
            st.success("✅ ההערה נוספה!")
            st.rerun()
        
        # רשימת תגובות
        st.markdown("---")
        st.markdown("### 📝 כל ההערות")
        
        comments = get_comments(project['id'])
        
        # סינון
        filter_option = st.selectbox(
            "סינון",
            ["הכל", "לא טופלו", "טופלו"] + [f"{c['icon']} {c['label']}" for c in CATEGORIES.values()]
        )
        
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
    render_header(f"🎬 {project['title']}")
    
    st.markdown(f"""
    <div style="background: #F0FDF4; border-radius: 12px; padding: 16px; margin-bottom: 24px; 
                border: 1px solid #86EFAC; text-align: center;">
        <span style="font-size: 18px;">👋 שלום! צפה בסרטון והוסף את המשוב שלך</span>
    </div>
    """, unsafe_allow_html=True)
    
    # טיימר
    col1, col2 = st.columns([3, 1])
    
    with col2:
        if not render_timer(project['expires_at']):
            st.error("הסרטון כבר לא זמין")
            return
    
    with col1:
        # נגן וידאו
        video_path = UPLOAD_DIR / project['video_filename']
        if video_path.exists():
            st.video(str(video_path))
        else:
            st.error("קובץ הוידאו לא נמצא")
            return
    
    # הוספת משוב
    st.markdown("---")
    st.markdown("### 💬 הוסף משוב")
    
    col_name, col_time = st.columns([2, 1])
    
    with col_name:
        author_name = st.text_input("השם שלך *", placeholder="הכנס את שמך...")
    
    with col_time:
        st.markdown("**נקודת זמן:**")
        col_min, col_sec = st.columns(2)
        with col_min:
            minutes = st.number_input("דקות", min_value=0, value=0, key="cl_min")
        with col_sec:
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
    
    comment_text = st.text_area("המשוב שלך *", placeholder="כתוב את המשוב שלך כאן...")
    
    if st.button("📤 שלח משוב", type="primary", disabled=not (author_name and comment_text)):
        timestamp = minutes * 60 + seconds
        add_comment(project['id'], timestamp, comment_text, author_name, "client", category, priority)
        st.success("✅ המשוב נשלח בהצלחה! תודה!")
        st.balloons()
        st.rerun()
    
    # הצגת משובים קודמים
    st.markdown("---")
    st.markdown("### 📝 משובים שנשלחו")
    
    comments = get_comments(project['id'])
    
    if not comments:
        st.info("עדיין אין משובים. היה הראשון! 🎉")
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
            st.info("ייתכן שעברו 72 שעות מאז העלאת הסרטון והוא נמחק אוטומטית.")
    
    else:
        # עמוד בית
        page_home()


if __name__ == "__main__":
    main()