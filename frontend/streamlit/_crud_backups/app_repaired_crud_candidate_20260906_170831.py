from __future__ import annotations

from pathlib import Path
import socket
import threading
import time

import pandas as pd
import requests
import streamlit as st
import uvicorn


from html import escape
# ============================================================
# APP CONFIG
# ============================================================

API_URL = "http://127.0.0.1:8000/api/v1"
PROJECT_ROOT = Path(__file__).resolve().parents[2]
STORAGE_DIR = PROJECT_ROOT / "storage"
STORAGE_DIR.mkdir(
    parents=True,
    exist_ok=True,
)

st.set_page_config(
    page_title="ChainPulse AI",
    page_icon="📦",
    layout="wide",
    initial_sidebar_state="expanded",
)


# ============================================================
# SESSION STATE
# ============================================================

DEFAULT_STATE = {
    "token": None,
    "user": None,
    "current_page": "Dashboard",
    "theme": "light",
    "ai_decision": None,
    "active_connection_id": None,
    "mapping_result": None,
    "validation_result": None,
    "report_bytes": None,
    "report_name": None,
    "report_mime": None,
}

for key, value in DEFAULT_STATE.items():
    if key not in st.session_state:
        st.session_state[key] = value


# ============================================================
# BACKEND AUTO START
# ============================================================


# ============================================================
# CHAINPULSE AI - UI FOUNDATION
# ============================================================


# ============================================================
# CHAINPULSE AI - APPLICATION NAVIGATION
# ============================================================


def chainpulse_navigation():
    """
    Central ChainPulse application navigation.

    Keeps all existing page names compatible with the
    existing page execution layer.
    """

    pages = [
        ("📊", "Dashboard"),
        ("📦", "Products"),
        ("📈", "Demand"),
        ("🔮", "Forecasting"),
        ("📦", "Inventory"),
        ("🚚", "Suppliers"),
        ("〰️", "Bullwhip"),
        ("⚠️", "Risk"),
        ("🎯", "Decisions"),
        ("🧪", "Simulations"),
        ("🤖", "AI Explain"),
        ("🔌", "Connect Data"),
        ("📄", "Reports"),
    ]

    current = st.session_state.get(
        "current_page",
        "Dashboard",
    )

    # --------------------------------------------------------
    # BRAND
    # --------------------------------------------------------

    st.sidebar.markdown(
        """
        <div class="cp-brand">
            <span class="cp-logo">📦</span>
            <span class="cp-brand-title">
                ChainPulse AI
            </span>
            <div class="cp-brand-subtitle">
                Supply-chain intelligence
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.sidebar.markdown(
        "<div style='color:#64748b;font-size:0.68rem;"
        "font-weight:700;text-transform:uppercase;"
        "letter-spacing:.08em;margin:0.3rem 0 0.5rem;'>"
        "Workspace"
        "</div>",
        unsafe_allow_html=True,
    )

    labels = [
        f"{icon}  {name}"
        for icon, name in pages
    ]

    current_label = (
        next(
            (
                f"{icon}  {name}"
                for icon, name in pages
                if name == current
            ),
            labels[0],
        )
    )

    selected_label = st.sidebar.radio(
        "Navigation",
        labels,
        index=labels.index(current_label),
        label_visibility="collapsed",
        key="chainpulse_main_navigation",
    )

    selected_page = next(
        (
            name
            for icon, name in pages
            if f"{icon}  {name}" == selected_label
        ),
        "Dashboard",
    )

    st.session_state.current_page = selected_page

    # --------------------------------------------------------
    # USER AREA
    # --------------------------------------------------------

    user = st.session_state.get("user")

    st.sidebar.divider()

    if user:
        name = (
            user.get("name")
            or user.get("email")
            or "User"
        )

        email = user.get(
            "email",
            "",
        )

        st.sidebar.markdown(
            f"""
            <div style="
                padding:0.7rem;
                border-radius:12px;
                background:rgba(255,255,255,0.06);
                border:1px solid rgba(255,255,255,0.08);
            ">
                <div style="
                    font-weight:700;
                    color:white;
                    font-size:0.85rem;
                ">
                    👤 {name}
                </div>
                <div style="
                    color:#94a3b8;
                    font-size:0.7rem;
                    margin-top:0.15rem;
                    overflow:hidden;
                    text-overflow:ellipsis;
                ">
                    {email}
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    # --------------------------------------------------------
    # SYSTEM STATUS
    # --------------------------------------------------------

    st.sidebar.markdown(
        """
        <div style="
            margin-top:0.8rem;
            padding:0.45rem 0.6rem;
            border-radius:9px;
            background:rgba(34,197,94,0.08);
            color:#86efac;
            font-size:0.7rem;
        ">
            ● ChainPulse services active
        </div>
        """,
        unsafe_allow_html=True,
    )

    # --------------------------------------------------------
    # LOGOUT
    # --------------------------------------------------------

    st.sidebar.divider()

    if st.sidebar.button(
        "🚪  Logout",
        key="chainpulse_logout_button",
        use_container_width=True,
    ):
        auth_keys = [
            "user",
            "token",
            "access_token",
            "jwt_token",
            "auth_token",
            "current_page",
            "chainpulse_main_navigation",
        ]

        for key in auth_keys:
            st.session_state.pop(key, None)

        st.rerun()

    return selected_page



def apply_chainpulse_theme():
    """
    ChainPulse AI professional SaaS design system.
    Presentation-only layer. Does not alter backend logic.
    """

    st.markdown(
        """
        <style>

        /* =====================================================
           GLOBAL
           ===================================================== */

        .stApp {
            background:
                linear-gradient(
                    180deg,
                    rgba(248,250,252,0.98) 0%,
                    rgba(241,245,249,0.98) 100%
                );
        }

        .main .block-container {
            max-width: 1450px;
            padding-top: 1.5rem;
            padding-bottom: 3rem;
        }

        /* =====================================================
           SIDEBAR
           ===================================================== */

        section[data-testid="stSidebar"] {
            background:
                linear-gradient(
                    180deg,
                    #0f172a 0%,
                    #111827 100%
                );
            border-right: 1px solid rgba(255,255,255,0.08);
        }

        section[data-testid="stSidebar"] > div {
            padding-top: 1rem;
        }

        section[data-testid="stSidebar"] * {
            color: #e5e7eb;
        }

        section[data-testid="stSidebar"] .stRadio label {
            border-radius: 10px;
            padding: 0.65rem 0.8rem;
            margin: 0.15rem 0;
            transition: all 0.15s ease;
        }

        section[data-testid="stSidebar"] .stRadio label:hover {
            background: rgba(255,255,255,0.08);
        }

        section[data-testid="stSidebar"] [data-baseweb="radio"] {
            margin-bottom: 2px;
        }

        /* =====================================================
           BRAND
           ===================================================== */

        .cp-brand {
            padding: 0.5rem 0.2rem 1.2rem 0.2rem;
        }

        .cp-brand-title {
            font-size: 1.25rem;
            font-weight: 800;
            letter-spacing: -0.03em;
            color: white;
        }

        .cp-brand-subtitle {
            font-size: 0.72rem;
            color: #94a3b8;
            margin-top: 0.15rem;
        }

        .cp-logo {
            display: inline-flex;
            align-items: center;
            justify-content: center;
            width: 38px;
            height: 38px;
            border-radius: 11px;
            background: linear-gradient(
                135deg,
                #2563eb,
                #7c3aed
            );
            color: white;
            font-size: 1.15rem;
            margin-right: 0.65rem;
            vertical-align: middle;
        }

        /* =====================================================
           TOP HEADER
           ===================================================== */

        .cp-header {
            display: flex;
            align-items: center;
            justify-content: space-between;
            padding: 0.3rem 0 1rem 0;
        }

        .cp-header-title {
            font-size: 1.9rem;
            font-weight: 800;
            color: #0f172a;
            letter-spacing: -0.035em;
        }

        .cp-header-subtitle {
            color: #64748b;
            font-size: 0.92rem;
            margin-top: 0.15rem;
        }

        /* =====================================================
           KPI CARDS
           ===================================================== */

        div[data-testid="stMetric"] {
            background: white;
            border: 1px solid #e2e8f0;
            border-radius: 16px;
            padding: 1rem 1.1rem;
            box-shadow:
                0 4px 14px rgba(15,23,42,0.045);
        }

        div[data-testid="stMetric"] label {
            color: #64748b !important;
            font-weight: 600;
        }

        div[data-testid="stMetricValue"] {
            color: #0f172a;
            font-weight: 800;
        }

        /* =====================================================
           BUTTONS
           ===================================================== */

        .stButton > button,
        .stDownloadButton > button {
            border-radius: 10px;
            min-height: 42px;
            font-weight: 650;
            border: 1px solid #dbe3ef;
            transition:
                transform 0.12s ease,
                box-shadow 0.12s ease;
        }

        .stButton > button:hover,
        .stDownloadButton > button:hover {
            transform: translateY(-1px);
            box-shadow:
                0 5px 14px rgba(15,23,42,0.10);
        }

        /* =====================================================
           INPUTS
           ===================================================== */

        div[data-baseweb="input"],
        div[data-baseweb="select"],
        textarea {
            border-radius: 10px !important;
        }

        /* =====================================================
           CONTAINERS / CARDS
           ===================================================== */

        div[data-testid="stExpander"] {
            border-radius: 14px;
            border: 1px solid #e2e8f0;
            background: white;
        }

        /* =====================================================
           DATAFRAMES
           ===================================================== */

        div[data-testid="stDataFrame"] {
            border-radius: 12px;
            overflow: hidden;
            border: 1px solid #e2e8f0;
        }

        /* =====================================================
           TABS
           ===================================================== */

        button[data-baseweb="tab"] {
            font-weight: 650;
        }

        /* =====================================================
           ALERTS
           ===================================================== */

        div[data-testid="stAlert"] {
            border-radius: 12px;
        }

        /* =====================================================
           FOOTER
           ===================================================== */

        .cp-footer {
            text-align: center;
            color: #94a3b8;
            font-size: 0.75rem;
            padding: 2rem 0 1rem 0;
        }

        /* =====================================================
           LOGIN
           ===================================================== */

        .cp-login-wrapper {
            max-width: 460px;
            margin: 5vh auto 0 auto;
            padding: 2rem;
            background: white;
            border: 1px solid #e2e8f0;
            border-radius: 20px;
            box-shadow:
                0 20px 50px rgba(15,23,42,0.08);
        }

        .cp-login-logo {
            width: 58px;
            height: 58px;
            display: flex;
            align-items: center;
            justify-content: center;
            margin: 0 auto 1rem auto;
            border-radius: 16px;
            background:
                linear-gradient(
                    135deg,
                    #2563eb,
                    #7c3aed
                );
            color: white;
            font-size: 1.7rem;
        }

        .cp-login-title {
            text-align: center;
            font-size: 1.7rem;
            font-weight: 800;
            color: #0f172a;
        }

        .cp-login-subtitle {
            text-align: center;
            color: #64748b;
            margin-bottom: 1.5rem;
        }

        /* =====================================================
           MOBILE
           ===================================================== */

        @media (max-width: 800px) {
            .main .block-container {
                padding-left: 1rem;
                padding-right: 1rem;
            }

            .cp-header-title {
                font-size: 1.45rem;
            }
        }

        </style>
        """,
        unsafe_allow_html=True,
    )


def chainpulse_header(
    page_title: str | None = None,
    page_description: str | None = None,
):

    title = page_title or "ChainPulse AI"

    description = (
        page_description
        or "Supply-chain intelligence platform"
    )

    st.markdown(
        f"""
        <div class="cp-header">

            <div class="cp-brand">

                <div class="cp-logo">
                    CP
                </div>

                <div>
                    <div class="cp-brand-name">
                        {title}
                    </div>

                    <div class="cp-brand-subtitle">
                        {description}
                    </div>
                </div>

            </div>

            <div class="cp-status">
                <span class="cp-status-dot"></span>
                System Online
            </div>

        </div>
        """,
        unsafe_allow_html=True,
    )


# Apply the global ChainPulse design system.
apply_chainpulse_theme()

def backend_is_running() -> bool:
    sock = socket.socket(
        socket.AF_INET,
        socket.SOCK_STREAM,
    )
    sock.settimeout(0.25)

    try:
        return (
            sock.connect_ex(
                ("127.0.0.1", 8000)
            )
            == 0
        )
    finally:
        sock.close()


def start_backend() -> None:
    uvicorn.run(
        "backend.main:app",
        host="127.0.0.1",
        port=8000,
        log_level="warning",
    )


def ensure_backend_running() -> None:
    if backend_is_running():
        return

    thread = threading.Thread(
        target=start_backend,
        daemon=True,
        name="chainpulse-api",
    )
    thread.start()

    for _ in range(40):
        if backend_is_running():
            return
        time.sleep(0.25)


ensure_backend_running()


# ============================================================
# THEME
# ============================================================

def apply_theme() -> None:

    dark = (
        st.session_state.theme
        == "dark"
    )

    if dark:
        bg = "#0b1220"
        panel = "#111827"
        panel2 = "#172033"
        text = "#f8fafc"
        muted = "#94a3b8"
        border = "#263244"
    else:
        bg = "#f6f8fc"
        panel = "#ffffff"
        panel2 = "#f1f5f9"
        text = "#0f172a"
        muted = "#64748b"
        border = "#e2e8f0"

    st.markdown(
        f"""
        <style>

        .stApp {{
            background: {bg};
            color: {text};
        }}

        .main .block-container {{
            max-width: 1500px;
            padding-top: 1.5rem;
            padding-bottom: 3rem;
            padding-left: 2rem;
            padding-right: 2rem;
        }}

        header[data-testid="stHeader"] {{
            background: transparent;
        }}

        section[data-testid="stSidebar"] {{
            background: {panel};
            border-right: 1px solid {border};
        }}

        .cp-brand {{
            display: flex;
            align-items: center;
            gap: 12px;
            margin-bottom: 10px;
        }}

        .cp-logo {{
            width: 42px;
            height: 42px;
            border-radius: 12px;
            display: flex;
            align-items: center;
            justify-content: center;
            background:
                linear-gradient(
                    135deg,
                    #2563eb,
                    #14b8a6
                );
            color: white;
            font-weight: 800;
            box-shadow:
                0 8px 22px
                rgba(37, 99, 235, 0.22);
        }}

        .cp-brand-title {{
            color: {text};
            font-size: 20px;
            font-weight: 800;
            line-height: 1;
        }}

        .cp-brand-subtitle {{
            color: {muted};
            font-size: 11px;
            margin-top: 4px;
        }}

        .cp-page-header {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 1rem;
        }}

        .cp-page-title {{
            font-size: 2rem;
            font-weight: 800;
            color: {text};
            letter-spacing: -0.03em;
        }}

        .cp-page-subtitle {{
            color: {muted};
            margin-top: 4px;
        }}

        div[data-testid="stMetric"] {{
            background: {panel};
            border: 1px solid {border};
            border-radius: 14px;
            padding: 1rem;
            box-shadow:
                0 4px 18px
                rgba(15, 23, 42, 0.04);
        }}

        div[data-testid="stMetricLabel"] {{
            color: {muted};
        }}

        div[data-testid="stMetricValue"] {{
            color: {text};
            font-weight: 800;
        }}

        .cp-card {{
            background: {panel};
            border: 1px solid {border};
            border-radius: 14px;
            padding: 1rem 1.1rem;
            margin-bottom: 0.8rem;
        }}

        .cp-muted {{
            color: {muted};
        }}

        .cp-small {{
            font-size: 12px;
            color: {muted};
        }}

        .stButton > button,
        .stDownloadButton > button {{
            border-radius: 9px;
            min-height: 42px;
            font-weight: 650;
        }}

        .stTextInput input,
        .stNumberInput input,
        .stTextArea textarea {{
            border-radius: 9px;
        }}

        div[data-baseweb="select"] > div {{
            border-radius: 9px;
        }}

        div[data-testid="stVerticalBlockBorderWrapper"] {{
            border-radius: 14px;
            border-color: {border};
            background: {panel};
        }}

        div[data-testid="stDataFrame"] {{
            border-radius: 12px;
            overflow: hidden;
        }}

        hr {{
            border-color: {border};
        }}

        .cp-footer {{
            text-align: center;
            color: {muted};
            font-size: 12px;
            padding: 1rem 0 0.2rem 0;
        }}

        </style>
        """,
        unsafe_allow_html=True,
    )


apply_theme()


# ============================================================
# HELPERS
# ============================================================


def api_request(
    method: str,
    endpoint: str,
    **kwargs,
):
    if not st.session_state.token:
        return None

    headers = kwargs.pop(
        "headers",
        {},
    )

    headers["Authorization"] = (
        "Bearer "
        + st.session_state.token
    )

    last_error = None

    for attempt in range(3):

        if not backend_is_running():
            try:
                ensure_backend_running()
            except Exception as exc:
                last_error = exc
                time.sleep(0.5)
                continue

        try:
            response = requests.request(
                method=method,
                url=f"{API_URL}{endpoint}",
                headers=headers,
                timeout=60,
                **kwargs,
            )

        except requests.ConnectionError as exc:
            last_error = exc

            try:
                ensure_backend_running()
            except Exception:
                pass

            time.sleep(0.75)
            continue

        except requests.RequestException as exc:
            st.error(
                "Unable to connect to ChainPulse API."
            )
            st.caption(str(exc))
            return None

        if response.status_code == 401:
            st.session_state.token = None
            st.session_state.user = None

            st.warning(
                "Your session expired. Please log in again."
            )

            st.rerun()

        if response.status_code >= 400:

            try:
                detail = response.json()
            except Exception:
                detail = response.text

            st.error(
                f"API error {response.status_code}: "
                f"{detail}"
            )

            return None

        if not response.content:
            return {}

        content_type = response.headers.get(
            "content-type",
            "",
        )

        if "application/json" in content_type:
            return response.json()

        return response.content

    st.error(
        "ChainPulse API is unavailable."
    )

    if last_error:
        st.caption(
            "The backend was started automatically, "
            "but it did not become reachable."
        )

    return None


def number(value) -> str:
    if value is None:
        return "—"

    try:
        return f"{float(value):,.2f}"
    except Exception:
        return str(value)


def risk_badge(level) -> str:
    value = str(
        level or "unknown"
    ).lower()

    mapping = {
        "low": "🟢 LOW",
        "medium": "🟡 MEDIUM",
        "high": "🟠 HIGH",
        "critical": "🔴 CRITICAL",
    }

    return mapping.get(
        value,
        f"⚪ {value.upper()}",
    )


def page_header(
    title: str,
    subtitle: str = "",
):
    st.markdown(
        f"""
        <div class="cp-page-header">
            <div>
                <div class="cp-page-title">
                    {title}
                </div>
                <div class="cp-page-subtitle">
                    {subtitle}
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def logout_user() -> None:
    """Clear all authentication state and return the user to the login screen."""
    for key in (
        "token",
        "user",
        "organization_id",
        "selected_product",
        "selected_supplier",
    ):
        st.session_state.pop(key, None)
def login_required() -> bool:
    return bool(
        st.session_state.token
    )


# ============================================================
# OAUTH CALLBACK
# ============================================================

def handle_oauth_callback():

    oauth_code = st.query_params.get(
        "oauth_code"
    )

    if not oauth_code:
        return

    try:
        response = requests.post(
            f"{API_URL}/auth/oauth/exchange",
            params={
                "oauth_code": oauth_code,
            },
            timeout=30,
        )

        if response.status_code != 200:
            st.error(
                f"OAuth login failed: "
                f"{response.text}"
            )
            return

        data = response.json()

        st.session_state.token = (
            data["access_token"]
        )

        st.query_params.clear()
        st.rerun()

    except requests.RequestException as exc:
        st.error(
            "Unable to connect to ChainPulse API."
        )
        st.caption(str(exc))


handle_oauth_callback()


# ============================================================

# ============================================================
# APPLICATION NAVIGATION
# ============================================================


# LOGIN
# ============================================================

def render_login():
    """
    Public authentication landing page.

    Supports:
    - Existing-user sign in
    - New organization + admin onboarding
    - OAuth provider entry points
    """

    st.markdown(
        "<div style='height:6vh'></div>",
        unsafe_allow_html=True,
    )

    left, center, right = st.columns(
        [1, 2, 1]
    )

    with center:

        st.markdown(
            """
            <div class="cp-card"
                 style="padding:2rem; margin-bottom:1rem;">
                <div class="cp-brand">
                    <div class="cp-logo">CP</div>
                    <div>
                        <div class="cp-brand-title">
                            ChainPulse AI
                        </div>
                        <div class="cp-brand-subtitle">
                            Supply-chain intelligence
                        </div>
                    </div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        st.markdown(
            "### Welcome to ChainPulse AI"
        )

        st.caption(
            "Predict. Detect. Decide."
        )

        sign_in_tab, create_account_tab = st.tabs(
            [
                "Sign In",
                "Create Account",
            ]
        )

        # ============================================================
        # SIGN IN
        # ============================================================

        with sign_in_tab:

            st.subheader(
                "Welcome back"
            )

            st.caption(
                "Sign in to your organization workspace."
            )

            with st.form(
                "login_form",
                clear_on_submit=False,
            ):

                email = st.text_input(
                    "Email",
                    placeholder="you@company.com",
                    key="login_email",
                )

                password = st.text_input(
                    "Password",
                    type="password",
                    key="login_password",
                )

                submitted = st.form_submit_button(
                    "Sign In",
                    use_container_width=True,
                    type="primary",
                )

            if submitted:

                clean_email = email.strip().lower()

                if not clean_email or not password:
                    st.warning(
                        "Enter both email and password."
                    )

                else:

                    try:

                        response = requests.post(
                            f"{API_URL}/auth/login",
                            json={
                                "email": clean_email,
                                "password": password,
                            },
                            timeout=20,
                        )

                        if response.status_code == 200:

                            data = response.json()

                            access_token = data.get(
                                "access_token"
                            )

                            if not access_token:
                                st.error(
                                    "Authentication succeeded but "
                                    "no access token was returned."
                                )
                            else:

                                st.session_state.token = (
                                    access_token
                                )

                                user = api_request(
                                    "GET",
                                    "/auth/me",
                                )

                                if user:

                                    st.session_state.user = (
                                        user
                                    )

                                    st.success(
                                        "Signed in successfully."
                                    )

                                    st.rerun()

                                else:

                                    st.session_state.token = None

                                    st.error(
                                        "Unable to load your user profile."
                                    )

                        elif response.status_code == 401:

                            st.error(
                                "Invalid email or password."
                            )

                        elif response.status_code == 403:

                            st.error(
                                "Your account does not have access."
                            )

                        else:

                            try:
                                detail = response.json().get(
                                    "detail",
                                    "Unable to sign in.",
                                )
                            except Exception:
                                detail = (
                                    "Unable to sign in."
                                )

                            st.error(
                                f"Sign in failed: {detail}"
                            )

                    except requests.RequestException as exc:

                        st.error(
                            "Unable to connect to ChainPulse API."
                        )

                        st.caption(str(exc))

        # ============================================================
        # CREATE ACCOUNT
        # ============================================================

        with create_account_tab:

            st.subheader(
                "Create your workspace"
            )

            st.caption(
                "Create your organization and administrator account."
            )

            with st.form(
                "create_account_form",
                clear_on_submit=False,
            ):

                organization_name = st.text_input(
                    "Organization name",
                    placeholder="Acme Supply Chain",
                    key="signup_organization",
                )

                full_name = st.text_input(
                    "Your name",
                    placeholder="John Smith",
                    key="signup_name",
                )

                signup_email = st.text_input(
                    "Work email",
                    placeholder="john@company.com",
                    key="signup_email",
                )

                signup_password = st.text_input(
                    "Password",
                    type="password",
                    key="signup_password",
                    help=(
                        "Use 8–72 characters."
                    ),
                )

                confirm_password = st.text_input(
                    "Confirm password",
                    type="password",
                    key="signup_confirm_password",
                )

                create_submitted = st.form_submit_button(
                    "Create Account",
                    use_container_width=True,
                    type="primary",
                )

            if create_submitted:

                clean_org = (
                    organization_name.strip()
                )

                clean_name = (
                    full_name.strip()
                )

                clean_email = (
                    signup_email.strip().lower()
                )

                validation_error = None

                if not clean_org:
                    validation_error = (
                        "Enter your organization name."
                    )

                elif len(clean_org) > 150:
                    validation_error = (
                        "Organization name must be 150 characters or fewer."
                    )

                elif not clean_name:
                    validation_error = (
                        "Enter your name."
                    )

                elif len(clean_name) < 2:
                    validation_error = (
                        "Name must contain at least 2 characters."
                    )

                elif len(clean_name) > 150:
                    validation_error = (
                        "Name must be 150 characters or fewer."
                    )

                elif not clean_email:
                    validation_error = (
                        "Enter your email address."
                    )

                elif not signup_password:
                    validation_error = (
                        "Create a password."
                    )

                elif len(signup_password) < 8:
                    validation_error = (
                        "Password must contain at least 8 characters."
                    )

                elif len(signup_password) > 72:
                    validation_error = (
                        "Password must contain 72 characters or fewer."
                    )

                elif signup_password != confirm_password:
                    validation_error = (
                        "Passwords do not match."
                    )

                if validation_error:

                    st.warning(
                        validation_error
                    )

                else:

                    try:

                        response = requests.post(
                            f"{API_URL}/auth/onboard",
                            json={
                                "organization_name": clean_org,
                                "name": clean_name,
                                "email": clean_email,
                                "password": signup_password,
                            },
                            timeout=20,
                        )

                        if response.status_code == 201:

                            data = response.json()

                            access_token = data.get(
                                "access_token"
                            )

                            if not access_token:

                                st.error(
                                    "Account was created but "
                                    "no access token was returned."
                                )

                            else:

                                st.session_state.token = (
                                    access_token
                                )

                                user = api_request(
                                    "GET",
                                    "/auth/me",
                                )

                                if user:

                                    st.session_state.user = (
                                        user
                                    )

                                    st.success(
                                        "Account created successfully."
                                    )

                                    st.rerun()

                                else:

                                    st.session_state.token = None

                                    st.error(
                                        "Account was created, "
                                        "but your profile could not be loaded."
                                    )

                        elif response.status_code == 409:

                            try:
                                detail = response.json().get(
                                    "detail",
                                    "An account or organization already exists.",
                                )
                            except Exception:
                                detail = (
                                    "An account or organization already exists."
                                )

                            st.error(
                                detail
                            )

                        elif response.status_code == 400:

                            try:
                                detail = response.json().get(
                                    "detail",
                                    "Invalid account information.",
                                )
                            except Exception:
                                detail = (
                                    "Invalid account information."
                                )

                            st.error(
                                detail
                            )

                        else:

                            try:
                                detail = response.json().get(
                                    "detail",
                                    "Unable to create account.",
                                )
                            except Exception:
                                detail = (
                                    "Unable to create account."
                                )

                            st.error(
                                f"Account creation failed: {detail}"
                            )

                    except requests.RequestException as exc:

                        st.error(
                            "Unable to connect to ChainPulse API."
                        )

                        st.caption(str(exc))

        # ============================================================
        # OAUTH
        # ============================================================

        st.divider()

        st.caption(
            "Or continue with"
        )

        c1, c2, c3 = st.columns(3)

        with c1:

            st.link_button(
                "🔵 Google",
                f"{API_URL}/auth/oauth/google/login",
                use_container_width=True,
            )

        with c2:

            st.link_button(
                "🟦 Microsoft",
                f"{API_URL}/auth/oauth/microsoft/login",
                use_container_width=True,
            )

        with c3:

            st.link_button(
                "Ⓜ️ Meta",
                f"{API_URL}/auth/oauth/meta/login",
                use_container_width=True,
            )

        st.caption(
            "OAuth providers must be configured by an administrator."
        )

def chainpulse_ui():

    st.markdown(
        '\n<style>\n\n/* ============================================================\n   CHAINPULSE AI — DESIGN SYSTEM\n   ============================================================ */\n\n:root {\n    --cp-bg: #f5f7fb;\n    --cp-surface: #ffffff;\n    --cp-surface-soft: #f8fafc;\n    --cp-border: #e5e7eb;\n    --cp-border-strong: #d7dce5;\n\n    --cp-text: #111827;\n    --cp-text-soft: #475569;\n    --cp-text-muted: #64748b;\n\n    --cp-sidebar: #0b1220;\n    --cp-sidebar-soft: #111a2d;\n    --cp-sidebar-border: rgba(255,255,255,.08);\n\n    --cp-primary: #2563eb;\n    --cp-primary-dark: #1d4ed8;\n    --cp-primary-soft: #eff6ff;\n\n    --cp-success: #059669;\n    --cp-success-soft: #ecfdf5;\n\n    --cp-warning: #d97706;\n    --cp-warning-soft: #fffbeb;\n\n    --cp-danger: #dc2626;\n    --cp-danger-soft: #fef2f2;\n\n    --cp-radius-sm: 8px;\n    --cp-radius-md: 12px;\n    --cp-radius-lg: 16px;\n    --cp-radius-xl: 20px;\n\n    --cp-shadow-sm:\n        0 1px 2px rgba(15, 23, 42, .04);\n\n    --cp-shadow-md:\n        0 8px 24px rgba(15, 23, 42, .06);\n\n    --cp-shadow-lg:\n        0 18px 45px rgba(15, 23, 42, .08);\n}\n\n\n/* ============================================================\n   GLOBAL APP\n   ============================================================ */\n\n.stApp {\n    background:\n        linear-gradient(\n            180deg,\n            #f8fafc 0%,\n            #f5f7fb 42%,\n            #f5f7fb 100%\n        );\n    color: var(--cp-text);\n}\n\n.main .block-container {\n    max-width: 1500px;\n    padding-top: 1.35rem;\n    padding-bottom: 4rem;\n    padding-left: 2rem;\n    padding-right: 2rem;\n}\n\n\n/* ============================================================\n   REMOVE STREAMLIT CHROME\n   ============================================================ */\n\n#MainMenu {\n    visibility: hidden;\n}\n\nfooter {\n    visibility: hidden;\n}\n\nheader[data-testid="stHeader"] {\n    background: transparent;\n}\n\n\n/* ============================================================\n   SIDEBAR — ENTERPRISE SAAS\n   ============================================================ */\n\nsection[data-testid="stSidebar"] {\n    background:\n        linear-gradient(\n            180deg,\n            #0b1220 0%,\n            #0d1526 55%,\n            #0a1020 100%\n        );\n\n    border-right: 1px solid var(--cp-sidebar-border);\n    box-shadow: 8px 0 30px rgba(2, 6, 23, .08);\n}\n\nsection[data-testid="stSidebar"] > div {\n    padding-top: 1rem;\n}\n\nsection[data-testid="stSidebar"] * {\n    color: #e5e7eb;\n}\n\n\n/* Sidebar headings */\n\nsection[data-testid="stSidebar"] h1,\nsection[data-testid="stSidebar"] h2,\nsection[data-testid="stSidebar"] h3 {\n    color: #ffffff !important;\n}\n\n\n/* Sidebar buttons */\n\nsection[data-testid="stSidebar"] .stButton > button {\n    width: 100%;\n    min-height: 42px;\n\n    border: 1px solid transparent;\n    border-radius: 10px;\n\n    background: transparent;\n    color: #cbd5e1;\n\n    font-size: .88rem;\n    font-weight: 600;\n\n    text-align: left;\n\n    padding: .65rem .85rem;\n\n    transition:\n        background .16s ease,\n        color .16s ease,\n        border-color .16s ease,\n        transform .16s ease;\n}\n\nsection[data-testid="stSidebar"] .stButton > button:hover {\n    background: rgba(255,255,255,.07);\n    color: #ffffff;\n    border-color: rgba(255,255,255,.08);\n    transform: translateX(1px);\n}\n\nsection[data-testid="stSidebar"] .stButton > button:focus {\n    box-shadow: 0 0 0 2px rgba(37,99,235,.35);\n}\n\n\n/* Sidebar separators */\n\nsection[data-testid="stSidebar"] hr {\n    border-color: rgba(255,255,255,.09);\n    margin: .75rem 0;\n}\n\n\n/* ============================================================\n   TYPOGRAPHY\n   ============================================================ */\n\nhtml,\nbody,\n.stApp,\nbutton,\ninput,\ntextarea,\nselect {\n    font-family:\n        Inter,\n        ui-sans-serif,\n        system-ui,\n        -apple-system,\n        BlinkMacSystemFont,\n        "Segoe UI",\n        sans-serif;\n}\n\nh1 {\n    color: #0f172a !important;\n    font-size: 2rem !important;\n    line-height: 1.15 !important;\n    font-weight: 800 !important;\n    letter-spacing: -.035em !important;\n}\n\nh2 {\n    color: #111827 !important;\n    font-size: 1.45rem !important;\n    font-weight: 750 !important;\n    letter-spacing: -.025em !important;\n}\n\nh3 {\n    color: #1e293b !important;\n    font-size: 1.08rem !important;\n    font-weight: 700 !important;\n}\n\np,\nlabel,\n.stCaption {\n    color: var(--cp-text-soft);\n}\n\n\n/* ============================================================\n   PAGE HEADER\n   ============================================================ */\n\n.cp-page-header {\n    position: relative;\n\n    background:\n        linear-gradient(\n            135deg,\n            #ffffff 0%,\n            #fbfdff 100%\n        );\n\n    border: 1px solid var(--cp-border);\n    border-radius: var(--cp-radius-lg);\n\n    padding: 1.4rem 1.55rem;\n\n    margin-bottom: 1.35rem;\n\n    box-shadow: var(--cp-shadow-sm);\n\n    overflow: hidden;\n}\n\n.cp-page-header::after {\n    content: "";\n\n    position: absolute;\n\n    right: -80px;\n    top: -100px;\n\n    width: 230px;\n    height: 230px;\n\n    background:\n        radial-gradient(\n            circle,\n            rgba(37,99,235,.08),\n            transparent 68%\n        );\n\n    pointer-events: none;\n}\n\n.cp-page-title {\n    position: relative;\n    z-index: 1;\n\n    color: #0f172a;\n\n    font-size: 1.7rem;\n    font-weight: 800;\n\n    letter-spacing: -.035em;\n\n    margin-bottom: .25rem;\n}\n\n.cp-page-caption {\n    position: relative;\n    z-index: 1;\n\n    color: var(--cp-text-muted);\n\n    font-size: .9rem;\n    line-height: 1.55;\n}\n\n\n/* ============================================================\n   BRAND\n   ============================================================ */\n\n.chainpulse-brand {\n    padding: .55rem .2rem 1.1rem .2rem;\n}\n\n.chainpulse-logo {\n    color: #ffffff;\n\n    font-size: 1.25rem;\n    font-weight: 800;\n\n    letter-spacing: -.03em;\n}\n\n.chainpulse-subtitle {\n    color: #94a3b8;\n\n    font-size: .73rem;\n    font-weight: 500;\n\n    margin-top: .18rem;\n}\n\n\n/* ============================================================\n   METRIC / KPI CARDS\n   ============================================================ */\n\ndiv[data-testid="stMetric"] {\n    background: var(--cp-surface);\n\n    border: 1px solid var(--cp-border);\n    border-radius: var(--cp-radius-lg);\n\n    padding: 1.05rem 1.1rem;\n\n    min-height: 112px;\n\n    box-shadow: var(--cp-shadow-sm);\n\n    transition:\n        transform .18s ease,\n        box-shadow .18s ease,\n        border-color .18s ease;\n}\n\ndiv[data-testid="stMetric"]:hover {\n    transform: translateY(-2px);\n\n    border-color: #d8dee9;\n\n    box-shadow: var(--cp-shadow-md);\n}\n\ndiv[data-testid="stMetricLabel"] {\n    color: var(--cp-text-muted) !important;\n\n    font-size: .78rem !important;\n    font-weight: 650 !important;\n\n    letter-spacing: .01em;\n}\n\ndiv[data-testid="stMetricValue"] {\n    color: #0f172a !important;\n\n    font-size: 1.65rem !important;\n    font-weight: 800 !important;\n\n    letter-spacing: -.03em;\n}\n\n\n/* ============================================================\n   GENERIC STREAMLIT CONTAINERS\n   ============================================================ */\n\ndiv[data-testid="stVerticalBlockBorderWrapper"] {\n    border-color: var(--cp-border) !important;\n    border-radius: var(--cp-radius-lg) !important;\n}\n\n\n/* ============================================================\n   BUTTONS\n   ============================================================ */\n\n.stButton > button,\n.stDownloadButton > button,\nbutton[kind="secondary"],\nbutton[kind="primary"] {\n    min-height: 40px;\n\n    border-radius: 10px;\n\n    font-weight: 650;\n\n    transition:\n        transform .15s ease,\n        box-shadow .15s ease,\n        background .15s ease;\n}\n\n.stButton > button:hover,\n.stDownloadButton > button:hover {\n    transform: translateY(-1px);\n}\n\n\n/* Primary */\n\nbutton[kind="primary"] {\n    background: var(--cp-primary) !important;\n    border-color: var(--cp-primary) !important;\n}\n\nbutton[kind="primary"]:hover {\n    background: var(--cp-primary-dark) !important;\n    border-color: var(--cp-primary-dark) !important;\n\n    box-shadow:\n        0 7px 18px rgba(37,99,235,.22);\n}\n\n\n/* Secondary */\n\nbutton[kind="secondary"] {\n    background: #ffffff !important;\n    border-color: var(--cp-border-strong) !important;\n    color: #334155 !important;\n}\n\n\n/* ============================================================\n   INPUTS\n   ============================================================ */\n\ninput,\ntextarea,\ndiv[data-baseweb="select"] > div {\n    border-radius: 10px !important;\n\n    border-color: #d9dee8 !important;\n\n    background: #ffffff !important;\n}\n\ninput:focus,\ntextarea:focus {\n    border-color: var(--cp-primary) !important;\n\n    box-shadow:\n        0 0 0 3px rgba(37,99,235,.10) !important;\n}\n\n\n/* ============================================================\n   SELECT BOX\n   ============================================================ */\n\ndiv[data-baseweb="select"] {\n    border-radius: 10px;\n}\n\ndiv[data-baseweb="select"] > div {\n    min-height: 40px;\n}\n\n\n/* ============================================================\n   DATAFRAMES / TABLES\n   ============================================================ */\n\ndiv[data-testid="stDataFrame"] {\n    border:\n\n        1px solid var(--cp-border);\n\n    border-radius: var(--cp-radius-lg);\n\n    overflow: hidden;\n\n    box-shadow: var(--cp-shadow-sm);\n\n    background: #ffffff;\n}\n\n\n/* ============================================================\n   TABS\n   ============================================================ */\n\nbutton[data-baseweb="tab"] {\n    color: #64748b !important;\n\n    font-size: .88rem !important;\n    font-weight: 650 !important;\n}\n\nbutton[data-baseweb="tab"][aria-selected="true"] {\n    color: var(--cp-primary) !important;\n}\n\n\n/* ============================================================\n   ALERTS\n   ============================================================ */\n\ndiv[data-testid="stAlert"] {\n    border-radius: var(--cp-radius-md);\n\n    border-width: 1px;\n\n    box-shadow: var(--cp-shadow-sm);\n}\n\n\n/* ============================================================\n   STATUS\n   ============================================================ */\n\n.cp-status {\n    display: inline-flex;\n\n    align-items: center;\n\n    gap: .45rem;\n\n    padding: .35rem .7rem;\n\n    border-radius: 999px;\n\n    background: var(--cp-success-soft);\n\n    color: var(--cp-success);\n\n    border: 1px solid #bbf7d0;\n\n    font-size: .75rem;\n\n    font-weight: 700;\n}\n\n.cp-status-dot {\n    width: 7px;\n    height: 7px;\n\n    border-radius: 50%;\n\n    background: #10b981;\n\n    box-shadow:\n        0 0 0 3px rgba(16,185,129,.12);\n}\n\n\n/* ============================================================\n   DIVIDERS\n   ============================================================ */\n\nhr {\n    border-color: var(--cp-border) !important;\n}\n\n\n/* ============================================================\n   EXPANDERS\n   ============================================================ */\n\ndetails[data-testid="stExpander"] {\n    background: #ffffff;\n\n    border: 1px solid var(--cp-border);\n\n    border-radius: var(--cp-radius-lg);\n\n    box-shadow: var(--cp-shadow-sm);\n\n    overflow: hidden;\n}\n\n\n/* ============================================================\n   FILE UPLOADERS\n   ============================================================ */\n\nsection[data-testid="stFileUploaderDropzone"] {\n    border: 1px dashed #cbd5e1;\n\n    border-radius: var(--cp-radius-lg);\n\n    background: #f8fafc;\n\n    transition:\n        border-color .15s ease,\n        background .15s ease;\n}\n\nsection[data-testid="stFileUploaderDropzone"]:hover {\n    border-color: #93c5fd;\n\n    background: #f8fbff;\n}\n\n\n/* ============================================================\n   PROGRESS / SPINNERS\n   ============================================================ */\n\ndiv[data-testid="stProgressBar"] > div > div {\n    border-radius: 999px;\n}\n\n\n/* ============================================================\n   DOWNLOADS\n   ============================================================ */\n\n.stDownloadButton > button {\n    background: #ffffff;\n\n    border: 1px solid var(--cp-border-strong);\n\n    color: #334155;\n}\n\n.stDownloadButton > button:hover {\n    border-color: #94a3b8;\n    background: #f8fafc;\n}\n\n\n/* ============================================================\n   RESPONSIVE\n   ============================================================ */\n\n@media (max-width: 900px) {\n\n    .main .block-container {\n        padding-left: 1rem;\n        padding-right: 1rem;\n    }\n\n    .cp-page-header {\n        padding: 1.15rem;\n    }\n\n    .cp-page-title {\n        font-size: 1.4rem;\n    }\n\n    div[data-testid="stMetric"] {\n        min-height: 100px;\n    }\n}\n\n\n/* ============================================================\n   ACCESSIBILITY / FOCUS\n   ============================================================ */\n\nbutton:focus-visible,\ninput:focus-visible,\ntextarea:focus-visible {\n    outline: 2px solid rgba(37,99,235,.45);\n    outline-offset: 2px;\n}\n\n\n/* ============================================================\n   SCROLLBAR\n   ============================================================ */\n\n::-webkit-scrollbar {\n    width: 8px;\n    height: 8px;\n}\n\n::-webkit-scrollbar-track {\n    background: #f1f5f9;\n}\n\n::-webkit-scrollbar-thumb {\n    background: #cbd5e1;\n    border-radius: 999px;\n}\n\n::-webkit-scrollbar-thumb:hover {\n    background: #94a3b8;\n}\n\n</style>\n',
        unsafe_allow_html=True,
    )


def chainpulse_brand():

    st.markdown(
        """
        <div class="chainpulse-brand">
            <div class="chainpulse-logo">
                ⚡ ChainPulse AI
            </div>
            <div class="chainpulse-subtitle">
                Supply-chain intelligence platform
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def chainpulse_page_header(
    title: str,
    subtitle: str = "",
):

    caption = (
        f'<div class="cp-page-caption">{subtitle}</div>'
        if subtitle
        else ""
    )

    st.markdown(
        f"""
        <div class="cp-page-header">
            <div class="cp-page-title">
                {title}
            </div>
            {caption}
        </div>
        """,
        unsafe_allow_html=True,
    )


def chainpulse_status(
    text: str = "System operational",
):

    st.markdown(
        f"""
        <div class="cp-status">
            <span class="cp-status-dot"></span>
            {text}
        </div>
        """,
        unsafe_allow_html=True,
    )


def chainpulse_footer():

    st.markdown(
        """
        <div class="cp-footer">
            ChainPulse AI · Supply-chain intelligence platform
        </div>
        """,
        unsafe_allow_html=True,
    )


# Apply UI globally.
chainpulse_ui()


# ============================================================
# DASHBOARD
# ============================================================

# ============================================================
# AUTHENTICATION GATE
# ============================================================

if not login_required():
    render_login()
    st.stop()

page = chainpulse_navigation()
if page == "Dashboard":

    page_header(
        "Supply Chain Dashboard",
        "A real-time view of your organization's operations.",
    )

    summary = api_request(
        "GET",
        "/dashboard/summary",
    )

    if summary:

        # EXECUTIVE KPI ROW
        c1, c2, c3, c4, c5 = st.columns(5)

        c1.metric(
            "Products",
            summary.get("product_count", 0),
        )

        c2.metric(
            "Demand",
            number(summary.get("total_demand_quantity", 0)),
        )

        c3.metric(
            "Revenue",
            number(summary.get("total_revenue", 0)),
        )

        c4.metric(
            "Inventory",
            number(summary.get("inventory_available", 0)),
        )

        overall_risk = str(
            summary.get("overall_risk_level", "low") or "low"
        )

        overall_score = float(
            summary.get("overall_risk_score", 0) or 0
        )

        c5.metric(
            "Risk",
            f"{overall_score:.1f}",
            delta=overall_risk.upper(),
            delta_color=(
                "inverse"
                if overall_risk.lower() in {"critical", "high"}
                else "normal"
            ),
        )

        st.markdown(
            "<div style='height:0.65rem'></div>",
            unsafe_allow_html=True,
        )

        st.subheader("Operational Health")

        h1, h2, h3, h4 = st.columns(4)

        supplier_reliability_raw = summary.get(
            "average_supplier_reliability"
        )

        below_reorder_raw = summary.get(
            "inventory_below_reorder"
        )

        stockouts_raw = summary.get(
            "inventory_stockouts"
        )

        risk_level_raw = summary.get("overall_risk_level")
        demand_risk_raw = summary.get("demand_risk_level")
        inventory_risk_raw = summary.get("inventory_risk_level")
        supplier_risk_raw = summary.get("supplier_risk_level")

        # Determine whether actual operational data exists.
        has_operational_data = any(
            value is not None
            for value in (
                supplier_reliability_raw,
                below_reorder_raw,
                stockouts_raw,
                risk_level_raw,
                demand_risk_raw,
                inventory_risk_raw,
                supplier_risk_raw,
            )
        )

        supplier_reliability = (
            float(supplier_reliability_raw)
            if supplier_reliability_raw is not None
            else None
        )

        below_reorder = (
            below_reorder_raw
            if below_reorder_raw is not None
            else None
        )

        stockouts = (
            stockouts_raw
            if stockouts_raw is not None
            else None
        )

        display_overall_risk = (
            str(overall_risk).upper()
            if has_operational_data and overall_risk
            else "N/A"
        )

        display_overall_score = (
            f"{overall_score:.1f}"
            if has_operational_data and overall_score is not None
            else "N/A"
        )

        with h1:
            st.markdown(
                f"""
                <div class="cp-dashboard-card">
                    <div class="cp-card-label">
                        Overall risk
                    </div>
                    <div class="cp-card-value">
                        {escape(display_overall_risk)}
                    </div>
                    <div class="cp-card-meta">
                        Score {display_overall_score} / 100
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )

        with h2:
            supplier_display = (
                f"{supplier_reliability:.1f}%"
                if supplier_reliability is not None
                else "N/A"
            )

            st.markdown(
                f"""
                <div class="cp-dashboard-card">
                    <div class="cp-card-label">
                        Supplier reliability
                    </div>
                    <div class="cp-card-value">
                        {supplier_display}
                    </div>
                    <div class="cp-card-meta">
                        {
                            "Average supplier performance"
                            if supplier_reliability is not None
                            else "No supplier data available"
                        }
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )

        with h3:
            below_display = (
                escape(str(below_reorder))
                if below_reorder is not None
                else "N/A"
            )

            st.markdown(
                f"""
                <div class="cp-dashboard-card">
                    <div class="cp-card-label">
                        Below reorder
                    </div>
                    <div class="cp-card-value">
                        {below_display}
                    </div>
                    <div class="cp-card-meta">
                        {
                            "Inventory positions requiring review"
                            if below_reorder is not None
                            else "No inventory data available"
                        }
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )

        with h4:
            stockout_display = (
                escape(str(stockouts))
                if stockouts is not None
                else "N/A"
            )

            st.markdown(
                f"""
                <div class="cp-dashboard-card">
                    <div class="cp-card-label">
                        Stockouts
                    </div>
                    <div class="cp-card-value">
                        {stockout_display}
                    </div>
                    <div class="cp-card-meta">
                        {
                            "Current stockout exposure"
                            if stockouts is not None
                            else "No inventory data available"
                        }
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )

        st.markdown(
            "<div style='height:0.75rem'></div>",
            unsafe_allow_html=True,
        )

        left, right = st.columns([1.35, 1])

        with left:
            st.subheader("Risk Overview")

            def dashboard_risk_score(level):
                if level is None:
                    return None

                level = str(level).lower().strip()

                return {
                    "critical": 100,
                    "high": 75,
                    "medium": 50,
                    "low": 25,
                }.get(level)

            risk_rows = []

            risk_values = {
                "Demand": demand_risk_raw,
                "Inventory": inventory_risk_raw,
                "Supplier": supplier_risk_raw,
            }

            for component, level in risk_values.items():
                score = dashboard_risk_score(level)

                if score is not None:
                    risk_rows.append(
                        {
                            "Component": component,
                            "Risk Score": score,
                        }
                    )

            if risk_rows:
                risk_data = pd.DataFrame(risk_rows)

                st.bar_chart(
                    risk_data.set_index("Component"),
                    height=280,
                )

                st.caption(
                    "Risk score is normalized to a 0–100 operational scale."
                )
            else:
                st.info(
                    "No risk data available yet. Add operational data to populate this view."
                )

        with right:
            st.subheader("Operational Status")

            st.metric(
                "Overall risk",
                overall_risk.upper(),
                delta=f"Score {overall_score:.1f} / 100",
                delta_color=(
                    "inverse"
                    if overall_risk.lower() in {"critical", "high"}
                    else "normal"
                ),
            )

            status_col1, status_col2 = st.columns(2)

            with status_col1:
                st.metric(
                    "Supplier reliability",
                    f"{supplier_reliability:.1f}%",
                )

                st.metric(
                    "Below reorder",
                    below_reorder,
                )

            with status_col2:
                st.metric(
                    "Stockouts",
                    stockouts,
                )

                st.caption(
                    "Current operational exposure"
                )

        st.markdown(
            "<div style='height:0.75rem'></div>",
            unsafe_allow_html=True,
        )

        alerts = summary.get(
            "alerts",
            [],
        )

        if not isinstance(alerts, list):
            alerts = [alerts] if alerts else []

        recommendations = summary.get(
            "recommendations",
            [],
        )

        if not isinstance(recommendations, list):
            recommendations = (
                [recommendations]
                if recommendations
                else []
            )

        alert_col, action_col = st.columns(2)

        with alert_col:
            st.subheader("Needs Attention")

            if alerts:
                for alert in alerts:
                    st.warning(
                        str(alert),
                        icon="⚠️",
                    )
            else:
                st.success(
                    "No major operational alerts detected.",
                    icon="✅",
                )

        with action_col:
            st.subheader("Recommended Actions")

            if recommendations:
                for recommendation in recommendations:
                    st.info(
                        str(recommendation),
                        icon="➡️",
                    )
            else:
                st.caption(
                    "No recommendations are currently available."
                )

    else:
        st.error(
            "Unable to load dashboard data."
        )

        st.caption(
            "Check that the ChainPulse API is running "
            "and that your session is authenticated."
        )
 elif page == "Products":
    page_header(
        "Products",
        "Manage products and inspect product-level intelligence.",
    )

    products = api_request(
        "GET",
        "/products",
    )

    current_user = st.session_state.get("user") or {}

    organization_id = (
        current_user.get("organization_id")
        or (
            current_user.get("organization", {}).get("id")
            if isinstance(current_user.get("organization"), dict)
            else None
        )
    )

    # ========================================================
    # PRODUCTS LIST
    # ========================================================

    if products:

        df = pd.DataFrame(products)

        search = st.text_input(
            "Search products",
            placeholder="Search by SKU or name...",
            key="products_search",
        )

        if search.strip():

            mask = (
                df["sku"]
                .astype(str)
                .str.contains(
                    search,
                    case=False,
                    na=False,
                )
                |
                df["name"]
                .astype(str)
                .str.contains(
                    search,
                    case=False,
                    na=False,
                )
            )

            df = df[mask]

        st.dataframe(
            df,
            use_container_width=True,
            hide_index=True,
        )

    # ========================================================
    # PRODUCT DETAILS
    # ========================================================

    if products:

        st.divider()

        st.subheader("Product Details")

        selected = st.selectbox(
            "Select product",
            products,
            format_func=lambda x:
                f"{x['sku']} — {x['name']}",
            key="product_details_select",
        )

        if selected:

            detail = api_request(
                "GET",
                f"/dashboard/product/{selected['id']}",
            )

            if detail:

                c1, c2, c3, c4 = st.columns(4)

                c1.metric(
                    "Demand",
                    number(
                        detail.get(
                            "total_demand_quantity"
                        )
                    ),
                )

                c2.metric(
                    "Revenue",
                    number(
                        detail.get(
                            "total_revenue"
                        )
                    ),
                )

                c3.metric(
                    "Inventory",
                    number(
                        detail.get(
                            "latest_inventory_on_hand"
                        )
                    ),
                )

                c4.metric(
                    "Forecast",
                    number(
                        detail.get(
                            "latest_forecast_demand"
                        )
                    ),
                )

    # ========================================================
    # CRUD
    # ========================================================

    st.divider()

    st.subheader("Product Management")

    tab_view, tab_create, tab_update, tab_delete = st.tabs(
        [
            "📋 Products",
            "➕ Create",
            "✏️ Edit",
            "🗑️ Delete",
        ]
    )

    # ========================================================
    # VIEW
    # ========================================================

    with tab_view:

        if products:

            view_df = pd.DataFrame(products)

            preferred_columns = [
                "sku",
                "name",
                "category",
                "unit_cost",
                "selling_price",
                "lead_time_days",
                "active",
                "supplier_id",
            ]

            available_columns = [
                column
                for column in preferred_columns
                if column in view_df.columns
            ]

            if available_columns:

                st.dataframe(
                    view_df[available_columns],
                    use_container_width=True,
                    hide_index=True,
                )

        else:

            st.info(
                "No products found."
            )

    # ========================================================
    # CREATE
    # ========================================================

    with tab_create:

        st.caption(
            "Create a new product in your organization."
        )

        create_col1, create_col2 = st.columns(2)

        with create_col1:

            create_sku = st.text_input(
                "SKU",
                key="create_product_sku",
            )

            create_name = st.text_input(
                "Product name",
                key="create_product_name",
            )

            create_category = st.text_input(
                "Category",
                key="create_product_category",
            )

            create_supplier_id = st.text_input(
                "Supplier ID (optional)",
                key="create_product_supplier",
            )

        with create_col2:

            create_unit_cost = st.number_input(
                "Unit cost",
                min_value=0.0,
                value=0.0,
                step=0.01,
                key="create_product_unit_cost",
            )

            create_selling_price = st.number_input(
                "Selling price",
                min_value=0.0,
                value=0.0,
                step=0.01,
                key="create_product_selling_price",
            )

            create_lead_time = st.number_input(
                "Lead time (days)",
                min_value=0,
                value=1,
                step=1,
                key="create_product_lead_time",
            )

            create_active = st.checkbox(
                "Active",
                value=True,
                key="create_product_active",
            )

        if st.button(
            "Create Product",
            type="primary",
            key="create_product_button",
        ):

            if not organization_id:

                st.error(
                    "Organization information is missing. "
                    "Please log out and log in again."
                )

            elif not create_sku.strip():

                st.error(
                    "SKU is required."
                )

            elif not create_name.strip():

                st.error(
                    "Product name is required."
                )

            else:

                payload = {
                    "organization_id": organization_id,
                    "sku": create_sku.strip(),
                    "name": create_name.strip(),
                    "category": (
                        create_category.strip()
                        if create_category.strip()
                        else None
                    ),
                    "unit_cost": float(
                        create_unit_cost
                    ),
                    "selling_price": float(
                        create_selling_price
                    ),
                    "lead_time_days": int(
                        create_lead_time
                    ),
                    "active": bool(
                        create_active
                    ),
                }

                if create_supplier_id.strip():

                    payload["supplier_id"] = (
                        create_supplier_id.strip()
                    )

                result = api_request(
                    "POST",
                    "/products",
                    json=payload,
                )

                if result:

                    st.success(
                        f"Product '{create_sku.strip()}' created successfully."
                    )

                    st.rerun()

    # ========================================================
    # UPDATE
    # ========================================================

    with tab_update:

        if not products:

            st.info(
                "No products available to edit."
            )

        else:

            edit_product = st.selectbox(
                "Product to edit",
                products,
                format_func=lambda x:
                    f"{x['sku']} — {x['name']}",
                key="edit_product_select",
            )

            edit_col1, edit_col2 = st.columns(2)

            with edit_col1:

                edit_sku = st.text_input(
                    "SKU",
                    value=str(
                        edit_product.get("sku", "")
                    ),
                    key="edit_product_sku",
                )

                edit_name = st.text_input(
                    "Product name",
                    value=str(
                        edit_product.get("name", "")
                    ),
                    key="edit_product_name",
                )

                edit_category = st.text_input(
                    "Category",
                    value=str(
                        edit_product.get("category") or ""
                    ),
                    key="edit_product_category",
                )

            with edit_col2:

                edit_unit_cost = st.number_input(
                    "Unit cost",
                    min_value=0.0,
                    value=float(
                        edit_product.get(
                            "unit_cost",
                            0,
                        )
                        or 0
                    ),
                    step=0.01,
                    key="edit_product_unit_cost",
                )

                edit_selling_price = st.number_input(
                    "Selling price",
                    min_value=0.0,
                    value=float(
                        edit_product.get(
                            "selling_price",
                            0,
                        )
                        or 0
                    ),
                    step=0.01,
                    key="edit_product_selling_price",
                )

                edit_lead_time = st.number_input(
                    "Lead time (days)",
                    min_value=0,
                    value=int(
                        edit_product.get(
                            "lead_time_days",
                            0,
                        )
                        or 0
                    ),
                    step=1,
                    key="edit_product_lead_time",
                )

                edit_active = st.checkbox(
                    "Active",
                    value=bool(
                        edit_product.get(
                            "active",
                            True,
                        )
                    ),
                    key="edit_product_active",
                )

            if st.button(
                "Save Changes",
                type="primary",
                key="edit_product_button",
            ):

                if not organization_id:

                    st.error(
                        "Organization information is missing. "
                        "Please log out and log in again."
                    )

                elif not edit_sku.strip():

                    st.error(
                        "SKU is required."
                    )

                elif not edit_name.strip():

                    st.error(
                        "Product name is required."
                    )

                else:

                    payload = {
                        "organization_id": organization_id,
                        "sku": edit_sku.strip(),
                        "name": edit_name.strip(),
                        "category": (
                            edit_category.strip()
                            if edit_category.strip()
                            else None
                        ),
                        "unit_cost": float(
                            edit_unit_cost
                        ),
                        "selling_price": float(
                            edit_selling_price
                        ),
                        "lead_time_days": int(
                            edit_lead_time
                        ),
                        "active": bool(
                            edit_active
                        ),
                    }

                    result = api_request(
                        "PUT",
                        f"/products/{edit_product['id']}",
                        json=payload,
                    )

                    if result:

                        st.success(
                            "Product updated successfully."
                        )

                        st.rerun()

    # ========================================================
    # DELETE
    # ========================================================

    with tab_delete:

        if not products:

            st.info(
                "No products available to delete."
            )

        else:

            delete_product = st.selectbox(
                "Product to delete",
                products,
                format_func=lambda x:
                    f"{x['sku']} — {x['name']}",
                key="delete_product_select",
            )

            st.warning(
                "Deleting a product will deactivate it. "
                "This uses the backend soft-delete behavior."
            )

            confirm_delete = st.checkbox(
                "I understand that this product will be deactivated.",
                key="confirm_product_delete",
            )

            if st.button(
                "Delete Product",
                type="primary",
                disabled=not confirm_delete,
                key="delete_product_button",
            ):

                result = api_request(
                    "DELETE",
                    f"/products/{delete_product['id']}",
                )

                if result:

                    st.success(
                        "Product deleted successfully."
                    )

                    st.rerun()
 elif page == "Demand":
    page_header(
        "Demand Analytics",
        "Review demand history for each product.",
    )

    products = api_request(
        "GET",
        "/products",
    )

    if products:

        product = st.selectbox(
            "Product",
            products,
            format_func=lambda x:
                f"{x['sku']} — {x['name']}",
        )

        demand = api_request(
            "GET",
            f"/demand/{product['id']}",
        )

        if demand:

            df = pd.DataFrame(demand)

            if "date" in df.columns:
                df["date"] = pd.to_datetime(
                    df["date"]
                )

            st.line_chart(
                df.set_index("date")[
                    ["quantity"]
                ]
                if "date" in df.columns
                and "quantity" in df.columns
                else df
            )

            st.dataframe(
                df,
                use_container_width=True,
                hide_index=True,
            )

    st.divider()

    st.subheader(
        "Add Demand Record"
    )

    if products:

        p = st.selectbox(
            "Product",
            products,
            key="demand_product",
            format_func=lambda x:
                f"{x['sku']} — {x['name']}",
        )

        c1, c2, c3 = st.columns(3)

        demand_date = c1.date_input(
            "Date"
        )

        quantity = c2.number_input(
            "Quantity",
            min_value=0.0,
            value=100.0,
        )

        revenue = c3.number_input(
            "Revenue",
            min_value=0.0,
            value=20000.0,
        )

        if st.button(
            "Add Demand",
            type="primary",
        ):

            result = api_request(
                "POST",
                "/demand",
                json={
                    "product_id":
                        p["id"],
                    "date":
                        str(demand_date),
                    "quantity":
                        quantity,
                    "revenue":
                        revenue,
                },
            )

            if result:
                st.success(
                    "Demand record added."
                )


# ============================================================
# FORECASTING
# ============================================================
 elif page == "Forecasting":
    page_header(
        "Forecasting",
        "Generate product demand forecasts using ChainPulse models.",
    )

    products = api_request(
        "GET",
        "/products",
    )

    if products:

        product = st.selectbox(
            "Product",
            products,
            format_func=lambda x:
                f"{x['sku']} — {x['name']}",
        )

        c1, c2 = st.columns(2)

        periods = c1.number_input(
            "Forecast periods",
            min_value=1,
            max_value=100,
            value=7,
        )

        window = c2.number_input(
            "Moving average window",
            min_value=1,
            max_value=100,
            value=3,
        )

        if st.button(
            "Generate Forecast",
            type="primary",
        ):

            result = api_request(
                "POST",
                f"/forecasting/product/{product['id']}",
                json={
                    "periods": periods,
                    "window": window,
                },
            )

            if result:

                c1, c2 = st.columns(2)

                c1.metric(
                    "Data Points",
                    result.get(
                        "data_points",
                        0,
                    ),
                )

                c2.metric(
                    "Forecast Periods",
                    periods,
                )

                st.subheader(
                    "Forecast Comparison"
                )

                ma = result.get(
                    "moving_average",
                    [],
                )

                es = result.get(
                    "exponential_smoothing",
                    [],
                )

                length = max(
                    len(ma),
                    len(es),
                )

                forecast_df = pd.DataFrame(
                    {
                        "Moving Average":
                            (
                                ma
                                + [None]
                                * (
                                    length
                                    - len(ma)
                                )
                            ),
                        "Exponential Smoothing":
                            (
                                es
                                + [None]
                                * (
                                    length
                                    - len(es)
                                )
                            ),
                    }
                )

                st.line_chart(
                    forecast_df
                )


# ============================================================
# INVENTORY
# ============================================================
 elif page == "Inventory":
    page_header(
        "Inventory Intelligence",
        "Analyze stock coverage, reorder levels, and inventory risk.",
    )

    products = api_request(
        "GET",
        "/products",
    )

    if products:

        product = st.selectbox(
            "Product",
            products,
            format_func=lambda x:
                f"{x['sku']} — {x['name']}",
        )

        inventory = api_request(
            "GET",
            f"/inventory/{product['id']}",
        )

        if inventory:

            df = pd.DataFrame(
                inventory
            )

            st.dataframe(
                df,
                use_container_width=True,
                hide_index=True,
            )

    st.divider()

    st.subheader(
        "Inventory Analysis"
    )

    c1, c2, c3 = st.columns(3)

    average_daily_demand = (
        c1.number_input(
            "Average daily demand",
            min_value=0.0,
            value=100.0,
        )
    )

    demand_std = c2.number_input(
        "Demand standard deviation",
        min_value=0.0,
        value=20.0,
    )

    lead_time_days = c3.number_input(
        "Lead time days",
        min_value=0.0,
        value=5.0,
    )

    c1, c2, c3 = st.columns(3)

    current_inventory = c1.number_input(
        "Current inventory",
        min_value=0.0,
        value=600.0,
    )

    annual_demand = c2.number_input(
        "Annual demand",
        min_value=0.0,
        value=36500.0,
    )

    ordering_cost = c3.number_input(
        "Ordering cost",
        min_value=0.0,
        value=100.0,
    )

    holding_cost = st.number_input(
        "Holding cost",
        min_value=0.01,
        value=5.0,
    )

    if st.button(
        "Analyze Inventory",
        type="primary",
    ):

        result = api_request(
            "POST",
            "/inventory/analyze",
            json={
                "average_daily_demand":
                    average_daily_demand,
                "demand_std":
                    demand_std,
                "lead_time_days":
                    lead_time_days,
                "current_inventory":
                    current_inventory,
                "annual_demand":
                    annual_demand,
                "ordering_cost":
                    ordering_cost,
                "holding_cost":
                    holding_cost,
                "service_level_z":
                    1.65,
            },
        )

        if result:

            c1, c2, c3, c4 = st.columns(4)

            c1.metric(
                "Safety Stock",
                number(
                    result["safety_stock"]
                ),
            )

            c2.metric(
                "Reorder Point",
                number(
                    result["reorder_point"]
                ),
            )

            c3.metric(
                "EOQ",
                number(
                    result[
                        "economic_order_quantity"
                    ]
                ),
            )

            c4.metric(
                "Days of Inventory",
                number(
                    result[
                        "days_of_inventory"
                    ]
                ),
            )

            st.info(
                "Stockout Risk: "
                + risk_badge(
                    result["stockout_risk"]
                )
            )

            st.info(
                "Overstock Risk: "
                + risk_badge(
                    result["overstock_risk"]
                )
            )


# ============================================================
# SUPPLIERS
# ============================================================
 elif page == "Suppliers":
    page_header(
        "Supplier Intelligence",
        "Monitor supplier performance and risk.",
    )

    suppliers = api_request(
        "GET",
        "/suppliers",
    )

    if suppliers:

        st.dataframe(
            pd.DataFrame(
                suppliers
            ),
            use_container_width=True,
            hide_index=True,
        )

    st.divider()

    st.subheader(
        "Evaluate Supplier"
    )

    c1, c2, c3 = st.columns(3)

    on_time_rate = c1.number_input(
        "On-time rate",
        min_value=0.0,
        max_value=1.0,
        value=0.95,
    )

    defect_rate = c2.number_input(
        "Defect rate",
        min_value=0.0,
        max_value=1.0,
        value=0.02,
    )

    actual_lead_time = c3.number_input(
        "Actual lead time",
        min_value=0.0,
        value=7.0,
    )

    c1, c2, c3 = st.columns(3)

    expected_lead_time = c1.number_input(
        "Expected lead time",
        min_value=0.01,
        value=7.0,
    )

    supplier_cost = c2.number_input(
        "Supplier cost",
        min_value=0.0,
        value=95.0,
    )

    benchmark_cost = c3.number_input(
        "Benchmark cost",
        min_value=0.01,
        value=100.0,
    )

    if st.button(
        "Evaluate Supplier",
        type="primary",
    ):

        result = api_request(
            "POST",
            "/suppliers/evaluate",
            json={
                "on_time_rate":
                    on_time_rate,
                "defect_rate":
                    defect_rate,
                "actual_lead_time_days":
                    actual_lead_time,
                "expected_lead_time_days":
                    expected_lead_time,
                "supplier_cost":
                    supplier_cost,
                "benchmark_cost":
                    benchmark_cost,
            },
        )

        if result:

            cols = st.columns(5)

            cols[0].metric(
                "Reliability",
                number(
                    result[
                        "reliability_score"
                    ]
                ),
            )

            cols[1].metric(
                "Quality",
                number(
                    result["quality_score"]
                ),
            )

            cols[2].metric(
                "Lead Time",
                number(
                    result["lead_time_score"]
                ),
            )

            cols[3].metric(
                "Cost",
                number(
                    result["cost_score"]
                ),
            )

            cols[4].metric(
                "Overall",
                number(
                    result["overall_score"]
                ),
            )

            st.info(
                "Risk: "
                + risk_badge(
                    result["risk_level"]
                )
            )

            st.success(
                result["recommendation"]
            )


# ============================================================
# BULLWHIP
# ============================================================
 elif page == "Bullwhip":
    page_header(
        "Bullwhip Effect",
        "Measure variability amplification across the supply chain.",
    )

    labels = [
        "Customer demand",
        "Retailer orders",
        "Distributor orders",
        "Manufacturer orders",
    ]

    values = []

    for label in labels:
        values.append(
            st.text_input(
                label,
                value="",
                placeholder="Enter real demand/order history",
            )
        )
    if st.button(
        "Analyze Bullwhip",
        type="primary",
    ):

        try:
            parsed = [
                [
                    float(
                        x.strip()
                    )
                    for x in value.split(",")
                ]
                for value in values
            ]

            payload = {
                "customer_demand":
                    parsed[0],
                "retailer_orders":
                    parsed[1],
                "distributor_orders":
                    parsed[2],
                "manufacturer_orders":
                    parsed[3],
            }

        except ValueError:

            st.error(
                "Enter comma-separated numeric values."
            )
            st.stop()

        result = api_request(
            "POST",
            "/analytics/bullwhip",
            json=payload,
        )

        if result:

            c1, c2, c3 = st.columns(3)

            c1.metric(
                "Overall Ratio",
                number(
                    result[
                        "overall_bullwhip_ratio"
                    ]
                ),
            )

            c2.metric(
                "Severity",
                result[
                    "severity"
                ].upper(),
            )

            c3.metric(
                "Interpretation",
                result[
                    "interpretation"
                ],
            )

            st.subheader(
                "Variance"
            )

            variance = pd.DataFrame(
                {
                    "Customer": [
                        result[
                            "customer_variance"
                        ]
                    ],
                    "Retailer": [
                        result[
                            "retailer_variance"
                        ]
                    ],
                    "Distributor": [
                        result[
                            "distributor_variance"
                        ]
                    ],
                    "Manufacturer": [
                        result[
                            "manufacturer_variance"
                        ]
                    ],
                }
            ).T

            variance.columns = [
                "Variance"
            ]

            st.bar_chart(
                variance
            )

            st.subheader(
                "Recommendations"
            )

            for item in result.get(
                "recommendations",
                [],
            ):
                st.warning(item)


# ============================================================
# RISK
# ============================================================
 elif page == "Risk":
    page_header(
        "Risk Intelligence",
        "Aggregate demand, inventory, supplier, and bullwhip risk.",
    )

    c1, c2, c3, c4 = st.columns(4)

    risks = {}

    risks["demand"] = c1.selectbox(
        "Demand",
        [
            "low",
            "medium",
            "high",
            "critical",
        ],
        index=1,
    )

    risks["inventory"] = c2.selectbox(
        "Inventory",
        [
            "low",
            "medium",
            "high",
            "critical",
        ],
        index=1,
    )

    risks["supplier"] = c3.selectbox(
        "Supplier",
        [
            "low",
            "medium",
            "high",
            "critical",
        ],
        index=1,
    )

    risks["bullwhip"] = c4.selectbox(
        "Bullwhip",
        [
            "low",
            "medium",
            "high",
            "critical",
        ],
        index=3,
    )

    if st.button(
        "Analyze Overall Risk",
        type="primary",
    ):

        result = api_request(
            "POST",
            "/risk/analyze",
            json={
                "components":
                    risks
            },
        )

        if result:

            c1, c2 = st.columns(2)

            c1.metric(
                "Risk Score",
                number(
                    result[
                        "overall_score"
                    ]
                ),
            )

            c2.metric(
                "Risk Level",
                result[
                    "risk_level"
                ].upper(),
            )

            drivers = result.get(
                "primary_drivers",
                [],
            )

            if drivers:

                st.subheader(
                    "Primary Drivers"
                )

                for driver in drivers:
                    st.warning(
                        driver.upper()
                    )

            details = pd.DataFrame(
                result[
                    "component_details"
                ]
            )

            st.dataframe(
                details,
                use_container_width=True,
                hide_index=True,
            )

            st.bar_chart(
                details.set_index(
                    "component"
                )[["score"]]
            )


# ============================================================
# DECISIONS
# ============================================================
 elif page == "Decisions":
    page_header(
        "Decision Engine",
        "Turn operational risk into recommended actions.",
    )

    c1, c2 = st.columns(2)

    current_inventory = c1.number_input(
        "Current inventory",
        min_value=0.0,
        value=600.0,
    )

    reorder_point = c2.number_input(
        "Reorder point",
        min_value=0.0,
        value=950.0,
    )

    c1, c2, c3 = st.columns(3)

    stockout_risk = c1.selectbox(
        "Stockout risk",
        [
            "low",
            "medium",
            "high",
            "critical",
        ],
        index=1,
    )

    overstock_risk = c2.selectbox(
        "Overstock risk",
        [
            "low",
            "medium",
            "high",
            "critical",
        ],
        index=0,
    )

    supplier_risk = c3.selectbox(
        "Supplier risk",
        [
            "low",
            "medium",
            "high",
            "critical",
        ],
        index=0,
    )

    if st.button(
        "Evaluate Decision",
        type="primary",
    ):

        result = api_request(
            "POST",
            "/decisions/evaluate",
            json={
                "current_inventory":
                    current_inventory,
                "reorder_point":
                    reorder_point,
                "stockout_risk":
                    stockout_risk,
                "overstock_risk":
                    overstock_risk,
                "supplier_risk_level":
                    supplier_risk,
            },
        )

        if result:

            c1, c2, c3 = st.columns(3)

            c1.metric(
                "Risk Score",
                number(
                    result[
                        "risk_score"
                    ]
                ),
            )

            c2.metric(
                "Risk Level",
                result[
                    "risk_level"
                ].upper(),
            )

            c3.metric(
                "Actions",
                len(
                    result.get(
                        "decisions",
                        [],
                    )
                ),
            )

            for decision in result.get(
                "decisions",
                [],
            ):

                with st.container(
                    border=True
                ):

                    st.subheader(
                        decision.get(
                            "action",
                            "UNKNOWN",
                        )
                    )

                    st.write(
                        decision.get(
                            "reason",
                            "",
                        )
                    )

                    c1, c2 = st.columns(2)

                    c1.write(
                        "Priority: "
                        f"**{decision.get('priority', 'unknown')}**"
                    )

                    c2.write(
                        "Confidence: "
                        f"**{float(decision.get('confidence', 0)):.1f}%**"
                    )

                    st.caption(
                        "Category: "
                        + str(
                            decision.get(
                                "category",
                                "general",
                            )
                        )
                    )


# ============================================================
# SIMULATIONS
# ============================================================
 elif page == "Simulations":
    page_header(
        "Scenario Simulation",
        "Test demand, lead-time, and inventory changes before acting.",
    )

    name = st.text_input(
        "Scenario name",
        value="UI Scenario",
    )

    c1, c2, c3 = st.columns(3)

    demand_change = c1.number_input(
        "Demand change %",
        min_value=-100.0,
        value=20.0,
    )

    lead_change = c2.number_input(
        "Lead time change %",
        min_value=-100.0,
        value=10.0,
    )

    inventory_change = c3.number_input(
        "Inventory change %",
        min_value=-100.0,
        value=-10.0,
    )

    c1, c2, c3 = st.columns(3)

    average_daily_demand = c1.number_input(
        "Average daily demand",
        min_value=0.0,
        value=125.0,
    )

    demand_std = c2.number_input(
        "Demand standard deviation",
        min_value=0.0,
        value=18.0,
    )

    lead_time_days = c3.number_input(
        "Lead time days",
        min_value=0.0,
        value=7.0,
    )

    c1, c2, c3 = st.columns(3)

    current_inventory = c1.number_input(
        "Current inventory",
        min_value=0.0,
        value=600.0,
    )

    annual_demand = c2.number_input(
        "Annual demand",
        min_value=0.0,
        value=45625.0,
    )

    ordering_cost = c3.number_input(
        "Ordering cost",
        min_value=0.0,
        value=100.0,
    )

    holding_cost = st.number_input(
        "Holding cost",
        min_value=0.01,
        value=5.0,
    )

    if st.button(
        "Run Simulation",
        type="primary",
    ):

        result = api_request(
            "POST",
            "/simulations/run",
            json={
                "scenario": {
                    "name": name,
                    "demand_change_pct":
                        demand_change,
                    "lead_time_change_pct":
                        lead_change,
                    "inventory_change_pct":
                        inventory_change,
                },
                "average_daily_demand":
                    average_daily_demand,
                "demand_std":
                    demand_std,
                "lead_time_days":
                    lead_time_days,
                "current_inventory":
                    current_inventory,
                "annual_demand":
                    annual_demand,
                "ordering_cost":
                    ordering_cost,
                "holding_cost":
                    holding_cost,
                "service_level_z":
                    1.65,
            },
        )

        if result:

            metrics = [
                "safety_stock",
                "reorder_point",
                "economic_order_quantity",
                "days_of_inventory",
            ]

            table = pd.DataFrame(
                {
                    "Metric": metrics,
                    "Baseline": [
                        result[
                            "baseline"
                        ][x]
                        for x in metrics
                    ],
                    "Scenario": [
                        result[
                            "simulated"
                        ][x]
                        for x in metrics
                    ],
                    "Change %": [
                        result[
                            "impact"
                        ][x]["change_pct"]
                        for x in metrics
                    ],
                }
            )

            st.dataframe(
                table,
                use_container_width=True,
                hide_index=True,
            )

            st.bar_chart(
                table.set_index(
                    "Metric"
                )[[
                    "Baseline",
                    "Scenario",
                ]]
            )


# ============================================================
# AI EXPLAIN
# ============================================================
 elif page == "AI Explain":
    page_header(
        "AI Explainability",
        "Generate a human-readable explanation from a real decision.",
    )

    c1, c2 = st.columns(2)

    current_inventory = c1.number_input(
        "Current inventory",
        min_value=0.0,
        value=600.0,
    )

    reorder_point = c2.number_input(
        "Reorder point",
        min_value=0.0,
        value=950.0,
    )

    c1, c2, c3 = st.columns(3)

    stockout_risk = c1.selectbox(
        "Stockout risk",
        [
            "low",
            "medium",
            "high",
            "critical",
        ],
        index=1,
    )

    overstock_risk = c2.selectbox(
        "Overstock risk",
        [
            "low",
            "medium",
            "high",
            "critical",
        ],
        index=0,
    )

    supplier_risk = c3.selectbox(
        "Supplier risk",
        [
            "low",
            "medium",
            "high",
            "critical",
        ],
        index=0,
    )

    if st.button(
        "Generate Decision",
        type="primary",
    ):

        result = api_request(
            "POST",
            "/decisions/evaluate",
            json={
                "current_inventory":
                    current_inventory,
                "reorder_point":
                    reorder_point,
                "stockout_risk":
                    stockout_risk,
                "overstock_risk":
                    overstock_risk,
                "supplier_risk_level":
                    supplier_risk,
            },
        )

        if result:
            st.session_state.ai_decision = (
                result
            )

    decision = st.session_state.ai_decision

    if decision:

        st.divider()

        c1, c2, c3 = st.columns(3)

        c1.metric(
            "Risk",
            number(
                decision.get(
                    "risk_score",
                    0,
                )
            ),
        )

        c2.metric(
            "Risk Level",
            decision.get(
                "risk_level",
                "unknown",
            ).upper(),
        )

        c3.metric(
            "Actions",
            len(
                decision.get(
                    "decisions",
                    [],
                )
            ),
        )

        for item in decision.get(
            "decisions",
            [],
        ):

            with st.container(
                border=True
            ):

                st.subheader(
                    item.get(
                        "action",
                        "UNKNOWN",
                    )
                )

                st.write(
                    item.get(
                        "reason",
                        "",
                    )
                )

        st.divider()

        if st.button(
            "Explain This Decision",
            type="primary",
        ):

            result = api_request(
                "POST",
                "/ai/explain",
                json={
                    "decision":
                        decision
                },
            )

            if result:

                st.subheader(
                    result.get(
                        "title",
                        "ChainPulse Insight",
                    )
                )

                st.write(
                    result.get(
                        "summary",
                        "",
                    )
                )

                st.success(
                    result.get(
                        "recommendation",
                        "",
                    )
                )

                c1, c2 = st.columns(2)

                c1.metric(
                    "Confidence",
                    f'{float(result.get("confidence", 0)):.1f}%',
                )

                c2.metric(
                    "Category",
                    result.get(
                        "category",
                        "general",
                    ),
                )


# ============================================================
# CONNECT DATA
# ============================================================
 elif page == "Connect Data":
    page_header(
        "Connect Data",
        "Bring CSV, Excel, JSON, SQLite, SQL, or REST data into ChainPulse.",
    )

    source = st.selectbox(
        "Source type",
        [
            "CSV",
            "Excel",
            "JSON",
            "SQLite",
            "SQL",
            "REST API",
        ],
    )

    st.subheader(
        "Connection"
    )

    connection_name = st.text_input(
        "Connection name",
        value=f"{source} Connection",
    )

    if source in {
        "CSV",
        "Excel",
        "JSON",
    }:

        extensions = {
            "CSV": ["csv"],
            "Excel": [
                "xlsx",
                "xls",
            ],
            "JSON": ["json"],
        }

        uploaded = st.file_uploader(
            "Upload file",
            type=extensions[source],
        )

        if uploaded:

            if st.button(
                "Save & Connect",
                type="primary",
            ):

                safe_name = (
                    Path(
                        uploaded.name
                    ).name
                )

                destination = (
                    STORAGE_DIR
                    / safe_name
                )

                destination.write_bytes(
                    uploaded.getvalue()
                )

                connector_type = {
                    "CSV": "csv",
                    "Excel": "xlsx",
                    "JSON": "json",
                }[source]

                result = api_request(
                    "POST",
                    "/data-connections",
                    json={
                        "name":
                            connection_name,
                        "connector_type":
                            connector_type,
                        "config": {
                            "path": str(
                                destination
                            ),
                        },
                        "secrets": {},
                    },
                )

                if result:
                    st.session_state.active_connection_id = (
                        result["id"]
                    )
                    st.success(
                        "Connection created."
                    )

    elif source == "SQLite":

        path_value = st.text_input(
            "SQLite database path",
            placeholder="storage/database.db",
        )

        table = st.text_input(
            "Table",
            placeholder="sales",
        )

        if st.button(
            "Connect SQLite",
            type="primary",
        ):

            result = api_request(
                "POST",
                "/data-connections",
                json={
                    "name":
                        connection_name,
                    "connector_type":
                        "sqlite",
                    "config": {
                        "path":
                            path_value,
                        "table":
                            table,
                    },
                    "secrets": {},
                },
            )

            if result:
                st.session_state.active_connection_id = (
                    result["id"]
                )
                st.success(
                    "SQLite connection created."
                )

    elif source == "SQL":

        sql_url = st.text_input(
            "SQLAlchemy connection URL",
            type="password",
            placeholder="sqlite:///storage/example.db",
        )

        table = st.text_input(
            "Table",
            placeholder="sales",
        )

        if st.button(
            "Connect SQL",
            type="primary",
        ):

            result = api_request(
                "POST",
                "/data-connections",
                json={
                    "name":
                        connection_name,
                    "connector_type":
                        "sql",
                    "config": {
                        "url":
                            sql_url,
                        "table":
                            table,
                    },
                    "secrets": {},
                },
            )

            if result:
                st.session_state.active_connection_id = (
                    result["id"]
                )
                st.success(
                    "SQL connection created."
                )

    elif source == "REST API":

        url = st.text_input(
            "API URL",
            placeholder="https://api.example.com/data",
        )

        method = st.selectbox(
            "Method",
            ["GET", "POST"],
        )

        api_key = st.text_input(
            "API key",
            type="password",
        )

        if st.button(
            "Connect REST API",
            type="primary",
        ):

            result = api_request(
                "POST",
                "/data-connections",
                json={
                    "name":
                        connection_name,
                    "connector_type":
                        "rest",
                    "config": {
                        "url":
                            url,
                        "method":
                            method,
                    },
                    "secrets": (
                        {
                            "api_key":
                                api_key
                        }
                        if api_key
                        else {}
                    ),
                },
            )

            if result:
                st.session_state.active_connection_id = (
                    result["id"]
                )
                st.success(
                    "REST API connection created."
                )

    connections = api_request(
        "GET",
        "/data-connections",
    )

    if connections:

        st.divider()

        st.subheader(
            "Saved Connections"
        )

        st.dataframe(
            pd.DataFrame(
                connections
            ),
            use_container_width=True,
            hide_index=True,
        )

    connection_id = (
        st.session_state.active_connection_id
    )

    if connection_id:

        st.divider()

        st.subheader(
            "Data Preview"
        )

        preview = api_request(
            "POST",
            "/ingestion/preview",
            json={
                "connection_id":
                    connection_id,
                "limit":
                    100,
            },
        )

        if preview:

            st.write(
                f"Rows: "
                f"**{preview.get('total_rows', 0)}**"
            )

            rows = preview.get(
                "rows",
                [],
            )

            if rows:
                st.dataframe(
                    pd.DataFrame(rows),
                    use_container_width=True,
                    hide_index=True,
                )

            st.subheader(
                "Automatic Mapping"
            )

            target = st.selectbox(
                "Import target",
                [
                    "demand",
                    "products",
                    "inventory",
                    "bullwhip",
                ],
            )

            if st.button(
                "Detect Columns",
                type="primary",
            ):

                mapping = api_request(
                    "POST",
                    "/ingestion/auto-map",
                    json={
                        "connection_id":
                            connection_id,
                        "target":
                            target,
                        "limit":
                            100,
                    },
                )

                if mapping:
                    st.session_state.mapping_result = (
                        mapping
                    )

        mapping_result = (
            st.session_state.mapping_result
        )

        if mapping_result:

            st.subheader(
                "Review Mapping"
            )

            suggestions = (
                mapping_result.get(
                    "suggestions",
                    {},
                )
            )

            edited_mapping = {}

            for source_col, info in suggestions.items():

                edited_mapping[
                    source_col
                ] = st.text_input(
                    source_col,
                    value=info.get(
                        "target",
                        "",
                    ),
                    key=f"map_{source_col}",
                )

            required = {
                "demand": [
                    "demand_date",
                    "product_sku",
                    "quantity",
                ],
                "products": [
                    "product_sku",
                    "product_name",
                ],
                "inventory": [
                    "inventory_date",
                    "product_sku",
                    "on_hand",
                ],
                "bullwhip": [
                    "bullwhip_date",
                    "customer_demand",
                    "retailer_orders",
                    "distributor_orders",
                    "manufacturer_orders",
                ],
            }[target]

            if st.button(
                "Validate Data",
                type="primary",
            ):

                validation = api_request(
                    "POST",
                    "/ingestion/validate",
                    json={
                        "connection_id":
                            connection_id,
                        "mapping": {
                            dest:
                                source
                            for source, dest
                            in edited_mapping.items()
                        },
                        "required_fields":
                            required,
                    },
                )

                if validation:
                    st.session_state.validation_result = (
                        validation
                    )

        validation = (
            st.session_state.validation_result
        )

        if validation:

            c1, c2, c3 = st.columns(3)

            c1.metric(
                "Valid Rows",
                validation.get(
                    "valid_rows",
                    0,
                ),
            )

            c2.metric(
                "Invalid Rows",
                validation.get(
                    "invalid_rows",
                    0,
                ),
            )

            c3.metric(
                "Status",
                "VALID"
                if validation.get(
                    "valid"
                )
                else "CHECK DATA",
            )

            if validation.get(
                "issues"
            ):

                st.dataframe(
                    pd.DataFrame(
                        validation["issues"]
                    ),
                    use_container_width=True,
                    hide_index=True,
                )


        if validation.get("valid"):
            st.success("Data is valid and ready to import.")

            if st.button(
                "Import Valid Rows",
                type="primary",
            ):
                with st.spinner("Importing data into ChainPulse..."):
                    import_result = api_request(
                        "POST",
                        "/ingestion/import",
                        json={
                            "connection_id": connection_id,
                            "mapping": {
                                destination: source_column
                                for source_column, destination
                                in edited_mapping.items()
                                if destination.strip()
                            },
                            "required_fields": required,
                            "target": target,
                        },
                    )

                if import_result:
                    imported = import_result.get("rows_imported", 0)
                    received = import_result.get("rows_received", 0)
                    errors = import_result.get("errors", [])

                    if import_result.get("success"):
                        st.success(
                            f"Imported {imported} of {received} rows into "
                            f"{target.title()}."
                        )
                    else:
                        st.warning(
                            f"Imported {imported} of {received} rows. "
                            "Review the errors below."
                        )

                    if errors:
                        st.dataframe(
                            pd.DataFrame(errors),
                            use_container_width=True,
                            hide_index=True,
                        )
        else:
            st.warning(
                "Resolve validation issues before importing data."
            )


# ============================================================
# REPORTS
# ============================================================
 elif page == "Reports":
    page_header(
        "Report Builder",
        "Create professional Excel, PDF, or Word reports from live ChainPulse data.",
    )

    title = st.text_input(
        "Report title",
        value="ChainPulse Supply Chain Report",
    )

    format_choice = st.radio(
        "Format",
        ["PDF", "Word", "Excel"],
        horizontal=True,
    )

    st.subheader(
        "Sections"
    )

    c1, c2, c3 = st.columns(3)

    include_dashboard = c1.checkbox(
        "Dashboard",
        True,
    )

    include_products = c1.checkbox(
        "Products",
        True,
    )

    include_risk = c2.checkbox(
        "Risk",
        True,
    )

    include_alerts = c2.checkbox(
        "Alerts",
        True,
    )

    include_recommendations = c3.checkbox(
        "Recommendations",
        True,
    )

    summary = api_request(
        "GET",
        "/dashboard/summary",
    )

    if summary:

        st.divider()

        c1, c2, c3, c4 = st.columns(4)

        c1.metric(
            "Products",
            summary.get(
                "product_count",
                0,
            ),
        )

        c2.metric(
            "Demand",
            number(
                summary.get(
                    "total_demand_quantity",
                    0,
                )
            ),
        )

        c3.metric(
            "Revenue",
            number(
                summary.get(
                    "total_revenue",
                    0,
                )
            ),
        )

        c4.metric(
            "Risk",
            (
                f'{summary.get("overall_risk_score", 0):.1f} '
                f'{summary.get("overall_risk_level", "").upper()}'
            ),
        )

    if st.button(
        "Generate Report",
        type="primary",
        use_container_width=True,
    ):

        payload = {
            "title":
                title,
            "format":
                (
                    "pdf"
                    if format_choice == "PDF"
                    else "docx"
                ),
            "include_dashboard":
                include_dashboard,
            "include_products":
                include_products,
            "include_risk":
                include_risk,
            "include_alerts":
                include_alerts,
            "include_recommendations":
                include_recommendations,
        }

        response = requests.post(
            f"{API_URL}/reports/generate",
            headers={
                "Authorization":
                    f"Bearer "
                    f"{st.session_state.token}"
            },
            json=payload,
            timeout=120,
        )

        if response.status_code == 200:

            extension = (
                "pdf"
                if format_choice == "PDF"
                else "docx"
            )

            mime = (
                "application/pdf"
                if format_choice == "PDF"
                else (
                    "application/vnd.openxmlformats-"
                    "officedocument.wordprocessingml.document"
                )
            )

            st.session_state.report_bytes = (
                response.content
            )

            st.session_state.report_name = (
                f"{title.strip() or 'chainpulse_report'}."
                f"{extension}"
            )

            st.session_state.report_mime = mime

            st.success(
                "Report generated successfully."
            )

        else:

            st.error(
                f"Report generation failed "
                f"({response.status_code})."
            )

            st.code(
                response.text,
                language="json",
            )

    if st.session_state.report_bytes:

        st.download_button(
            "⬇️ Download Report",
            data=st.session_state.report_bytes,
            file_name=st.session_state.report_name,
            mime=st.session_state.report_mime,
            use_container_width=True,
        )


# ============================================================
# FOOTER
# ============================================================

st.divider()

st.markdown(
    """
    <div class="cp-footer">
        ChainPulse AI · Supply-chain intelligence platform
    </div>
    """,
    unsafe_allow_html=True,
)





















