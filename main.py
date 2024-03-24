from sanic import Sanic, response, HTTPResponse, json, redirect, html, file
from sanic import Sanic
from sanic.response import text, html
from jinja2 import Environment, FileSystemLoader, select_autoescape
import base64
import database
from datetime import datetime
import random
import os
import string
app = Sanic("WorldSkillsApi")

tokens = {}

def generatetoken():
    token = base64.b64encode(datetime.now().strftime('%Y-%m-%d %H:%M:%S').encode('utf-8')).decode('utf-8')
    return token

def verify_token(request):
    authorization_header = request.headers.get('Authorization')
    if not authorization_header:
        return False
    if authorization_header.startswith('Bearer '):
            bearer_token = authorization_header.split(' ')[1]
    else: return False
    global tokens
    try:
        return tokens[bearer_token]
    except:
        return False
def get_token(request):
    authorization_header = request.headers.get('Authorization')
    if not authorization_header:
        return False
    if authorization_header.startswith('Bearer '):
            bearer_token = authorization_header.split(' ')[1]
    else: return False
    
    return bearer_token

@app.post("/authorization")
async def authorization(request):
    global tokens
    if not request.json:
        return json({"success": False,
                    "message": "Login failed"}, status=401)
    email = request.json.get('email')
    password = request.json.get('password')
    first_name= request.json.get('first_name')
    last_name = request.json.get('last_name')
    dbresp = database.loginUser(email, password, first_name, last_name)
    if dbresp:
        token = generatetoken()
        tokens[token]={'email':email,'password':password,"first_name":first_name, "first_name":last_name}
        return json({"success": True,
                    "message": "Success",
                    "token": token}, status=200)
    else:
        return json({"success": False,
                    "message": "Login failed"}, status=401)

@app.post("/registration")
async def registration(request):
    global tokens
    if not request.json:
        return json({"success": False,
                    "message": "Registration failed"}, status=401)
    email = request.json.get('email')
    password = request.json.get('password')
    first_name = request.json.get('first_name')
    last_name = request.json.get('last_name')
    message = {}
    if not email:
        message['email'] = 'email cannot be blank'
    if not password:
        message['password'] = 'password cannot be blank'
    if not first_name:
        message['first_name'] = 'first_name cannot be blank'
    if not last_name:
        message['last_name'] = 'last_name cannot be blank'
    if len(message.keys()) > 0:
        return json({"success": False,
                    "message": message}, status=422)
    if not database.createUser(email, password, first_name, last_name):
        return json({"success": False,
                    "message": "Registration failed, email already exists"}, status=500)
    token = generatetoken()
    tokens[token]={'email':email,'password':password,"first_name":first_name, "first_name":last_name}
    return json({"success": True, 'message':'Success', "token": token}, status=200)

@app.get('/logout')
async def logout(request):
    if verify_token(request):
        del tokens[get_token(request)]
        return json({"success": True, 'message':'Success'}, status=200)
    else:
        return json({"success": False, 'message':'Unauthorised'}, status=401)

def getrandomstring(length):
    return ''.join(random.choice(string.ascii_letters + string.digits) for _ in range(length))

#region Работа с файлами
@app.get('/files/<fileid>')
async def get_file(request, fileid):
    user = verify_token(request)
    if not user:
        return response.json({'error': 'Unauthorised'}, status=401)
    email = database.IsUserAllowedToFile(fileid, user['email'])
    if not email:
        return response.json({'error': 'Access not allowed'}, status=403)
    try:
        filepath = f"files/{email}/{database.getFilenameWithFileId(fileid)}"
        return await response.file(filepath)
    except:
        return response.json({'error': 'File not found'}, status=404)

@app.delete('/files/<fileid>')
async def delete_file(request, fileid):
    user = verify_token(request)
    if not user:
        return response.json({'error': 'Unauthorised'}, status=401)
    try:
        os.remove(f"files/{user['email']}/{database.getFilenameWithFileId(fileid)}")
        database.deletefile(fileid)
    except:
        return response.json({'error': 'File not found'}, status=404)
    return response.json({'success': True, "message": "Deleted"}, status=200)

@app.patch('/files/<fileid>')
async def rename_file(request, fileid):
    user = verify_token(request)
    if not user:
        return response.json({'error': 'Unauthorised'}, status=401)
    email = database.IsUserAllowedToFile(fileid, user['email'])
    if not database.IsUserFileOwner(fileid, user['email']):
        return response.json({'error': 'Access not allowed'}, status=403)
    if not email:
        return response.json({'error': 'Access not allowed'}, status=403)
    try:
        os.rename(f"files/{user['email']}/{database.getFilenameWithFileId(fileid)}", f"files/{user['email']}/{request.json['name']}")
        database.renameFile(fileid, request.json['name'])
    except:
        return response.json({'error': 'File not found'}, status=404)
    return response.json({'success': True, "message": "Renamed"}, status=200)

@app.post('/files/<fileid>/accesses')
async def append_file_accesses(request, fileid):
    user = verify_token(request)
    if not user:
        return response.json({'error': 'Unauthorised'}, status=401)
    if not database.IsUserFileOwner(fileid, user['email']):
        return response.json({'error': 'Access not allowed'}, status=403)
    if not request.json:
        return response.json({'error': 'email not provided'}, status=400)
    if not 'email' in request.json:
        return response.json({'error': 'email not provided'}, status=400)
    email = request.json['email']
    if email == user['email']:
        return response.json({'error': 'You cannot add yourself as an access'}, status=400)
    status = database.AppendFileAccesses(fileid, email)
    if status == 5000:
        return response.json({'error': 'Email not registered'}, status=400)
    elif status == 10000:
        return response.json({'error': 'Email already in access list'}, status=400)
    
    accesses=database.getFileAccesses(fileid)[0]
    output = []
    owner = database.getUserInfoByEmail(user['email'])
    output.append({
        "fullname": owner[2] + " " + owner[3],
        "email": owner[0],
        "type": "author"
    })
    if accesses:
        for access in accesses.split(':'):
            info = database.getUserInfoByEmail(access)
            output.append({
                "fullname": info[2] + " " + info[3],
                "email": info[0],
                "type": "co-author"
            })
    return response.json(output, status=200)
@app.delete('/files/<fileid>/accesses')
async def delete_file_accesses(request, fileid):
    user = verify_token(request)
    if not user:
        return response.json({'error': 'Unauthorised'}, status=401)
    if not database.IsUserFileOwner(fileid, user['email']):
        return response.json({'error': 'Access not allowed'}, status=403)
    if not request.json:
        return response.json({'error': 'email not provided'}, status=400)
    if not 'email' in request.json:
        return response.json({'error': 'email not provided'}, status=400)
    email = request.json['email']
    status = database.DeleteFileAccesses(fileid, email)
    if status == 10000:
        return response.json({'error': 'Email is not in access list'}, status=400)
    
    accesses=database.getFileAccesses(fileid)[0]
    output = []
    owner = database.getUserInfoByEmail(user['email'])
    output.append({
        "fullname": owner[2] + " " + owner[3],
        "email": owner[0],
        "type": "author"
    })
    if accesses:
        for access in accesses.split(':'):
            info = database.getUserInfoByEmail(access)
            output.append({
                "fullname": info[2] + " " + info[3],
                "email": info[0],
                "type": "co-author"
            })
    return response.json(output, status=200)
@app.get('/files/<fileid>/accesses')
async def get_file_accesses(request, fileid):
    user = verify_token(request)
    if not user:
        return response.json({'error': 'Unauthorised'}, status=401)
    if not database.IsUserFileOwner(fileid, user['email']):
        return response.json({'error': 'Access not allowed'}, status=403)
    accesses=database.getFileAccesses(fileid)[0]
    output = []
    owner = database.getUserInfoByEmail(user['email'])
    output.append({
        "fullname": owner[2] + " " + owner[3],
        "email": owner[0],
        "type": "author"
    })
    if accesses:
        for access in accesses.split(':'):
            info = database.getUserInfoByEmail(access)
            output.append({
                "fullname": info[2] + " " + info[3],
                "email": info[0],
                "type": "co-author"
            })
    return response.json(output, status=200)
@app.get('/files/disk')
async def getUserFiles(request):
    user = verify_token(request)
    if not user:
        return response.json({'error': 'Unauthorised'}, status=401)
    output = []
    for file in database.getUserFiles(user['email']):
        accesses = database.getFileAccesses(file[0])
        accesslist = []
        owner = database.getUserInfoByEmail(user['email'])
        accesslist.append({
            "fullname": owner[2] + " " + owner[3],
            "email": owner[0],
            "type": "author"
        })
        if accesses[0]:
            for access in accesses[0].split(':'):
                info = database.getUserInfoByEmail(access)
                accesslist.append({
                    "fullname": info[2] + " " + info[3],
                    "email": info[0],
                    "type": "co-author"
                })
        output.append({
            'file_id' : file[0],
            'name' : file[1],
            'url' : '/files/' + str(file[0]),
            'accesses' : accesslist
        })
    return response.json(output, status=200)
@app.get('/files/shared')
async def getUserSharedFiles(request):
    user = verify_token(request)
    if not user:
        return response.json({'error': 'Unauthorised'}, status=401)
    output = []
    for file in database.getUserSharedFiles(user['email']):
        output.append({
            'file_id' : file[0],
            'name' : file[1],
            'url' : '/files/' + str(file[0])
        })
    return response.json(output, status=200)

@app.post('/files')
async def files_upload(request):
    user = verify_token(request)
    if not user:
        return response.json({'error': 'Unauthorised'}, status=401)
    
    if 'file' not in request.files:
        return response.json({'error': 'No file part'}, status=400)
    output = []
    uploaded_files = request.files
    for uploaded_file in uploaded_files.values():
        try:
            await save_file(uploaded_file[0], user['email'])
            output.append({
                "success" : True,
                "message" : "Success",
                "name": uploaded_file[0].name,
                "url": "/files/" + uploaded_file[0].name,
                "file_id": database.getFileId(uploaded_file[0].name, user['email'])
            })
        except:
            output.append({
                "success" : False,
                "message" : "File not loaded",
                "name": uploaded_file[0].name
            })
    return response.json(output, status=200)

async def save_file(uploaded_file, email):
    save_path = f"./files/{email}/" + uploaded_file.name
    os.makedirs(f"./files/{email}/", exist_ok=True)
    if os.path.isfile(save_path):
        raise Exception(f"File {uploaded_file.name} already exists")
    with open(save_path, 'wb') as f:
        f.write(uploaded_file.body)
    return database.registerfile(uploaded_file.name, email)

#endregion

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=3000, debug=False)