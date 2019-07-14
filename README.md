# radio-to-playlist
converts an iHeartRadio station's latest tracks into a Deezer playlist

## Getting Started
You'll need to add a configuration file as follows to `config.json` in the root directory.

```json
{
	"deezer_access_token": "XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX",
	"deezer_base_url": "https://XXXX.iheart.com",
	"deezer_playlist_id": 0123456789
}
```

### Getting a Deezer Access Token
[Deezer's docs](https://developers.deezer.com/api/oauth) are very good here and explain how to obtain a token.
**You need to use the *manage_library* permission** from Deezer.

### Deezer Base URL
Note that the `deezer_base_url` value should not have a trailing `/` and should be in the form of an `iheart.com` subdomain.

### Deezer Playlist ID
This can be found in the format: `https://www.deezer.com/<country_code>/playlist/<deezer_playlist_id>`.

You will need to own the playlist that you wish to modify and can create one through Deezer's website.
