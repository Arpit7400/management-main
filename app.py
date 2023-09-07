from flask import Flask, request, jsonify, render_template
from flask_pymongo import PyMongo, MongoClient
from datetime import datetime
from bson import ObjectId

app = Flask(__name__)
app.config["MONGO_URI"] = "mongodb://localhost:27017/newdatabse"
mongo = PyMongo(app)
# client = MongoClient("mongodb://localhost:27017")
# mongo = client["newdatabase"]
# mongo_m = client["management"]


app.config["MONGO_URI"] = "mongodb://localhost:27017/newdatabse_management"
mongo_m = PyMongo(app)

@app.route('/')
def xyz():
    return render_template('class_post.html')

# API endpoints
def get_entities(collection_name, dbinitialize):
    all_entities = list(dbinitialize.db[collection_name].find())
    return jsonify(all_entities)

def get_entity(collection_name, entity_id, dbinitialize):
    entity = dbinitialize.db[collection_name].find_one({"_id": entity_id})
    return entity

def update_entity(collection_name, entity_id, entity_data, dbinitialize):
    result = dbinitialize.db[collection_name].update_one({"_id": entity_id},
                                                  {"$set": entity_data})
    if result.modified_count == 0:
        return jsonify({"error": f"{collection_name.capitalize()} notfound"}), 404
    updated_entity = dbinitialize.db[collection_name].find_one({"_id": entity_id})
    return jsonify(updated_entity)

#geting boards name available in curriculum 
@app.route('/board', methods=['GET'])                                                                   #checked
def get_boards():
    return get_entities('boards',mongo)


# Class operations
@app.route('/class', methods=['GET'])  #fetching class name in create class & sec from curri            #checked
def get_classes():
    return get_entities('school_classes', mongo)

#create section by giving class id 
@app.route('/class/<string:class_id>', methods=['POST'])                                                #checked
def create_class(class_id):
    class_extract = get_entity('school_classes', class_id, mongo)
    name = class_extract['name']
    section = request.form.get('section')
    strength = request.form.get('strength')
    existing_class = mongo_m.db.school_class_sec.find_one({"name": name, "section": section})
    if existing_class is not None:
        return jsonify({"error": "Class with the same name and section already exists"}), 400
    class_data = {
        "_id": str(ObjectId()),
        "name": name,
        "section": section, #by default set A 
        "strength": strength, # can be empty 
        "blocked": False
    }
    try:
        inserted_id = mongo_m.db.school_class_sec.insert_one(class_data).inserted_id
        inserted = mongo_m.db.school_class_sec.find_one({"_id": inserted_id})
        return jsonify({"_id": str(inserted["_id"]), "section": inserted["section"], "strength": inserted["strength"]})
    except Exception as e:
        return jsonify({"error": "Error occurred while creating the class"}), 500

#api to fetch all sections                                                                           #checked
@app.route('/class/all_section/<string:classname>', methods=['GET'])
def get_all_section(classname):
    print("hello")
    try:
        print("try")
        sec_of_class = mongo_m.db.school_class_sec.find({"name": classname})
        print(sec_of_class)
        all_sec = []
        for sec in sec_of_class:
            all_sec.append(sec["section"])
        if not all_sec:
            return jsonify({"error": f"No sections found for class '{classname}'"}), 404
        return jsonify(all_sec)

    except Exception as e:
        return jsonify({"error": str(e)}), 500

# @app.route('/class/all_section/<string:classname>', methods=['GET'])
# def get_all_section(classname):
#     try:
#         sec_of_class = mongo_m.db.school_class_sec.find({"name": classname})
#         all_sec = [sec["section"] for sec in list(sec_of_class)]

#         if not all_sec:
#             return jsonify({"error": f"No sections found for class '{classname}'"}), 404

#         return jsonify({"sections": all_sec}), 200

#     except Exception as e:
#         return jsonify({"error": str(e)}), 500

#get class and section from management database
@app.route('/class/section/<string:class_id>', methods=['GET'])                                          #checked
def get_class(class_id): #fetching all classes and sec 
    return get_entity('school_class_sec', class_id, mongo_m)

#getting class by its name
@app.route('/class/names/<string:name>', methods=['GET'])                                                #checked
def get_class_Data(name):
    try:
        book = mongo.db.school_classes.find_one({"name": name})
        if (book):
            return jsonify(book)
        else:
            return jsonify({"error": "No book found for the provided id"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500

#update class details 
@app.route('/class/<string:class_id>', methods=['PUT'])                                                 #checked
def update_class(class_id):
    print(class_id)
    class_data = {}
    if 'name' in request.form:
        class_data['name'] = request.form.get('name')
        class_data['section'] = request.form.get('section')
        class_data['strength'] = request.form.get('strength')

        return update_entity('school_class_sec', class_id, class_data, mongo_m)
    else:
        return "Error", 415
#subject operations
#getting all subjects from curriculum
@app.route('/subject', methods=['GET'])                                                                  #checked
def get_subject():
    return get_entities('books', mongo)

#saving subject in management
@app.route('/subject/save/<string:name>', methods= ['POST'])                                            #checked
def save_subject(name):
    result = mongo_m.db.subjects.find_one({"name": name})
    if result is None:
        new_subject = {
            "_id": str(ObjectId()),
            "name": name,
            "blocked": False
        }
        inserted_id = mongo_m.db.subjects.insert_one(new_subject).inserted_id
        inserted = mongo_m.db.subjects.find_one({"_id": inserted_id})
        return jsonify({"_id": str(inserted["_id"]), "name": inserted["name"]}), 201
    else:
        return "Alreaady Exist", 201

#getting all subjects from management                                                               #checked
@app.route('/subject_m', methods=['GET'])
def get_subject_m():
    return get_entities('subjects', mongo_m)         


#API to creata subject in management                                                                 #checked
@app.route('/api/create_subject', methods=['POST'])
def create_subject():
    subject_name = request.form.get('name')  # Use request.form to access form data
    if not subject_name:
        return jsonify({'message': 'Please provide the subject name'}), 400

    new_subject = {
        "_id": str(ObjectId()),
        "name": subject_name,
        "blocked": False
    }
    inserted_id = mongo_m.db.subjects.insert_one(new_subject).inserted_id
    inserted = mongo_m.db.subjects.find_one({"_id": inserted_id})
    return jsonify({"_id": str(inserted["_id"]), "name": inserted["name"]}), 201

#create assign subject
@app.route('/class/assign/subject/create', methods= ['POST'])                                            #checked
def assign_subject_create():
    subject_name = request.form.get("subject")
    class_assign = request.form.get("name")
    section = request.form.get("section")
    existing_class = mongo_m.db.subject_assign.find_one(
        {"subject": subject_name, "name": class_assign,"section": section})
    if existing_class:
        return jsonify({"error": "Class with the same name and section already exists"}), 400
    assign_data={
        "_id": str(ObjectId()),
        "name": class_assign,
        "section":section,
        "subject":subject_name
    }
    inserted_id = mongo_m.db.subject_assign.insert_one(assign_data).inserted_id
    inserted = mongo_m.db.subject_assign.find_one({"_id": inserted_id})
    return jsonify({"_id": str(inserted["_id"]), "name": inserted["name"]}), 201

#fetch all class,section,subjects that are assign to class
@app.route('/class/assign/subject', methods= ["GET"])                                                   #checked
def get_all_class_subject():
    return get_entities("subject_assign", mongo_m)

# BookName operations
@app.route('/bookname', methods=['POST'])                                                               #checked
def create_bookname():
    # if 'name' not in request.json or 'subject' not in request.json or 'class' not in request.json or 'publication' not in request.json:
    #     return jsonify({"error": "Missing name, board, subject, or publication in request"}), 400

    name = request.form.get('name')
    subject = request.form.get('subject')
    board = request.form.get('board')
    class_name = request.form.get('class')
    publication = request.form.get('publication')
    section = request.form.get('section')

    bookname_data = {
        "_id": str(ObjectId()),
        "board": board,
        "class": class_name,
        "section": section,
        "publication": publication,
        "name": name,
        "subject": subject,
        "blocked": False
    }
    # return create_entity('booknames', bookname_data)
    inserted_id = mongo_m.db.booknames.insert_one(bookname_data).inserted_id
    inserted = mongo_m.db.booknames.find_one({"_id": inserted_id})
    inserted["_id"] = str(inserted["_id"])
    return jsonify(inserted)

#fetching all booknames from curriculum database
@app.route('/bookname', methods=['GET'])                                                                 #checked
def get_booknames():
    return get_entities('booknames', mongo)

#fetching single bookname
@app.route('/bookname/<string:bookname_id>', methods=['GET'])                                             #checked
def get_bookname(bookname_id):
    return get_entity('booknames', bookname_id, mongo)

#update bookname
# @app.route('/bookname/<string:bookname_id>', methods=['PUT'])
# def update_bookname(bookname_id):
#     bookname_data = {}
#     if 'name' in request.json:
#         bookname_data['name'] = request.json['name']
#     if 'stream_id' in request.json:
#         bookname_data['stream_id'] = request.json['stream_id']
#     if 'class_id' in request.json:
#         bookname_data['class_id'] = request.json['class_id']
#     if 'publication_id' in request.json:
#         bookname_data['publication_id'] = request.json['publication_id']

#     return update_entity('booknames', bookname_id, bookname_data, mongo)

#publication details
@app.route('/publication', methods=['GET'])                                                             #checked
def get_publications():
    return get_entities('publications', mongo)


@app.route('/publication/<string:publication_id>', methods=['GET'])                                     #checked
def get_publication(publication_id):
    return get_entity('publications', publication_id, mongo)


### All about Schedule

# Define a function to check if a time slot is available for a teacher in a class and section
def is_time_slot_available(teacher_id, class_id, section_id, day_id, subject_id, start_time, end_time):
    existing_schedule = mongo_m.db.schedule.find_one({
        'teacher_id': teacher_id,
        'class_id': class_id,
        'section_id': section_id,
        'day_id' : day_id,
        'subject_id': subject_id,
        'start_time': {'$lt': end_time},
        'end_time': {'$gt': start_time}
    })
    return existing_schedule is None


# API to assign a Day
@app.route('/api/create_days', methods=['POST'])                                                       #checked
def create_day():
    day_name = request.form.get('name')  # Use request.form to access form data
    if not day_name:
        return jsonify({'message': 'Please provide the day name'}), 400

    new_day = {
        'name': day_name,
    }
    result = mongo_m.db.days.insert_one(new_day)
    return jsonify({'message': 'Day created successfully', 'id': str(result.inserted_id), 'name': day_name}), 201


# API to create a new teacher
@app.route('/api/create_teacher', methods=['POST'])                                             #checked
def create_teacher():
    teacher_name = request.form.get('name')  # Use request.form to access form data
    if not teacher_name:
        return jsonify({'message': 'Please provide the teacher name'}), 400

    new_teacher = {
        'name': teacher_name,
    }
    result = mongo_m.db.teachers.insert_one(new_teacher)
    return jsonify({'message': 'Teacher created successfully', 'id': str(result.inserted_id), 'name': teacher_name}), 201

# API to create a new activity
@app.route('/api/create_activity', methods=['POST'])                                                #checked
def create_activity():
    activity_name = request.form.get('name')
    if not activity_name:
        return jsonify({'message': 'Please provide the activity name'}), 400

    existing_activity = mongo_m.db.activities.find_one({'name': activity_name})
    if existing_activity:
        return jsonify({'message': 'Activity already exists', 'id': str(existing_activity['_id'])}), 200

    new_activity = {
        'name': activity_name,
    }
    result = mongo_m.db.activities.insert_one(new_activity)
    return jsonify({'message': 'Activity created successfully', 'id': str(result.inserted_id), 'name': activity_name}), 201

# API to create a new break 
@app.route('/api/create_break', methods=['POST'])                                               #checked
def create_break():
    break_name = request.form.get('name')
    if not break_name:
        return jsonify({'message': 'Please provide the break name'}), 400

    existing_break = mongo_m.db.breaks.find_one({'name': break_name})
    if existing_break:
        return jsonify({'message': 'Break already exists', 'id': str(existing_break['_id']), 'name': str(existing_break['name'])}), 200

    new_break = {
        'name': break_name,
    }
    result = mongo_m.db.breaks.insert_one(new_break)
    return jsonify({'message': 'Break created successfully', 'id': str(result.inserted_id), 'name': break_name}), 201

# API to create a new schedule
# API to create a new lecture schedule
@app.route('/api/create_schedule', methods=['POST'])                                            #checked
def create_schedule():
    teacher = request.form.get('teacher')
    class_name = request.form.get('class')
    section = request.form.get('section')
    day = request.form.get('day')
    # start_time = datetime.strptime(request.form.get('start_time'), '%H:%M')
    # end_time = datetime.strptime(request.form.get('endtime'), '%H:%M')
    start_time = request.form.get('start_time')
    end_time = request.form.get('end_time')

    subject = request.form.get('subject')
    activity = request.form.get('activity')
    break_c = request.form.get('break')

    # Check if exactly one of Subject, Activity, or Break is chosen
    if not ((subject and not activity and not break_c) or
            (activity and not subject and not break_c) or
            (break_c and not subject and not activity)):
        return jsonify({'message': 'You must choose exactly one of Subject, Activity, or Break.'}), 400

    # Disable input fields on the server side based on the chosen option
    if subject:
        activity = None
        break_c = None
    elif activity:
        subject = None
        break_c = None
    else:
        subject = None
        activity = None

    # Check if the time slot is available
    existing_schedule = mongo_m.db.schedule.find_one({
        'teacher': teacher,
        'day': day,
        'start_time': {'$lt': end_time},
        'end_time': {'$gt': start_time}
    })

    if existing_schedule:
        return jsonify({'message': 'Teacher already has a lecture scheduled during this time'}), 400

    new_schedule = {
        'teacher': teacher,
        'class': class_name,
        'section': section,
        'day': day,
        'start_time': start_time,
        'end_time': end_time,
    }

    if subject:
        new_schedule['subject'] = subject
    elif activity:
        new_schedule['activity'] = activity
    else:
        new_schedule['break'] = break_c

    result = mongo_m.db.schedule.insert_one(new_schedule)
    return jsonify({'message': 'Lecture scheduled successfully', 'id': str(result.inserted_id)}), 201


# Route to fetch teachers from the database
@app.route('/api/get_teachers', methods=['GET'])                                                        #checked
def get_teachers():
    teachers = mongo_m.db.teachers.find()
    return jsonify([{"_id": str(t['_id']), "name": t['name']} for t in teachers])

# Route to fetch activities from the database
@app.route('/api/get_activities', methods=['GET'])                                                      #checked
def get_activities():
    activities = mongo_m.db.activities.find()
    return jsonify([{"_id": str(a['_id']), "name": a['name']} for a in activities])

# Route to fetch breaks from the database
@app.route('/api/get_breaks', methods=['GET'])                                                           #checked
def get_breaks():
    breaks = mongo_m.db.breaks.find()
    return jsonify([{"_id": str(b['_id']), "name": b['name']} for b in breaks])


if __name__ == "__main__":
    app.run(debug=True)