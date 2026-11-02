import os
import json
import sqlite3
import time
from pathlib import Path

import pandas as pd
import plotly.express as px
import sqlparse
import streamlit as st

from dotenv import load_dotenv
from openai import OpenAI


# =====================================================
# 1. CONFIGURATION
# =====================================================

BASE_DIR = Path(__file__).resolve().parent
DB_PATH = BASE_DIR / "ecommerce.db"

load_dotenv(BASE_DIR / ".env")

API_KEY = os.getenv("OPENAI_API_KEY")
MODEL = os.getenv("OPENAI_MODEL", "gpt-6-luna")

st.set_page_config(
    page_title="AI SQL Assistant",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)


# =====================================================
# 2. LANGUAGE SYSTEM
# =====================================================

LANGUAGES = {
    "English": "🇬🇧 English",
    "ქართული": "🇬🇪 ქართული"
}

TRANSLATIONS = {
    "English": {
        "api_error": "OPENAI_API_KEY was not found in the .env file.",
        "database_error": "Database file ecommerce.db was not found.",
        "language": "🌐 Language",
        "database": "Database",
        "connected": "Database connected",
        "database_explorer": "Database Explorer",
        "explorer_caption": "Explore database tables, records, and columns.",
        "tables_count": "The database contains {count} tables.",
        "records": "records",
        "columns_types": "Columns and Data Types",
        "column_name": "Column Name",
        "data_type": "Data Type",
        "primary_key": "Primary Key",
        "yes": "Yes",
        "no": "No",
        "example_questions": "Example Questions",
        "title": "AI Data Analyst",
        "subtitle": "Ask questions. Generate SQL. Discover insights.",
        "total_customers": "Total Customers",
        "total_orders": "Total Orders",
        "total_products": "Total Products",
        "ask_database": "Ask your database",
        "question_label": "Enter your question in English or Georgian:",
        "placeholder": "Example: Which month had the highest number of orders?",
        "analyze": "✨ Analyze Database",
        "enter_question": "Please enter a question first.",
        "generating_sql": "🤖 AI is generating SQL...",
        "generated_sql": "🧠 Generated SQL",
        "fetching_data": "🔍 Retrieving data...",
        "analysis": "📝 AI Text Analysis",
        "analyzing": "AI is analyzing the data...",
        "summary": "📌 Analysis Summary",
        "visualization": "📊 Automatic Data Visualization",
        "choosing_chart": "AI is selecting the appropriate chart...",
        "selected_chart": "Selected chart:",
        "no_chart": "No suitable chart could be selected for these results.",
        "data_table": "📋 Data Table",
        "no_data": "No data found.",
        "showing": "Showing {count} records (maximum 500).",
        "download": "⬇️ Download CSV",
        "error": "Error: {error}",
        "error_help": "Check your question, database, and API settings.",
        "single_query": "Only one SQL query is allowed.",
        "empty_sql": "SQL query is empty.",
        "select_only": "Only SELECT queries are allowed.",
        "no_data_analysis": "No data was found. Try rephrasing your question.",
        "customers": "Customers",
        "orders": "Orders",
        "order_items": "Order Items",
        "products": "Products",
        "sellers": "Sellers",
        "order_payments": "Payments",
        "order_reviews": "Reviews",
        "geolocation": "Geolocation",
        "category_translation": "Category Translations",
        "customers_description": "Customer information, unique IDs, and locations",
        "orders_description": "Order statuses, creation dates, and delivery dates",
        "order_items_description": "Products in each order, prices, and shipping costs",
        "products_description": "Product categories, dimensions, and weights",
        "sellers_description": "Seller unique IDs and locations",
        "order_payments_description": "Payment methods, installments, and payment amounts",
        "order_reviews_description": "Customer reviews, comments, and review dates",
        "geolocation_description": "Geographic coordinates and postal codes",
        "category_translation_description": "Portuguese and English product category names",
        "default_description": "Database table",
        "chart_none": "No suitable chart could be selected."
    },
    "ქართული": {
        "api_error": "OPENAI_API_KEY ვერ მოიძებნა .env ფაილში.",
        "database_error": "ecommerce.db ფაილი ვერ მოიძებნა.",
        "language": "🌐 ენა",
        "database": "მონაცემთა ბაზა",
        "connected": "მონაცემთა ბაზასთან კავშირი დამყარებულია",
        "database_explorer": "მონაცემთა ბაზის დათვალიერება",
        "explorer_caption": "დაათვალიერე ცხრილები, ჩანაწერები და სვეტები.",
        "tables_count": "მონაცემთა ბაზაში არის {count} ცხრილი.",
        "records": "ჩანაწერი",
        "columns_types": "სვეტები და მონაცემთა ტიპები",
        "column_name": "სვეტის სახელი",
        "data_type": "მონაცემთა ტიპი",
        "primary_key": "Primary Key",
        "yes": "დიახ",
        "no": "არა",
        "example_questions": "მაგალითი შეკითხვები",
        "title": "AI მონაცემთა ანალიტიკოსი",
        "subtitle": "დასვი შეკითხვა. შექმენი SQL. აღმოაჩინე მნიშვნელოვანი მონაცემები.",
        "total_customers": "მომხმარებლების რაოდენობა",
        "total_orders": "შეკვეთების რაოდენობა",
        "total_products": "პროდუქტების რაოდენობა",
        "ask_database": "დაუსვი შეკითხვა მონაცემთა ბაზას",
        "question_label": "შეიყვანე შეკითხვა ქართულად ან ინგლისურად:",
        "placeholder": "მაგალითად: რომელ თვეში დაფიქსირდა ყველაზე მეტი შეკვეთა?",
        "analyze": "✨ მონაცემების ანალიზი",
        "enter_question": "გთხოვ, ჯერ შეიყვანე შეკითხვა.",
        "generating_sql": "🤖 AI ქმნის SQL მოთხოვნას...",
        "generated_sql": "🧠 გენერირებული SQL",
        "fetching_data": "🔍 მონაცემების მოძიება...",
        "analysis": "📝 AI-ის ტექსტური ანალიზი",
        "analyzing": "AI აანალიზებს მონაცემებს...",
        "summary": "📌 ანალიზის შეჯამება",
        "visualization": "📊 მონაცემების ავტომატური ვიზუალიზაცია",
        "choosing_chart": "AI არჩევს შესაბამის დიაგრამას...",
        "selected_chart": "არჩეული დიაგრამა:",
        "no_chart": "ამ შედეგებისთვის შესაბამისი დიაგრამა ვერ შეირჩა.",
        "data_table": "📋 მონაცემების ცხრილი",
        "no_data": "მონაცემები ვერ მოიძებნა.",
        "showing": "ნაჩვენებია {count} ჩანაწერი (მაქსიმუმ 500).",
        "download": "⬇️ CSV ფაილის ჩამოტვირთვა",
        "error": "შეცდომა: {error}",
        "error_help": "შეამოწმე შეკითხვა, მონაცემთა ბაზა და API პარამეტრები.",
        "single_query": "დაშვებულია მხოლოდ ერთი SQL მოთხოვნა.",
        "empty_sql": "SQL მოთხოვნა ცარიელია.",
        "select_only": "დაშვებულია მხოლოდ SELECT მოთხოვნები.",
        "no_data_analysis": "მონაცემები ვერ მოიძებნა. სცადე შეკითხვის სხვაგვარად ფორმულირება.",
        "customers": "მომხმარებლები",
        "orders": "შეკვეთები",
        "order_items": "შეკვეთის პროდუქტები",
        "products": "პროდუქტები",
        "sellers": "გამყიდველები",
        "order_payments": "გადახდები",
        "order_reviews": "შეფასებები",
        "geolocation": "გეოლოკაცია",
        "category_translation": "კატეგორიების თარგმანი",
        "customers_description": "მომხმარებლების ინფორმაცია, უნიკალური ID და მდებარეობა",
        "orders_description": "შეკვეთების სტატუსი, შექმნისა და მიწოდების თარიღები",
        "order_items_description": "თითოეულ შეკვეთაში არსებული პროდუქტები, ფასები და ტრანსპორტირების ღირებულება",
        "products_description": "პროდუქტების კატეგორიები, ზომები და წონა",
        "sellers_description": "გამყიდველების უნიკალური ID და მდებარეობა",
        "order_payments_description": "გადახდის მეთოდები, განვადება და გადახდილი თანხები",
        "order_reviews_description": "მომხმარებლების შეფასებები, კომენტარები და შეფასების თარიღები",
        "geolocation_description": "გეოგრაფიული კოორდინატები და საფოსტო ინდექსები",
        "category_translation_description": "პროდუქტის კატეგორიების პორტუგალიური და ინგლისური სახელები",
        "default_description": "მონაცემთა ცხრილი",
        "chart_none": "ამ შედეგებისთვის შესაბამისი დიაგრამა ვერ შეირჩა."
    }
}

if "language" not in st.session_state:
    st.session_state.language = "English"


def t(key, **kwargs):
    text = TRANSLATIONS[st.session_state.language].get(
        key,
        TRANSLATIONS["English"].get(key, key)
    )
    return text.format(**kwargs)


# Show configuration errors in the currently selected language.
if not API_KEY:
    st.error(t("api_error"))
    st.stop()

if not DB_PATH.exists():
    st.error(t("database_error"))
    st.stop()

client = OpenAI(api_key=API_KEY)


# =====================================================
# 3. DESIGN
# =====================================================

st.markdown("""
<style>
.stApp {
    background-color: #0b1120;
    color: #e5e7eb;
}
[data-testid="stSidebar"] {
    background-color: #111827;
    border-right: 1px solid #263247;
}
.main-title {
    font-size: 36px;
    font-weight: 800;
    color: #f8fafc;
    margin-bottom: 5px;
}
.subtitle {
    color: #94a3b8;
    font-size: 15px;
    margin-bottom: 25px;
}
.metric-card {
    background: #151f32;
    border: 1px solid #263750;
    padding: 20px;
    border-radius: 14px;
    min-height: 110px;
}
.metric-label {
    color: #94a3b8;
    font-size: 13px;
}
.metric-value {
    color: #f8fafc;
    font-size: 27px;
    font-weight: 700;
    margin-top: 8px;
}
.answer-card {
    background: #151f32;
    border: 1px solid #263750;
    border-radius: 14px;
    padding: 20px;
    margin-top: 10px;
    margin-bottom: 15px;
}
.answer-title {
    color: #60a5fa;
    font-size: 18px;
    font-weight: 700;
}
div.stButton > button {
    background-color: #2563eb;
    color: white;
    border: none;
    border-radius: 9px;
    font-weight: 600;
    padding: 10px 20px;
}
div.stButton > button:hover {
    background-color: #1d4ed8;
    color: white;
}
[data-testid="stDataFrame"] {
    border: 1px solid #263247;
    border-radius: 12px;
}
</style>
""", unsafe_allow_html=True)


# =====================================================
# 4. DATABASE INFORMATION
# =====================================================

TABLE_INFO = {
    "customers": {"icon": "👥"},
    "orders": {"icon": "📦"},
    "order_items": {"icon": "🛒"},
    "products": {"icon": "🏷️"},
    "sellers": {"icon": "🏪"},
    "order_payments": {"icon": "💳"},
    "order_reviews": {"icon": "⭐"},
    "geolocation": {"icon": "📍"},
    "category_translation": {"icon": "🌐"}
}


# =====================================================
# 5. DATABASE FUNCTIONS
# =====================================================

def get_connection():
    return sqlite3.connect(
        f"file:{DB_PATH.as_posix()}?mode=ro",
        uri=True,
        timeout=10
    )


def get_schema():
    conn = get_connection()
    cursor = conn.cursor()

    try:
        cursor.execute("""
            SELECT name
            FROM sqlite_master
            WHERE type = 'table'
            AND name NOT LIKE 'sqlite_%'
        """)

        tables = cursor.fetchall()
        schema = {}

        for (table,) in tables:
            cursor.execute(f'PRAGMA table_info("{table}")')
            columns = cursor.fetchall()

            schema[table] = [
                {
                    "name": column[1],
                    "type": column[2] or "UNKNOWN",
                    "primary_key": bool(column[5])
                }
                for column in columns
            ]

        return schema
    finally:
        conn.close()


def get_table_count(table):
    conn = get_connection()
    try:
        cursor = conn.cursor()
        # Table names originate from the database schema.
        cursor.execute(f'SELECT COUNT(*) FROM "{table}"')
        return cursor.fetchone()[0]
    finally:
        conn.close()


# =====================================================
# 6. DATABASE EXPLORER
# =====================================================

def display_database_explorer(schema):
    st.markdown(f"### 🗄️ {t('database_explorer')}")
    st.caption(t("explorer_caption"))
    st.markdown(f"**{t('tables_count', count=len(schema))}**")

    for table, columns in schema.items():
        count = get_table_count(table)
        name = t(table)
        description = t(f"{table}_description")
        icon = TABLE_INFO.get(table, {"icon": "📁"})["icon"]

        with st.expander(
            f"{icon} {name} · {count:,} {t('records')}"
        ):
            st.markdown(f"**{name}**")
            st.caption(description)
            st.divider()
            st.markdown(f"**{t('columns_types')}**")

            columns_df = pd.DataFrame([
                {
                    t("column_name"): column["name"],
                    t("data_type"): column["type"],
                    t("primary_key"): (
                        t("yes") if column["primary_key"] else t("no")
                    )
                }
                for column in columns
            ])

            st.dataframe(
                columns_df,
                use_container_width=True,
                hide_index=True
            )


# =====================================================
# 7. SQL VALIDATION AND EXECUTION
# =====================================================

def execute_query(sql):
    statements = sqlparse.split(sql)

    if len(statements) != 1:
        raise ValueError(t("single_query"))

    parsed = sqlparse.parse(sql)

    if not parsed:
        raise ValueError(t("empty_sql"))

    if parsed[0].get_type() != "SELECT":
        raise ValueError(t("select_only"))

    allowed_actions = {
        sqlite3.SQLITE_SELECT,
        sqlite3.SQLITE_READ,
        sqlite3.SQLITE_FUNCTION,
        getattr(sqlite3, "SQLITE_RECURSIVE", -1)
    }

    def authorize(action, arg1, arg2, db_name, trigger):
        if action in allowed_actions:
            return sqlite3.SQLITE_OK
        return sqlite3.SQLITE_DENY

    conn = get_connection()
    conn.set_authorizer(authorize)

    deadline = time.monotonic() + 5
    conn.set_progress_handler(
        lambda: 1 if time.monotonic() > deadline else 0,
        1000
    )

    try:
        safe_sql = sql.strip().rstrip(";")
        final_sql = (
            f"SELECT * FROM ({safe_sql}) AS ai_result LIMIT 500"
        )

        df = pd.read_sql_query(final_sql, conn)
        return df
    finally:
        conn.close()


# =====================================================
# 8. AI SQL GENERATION
# =====================================================

def generate_sql(question, schema):
    prompt = f"""
You are an expert SQL analyst working with SQLite.

The user can ask questions in Georgian or English.

DATABASE SCHEMA:
{json.dumps(schema, ensure_ascii=False, indent=2)}

RULES:
1. Generate only valid SQLite SELECT statements.
2. Never generate INSERT, UPDATE, DELETE, DROP,
   ALTER, CREATE, ATTACH or DETACH.
3. Use only existing tables and columns.
4. Use appropriate JOINs when necessary.
5. Use meaningful aliases.
6. For non-aggregated queries, use LIMIT 100.
7. For aggregated queries, use a reasonable number of rows.
8. Never invent column names.
9. Return only SQL code without Markdown.

USER QUESTION:
{question}
"""

    response = client.responses.create(
        model=MODEL,
        instructions=(
            "Generate safe, read-only SQLite SQL. "
            "Return one SELECT statement only."
        ),
        input=prompt,
        max_output_tokens=1200
    )

    sql = response.output_text.strip()
    sql = sql.replace("```sql", "")
    sql = sql.replace("```SQL", "")
    sql = sql.replace("```", "")
    return sql.strip()


# =====================================================
# 9. AI TEXT ANALYSIS
# =====================================================

def analyze_results(question, df):
    language = st.session_state.language
    language_instruction = (
        "Georgian" if language == "ქართული" else "English"
    )

    if df.empty:
        return t("no_data_analysis")

    preview = df.head(30).to_dict(orient="records")

    prompt = f"""
You are a professional Data Analyst.

IMPORTANT:
Write your entire analysis in {language_instruction}.
Do not switch languages.

USER QUESTION:
{question}

QUERY RESULTS:
{json.dumps(preview, ensure_ascii=False, default=str)}

Number of records: {len(df)}

TASK:
1. Explain the query results.
2. Highlight important numbers and facts.
3. Provide a short conclusion when supported by the data.
4. Do not invent information.
5. Do not make unsupported assumptions.
6. Use clear and structured formatting.
"""

    response = client.responses.create(
        model=MODEL,
        instructions=(
            f"You are a professional data analyst. "
            f"Always answer in {language_instruction}. "
            "Analyze only the supplied data."
        ),
        input=prompt,
        max_output_tokens=800
    )

    return response.output_text.strip()


# =====================================================
# 10. AUTOMATIC CHART SELECTION
# =====================================================

def generate_chart_config(question, df):
    if df.empty or len(df.columns) < 2:
        return None

    language = st.session_state.language
    chart_language = "Georgian" if language == "ქართული" else "English"

    column_info = {
        column: str(df[column].dtype)
        for column in df.columns
    }

    sample = df.head(15).to_dict(orient="records")

    prompt = f"""
You are an expert data visualization specialist.

The chart title must be written in {chart_language}.

USER QUESTION:
{question}

AVAILABLE COLUMNS AND TYPES:
{json.dumps(column_info, ensure_ascii=False)}

SAMPLE DATA:
{json.dumps(sample, ensure_ascii=False, default=str)}

Choose the most suitable chart.

Allowed chart types:
- bar
- line
- pie
- scatter
- none

RULES:
1. Use only existing column names.
2. Bar charts are suitable for category comparisons.
3. Line charts are suitable for time trends.
4. Pie charts are suitable for proportions.
5. Scatter charts are suitable for relationships between numeric variables.
6. For bar, line and pie, y must be numeric.
7. For scatter, both x and y must be numeric.
8. Never invent columns or data.
9. Choose none if a chart is unsuitable.

Return only valid JSON:
{{
    "chart_type": "bar",
    "x": "column_name",
    "y": "column_name",
    "title": "Chart title"
}}
"""

    response = client.responses.create(
        model=MODEL,
        instructions="Return only valid JSON. Do not include Markdown.",
        input=prompt,
        max_output_tokens=300
    )

    try:
        result = response.output_text.strip()
        start = result.find("{")
        end = result.rfind("}") + 1

        if start == -1 or end == 0:
            return None

        config = json.loads(result[start:end])

        chart_type = config.get("chart_type")
        x = config.get("x")
        y = config.get("y")

        if chart_type not in ["bar", "line", "pie", "scatter"]:
            return None

        if x not in df.columns or y not in df.columns:
            return None

        if not pd.api.types.is_numeric_dtype(df[y]):
            return None

        if chart_type == "scatter":
            if not pd.api.types.is_numeric_dtype(df[x]):
                return None

        return config

    except (ValueError, TypeError, KeyError):
        return None


# =====================================================
# 11. CHART DISPLAY
# =====================================================

def display_chart(df, config):
    if not config:
        st.info(t("no_chart"))
        return

    chart_type = config["chart_type"]
    x = config["x"]
    y = config["y"]
    title = config.get("title", "Data Visualization")

    if chart_type == "bar":
        fig = px.bar(df, x=x, y=y, title=title, text_auto=True)
    elif chart_type == "line":
        fig = px.line(df, x=x, y=y, title=title, markers=True)
    elif chart_type == "pie":
        fig = px.pie(df, names=x, values=y, title=title)
    elif chart_type == "scatter":
        fig = px.scatter(df, x=x, y=y, title=title)
    else:
        return

    fig.update_layout(
        template="plotly_dark",
        paper_bgcolor="#151f32",
        plot_bgcolor="#151f32",
        font=dict(color="#e5e7eb"),
        margin=dict(l=20, r=20, t=60, b=20),
        title_x=0.02
    )

    st.plotly_chart(fig, use_container_width=True)


# =====================================================
# 12. LOAD DATABASE SCHEMA
# =====================================================

schema = get_schema()


# =====================================================
# 13. SIDEBAR
# =====================================================

with st.sidebar:
    st.markdown("## 📊 AI SQL Assistant")
    st.caption("Intelligent Database Analysis")
    st.divider()

    st.selectbox(
        t("language"),
        options=list(LANGUAGES.keys()),
        format_func=lambda value: LANGUAGES[value],
        key="language"
    )

    st.divider()
    st.markdown(f"### 🗄️ {t('database')}")
    st.success(t("connected"))

    display_database_explorer(schema)

    st.divider()
    st.markdown(f"### 💡 {t('example_questions')}")

    if st.session_state.language == "ქართული":
        examples = [
            "რამდენი მომხმარებელია ბაზაში?",
            "რომელია ყველაზე გაყიდვადი პროდუქტის კატეგორიები?",
            "რომელ შტატშია ყველაზე მეტი მომხმარებელი?",
            "რა არის შეკვეთების საშუალო ღირებულება?",
            "აჩვენე შეკვეთების რაოდენობა თვეების მიხედვით"
        ]
    else:
        examples = [
            "How many customers are in the database?",
            "What are the top-selling product categories?",
            "Which state has the most customers?",
            "What is the average order value?",
            "Show orders by month"
        ]

    for i, example in enumerate(examples):
        if st.button(
            example,
            key=f"example_{i}",
            use_container_width=True
        ):
            st.session_state.question = example


# =====================================================
# 14. MAIN DASHBOARD
# =====================================================

st.markdown(
    f'<div class="main-title">{t("title")}</div>',
    unsafe_allow_html=True
)

st.markdown(
    f'<div class="subtitle">{t("subtitle")}</div>',
    unsafe_allow_html=True
)


# =====================================================
# 15. DASHBOARD METRICS
# =====================================================

customers_count = (
    get_table_count("customers") if "customers" in schema else 0
)
orders_count = (
    get_table_count("orders") if "orders" in schema else 0
)
products_count = (
    get_table_count("products") if "products" in schema else 0
)

col1, col2, col3 = st.columns(3)

with col1:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-label">👥 {t("total_customers")}</div>
        <div class="metric-value">{customers_count:,}</div>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-label">📦 {t("total_orders")}</div>
        <div class="metric-value">{orders_count:,}</div>
    </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-label">🛍️ {t("total_products")}</div>
        <div class="metric-value">{products_count:,}</div>
    </div>
    """, unsafe_allow_html=True)

st.divider()


# =====================================================
# 16. QUESTION INPUT
# =====================================================

st.markdown(f"### 💬 {t('ask_database')}")

question = st.text_area(
    t("question_label"),
    key="question",
    height=100,
    placeholder=t("placeholder")
)


# =====================================================
# 17. ANALYSIS WORKFLOW
# =====================================================

if st.button(t("analyze"), use_container_width=True):

    if not question.strip():
        st.warning(t("enter_question"))

    else:
        try:
            # STEP 1: SQL GENERATION
            with st.spinner(t("generating_sql")):
                sql = generate_sql(question, schema)

            st.markdown(f"### {t('generated_sql')}")
            st.code(sql, language="sql")

            # STEP 2: SQL EXECUTION
            with st.spinner(t("fetching_data")):
                df = execute_query(sql)

            st.divider()

            # STEP 3: TEXT ANALYSIS
            st.markdown(f"### {t('analysis')}")

            with st.spinner(t("analyzing")):
                answer = analyze_results(question, df)

            st.markdown(
                f"""
                <div class="answer-card">
                    <div class="answer-title">{t("summary")}</div>
                </div>
                """,
                unsafe_allow_html=True
            )

            st.markdown(answer)
            st.divider()

            # STEP 4: AUTOMATIC CHART
            st.markdown(f"### {t('visualization')}")

            with st.spinner(t("choosing_chart")):
                chart_config = generate_chart_config(question, df)

            if chart_config:
                st.caption(
                    f"{t('selected_chart')} "
                    f"{chart_config['chart_type'].upper()}"
                )

            display_chart(df, chart_config)
            st.divider()

            # STEP 5: DATA TABLE
            st.markdown(f"### {t('data_table')}")

            if df.empty:
                st.info(t("no_data"))
            else:
                st.caption(t("showing", count=len(df)))

                st.dataframe(
                    df,
                    use_container_width=True,
                    hide_index=True
                )

                csv = df.to_csv(index=False).encode("utf-8-sig")

                st.download_button(
                    label=t("download"),
                    data=csv,
                    file_name="sql_results.csv",
                    mime="text/csv"
                )

        except Exception as e:
            st.error(t("error", error=str(e)))
            st.info(t("error_help"))
