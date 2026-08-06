import os
import base64
import streamlit as st
from databricks.sdk import WorkspaceClient
from datetime import datetime

# Initialize Databricks client
w = WorkspaceClient()

# Get Lakebase connection details from secrets
try:
    db_host_encoded = w.secrets.get_secret(scope="lakebase", key="pghost").value
    db_user_encoded = w.secrets.get_secret(scope="lakebase", key="pguser").value
    db_name_encoded = w.secrets.get_secret(scope="lakebase", key="pgdatabase").value
    db_port_encoded = w.secrets.get_secret(scope="lakebase", key="pgport").value
    
    db_host = base64.b64decode(db_host_encoded).decode('utf-8')
    db_user = base64.b64decode(db_user_encoded).decode('utf-8')
    db_name = base64.b64decode(db_name_encoded).decode('utf-8')
    db_port = base64.b64decode(db_port_encoded).decode('utf-8')
    secrets_loaded = True
except Exception as e:
    secrets_loaded = False
    error_msg = str(e)
    db_host = db_user = db_name = db_port = "N/A"

# Streamlit UI
st.set_page_config(page_title="Support Center", page_icon="🎫", layout="wide")
st.title("🎫 Support Ticket Center - Setup Required")

st.error("⚠️ **Network Connectivity Issue**")

st.markdown("""
### 🚫 The Problem

Databricks Apps cannot make **direct external connections** to Lakebase Postgres endpoints on port 5432 due to network restrictions.

**Error:** `Connection refused` to Lakebase endpoint on port 5432

### 🔧 Lakebase Configuration (from secrets)
""")

if secrets_loaded:
    st.info(f"""
    * **Host:** `{db_host}`
    * **Database:** `{db_name}`
    * **User:** `{db_user}`
    * **Port:** `{db_port}`
    
    ✅ Secrets are correctly configured  
    ❌ Direct connection blocked by network policy
    """)
else:
    st.warning(f"Failed to load secrets: {error_msg}")

st.markdown("""
### ✅ Solution Options

**Option 1: Use Foreign Catalog (Recommended)**
1. Create a Foreign Catalog connection in Unity Catalog that connects to your Lakebase database
2. Query the tables through a SQL Warehouse instead of direct psycopg2
3. Update the app to use `databricks-sql-connector`

**Option 2: Mirror Data to Unity Catalog**
1. Set up a Delta Live Tables pipeline to replicate Lakebase tables to Unity Catalog
2. Query Unity Catalog tables directly from the app

**Option 3: API-based Queries**
1. Use the Databricks SDK to execute queries via the Lakebase API
2. Requires restructuring the app to use API calls instead of SQL connections

### 📊 Your Data

The following tables exist in Lakebase and contain sample data:
* `service_mgmt.tickets` (5 tickets)
* `service_mgmt.ticket_messages` (10+ messages)

### 🔧 Next Steps

1. **Decide on architecture:** Choose one of the options above
2. **Set up connectivity:** Configure Foreign Catalog or data replication
3. **Update app code:** Modify connection logic based on chosen approach

""")

st.info("💡 **Recommendation:** Use Foreign Catalog to query Lakebase tables through Unity Catalog - this is the most straightforward approach.")

st.markdown("---")
st.markdown("### 📚 Additional Resources")
st.markdown("* [Databricks Foreign Catalog Documentation](https://docs.databricks.com/en/query-federation/index.html)")
st.markdown("* [Lakebase Documentation](https://docs.databricks.com/en/lakebase/index.html)")
