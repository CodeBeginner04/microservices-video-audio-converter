import os, requests

def login(request):
    auth= request.authorization
    if not auth:
        return None, ("Missing credentials", 401)

    basicAuth= (auth.username, auth.password)

    response = requests.post(f"http://{os.environ.get('AUTH_SVC_HOST','host.minikube.internal')}:{os.environ.get('AUTH_SVC_PORT','5000')}/login", 
                             auth=basicAuth)
    if response.status_code == 200:
        return response.text, None
    else:
        return None, (response.text, response.status_code)