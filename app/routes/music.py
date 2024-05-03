
from app import app
import mongoengine.errors
from flask import render_template, flash, redirect, url_for
from flask_login import current_user
from app.classes.data import Music, Comment
from app.classes.forms import MusicForm, CommentForm
from flask_login import login_required
import datetime as dt

@app.route('/music/new', methods=['GET', 'POST'])
# This means the user must be logged in to see this page
@login_required
# This is a function that is run when the user requests this route.
def musicNew():
    # This gets the form object from the form.py classes that can be displayed on the template.
    form = MusicForm()

    # This is a conditional that evaluates to 'True' if the user submitted the form successfully.
    # validate_on_submit() is a method of the form object. 
    if form.validate_on_submit():

        # This stores all the values that the user entered into the new blog form. 
        # Blog() is a mongoengine method for creating a new blog. 'newBlog' is the variable 
        # that stores the object that is the result of the Blog() method.  
        newMusic = Music(
            # the left side is the name of the field from the data table
            # the right side is the data the user entered which is held in the form object.
            subject = form.subject.data,
            artist = form.artist.data,
            genre = form.genre.data,
            favorite = form.favorite.data,
            author = current_user.id,
            
            # This sets the modifydate to the current datetime.
            modify_date = dt.datetime.utcnow
        )
        # This is a method that saves the data to the mongoDB database.
        newMusic.save()

        # Once the new blog is saved, this sends the user to that blog using redirect.
        # and url_for. Redirect is used to redirect a user to different route so that 
        # routes code can be run. In this case the user just created a blog so we want 
        # to send them to that blog. url_for takes as its argument the function name
        # for that route (the part after the def key word). You also need to send any
        # other values that are needed by the route you are redirecting to.
        return redirect(url_for('music',musicID=newMusic.id))

    # if form.validate_on_submit() is false then the user either has not yet filled out
    # the form or the form had an error and the user is sent to a blank form. Form errors are 
    # stored in the form object and are displayed on the form. take a look at blogform.html to 
    # see how that works.
    return render_template('musicform.html',form=form)

@app.route('/music/<musicID>')
# This route will only run if the user is logged in.
@login_required
def music(musicID):
    # retrieve the blog using the blogID
    thisMusic = Music.objects.get(id=musicID)
    # If there are no comments the 'comments' object will have the value 'None'. Comments are 
    # related to blogs meaning that every comment contains a reference to a blog. In this case
    # there is a field on the comment collection called 'blog' that is a reference the Blog
    # document it is related to.  You can use the blogID to get the blog and then you can use
    # the blog object (thisBlog in this case) to get all the comments.
    theseComments = Comment.objects(music=thisMusic)
    # Send the blog object and the comments object to the 'blog.html' template.
    return render_template('music.html',music=thisMusic,comments=theseComments)

# This route will delete a specific blog.  You can only delete the blog if you are the author.
# <blogID> is a variable sent to this route by the user who clicked on the trash can in the 
# template 'blog.html'. 
# TODO add the ability for an administrator to delete blogs. 

@app.route('/music/list')
@app.route('/musics')
# This means the user must be logged in to see this page
@login_required
def musicList():
    # This retrieves all of the 'blogs' that are stored in MongoDB and places them in a
    # mongoengine object as a list of dictionaries name 'blogs'.
    musics = Music.objects()
    # This renders (shows to the user) the blogs.html template. it also sends the blogs object 
    # to the template as a variable named blogs.  The template uses a for loop to display
    # each blog.
    return render_template('musiclist.html',musics=musics)

# This route will get one specific blog and any comments associated with that blog.  
# The blogID is a variable that must be passsed as a parameter to the function and 
# can then be used in the query to retrieve that blog from the database. This route 
# is called when the user clicks a link on bloglist.html template.
# The angle brackets (<>) indicate a variable. 

@app.route('/music/favorites')
# This means the user must be logged in to see this page
@login_required
def musicFavorites():
    # This retrieves all of the 'blogs' that are stored in MongoDB and places them in a
    # mongoengine object as a list of dictionaries name 'blogs'.
    musics = Music.objects()
    # This renders (shows to the user) the blogs.html template. it also sends the blogs object 
    # to the template as a variable named blogs.  The template uses a for loop to display
    # each blog.
    return render_template('musicfavorites.html',musics=musics)

# This route will get one specific blog and any comments associated with that blog.  
# The blogID is a variable that must be passsed as a parameter to the function and 
# can then be used in the query to retrieve that blog from the database. This route 
# is called when the user clicks a link on bloglist.html template.
# The angle brackets (<>) indicate a variable. 


@app.route('/music/edit/<musicID>', methods=['GET', 'POST'])
@login_required
def musicEdit(musicID):
    editMusic = Music.objects.get(id=musicID)
    # if the user that requested to edit this blog is not the author then deny them and
    # send them back to the blog. If True, this will exit the route completely and none
    # of the rest of the route will be run.
    if current_user != editMusic.author:
        flash("You can't edit a song you don't own.")
        return redirect(url_for('music',musicID=musicID))
    # get the form object
    form = MusicForm()
    # If the user has submitted the form then update the blog.
    if form.validate_on_submit():
        # update() is mongoengine method for updating an existing document with new data.
        editMusic.update(
            subject = form.subject.data,
            modify_date = dt.datetime.utcnow
        )
        # After updating the document, send the user to the updated blog using a redirect.
        return redirect(url_for('music',musicID=musicID))

    # if the form has NOT been submitted then take the data from the editBlog object
    # and place it in the form object so it will be displayed to the user on the template.
    form.subject.data = editMusic.subject


    # Send the user to the blog form that is now filled out with the current information
    # from the form.
    return render_template('musicform.html',form=form)

@app.route('/music/delete/<musicID>')
# Only run this route if the user is logged in.
@login_required
def musicDelete(musicID):
    # retrieve the blog to be deleted using the blogID
    deleteMusic = Music.objects.get(id=musicID)
    # check to see if the user that is making this request is the author of the blog.
    # current_user is a variable provided by the 'flask_login' library.
    if current_user == deleteMusic.author:
        # delete the blog using the delete() method from Mongoengine
        deleteMusic.delete()
        # send a message to the user that the blog was deleted.
        flash('The song was deleted.')
    else:
        # if the user is not the author tell them they were denied.
        flash("You can't delete a song you don't own.")
    # Retrieve all of the remaining blogs so that they can be listed.
    musics = Music.objects()  
    # Send the user to the list of remaining blogs.
    return render_template('music.html',musics=musics)
