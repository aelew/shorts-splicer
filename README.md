# 🎬 shorts-splicer
 
A program that lets you automatically split up existing shorts and reupload them to YouTube and TikTok.

> [!WARNING]  
> This project is no longer actively maintained. The code is available for demonstration purposes, but please be aware that no updates or support will be provided for it.

## How it works
When you run the program, it will ask you if you want to split up your video, or construct one using clips you've already split up.

If you choose to split up a video, it will:
- Prompt you for the path to the video you want to split up
- Automatically detect scenes in the video
- Split the video into multiple clips and save them to `/clips`

If you choose to construct a new video, it will:
- Choose a random selection of clips from `/clips`
- Concatenate the chosen clips into a new video
- Delete the old clips from `/clips`
- Upload the new video to the platform of your choice.

Settings can be customized in [config/settings.json](config/settings.json).  
TikTok support is currently not implemented.

## Run locally

Clone the project

```bash
git clone https://github.com/aelew/shorts-splicer.git
```

Go to the project directory

```bash
cd shorts-splicer
```

Install dependencies

```bash
pip install -r requirements.txt
```

Start the splicer

```bash
py main.py
```

## 🧾 License

This project is licensed under the [MIT](LICENSE) license.
