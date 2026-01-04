import os, requests

def token(request):
    if not "Authorization" in request.headers:
        return None, ("Missing token", 401)
    
    token = request.headers["Authorization"]

    if not token:
        return None, ("Missing token", 401)
    
    response = requests.post(f"http://{os.environ.get('AUTH_SVC_HOST','host.minikube.internal')}:{os.environ.get('AUTH_SVC_PORT','5000')}/protected", 
                             headers={"Authorization": token})
    
    if response.status_code == 200:
        return response.text, None
    else:
        return None, (response.text, response.status_code)