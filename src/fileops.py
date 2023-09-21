import os, tempfile, datetime, time
ALLOWED_EXTENSIONS = {'mp4'}

def allowed_file(filename: str) -> bool:
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def delete_file(filePath: str) -> str:
    try:
        if filePath:
            os.remove(filePath)
            return 'Video deleted.'
        return 'No video path provided.'
    except Exception as e:
        return f'Error deleting file: {e}'

def delete_files_in_folder(filePath: str):
    for filename in os.listdir(filePath):
        file_path = os.path.join(filePath, filename)
        try:
            if os.path.isfile(file_path):
                os.unlink(file_path)
        except Exception as e:
            print(f"Error deleting file: {e}")

def upload_to_local_folder(file, objectID: str, fileName: str) -> str:
    try:
        upload_folder = 'uploads'
        os.makedirs(upload_folder, exist_ok=True)
        filePath = os.path.join(upload_folder, objectID + fileName)
        file.save(filePath)
        return filePath
    except Exception as e:
        print(f"Error uploading file: {e}")
        return e

def create_object_id():
    return (datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S")+str(time.time())).replace(".","").replace("-","")