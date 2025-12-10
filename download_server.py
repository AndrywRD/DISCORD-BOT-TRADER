from http.server import HTTPServer, SimpleHTTPRequestHandler
import os

os.chdir(os.path.dirname(os.path.abspath(__file__)))

print("Servidor de download iniciado!")
print("Acesse a URL do projeto para baixar os arquivos.")
print("Clique nos arquivos para baixar.")

HTTPServer(("0.0.0.0", 5000), SimpleHTTPRequestHandler).serve_forever()
