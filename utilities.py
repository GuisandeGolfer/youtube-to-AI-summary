import streamlit as st
import requests

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
