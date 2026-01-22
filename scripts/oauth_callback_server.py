"""
Servidor simple para recibir el callback de OAuth de Freelancer.
Ejecutar este servidor antes de iniciar el flujo OAuth.
"""
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
import webbrowser

class OAuthCallbackHandler(BaseHTTPRequestHandler):
    """Handler para recibir el callback de OAuth."""
    
    authorization_code = None
    
    def do_GET(self):
        """Maneja la solicitud GET del callback."""
        # Parsear URL
        parsed_url = urlparse(self.path)
        query_params = parse_qs(parsed_url.query)
        
        # Obtener código de autorización
        code = query_params.get('code', [None])[0]
        error = query_params.get('error', [None])[0]
        
        if code:
            OAuthCallbackHandler.authorization_code = code
            
            # Respuesta exitosa
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            
            html = f"""
            <html>
            <head><title>Autenticación Exitosa</title></head>
            <body style="font-family: Arial; text-align: center; padding: 50px;">
                <h1 style="color: green;">✅ Autenticación Exitosa</h1>
                <p>Código de autorización recibido:</p>
                <code style="background: #f0f0f0; padding: 10px; display: block; margin: 20px;">{code}</code>
                <p>Puedes cerrar esta ventana y volver a la terminal.</p>
            </body>
            </html>
            """
            self.wfile.write(html.encode())
            
        elif error:
            # Error en autorización
            self.send_response(400)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            
            html = f"""
            <html>
            <head><title>Error de Autenticación</title></head>
            <body style="font-family: Arial; text-align: center; padding: 50px;">
                <h1 style="color: red;">❌ Error de Autenticación</h1>
                <p>Error: {error}</p>
                <p>Vuelve a la terminal e intenta nuevamente.</p>
            </body>
            </html>
            """
            self.wfile.write(html.encode())
        
        else:
            # Sin código ni error
            self.send_response(400)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            self.wfile.write(b"No authorization code received")
    
    def log_message(self, format, *args):
        """Silenciar logs del servidor."""
        pass

def run_callback_server(port=8080):
    """
    Inicia el servidor de callback en el puerto especificado.
    """
    server_address = ('', port)
    httpd = HTTPServer(server_address, OAuthCallbackHandler)
    
    print(f"🌐 Servidor de callback iniciado en http://localhost:{port}")
    print(f"   Esperando callback de Freelancer OAuth...")
    print(f"   Presiona Ctrl+C para detener\n")
    
    try:
        # Procesar solo una solicitud
        httpd.handle_request()
        
        if OAuthCallbackHandler.authorization_code:
            print(f"\n✅ Código recibido: {OAuthCallbackHandler.authorization_code}")
            return OAuthCallbackHandler.authorization_code
        else:
            print("\n❌ No se recibió código de autorización")
            return None
            
    except KeyboardInterrupt:
        print("\n\n⚠️ Servidor detenido por el usuario")
        return None
    finally:
        httpd.server_close()

if __name__ == "__main__":
    code = run_callback_server()
    if code:
        print(f"\nUsa este código en el script de autenticación: {code}")
