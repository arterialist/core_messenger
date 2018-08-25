# Core Messenger

![Logo](https://github.com/arterialist/core_messenger/blob/master/images/app-icon-128.png?raw=true)
## What is this?
Core messenger is yet another P2P messenger with optional [servers](https://github.com/arterialist/core_server) that can be used as relay node or chatroom. It's based on [core_client](https://github.com/arterialist/core_client), and it means that everyone can try to create their own messenger using it. Core_proto is, despite being under heavy development, very flexible in terms of behaviour customisation. It supports plugins, which basically just modify incoming/outcoming data and react to it.

## Possibilities

- Complete anonymity (no ids, phone numbers, accounts, just username and port)
- Up to 1024 simultaneous connections (possibly will be expanded in the future)
- Thanks to [servers](https://github.com/arterialist/core_server), can work under NAT (more solutions are planned)
- More to come with time (_just try it now_)

## Short FAQ

**Q: Where are my prebuilt binaries for Windows, Linux and MacOS?**

A: This product is now very unstable, untested (_testers needed_), and actively developed, so I see no reason to build new binaries each and every feature/commit/fix/etc. as for now. In the future, when this project will reach alpha state, I will setup automatic build and deploy to _Releases_ section.

**Q: Why are you using self-made protocol, library etc.?**

A: I'm a programmer (obviously), and I truly enjoy programming when I really create something new from ground up. Also making my own protocol/library helps me to learn a lot about different things, which is true pleasure. I could use such things as libp2p and MTProto, but what's the point of making basically another GUI for existing and widely used tools?

**Q: Is it safe? Do you have any encryption implemented or at least in plans?**

A: I have AES256 encryption at packet level implemented, as per [this commit](https://github.com/arterialist/core_client/commit/f18691c7e68f029123cc783e2cf68a242e7afba5), but as you can see it from the commit message, it's experimental. My main goal now is to build flexible and powerful plugin system, so anyone with some python coding skills can create its own plugin. Is it safe? Well, you can enable AES256 plugin and change secret key (don't forget to tell it to opponent), and your messaging will be safe. Again, more security coming soon (encrypted database too).

## Requirements and Installation

### Requirements

- python 3.6 or above
- Qt5 installed in the system (usually you don't need to care about this)

### Installation

- `git clone https://github.com/arterialist/core_messenger.git`
- `cd core_messenger`
- `pip3 install -r requirements.txt` (or just `pip3 install pyqt5`)
Done! Launch with `python3 main.py`

## Other Info

### Useful Links
- [Core Client](https://github.com/arterialist/core_client)
- [Core Server](https://github.com/arterialist/core_server)

Author: Arterialist [GitHub](https://github.com/arterialist) | [Telegram](https://t.me/arterialist)