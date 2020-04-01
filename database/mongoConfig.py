from pymongo import MongoClient
import mongoengine
from mongoModels import Video, Behaviour, Prediction

mongo = MongoClient()
mongo = MongoClient('localhost', 27017)

#Database name
db = mongo['AwakeTree']
mongoengine.connect('AwakeTree')

#Tables (Collections)
videos = db["videos"]
videoBehaviour = db["videoBehaviour"]
predictions = db["predictions"]

def addVideo(video):
    video.save()

def findVideoById(videoID):
    try:
        return Video.objects(videoID=str(videoID)).get()
    except:
        print("No video with that ID found")

def findVideoByTitle(title):
    try:
        return Video.objects(title=str(title)).get()
    except:
        print("No video with that title found")

def findVideosByGenre(genre):
    try:
        return Video.objects(genre=str(genre))
    except:
        print("No videos with that genre found")

def addPlayBehaviour(played):
    try:
        Behaviour.objects(videoID=played.videoID).get()
    except:
        played.save()
    else:
        Behaviour.objects(videoID=played.videoID).update(push__played__1=played.played)

def addPauseBehaviour(paused):
    try:
        Behaviour.objects(videoID=paused.videoID).get()
    except:
        paused.save()
    else:
        Behaviour.objects(videoID=paused.videoID).update(push__paused__1=paused.paused)

def addFFBehaviour(fastforwarded):
    try:
        Behaviour.objects(videoID=fastforwarded.videoID).get()
    except:
        fastforwarded.save()
    else:
        Behaviour.objects(videoID=fastforwarded.videoID).update(push__fastforwarded__1=fastforwarded.fastforwarded)

def addRWBehaviour(rewound):
    try:
        Behaviour.objects(videoID=rewound.videoID).get()
    except:
        rewound.save()
    else:
        Behaviour.objects(videoID=rewound.videoID).update(push__rewound__1=rewound.rewound)


def filterBehaviourByGenre(genre):
    filteredVideos = []
    for video in findVideosByGenre(genre):
        try:
            Behaviour.objects(videoID=video.videoID).get()
        except:
            print("No behaviour associated with that video added yet")
        else:
            filteredVideos.append(Behaviour.objects(videoID=video.videoID).get())
    # for elem in filteredVideos:
    #     print(elem.videoID)
    return filteredVideos

def addPrediction(prediction):
    try:
        Prediction.objects(genre=prediction.genre).get()
    except:
        prediction.save()
    else:
        Prediction.objects(genre=prediction.genre).update(set__activateControls=prediction.activateControls)
        # if not prediction.activateControls[0] in Prediction.objects(genre=prediction.genre).get().activateControls:
        #     Prediction.objects(genre=prediction.genre).update(push__activateControls__1=prediction.activateControls)

def findPredictionByGenre(genre):
    try:
        return Prediction.objects(genre=str(genre)).get().activateControls
    except:
        print("No prediction with that genre found")

# def seedDatabase():
    # addVideo(Video(videoID="001", title="video1", length=2152, genre="Action"))
    # addVideo(Video(videoID="002", title="Summer2015", length=2152, genre="Action"))
    # addVideo(Video(videoID="003", title="Horror1", length=2152, genre="Horror"))
    # addVideo(Video(videoID="004", title="Comedy1", length=2152, genre="Comedy"))
    # addVideo(Video(videoID="005", title="Drama1", length=2152, genre="Drama"))
    # addPlayBehaviour(Behaviour(videoID="001", played=[0, 20, 40, 60]))
    # addPauseBehaviour(Behaviour(videoID="001", paused=[1, 25, 30]))
    # addFFBehaviour(Behaviour(videoID="001", fastforwarded=[50]))
    # addRWBehaviour(Behaviour(videoID="001", rewound=[89]))
    # addPlayBehaviour(Behaviour(videoID="002", played=[0, 21, 41, 61]))
    # addPauseBehaviour(Behaviour(videoID="002", paused=[5, 22, 90]))
    # addFFBehaviour(Behaviour(videoID="002", fastforwarded=[60]))
    # addRWBehaviour(Behaviour(videoID="002", rewound=[99]))
# seedDatabase()
