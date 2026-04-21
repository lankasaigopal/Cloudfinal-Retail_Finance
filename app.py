import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

st.set_page_config(
    page_title="Retail Financial Dashboard",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ---------- Custom CSS ----------
st.markdown("""
<style>
    .stApp {
        background-color: #dfeaf7;
    }

    section[data-testid="stSidebar"] {
        background: #0b1f4d;
        border-right: 1px solid #122b66;
    }

    section[data-testid="stSidebar"] * {
        color: white !important;
    }

    .login-brand {
        text-align: center;
        font-size: 2.2rem;
        font-weight: 700;
        color: #111827;
        margin-top: 1rem;
        margin-bottom: 1.8rem;
    }

    .hero-wrap {
        text-align: center;
        padding: 10px 20px 10px 20px;
    }

    .hero-title {
        font-size: 4.2rem;
        font-weight: 400;
        color: #111827;
        line-height: 1.05;
        margin-bottom: 0.2rem;
    }

    .hero-title strong {
        font-weight: 800;
        display: block;
    }

    .hero-subtitle {
        font-size: 1.3rem;
        color: #374151;
        margin-top: 1rem;
        margin-bottom: 2rem;
    }

    .card-title {
        font-size: 2rem;
        font-weight: 700;
        color: #111827;
        margin-bottom: 1rem;
    }
    .login-box {
        background: transparent;
        border-radius: 0;
        padding: 0;
        box-shadow: none;
    }
    .login-help {
        background: #eef4ff;
        border-left: 6px solid #2563eb;
        padding: 12px 14px;
        border-radius: 10px;
        margin-top: 14px;
        margin-bottom: 12px;
        color: #1e3a8a;
        font-weight: 500;
    }
    div[data-testid="stForm"] {
        background: #ffffff;
        border-radius: 22px;
        padding: 28px 28px 18px 28px;
        box-shadow: inset 0 0 0 1px #e5e7eb;
    }

    .login-title-center {
        text-align: center;
        font-size: 2rem;
        font-weight: 700;
        color: #111827;
        margin-bottom: 1rem;
    }
    .inner-page {
        background: #0b1f4d;
        padding: 20px 24px 30px 24px;
        border-radius: 18px;
        color: white;
        margin-bottom: 20px;
    }

    .inner-page h1,
    .inner-page h2,
    .inner-page h3,
    .inner-page p,
    .inner-page div {
        color: white !important;
    }

    div[data-testid="metric-container"] {
        background: white;
        border: 1px solid #dbe4f0;
        padding: 16px;
        border-radius: 18px;
        box-shadow: 0 4px 14px rgba(0,0,0,0.06);
    }

    .info-card {
        background: #ffffff;
        padding: 14px 18px;
        border-radius: 14px;
        box-shadow: 0 3px 10px rgba(0,0,0,0.05);
        border-left: 6px solid #0b1f4d;
        margin-bottom: 1rem;
        color: #1f2937;
    }

    .stButton > button {
        background: #111827;
        color: white;
        border: none;
        border-radius: 10px;
        padding: 0.65rem 1.2rem;
        font-weight: 600;
    }

    .stButton > button:hover {
        background: #000000;
        color: white;
    }

    div[data-testid="stDataFrame"] {
        background: white;
        border-radius: 14px;
        padding: 8px;
        box-shadow: 0 3px 10px rgba(0,0,0,0.06);
    }
</style>
""", unsafe_allow_html=True)

# ---------- Load Data ----------
@st.cache_data
def load_data():
    data = pd.read_csv("merged_retail_data.csv")
    clv_data = pd.read_csv("household_clv.csv")
    churn_data = pd.read_csv("churn_data.csv")

    data.columns = data.columns.str.strip().str.lower().str.replace(" ", "_")
    clv_data.columns = clv_data.columns.str.strip().str.lower().str.replace(" ", "_")
    churn_data.columns = churn_data.columns.str.strip().str.lower().str.replace(" ", "_")

    if "date" in data.columns:
        data["date"] = pd.to_datetime(data["date"], errors="coerce")

    # Robust loyalty fix
    if "loyalty" not in data.columns:
        try:
            households = pd.read_csv("households.csv")
            households.columns = households.columns.str.strip().str.lower().str.replace(" ", "_")

            possible_loyalty_cols = ["loyalty", "loyalty", "loyalty_status"]
            loyalty_col = None
            for col in possible_loyalty_cols:
                if col in households.columns:
                    loyalty_col = col
                    break

            if "hshd_num" in households.columns and loyalty_col is not None:
                loyalty_lookup = households[["hshd_num", loyalty_col]].drop_duplicates()
                loyalty_lookup = loyalty_lookup.rename(columns={loyalty_col: "loyalty"})
                data = data.merge(loyalty_lookup, on="hshd_num", how="left")

                if "loyalty" in data.columns:
                    data["loyalty"] = data["loyalty"].fillna("Unknown").astype(str)
        except Exception:
            pass
    else:
        data["loyalty"] = data["loyalty"].fillna("Unknown").astype(str)

    return data, clv_data, churn_data

data, clv_data, churn_data = load_data()

# ---------- Session State ----------
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

# ---------- Login ----------
def login_page():
    st.markdown("<div class='login-brand'>Retail Insight Dashboard</div>", unsafe_allow_html=True)

    st.markdown("""
    <div class="hero-wrap">
        <div class="hero-title">Retail insights,<strong>built for smarter decisions</strong></div>
        <div class="hero-subtitle">Analyze households, track sales patterns, and explore customer behavior with clarity and confidence.</div>
    </div>
    """, unsafe_allow_html=True)

    left, center, right = st.columns([1.2, 3.2, 1.2])

    with center:
        st.markdown("<div class='login-box'>", unsafe_allow_html=True)
        st.markdown("<div class='card-title' style='text-align:center;'>Login</div>", unsafe_allow_html=True)

        with st.form("login_form", clear_on_submit=False):
            username = st.text_input("Username", placeholder="Enter username")
            password = st.text_input("Password", type="password", placeholder="Enter password")
            email = st.text_input("Email Address", placeholder="Enter email address")

            st.markdown(
                "<div class='login-help'>Login credentials: Username = <b>lankasp</b> | Password = <b>cloudfinal</b> | Email = <b>lankasp@gmail.com</b></div>",
                unsafe_allow_html=True
            )

            login_clicked = st.form_submit_button("Login")

            if login_clicked:
                if (
                    username == "lankasp"
                    and password == "cloudfinal"
                    and email.strip().lower() == "lankasp@gmail.com"
                ):
                    st.session_state.logged_in = True
                    st.success("Login successful.")
                    st.rerun()
                elif email.strip().lower() != "lankasp@gmail.com":
                    st.error("Please use the authorized email: lankasp@gmail.com")
                else:
                    st.error("Invalid username or password.")

        st.markdown("</div>", unsafe_allow_html=True)

if not st.session_state.logged_in:
    login_page()
    st.stop()

# ---------- Sidebar ----------
st.sidebar.markdown("## 📌 Navigation")
st.sidebar.markdown("Use the menu below to explore the retail dashboard.")

page = st.sidebar.radio(
    "Go to",
    ["Dashboard", "Household Search", "Sample Data Pull", "CLV Analysis", "Churn Analysis"]
)

st.sidebar.markdown("---")
st.sidebar.markdown("### 🔑 Login Credentials")
st.sidebar.write("**Username:** lankasp")
st.sidebar.write("**Password:** cloudfinal")
st.sidebar.write("**Email:** lankasp@gmail.com")

if st.sidebar.button("Logout"):
    st.session_state.logged_in = False
    st.rerun()

# ---------- Dashboard ----------
if page == "Dashboard":
    st.markdown("<div class='inner-page'><h1>Retail Financial Dashboard</h1><p>Interactive overview of sales performance, customer activity, and loyalty behavior.</p></div>", unsafe_allow_html=True)

    total_sales = data["spend"].sum()
    total_units = data["units"].sum()
    total_households = data["hshd_num"].nunique()
    total_products = data["product_num"].nunique()

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("💰 Total Sales", f"${total_sales:,.2f}")
    col2.metric("📦 Total Units", f"{total_units:,.0f}")
    col3.metric("👥 Total Households", f"{total_households}")
    col4.metric("🛒 Total Products", f"{total_products}")

    st.subheader("Top 10 Departments by Sales")
    st.markdown("<div class='info-card'>This chart highlights the top departments contributing the most to total sales.</div>", unsafe_allow_html=True)

    sales_by_department = data.groupby("department")["spend"].sum().sort_values(ascending=False).head(10)

    fig, ax = plt.subplots(figsize=(10, 5))
    sales_by_department.plot(kind="bar", ax=ax)
    ax.set_title("Top 10 Departments by Sales")
    ax.set_xlabel("Department")
    ax.set_ylabel("Total Sales")
    plt.xticks(rotation=45)
    plt.tight_layout()
    st.pyplot(fig)

    st.subheader("Monthly Sales Trend")
    st.markdown("<div class='info-card'>This trend shows how retail spending changes over time across months.</div>", unsafe_allow_html=True)

    monthly_sales = data.groupby(data["date"].dt.to_period("M"))["spend"].sum()
    monthly_sales.index = monthly_sales.index.astype(str)

    fig, ax = plt.subplots(figsize=(10, 5))
    monthly_sales.plot(kind="line", marker="o", ax=ax)
    ax.set_title("Monthly Sales Trend")
    ax.set_xlabel("Month")
    ax.set_ylabel("Total Sales")
    plt.xticks(rotation=45)
    plt.tight_layout()
    st.pyplot(fig)

    st.subheader("Spending by Loyalty Flag")

    if "loyalty" in data.columns:
        loyalty_plot_data = data.copy()
        loyalty_plot_data["loyalty"] = loyalty_plot_data["loyalty"].fillna("Unknown").astype(str)

        loyalty_sales = loyalty_plot_data.groupby("loyalty", dropna=False)["spend"].sum()

        if not loyalty_sales.empty:
            fig, ax = plt.subplots(figsize=(6, 4))
            loyalty_sales.plot(kind="bar", ax=ax)
            ax.set_title("Spending by Loyalty Flag")
            ax.set_xlabel("Loyalty Flag")
            ax.set_ylabel("Total Sales")
            plt.tight_layout()
            st.pyplot(fig)
        else:
            st.warning("Loyalty flag values are empty.")
    else:
        st.warning("Loyalty flag data is not available in the current files.")
# ---------- Household Search ----------
elif page == "Household Search":
    st.markdown("<div class='inner-page'><h1>Household Search</h1><p>Search customer purchase history by household number.</p></div>", unsafe_allow_html=True)

    st.markdown("<div class='info-card'>Enter a household number to retrieve transaction-level purchase records sorted by household, basket, date, product, department, and commodity.</div>", unsafe_allow_html=True)

    hshd_id = st.number_input("Enter Household Number", min_value=1, step=1)

    if st.button("Search Household"):
        result = data[data["hshd_num"] == hshd_id].copy()

        if result.empty:
            st.warning("No data found for this household.")
        else:
            result = result.sort_values(
                by=["hshd_num", "basket_num", "date", "product_num", "department", "commodity"]
            )
            st.success(f"Showing results for Household {hshd_id}")
            st.dataframe(result, use_container_width=True)

# ---------- Sample Data Pull ----------
elif page == "Sample Data Pull":
    st.markdown("<div class='inner-page'><h1>Sample Data Pull for Household #10</h1><p>Joined data view for the required sample household.</p></div>", unsafe_allow_html=True)

    st.markdown("<div class='info-card'>This page displays the required joined sample data pull for household number 10 using the Households, Transactions, and Products datasets.</div>", unsafe_allow_html=True)

    sample = data[data["hshd_num"] == 10].copy()

    if sample.empty:
        st.warning("No data found for household 10.")
    else:
        sample = sample.sort_values(
            by=["hshd_num", "basket_num", "date", "product_num", "department", "commodity"]
        )
        st.dataframe(sample, use_container_width=True)

# ---------- CLV Analysis ----------
elif page == "CLV Analysis":
    st.markdown("<div class='inner-page'><h1>Customer Lifetime Value (CLV) Analysis</h1><p>Top households ranked by total spend.</p></div>", unsafe_allow_html=True)

    st.markdown("<div class='info-card'>Customer Lifetime Value (CLV) helps identify households with the highest long-term revenue contribution and supports better prioritization strategies.</div>", unsafe_allow_html=True)

    top_clv = clv_data.sort_values("total_spend", ascending=False).head(10)
    st.dataframe(top_clv, use_container_width=True)

    fig, ax = plt.subplots(figsize=(10, 5))
    ax.bar(top_clv["hshd_num"].astype(str), top_clv["total_spend"])
    ax.set_title("Top 10 Households by Total Spend")
    ax.set_xlabel("Household Number")
    ax.set_ylabel("Total Spend")
    plt.xticks(rotation=45)
    plt.tight_layout()
    st.pyplot(fig)

# ---------- Churn Analysis ----------
elif page == "Churn Analysis":
    st.markdown("<div class='inner-page'><h1>Churn Risk Analysis</h1><p>Identify customers at higher risk of disengagement.</p></div>", unsafe_allow_html=True)

    st.markdown("<div class='info-card'>This view helps identify households with higher churn risk based on shopping activity and basket behavior.</div>", unsafe_allow_html=True)

    churn_counts = churn_data["churn_risk"].value_counts().sort_index()

    fig, ax = plt.subplots(figsize=(6, 4))
    churn_counts.plot(kind="bar", ax=ax)
    ax.set_title("Churn Risk Distribution")
    ax.set_xlabel("Churn Risk (0 = Low, 1 = High)")
    ax.set_ylabel("Number of Households")
    plt.tight_layout()
    st.pyplot(fig)

    st.subheader("Households with High Churn Risk")
    high_churn = churn_data[churn_data["churn_risk"] == 1]
    st.dataframe(high_churn.head(20), use_container_width=True)