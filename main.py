from sanic import Sanic, response, HTTPResponse, json, redirect, html, file, empty
from sanic import Sanic
from sanic_cors import CORS
from sanic.response import text, html
import base64
from database import Database
from datetime import datetime, date
from jinja2 import Environment, FileSystemLoader, select_autoescape
import random
import os
import string
import uuid
import re
from PIL import Image, ImageDraw, ImageFont
import io
import os

app = Sanic("WorldSkillsApiV2")

tokens = {}

env = Environment(
    loader=FileSystemLoader('templates'),  # Папка с шаблонами
    autoescape=select_autoescape(['html', 'xml'])
)
CORS(app, resources={"*": {"origins": "*"}})

app.static("/static/", "./static/")

#region default_responses
def unauthorized_response():
    return json({"message":"Login failed"}, status=403)

def forbidden_response():
    return json({"message":"Forbidden for you"}, status=403)

def not_found_response():
    return json({"message":"Not found", "status":404}, status=404)

def error_response(errors:dict={}, message:str='Validation Error', status_code:int=422):
    return json({
            "error":{
                "code":status_code,
                "message":message,
                "errors":errors
            }
        }, status=status_code)

def empty_response():
    return empty(status=204)
#endregion
#region funcs
def getrandomstring(length):
    return ''.join(random.choice(string.ascii_letters + string.digits) for _ in range(length))
#endregion
#region pages
@app.get('/')
async def indexPage(request):
    template = env.get_template('index.html')
    return response.html(template.render())
#endregion

def generatetoken():
    token = uuid.uuid4().hex
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
        return error_response({"json":["data not found"]}, "Authorization failed", 400)
    email = request.json.get('email')
    messages = {}
    if not email:
        messages['email'] = ['email cannot be blank']
    password = request.json.get('password')
    if not password:
        messages['password'] = ['password cannot be blank']
    if messages:
        return error_response(messages, "Validation error", 422)
    password = request.json.get('password')
    dbresp = Database.authenticate_user(email, password)
    if dbresp:
        token = generatetoken()
        #TODO: FIX
        tokens[token]={'email':email,'password':password}
        return json({"data":{
                        "user":{
                            "id": dbresp["id"],
                            "name": dbresp["name"],
                            "birth_date": dbresp["birth_date"],
                            "email": dbresp["email"]
                        }
                    },
                    "token": token}, status=200)
    else:
        return unauthorized_response()

@app.post("/registration")
async def registration(request):
    global tokens
    if not request.json:
        return error_response({"json":["data not found"]}, "Validation error", 422)
    messages = {}
    first_name = request.json.get('first_name')
    if not first_name:
        messages['first_name'] = ['first_name cannot be blank']
    last_name = request.json.get('last_name')
    if not last_name:
        messages['last_name'] = ['last_name cannot be blank']
    patronymic = request.json.get('patronymic')
    if not patronymic:
        messages['patronymic'] = ['patronymic cannot be blank']
    email = request.json.get('email')
    if not email:
        messages['email'] = ['email cannot be blank']
    password = request.json.get('password')
    if not password:
        messages['password'] = ['password cannot be blank']
        
    if password and not re.match(r"^(?=(.*[a-z]))(?=(.*[A-Z]))(?=(.*\d)).{3,}$",password):
        messages['password'] = ['password is too easy']
        
    birth_date = request.json.get('birth_date')
    
    if not birth_date:
        messages['birth_date'] = ['birth_date cannot be blank']
        
    if birth_date:
        try:
            datetime.strptime(birth_date, "%Y-%m-%d")
        except:
            messages['birth_date'] = ['birth_date is in incorrect format']
    if messages:
        return error_response(messages, "Validation error", 422)
    
    if not Database.register_user(first_name, last_name, patronymic, email, password, birth_date):
        return error_response({}, "Пользователь с таким Email уже существует", 400)
    token = generatetoken()
    tokens[token]={'email':email,'password':password,"first_name":first_name, "first_name":last_name}
    return json({
            "data":{
                "user":{
                    "name": f"{first_name} {last_name} {patronymic}",
                    "email": email
                },
                "code":201,
                "message":"Пользователь создан"
            }
        }, status=201)

@app.get('/logout')
async def logout(request):
    if verify_token(request):
        del tokens[get_token(request)]
        return empty_response()
    else:
        return unauthorized_response()

@app.get("/api/gagarin-flight")
async def get_gagarin_flight(request):
    if not verify_token(request):
        return unauthorized_response()
    return json(Database.get_gagarin_mission())

@app.get("/flight")
async def get_flight(request):
    if not verify_token(request):
        return unauthorized_response()
    return json({
    "data": {
    "name": "Аполлон-11",
    "crew_capacity": 3,
    "cosmonaut": [
    {
        "name": "Нил Армстронг",

        "role": "Командир"
    },
    {
        "name": "Базз Олдрин",
        "role": "Пилот лунного модуля"
    },
    {
        "name": "Майкл Коллинз",
        "role": "Пилот командного модуля"
    }
    ],
    "launch_details": {
    "launch_date": "1969-07-16",
    "launch_site": {
        "name": "Космический центр имени Кеннеди",
        "latitude": "28.5721000",
        "longitude": "-80.6480000"
    }
    },
    "landing_details": {
    "landing_date": "1969-07-20",
    "landing_site": {
        "name": "Море спокойствия",
        "latitude": "0.6740000",
        "longitude": "23.4720000"
    }}}
}, status=200)
    

@app.get("/lunar-missions")
async def get_lunar_missions(request):
    if not verify_token(request):
        return unauthorized_response()
    return json([
  {
    "mission": {
      "name": "Аполлон-11",

      "launch_details": {
        "launch_date": "1969-07-16",

        "launch_site": {
          "name": "Космический центр имени Кеннеди",

          "location": {
            "latitude": "28.5721000",

            "longitude": "-80.6480000"
          }
        }
      },

      "landing_details": {
        "landing_date": "1969-07-20",

        "landing_site": {
          "name": "Море спокойствия",

          "coordinates": {
            "latitude": "0.6740000",

            "longitude": "23.4720000"
          }
        }
      },

      "spacecraft": {
        "command_module": "Колумбия",

        "lunar_module": "Орел",

        "crew": [
          {
            "name": "Нил Армстронг",

            "role": "Командир"
          },

          {
            "name": "Базз Олдрин",

            "role": "Пилот лунного модуля"
          },

          {
            "name": "Майкл Коллинз",

            "role": "Пилот командного модуля"
          }
        ]
      }
    }
  },

  {
    "mission": {
      "name": "Аполлон-17",

      "launch_details": {
        "launch_date": "1972-12-07",

        "launch_site": {
          "name": "Космический центр имени Кеннеди",

          "location": {
            "latitude": "28.5721000",

            "longitude": "-80.6480000"
          }
        }
      },

      "landing_details": {
        "landing_date": "1972-12-19",

        "landing_site": {
          "name": "Телец-Литтров",

          "coordinates": {
            "latitude": "20.1908000",

            "longitude": "30.7717000"
          }
        }
      },

      "spacecraft": {
        "command_module": "Америка",

        "lunar_module": "Челленджер",

        "crew": [
          {
            "name": "Евгений Сернан",

            "role": "Командир"
          },

          {
            "name": "Харрисон Шмитт",

            "role": "Пилот лунного модуля"
          },

          {
            "name": "Рональд Эванс",

            "role": "Пилот командного модуля"
          }
        ]
      }
    }
  }
]
)
    
def validate_lunar_missions_json(data):
    errors = {}
    data = data['mission']
    # Обязательные поля на уровне миссии
    mission_keys = ['name', 'launch_details', 'landing_details', 'spacecraft']
    for key in mission_keys:
        if key not in data:
            errors[key] = [f'field {key} can not be blank']

    # Обязательные поля для launch_details
    if 'launch_details' in data:
        launch_details = data['launch_details']
        if 'launch_date' not in launch_details or not launch_details['launch_date']:
            errors['launch_date'] = ['field launch_details can not be blank']
        if 'launch_site' not in launch_details or not launch_details['launch_site']:
            errors['launch_site'] = ['field launch_site can not be blank']
        else:
            launch_site = launch_details['launch_site']
            if 'name' not in launch_site or not launch_site['name']:
                errors['launch_site_name'] = ['field launch_site_name can not be blank']
            if 'location' not in launch_site or not launch_site['location']:
                errors['launch_site_location'] = ['field launch_site_location can not be blank']
            else:
                location = launch_site['location']
                if 'latitude' not in location or 'longitude' not in location:
                    errors['launch_site_coordinates'] = ['field launch_site_coordinates can not be blank']

    # Обязательные поля для landing_details
    if 'landing_details' in data:
        landing_details = data['landing_details']
        if 'landing_date' not in landing_details or not landing_details['landing_date']:
            errors['landing_date'] = ['field landing_date can not be blank']
        if 'landing_site' not in landing_details or not landing_details['landing_site']:
            errors['landing_site'] = ['field landing_site can not be blank']
        else:
            landing_site = landing_details['landing_site']
            if 'name' not in landing_site or not landing_site['name']:
                errors['landing_site_name'] = ['field landing_site_name can not be blank']
            if 'coordinates' not in landing_site or not landing_site['coordinates']:
                errors['landing_site_coordinates'] = ['field landing_site_coordinates can not be blank']
            else:
                coordinates = landing_site['coordinates']
                if 'latitude' not in coordinates or 'longitude' not in coordinates:
                    errors['landing_site_coordinates_values'] = ['field landing_site_coordinates_values can not be blank']

    # Обязательные поля для spacecraft
    if 'spacecraft' in data:
        spacecraft = data['spacecraft']
        if 'command_module' not in spacecraft or not spacecraft['command_module']:
            errors['command_module'] = ['field command_module can not be blank']
        if 'lunar_module' not in spacecraft or not spacecraft['lunar_module']:
            errors['lunar_module'] = ['field lunar_module can not be blank']
        if 'crew' not in spacecraft or not spacecraft['crew']:
            errors['crew'] = ['field crew can not be blank']
        else:
            crew = spacecraft['crew']
            for index, member in enumerate(crew):
                if 'name' not in member or not member['name']:
                    errors[f'crew_member_{index}_name'] = ['field crew_member_name can not be blank']
                if 'role' not in member or not member['role']:
                    errors[f'crew_member_{index}_role'] = ['field crew_member_role can not be blank']

    return errors
    
@app.post("/lunar-missions")
async def create_lunar_mission(request):
    if not verify_token(request):
        return unauthorized_response()
    data = request.json
    errors = validate_lunar_missions_json(data)
    
    if errors:
        return error_response(errors, "Validation error", 422)

    # Если ошибок нет, обрабатываем данные
    return json({ 
"data":{ 
"code":201, 
"message":"Миссия добавлена" 
} 
} , status=201)

@app.delete("/lunar-missions/<mission_id:int>")
async def del_lunar_mission(request, mission_id):
    if not verify_token(request):
        return unauthorized_response()
    if not mission_id:
        return error_response({mission_id:['mission_id can not be blank']},"Validation error", 400)
    if mission_id>10:
        return not_found_response()
    return empty_response()

@app.patch("/lunar-missions/<mission_id:int>")
async def patch_lunar_missions(request, mission_id):
    if not verify_token(request):
        return unauthorized_response()
    data = request.json
    errors = validate_lunar_missions_json(data)
    
    if errors:
        return error_response(errors, "Validation error", 422)

    # Если ошибок нет, обрабатываем данные
    return json({ 
"data":{ 
"code":201, 
"message":"Миссия обновлена" 
} 
} , status=201)



@app.post("/lunar-watermark")
async def create_lunar_watermark(request):
    if not verify_token(request):
        return unauthorized_response()
    errors = {}
    fileimage = request.files.get("fileimage")
    if not fileimage:
        errors['fileimage'] = ["no fileimage provided"]
    message = request.form.get("message")
    if not message:
        errors['message'] = ["no message provided"]
    if errors:
        return error_response(errors, "Validation error", 422)
    if fileimage:
        image = Image.open(io.BytesIO(fileimage.body))
        width, height = image.size
        draw = ImageDraw.Draw(image)
        text = message
        font_size = height/4
        opacity = 128
        text_color = (255, 255, 255, opacity)
        draw.text((0,0),font_size=font_size, font=ImageFont.truetype("DejaVuSans.ttf" , font_size), text=text, fill=text_color)
        img_byte_arr = io.BytesIO()
        image.save(img_byte_arr, format="PNG")
        img_byte_arr.seek(0)
        output_path = 'output_image.png'
        image.save(output_path, format="PNG")
        return await file(output_path)

@app.get("/space-flights")
async def get_space_flights(request):
    if not verify_token(request):
        return unauthorized_response()
    return json(
    {
"data": [
    {
        "flight_number": "СФ-103",

        "destination": "Марс",

        "launch_date": "2025-05-15",

        "seats_available": 2
    },

    {
        "flight_number": "СФ-105",

        "destination": "Юпитер",

        "launch_date": "2024-06-01",

        "seats_available": 3
    }
    ]
}, status=200)

@app.post("/space-flights")
async def create_space_flight(request):
    if not verify_token(request):
        return unauthorized_response()
    errors = {}
    if not request.json.get("flight_number"):
        errors["flight_number"] = ['flight_number is blank']
    if not request.json.get("destination"):
        errors["destination"] = ['destination is blank']
    if not request.json.get("launch_date"):
        errors["launch_date"] = ['launch_date is blank']
    if not request.json.get("seats_available"):
        errors["seats_available"] = ['seats_available is blank']
    if errors:
        return error_response(errors, 'Validation Error', 422)
    return json({ 
"data":{ 
"code":201, 
"message":"Космический полет создан" 
} 
} )

@app.post("/book-flight")
async def book_flight(request):
    if not verify_token(request):
        return unauthorized_response()
    number = request.json.get("flight_number")
    if not number:
        return error_response({"flight_number":['field flight_number cannot be blank']}, message='Validation Error', status_code=422)
    return json({
        "data": {
        "code": 201,
        "message": "Рейс забронирован"
        }
    }
)
missions = [{
    "mission": {
        "name": "Аполлон-11",
        "launch_details": {
        "launch_date": "1969-07-16",
        "launch_site": {
            "name": "Космический центр имени Кеннеди",
            "location": {
                "latitude": "28.5721000",
                "longitude": "-80.6480000"
            }
        }
    },

    "landing_details": {
        "landing_date": "1969-07-20",

        "landing_site": {
            "name": "Море спокойствия",

            "coordinates": {
            "latitude": "0.6740000",

            "longitude": "23.4720000"
            }
        }
        },

    "spacecraft": {
        "command_module": "Колумбия",

        "lunar_module": "Орел",

        "crew": [
        {
            "name": "Нил Армстронг",

            "role": "Командир"
        },

        {
            "name": "Базз Олдрин",

            "role": "Пилот лунного модуля"
        },

        {
            "name": "Майкл Коллинз",

            "role": "Пилот командного модуля"
        }
        ]
        }
    }
},
{
    "mission": {
    "name": "Аполлон-17",
    "launch_details": {
        "launch_date": "1972-12-07",
        "launch_site": {
            "name": "Космический центр имени Кеннеди",
            "location": {
                "latitude": "28.5721000",
                "longitude": "-80.6480000"
            }
        }
    },

    "landing_details": {
        "landing_date": "1972-12-19",
        "landing_site": {
        "name": "Телец-Литтров",
        "coordinates": {
            "latitude": "20.1908000",
            "longitude": "30.7717000"
            }
        }
    },

    "spacecraft": {
        "command_module": "Америка",
        "lunar_module": "Челленджер",
        "crew": [
        {
            "name": "Евгений Сернан",
            "role": "Командир"
        },
        {
            "name": "Харрисон Шмитт",
            "role": "Пилот лунного модуля"
        },
        {
            "name": "Рональд Эванс",
            "role": "Пилот командного модуля"
        }
        ]
        }
    }
},
{
            "mission": {
                "name": "Восток 1",
                "launch_details": {
                    "launch_date": "1961-04-12",
                    "launch_site": {
                        "name": "Космодром Байконур",
                        "location": {
                            "latitude": "45.9650000",
                            "longitude": "63.3050000"
                        }
                    }
                },
                "flight_duration": {
                    "hours": 1,
                    "minutes": 48
                },
                "spacecraft": {
                    "name": "Восток 3KA",
                    "manufacturer": "OKB-1",
                    "crew_capacity": 1
                }
            },
            "landing": {
                "date": "1961-04-12",
                "site": {
                    "name": "Смеловка",
                    "country": "СССР",
                    "coordinates": {
                        "latitude": "51.2700000",
                        "longitude": "45.9970000"
                    }
                },
                "details": {
                    "parachute_landing": 1,
                    "impact_velocity_mps": 7
                }
            },
            "cosmonaut": {
                "name": "Юрий Гагарин",
                "birthdate": "1934-03-09",
                "rank": "Старший лейтенант",
                "bio": {
                    "early_life": "Родился в Клушино, Россия.",
                    "career": "Отобран в отряд космонавтов в 1960 году...",
                    "post_flight": "Стал международным героем."
                }
            }
        }
]
@app.get('/search')
async def search(request):
    if not verify_token(request):
        return unauthorized_response()
    
    searchparam = request.args.get('query')
    if not searchparam:
        return error_response({'query':["query cannot be blank"]}, message='Validation Error', status_code=422)
    output = []
    for m in missions:
        try:
            if searchparam.lower() in m['mission']['name'].lower() or searchparam.lower() in m['mission']['spacecraft']['name'].lower():
                output.append(m)
        except:
            continue
    if output:
        return json(output, status=200)
    return not_found_response()

@app.get("/api-file")
async def api_docs_and_html(request):
    return await file("api-file.zip")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=3000, debug=False)