import os
import traceback

from flask import request, send_file
from flask_jwt_extended import get_jwt_identity, jwt_required
from flask_restful import Resource
from flask_uploads import UploadNotAllowed
from libs import image_helper
from schemas.image import ImageSchema

image_schema = ImageSchema()

IMAGE_UPLOAD_SUCCESS = 'Image with name <{}> has been successfully saved.'
IMAGE_ILLEGAL_EXTENSION = 'The uploaded file extension <{}> is not supported.'
IMAGE_ILLEGAL_FILENAME = 'The filename <{}> of the file is not valid.'
IMAGE_NOT_FOUND = 'Image <{}> was not found.'
IMAGE_DELETE_FAILED = 'Deleting image failed.'
IMAGE_DELETED_SUCCESS = 'Deleted image <{}> successfully.'


class ImageUpload(Resource):
    @jwt_required
    def post(self):
        """
        This endpoint is used to upload an image file. It uses the
        JWT to retrieve user information and save the image in the user's folder.
        If a file with the same name exists in the user's folder, name conflicts
        will be automatically resolved by appending a underscore and a smallest
        unused integer. (eg. filename.png to filename_1.png).
        """
        data = image_schema.load(request.files)
        user_id = get_jwt_identity()
        folder = f"user_{user_id}"  # static/images/user_23
        try:
            # save(self, storage, folder=None, name=None)
            image_path = image_helper.save_image(data["image"], folder=folder)
            # here we only return the basename of the image and hide the internal folder structure from our user
            basename = image_helper.get_basename(image_path)
            return {"message": IMAGE_UPLOAD_SUCCESS.format(basename)}, 201
        except UploadNotAllowed:  # forbidden file type
            extension = image_helper.get_extension(data["image"])
            return {"message": IMAGE_ILLEGAL_EXTENSION.format(extension)}, 400


class Image(Resource):
    @jwt_required
    def get(self, filename: str):
        """
        This endpoint returns the requested image if exists. It will use JWT to
        retrieve user information and look for the image inside the user's folder.
        """
        user_id = get_jwt_identity()
        folder = f"user_{user_id}"
        # check if filename is URL secure
        if not image_helper.is_filename_safe(filename):
            return {"message": IMAGE_ILLEGAL_FILENAME.format(filename)}, 400
        try:
            # try to send the requested file to the user with status code 200
            return send_file(image_helper.get_path(filename, folder))
        except FileNotFoundError:
            return {"message": IMAGE_NOT_FOUND.format(filename)}, 404

    @jwt_required
    def delete(self, filename: str):
        """
        This endpoint is used to delete the requested image under the user's folder.
        It uses the JWT to retrieve user information.
        """
        user_id = get_jwt_identity()
        folder = f"user_{user_id}"

        # check if filename is URL secure
        if not image_helper.is_filename_safe(filename):
            return {"message": IMAGE_ILLEGAL_FILENAME.format(filename)}, 400

        try:
            os.remove(image_helper.get_path(filename, folder))
            return {"message": IMAGE_DELETED_SUCCESS.format(filename)}, 200
        except FileNotFoundError:
            return {"message": IMAGE_NOT_FOUND.format(filename)}, 404
        except:
            traceback.print_exc()
            return {"message": IMAGE_DELETE_FAILED}, 500
