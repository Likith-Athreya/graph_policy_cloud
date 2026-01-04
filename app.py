import streamlit as st
import boto3
import json

# ------------------------
# Page config
# ------------------------
st.set_page_config(
    page_title="Policy Query Interface",
    layout="centered"
)

st.title("Policy Query Interface")
st.write(
    "Enter a natural language query. "
    "The system retrieves the relevant policy, clauses, conditions, and outcomes."
)

# ------------------------
# AWS Lambda client
# ------------------------
lambda_client = boto3.client(
    "lambda",
    region_name="eu-north-1"
)

LAMBDA_FUNCTION_NAME = "s3_ingester"

# ------------------------
# UI Input
# ------------------------
query = st.text_input(
    "Enter your question",
    placeholder="e.g. severance after poor performance"
)

# ------------------------
# Submit
# ------------------------
if st.button("Search"):
    if not query.strip():
        st.warning("Please enter a query")
    else:
        with st.spinner("Querying policy system..."):
            try:
                response = lambda_client.invoke(
                    FunctionName=LAMBDA_FUNCTION_NAME,
                    InvocationType="RequestResponse",
                    Payload=json.dumps({
                        "query": query
                    })
                )

                payload = json.loads(
                    response["Payload"].read().decode("utf-8")
                )

                if "errorMessage" in payload:
                    st.error(payload["errorMessage"])
                else:
                    # ------------------------
                    # Display result
                    # ------------------------
                    st.subheader("Matched Policy")
                    st.json(payload["semantic_match"])

                    st.subheader("Policy Details")
                    graph = payload["graph_context"]

                    st.markdown(f"**Policy ID:** {graph['policy_id']}")
                    st.markdown(f"**Policy Name:** {graph['policy_name']}")

                    if graph["conditions"]:
                        st.markdown("### Conditions")
                        for c in graph["conditions"]:
                            st.write(f"- {c}")

                    if graph["clauses"]:
                        st.markdown("### Clauses")
                        for c in graph["clauses"]:
                            st.write(f"- {c}")

                    if graph["outcomes"]:
                        st.markdown("### Outcomes")
                        for o in graph["outcomes"]:
                            st.write(f"- {o}")

            except Exception as e:
                st.error(str(e))
