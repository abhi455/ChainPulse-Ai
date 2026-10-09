from __future__ import annotations

from pathlib import Path
import socket
import threading
import time

import pandas as pd
import requests
import streamlit as st
import uvicorn


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
# LOGIN
# ============================================================

def render_login():

    st.markdown(
        "<div style='height:8vh'></div>",
        unsafe_allow_html=True,
    )

    left, center, right = st.columns(
        [1, 2, 1]
    )

    with center:

        st.markdown(
            """
            <div class="cp-card"
                 style="padding:2rem;">
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
                value=(
                    "chainpulse.admin.integration"
                    "@example.com"
                ),
            )

            password = st.text_input(
                "Password",
                type="password",
            )

            submitted = (
                st.form_submit_button(
                    "Login",
                    use_container_width=True,
                    type="primary",
                )
            )

        if submitted:

            if (
                not email.strip()
                or not password
            ):
                st.warning(
                    "Enter both email and password."
                )
            else:

                try:
                    response = requests.post(
                        f"{API_URL}/auth/login",
                        json={
                            "email":
                                email.strip(),
                            "password":
                                password,
                        },
                        timeout=20,
                    )

                    if response.status_code != 200:
                        st.error(
                            f"Login failed "
                            f"({response.status_code})"
                        )
                        st.caption(
                            response.text
                        )
                    else:

                        data = response.json()

                        st.session_state.token = (
                            data["access_token"]
                        )

                        user = api_request(
                            "GET",
                            "/auth/me",
                        )

                        if user:
                            st.session_state.user = (
                                user
                            )

                        st.rerun()

                except requests.RequestException as exc:
                    st.error(
                        "Unable to connect to ChainPulse API."
                    )
                    st.caption(str(exc))

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


if not login_required():
    render_login()
    st.stop()


# ============================================================
# LOAD USER
# ============================================================

if st.session_state.user is None:
    current_user = api_request(
        "GET",
        "/auth/me",
    )

    if current_user:
        st.session_state.user = (
            current_user
        )


# ============================================================
# SIDEBAR
# ============================================================

with st.sidebar:

    st.markdown(
        """
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
        """,
        unsafe_allow_html=True,
    )

    st.divider()

    st.caption("WORKSPACE")

    nav = [
        ("📊", "Dashboard"),
        ("📦", "Products"),
        ("📈", "Demand"),
        ("🔮", "Forecasting"),
        ("📦", "Inventory"),
        ("🚚", "Suppliers"),
        ("🔄", "Bullwhip"),
        ("⚠️", "Risk"),
        ("⚡", "Decisions"),
        ("🧪", "Simulations"),
        ("🤖", "AI Explain"),
        ("🔌", "Connect Data"),
        ("📄", "Reports"),
    ]

    labels = [
        f"{icon}  {name}"
        for icon, name in nav
    ]

    label_to_name = {
        f"{icon}  {name}": name
        for icon, name in nav
    }

    current = st.session_state.current_page

    current_label = next(
        (
            label
            for label, name in label_to_name.items()
            if name == current
        ),
        labels[0],
    )

    selected = st.radio(
        "Navigation",
        labels,
        index=labels.index(
            current_label
        ),
        label_visibility="collapsed",
    )

    page = label_to_name[selected]
    st.session_state.current_page = page

    st.divider()

    theme = st.radio(
        "Appearance",
        ["☀️ Light", "🌙 Dark"],
        index=(
            1
            if st.session_state.theme == "dark"
            else 0
        ),
        horizontal=True,
        label_visibility="collapsed",
    )

    new_theme = (
        "dark"
        if theme == "🌙 Dark"
        else "light"
    )

    if new_theme != st.session_state.theme:
        st.session_state.theme = new_theme
        st.rerun()

    st.divider()

    user = st.session_state.user or {}

    st.markdown(
        f"**{user.get('name', 'User')}**"
    )

    st.caption(
        user.get("email", "")
    )

    st.caption(
        "Role: "
        + str(
            user.get(
                "role",
                "user",
            )
        )
    )

    c1, c2 = st.columns(2)

    with c1:
        if st.button(
            "🔄",
            help="Refresh",
            use_container_width=True,
        ):
            st.rerun()

    with c2:
        if st.button(
            "🚪",
            help="Logout",
            use_container_width=True,
        ):
            st.session_state.token = None
            st.session_state.user = None
            st.session_state.current_page = (
                "Dashboard"
            )
            st.rerun()


# ============================================================
# DASHBOARD
# ============================================================

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

        c1, c2, c3, c4, c5 = st.columns(5)

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
            "Inventory",
            number(
                summary.get(
                    "inventory_available",
                    0,
                )
            ),
        )

        c5.metric(
            "Risk",
            (
                f'{summary.get("overall_risk_score", 0):.1f}'
                f" · "
                f'{summary.get("overall_risk_level", "").upper()}'
            ),
        )

        st.divider()

        left, right = st.columns(
            [1.25, 1]
        )

        with left:

            st.subheader(
                "Risk Overview"
            )

            risk_data = pd.DataFrame(
                {
                    "Component": [
                        "Demand",
                        "Inventory",
                        "Supplier",
                    ],
                    "Risk Score": [
                        100 if summary.get(
                            "demand_risk_level"
                        ) == "critical"
                        else 75 if summary.get(
                            "demand_risk_level"
                        ) == "high"
                        else 50 if summary.get(
                            "demand_risk_level"
                        ) == "medium"
                        else 25,

                        100 if summary.get(
                            "inventory_risk_level"
                        ) == "critical"
                        else 75 if summary.get(
                            "inventory_risk_level"
                        ) == "high"
                        else 50 if summary.get(
                            "inventory_risk_level"
                        ) == "medium"
                        else 25,

                        100 if summary.get(
                            "supplier_risk_level"
                        ) == "critical"
                        else 75 if summary.get(
                            "supplier_risk_level"
                        ) == "high"
                        else 50 if summary.get(
                            "supplier_risk_level"
                        ) == "medium"
                        else 25,
                    ],
                }
            )

            st.bar_chart(
                risk_data.set_index(
                    "Component"
                )
            )

        with right:

            st.subheader(
                "Operational Status"
            )

            st.markdown(
                f"**Overall:** "
                f"{risk_badge(summary.get('overall_risk_level'))}"
            )

            st.markdown(
                f"**Supplier reliability:** "
                f"{summary.get('average_supplier_reliability', 0):.1f}%"
            )

            st.markdown(
                f"**Below reorder:** "
                f"{summary.get('inventory_below_reorder', 0)}"
            )

            st.markdown(
                f"**Stockouts:** "
                f"{summary.get('inventory_stockouts', 0)}"
            )

        st.divider()

        st.subheader(
            "Needs Attention"
        )

        alerts = summary.get(
            "alerts",
            [],
        )

        if alerts:
            for alert in alerts:
                st.warning(alert)
        else:
            st.success(
                "No major operational alerts detected."
            )

        recommendations = summary.get(
            "recommendations",
            [],
        )

        if recommendations:

            st.subheader(
                "Recommended Actions"
            )

            for recommendation in recommendations:
                st.info(
                    recommendation
                )


# ============================================================
# PRODUCTS
# ============================================================

elif page == "Products":

    page_header(
        "Products",
        "Manage products and inspect product-level intelligence.",
    )

    products = api_request(
        "GET",
        "/products",
    )

    if products:

        df = pd.DataFrame(products)

        search = st.text_input(
            "Search products",
            placeholder="Search by SKU or name...",
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

        if products:

            selected = st.selectbox(
                "Product details",
                products,
                format_func=lambda x:
                    f"{x['sku']} — {x['name']}",
            )

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


# ============================================================
# DEMAND
# ============================================================

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

    defaults = [
        "100,115,108,130,125,150,140",
        "105,120,115,145,135,165,155",
        "110,130,125,160,150,180,170",
        "115,140,135,175,165,195,185",
    ]

    labels = [
        "Customer demand",
        "Retailer orders",
        "Distributor orders",
        "Manufacturer orders",
    ]

    values = []

    for label, default in zip(
        labels,
        defaults,
    ):
        values.append(
            st.text_input(
                label,
                value=default,
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


# ============================================================
# REPORTS
# ============================================================

elif page == "Reports":

    page_header(
        "Report Builder",
        "Create professional PDF or Word reports from live ChainPulse data.",
    )

    title = st.text_input(
        "Report title",
        value="ChainPulse Supply Chain Report",
    )

    format_choice = st.radio(
        "Format",
        ["PDF", "Word"],
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
