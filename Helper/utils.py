import os
import uuid
from flask import Flask, flash, request, redirect

def saveRecordedFile(request):
# check if the post request has the file part
    print(request.files)
    if 'file' not in request.files:
        print("err")
        flash('No file part')
        return redirect(request.url)
    
    file = request.files['file']

    # if user does not select file, browser also
    # submit an empty part without filename
    if file.filename == '':
        flash('No selected file')
        return redirect(request.url)
    
    file_name = str(uuid.uuid4()) + ".mp3"
    full_file_name = os.path.join("Data", file_name)


    try:
        full_file_name = os.path.join("Data", file_name)
        file.save(full_file_name)
        return full_file_name

    except:
        print("error")

    return "error"