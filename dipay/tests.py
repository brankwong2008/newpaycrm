
from flask import Flask, request
import subprocess
import os

app = Flask(__name__)

@app.route("/",methods=["GET"])
def index():
    return "hello welcome to index"


@app.route("/hook",methods=["POST","GET"])
def hook():
    print('request:',request)

    base_path = r'/opt/env1'
    project_file_path = os.path.join(base_path,'paycrm')
    # if not os.path.exists(project_file_path):
    #     subprocess.check_call(f'mkdir {project_file_path}', shell=True, cwd=base_path)

    return "success"



# if __name__ == "__main__":
#         app.run(host="0.0.0.0",port=9001,debug=True)

if __name__ == "__main__":
    class F:
        a = 0
        b = 0
    f = F()

    data = [("a",3),("b",4)]

    [setattr(f, x[0], x[1]) for x in data]

    print("f.a,f.b",f.a,f.b)






