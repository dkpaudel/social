from itertools import chain
from  django . shortcuts  import  get_object_or_404, render, redirect
from django.http import HttpResponse
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from . models import  Followers, LikePost, DislikePost,Post,Comment, Profile
from django.db.models import Q




def signup(request):
    if request.method == 'POST':
        fnm = request.POST.get('fnm')  # Username
        emailid = request.POST.get('emailid')  # Email
        pwd = request.POST.get('pwd')  # Password
        confirm_pwd = request.POST.get('confirm_pwd')  # Password confirmation

        # Check if any field is empty
        if not fnm or not emailid or not pwd or not confirm_pwd:
            return render(request, 'signup.html', {'invalid': "All fields are required."})

        # Check if passwords match
        if pwd != confirm_pwd:
            return render(request, 'signup.html', {'invalid': "Passwords do not match."})

        # Check if username already exists
        if User.objects.filter(username=fnm).exists():
            return render(request, 'signup.html', {'invalid': "Username already exists."})

        # Check if email already exists
        if User.objects.filter(email=emailid).exists():
            return render(request, 'signup.html', {'invalid': "Email is already registered."})

        # Create the user
        my_user = User.objects.create_user(username=fnm, email=emailid, password=pwd)
        my_user.save()

        # Create the Profile linked to the user
        new_profile = Profile.objects.create(user=my_user, id_user=my_user.id)
        new_profile.save()

        # Log the user in
        login(request, my_user)
        return redirect('/')

    return render(request, 'signup.html')
       
        
        
    

def loginn(request):
 
  if request.method == 'POST':
        fnm=request.POST.get('fnm')
        pwd=request.POST.get('pwd')
        print(fnm,pwd)
        userr=authenticate(request,username=fnm,password=pwd)
        if userr is not None:
            login(request,userr)
            return redirect('/')
        
 
        invalid="Invalid Credentials"
        return render(request, 'loginn.html',{'invalid':invalid})
               
  return render(request, 'loginn.html')

@login_required(login_url='/loginn')
def logoutt(request):
    logout(request)
    return redirect('/loginn')



@login_required(login_url='/loginn')
def home(request):
    
    following_users = Followers.objects.filter(follower=request.user.username).values_list('user', flat=True)

    
    post = Post.objects.filter(Q(user=request.user.username) | Q(user__in=following_users)).order_by('-created_at')

    profile = Profile.objects.get(user=request.user)

    context = {
        'post': post,
        'profile': profile,
    }
    return render(request, 'main.html',context)
    


@login_required(login_url='/loginn')
def upload(request):

    if request.method == 'POST':
        user = request.user.username
        image = request.FILES.get('image_upload')
        caption = request.POST['caption']

        new_post = Post.objects.create(user=user, image=image, caption=caption)
        new_post.save()

        return redirect('/')
    else:
        return redirect('/')


# from django.shortcuts import get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from .models import Post, LikePost, DislikePost  # Ensure you import the necessary models

@login_required(login_url='/loginn')
def likes(request, id):
    if request.method == 'GET':
    
        username = request.user.username
        post = get_object_or_404(Post, id=id)  # Fetch the post using UUID

        like_filter = LikePost.objects.filter(post_id=post.id, username=username).first()
        dislike_filter = DislikePost.objects.filter(post_id=post.id, username=username).first()

        if like_filter is None:
            # If the user had disliked the post before, remove the dislike
            if dislike_filter:
                dislike_filter.delete()
                post.no_of_dislikes -= 1
             
            # Add a new like
            LikePost.objects.create(post_id=post.id, username=username)
            post.no_of_likes += 1
           
        else:
            # Remove the like if already liked
            like_filter.delete()
            post.no_of_likes -= 1
          

        post.save()
   
        return redirect('/#' + str(post.id))  # UUID should be converted to string

@login_required(login_url='/loginn')
def dislikes(request, id):
    if request.method == 'GET':
        username = request.user.username
        post = get_object_or_404(Post, id=id)  # Fetch the post using UUID

        dislike_filter = DislikePost.objects.filter(post_id=post.id, username=username).first()
        like_filter = LikePost.objects.filter(post_id=post.id, username=username).first()

        if dislike_filter is None:
            # If the user had liked the post, remove the like first
            if like_filter:
                like_filter.delete()
                post.no_of_likes -= 1

            # Add a new dislike
            DislikePost.objects.create(post_id=post.id, username=username)
            post.no_of_dislikes += 1
        else:
            # Remove the dislike if already disliked
            dislike_filter.delete()
            post.no_of_dislikes -= 1

        post.save()
        return redirect('/#' + str(post.id))  # UUID should be converted to string
    

@login_required(login_url='/loginn')
def explore(request):
    sort_by = request.GET.get('sort_by', '-created_at')  # Default: Most Recent
    post = Post.objects.all().order_by(sort_by)
    profile = Profile.objects.get(user=request.user)

    context = {
        'post': post,
        'profile': profile,
    }
    return render(request, 'explore.html', context)


    
@login_required(login_url='/loginn')
def profile(request,id_user  ):
  
    user_object = User.objects.get(username=id_user)
    print(user_object)
    profile = Profile.objects.get(user=request.user)
    user_profile = Profile.objects.get(user=user_object)

    sort_option = request.GET.get('sort_by', '-created_at')

    # Allowed sorting fields
    allowed_sorts = {
        'most_recent': '-created_at',
        'oldest': 'created_at',
        'most_liked': '-no_of_likes',
        'most_disliked': '-no_of_dislikes',
        'most_commented': '-no_of_comments',
    }

    # Validate sort option
    order_by_field = allowed_sorts.get(sort_option, '-created_at')
    user_posts = Post.objects.filter(user=id_user).order_by(order_by_field)
   
    user_post_length = len(user_posts)

    follower = request.user.username
    user = id_user
    
    if Followers.objects.filter(follower=follower, user=user).first():
        follow_unfollow = 'Unfollow'
    else:
        follow_unfollow = 'Follow'

    user_followers = len(Followers.objects.filter(user=id_user))
    user_following = len(Followers.objects.filter(follower=id_user))
    


    context = {
        'user_object': user_object,
        'user_profile': user_profile,
        'user_posts': user_posts,
        'user_post_length': user_post_length,
        'profile': profile,
        'follow_unfollow':follow_unfollow,
        'user_followers': user_followers,
        'user_following': user_following,
        'selected_sort': sort_option,
    }
    
    
    if request.user.username == id_user:
        if request.method == 'POST':
            if request.FILES.get('image') == None:
             image = user_profile.profileimg
             bio = request.POST['bio']
             location = request.POST['location']

             user_profile.profileimg = image
             user_profile.bio = bio
             user_profile.location = location
             user_profile.save()
            if request.FILES.get('image') != None:
             image = request.FILES.get('image')
             bio = request.POST['bio']
             location = request.POST['location']

             user_profile.profileimg = image
             user_profile.bio = bio
             user_profile.location = location
             user_profile.save()
            

            return redirect('/profile/'+id_user)
        else:
            return render(request, 'profile.html', context)
    return render(request, 'profile.html', context)

@login_required(login_url='/loginn')
def delete(request, id):
    post = Post.objects.get(id=id)
    post.delete()

    return redirect('/profile/'+ request.user.username)


@login_required(login_url='/loginn')
def search_results(request):
    query = request.GET.get('q')

    users = Profile.objects.filter(user__username__icontains=query)
    posts = Post.objects.filter(caption__icontains=query)

    context = {
        'query': query,
        'users': users,
        'posts': posts,
    }
    return render(request, 'search_user.html', context)

def home_post(request,id):
    post=Post.objects.get(id=id)
    profile = Profile.objects.get(user=request.user)
    context={
        'post':post,
        'profile':profile
    }
    return render(request, 'main.html',context)



def follow(request):
    if request.method == 'POST':
        follower = request.POST['follower']
        user = request.POST['user']

        if Followers.objects.filter(follower=follower, user=user).first():
            delete_follower = Followers.objects.get(follower=follower, user=user)
            delete_follower.delete()
            return redirect('/profile/'+user)
        else:    
            new_follower = Followers.objects.create(follower=follower, user=user)
            new_follower.save()
            return redirect('/profile/'+user)
    else:
        return redirect('/')



@login_required(login_url='/loginn')
def add_comment(request, id):
    if request.method == "POST":
        text = request.POST.get('text')  # Get comment text from form
        username = request.user.username
        post = get_object_or_404(Post, id=id)
        
        if text.strip():  # Ensure comment is not empty
            Comment.objects.create(post_id=post.id, username=username, text=text)
            post.no_of_comments += 1
            post.save()
        
    return redirect('/#' + str(post.id))



from django.http import JsonResponse


def fetch_comments(request, id):
    post = get_object_or_404(Post, id=id)
    comments = Comment.objects.filter(post_id=post.id).order_by('-created_at')
    
    comments_data = [
        {
            "username": comment.username,
            "text": comment.text,
            "created_at": comment.created_at.strftime('%Y-%m-%d %H:%M:%S')
        }
        for comment in comments
    ]

    return JsonResponse({"comments": comments_data})



from .models import ChatRoom, ChatMessage
from django.contrib.auth.models import User

@login_required(login_url='/loginn')
def chat_home(request):
    chat_rooms = ChatRoom.objects.filter(Q(user1=request.user) | Q(user2=request.user))
    return render(request, 'chat/chat_home.html', {'chat_rooms': chat_rooms})

@login_required(login_url='/loginn')
def chat_room(request, room_id):
    room = get_object_or_404(ChatRoom, id=room_id)
    if request.user not in [room.user1, room.user2]:
        return redirect('chat_home')

    if request.method == "POST":
        text = request.POST.get('text')
        ChatMessage.objects.create(room=room, sender=request.user, message=text)
        return redirect(f'/chat/{room_id}/')

    messages = ChatMessage.objects.filter(room=room).order_by('timestamp')
    chat_partner = room.user2 if room.user1 == request.user else room.user1
    return render(request, 'chat/chat_room.html', {'room': room, 'messages': messages, 'chat_partner': chat_partner})

@login_required(login_url='/loginn')

def start_chat(request, username):
    user_to_chat = get_object_or_404(User, username=username)

    # Check if a chat room already exists between these users (in any order)
    room = ChatRoom.objects.filter(
        (Q(user1=request.user) & Q(user2=user_to_chat)) |
        (Q(user1=user_to_chat) & Q(user2=request.user))
    ).first()

    # If no existing chat room, create a new one
    if not room:
        room = ChatRoom.objects.create(user1=request.user, user2=user_to_chat)

    return redirect(f'/chat/{room.id}/')


def fetch_likes(request, id):
    post = get_object_or_404(Post, id=id)
    likes= LikePost.objects.filter(post_id=post.id)
    
    likes_data = [
        {
            "username": like.username,
            
        }
        for like in likes
    ]
    return JsonResponse({"likes": likes_data})

def fetch_dislikes(request, id):
    post = get_object_or_404(Post, id=id)
    dislikes= DislikePost.objects.filter(post_id=post.id)
    
    dislikes_data = [
        {
            "username": dislike.username,
            
        }
        for dislike in dislikes
    ]
    return JsonResponse({"dislikes": dislikes_data})

def fetch_followers(request,username):
   followers= Followers.objects.filter(user=username)
   followers_data=[
       {
           "username":follower.follower
       }
       for follower in followers
   ]
   return JsonResponse({"followers":followers_data})

def fetch_followings(request,username):
   followings= Followers.objects.filter(follower=username)
   followings_data=[
       {
           "username":following.user
       }
       for following in followings
   ]
   return JsonResponse({"followings":followings_data})


