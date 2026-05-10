import streamlit as st
from openai import OpenAI
import json
from datetime import datetime

# ── PAGE CONFIG ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Tez Araştırma Asistanı",
    page_icon="🧬",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── DARK & SLEEK CSS ──────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Space+Mono:wght@400;700&family=DM+Sans:wght@300;400;500;600&display=swap');

:root {
    --bg-primary:    #0d1117;
    --bg-secondary:  #111827;
    --bg-card:       #161d2b;
    --bg-input:      #1a2236;
    --accent-blue:   #3b82f6;
    --accent-teal:   #14b8a6;
    --accent-purple: #6366f1;
    --text-primary:  #e2e8f0;
    --text-muted:    #64748b;
    --text-dim:      #94a3b8;
    --border:        #1e2d45;
    --border-glow:   #3b82f633;
    --radius:        12px;
}

/* ── Global reset ── */
html, body, [class*="css"] {
    font-family: 'DM Sans', sans-serif;
    background-color: var(--bg-primary) !important;
    color: var(--text-primary) !important;
}

/* ── Main container ── */
.main .block-container {
    background-color: var(--bg-primary);
    padding: 2rem 2.5rem 4rem;
    max-width: 1100px;
}

/* ── Sidebar ── */
[data-testid="stSidebar"] {
    background: var(--bg-secondary) !important;
    border-right: 1px solid var(--border) !important;
}
[data-testid="stSidebar"] * { color: var(--text-primary) !important; }

/* ── Header strip ── */
.app-header {
    background: linear-gradient(135deg, #0f1a2e 0%, #0d1117 50%, #0a1628 100%);
    border: 1px solid var(--border);
    border-radius: var(--radius);
    padding: 1.6rem 2rem;
    margin-bottom: 1.8rem;
    position: relative;
    overflow: hidden;
}
.app-header::before {
    content: '';
    position: absolute; inset: 0;
    background: radial-gradient(ellipse 60% 80% at 20% 50%, #3b82f618 0%, transparent 70%);
    pointer-events: none;
}
.app-header-title {
    font-family: 'Space Mono', monospace;
    font-size: 1.5rem;
    font-weight: 700;
    background: linear-gradient(90deg, #60a5fa, #14b8a6);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    margin: 0 0 .35rem;
    letter-spacing: -0.5px;
}
.app-header-sub {
    font-size: .85rem;
    color: var(--text-muted);
    margin: 0;
    letter-spacing: .3px;
}

/* ── Module badge ── */
.module-badge {
    display: inline-flex;
    align-items: center;
    gap: .45rem;
    background: var(--bg-card);
    border: 1px solid var(--border);
    border-radius: 999px;
    padding: .35rem .9rem;
    font-size: .78rem;
    font-weight: 600;
    letter-spacing: .6px;
    text-transform: uppercase;
    color: var(--accent-teal);
    margin-bottom: 1.2rem;
}

/* ── Chat messages ── */
.chat-wrapper {
    display: flex;
    flex-direction: column;
    gap: 1rem;
    margin-bottom: 1rem;
}
.msg-row { display: flex; gap: .8rem; align-items: flex-start; }
.msg-row.user  { flex-direction: row-reverse; }

.avatar {
    width: 36px; height: 36px;
    border-radius: 10px;
    display: flex; align-items: center; justify-content: center;
    font-size: 1rem;
    flex-shrink: 0;
}
.avatar.ai   { background: linear-gradient(135deg,#1e3a5f,#0f2744); border: 1px solid #2563eb55; }
.avatar.user { background: linear-gradient(135deg,#1a3a2e,#0f2720); border: 1px solid #14b8a655; }

.bubble {
    max-width: 82%;
    border-radius: var(--radius);
    padding: .9rem 1.1rem;
    font-size: .92rem;
    line-height: 1.65;
    word-break: break-word;
}
.bubble.ai {
    background: var(--bg-card);
    border: 1px solid var(--border);
    color: var(--text-primary);
}
.bubble.user {
    background: linear-gradient(135deg,#1a3a2e,#12302a);
    border: 1px solid #14b8a630;
    color: #d1faf5;
}
.bubble p { margin: 0 0 .5rem; }
.bubble p:last-child { margin-bottom: 0; }
.bubble code {
    font-family: 'Space Mono', monospace;
    font-size: .82em;
    background: #0d1117;
    border: 1px solid var(--border);
    border-radius: 5px;
    padding: .1rem .35rem;
    color: #93c5fd;
}
.bubble pre {
    background: #0d1117;
    border: 1px solid var(--border);
    border-radius: 8px;
    padding: .8rem 1rem;
    overflow-x: auto;
    margin: .5rem 0;
}
.bubble pre code { background: none; border: none; padding: 0; }

.msg-time {
    font-size: .7rem;
    color: var(--text-muted);
    margin-top: .3rem;
    text-align: right;
}
.msg-row.user .msg-time { text-align: left; }

/* ── Typing indicator ── */
.typing-dots { display: flex; gap: 5px; align-items: center; padding: .2rem 0; }
.typing-dots span {
    width: 7px; height: 7px;
    background: var(--accent-blue);
    border-radius: 50%;
    animation: bounce 1.2s infinite;
}
.typing-dots span:nth-child(2) { animation-delay: .2s; }
.typing-dots span:nth-child(3) { animation-delay: .4s; }
@keyframes bounce { 0%,60%,100%{transform:translateY(0)} 30%{transform:translateY(-6px)} }

/* ── Input area ── */
[data-testid="stTextInput"] input,
[data-testid="stTextArea"] textarea {
    background: var(--bg-input) !important;
    border: 1px solid var(--border) !important;
    border-radius: 10px !important;
    color: var(--text-primary) !important;
    font-family: 'DM Sans', sans-serif !important;
    font-size: .92rem !important;
    transition: border-color .2s;
}
[data-testid="stTextInput"] input:focus,
[data-testid="stTextArea"] textarea:focus {
    border-color: var(--accent-blue) !important;
    box-shadow: 0 0 0 3px var(--border-glow) !important;
}

/* ── Buttons ── */
[data-testid="baseButton-primary"],
.stButton > button {
    background: linear-gradient(135deg, #1d4ed8, #1e40af) !important;
    color: #fff !important;
    border: none !important;
    border-radius: 9px !important;
    font-weight: 600 !important;
    font-family: 'DM Sans', sans-serif !important;
    transition: all .2s !important;
}
.stButton > button:hover {
    background: linear-gradient(135deg, #2563eb, #1d4ed8) !important;
    transform: translateY(-1px) !important;
    box-shadow: 0 4px 16px #3b82f633 !important;
}

/* ── Radio / selectbox ── */
[data-testid="stRadio"] label,
[data-testid="stSelectbox"] * {
    color: var(--text-dim) !important;
    font-size: .9rem !important;
}
[data-testid="stRadio"] [aria-checked="true"] + div { color: var(--accent-teal) !important; }

/* ── Expander ── */
details summary {
    color: var(--text-dim) !important;
    font-size: .85rem !important;
}
details[open] > summary { color: var(--accent-teal) !important; }

/* ── Metric cards (sidebar) ── */
.metric-card {
    background: var(--bg-card);
    border: 1px solid var(--border);
    border-radius: 10px;
    padding: .75rem 1rem;
    margin-bottom: .6rem;
    display: flex;
    justify-content: space-between;
    align-items: center;
}
.metric-label { font-size: .78rem; color: var(--text-muted); }
.metric-value { font-family: 'Space Mono', monospace; font-size: .88rem; color: var(--accent-blue); font-weight: 700; }

/* ── Divider ── */
hr { border-color: var(--border) !important; margin: 1.2rem 0 !important; }

/* ── Scrollbar ── */
::-webkit-scrollbar { width: 6px; }
::-webkit-scrollbar-track { background: var(--bg-primary); }
::-webkit-scrollbar-thumb { background: #1e3a5f; border-radius: 10px; }
::-webkit-scrollbar-thumb:hover { background: var(--accent-blue); }

/* ── Formula / quick-tool cards ── */
.tool-card {
    background: var(--bg-card);
    border: 1px solid var(--border);
    border-radius: var(--radius);
    padding: 1.1rem 1.3rem;
    margin-bottom: .8rem;
}
.tool-card-title {
    font-family: 'Space Mono', monospace;
    font-size: .8rem;
    color: var(--accent-teal);
    font-weight: 700;
    letter-spacing: .6px;
    text-transform: uppercase;
    margin-bottom: .6rem;
}
</style>
""", unsafe_allow_html=True)

# ── SESSION STATE INIT ────────────────────────────────────────────────────────
if "messages" not in st.session_state:
    st.session_state.messages = []      # {"role","content","time"}
if "module" not in st.session_state:
    st.session_state.module = "Araştırma"
if "api_key" not in st.session_state:
    st.session_state.api_key = ""
if "mol_result" not in st.session_state:
    st.session_state.mol_result = None

# ── SYSTEM PROMPTS ────────────────────────────────────────────────────────────
BASE_SYSTEM = (
    "Sen bir eczacılık fakültesi öğrencisi için uzman bir tez danışmanısın. "
    "Özellikle polifenolik bileşiklerin (Resveratrol, Viniferin, Quercetin vb.) "
    "antioksidan kapasiteleri, moleküler etki mekanizmaları ve sitotoksisite analizleri "
    "konusunda derinlemesine uzmanlığa sahipsin. "
    "ZORUNLU DİL KURALLARI: Her cümleye büyük harfle başla. Özel isimleri, "
    "kimyasal bileşik adlarını ve akademik terimleri büyük harfle yaz. "
    "Kesinlikle resmi, bilimsel, imla kurallarına uygun Türkçe kullan. "
    "Yanıtlarını yapılandırılmış, detaylı ve kaynaklara atıfla desteklenmiş biçimde ver."
)

MODULE_PROMPTS = {
    "Araştırma": (
        BASE_SYSTEM
        + " Şu anda AKADEMİK ARAŞTIRMA MODÜLÜ'ndesin. "
        "PubMed, Web of Science ve Scopus gibi akademik veritabanlarında literatür tarama stratejileri konusunda rehberlik et. "
        "MESH terimleri, Boolean operatörler ve sistematik derleme metodolojisi hakkında ayrıntılı bilgi ver. "
        "Kullanıcıya makale değerlendirme kriterleri, IF (Impact Factor) ve atıf analizi konularında destek sağla."
    ),
    "Deney": (
        BASE_SYSTEM
        + " Şu anda DENEY MODÜLÜ'ndesin. "
        "Molarite, normalite ve konsantrasyon hesaplamaları, stok çözelti hazırlama protokolleri, "
        "DPPH/ABTS antioksidan tayin yöntemleri, MTT sitotoksisite deneyleri ve UV-Vis spektrofotometri "
        "konularında adım adım protokol ve hesaplama desteği sun. "
        "Formülleri açıkça yaz ve sayısal örneklerle destekle."
    ),
    "Yazım": (
        BASE_SYSTEM
        + " Şu anda AKADEMİK YAZIM MODÜLÜ'ndesin. "
        "APA 7. baskı, Vancouver ve IEEE referans biçimlendirmeleri konusunda uzman desteği ver. "
        "IMRaD yapısına (Introduction, Methods, Results, Discussion) uygun paragraf düzenleme, "
        "bilimsel özet yazımı, anahtar kelime optimizasyonu ve akademik dil iyileştirmeleri yap. "
        "Kullanıcının verdiği metni düzelt ve iyileştir."
    ),
}

# ── OPENROUTER CLIENT ─────────────────────────────────────────────────────────
def get_client(api_key: str) -> OpenAI:
    return OpenAI(
        base_url="https://openrouter.ai/api/v1",
        api_key=api_key,
    )

def chat_with_model(api_key: str, module: str, history: list) -> str:
    client = get_client(api_key)
    messages = [{"role": "system", "content": MODULE_PROMPTS[module]}]
    for m in history:
        messages.append({"role": m["role"], "content": m["content"]})
    try:
        response = client.chat.completions.create(
            model="google/gemini-pro-1.5",
            messages=messages,
            max_tokens=2048,
            temperature=0.7,
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"⚠️ API Hatası: {str(e)}"

# ── MOLARITE HESAPLAMA ────────────────────────────────────────────────────────
def calculate_molarity(mass_g: float, mol_weight: float, volume_ml: float) -> dict:
    moles = mass_g / mol_weight
    molarity = moles / (volume_ml / 1000)
    return {"mol": round(moles, 6), "M": round(molarity, 6)}

def calculate_dilution(c1: float, v2: float, c2: float) -> float:
    return round((c2 * v2) / c1, 4)

# ── SIDEBAR ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div style='text-align:center; padding:.5rem 0 1rem;'>
        <div style='font-family:Space Mono,monospace; font-size:1.1rem;
             background:linear-gradient(90deg,#60a5fa,#14b8a6);
             -webkit-background-clip:text;-webkit-text-fill-color:transparent;
             font-weight:700; letter-spacing:-0.5px;'>
            🧬 THESISAI
        </div>
        <div style='font-size:.72rem;color:#475569;margin-top:.25rem;letter-spacing:.5px;'>
            POLİFENOLİK ARAŞTIRMA SİSTEMİ
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("**API Yapılandırması**")
    api_key_input = st.text_input(
        "OpenRouter API Anahtarı",
        value=st.session_state.api_key,
        type="password",
        placeholder="sk-or-...",
        label_visibility="collapsed",
    )
    if api_key_input:
        st.session_state.api_key = api_key_input

    st.divider()

    st.markdown("**Modül Seçimi**")
    module_icons = {"Araştırma": "🔬", "Deney": "⚗️", "Yazım": "📝"}
    selected = st.radio(
        "Modül",
        list(module_icons.keys()),
        format_func=lambda x: f"{module_icons[x]}  {x} Modülü",
        index=list(module_icons.keys()).index(st.session_state.module),
        label_visibility="collapsed",
    )
    if selected != st.session_state.module:
        st.session_state.module = selected

    st.divider()

    # Stats
    total_msgs = len(st.session_state.messages)
    user_msgs  = sum(1 for m in st.session_state.messages if m["role"] == "user")
    st.markdown("**Oturum İstatistikleri**")
    st.markdown(f"""
    <div class='metric-card'>
        <span class='metric-label'>Toplam Mesaj</span>
        <span class='metric-value'>{total_msgs}</span>
    </div>
    <div class='metric-card'>
        <span class='metric-label'>Kullanıcı Sorusu</span>
        <span class='metric-value'>{user_msgs}</span>
    </div>
    <div class='metric-card'>
        <span class='metric-label'>Aktif Modül</span>
        <span class='metric-value'>{selected[:6].upper()}</span>
    </div>
    """, unsafe_allow_html=True)

    st.divider()

    if st.button("🗑️  Geçmişi Temizle", use_container_width=True):
        st.session_state.messages = []
        st.session_state.mol_result = None
        st.rerun()

    # Quick tips per module
    tips = {
        "Araştırma": ["PubMed MESH Terimler", "Sistematik Derleme", "IF Sorgulama"],
        "Deney":     ["DPPH Protokolü", "MTT Assay", "IC₅₀ Hesaplama"],
        "Yazım":     ["APA 7 Format", "IMRaD Yapısı", "Özet Yazımı"],
    }
    st.markdown("**Hızlı Sorular**")
    for tip in tips[selected]:
        if st.button(tip, key=f"tip_{tip}", use_container_width=True):
            st.session_state.messages.append({
                "role": "user",
                "content": tip + " hakkında detaylı bilgi ver.",
                "time": datetime.now().strftime("%H:%M"),
            })
            st.rerun()

# ── MAIN CONTENT ──────────────────────────────────────────────────────────────
mod = st.session_state.module
mod_colors = {"Araştırma": "#3b82f6", "Deney": "#14b8a6", "Yazım": "#6366f1"}
mod_descs = {
    "Araştırma": "Literatür tarama · PubMed stratejileri · Sistematik derleme",
    "Deney":     "Molarite hesaplama · Protokol tasarımı · Veri analizi",
    "Yazım":     "Paragraf düzenleme · Kaynakça formatlama · IMRaD yapısı",
}

st.markdown(f"""
<div class='app-header'>
    <div class='app-header-title'>🧬 Tez Araştırma & Laboratuvar Asistanı</div>
    <div class='app-header-sub'>Polifenolik Bileşikler Uzmanlık Platformu — Eczacılık Fakültesi</div>
</div>
<div class='module-badge'>
    <span style='width:8px;height:8px;border-radius:50%;background:{mod_colors[mod]};display:inline-block;'></span>
    {module_icons[mod]} {mod} Modülü — {mod_descs[mod]}
</div>
""", unsafe_allow_html=True)

# ── DENEY MODÜLÜ: Hızlı Hesaplama Araçları ───────────────────────────────────
if mod == "Deney":
    with st.expander("⚗️  Molarite & Dilüsyon Hızlı Hesaplama Araçları", expanded=False):
        col1, col2 = st.columns(2)

        with col1:
            st.markdown("<div class='tool-card'><div class='tool-card-title'>Molarite Hesaplama</div>", unsafe_allow_html=True)
            mass   = st.number_input("Kütle (g)", min_value=0.0, value=0.0, step=0.001, format="%.4f", key="mass")
            mw     = st.number_input("Moleküler Ağırlık (g/mol)", min_value=0.0, value=228.24, step=0.01, key="mw")
            vol_ml = st.number_input("Hacim (mL)", min_value=0.0, value=100.0, step=1.0, key="vol")
            if st.button("Hesapla", key="calc_mol"):
                if mw > 0 and vol_ml > 0 and mass > 0:
                    res = calculate_molarity(mass, mw, vol_ml)
                    st.success(f"**{res['mol']} mol** → **{res['M']} M** ({res['M']*1000:.4f} mM)")
                else:
                    st.warning("Lütfen tüm alanları doldurun.")
            st.markdown("</div>", unsafe_allow_html=True)

        with col2:
            st.markdown("<div class='tool-card'><div class='tool-card-title'>Seyreltme (C₁V₁ = C₂V₂)</div>", unsafe_allow_html=True)
            c1 = st.number_input("Stok Konsantrasyon C₁ (mM)", min_value=0.0, value=10.0, step=0.1, key="c1")
            c2 = st.number_input("Hedef Konsantrasyon C₂ (mM)", min_value=0.0, value=0.1, step=0.01, key="c2")
            v2 = st.number_input("Hedef Hacim V₂ (mL)", min_value=0.0, value=10.0, step=0.5, key="v2")
            if st.button("Hesapla", key="calc_dil"):
                if c1 > 0 and c2 > 0 and v2 > 0:
                    v1 = calculate_dilution(c1, v2, c2)
                    solvent = round(v2 - v1, 4)
                    st.success(f"Stoktan **{v1} mL** al → **{solvent} mL** çözücü ekle")
                else:
                    st.warning("Lütfen tüm alanları doldurun.")
            st.markdown("</div>", unsafe_allow_html=True)

# ── YAZIM MODÜLÜ: Metin Düzenleme Alanı ──────────────────────────────────────
quick_text = None
if mod == "Yazım":
    with st.expander("📝  Metin Düzenleme / Paragraf Gönderi", expanded=False):
        raw_text = st.text_area(
            "Düzeltilecek / iyileştirilecek metni buraya yapıştırın:",
            height=150,
            placeholder="Akademik paragraf, özet veya tartışma bölümünü buraya girin...",
        )
        ref_style = st.selectbox("Referans Formatı", ["APA 7", "Vancouver", "IEEE"])
        if st.button("Düzenle ve Gönder →", key="send_text"):
            if raw_text.strip():
                quick_text = (
                    f"Aşağıdaki metni {ref_style} formatına uygun, IMRaD yapısına göre "
                    f"akademik dil kuralları çerçevesinde düzenle ve iyileştir:\n\n{raw_text}"
                )

# ── CHAT HISTORY ──────────────────────────────────────────────────────────────
st.markdown("<div class='chat-wrapper'>", unsafe_allow_html=True)

if not st.session_state.messages:
    welcome_texts = {
        "Araştırma": (
            "Merhaba! Ben Tez Araştırma Asistanınım. "
            "Polifenolik bileşikler, antioksidan kapasiteleri ve literatür tarama stratejileri "
            "konularında size destek olmaya hazırım. Nasıl yardımcı olabilirim?"
        ),
        "Deney": (
            "Laboratuvar Modülü aktif. Molarite hesapları, stok çözelti hazırlama protokolleri, "
            "DPPH/ABTS deneyleri ve MTT sitotoksisite testleri konularında soru sorabilirsiniz."
        ),
        "Yazım": (
            "Akademik Yazım Modülü hazır. Paragraf düzenleme, APA/Vancouver kaynakça formatlama "
            "ve bilimsel özet yazımı konularında yardımcı olabilirim."
        ),
    }
    st.markdown(f"""
    <div class='msg-row'>
        <div class='avatar ai'>🧬</div>
        <div>
            <div class='bubble ai'>{welcome_texts[mod]}</div>
            <div class='msg-time'>{datetime.now().strftime("%H:%M")}</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

for msg in st.session_state.messages:
    role_class = "user" if msg["role"] == "user" else "ai"
    avatar = "👤" if msg["role"] == "user" else "🧬"
    content = msg["content"].replace("\n", "<br>")
    t = msg.get("time", "")
    st.markdown(f"""
    <div class='msg-row {role_class}'>
        <div class='avatar {role_class}'>{avatar}</div>
        <div>
            <div class='bubble {role_class}'>{content}</div>
            <div class='msg-time'>{t}</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("</div>", unsafe_allow_html=True)

# ── INPUT AREA ────────────────────────────────────────────────────────────────
st.markdown("<br>", unsafe_allow_html=True)
col_input, col_btn = st.columns([5, 1])
with col_input:
    user_input = st.text_input(
        "Mesajınız",
        placeholder=f"{module_icons[mod]} {mod} modülünde sorunuzu yazın...",
        label_visibility="collapsed",
        key="user_input",
    )
with col_btn:
    send_clicked = st.button("Gönder →", use_container_width=True, type="primary")

# ── SEND LOGIC ────────────────────────────────────────────────────────────────
def send_message(content: str):
    if not st.session_state.api_key:
        st.error("⚠️ Lütfen sol menüden OpenRouter API anahtarınızı girin.")
        return
    ts = datetime.now().strftime("%H:%M")
    st.session_state.messages.append({"role": "user", "content": content, "time": ts})

    # Call model
    with st.spinner(""):
        reply = chat_with_model(
            st.session_state.api_key,
            st.session_state.module,
            st.session_state.messages[:-1] + [{"role": "user", "content": content}],
        )

    st.session_state.messages.append({
        "role": "assistant",
        "content": reply,
        "time": datetime.now().strftime("%H:%M"),
    })
    st.rerun()

if quick_text:
    send_message(quick_text)
elif send_clicked and user_input.strip():
    send_message(user_input.strip())

# ── FOOTER ────────────────────────────────────────────────────────────────────
st.markdown("""
<div style='text-align:center;padding:2rem 0 1rem;
     font-size:.72rem;color:#334155;letter-spacing:.4px;'>
    THESISAI · Powered by Gemini 1.5 Pro via OpenRouter ·
    <span style='color:#1e3a5f;'>Eczacılık Tez Destek Platformu</span>
</div>
""", unsafe_allow_html=True)
