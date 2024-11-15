import streamlit as st
import requests
from streamlit_autorefresh import st_autorefresh


def get_result(task_id: str):
    try:
        # Send the GET request to the server
        response = requests.get(f'http://127.0.0.1:8000/task/{task_id}')
        response.raise_for_status()  # Raises an HTTPError for bad responses

        # Parse the response JSON
        summary = response.json()
        print(summary)
        return summary

    except requests.exceptions.RequestException as e:
        # Handle network-related errors gracefully
        st.error(f"Request error: {e}")
        return {"status": "UNKNOWN", "error": str(e)}
    except ValueError as e:
        # Handle JSON decoding errors
        st.error(f"Error parsing response: {e}")
        return {"status": "UNKNOWN", "error": str(e)}

def send_req_to_server(url, summary_type, **kwargs):
    st.write(f'URL is {url}, and summary type is {summary_type}')

    data = {"url": url, "detail_level": summary_type}

    # TODO: Update the URL to your deployed FastAPI server
    try:
        response = requests.post('http://127.0.0.1:8000/start-download', json=data)
        response.raise_for_status()  # Raises an HTTPError for bad responses
        return response.json()
    except requests.exceptions.RequestException as e:
        st.error(f"Request error: {e}")
        return {"status": "FAILED", "error": str(e)}


st.title("Free YouTube to AI Summary")

# Initialize session state variables
if 'task_id' not in st.session_state:
    st.session_state.task_id = None

if 'polling' not in st.session_state:
    st.session_state.polling = False

if 'task_status' not in st.session_state:
    st.session_state.task_status = None

if 'summary' not in st.session_state:
    st.session_state.summary = None

if 'error' not in st.session_state:
    st.session_state.error = None

# User inputs
with st.form("my_form"):
    url = st.text_input('YouTube URL')
    summary_type = st.selectbox('Pick a type of summary', [
        'detailed',
        'short & sweet',
        'highly-detailed [premium]',
        'old english',
        'Latin'
    ])
    send_button = st.form_submit_button('Get My Summary')

# Start the task
if send_button:
    with st.spinner("Sending Request to OpenAI... please be patient."):
        response = send_req_to_server(url, summary_type)
        if response and 'task_id' in response:
            print(f"in send button if statement: {response}")
            st.session_state.task_id = response['task_id']
            st.session_state.polling = True
            st.session_state.task_status = 'pending'
            st.session_state.summary = None
            st.session_state.error = None
            st.write("Task started. Task ID:", st.session_state.task_id)
        else:
            st.error("Failed to start task.")
            st.write(response)

# Polling mechanism
if st.session_state.polling and st.session_state.task_id:
    # Autorefresh every 5 seconds
    count = st_autorefresh(interval=5000, limit=None, key="polling_key")
    # Fetch task status
    summary = get_result(st.session_state.task_id)
    status = summary.get('status', 'UNKNOWN').lower()
    st.write(f"Current task status: {status}")

    if status == 'completed':
        print(f"status is now completed: {summary}")
        st.session_state.task_status = 'completed'
        st.session_state.summary = summary.get('summary', 'No summary found.')
        st.session_state.polling = False
    elif status == 'failed':
        st.session_state.task_status = 'failed'
        st.session_state.error = summary.get('error', 'No error information.')
        st.session_state.polling = False
    else:
        st.session_state.task_status = status

# Display the result or status message outside the polling block
if st.session_state.task_status == 'completed':
    st.success("Task completed!")
    st.markdown("Summary:", st.session_state.summary)
elif st.session_state.task_status == 'failed':
    st.error("Task failed.")
    st.write("Error:", st.session_state.error)
elif st.session_state.task_status == 'in_progress' or st.session_state.task_status == 'pending':
    st.info("Task is still in progress...")

