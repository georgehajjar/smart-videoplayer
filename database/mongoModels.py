import mongoengine

class Video(mongoengine.Document):
    videoID = mongoengine.StringField(required=True, unique=True, max_length=3) #Limit to 3 chars
    title = mongoengine.StringField(required=True)
    length = mongoengine.IntField(required=True) #Stored in seconds so no need for double/float
    genre = mongoengine.StringField(required=True)
    # path = mongoengine.StringField(required=True) #Location of video file
    # meta = {'allow_inheritance': True}

class Behaviour(mongoengine.Document):
    videoID = mongoengine.StringField(required=True) #Used to reference Video collection
    paused = mongoengine.ListField()
    played = mongoengine.ListField()
    rewound = mongoengine.ListField()
    fastforwarded = mongoengine.ListField()

class Predictions(mongoengine.Document):
    activateControls = mongoengine.ListField()
