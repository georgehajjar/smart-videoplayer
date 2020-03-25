from pymongo import MongoClient
import mongoengine
from mongoModels import Video, Behaviour

mongo = MongoClient()
mongo = MongoClient('localhost', 27017)
db = mongo['AwakeTree']
mongoengine.connect('AwakeTree')

#Tables (Collections)
videos = db["videos"]
videoBehaviour = db["videoBehaviour"]

def addVideo(Video):
    Video.save()

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
    for elem in filteredVideos:
        print(elem.videoID)

# def seedDatabase():
#     addVideo(Video(videoID="001", title="video1", length=21.52, genre="Action"))
#     addVideo(Video(videoID="002", title="Summer2015", length=21.52, genre="Action"))
    # addVideo(Video(videoID="003", path="", title="video3", length=0.0, genre="Comedy"))
    # addVideo(Video(videoID="004", path="", title="video4", length=0.0, genre="Action"))
    # addVideo(Video(videoID="005", path="", title="video5", length=0.0, genre="Drama"))
    # addVideo(Video(videoID="006", path="", title="video6", length=0.0, genre="Action"))
    # addPlayBehaviour(Behaviour(videoID="001", played=[1]))
    # addPlayBehaviour(Behaviour(videoID="001", played=[2]))
    # addPlayBehaviour(Behaviour(videoID="001", played=[3]))
    # addFFBehaviour(Behaviour(videoID="001", fastforwarded=[4]))
    # addFFBehaviour(Behaviour(videoID="001", fastforwarded=[2]))
    # addRWBehaviour(Behaviour(videoID="001", rewound=[10]))
    # addPauseBehaviour(Behaviour(videoID="001", paused=[8]))
    # addRWBehaviour(Behaviour(videoID="001", rewound=[6]))

# seedDatabase()
