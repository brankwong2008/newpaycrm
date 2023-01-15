#
# from flask import Flask, request
# import subprocess
# import os
# app = Flask(__name__)
#
# @app.route("/",methods=["GET"])
# def index():
#     return "hello welcome to index"
#
#
# @app.route("/hook",methods=["POST","GET"])
# def hook():
#     print('request:',request)
#
#     base_path = r'/opt/env1'
#     project_file_path = os.path.join(base_path,'paycrm')
#     # if not os.path.exists(project_file_path):
#     #     subprocess.check_call(f'mkdir {project_file_path}', shell=True, cwd=base_path)
#
#     return "success"

# if __name__ == "__main__":
#         app.run(host="0.0.0.0",port=9001,debug=True)


from django.test import TestCase

import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'paycrm.settings')

if __name__ == "__main__":
    from django_redis import get_redis_connection

    conn = get_redis_connection()
    conn.set("phone/var/url", "1223", ex=300)
    res = conn.get("phone/var/url")

    print("the res is:", res)








