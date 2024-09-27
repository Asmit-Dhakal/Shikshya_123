from rest_framework import generics
from rest_framework.permissions import IsAuthenticated

from .models import ChatRoom, Message
from .serializers import ChatRoomSerializer, MessageSerializer

class ChatRoomListCreate(generics.ListCreateAPIView):
    queryset = ChatRoom.objects.all()
    serializer_class = ChatRoomSerializer

class MessageListCreate(generics.ListCreateAPIView):
    serializer_class = MessageSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        room_name = self.kwargs['room_name']
        print(f'Fetching messages for room: {room_name}')
        return Message.objects.filter(room__name=room_name)

    def perform_create(self, serializer):
        room_name = self.kwargs['room_name']
        room = ChatRoom.objects.get(name=room_name)
        print(f'Saving new message in room: {room_name}')
        serializer.save(room=room, user=self.request.user)
