from pathlib import Path
import os
from typing import Any

import pandas as pd
import requests
import streamlit as st


# ============================================================
# CONFIG
# ============================================================

API_URL = os.getenv(
    "CHAINPULSE_API_URL",
    "http://127.0.0.1:8000/api/v1",
).rstrip("/")



# ============================================================
# AUTOMATIC BACKEND STARTUP
# ============================================================

import socket
import threading
import time

import uvicorn


CHAINPULSE_API_HOST = "127.0.0.1"
CHAINPULSE_API_PORT = 8000


def backend_is_running() -> bool:
    sock = socket.socket(
        socket.AF_INET,
        socket.SOCK_STREAM,
    )

    sock.settimeout(0.3)

    try:
        return (
            sock.connect_ex(
                (
                    CHAINPULSE_API_HOST,
                    CHAINPULSE_API_PORT,
                )
            )
            == 0
        )

    finally:
        sock.close()


def start_backend():
    uvicorn.run(
        "backend.main:app",
        host=CHAINPULSE_API_HOST,
        port=CHAINPULSE_API_PORT,
        log_level="warning",
    )


def ensure_backend_running():

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
# CHAINPULSE UI THEME
# ============================================================

if "theme_mode" not in st.session_state:
    st.session_state.theme_mode = "light"


def apply_chainpulse_theme():
    dark = st.session_state.theme_mode == "dark"

    if dark:
        background = "#0b1220"
        surface = "#111827"
        surface_2 = "#172033"
        text = "#f3f4f6"
        muted = "#9ca3af"
        border = "#263244"
        input_bg = "#111827"
    else:
        background = "#f7f9fc"
        surface = "#ffffff"
        surface_2 = "#f1f5f9"
        text = "#111827"
        muted = "#64748b"
        border = "#e2e8f0"
        input_bg = "#ffffff"

    st.markdown(
        f"""
        <style>

        /* ================================================== */
        /* GLOBAL */
        /* ================================================== */

        .stApp {{
            background: {background};
            color: {text};
        }}

        .main .block-container {{
            max-width: 1450px;
            padding-top: 2rem;
            padding-bottom: 3rem;
            padding-left: 2.5rem;
            padding-right: 2.5rem;
        }}

        h1 {{
            font-size: 2.2rem !important;
            font-weight: 750 !important;
            letter-spacing: -0.03em;
        }}

        h2 {{
            font-size: 1.55rem !important;
            font-weight: 700 !important;
        }}

        h3 {{
            font-size: 1.15rem !important;
            font-weight: 650 !important;
        }}

        p, label, .stMarkdown {{
            color: {text};
        }}

        /* ================================================== */
        /* SIDEBAR */
        /* ================================================== */

        section[data-testid="stSidebar"] {{
            background: {surface};
            border-right: 1px solid {border};
        }}

        section[data-testid="stSidebar"] > div {{
            padding-top: 1rem;
        }}

        section[data-testid="stSidebar"] .stRadio label {{
            border-radius: 10px;
            padding: 0.55rem 0.75rem;
            margin: 0.12rem 0;
            transition: 0.15s ease;
        }}

        section[data-testid="stSidebar"] .stRadio label:hover {{
            background: {surface_2};
        }}

        /* ================================================== */
        /* TOP BRAND */
        /* ================================================== */

        .cp-brand {{
            display: flex;
            align-items: center;
            gap: 12px;
            margin-bottom: 0.25rem;
        }}

        .cp-logo {{
            width: 42px;
            height: 42px;
            border-radius: 12px;
            background: linear-gradient(
                135deg,
                #2563eb,
                #14b8a6
            );
            display: flex;
            align-items: center;
            justify-content: center;
            color: white;
            font-weight: 800;
            font-size: 18px;
            box-shadow: 0 8px 20px rgba(37, 99, 235, 0.22);
        }}

        .cp-brand-title {{
            font-size: 20px;
            font-weight: 800;
            line-height: 1;
            color: {text};
        }}

        .cp-brand-subtitle {{
            font-size: 11px;
            color: {muted};
            margin-top: 4px;
        }}

        /* ================================================== */
        /* CARDS */
        /* ================================================== */

        div[data-testid="stMetric"] {{
            background: {surface};
            border: 1px solid {border};
            border-radius: 14px;
            padding: 1rem;
            box-shadow: 0 4px 16px rgba(15, 23, 42, 0.04);
        }}

        div[data-testid="stMetricLabel"] {{
            color: {muted};
        }}

        div[data-testid="stMetricValue"] {{
            color: {text};
            font-weight: 750;
        }}

        /* ================================================== */
        /* CONTAINERS */
        /* ================================================== */

        div[data-testid="stVerticalBlockBorderWrapper"] {{
            border-color: {border};
            border-radius: 14px;
            background: {surface};
        }}

        /* ================================================== */
        /* INPUTS */
        /* ================================================== */

        input, textarea {{
            background: {input_bg} !important;
            color: {text} !important;
            border-color: {border} !important;
            border-radius: 9px !important;
        }}

        div[data-baseweb="select"] > div {{
            background: {input_bg};
            border-color: {border};
            border-radius: 9px;
        }}

        /* ================================================== */
        /* BUTTONS */
        /* ================================================== */

        .stButton > button {{
            border-radius: 9px;
            min-height: 42px;
            font-weight: 650;
            border: 1px solid {border};
            transition: all 0.15s ease;
        }}

        .stButton > button:hover {{
            transform: translateY(-1px);
            box-shadow: 0 5px 14px rgba(15, 23, 42, 0.08);
        }}

        .stDownloadButton > button {{
            border-radius: 9px;
            min-height: 42px;
            font-weight: 650;
        }}

        /* ================================================== */
        /* ALERTS */
        /* ================================================== */

        div[data-testid="stAlert"] {{
            border-radius: 10px;
        }}

        /* ================================================== */
        /* DATAFRAME */
        /* ================================================== */

        div[data-testid="stDataFrame"] {{
            border: 1px solid {border};
            border-radius: 12px;
            overflow: hidden;
        }}

        /* ================================================== */
        /* TABS */
        /* ================================================== */

        button[data-baseweb="tab"] {{
            font-weight: 650;
        }}

        /* ================================================== */
        /* DIVIDERS */
        /* ================================================== */

        hr {{
            border-color: {border};
        }}

        /* ================================================== */
        /* FOOTER */
        /* ================================================== */

        .cp-footer {{
            text-align: center;
            color: {muted};
            font-size: 12px;
            padding: 1rem 0;
        }}

        </style>
        """,
        unsafe_allow_html=True,
    )


apply_chainpulse_theme()


st.set_page_config(
    page_title="ChainPulse AI",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)


# ============================================================
# SESSION STATE
# ============================================================

if "token" not in st.session_state:
    st.session_state.token = None

if "user" not in st.session_state:
    st.session_state.user = None

if "api_error" not in st.session_state:
    st.session_state.api_error = None


# ============================================================
# API HELPERS
# ============================================================

def auth_headers() -> dict[str, str]:
    if not st.session_state.token:
        return {}
    return {
        "Authorization": f"Bearer {st.session_state.token}",
    }


def api_request(
    method: str,
    endpoint: str,
    *,
    json: dict[str, Any] | None = None,
    params: dict[str, Any] | None = None,
    timeout: int = 20,
) -> Any:

    try:
        response = requests.request(
            method=method,
            url=f"{API_URL}{endpoint}",
            headers=auth_headers(),
            json=json,
            params=params,
            timeout=timeout,
        )
    except requests.RequestException as exc:
        st.error(
            "ChainPulse API is unavailable. "
            "Start FastAPI on http://127.0.0.1:8000."
        )
        st.caption(str(exc))
        return None

    if response.status_code == 401:
        st.session_state.token = None
        st.session_state.user = None
        st.warning("Your session has expired. Please log in again.")
        st.rerun()

    if not response.ok:
        try:
            detail = response.json()
        except ValueError:
            detail = response.text

        st.error(
            f"API error {response.status_code}: {detail}"
        )
        return None

    if not response.content:
        return {}

    try:
        return response.json()
    except ValueError:
        return response.text


def money(value: float | None) -> str:
    if value is None:
        return "—"
    return f"${value:,.2f}"


def number(value: float | int | None) -> str:
    if value is None:
        return "—"
    return f"{value:,.2f}"


def risk_badge(level: str | None) -> str:
    value = (level or "unknown").upper()

    mapping = {
        "LOW": "🟢 LOW",
        "MEDIUM": "🟡 MEDIUM",
        "HIGH": "🟠 HIGH",
        "CRITICAL": "🔴 CRITICAL",
    }

    return mapping.get(value, f"⚪ {value}")


def require_login() -> bool:
    if st.session_state.token:
        return True

    st.title("ChainPulse AI")
    st.subheader("Supply-chain intelligence platform")
    st.info("Log in to access your organization dashboard.")

    with st.form("login_form"):
        email = st.text_input(
            "Email",
            value="chainpulse.admin.integration@example.com",
        )
        password = st.text_input(
            "Password",
            type="password",
            value="",
        )

        submitted = st.form_submit_button(
            "Login",
            use_container_width=True,
        )

    if submitted:
        if not email.strip() or not password:
            st.warning("Enter both email and password.")
            return False

        try:
            response = requests.post(
                f"{API_URL}/auth/login",
                json={
                    "email": email.strip(),
                    "password": password,
                },
                timeout=20,
            )
        except requests.RequestException as exc:
            st.error(
                "Unable to connect to ChainPulse API."
            )
            st.caption(str(exc))
            return False

        if response.status_code != 200:
            try:
                detail = response.json()
            except ValueError:
                detail = response.text

            st.error(
                f"Login failed ({response.status_code}): {detail}"
            )
            return False

        data = response.json()

        st.session_state.token = data["access_token"]

        user = api_request(
            "GET",
            "/auth/me",
        )

        if user:
            st.session_state.user = user
            st.rerun()

    return False


# ============================================================
# LOGIN
# ============================================================

if not require_login():
    st.stop()


# ============================================================

# ============================================================
# OAUTH CALLBACK
# ============================================================

def handle_oauth_callback():
    oauth_code = st.query_params.get("oauth_code")

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
                f"OAuth login failed: {response.text}"
            )
            return

        data = response.json()

        st.session_state["token"] = data["access_token"]
        st.session_state["authenticated"] = True

        st.query_params.clear()

        st.rerun()

    except requests.RequestException as exc:
        st.error(
            f"Unable to connect to ChainPulse API: {exc}"
        )


handle_oauth_callback()




# ============================================================
# SOCIAL LOGIN
# ============================================================

if not st.session_state.get("authenticated", False):

    st.divider()

    st.subheader("Continue with")

    oauth_google, oauth_microsoft, oauth_meta = st.columns(3)

    with oauth_google:
        st.link_button(
            "🔵 Google",
            f"{API_URL}/auth/oauth/google/login",
            use_container_width=True,
        )

    with oauth_microsoft:
        st.link_button(
            "🟦 Microsoft",
            f"{API_URL}/auth/oauth/microsoft/login",
            use_container_width=True,
        )

    with oauth_meta:
        st.link_button(
            "Ⓜ️ Meta",
            f"{API_URL}/auth/oauth/meta/login",
            use_container_width=True,
        )

    st.caption(
        "Sign in securely using your existing Google, "
        "Microsoft, or Meta account."
    )


# SIDEBAR
# ============================================================

user = st.session_state.user or {}

with st.sidebar:

    st.markdown(
        """
        <div class="cp-brand">
            <div class="cp-logo">CP</div>
            <div>
                <div class="cp-brand-title">ChainPulse AI</div>
                <div class="cp-brand-subtitle">
                    Supply-chain intelligence
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.divider()

    theme_mode = st.radio(
        "Appearance",
        ["☀️ Light", "🌙 Dark"],
        index=(
            1
            if st.session_state.theme_mode == "dark"
            else 0
        ),
        horizontal=True,
        label_visibility="collapsed",
    )

    new_theme = (
        "dark"
        if theme_mode == "🌙 Dark"
        else "light"
    )

    if new_theme != st.session_state.theme_mode:
        st.session_state.theme_mode = new_theme
        st.rerun()



    st.markdown(
        "## 📦 ChainPulse AI"
    )

    st.caption(
        "Supply-chain intelligence platform"
    )

    st.divider()

    navigation = [
        ("📊 Dashboard", "Dashboard"),
        ("📦 Products", "Products"),
        ("📈 Demand", "Demand"),
        ("🔮 Forecasting", "Forecasting"),
        ("📦 Inventory", "Inventory"),
        ("🚚 Suppliers", "Suppliers"),
        ("🔄 Bullwhip", "Bullwhip"),
        ("⚠️ Risk", "Risk"),
        ("⚡ Decisions", "Decisions"),
        ("🧪 Simulations", "Simulations"),
        ("🤖 AI Explain", "AI Explain"),
        ("🔌 Connect Data", "Connect Data"),
        ("📄 Reports", "Reports"),
    ]

    labels = [
        label
        for label, _ in navigation
    ]

    label_to_page = dict(navigation)

    current_page = st.session_state.get(
        "current_page",
        "Dashboard",
    )

    current_label = next(
        (
            label
            for label, value in navigation
            if value == current_page
        ),
        labels[0],
    )

    selected_label = st.radio(
        "Navigation",
        labels,
        index=labels.index(current_label),
        label_visibility="collapsed",
    )

    page = label_to_page[selected_label]

    st.session_state.current_page = page

    st.divider()

    current_user = st.session_state.get(
        "user"
    )

    if current_user:

        st.markdown(
            f"**{current_user.get('name', 'User')}**"
        )

        st.caption(
            current_user.get(
                "email",
                "",
            )
        )

        st.caption(
            "Role: "
            + str(
                current_user.get(
                    "role",
                    "user",
                )
            )
        )

    col_refresh, col_logout = st.columns(2)

    with col_refresh:

        if st.button(
            "🔄",
            help="Refresh current page",
            use_container_width=True,
        ):
            st.rerun()

    with col_logout:

        if st.button(
            "🚪",
            help="Log out",
            use_container_width=True,
        ):

            st.session_state.token = None
            st.session_state.user = None
            st.session_state.ai_decision = None

            st.session_state.pop(
                "active_connection_id",
                None,
            )

            st.session_state.pop(
                "mapping_result",
                None,
            )

            st.session_state.pop(
                "validation_result",
                None,
            )

            st.session_state.current_page = (
                "Dashboard"
            )

            st.rerun()



# ============================================================
# DASHBOARD
# ============================================================

if page == "Dashboard":

    st.title("📊 Supply Chain Dashboard")
    st.caption(
        "Real-time operational view of your ChainPulse organization."
    )

    summary = api_request(
        "GET",
        "/dashboard/summary",
    )

    if summary is None:
        st.stop()

    cols = st.columns(4)

    cols[0].metric(
        "Products",
        summary.get("active_product_count", 0),
    )

    cols[1].metric(
        "Demand Records",
        summary.get("demand_record_count", 0),
    )

    cols[2].metric(
        "Inventory Available",
        number(summary.get("inventory_available")),
    )

    cols[3].metric(
        "Overall Risk",
        f"{number(summary.get('overall_risk_score'))}",
        help=summary.get("overall_risk_level"),
    )

    st.divider()

    left, right = st.columns(2)

    with left:
        st.subheader("Risk Overview")

        risk_data = pd.DataFrame(
            {
                "Component": [
                    "Overall",
                    "Demand",
                    "Inventory",
                    "Supplier",
                ],
                "Risk Score": [
                    summary.get("overall_risk_score", 0),
                    {
                        "low": 25,
                        "medium": 50,
                        "high": 75,
                        "critical": 100,
                    }.get(
                        summary.get("demand_risk_level"),
                        0,
                    ),
                    {
                        "low": 25,
                        "medium": 50,
                        "high": 75,
                        "critical": 100,
                    }.get(
                        summary.get("inventory_risk_level"),
                        0,
                    ),
                    {
                        "low": 25,
                        "medium": 50,
                        "high": 75,
                        "critical": 100,
                    }.get(
                        summary.get("supplier_risk_level"),
                        0,
                    ),
                ],
            }
        )

        st.bar_chart(
            risk_data.set_index("Component")
        )

        st.write(
            f"**Overall:** "
            f"{risk_badge(summary.get('overall_risk_level'))}"
        )

        drivers = summary.get(
            "primary_risk_drivers",
            [],
        )

        if drivers:
            st.write(
                "**Primary drivers:** "
                + ", ".join(drivers)
            )

    with right:
        st.subheader("Operational Alerts")

        for alert in summary.get(
            "alerts",
            [],
        ):
            st.warning(alert)

        st.subheader("Recommendations")

        for recommendation in summary.get(
            "recommendations",
            [],
        ):
            st.info(recommendation)

    st.divider()

    k1, k2, k3, k4 = st.columns(4)

    k1.metric(
        "Total Demand",
        number(summary.get("total_demand_quantity")),
    )

    k2.metric(
        "Revenue",
        money(summary.get("total_revenue")),
    )

    k3.metric(
        "Inventory On Hand",
        number(summary.get("inventory_on_hand")),
    )

    k4.metric(
        "Suppliers",
        summary.get("supplier_count", 0),
    )


# ============================================================
# PRODUCTS
# ============================================================

elif page == "Products":

    st.title("📦 Products")

    products = api_request(
        "GET",
        "/products",
    )

    if products is None:
        st.stop()

    if not products:
        st.info("No products found.")
        st.stop()

    df = pd.DataFrame(products)

    st.dataframe(
        df[
            [
                "sku",
                "name",
                "category",
                "unit_cost",
                "selling_price",
                "lead_time_days",
                "active",
            ]
        ],
        use_container_width=True,
        hide_index=True,
    )

    st.divider()

    selected = st.selectbox(
        "Select product",
        range(len(products)),
        format_func=lambda i:
        f"{products[i]['sku']} — {products[i]['name']}",
    )

    product = products[selected]

    detail = api_request(
        "GET",
        f"/dashboard/product/{product['id']}",
    )

    if detail:
        c1, c2, c3, c4 = st.columns(4)

        c1.metric(
            "Demand",
            number(detail["total_demand_quantity"]),
        )

        c2.metric(
            "Revenue",
            money(detail["total_revenue"]),
        )

        c3.metric(
            "Inventory",
            number(detail["latest_inventory_on_hand"]),
        )

        c4.metric(
            "Forecast",
            number(detail["latest_forecast_demand"]),
        )

        st.subheader("Product Detail")
        st.json(detail)


# ============================================================
# DEMAND
# ============================================================

elif page == "Demand":

    st.title("📉 Demand Analysis")

    products = api_request(
        "GET",
        "/products",
    )

    if not products:
        st.info("No products available.")
        st.stop()

    selected = st.selectbox(
        "Product",
        range(len(products)),
        format_func=lambda i:
        f"{products[i]['sku']} — {products[i]['name']}",
    )

    product_id = products[selected]["id"]

    demand = api_request(
        "GET",
        f"/demand/{product_id}",
    )

    if demand is None:
        st.stop()

    if not demand:
        st.info("No demand history for this product.")
        st.stop()

    df = pd.DataFrame(demand)

    df["date"] = pd.to_datetime(df["date"])
    df = df.sort_values("date")

    st.subheader("Demand Trend")

    chart_data = df.set_index("date")[["quantity"]]

    st.line_chart(chart_data)

    c1, c2, c3 = st.columns(3)

    c1.metric(
        "Records",
        len(df),
    )

    c2.metric(
        "Total Quantity",
        number(df["quantity"].sum()),
    )

    c3.metric(
        "Revenue",
        money(df["revenue"].sum()),
    )

    st.dataframe(
        df,
        use_container_width=True,
        hide_index=True,
    )

    st.divider()

    st.subheader("Add Demand Record")

    with st.form("demand_form"):

        demand_date = st.date_input(
            "Date"
        )

        quantity = st.number_input(
            "Quantity",
            min_value=0.0,
            value=100.0,
        )

        revenue = st.number_input(
            "Revenue",
            min_value=0.0,
            value=0.0,
        )

        submit = st.form_submit_button(
            "Create Demand Record"
        )

    if submit:
        result = api_request(
            "POST",
            "/demand",
            json={
                "product_id": product_id,
                "date": demand_date.isoformat(),
                "quantity": quantity,
                "revenue": revenue,
            },
        )

        if result:
            st.success("Demand record created.")
            st.rerun()


# ============================================================
# FORECASTING
# ============================================================

elif page == "Forecasting":

    st.title("📈 Forecasting")

    products = api_request(
        "GET",
        "/products",
    )

    if not products:
        st.info("No products available.")
        st.stop()

    selected = st.selectbox(
        "Product",
        range(len(products)),
        format_func=lambda i:
        f"{products[i]['sku']} — {products[i]['name']}",
    )

    product_id = products[selected]["id"]

    periods = st.number_input(
        "Forecast periods",
        min_value=1,
        max_value=30,
        value=3,
    )

    window = st.number_input(
        "Moving-average window",
        min_value=1,
        max_value=30,
        value=3,
    )

    if st.button(
        "Generate Forecast",
        type="primary",
    ):

        result = api_request(
            "POST",
            f"/forecasting/product/{product_id}",
            json={
                "periods": periods,
                "window": window,
            },
        )

        if result:

            demand = api_request(
                "GET",
                f"/demand/{product_id}",
            )

            if demand:

                historical = pd.DataFrame(demand)

                historical["date"] = pd.to_datetime(
                    historical["date"]
                )

                historical = historical.sort_values(
                    "date"
                )

                st.subheader("Historical Demand")

                st.line_chart(
                    historical.set_index("date")[["quantity"]]
                )

            c1, c2 = st.columns(2)

            with c1:
                st.subheader("Moving Average")
                st.line_chart(
                    result["moving_average"]
                )

            with c2:
                st.subheader("Exponential Smoothing")
                st.line_chart(
                    result["exponential_smoothing"]
                )

            st.json(result)


# ============================================================
# INVENTORY
# ============================================================

elif page == "Inventory":

    st.title("📦 Inventory Intelligence")

    products = api_request(
        "GET",
        "/products",
    )

    if not products:
        st.info("No products available.")
        st.stop()

    selected = st.selectbox(
        "Product",
        range(len(products)),
        format_func=lambda i:
        f"{products[i]['sku']} — {products[i]['name']}",
    )

    product = products[selected]
    product_id = product["id"]

    history = api_request(
        "GET",
        f"/inventory/{product_id}",
    )

    if history:
        df = pd.DataFrame(history)

        df["date"] = pd.to_datetime(
            df["date"]
        )

        st.subheader("Inventory History")

        st.line_chart(
            df.set_index("date")[["on_hand"]]
        )

        st.dataframe(
            df,
            use_container_width=True,
            hide_index=True,
        )

    st.divider()

    st.subheader("Inventory Analysis")

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
        value=float(product["lead_time_days"]),
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
        "Analyze Inventory",
        type="primary",
    ):

        result = api_request(
            "POST",
            "/inventory/analyze",
            json={
                "average_daily_demand":
                    average_daily_demand,
                "demand_std": demand_std,
                "lead_time_days": lead_time_days,
                "current_inventory": current_inventory,
                "annual_demand": annual_demand,
                "ordering_cost": ordering_cost,
                "holding_cost": holding_cost,
                "service_level_z": 1.65,
            },
        )

        if result:

            cols = st.columns(4)

            cols[0].metric(
                "Safety Stock",
                number(result["safety_stock"]),
            )

            cols[1].metric(
                "Reorder Point",
                number(result["reorder_point"]),
            )

            cols[2].metric(
                "EOQ",
                number(result["economic_order_quantity"]),
            )

            cols[3].metric(
                "Days of Inventory",
                number(result["days_of_inventory"]),
            )

            st.write(
                f"Stockout Risk: "
                f"{risk_badge(result['stockout_risk'])}"
            )

            st.write(
                f"Overstock Risk: "
                f"{risk_badge(result['overstock_risk'])}"
            )


# ============================================================
# SUPPLIERS
# ============================================================

elif page == "Suppliers":

    st.title("🚚 Supplier Intelligence")

    suppliers = api_request(
        "GET",
        "/suppliers",
    )

    if suppliers:
        st.subheader("Suppliers")

        st.dataframe(
            pd.DataFrame(suppliers),
            use_container_width=True,
            hide_index=True,
        )

    st.divider()

    st.subheader("Evaluate Supplier")

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
                "on_time_rate": on_time_rate,
                "defect_rate": defect_rate,
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
                number(result["reliability_score"]),
            )

            cols[1].metric(
                "Quality",
                number(result["quality_score"]),
            )

            cols[2].metric(
                "Lead Time",
                number(result["lead_time_score"]),
            )

            cols[3].metric(
                "Cost",
                number(result["cost_score"]),
            )

            cols[4].metric(
                "Overall",
                number(result["overall_score"]),
            )

            st.write(
                f"Risk: "
                f"{risk_badge(result['risk_level'])}"
            )

            st.success(
                result["recommendation"]
            )


# ============================================================
# BULLWHIP
# ============================================================

elif page == "Bullwhip":

    st.title("🔄 Bullwhip Effect")

    st.caption(
        "Measure order variability amplification across the supply chain."
    )

    default_values = [
        100,
        115,
        108,
        130,
        125,
        150,
        140,
    ]

    customer = st.text_input(
        "Customer demand",
        value=",".join(map(str, default_values)),
    )

    retailer = st.text_input(
        "Retailer orders",
        value="105,120,115,145,135,165,155",
    )

    distributor = st.text_input(
        "Distributor orders",
        value="110,130,125,160,150,180,170",
    )

    manufacturer = st.text_input(
        "Manufacturer orders",
        value="115,140,135,175,165,195,185",
    )

    if st.button(
        "Analyze Bullwhip",
        type="primary",
    ):

        try:
            payload = {
                "customer_demand":
                    [float(x.strip()) for x in customer.split(",")],
                "retailer_orders":
                    [float(x.strip()) for x in retailer.split(",")],
                "distributor_orders":
                    [float(x.strip()) for x in distributor.split(",")],
                "manufacturer_orders":
                    [float(x.strip()) for x in manufacturer.split(",")],
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
                number(result["overall_bullwhip_ratio"]),
            )

            c2.metric(
                "Severity",
                result["severity"].upper(),
            )

            c3.metric(
                "Interpretation",
                result["interpretation"],
            )

            st.subheader("Variance by Level")

            variance_df = pd.DataFrame(
                {
                    "Stage": [
                        "Customer",
                        "Retailer",
                        "Distributor",
                        "Manufacturer",
                    ],
                    "Variance": [
                        result["customer_variance"],
                        result["retailer_variance"],
                        result["distributor_variance"],
                        result["manufacturer_variance"],
                    ],
                }
            )

            st.bar_chart(
                variance_df.set_index("Stage")
            )

            st.subheader("Bullwhip Ratios")

            ratio_df = pd.DataFrame(
                {
                    "Stage": [
                        "Retailer",
                        "Distributor",
                        "Manufacturer",
                    ],
                    "Ratio": [
                        result["retailer_bullwhip_ratio"],
                        result["distributor_bullwhip_ratio"],
                        result["manufacturer_bullwhip_ratio"],
                    ],
                }
            )

            st.bar_chart(
                ratio_df.set_index("Stage")
            )

            st.subheader("Recommendations")

            for recommendation in result.get(
                "recommendations",
                [],
            ):
                st.warning(recommendation)


# ============================================================
# RISK
# ============================================================

elif page == "Risk":

    st.title("⚠️ Risk Intelligence")

    c1, c2, c3, c4 = st.columns(4)

    demand_risk = c1.selectbox(
        "Demand",
        ["low", "medium", "high", "critical"],
        index=1,
    )

    inventory_risk = c2.selectbox(
        "Inventory",
        ["low", "medium", "high", "critical"],
        index=1,
    )

    supplier_risk = c3.selectbox(
        "Supplier",
        ["low", "medium", "high", "critical"],
        index=1,
    )

    bullwhip_risk = c4.selectbox(
        "Bullwhip",
        ["low", "medium", "high", "critical"],
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
                "components": {
                    "demand": demand_risk,
                    "inventory": inventory_risk,
                    "supplier": supplier_risk,
                    "bullwhip": bullwhip_risk,
                }
            },
        )

        if result:

            c1, c2 = st.columns(2)

            c1.metric(
                "Risk Score",
                number(result["overall_score"]),
            )

            c2.metric(
                "Risk Level",
                result["risk_level"].upper(),
            )

            st.subheader("Primary Drivers")

            for driver in result.get(
                "primary_drivers",
                [],
            ):
                st.warning(driver.upper())

            details = pd.DataFrame(
                result["component_details"]
            )

            st.subheader("Risk Components")

            st.dataframe(
                details,
                use_container_width=True,
                hide_index=True,
            )

            st.bar_chart(
                details.set_index("component")[["score"]]
            )


# ============================================================
# DECISIONS
# ============================================================

elif page == "Decisions":

    st.title("⚡ Decision Engine")

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
        ["low", "medium", "high", "critical"],
        index=1,
    )

    overstock_risk = c2.selectbox(
        "Overstock risk",
        ["low", "medium", "high", "critical"],
        index=0,
    )

    supplier_risk = c3.selectbox(
        "Supplier risk",
        ["low", "medium", "high", "critical"],
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
                number(result["risk_score"]),
            )

            c2.metric(
                "Risk Level",
                result["risk_level"].upper(),
            )

            c3.metric(
                "Decisions",
                len(result["decisions"]),
            )

            for decision in result["decisions"]:
                with st.container(border=True):
                    st.subheader(
                        decision["action"]
                    )

                    st.write(
                        decision["reason"]
                    )

                    st.write(
                        f"Priority: **{decision['priority']}**"
                    )

                    st.write(
                        f"Confidence: **{decision['confidence']:.1f}%**"
                    )

                    st.caption(
                        f"Category: {decision['category']}"
                    )


# ============================================================
# SIMULATIONS
# ============================================================

elif page == "Simulations":

    st.title("🧪 Scenario Simulation")

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

    st.divider()

    c1, c2, c3 = st.columns(3)

    average_daily_demand = c1.number_input(
        "Average daily demand",
        min_value=0.0,
        value=125.0,
    )

    demand_std = c2.number_input(
        "Demand std",
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
                "service_level_z": 1.65,
            },
        )

        if result:

            st.subheader("Baseline vs Simulated")

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
                        result["baseline"][x]
                        for x in metrics
                    ],
                    "Scenario": [
                        result["simulated"][x]
                        for x in metrics
                    ],
                    "Change %": [
                        result["impact"][x]["change_pct"]
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
                table.set_index("Metric")[
                    ["Baseline", "Scenario"]
                ]
            )

            st.subheader("Impact")

            for metric in metrics:
                impact = result["impact"][metric]

                st.write(
                    f"**{metric.replace('_', ' ').title()}** — "
                    f"{impact['change_pct']:.2f}% "
                    f"({impact['impact']})"
                )


# ============================================================
# AI EXPLAIN
# ============================================================

elif page == "AI Explain":

    st.title("🤖 AI Explainability")
    st.caption(
        "Generate an explanation from an actual ChainPulse decision."
    )

    st.subheader("1. Generate Decision")

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
        ["low", "medium", "high", "critical"],
        index=1,
    )

    overstock_risk = c2.selectbox(
        "Overstock risk",
        ["low", "medium", "high", "critical"],
        index=0,
    )

    supplier_risk = c3.selectbox(
        "Supplier risk",
        ["low", "medium", "high", "critical"],
        index=0,
    )

    if st.button(
        "Generate Decision",
        type="primary",
    ):

        decision_result = api_request(
            "POST",
            "/decisions/evaluate",
            json={
                "current_inventory": current_inventory,
                "reorder_point": reorder_point,
                "stockout_risk": stockout_risk,
                "overstock_risk": overstock_risk,
                "supplier_risk_level": supplier_risk,
            },
        )

        if decision_result:
            st.session_state.ai_decision = decision_result

    decision_result = st.session_state.get("ai_decision")

    if decision_result:

        st.divider()
        st.subheader("Decision Result")

        c1, c2, c3 = st.columns(3)

        c1.metric(
            "Risk Score",
            number(decision_result.get("risk_score", 0)),
        )

        c2.metric(
            "Risk Level",
            decision_result.get(
                "risk_level",
                "unknown",
            ).upper(),
        )

        c3.metric(
            "Decisions",
            len(
                decision_result.get(
                    "decisions",
                    [],
                )
            ),
        )

        for decision in decision_result.get("decisions", []):
            with st.container(border=True):
                st.write(
                    f"**Action:** "
                    f"{decision.get('action', 'UNKNOWN')}"
                )
                st.write(
                    f"**Priority:** "
                    f"{decision.get('priority', 'unknown')}"
                )
                st.write(
                    f"**Reason:** "
                    f"{decision.get('reason', '')}"
                )
                st.write(
                    f"**Confidence:** "
                    f"{float(decision.get('confidence', 0)):.1f}%"
                )

        st.divider()
        st.subheader("AI Explanation")

        if st.button(
            "Explain This Decision",
            type="primary",
        ):

            ai_result = api_request(
                "POST",
                "/ai/explain",
                json={
                    "decision": decision_result,
                },
            )

            if ai_result:
                st.subheader(
                    ai_result.get(
                        "title",
                        "ChainPulse Insight",
                    )
                )

                st.write(
                    ai_result.get(
                        "summary",
                        "",
                    )
                )

                st.success(
                    ai_result.get(
                        "recommendation",
                        "",
                    )
                )

                c1, c2 = st.columns(2)

                c1.metric(
                    "Confidence",
                    f"{float(ai_result.get('confidence', 0)):.1f}%",
                )

                c2.metric(
                    "Category",
                    ai_result.get(
                        "category",
                        "general",
                    ),
                )


# ============================================================
# CONNECT DATA
# ============================================================

elif page == "Connect Data":

    st.title("🔌 Connect Data")
    st.caption(
        "Connect files and data sources, preview them, map columns, "
        "validate the data, and import it into ChainPulse."
    )

    upload_tab, saved_tab = st.tabs(
        ["Upload Data", "Saved Connections"]
    )

    with upload_tab:

        st.subheader("1. Choose a source")

        source_type = st.selectbox(
            "Source type",
            [
                "CSV",
                "Excel",
                "JSON",
                "SQLite",
                "REST API",
            ],
        )

        if source_type in ["CSV", "Excel", "JSON"]:

            extensions = {
                "CSV": ["csv"],
                "Excel": ["xlsx", "xls"],
                "JSON": ["json"],
            }

            uploaded_file = st.file_uploader(
                "Upload file",
                type=extensions[source_type],
            )

            if uploaded_file:

                connection_name = st.text_input(
                    "Connection name",
                    value=uploaded_file.name,
                )

                if st.button(
                    "Upload & Connect",
                    type="primary",
                ):

                    try:
                        response = requests.post(
                            f"{API_URL}/data-import/upload",
                            headers={
                                "Authorization":
                                    f"Bearer "
                                    f"{st.session_state.token}"
                            },
                            files={
                                "file": (
                                    uploaded_file.name,
                                    uploaded_file.getvalue(),
                                    uploaded_file.type,
                                )
                            },
                            data={
                                "name": connection_name,
                            },
                            timeout=60,
                        )

                        if response.status_code >= 400:
                            st.error(
                                f"Upload failed: "
                                f"{response.text}"
                            )

                        else:

                            data = response.json()

                            st.session_state[
                                "active_connection_id"
                            ] = data["connection_id"]

                            st.success(
                                "Data source connected successfully."
                            )

                    except requests.RequestException as exc:

                        st.error(
                            f"Unable to connect to ChainPulse API: {exc}"
                        )

        elif source_type == "SQLite":

            sqlite_path = st.text_input(
                "Database path",
                placeholder="storage/example.db",
            )

            sqlite_table = st.text_input(
                "Table name",
                placeholder="sales",
            )

            sqlite_name = st.text_input(
                "Connection name",
                value="SQLite Connection",
            )

            if st.button(
                "Connect SQLite",
                type="primary",
            ):

                result = api_request(
                    "POST",
                    "/data-connections",
                    json={
                        "name": sqlite_name,
                        "connector_type": "sqlite",
                        "config": {
                            "path": sqlite_path,
                            "table": sqlite_table,
                        },
                        "secrets": {},
                    },
                )

                if result:
                    st.session_state[
                        "active_connection_id"
                    ] = result["id"]

                    st.success(
                        "SQLite connection created."
                    )

        elif source_type == "REST API":

            rest_name = st.text_input(
                "Connection name",
                value="REST API Connection",
            )

            rest_url = st.text_input(
                "API URL",
                placeholder="https://api.example.com/data",
            )

            rest_method = st.selectbox(
                "HTTP Method",
                ["GET", "POST"],
            )

            if st.button(
                "Connect REST API",
                type="primary",
            ):

                result = api_request(
                    "POST",
                    "/data-connections",
                    json={
                        "name": rest_name,
                        "connector_type": "rest",
                        "config": {
                            "url": rest_url,
                            "method": rest_method,
                        },
                        "secrets": {},
                    },
                )

                if result:
                    st.session_state[
                        "active_connection_id"
                    ] = result["id"]

                    st.success(
                        "REST API connection created."
                    )

    active_connection_id = st.session_state.get(
        "active_connection_id"
    )

    if active_connection_id:

        st.divider()

        st.subheader("2. Preview")

        preview = api_request(
            "POST",
            "/ingestion/preview",
            json={
                "connection_id": active_connection_id,
                "limit": 100,
            },
        )

        if preview:

            st.metric(
                "Rows",
                preview.get(
                    "total_rows",
                    0,
                ),
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

            st.subheader("3. Automatic Mapping")

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

                mapping_result = api_request(
                    "POST",
                    "/ingestion/auto-map",
                    json={
                        "connection_id":
                            active_connection_id,
                        "target":
                            target,
                        "limit":
                            100,
                    },
                )

                if mapping_result:
                    st.session_state[
                        "mapping_result"
                    ] = mapping_result

        mapping_result = st.session_state.get(
            "mapping_result"
        )

        if mapping_result:

            st.subheader(
                "4. Review Mapping"
            )

            suggestions = mapping_result.get(
                "suggestions",
                {},
            )

            mapping = {}

            for source_column, info in suggestions.items():

                destination = st.text_input(
                    source_column,
                    value=info["target"],
                    key=(
                        "map_"
                        + source_column
                    ),
                )

                mapping[
                    source_column
                ] = destination

                st.caption(
                    f"Confidence: "
                    f"{info.get('confidence', 0)}%"
                )

            missing = mapping_result.get(
                "missing_required",
                [],
            )

            if missing:
                st.warning(
                    "Missing required fields: "
                    + ", ".join(missing)
                )

            required_fields = {
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

                validation_mapping = {
                    destination: source
                    for source, destination
                    in mapping.items()
                }

                validation = api_request(
                    "POST",
                    "/ingestion/validate",
                    json={
                        "connection_id":
                            active_connection_id,
                        "mapping":
                            validation_mapping,
                        "required_fields":
                            required_fields,
                    },
                )

                if validation:
                    st.session_state[
                        "validation_result"
                    ] = validation

        validation_result = st.session_state.get(
            "validation_result"
        )

        if validation_result:

            st.subheader("5. Data Quality")

            c1, c2, c3 = st.columns(3)

            c1.metric(
                "Valid Rows",
                validation_result.get(
                    "valid_rows",
                    0,
                ),
            )

            c2.metric(
                "Invalid Rows",
                validation_result.get(
                    "invalid_rows",
                    0,
                ),
            )

            c3.metric(
                "Status",
                "VALID"
                if validation_result.get(
                    "valid"
                )
                else "CHECK DATA",
            )

            issues = validation_result.get(
                "issues",
                [],
            )

            if issues:
                st.dataframe(
                    pd.DataFrame(issues),
                    use_container_width=True,
                    hide_index=True,
                )

            if validation_result.get(
                "valid_rows",
                0,
            ) > 0:

                if st.button(
                    "Import into ChainPulse",
                    type="primary",
                ):

                    final_mapping = {
                        destination: source
                        for source, destination
                        in mapping.items()
                    }

                    result = api_request(
                        "POST",
                        "/ingestion/import",
                        json={
                            "connection_id":
                                active_connection_id,
                            "mapping":
                                final_mapping,
                            "required_fields":
                                required_fields,
                            "target":
                                target,
                        },
                    )

                    if result:

                        st.success(
                            "Import completed: "
                            f"{result.get('rows_imported', 0)} "
                            "rows imported."
                        )

                        if result.get("errors"):
                            st.warning(
                                "Some rows require attention."
                            )

                            st.dataframe(
                                pd.DataFrame(
                                    result["errors"]
                                ),
                                use_container_width=True,
                                hide_index=True,
                            )

    with saved_tab:

        st.subheader("Saved Connections")

        connections = api_request(
            "GET",
            "/data-connections",
        )

        if connections:

            for connection in connections:

                with st.container(border=True):

                    c1, c2, c3 = st.columns(
                        [4, 2, 1]
                    )

                    c1.write(
                        f"**{connection['name']}**"
                    )

                    c2.write(
                        connection[
                            "connector_type"
                        ].upper()
                    )

                    if c3.button(
                        "Use",
                        key=(
                            "connection_"
                            f"{connection['id']}"
                        ),
                    ):

                        st.session_state[
                            "active_connection_id"
                        ] = connection["id"]

                        st.rerun()


# ============================================================

# ============================================================
# REPORT BUILDER
# ============================================================

elif page == "Reports":

    st.title("📄 Report Builder")

    st.caption(
        "Build a professional report from your ChainPulse data."
    )

    # --------------------------------------------------------
    # Report configuration
    # --------------------------------------------------------

    st.subheader("Report Settings")

    report_title = st.text_input(
        "Report title",
        value="ChainPulse Supply Chain Report",
    )

    output_format = st.radio(
        "Format",
        ["PDF", "Word"],
        horizontal=True,
    )

    st.subheader("Include")

    c1, c2, c3 = st.columns(3)

    include_dashboard = c1.checkbox(
        "Dashboard",
        value=True,
    )

    include_products = c1.checkbox(
        "Products",
        value=True,
    )

    include_risk = c2.checkbox(
        "Risk intelligence",
        value=True,
    )

    include_alerts = c2.checkbox(
        "Alerts",
        value=True,
    )

    include_recommendations = c3.checkbox(
        "Recommendations",
        value=True,
    )

    # --------------------------------------------------------
    # Live preview
    # --------------------------------------------------------

    st.divider()

    st.subheader("Live Preview")

    summary = api_request(
        "GET",
        "/dashboard/summary",
    )

    if summary:

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

        if include_risk:

            st.write(
                "**Risk Level:** "
                + str(
                    summary.get(
                        "overall_risk_level",
                        "unknown",
                    )
                ).upper()
            )

        if include_alerts:

            alerts = summary.get(
                "alerts",
                [],
            )

            if alerts:
                st.subheader("Alerts")

                for alert in alerts:
                    st.warning(alert)

        if include_recommendations:

            recommendations = summary.get(
                "recommendations",
                [],
            )

            if recommendations:
                st.subheader("Recommendations")

                for recommendation in recommendations:
                    st.info(recommendation)

    else:

        st.warning(
            "Unable to load dashboard data."
        )

    # --------------------------------------------------------
    # Generate
    # --------------------------------------------------------

    st.divider()

    if st.button(
        "🚀 Generate Report",
        type="primary",
        use_container_width=True,
    ):

        payload = {
            "title": report_title,
            "format": (
                "pdf"
                if output_format == "PDF"
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

        try:

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

            if response.status_code != 200:

                st.error(
                    "Report generation failed."
                )

                st.code(
                    response.text,
                    language="json",
                )

            else:

                extension = (
                    "pdf"
                    if output_format == "PDF"
                    else "docx"
                )

                filename = (
                    f"{report_title.strip() or 'chainpulse_report'}"
                    f".{extension}"
                )

                mime_type = (
                    "application/pdf"
                    if output_format == "PDF"
                    else (
                        "application/vnd.openxmlformats-"
                        "officedocument.wordprocessingml.document"
                    )
                )

                st.success(
                    "Report generated successfully."
                )

                st.download_button(
                    label="⬇️ Download Report",
                    data=response.content,
                    file_name=filename,
                    mime=mime_type,
                    use_container_width=True,
                )

        except requests.RequestException as exc:

            st.error(
                "Unable to connect to ChainPulse API."
            )

            st.caption(str(exc))


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


