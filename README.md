# Smart Video Player

## Problem 
It has been observed that individuals average **71 daily minutes** on Netflix per day, resulting in a cumulative **165 million hours of Netflix watched daily** across the globe. That consumes nearly 500 million GB of bandwidth – equivalent to **15% of the world’s bandwidth.** This highlights the key problem that exists with many video streaming services -​ **resources go to waste when there is no interaction with the video.**

When users are not interacting with the video player, current video player technologies maintain a TCP connection between video controls and their server for the video streaming session. 

## Solution
An intelligent video streaming application that implements machine learning techniques to address the aforementioned problem. The goal is to track usage patterns of individual users; use machine learning techniques to assess these patterns; and suspend unnecessary connections to the client. Through the use of machine learning, when it is identified that a user will perform an action on the video player, the user's inaction is simultaneously identified. The server then can put the video player control functions to sleep while the user continues to watch.


## Installation

#### Install the following python packages:
```bash
pip3 install wxPython sklearn pymongo mongoengine numpy PyYAML
```

#### Install [mongodb](https://docs.mongodb.com/manual/tutorial/install-mongodb-on-os-x/) and start it:
```bash
brew services start mongodb-community@4.2
```

#### Place raw .mp4 files in folder outside of parent folder.

- smart-videoplayer(folder)
- Video1.mp4
- Video2.mp4

#### Open database/mongoConfig.py in editor

- Comment out line 100 and 114
- Add inside function:

```python
addVideo(Video(videoID="001", title="Video1", length=2152, genre=“Action"))
```
- ID should be 001, 002, 003 … etc.
- Length is in milliseconds.
- Title must be exactly the same as the .mp4 file name (from our example above it would be ‘Video1’).

#### Run mongoConfig.py:
```bash
python3 mongoConfig.py
```	

If this was done properly, open another terminal window and start mongo:
```mongo
mongo
use AwakeTree
show collections
db.video.find()
```	
You should see the video added. Repeat this with 3 other videos of choice.

## Usage

Start the control server
```bash
python3 controlServer.py
```	

Start the videoPlayer
```bash
python3 videoPlayer.py
```

Expand the video player, click on ‘Load Video 1.’
You can now interact with the video.

After you interact with the video and enough data is added, the next video you load it will generate predictions.

Before we jump into this, let's inspect the database to see what we’ve done.

```mongo
db.behaviour.find()
```
We can see all our actions clocked with their respective times (in ms).

Now try:
```mongo
db.prediction.find()
```
	
You can see that each genre has their own prediction array of times where the server and client should be connected.

If you go back to the video player you can see at the bottom right a status ‘Connected: True/False’ which denotes whether the server and client are connected or not.

Additionally, you can notice that if you attempt to interact with the video player while ‘Connected: False’ we cannot, as we are not connected to the server.

As you can see this is a proof of concept example that can be easily implemented onto a much larger infrastructure product.