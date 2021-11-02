Replacing Nvidia Shield launcher
=================================

:date: 2021-11-01
:category: Blog
:slug: replacing-nvidia-shield-launcher
:tags: android
:summary:
    Android TV recently added ads to their home screen and I finally cared
    enough to do something about it.

Some time ago, there was an update to Android TV that added some "Hightlights"
section taking up the top 30% of the screen space on your TV. These would range
from irrelevant to disturbing depending on the content that Google decided to
show you. Apparently Google doesn't consider this to be an advertisement,
although I don't see how you could consider showing me content I don't own and
asking me to buy it isn't considered an advertisement but maybe you see the
world differently when you are an advertising company.

Why is this the world we live in?
----------------------------------

There is a
`support page <https://support.google.com/androidtv/thread/114562604/highlights-are-terrible-and-nearly-universally-disliked-why-can-we-not-disable-them?hl=en>`_
Asking for an option to disable this "feature", and the answer from a google
product employee was to downgrade the application to a version from before they
made this change. I decided if I'm going to be changing versions of things I
sure am not going to be continuing to use a Google application.

Trying to take a quicker approach
----------------------------------

I tried blocking the domain `androidtvwatsonfe-pa.googleapis.com` on my router,
but that just changed the ads from annoying features on TV shows and/or movies I
don't care about to trying to tell me to use YouTube and Google TV, which was
almost more annoying.

Taking the "nuke it from orbit" approach
-----------------------------------------

Luckily it is actually pretty easy to replace the stock launcher, although it
does require some minor technical competence at using `abd` to disable the stock
launcher. I decided to try out
`FLauncher <https://gitlab.com/etienn01/flauncher>`_ which is available on the
Android app store. I was able to load the application and see what it looks like
and it seemed like a perfect fit. Nice and simple and just shows me a listing of
the few streaming application I like to use. Where `adb` comes in to play is
when you want to actually disable the stock launcher and have the Nvidia Shield
device load directly into this ad-free environment.

Enabling `adb` connections over the network on the Nvidia Shield is easy
enough::

    Android Settings
    │
    └─ Device Preferences
        │
        └─ About
            │
            ├─ Build (click 7 times, this enables the hidden "Developer Options")
            │
            └─ Developer Options
                │
                └─ Network Debugging


Take note of the IP and port next to Network Debugging, you will need this in a moment.

If you don't already have `adb` installed you can either figure out how to
install it on your host OS, or just do what I did and run an `Ubuntu` docker
container and do `apt install adb` in there.

With `adb` ready to go, just run `adb connect <ip:port from previous step>` and
then accept a prompt from the Android device to trust this connection.

The only thing we need to do is disable the launcher, and to do that we can just
run `adb shell pm disable-user --user 0 com.google.android.tvlauncher`.

The Android device should now ask you which launcher you want to use (I had a
few installed at the time, maybe it doesn't list anything for you if you only
have one), Assuming it presents you a choice, make one and then a reboot should
now be all you need to confirm that you don't see any advertisements on your
launcher.

Closing remarks
----------------

I did disable a few other services as well in earlier troubleshooting, but I
don't think they are relevant to swapping the launcher. For the sake of
completeness they were `com.google.android.leanbacklauncher` and
`com.google.android.leanbacklauncher.recommendations`

It is maybe a good idea to turn off the network debugging option when you are
done, since it probably reduces the overall security of your device or
something.
