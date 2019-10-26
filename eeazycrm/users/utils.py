import os
import secrets
from PIL import Image

from flask import current_app


def upload_avatar(user, form_picture):
    random_hex = secrets.token_hex(8)
    _, f_ext = os.path.splitext(form_picture.filename)
    pic_name = random_hex + f_ext

    # if the pic already exists, remove it first
    if user.avatar:
        file_path = os.path.join(current_app.root_path, 'static/profile_imgs',
                                 user.avatar)
        if os.path.exists(file_path):
            os.remove(file_path)
        else:
            print(f'file {file_path} does not exist!')

    pic_path = os.path.join(current_app.root_path,
                            'static/profile_imgs', pic_name)

    # resize the image before saving
    output_size = (128, 128)
    img = Image.open(form_picture)
    img.thumbnail(output_size)
    img.save(pic_path)

    return pic_name


