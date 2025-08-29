####
# LISTAR ARCHIVOS EN BLOB:
####

from azure.storage.blob import BlobServiceClient
from dotenv import load_dotenv
import os

load_dotenv()

# Usa la cadena de conexión de tu storage account
connection_string = os.getenv("AZURE_STORAGE_CONNECTION_STRING")

# Crear el cliente del servicio
blob_service_client = BlobServiceClient.from_connection_string(connection_string)

# Nombre del contenedor
container_name = "finsight-container"

# Obtener cliente del contenedor
container_client = blob_service_client.get_container_client(container_name)

# Listar blobs en el contenedor
print("Blobs en el contenedor:")
for blob in container_client.list_blobs():
    print(f" - {blob.name}")

#####
# SUBIR UN ARCHIVO:
####
from azure.storage.blob import BlobClient

# Crear cliente de blob
blob_client = blob_service_client.get_blob_client(container=container_name, blob="archivo.txt")

# Subir un archivo local
with open("test.txt", "rb") as data:
    blob_client.upload_blob(data, overwrite=True)

print("Archivo subido correctamente ✅")


#####
# DESCARGAR ARCHIVO
#####

blob_client = blob_service_client.get_blob_client(container="finsight-container", blob="As festas juninas.pdf")

import os

os.makedirs("./files", exist_ok=True)
with open("./files/archivo_descargado.pdf", "wb") as file:
    download_stream = blob_client.download_blob()
    file.write(download_stream.readall())

