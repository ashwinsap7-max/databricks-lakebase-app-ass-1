import os
import streamlit as st
from databricks.sdk import WorkspaceClient
from datetime import datetime

# Initialize Databricks client
w = WorkspaceClient()

# Lakebase project configuration
PROJECT_NAME = "dataexperts-ash-ass1"
BRANCH_NAME = "production"
DATABASE_NAME = "support-app"

# Helper function to execute Lakebase SQL
def execute_lakebase_query(sql, params=None):
    """Execute a SQL query against Lakebase using Databricks SDK"""
    try:
        # Note: This uses internal Databricks APIs to route queries to Lakebase
        # The executeLakebasePostgresSql tool pattern
        from databricks.sdk.service.sql import ExecuteStatementRequestOnWaitTimeout
        
        # Create a simple wrapper that executes via SQL execution API
        # targeting the Lakebase compute endpoint
        
        # For now, return mock data
        # TODO: Implement proper API-based query execution
        return []
    except Exception as e:
        st.error(f"Query failed: {e}")
        return []

# Streamlit UI
st.set_page_config(page_title="Support Center", page_icon="🎫", layout="wide")
st.title("🎫 Support Ticket Center")

st.info("📊 **Data Source:** Lakebase Postgres (`support-app` database)")

# Sidebar for navigation
page = st.sidebar.radio("Navigation", ["View Tickets", "Create Ticket", "About"])

if page == "View Tickets":
    st.header("All Support Tickets")
    
    st.warning("⚠️ **Implementation Note:** API-based Lakebase queries are being configured.")
    
    st.markdown("""
    ### Current Status
    
    * ✅ Lakebase database created: `support-app`
    * ✅ Tables created: `service_mgmt.tickets`, `service_mgmt.ticket_messages`
    * ✅ Sample data inserted (5 tickets, 10+ messages)
    * ⏳ **In Progress:** Configuring API-based query execution
    
    ### Next Steps
    
    The app needs to query Lakebase through the Databricks SDK/API rather than direct connections,
    as network policies prevent external database connections from Databricks Apps.
    
    """)
    
    # Show sample of what the data looks like
    st.subheader("Sample Ticket Structure")
    st.code("""
    Table: service_mgmt.tickets
    - ticket_id (SERIAL PRIMARY KEY)
    - title (VARCHAR(200))
    - status (VARCHAR(50))  -- 'open', 'in_progress', 'resolved'
    - created_by (VARCHAR(100))
    - created_at (TIMESTAMP)
    
    Table: service_mgmt.ticket_messages
    - message_id (SERIAL PRIMARY KEY)
    - ticket_id (INTEGER FK)
    - message_text (TEXT)
    - author (VARCHAR(100))
    - created_at (TIMESTAMP)
    """, language="sql")

elif page == "Create Ticket":
    st.header("Create New Support Ticket")
    
    st.info("Ticket creation will be enabled once API-based query execution is configured.")
    
    with st.form("create_ticket_form"):
        ticket_title = st.text_input("Ticket Title *")
        ticket_status = st.selectbox("Initial Status", ["open", "in_progress", "resolved"])
        ticket_creator = st.text_input("Your Email *")
        
        submitted = st.form_submit_button("Create Ticket")
        
        if submitted:
            st.warning("Feature coming soon - pending API configuration")

elif page == "About":
    st.header("About This App")
    
    st.markdown("""
    ### Architecture
    
    This Databricks App connects to a **Lakebase Postgres database** to manage support tickets.
    
    **Technical Stack:**
    * **Frontend:** Streamlit (Python web framework)
    * **Database:** Lakebase Postgres (`support-app`)
    * **Connection Method:** Databricks SDK/API (due to network restrictions)
    * **Deployment:** Databricks Apps V2
    
    ### Database Schema
    
    * **Project:** `dataexperts-ash-ass1`
    * **Branch:** `production`  
    * **Database:** `support-app`
    * **Schema:** `service_mgmt`
    * **Tables:** `tickets`, `ticket_messages`
    
    ### Why API-based queries?
    
    Databricks Apps cannot make direct external connections to Lakebase Postgres endpoints.
    Instead, queries must route through Databricks internal APIs, similar to how the
    workspace query tools access Lakebase.
    
    """)

# Footer
st.sidebar.markdown("---")
st.sidebar.info(f"""
**Lakebase Connection**  
Project: {PROJECT_NAME}  
Branch: {BRANCH_NAME}  
Database: {DATABASE_NAME}
""")
