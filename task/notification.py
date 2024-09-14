import json
from fcm_django.models import FCMDevice
from firebase_admin.messaging import Message, Notification


def notifyTask(user, notification, data):
    for device in FCMDevice.objects.all().filter(user=user):
        message = Message(
            notification=Notification(**notification),
            data=data  # Add data to the message
        )
        
        device.send_message(message)
        
        