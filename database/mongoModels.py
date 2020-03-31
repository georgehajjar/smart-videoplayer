import mongoengine

class Video(mongoengine.Document):
    videoID = mongoengine.StringField(required=True, unique=True, max_length=3) #Limit to 3 chars
    title = mongoengine.StringField(required=True) #Also used as name of video file (must hold true in order to locate video)
    length = mongoengine.IntField(required=True) #Stored in milliseconds so no need for double/float
    genre = mongoengine.StringField(required=True)

class Behaviour(mongoengine.Document):
    videoID = mongoengine.StringField(required=True) #Used to reference Video collection
    played = mongoengine.ListField() #Milliseconds
    paused = mongoengine.ListField() #Milliseconds
    rewound = mongoengine.ListField() #Milliseconds
    fastforwarded = mongoengine.ListField() #Milliseconds

class Prediction(mongoengine.Document):
    genre = mongoengine.StringField(required=True)
    activateControls = mongoengine.ListField() #List of times where action is anticipated
