# CozmoLetsRobot
Host Anki Cozmo on LetsRobot.tv

## Pre-setup
## install socketIO-client for python3
pip3 install socketIO-client

## Setup instructions:

Setup the Cozmo SDK on your computer using their instructions:

* http://cozmosdk.anki.com/docs/initial.html#installation

Clone Nocturnal's fork of the runmyrobot scripts:

* git clone https://github.com/Nocturnal42/runmyrobot.git

Copy the files from this repo to the appropriate directories:

* Copy hardware/cozmo.py to runmyrobot/hardware

* Copy tts/cozmo_tts.py to runmyrobot/tts

Edit runmyrobot/letsrobot.sample.conf:

* Enter your owner, robot_id, camera_id from LetsRobot.tv
* change [robot] type=none to type=cozmo
* change [tts] type=none to type=cozmo_tts
* Save file as letsrobot.conf

## Extra Mac setup instructions:
## install ffmpeg:
brew install ffmpeg

## Starting Cozmo:

* Using the Cozmo app enter SDK mode and connect your mobile device to the host machine.
* Execute the LetsRobot controller using `python3 controller.py`
* For audio streaming execute python send_video.py YOURCAMERAID 0 --no-camera &

## Update the Let's Robot robot configuration to have these custom controls:
```
[  
   {  
      "button_panels":[  
         {  
            "button_panel_label":"movement controls",
            "buttons":[  
               {  
                  "label":"Left",
                  "command":"L"
               },
               {  
                  "label":"Right",
                  "command":"R"
               },
               {  
                  "label":"Forward",
                  "command":"F"
               },
               {  
                  "label":"Backward",
                  "command":"B"
               },
               {  
                  "label":"LookUp",
                  "command":"Q"
               },
               {  
                  "label":"LookDown",
                  "command":"A"
               },
               {  
                  "label":"LiftUp",
                  "command":"W"
               },
               {  
                  "label":"LiftDown",
                  "command":"S"
               },
               {  
                  "label":"LightToggle",
                  "command":"V"
               }
            ]
         },
         {  
            "button_panel_label":"animation controls",
            "buttons":[  
               {  
                  "label":"drat",
                  "command":"0"
               },
               {  
                  "label":"giggle",
                  "command":"1"
               },
               {  
                  "label":"wow",
                  "command":"2"
               },
               {  
                  "label":"tick tock",
                  "command":"3"
               },
               {  
                  "label":"ping pong",
                  "command":"4"
               },
               {  
                  "label":"meow",
                  "command":"5"
               },
               {  
                  "label":"wufwuf",
                  "command":"6"
               },
               {  
                  "label":"lookup",
                  "command":"7"
               },
               {  
                  "label":"excite",
                  "command":"8"
               },
               {  
                  "label":"backup",
                  "command":"9"
               }
            ]
         },
         {  
            "button_panel_label":"say something cute",
            "buttons":[  
               {  
                  "label":"hello",
                  "command":"sayhi"
               },
               {  
                  "label":"watch this",
                  "command":"saywatch"
               },
               {  
                  "label":"love you",
                  "command":"saylove"
               },
               {  
                  "label":"bye",
                  "command":"saybye"
               },
               {  
                  "label":"happy",
                  "command":"sayhappy"
               },
               {  
                  "label":"sad",
                  "command":"saysad"
               },
               {  
                  "label":"howru",
                  "command":"sayhowru"
               }
            ]
         },
         {  
            "button_panel_label":"more fun stuff",
            "buttons":[  
               {  
                  "label":"singsong",
                  "command":"singsong",
                  "premium":true,
                  "price":1000000
               },
               {  
                  "label":"lightcubes",
                  "command":"lightcubes",
                  "premium":true,
                  "price":0
               },
               {  
                  "label":"dimcubes",
                  "command":"dimcubes",
                  "premium":true,
                  "price":0
               }
            ]
         }
      ]
   }
]
```

## Note for audio streaming on MacOS:

The `startAudioCaptureLinux` function in send_video.py calls ffmpeg with alsa input. If you want to stream audio from your mac use `-f avfoundation -i ":0"` in place of `-f alsa -ar 44100 -ac %d -i hw:%d`

Remove the first two arguments in the parentheses since you're removing two %d's

I also recommend changing the audio streaming bitrate from 32k to 128k with `-b:a 128k` in the same ffmpeg call.