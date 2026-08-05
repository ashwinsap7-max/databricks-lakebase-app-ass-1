"""
One-time setup script: creates the Databricks secret scope and stores Lakebase credentials.
Run this from a Databricks notebook with appropriate permissions.

NEVER commit actual secret values to Git!

Usage:
    Run this script in a Databricks notebook
"""
from databricks.sdk import WorkspaceClient
from databricks.sdk.service import workspace
import getpass

w = WorkspaceClient()

# Create secret scope for Lakebase credentials
scope_name = "lakebase"

try:
    w.secrets.create_scope(scope=scope_name)
    print(f"✅ Created secret scope: {scope_name}")
except Exception as e:
    print(f"ℹ️  Secret scope '{scope_name}' may already exist: {e}")

# Store Lakebase connection details
print("\n📝 Enter your Lakebase connection details:")
print("(These will be securely stored in Databricks Secrets)\n")

w.secrets.put_secret(
    scope=scope_name,
    key="pghost",
    string_value=input("Lakebase endpoint host (e.g., ep-branch-id.aws.lakebase.databricks.com): ")
)
print("✅ Stored: pghost")

w.secrets.put_secret(
    scope=scope_name,
    key="pgdatabase",
    string_value=input("Database name (e.g., support-system): ")
)
print("✅ Stored: pgdatabase")

w.secrets.put_secret(
    scope=scope_name,
    key="pguser",
    string_value=input("Database user (your email or service principal): ")
)
print("✅ Stored: pguser")

w.secrets.put_secret(
    scope=scope_name,
    key="pgport",
    string_value=input("Database port (default 5432): ") or "5432"
)
print("✅ Stored: pgport")

# Grant read access to users
try:
    w.secrets.put_acl(
        scope=scope_name,
        principal="users",
        permission=workspace.AclPermission.READ,
    )
    print(f"\n✅ Granted READ access to 'users' on scope '{scope_name}'")
except Exception as e:
    print(f"⚠️  Could not set ACL: {e}")

print("\n🎉 Setup complete! Your app can now securely access Lakebase credentials.")
print(f"\nSecret scope: {scope_name}")
print("Keys stored: pghost, pgdatabase, pguser, pgport")