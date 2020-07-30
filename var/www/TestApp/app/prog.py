import os
import shutil
from app import app

from flask import Flask, request, redirect, abort, jsonify, send_from_directory
from werkzeug.utils import secure_filename

#UPLOAD_DIRECTORY = "g:/OneDrive/coding/python/PythonPractice/testfolder/api_uploaded_files"
#print(os.getcwd()) # Show work dir

ALLOWED_EXTENSIONS = set(['txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif', 'ini']) 

def allowed_file(filename):
	return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


if not os.path.exists(app.config['UPLOAD_DIRECTORY']):
    os.makedirs(app.config['UPLOAD_DIRECTORY'])


#app = Flask(__name__)``

@app.route('/', methods=['GET'])
def home():
    return "Hello World!"



@app.route('/files', methods=['GET'])   # Endpoint to list files on the server
def listFiles():   

    files = []

    for filename in os.listdir(app.config['UPLOAD_DIRECTORY']):
        pathToFile = os.path.join(app.config['UPLOAD_DIRECTORY'], filename)
        if os.path.isfile(pathToFile):
            files.append(filename)
    return jsonify(files)



@app.route('/files/<path:path>', methods=['GET']) # Download a file
def getFile(path):
    return send_from_directory(app.config['UPLOAD_DIRECTORY'], path, as_attachment=True)



@app.route('/files/<filename>', methods=['POST']) # Upload File
def postFile(filename):
    if '/' in filename:  # Return 400 BAD REQUEST
        abort(400, "No SubDir's Allowed")

    with open(os.path.join(app.config['UPLOAD_DIRECTORY'], filename), 'wb') as fp:
        fp.write(request.data)

    return jsonify(201, 'File uploaded successfully!') # Return 201 CREATED



@app.route('/del-files/<filename>', methods=['DELETE'])  # Del file by filename
def delFile(filename):
    filePath = os.path.join(app.config['UPLOAD_DIRECTORY'], filename) 
    if os.path.isfile(filePath):
        os.remove(filePath)
        response = {"message": "File Deleted"}
    else:
        response = {"message": "File Not Found!"}
    
    return jsonify(response), 200



@app.route('/multiple-files-upload', methods=['POST'])
def uploadFiles():
	# check if the post request has the file part
	if 'files[]' not in request.files:
		resp = jsonify({'message' : 'No file part in the request'})
		resp.status_code = 400
		return resp
	
	files = request.files.getlist('files[]')
	
	errors = {}
	success = False
	
	for file in files:		
		if file and allowed_file(file.filename):   #allowed_file(filename) to allow user only upload allowed file types
			filename = secure_filename(file.filename)
			file.save(os.path.join(app.config['UPLOAD_DIRECTORY'], filename))
			success = True
		else:
			errors[file.filename] = 'File type is not allowed'
	
	if success:
		response = jsonify({'message' : 'Files successfully uploaded'})
		response.status_code = 201
		return response
	else:
		response = jsonify(errors)
		response.status_code = 500
		return response



@app.route('/folders', methods=['GET'])   # List all folders in Path
def listFolders():   
    folders = []

    for dirs in os.listdir(app.config['UPLOAD_DIRECTORY']):
        pathToDirs = os.path.join(app.config['UPLOAD_DIRECTORY'], dirs)
        if os.path.isdir(pathToDirs):
            folders.append(dirs)
    return jsonify(folders)



@app.route('/create-folder/<dirName>', methods=['GET'])   # Creates 1 folder with a name entry
def createFolder(dirName):
    filePath = os.path.join(app.config['UPLOAD_DIRECTORY'])
    if os.path.exists(dirName):
        response = {"message": "Folder already exists!"}
    else:
        os.chdir(filePath)
        os.mkdir(dirName)
        response = {"message": "Folder created"}
    return jsonify (response), 200



@app.route('/create-folders/<dirName>/<dirName2>', methods=['GET'])   # Creates 2 folder with a name entry
def createFolders(dirName, dirName2):
    filePath = os.path.join(app.config['UPLOAD_DIRECTORY'])
    if os.path.exists(dirName) or os.path.exists(dirName2):
        response = {"message": "Folders already exists!"}
    else:
        os.chdir(filePath)
        os.mkdir(dirName)
        os.mkdir(dirName2)
        response = {"message": "Folders created"}
    return jsonify (response), 200



@app.route('/del-folder/<dirDel>', methods=['DELETE'])   # Delete 1 folder
def deleteFolder(dirDel):
    filePath = os.path.join(app.config['UPLOAD_DIRECTORY'])
    os.chdir(filePath)
    if os.path.exists(dirDel):
        os.rmdir(dirDel)
        response = {"message": "Folder deleted successfully."}
    else:
        response = {"message": "Folder NOT found!"}
    return jsonify (response), 200



@app.route('/del-all-folders', methods=['DELETE'])        # Delete all folders tree + included files in folders 
def delAllFoldersTree():
    for dir in os.listdir(app.config['UPLOAD_DIRECTORY']):
        path = os.path.join(app.config['UPLOAD_DIRECTORY'], dir)
        if os.path.exists(path):
            shutil.rmtree(path, ignore_errors=True)
            response = {"message": "All folders deleted"}
        else:
            response = {"message": "Folders NOT found"}
    return jsonify (response), 200



@app.route('/del-all-empty-folders', methods=['DELETE'])     # Delete only all empty folders
def delAllEmptyDirs():
    folders = []

    for dirs in os.listdir(app.config['UPLOAD_DIRECTORY']):
        pathToDirs = os.path.join(app.config['UPLOAD_DIRECTORY'], dirs)
        if os.path.isdir(pathToDirs):
            folders.append(dirs)
            os.rmdir(pathToDirs)
            response = {"message": "All Folders deleted"}    # ?
    return jsonify(response)



@app.route('/upload-folder/<string:dirName>', methods=['POST'])
def uploadFolders(dirName):
    filePath = os.path.join(app.config['UPLOAD_DIRECTORY'])
    if os.path.exists(dirName):
        response = {"message": "Folder already uploaded!"}
    else:
        os.chdir(filePath)
        os.mkdir(dirName)
        pathNewFld = os.path.abspath(dirName)
        os.chdir(pathNewFld)
        newPath = os.getcwd()

    files = request.files.getlist('files[]')
	
    errors = {}
    success = False
	
    for file in files:
        if file and allowed_file(file.filename):   #allowed_file(filename) to allow user only upload allowed file types
            filename = secure_filename(file.filename)
            file.save(os.path.join(newPath, filename))
            success = True
        else:
            errors[file.filename] = 'File type is not allowed'
    
    if success:
        response = jsonify({'message' : 'Folder successfully uploaded!'})
        response.status_code = 201
        return response
    else:
        response = jsonify(errors)
        response.status_code = 500
        return response
        
    #return jsonify (response), 200


@app.route('/create-multiple-folders/<folders>', methods=['POST']) 
def createMultipleFolders(folders): 
    os.chdir(app.config['UPLOAD_DIRECTORY'])
    for folder in folders:
        if not os.path.exists(folder):
            os.mkdir(folder)
            response = {"Folders created successfully"}
        else:
            response = {"Folders already exists!"}
    return jsonify(response) 



@app.route('/create-folder-tree/<root_dir>/<main_dir>/<dir_names>', methods=['GET'])
def createDirsTree(root_dir, main_dir, dir_names):
    # Create directory
    os.chdir(app.config['UPLOAD_DIRECTORY'])
    for i in range(0, len(main_dir)):
        for j in range(0,len(main_dir[i])):
            dirName = str(root_dir) + '/' + str(main_dir[i][j])
            
            try:
                # Create target Directory
                os.makedirs(dirName)
                response = {"Directory " , dirName ,  " Created "} 
            except FileExistsError:
                response = {"Directory " , dirName ,  " already exists"}        

            # Create target Directory if don't exist
            if not os.path.exists(dirName):
                os.makedirs(dirName)
                response = {"Directory " , dirName ,  " Created "}
            else:    
                response = {"Directory " , dirName ,  " already exists"}
    return jsonify(response)





@app.errorhandler(404)
def not_found(error=None):
    message = {
        'status': 404,
        'message': 'Not Found: ' + request.url,
    }
    resp = jsonify(message)
    resp.status_code = 404

    return resp


if __name__ == "__main__":
    app.run(debug=True, port=8000)