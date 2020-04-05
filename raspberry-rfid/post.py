import requests
import json

url = "http://192.168.225.132:8080/yee/"

def post(payload, id):
    return(requests.post(url + str(id), data=json.dumps(payload)))

if __name__ == "__main__":
    payload = dict(id=1,
                   name="Al")
    print(post(payload, 1))