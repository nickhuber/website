Using Tasker and intents to play Google Play Music when you start driving
==========================================================================

:date: 2019-09-13
:modified: 2019-09-19
:category: Blog
:slug: intents-tasker-google-play-music-for-car
:tags: automation
:summary:
    What is needed to automatically play music from your phone when connecting
    to a bluetooth device.

What you will need:

- An Android phone
- Tasker_
- `Google Play Music`_
- A bluetooth device to connect to

I think it is easiest to start by creating the task, so go to the tasks view and
add a new task, giving it a name. In the lower right of this panel click the +
to begin adding a new action, and select "System" and then "Send Intent". The
intent information can be gained from this `useful reddit post`_ but what I entered was

.. code-block:: text

    Action:android.media.action.MEDIA_PLAY_FROM_SEARCH
    Cat:None
    Mime Type:
    Data:
    Extra:query:Driving
    Extra:android.intent.extra.focus:vnd.android.cursor.item/playlist
    Extra:
    Package:com.google.android.music
    Class:
    Target:Activity

You can then test the task by clicking the play button in the lower left, it
should open up Google Play Music and begin playing the playlist you selected.
Note that automatically generated playlists liked "Thumbs up" and "Last added"
don't seem to work with this method.

I had some issues if I played a radio with the same name from a previous bad
attempt at running the task, but just manually playing the playlist defined in
the query again seemed to correct this behaviour from ever happening again.

With that done its time to cause this task to trigger when we want it to. I use
the connection to my car's bluetooth system. In Tasker navigate to the Profiles
tab and create a new profile. Select "State" as the type and then choose "Net"
for the category, and then "BT Connected" You can use the magnifying glass
picker icon for both the name and address rows to ensure that this only triggers
when you connect to the specific bluetooth device that you want.

All that is left to do now is enable bluetooth and turn on the bluetooth device
and watch Tasker start playing your music for you. I found this much simpler
than fiddling with AutoTools_. I just wish that it was easier to discover and
use all the various intents that are available on your phone.

.. _Tasker: https://tasker.joaoapps.com/
.. _`Google Play Music`: https://play.google.com/music/listen#/home
.. _`useful reddit post`: https://reddit.com/r/tasker/comments/8m2csu/tasker_google_play_music_alarm_clock/dzl9o3m/
.. _`AutoTools`: https://joaoapps.com/autotools-supercharge-tasker/
