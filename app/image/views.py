
import sys
from flask import flash, render_template, request, send_file, redirect, url_for
from base64 import b64encode
from flask_login import current_user, login_required

from . import image
from ..models import Image, MediaType

IMAGE_FORMAT=["jpg", "png"]
VIDEO_FORMAT="mp4"

@image.route("/image/view/<string:imageid>")
@login_required
def image_view(imageid):
    img = Image.objects.get_or_404(id=imageid, user=current_user.id)
    media = b64encode(img.data).decode("utf-8")
    if img.mtype == MediaType.IMAGE:
        return render_template('image/view-image.html', image=media)
    if img.mtype == MediaType.VIDEO:
        return render_template('image/view-video.html', video=media)
    flash('Bad media format.', 'danger')
    return redirect(url_for('image.images_list'))
    #return send_file(io.BytesIO(img.data), attachment_filename='img.filename', mimetype='image/jpg')


@image.route('/image/add', methods = ['post', 'get'])
@login_required
def image_add():
    if request.method == 'POST':
        file = request.files['image']
        mtype = None
        if (file.filename.endswith(VIDEO_FORMAT)):
            mtype = MediaType.VIDEO
        else:
            for ext in IMAGE_FORMAT:
                if (file.filename.endswith(ext)):
                    mtype = MediaType.IMAGE
            if mtype is None:
                flash('Bad media format.', 'danger')
                return redirect(url_for('image.images_list'))
        try:
            img = Image(user=current_user.id, name=file.filename, data=file.read(), mtype=mtype)
            img.create()
            flash('image recorded, id={}'.format(str(img.id)), 'success')
        except Exception as e:
            flash('error to save Image', 'danger')
        return redirect(url_for('image.images_list'))
    return render_template('image/add-image.html')


@image.route('/image-capture', methods = ['get'])
@login_required
def image_capture():
    return render_template('image/capture-image.html', title='capture an image')


@image.route('/images', methods = ['get'])
@login_required
def images_list():
    images = Image.objects(user=current_user.id)
    return render_template('image/list-images.html', images=images, media_types_list=MediaType, title='Liste des images')



@image.route('/image/delete/<string:imageid>', methods = ['get', 'post'])
@login_required
def image_delete(imageid):
    img = Image.objects.get_or_404(id=imageid, user=current_user.id)
    img.delete()
    flash("Image {} Deleted".format(image.name), 'success')
    return redirect(url_for('image.images_list'))
 