# HTTP Proxy Server  

A concurrent HTTP/1.0 proxy server handling GET requests. Supports browser configuration and multiple concurrent clients.  

## Features  
- **Thread-based concurrency** for multiple clients  
- **HTTP/1.0 protocol compliance**  
- **GET method support**  
- **Basic error handling** (400/501/502 responses)  
- **Windows compatibility**  
- **Browser proxy configuration support**  

## Installation & Usage  

### Start Proxy  
Run the following command:  

python proxy_server.py

The server listens on port **8080**.  

## Browser Configuration  

### Firefox  
Go to **Settings → Network Settings → Manual proxy** and set:  

127.0.0.1:8080


### Chrome  
Use the **Proxy SwitchyOmega** extension to configure the proxy.  

## Verification  

### PowerShell  
Run:  

Invoke-WebRequest -Uri "http://httpbin.org/ip" -Proxy "http://localhost:8080"


### CURL (if installed)  
Run:  

curl --proxy http://localhost:8080 http://httpbin.org/ip
 

### Browser (after setup)
On the search bar type:

http://httpbin.org/ip

## Limitations  
- ❌ No HTTPS support  
- ❌ GET method only  
- ❌ No caching  
- ❌ No authentication  


