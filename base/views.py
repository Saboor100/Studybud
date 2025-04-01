from django.shortcuts import render, redirect, get_object_or_404
from django.db.models import Q
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required #for create room page to require login for creatingroom
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.models import User
from .models import Room, Topic, message 
from .forms import RoomForm, MessageForm , CustomUserCreationForm , Userform
from django.contrib.auth import get_user_model


# rooms =[
#     {'id':1,'name':'Lets learn python' },
#     {'id':2,'name':'NIGGAS' },
#     {'id':3,'name':'RACISM' },
# ]

def loginPage(request):
    page = 'login'
    if request.user.is_authenticated:
        return redirect('home')
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        try :
            user = User.objects.get(username=username)
        except:
            messages.error(request, 'User does not exist')

        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('home')
        else:
            messages.error(request, 'Username or password does not exist')
    context = {'page':page}
    return render(request, 'base/login_register.html',context)

def logoutUser(request):
    logout(request)
    return redirect('home')
def registerPage(request):
    form = CustomUserCreationForm()
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.username = user.username.lower()
            user.save()
            login(request, user)
            return redirect('home')
        else:
            print(form.errors)
            messages.error(request, 'An error occured during registration')
    return render(request, 'base/login_register.html',{'form':form})
def home(request):
    q = request.GET.get('q') if request.GET.get('q') != None else ''
    rooms = Room.objects.filter(
        Q(topic__name__icontains=q) 
      | Q(name__icontains=q)
      | Q(description__icontains=q)
      )
    topics = Topic.objects.all()[0:4]
    room_count = rooms.count()
    room_messages = message.objects.filter(Q(room__topic__name__icontains=q))
    context = {'rooms': rooms, 'topics':topics, 'room_count':room_count , 'room_messages':room_messages}
    return render(request, 'base/home.html',context) 

def rooms_view(request, pk):
    room = Room.objects.get(id=pk)
    room_messages = room.message_set.all().order_by('-created')
    participants = room.participants.all()

    if request.method == 'POST':
        form = MessageForm(request.POST, request.FILES)
        if form.is_valid():
            message = form.save(commit=False)
            message.user = request.user
            message.room = room

            # ✅ Explicitly assign the file if uploaded
            if request.FILES.get('file'):
                message.file = request.FILES.get('file')

            # ✅ Save if there's either a body or a file
            if message.body or message.file:
                print(f"Saving message with body: {message.body}, file: {message.file}")  # Debugging
                message.save()
            else:
                print("No body or file detected.")

            room.participants.add(request.user)
            return redirect('room', pk=room.id)
        else:
            print("Form errors:", form.errors)  # Debugging form errors
    else:
        form = MessageForm()

    # ✅ Debugging: Print all messages in the room
    for msg in room_messages:
        print(f"Message: {msg.body}, File: {msg.file}")

    context = {
        'room': room,
        'room_messages': room_messages,
        'participants': participants,
        'form': form
    }
    return render(request, 'base/room.html', context)



@login_required(login_url='login')
def userProfile(request, pk):
    User = get_user_model()
    user = User.objects.get(id=pk)
    rooms = user.room_set.all()
    room_messages = user.message_set.all()
    topics = Topic.objects.all()
    context = {'user': user, 'rooms': rooms, 'room_messages':room_messages, 'topics':topics}
    return render(request, 'base/profile.html',context)

@login_required(login_url='login')
def createRoom(request):
    form = RoomForm()
    topics = Topic.objects.all()
    if request.method == 'POST':
        # for creating new topics with name of our choice
        topic_name = request.POST.get('topic')
        topic, created = Topic.objects.get_or_create(name=topic_name)

        Room.objects.create(
            host = request.user,
            topic = topic,
            name = request.POST.get('name'),
            description = request.POST.get('description'),
        )
      
        return redirect('home')
    context = {'form': form, 'topics':topics}
    return render(request, 'base/room_form.html',context)

@login_required(login_url='login')
def updateRoom(request, pk):
    room = Room.objects.get(id=pk)
    form = RoomForm(instance=room)
    topics = Topic.objects.all()
    if request.user != room.host:
        return HttpResponse('You are not allowed here')
    if request.method == 'POST':
         topic_name = request.POST.get('topic')
         topic, created = Topic.objects.get_or_create(name=topic_name)
         room.name = request.POST.get('name')
         room.topic = topic
         room.description = request.POST.get('description')
         room.save()


         return redirect('home')
    context = {'form': form, 'topics':topics, 'room':room}
    return render(request, 'base/room_form.html',context)

@login_required(login_url='login')
def deleteRoom(request, pk):
    room = Room.objects.get(id=pk)
    if request.user != room.host:
        return HttpResponse('You are not allowed to delete this room')
    if request.method == 'POST':
        room.delete()
        return redirect('home')
    return render(request, 'base/delete.html',{'obj':room})

@login_required(login_url='login')
def deleteMessage(request, pk):
    message_delete = get_object_or_404(message, id=pk)

    if request.user != message_delete.user:
        return HttpResponse('You are not allowed to delete this message')

    if request.method == 'POST':
        message_delete.delete()
        return redirect('home')

    return render(request, 'base/delete.html', {'obj': message_delete})

@login_required(login_url='login')
def updateUser(request):
    user = request.user
    form = Userform(instance=user)
    if request.method == 'POST':
        form = Userform (request.POST, request.FILES , instance=user)
        if form.is_valid():
            form.save()
            return redirect('user-profile', pk=user.id)
    return render(request, 'base/update-user.html', {'form': form})


def topicsPage(request):
    q = request.GET.get('q') if request.GET.get('q') != None else ''
    topics = Topic.objects.filter(name__icontains=q)
    return render(request, 'base/topics.html', {'topics':topics})

def activityPage(request):
    room_messages = message.objects.all()  # Fetch all messages
    # Debugging: Print message details
    for msg in room_messages:
        print(f"Message ID: {msg.id}, Body: {msg.body}, File: {msg.file}")
    return render(request, 'base/activity.html', {'room_messages': room_messages})

def video_call_view(request):
    room_id = request.GET.get('roomname')  # Get the room ID from the URL query string
    if not room_id:
        return HttpResponse("Room ID is required", status=400)

    room = get_object_or_404(Room, id=room_id)
    participants = room.participants.all()  # Fetch participants in the room

    context = {
        'room': room,
        'participants': participants,
    }
    return render(request, 'base/video_call.html', context)

#<-----END----->
