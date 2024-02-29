# Music_Badger-Youtube_Feed

Application to tag and filter youtube channels.
like youtube subscription feed but all channel uploads are taged

better docs soon

## Installation

Install from [Docker Hub](https://hub.docker.com/r/pidi3000/music_badger-youtube_feed)

## Create channel

A new channel entry can be created using:

- A video from the channel
- the channel ID
- the channel handle

regardless of the following rules if the `Channel Link` field contains the domains
`youtube.com` or `youtu.be`, they and everything before will be removed.

### from video

When creating from a video the `Channel Link` field must:

- be a URL with the path `watch?`, AND
- have URL parameter `v=video_id` at any position

it can contain other URL parameters like :

- `si=xyz`

### from ID

When creating using the channel ID the `Channel Link` field must:

- be a URL with the path `channel/` followed by the channel ID, OR
- be only the channel ID, but MUST start with 'UC'

### from handle

When creating using the channel handle the `Channel Link` field must:

- only be the channel handle, startinn with `@` is recommended

### Examples

Good:

- `youtube.com/watch?v=VIDEO_ID`
- `watch?si=xyz&v=VIDEO_ID`
- `channel/CHANNEL_ID`
- `UCabc` (id starting with 'UC')
- `https://youtu.be/CHANNEL_HANDLE`
- `youtube.com/@CHANNEL_HANDLE`
- `@CHANNEL_HANDLE`
- `CHANNEL_HANDLE`

Bad:

- `abc` (will be interpreted as channel handle)
- `v=VIDEO_ID`
