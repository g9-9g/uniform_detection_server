from werkzeug.utils import secure_filename
import os
import json 

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'}

def tail(filename):
    return filename.rsplit('.', 1)[1].lower()

def head(filename):
    if '_' in filename:
        return filename.rsplit('_', 1)[0].lower()
    
    return None

def allowed_uid (userids):
    return userids.isnumeric()

def handle_files (request, save_dir):
    # files = request.files.getlist('images')
    # userIDs = request.form['textlist'].split(' ')
    userIDs = request.form.getlist('uids')
    print(userIDs, type(userIDs),len(userIDs))

    if not (isinstance(userIDs, list) and len(userIDs) > 0):
        raise Exception('Invalid userids')

    # if len(userIDs) != len(files):
    #     raise Exception("Number of images and userIDs are not equal")
    
    data = {}

    for userID in userIDs:
        userID = str(userID)
        if not allowed_uid(userID) or not userID in request.files:
            continue

        data[userID] = []
        files = request.files.getlist(userID)
        for i,file in enumerate(files):
            if file and allowed_file(file.filename):
                filename = secure_filename(userID+'_'+str(i)+'.'+tail(file.filename))
                print(filename)
                file.save(os.path.join(save_dir, filename))
                data[userID].append(os.path.join(save_dir, filename))
                
    print(data)

    return data,userIDs
    # data = []

    # for file, userID in zip(files, userIDs):
    #     userID = str(userID)
    #     if file and allowed_file(file.filename) and userID.isnumeric():
    #         filename = secure_filename(file.filename)
    #         file.save(os.path.join(save_dir, filename))
    #         data.append((userID, os.path.join(save_dir, filename)))

    # return ([d[0] for d in data], [d[1] for d in data])


def empty_folder(folder_path):
    for filename in os.listdir(folder_path):
        file_path = os.path.join(folder_path, filename)
        try:
            if os.path.isfile(file_path):
                os.remove(file_path)
        except Exception as e:
            print(f"Error deleting file: {file_path} - {e}")


def handle_err (e):
    print(e)