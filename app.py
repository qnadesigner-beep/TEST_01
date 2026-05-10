import os
import json
import base64
import pathlib
import openai
import streamlit as st
from dotenv import load_dotenv

load_dotenv()

try:
    _api_key = st.secrets["OPENAI_API_KEY"]
except Exception:
    _api_key = os.getenv("OPENAI_API_KEY", "")

if not _api_key:
    st.error("OPENAI_API_KEY가 설정되지 않았습니다. Streamlit Cloud Secrets에 키를 추가해주세요.")
    st.stop()

client = openai.OpenAI(api_key=_api_key)

# ── System Prompts ─────────────────────────────────────────────────────────────

IMAGE_PROMPT_SYSTEM = (
    "You are a professional creative director for high-end lifestyle and interior magazines. "
    "Analyze the text and create exactly 3 image prompts that visually represent the content. "
    'Reply in JSON format: {"images": [{"description": "...", "prompt": "..."}, ...]}. '
    "description: Korean (1-2 sentences) explaining the visual concept. "
    "prompt: English, structured with labeled sections: "
    "[Subject] | [Environment] | [Lighting] | [Camera] | [Texture] | [Mood]. "
    "End with: Photorealistic professional photography. No text or logos. Minimum 80 words."
)

SEO_BLOG_SYSTEM = (
    "당신은 네이버 블로그 SEO 최적화 전문 작가입니다. 아래 규칙을 빠짐없이 지켜 작성하세요.\n\n"

    "【키워드 전략】\n"
    "- 입력 키워드의 형태소를 분석해 연관도 높은 단어군 5개를 related_keywords에 추출하세요.\n"
    "- 본문 전체에서 동일 단어·반복 표현을 철저히 피하고 유의어·우회 표현으로 다양하게 서술하세요.\n"
    "- 사전적 정의나 개념 설명은 배제하고 실질적·경험적 정보 위주로 작성하세요.\n"
    "- 질의 의도를 파악해 키워드 형태소를 각 본문에 자연스럽게 분배하세요.\n\n"

    "【제목 규칙】\n"
    "- 형식: 메인키워드를 맨 왼쪽에 배치 + 부사·꾸밈어 등 구체적 의미 없는 수식어로 구성\n"
    "- 클릭률 높은 표현 사용 (궁금증 유발, 숫자, 이득 강조), 30자 이내\n\n"

    "【구조 규칙 — 서론·본론1·본론2·결론 순서】\n"
    "각 파트는 반드시 소제목 → 인용구 → 본문 순서로 작성하세요.\n"
    "- 서론 소제목: 제목과 완전히 동일하게\n"
    "- 본론1·본론2 소제목: 제목의 핵심어를 발췌해 세분화\n"
    "- 결론 소제목: 행동 유도형 마무리 문장\n"
    "- 인용구: 해당 본문의 핵심 내용을 1문장으로 임팩트 있게 요약 (따옴표 없이)\n"
    "- 본문: 보고서 형식, 250자 내외, 동일 단어 반복 절대 금지\n\n"

    "반드시 아래 JSON 형식으로만 응답하세요:\n"
    '{"title": "제목", '
    '"related_keywords": ["연관어1", "연관어2", "연관어3", "연관어4", "연관어5"], '
    '"sections": ['
    '{"type": "서론", "heading": "소제목", "quote": "인용구", "body": "본문"}, '
    '{"type": "본론1", "heading": "소제목", "quote": "인용구", "body": "본문"}, '
    '{"type": "본론2", "heading": "소제목", "quote": "인용구", "body": "본문"}, '
    '{"type": "결론", "heading": "소제목", "quote": "인용구", "body": "본문"}], '
    '"hashtags": ["태그1","태그2","태그3","태그4","태그5","태그6","태그7","태그8","태그9","태그10","태그11","태그12"]}'
)


def generate_image_prompts(text: str) -> list[dict]:
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": IMAGE_PROMPT_SYSTEM},
            {"role": "user", "content": text},
        ],
        max_tokens=2048,
        response_format={"type": "json_object"},
    )
    return json.loads(response.choices[0].message.content)["images"]


def generate_seo_blog(keyword: str) -> dict:
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": SEO_BLOG_SYSTEM},
            {"role": "user", "content": keyword},
        ],
        max_tokens=3000,
        response_format={"type": "json_object"},
    )
    return json.loads(response.choices[0].message.content)


def generate_image(prompt: str) -> bytes:
    response = client.images.generate(
        model="gpt-image-1.5",
        prompt=prompt,
        size="1536x1024",
        quality="medium",
        n=1,
    )
    return base64.b64decode(response.data[0].b64_json)


# ── Page Config & CSS ─────────────────────────────────────────────────────────

st.set_page_config(page_title="블로그 디렉터", layout="wide")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@400;700;900&display=swap');

.stApp { background-color: #eeeee2; }
[data-testid="stHeader"] { background-color: #eeeee2; }
[data-testid="stMainBlockContainer"] { padding-top: 0 !important; }

/* ── 히어로 이미지 ── */
.hero-img {
    width: 100%;
    border-radius: 24px;
    margin-bottom: 24px;
    display: block;
}

/* ── 입력 카드 ── */
.input-card {
    background: #ffffff;
    border-radius: 24px;
    padding: 32px 36px 28px;
    margin-bottom: 20px;
}
.input-card-label {
    font-size: 1.4rem;
    font-weight: 800;
    color: #1a1a1a;
    margin-bottom: 6px;
}
.input-card-sub {
    font-size: 0.88rem;
    color: #888;
    margin-bottom: 20px;
}
.example-chips {
    display: flex;
    flex-wrap: wrap;
    gap: 8px;
    margin-top: 14px;
}
.chip {
    background: #F9ECEA;
    color: #C0392B99;
    border-radius: 30px;
    padding: 5px 14px;
    font-size: 0.82rem;
    font-weight: 600;
    border: 1.5px solid #E8A09A;
}

/* ── 입력 필드 강조 ── */
.stTextInput > div > div > input {
    background: #ffffff !important;
    border: none !important;
    border-radius: 14px !important;
    font-size: 1.05rem !important;
    padding: 14px 18px !important;
    color: #1a1a1a !important;
    box-shadow: none !important;
    outline: none !important;
}
.stTextInput > div > div > input:focus {
    border: none !important;
    box-shadow: none !important;
    outline: none !important;
}
.stTextInput > div > div > input::placeholder {
    color: #bbb !important;
    font-size: 0.95rem !important;
}

/* ── 생성 버튼 강조 ── */
.stButton > button[kind="primary"] {
    background: #C0392B !important;
    color: #ffffff !important;
    border: none !important;
    border-radius: 14px !important;
    font-size: 1rem !important;
    font-weight: 700 !important;
    padding: 12px 24px !important;
    box-shadow: none !important;
    transition: background 0.15s ease !important;
}
.stButton > button[kind="primary"]:hover {
    background: #A93226 !important;
}

/* ── 카드 ── */
.card-yellow {
    background: #FFB84C; border-radius: 20px;
    padding: 22px 24px; margin-bottom: 14px; color: #1a1a1a;
}
.card-blue {
    background: #B8D4F5; border-radius: 20px;
    padding: 22px 24px; margin-bottom: 14px; color: #1a1a1a;
}
.card-white {
    background: #ffffff; border-radius: 20px;
    padding: 24px; margin-bottom: 14px;
}
.card-purple {
    background: #C8BBFF; border-radius: 20px;
    padding: 22px 24px; margin-bottom: 14px; color: #1a1a1a;
}
.section-heading { font-size: 1.05rem; font-weight: 700; margin-bottom: 10px; }
.title-label {
    font-size: 0.78rem; font-weight: 600; opacity: 0.65;
    margin-bottom: 4px; letter-spacing: 0.04em; text-transform: uppercase;
}
.title-text { font-size: 1.35rem; font-weight: 800; line-height: 1.4; }
.hashtag-wrap { display: flex; flex-wrap: wrap; gap: 8px; }
.hashtag {
    background: #eeeee2; border-radius: 30px; padding: 5px 14px;
    font-size: 0.85rem; color: #5B4FCF; font-weight: 600;
}
</style>
""", unsafe_allow_html=True)

# ── 히어로 헤더 ───────────────────────────────────────────────────────────────

CHARACTER_SVG = """
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 260 210" width="220" height="185">
  <!-- 책상 -->
  <line x1="10" y1="178" x2="250" y2="178" stroke="#1a1a1a" stroke-width="2.8" stroke-linecap="round"/>

  <!-- 노트북 받침 -->
  <rect x="60" y="152" width="125" height="26" rx="5"
        fill="#F5F0E8" stroke="#1a1a1a" stroke-width="2.5"/>

  <!-- 노트북 화면 -->
  <path d="M72 152 L82 88 L198 88 L208 152"
        fill="#F5F0E8" stroke="#1a1a1a" stroke-width="2.5" stroke-linejoin="round"/>
  <!-- 화면 내용 줄 -->
  <line x1="100" y1="104" x2="155" y2="104" stroke="#1a1a1a" stroke-width="1.8" stroke-linecap="round"/>
  <line x1="100" y1="116" x2="178" y2="116" stroke="#1a1a1a" stroke-width="1.8" stroke-linecap="round"/>
  <line x1="100" y1="128" x2="168" y2="128" stroke="#1a1a1a" stroke-width="1.8" stroke-linecap="round"/>
  <line x1="100" y1="140" x2="148" y2="140" stroke="#1a1a1a" stroke-width="1.8" stroke-linecap="round"/>

  <!-- 몸통 -->
  <path d="M108 152 Q100 130 104 108 Q108 92 130 90 Q152 92 156 108 Q160 130 152 152"
        fill="#F5F0E8" stroke="#1a1a1a" stroke-width="2.5" stroke-linejoin="round"/>

  <!-- 머리 -->
  <ellipse cx="130" cy="60" rx="30" ry="32"
           fill="#F5F0E8" stroke="#1a1a1a" stroke-width="2.5"/>

  <!-- 머리카락 -->
  <path d="M100 52 Q104 24 130 26 Q156 24 160 52 Q148 38 130 40 Q112 38 100 52"
        fill="#1a1a1a" stroke="#1a1a1a" stroke-width="1"/>

  <!-- 눈 (찡그린) -->
  <path d="M116 56 Q120 52 124 56" fill="none" stroke="#1a1a1a" stroke-width="2.2" stroke-linecap="round"/>
  <path d="M136 56 Q140 52 144 56" fill="none" stroke="#1a1a1a" stroke-width="2.2" stroke-linecap="round"/>

  <!-- 입 (살짝 내려감) -->
  <path d="M122 72 Q130 68 138 72" fill="none" stroke="#1a1a1a" stroke-width="2" stroke-linecap="round"/>

  <!-- 양 손 → 관자놀이 -->
  <path d="M104 108 Q82 118 88 60" fill="none" stroke="#1a1a1a" stroke-width="2.5" stroke-linecap="round"/>
  <path d="M156 108 Q178 118 172 60" fill="none" stroke="#1a1a1a" stroke-width="2.5" stroke-linecap="round"/>
  <!-- 손 모양 -->
  <circle cx="88" cy="60" r="7" fill="#F5F0E8" stroke="#1a1a1a" stroke-width="2"/>
  <circle cx="172" cy="60" r="7" fill="#F5F0E8" stroke="#1a1a1a" stroke-width="2"/>

  <!-- 스트레스 물결선 -->
  <path d="M148 28 Q153 20 158 28 Q163 20 168 28 Q173 20 178 28"
        fill="none" stroke="#1a1a1a" stroke-width="2.2" stroke-linecap="round"/>
  <path d="M155 18 Q160 10 165 18 Q170 10 175 18"
        fill="none" stroke="#1a1a1a" stroke-width="2" stroke-linecap="round"/>

  <!-- 커피컵 -->
  <rect x="210" y="153" width="26" height="24" rx="4"
        fill="#F5F0E8" stroke="#1a1a1a" stroke-width="2.5"/>
  <path d="M236 160 Q246 160 246 169 Q246 178 236 178"
        fill="none" stroke="#1a1a1a" stroke-width="2" stroke-linecap="round"/>
  <!-- 커피 스팀 -->
  <path d="M218 150 Q221 143 218 136" fill="none" stroke="#1a1a1a" stroke-width="1.8" stroke-linecap="round"/>
  <path d="M226 150 Q229 143 226 136" fill="none" stroke="#1a1a1a" stroke-width="1.8" stroke-linecap="round"/>

  <!-- 연필꽂이 -->
  <line x1="32" y1="178" x2="32" y2="154" stroke="#1a1a1a" stroke-width="2.2" stroke-linecap="round"/>
  <line x1="25" y1="178" x2="25" y2="160" stroke="#1a1a1a" stroke-width="2.2" stroke-linecap="round"/>
  <line x1="39" y1="178" x2="39" y2="158" stroke="#1a1a1a" stroke-width="2.2" stroke-linecap="round"/>
</svg>
"""

# ── 히어로 이미지 ─────────────────────────────────────────────────────────────

hero_path = pathlib.Path(__file__).parent / "hero.png"
if hero_path.exists():
    with open(hero_path, "rb") as f:
        hero_b64 = base64.b64encode(f.read()).decode()
    st.markdown(
        f'<img class="hero-img" src="data:image/png;base64,{hero_b64}" alt="블로그 디렉터"/>',
        unsafe_allow_html=True,
    )
else:
    svg_b64 = base64.b64encode(CHARACTER_SVG.encode("utf-8")).decode("utf-8")
    st.markdown(f"""
    <div style="background:#F5F0E8;border-radius:24px;padding:40px 48px;
                display:flex;align-items:center;gap:36px;margin-bottom:24px;">
      <div style="flex:1;">
        <div style="display:inline-block;background:#E8E0FF;color:#5B4FCF;
                    font-size:0.78rem;font-weight:700;letter-spacing:0.08em;
                    text-transform:uppercase;padding:5px 14px;border-radius:30px;
                    margin-bottom:12px;">AI BLOG TOOL</div>
        <div style="font-size:3rem;font-weight:900;line-height:1.1;margin-bottom:10px;">
          <span style="color:#C0392B;">블로그</span> 디렉터</div>
        <div style="font-size:0.95rem;color:#666;line-height:1.6;">
          키워드 하나로 네이버 SEO 블로그 글과<br>어울리는 이미지 3장을 한 번에 만들어드립니다.
        </div>
      </div>
      <img src="data:image/svg+xml;base64,{svg_b64}" width="220" height="185" alt="character"/>
    </div>
    """, unsafe_allow_html=True)

# ── Session State ─────────────────────────────────────────────────────────────

for key, default in [("seo_result", None), ("seo_images", []),
                     ("img_only_images", [])]:
    if key not in st.session_state:
        st.session_state[key] = default

# ── 아이콘 로드 ───────────────────────────────────────────────────────────────

icon_path = pathlib.Path(__file__).parent / "icon_generate.png"
icon_html = ""
if icon_path.exists():
    with open(icon_path, "rb") as f:
        icon_b64 = base64.b64encode(f.read()).decode()
    icon_html = f'<img src="data:image/png;base64,{icon_b64}" style="width:52px;height:52px;object-fit:contain;display:block;margin:0 auto;" alt="generate"/>'

# ── 탭 ────────────────────────────────────────────────────────────────────────

tab1, tab2 = st.tabs(["📝 SEO 글 + 이미지", "🖼️ 원문 → 이미지"])

# ════════════════════════════════════════════════════════
# TAB 1 — 키워드 → SEO 글 + 이미지
# ════════════════════════════════════════════════════════
with tab1:
    st.markdown("""
    <div class="input-card">
      <div class="input-card-label">어떤 주제로 블로그를 써볼까요?</div>
      <div class="input-card-sub">키워드나 주제를 입력하면 SEO 최적화 글과 이미지 3장을 자동으로 만들어드립니다.</div>
    </div>
    """, unsafe_allow_html=True)

    examples = ["강남 브런치 카페", "재택근무 생산성", "제주도 한달살기", "홈카페 인테리어", "다이어트 식단"]
    chips_html = "".join(f'<span class="chip">#{e}</span>' for e in examples)
    st.markdown(f'<div style="margin-bottom:16px;"><div style="font-size:0.8rem;color:#aaa;margin-bottom:8px;">예시 키워드</div><div class="example-chips">{chips_html}</div></div>', unsafe_allow_html=True)

    keyword = st.text_input(
        label="keyword",
        placeholder="예: 강남 브런치 카페, 재택근무 생산성 높이는 법, 제주도 한달살기...",
        label_visibility="collapsed",
    )

    col_icon, col_btn, _ = st.columns([0.7, 2.3, 3])
    with col_icon:
        if icon_html:
            st.markdown(
                f'<div style="display:flex;align-items:center;height:100%;padding-top:4px;">{icon_html}</div>',
                unsafe_allow_html=True,
            )
    with col_btn:
        generate = st.button("SEO 글 + 이미지 생성", type="primary",
                             disabled=not keyword.strip(), use_container_width=True)

    if generate:
        st.session_state.seo_result = None
        st.session_state.seo_images = []

        with st.spinner("SEO 블로그 글 작성 중 (GPT-4o)..."):
            try:
                st.session_state.seo_result = generate_seo_blog(keyword)
            except Exception as e:
                st.error(f"글 생성 실패: {e}")
                st.stop()

        data = st.session_state.seo_result
        blog_content = " ".join(s["body"] for s in data.get("sections", []))

        with st.spinner("이미지 프롬프트 생성 중..."):
            try:
                img_prompts = generate_image_prompts(blog_content)
            except Exception as e:
                st.error(f"이미지 프롬프트 생성 실패: {e}")
                img_prompts = []

        for i, item in enumerate(img_prompts):
            with st.spinner(f"이미지 {i + 1}/3 생성 중 (gpt-image-1.5)..."):
                try:
                    st.session_state.seo_images.append({
                        "description": item["description"],
                        "prompt": item["prompt"],
                        "image_bytes": generate_image(item["prompt"]),
                    })
                except Exception as e:
                    st.error(f"이미지 {i + 1} 생성 실패: {e}")

    if st.session_state.seo_result:
        data = st.session_state.seo_result
        st.divider()

        st.markdown(f"""
        <div class="card-purple">
            <div class="title-label">제목</div>
            <div class="title-text">{data.get('title', '')}</div>
        </div>""", unsafe_allow_html=True)

        related = data.get("related_keywords", [])
        if related:
            kw_html = "".join(f'<span class="chip">#{k}</span>' for k in related)
            st.markdown(
                f'<div style="margin-bottom:20px;"><div style="font-size:0.8rem;color:#aaa;margin-bottom:8px;">연관 키워드</div>'
                f'<div class="example-chips">{kw_html}</div></div>',
                unsafe_allow_html=True,
            )

        section_colors = {"서론": "card-white", "본론1": "card-yellow", "본론2": "card-blue", "결론": "card-purple"}
        for section in data.get("sections", []):
            stype   = section.get("type", "")
            card_c  = section_colors.get(stype, "card-white")
            heading = section.get("heading", "")
            quote   = section.get("quote", "")
            body    = section.get("body", "")

            st.markdown(f"""
            <div class="{card_c}" style="margin-bottom:6px;">
                <div class="title-label">{stype}</div>
                <div class="section-heading" style="font-size:1.15rem;margin-bottom:12px;">{heading}</div>
            </div>""", unsafe_allow_html=True)

            if quote:
                st.markdown(f"""
                <div style="border-left:4px solid #C0392B;background:#FDF5F4;
                            border-radius:0 12px 12px 0;padding:14px 20px;
                            margin-bottom:6px;font-size:0.97rem;color:#7a2020;
                            font-style:italic;line-height:1.7;">{quote}</div>""",
                            unsafe_allow_html=True)

            st.markdown(f"""
            <div class="card-white" style="margin-bottom:20px;">
                <div style="line-height:1.9;font-size:0.97rem;">{body}</div>
            </div>""", unsafe_allow_html=True)

        tags_html = "".join(f'<span class="hashtag">#{t}</span>' for t in data.get("hashtags", []))
        st.markdown(f"""
        <div class="card-white">
            <div class="section-heading">해시태그</div>
            <div class="hashtag-wrap">{tags_html}</div>
        </div>""", unsafe_allow_html=True)

        full_text = f"{data.get('title', '')}\n\n"
        for s in data.get("sections", []):
            full_text += f"[{s.get('type','')}] {s.get('heading','')}\n"
            if s.get('quote'):
                full_text += f'"{s.get("quote","")}" \n\n'
            full_text += s.get('body', '') + "\n\n"
        full_text += " ".join(f"#{t}" for t in data.get("hashtags", []))

        with st.expander("📋 전체 글 복사"):
            st.text_area(label="copy", value=full_text, height=300,
                         label_visibility="collapsed", key="copy_area")

        if st.session_state.seo_images:
            st.divider()
            st.markdown("### 생성된 이미지")
            cols = st.columns(3)
            for i, (col, result) in enumerate(zip(cols, st.session_state.seo_images)):
                with col:
                    st.image(result["image_bytes"], use_container_width=True)
                    st.markdown(f"**{result['description']}**")
                    with st.expander(f"✏️ 프롬프트 {i + 1} 보기 / 수정"):
                        edited = st.text_area(
                            label="p", value=result["prompt"],
                            key=f"p_{i}", height=240, label_visibility="collapsed",
                        )
                        st.caption("프롬프트를 수정하고 버튼을 누르면 해당 이미지만 다시 생성합니다.")
                        if st.button(f"🔄 이미지 {i + 1} 다시 생성", key=f"regen_{i}", type="secondary"):
                            with st.spinner("재생성 중..."):
                                try:
                                    st.session_state.seo_images[i]["image_bytes"] = generate_image(edited)
                                    st.session_state.seo_images[i]["prompt"] = edited
                                    st.rerun()
                                except Exception as e:
                                    st.error(f"재생성 실패: {e}")

# ════════════════════════════════════════════════════════
# TAB 2 — 블로그 원문 → 이미지 생성
# ════════════════════════════════════════════════════════
with tab2:
    st.markdown("""
    <div class="input-card">
      <div class="input-card-label">블로그 원문을 붙여넣어 주세요</div>
      <div class="input-card-sub">작성된 블로그 글을 분석해 어울리는 이미지 3장을 만들어드립니다.</div>
    </div>
    """, unsafe_allow_html=True)

    blog_raw = st.text_area(
        label="blog_raw",
        placeholder="블로그 글 전체를 여기에 붙여넣으세요...",
        height=280,
        label_visibility="collapsed",
    )

    col_icon2, col_btn2, _ = st.columns([0.7, 2.3, 3])
    with col_icon2:
        if icon_html:
            st.markdown(
                f'<div style="display:flex;align-items:center;height:100%;padding-top:4px;">{icon_html}</div>',
                unsafe_allow_html=True,
            )
    with col_btn2:
        generate2 = st.button("이미지 3장 생성", type="primary",
                              disabled=not blog_raw.strip(), use_container_width=True)

    if generate2:
        st.session_state.img_only_images = []

        with st.spinner("이미지 프롬프트 생성 중..."):
            try:
                img_prompts2 = generate_image_prompts(blog_raw)
            except Exception as e:
                st.error(f"프롬프트 생성 실패: {e}")
                img_prompts2 = []

        for i, item in enumerate(img_prompts2):
            with st.spinner(f"이미지 {i + 1}/3 생성 중 (gpt-image-1.5)..."):
                try:
                    st.session_state.img_only_images.append({
                        "description": item["description"],
                        "prompt": item["prompt"],
                        "image_bytes": generate_image(item["prompt"]),
                    })
                except Exception as e:
                    st.error(f"이미지 {i + 1} 생성 실패: {e}")

    if st.session_state.img_only_images:
        st.divider()
        st.markdown("### 생성된 이미지")
        cols2 = st.columns(3)
        for i, (col, result) in enumerate(zip(cols2, st.session_state.img_only_images)):
            with col:
                st.image(result["image_bytes"], use_container_width=True)
                st.markdown(f"**{result['description']}**")
                with st.expander(f"✏️ 프롬프트 {i + 1} 보기 / 수정"):
                    edited2 = st.text_area(
                        label="p2", value=result["prompt"],
                        key=f"p2_{i}", height=240, label_visibility="collapsed",
                    )
                    st.caption("프롬프트를 수정하고 버튼을 누르면 해당 이미지만 다시 생성합니다.")
                    if st.button(f"🔄 이미지 {i + 1} 다시 생성", key=f"regen2_{i}", type="secondary"):
                        with st.spinner("재생성 중..."):
                            try:
                                st.session_state.img_only_images[i]["image_bytes"] = generate_image(edited2)
                                st.session_state.img_only_images[i]["prompt"] = edited2
                                st.rerun()
                            except Exception as e:
                                st.error(f"재생성 실패: {e}")
