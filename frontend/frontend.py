import streamlit as st
import requests

st.set_page_config(page_title="FinSights Uploader", layout="centered")

# --- UI Elements ---
st.title("Carga de Documentos para FinSights")
st.write("Esta interfaz permite subir un documento PDF para ser procesado por el sistema.")

backend_url = st.text_input(
    "URL del Backend de FinSights", 
    "http://127.0.0.1:8000"
)

company_id = st.text_input("ID de la Compañía", "", placeholder="Ej: aple, goog, msft")

uploaded_file = st.file_uploader(
    "Selecciona un archivo PDF", 
    type=["pdf"]
)

submit_button = st.button("Subir y Procesar Archivo")

# --- Logic ---
if submit_button:
    if not company_id:
        st.error("Por favor, ingresa el ID de la Compañía.")
    elif uploaded_file is None:
        st.error("Por favor, selecciona un archivo PDF para subir.")
    else:
        api_url = f"{backend_url}/api/v1/ingest/upload?company_id={company_id}"
        
        files = {
            "file": (uploaded_file.name, uploaded_file.getvalue(), uploaded_file.type)
        }
        
        with st.spinner(f"Subiendo '{uploaded_file.name}'..."):
            try:
                response = requests.post(api_url, files=files, timeout=30)
                
                if response.status_code == 200:
                    st.success("¡Archivo subido con éxito!")
                    response_data = response.json()
                    st.json(response_data)
                    st.write("URL del archivo en Azure:")
                    st.code(response_data.get("file_url"), language="text")
                else:
                    st.error(f"Error al subir el archivo (Código: {response.status_code})")
                    try:
                        st.json(response.json())
                    except Exception:
                        st.text(response.text)

            except requests.exceptions.RequestException as e:
                st.error(f"No se pudo conectar con el backend en '{backend_url}'.")
                st.error(f"Detalle del error: {e}")
