# Lightweight Push Library

Lightweight Push is a simple and easy to use push service. It lets you send end-to-end encrypted push messages to your Android mobile devices without hosting your own services or building your own App. The library uses the [AlertR Push Notification Service](https://alertr.de) which is build atop of [Google Firebase](https://firebase.google.com/). You only have to install the official [AlertR Android App](https://play.google.com/store/apps/details?id=de.alertr.alertralarmnotification) from Google Play to receive the messages and create an account at [alertr.de](https://alertr.de/register/). After that you can directly use the Lightweight Push library.

Unlike some other push service providers, Lightweight Push offers you real end-to-end encryption. The message is encrypted in the Lightweight Push directly before sending and decrypted on your Android devices. Neither the AlertR Push Notification Service nor Google can read the messages. Some other providers use the term "end-to-end encryption" only as marketing and do not have it. For example, some providers use a web api where the message is sent via a HTTPS request to the server of the provider. To state the simplicity of their service, they show commands with curl and the like that will make such a request and send you a push notification. However, the message in the shown requests is unencrypted and the encryption is done by the server of the provider before it is sent to your devices. So even though they use HTTPS, the message can still be read by the provider and therefore it is no end-to-end encryption.

Lightweight Push uses channels to send your messages to different Android devices. The Android devices subscribe to the channels they want to receive the messages from. This allows you to send messages triggered by specific events to different devices. For example in a server context, a failed HDD is only interesting for people responsible for hardware issues, but a failed server is also interesting for people working on this server.

Due to technical reasons, the subject and message size is at the moment limited to 1400 characters. However, if you send a message that is larger than 1400 characters, it will be truncated and send to you. In the near future this will change and a bigger size will be allowed.

You do not want to use some service on the Internet for this but host everything yourself? No problem, each component needed to send push messages is Open Source.

* [Push Server](https://github.com/sqall01/alertR-Push-Server)
* [Android App](https://github.com/sqall01/alertR-Push-Android)

A standalone console application for the library can be found [here](https://github.com/sqall01/lightweight-push).


# Installation and Usage

Lightweight Push is written for Python 2 and 3. For the encryption, it needs the `pycrypto` package. To make the installation of the Lightweight Push library as easy as possible, you can install it with pip via the following command:

```bash

pip --user install lightweightpush

```

Afterwards, all prerequisites are installed.

After you created and activated your [alertr.de](https://alertr.de/register/) account, the library is very easy to use. The following small script will send a push notification message to your mobile devices:

```python
import lightweightpush

push_service = lightweightpush.LightweightPush("my_email@alertr.de", "super_secret_password", "shared_secret_to_encrypt_msg")
push_service.send_msg("Subject of Message", "Message text", "MyChannel")
```

In order to receive the messages on your Android devices, you have to install the [AlertR Android App](https://play.google.com/store/apps/details?id=de.alertr.alertralarmnotification). The App settings screen looks like the following:

![Android App Settings](https://raw.githubusercontent.com/sqall01/lightweight-push-pip/master/pics/android_app_settings.jpg)

In the _Channel_ setting, a comma separated list of channels you want to receive with this device has to be set. As setting for our example configuration, we set only the following channel:

```bash
MyChannel

```

The _E-Mail Address_ setting is the used [alertr.de](https://alertr.de) username.

```bash
my_email@alertr.de

```

The _Shared Secret_ setting is used to decrypt the received messages. It has to be the same as the one configured in the Lightweight Push script.

```bash
shared_secret_to_encrypt_msg

```


# Infrastructure

The following image shows the used infrastructure:

![alertR Infrastructure Push](https://raw.githubusercontent.com/sqall01/lightweight-push-pip/master/pics/infrastructure_push.jpg)

Lightweight Push will encrypt your message with your shared secret and send it to the alertR Push Notification Service. The end-to-end encryption ensures that neither the alertR Push Notification Service nor the Google Firebase service is able to read your message. The message will be sent on a channel that you choose. The channel is used to be able to receive the same message on multiple devices you own or want to be able to receive the message. In order to prevent multiple uses of the same channel by different users and therefore collisions, the channel is linked to your alertr.de account. In the unlikely event that an attacker is able to deduce your used channel, only devices that know your used secret are able to decrypt the message. This is shown in the infrastructure image as an example. An attacker subscribes for the channel "MyAlarm" that is used by another user. The message is encrypted with the secret "MySecret". But only the device using this secret is able to decrypt the message.


# Support

If you like this project you can help to support it by contributing to it. You can contribute by writing tutorials, creating and documenting exciting new ideas to use it, writing code for it, and so on.

If you do not know how to do any of it or do not have the time, you can support me on [Patreon](https://www.patreon.com/sqall). Since services such as the push notification service have a monthly upkeep, the donation helps to keep these services free for everyone.

[![Patreon](https://c5.patreon.com/external/logo/become_a_patron_button.png)](https://www.patreon.com/sqall)


# Bugs and Feedback

For questions, bugs and discussion please use the [Github Issues](https://github.com/sqall01/lightweight-push-pip/issues).