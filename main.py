import cv2
import requests
from flask import Flask, request
from flask_restful import Resource, Api

app = Flask(__name__)
api = Api(app)


def count_people(path):
    # initialize the HOG descriptor/person detector
    hog = cv2.HOGDescriptor()
    hog.setSVMDetector(cv2.HOGDescriptor_getDefaultPeopleDetector())

    # load and resize image
    image = cv2.imread(path)
    image = cv2.resize(image, (750, 450))

    # detect people in the image
    (rects, weights) = hog.detectMultiScale(image, winStride=(4, 4), padding=(8, 8), scale=1.05)

    return len(rects)


class PeopleCounterStatic(Resource):
    def get(self):
        path = "photo.jpg"

        # count people
        counter = count_people(path)

        return {'peopleCount': counter}


class PeopleCounterDynamicUrl(Resource):
    def get(self):
        photo_path = "downloaded_photo.jpg"

        # get url from the request
        url = request.args.get('url')

        # get picture from url and save
        picture = requests.get(url).content
        with open(photo_path, "wb") as f:
            f.write(picture)

        # count people
        counter = count_people(photo_path)
        return {'peopleCount': counter}


@app.route('/send', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        file = request.files['file']
        if file:
            file_type = file.filename.rsplit('.', 1)[1].lower()
            file_name = f'send.{file_type}'
            file.save(file_name)
            counter = count_people(file_name)
            return {'peopleCount': counter}

    return '''
    <!doctype html>
    <title>Upload new Filess</title>
    <h1>Upload new File</h1>
    <form method=post enctype=multipart/form-data>
      <input type=file name=file>
      <input type=submit value=Upload>
    </form>
    '''


api.add_resource(PeopleCounterStatic, '/')
api.add_resource(PeopleCounterDynamicUrl, '/dynamic')

if __name__ == '__main__':
    app.run(debug=True)
