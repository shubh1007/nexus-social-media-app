from django.shortcuts import render, redirect
from django.http import HttpResponse
# User provides the information of user interacting
from django.contrib.auth.models import User, auth
# Send error messages to the front end
from django.contrib import messages
# In order to access the function the user must be logged in
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from .models import Profile, Post, LikePost, FollowersCount
# Chain converts list to iterable
from itertools import chain
import random
# Create your views here.
# If user is not logged in then the user is redirected to signin page to log in
@login_required(login_url= "signin")
def index(request):
    user_object = User.objects.get(username = request.user.username)
    print(request.user.username)
    user_profile = Profile.objects.get(user = user_object)
    # List of users of following users. Logged in user is following
    user_following_list = []
    user_following = FollowersCount.objects.filter(follower = request.user.username)
    feed = []
    # Store only the posts of users in user_following_list
    for users in user_following:
        user_following_list.append(users.user)
    for usernames in user_following_list:
        feed_lists = Post.objects.filter(user = usernames)
        feed.append(feed_lists)
    # Unpack all the feed and send to chain so that it becomes iterable
    feed_list = list(chain(*feed))
    # posts = Post.objects.all()

    # Get the Following Suggestion
    # Get all the users
    # Remove users which are already being followed
    # Remove the current logged in user from the list
    # Shuffle the list and chain it
    all_users = User.objects.all()
    user_following_all = []
    for users in user_following:
        user_list = User.objects.get(username = users.user)
        user_following_all.append(user_list)

    new_suggestions_list = [x for x in list(all_users) if (x not in list(user_following_all))]
    current_user = User.objects.filter(username = request.user.username)
    final_suggestion_list = [x for x in list(new_suggestions_list) if x not in list(current_user)]
    random.shuffle(final_suggestion_list)

    # Get the profiles of those usernames
    username_profile = []
    username_profile_list = []
    for users in final_suggestion_list:
        username_profile.append(users.id)
    for ids in username_profile:
        profile_lists = Profile.objects.filter(id_user = ids)
        username_profile_list.append(profile_lists)
    suggestions_username_profile_list = list(chain(*username_profile_list))  
    length = len(suggestions_username_profile_list)

    return render(request, "index.html", {
        "user_profile" : user_profile, 
        "posts": feed_list,
        "suggestions_username_profile_list": suggestions_username_profile_list[:min(4, length)]
        })

@login_required(login_url="signin")
def profile(request, pk):
    if not User.objects.filter(username = pk).exists():
        # print("HELLO")
        return redirect("/")
    user_object = User.objects.get(username = pk)
    user_profile = Profile.objects.get(user = user_object)
    user_posts = Post.objects.filter(user = pk)
    user_posts_length = len(user_posts)
    follower = request.user.username
    user = pk
    if FollowersCount.objects.filter(user = user, follower = follower).first():
        # User it already following the profile
        button_text = "Unfollow"
    else:
        button_text = "Follow"
        # User Followed by other profiles
    user_followers = len(FollowersCount.objects.filter(user = pk))
    user_following = len(FollowersCount.objects.filter(follower = pk))
    context = {
        "user_object": user_object,
        "user_profile": user_profile,
        "user_posts": user_posts,
        "user_post_length": user_posts_length,
        "button_text": button_text,
        "user_followers": user_followers,
        "user_following": user_following,
    }
    return render(request, "profile.html", context = context)

@csrf_exempt
def signin(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        # Authenticate the user | returns None if not authenticated
        user = auth.authenticate(username = username, password = password)
        if user is not None:
            # User is authenticated
            auth.login(request, user)
            return redirect("/")
        else:
            messages.info(request, "Credentials invalid")
            return redirect("signin")
    else:
        return render(request, "signin.html")

@csrf_exempt
def signup(request):
    if request.method == "POST":
        username = request.POST.get("username")
        email = request.POST.get("email")
        password = request.POST.get("password")
        password2 = request.POST.get("password2")
        if password == password2:
            # Check whether the email is present in the database
            if User.objects.filter(email=email).exists():
                messages.info(request, "Email Taken")
                return redirect("signup")
            elif User.objects.filter(username=username).exists():
                messages.info(request, "Username Taken")
                return redirect("signup")
            else:
                user = User.objects.create_user(
                    username=username,
                    email=email,
                    password=password,
                )
                user.save()
                # Log the user and then redirect the user to the settings page
                user_login = auth.authenticate(username = username, password = password)
                # Logs the user in 
                auth.login(request, user_login)
                # Create a profile object for the user
                user_model = User.objects.get(username = username)
                # Created a profile with user and id_user
                new_profile = Profile.objects.create( 
                    user = user_model, 
                    id_user = user_model.id)
                new_profile.save()

                return redirect("settings")
        else:
            # Give error message
            messages.info(request, "Password not matching")
            # redirecting to the signup url
            return redirect("signup")
    else:
        return render(request, "signup.html")

def logout(request):
    auth.logout(request)
    return redirect("signin")

@login_required(login_url="signin")
def settings(request):
    # get the user object and store in user_profile to implement the settings
    user_profile = Profile.objects.get(user = request.user)
    if request.method == "POST":
        image = None
        if request.FILES.get('image') == None:
            image = user_profile.profile_img
        else:
            image = request.FILES.get("image")
        
        bio = request.POST.get('bio')
        location = request.POST.get('location')
        user_profile.profile_img = image
        user_profile.bio = bio
        user_profile.location = location
        user_profile.save()
        return redirect("settings")
    # Send this user_profile object to the template to access the data related to that user
    return render(request, "setting.html", {"user_profile": user_profile})
    
@login_required(login_url="signin")
def upload(request):
    if request.method == "POST":
        # We just need image and caption as no_of_likes = 0 and time, id are set there in the models itself
        user = request.user.username
        image = request.FILES.get("image_upload")
        caption = request.POST.get("caption")
        new_post = Post.objects.create(user = user, image = image, caption = caption)
        new_post.save()
        return redirect("/")
    else:
        # If nothing is uploaded we just redirect to the home page
        return redirect("/")

@login_required(login_url="signin")
def like_post(request):
    username = request.user.username
    post_id = request.GET.get("post_id")
    post = Post.objects.get(id = post_id)
    # Here the user has already liked the post
    # We are using filter method so that we won't get any no key error
    # Get the first user only
    like_filter = LikePost.objects.filter(post_id = post_id, username = username).first()
    if like_filter == None:
        # User has not liked this post
        new_like = LikePost.objects.create(post_id = post_id, username = username)
        new_like.save()
        # Increase the number of likes by 1
        post.no_of_like = post.no_of_like + 1
        post.save()
        return redirect("/")
    else:
        # User already liked this post
        # Decrement the no_of_like for the post by 1
        # Delete the like object as the post is unliked by the user
        like_filter.delete()
        post.no_of_like = post.no_of_like - 1
        post.no_of_like = max(0, post.no_of_like)
        post.save()
        return redirect("/")

@login_required(login_url="signin")
def follow(request):
    if request.method == "POST":
        follower = request.POST.get("follower")
        user = request.POST.get("user")
        if FollowersCount.objects.filter( follower = follower, user = user).exists():
            # Check if logged in user is already following the user
            delete_follower = FollowersCount.objects.get(user = user, follower = follower)
            delete_follower.delete()
            return redirect("/profile/" + user)
        else:
            # Logged in User does not follows the user
            new_follower = FollowersCount.objects.create(user = user, follower = follower)
            new_follower.save()
            return redirect("/profile/" + user)
    return redirect("/")

@login_required(login_url="signin")
def search(request):
    user_object = User.objects.get(username = request.user.username)
    user_profile = Profile.objects.get(user = user_object)
    if request.method == "POST":
        username = request.POST.get("username")
        # checks whether the query text contain some part of the username 
        # Like shub will return shubham shubey and shubh
        username_object = User.objects.filter(username__icontains = username)
        username_profile = []
        username_profile_list = []
        for users in username_object:
            username_profile.append(users.id)
        for ids in username_profile:
            profile_lists = Profile.objects.filter(id_user = ids)
            username_profile_list.append(profile_lists)
        username_profile_list = list(chain(*username_profile_list))
    return render(request, "search.html", {"username_profile_list": username_profile_list, "user_profile": user_profile})





