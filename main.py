import json
import os
import random
import sys

from moviepy.video.compositing.concatenate import concatenate_videoclips
from moviepy.video.io.VideoFileClip import VideoFileClip
from scenedetect import detect, split_video_ffmpeg, AdaptiveDetector
from scenedetect.platform import get_file_name
from send2trash import send2trash
from simple_youtube_api.Channel import Channel
from simple_youtube_api.LocalVideo import LocalVideo


def upload_to_youtube():
    title = config["youtube"]["title"].replace("{part}", str(config["part"]))

    channel = Channel()
    channel.login("config/client_secret.json", "config/credentials.storage")

    video = LocalVideo(input_video_path, title, description=config["youtube"]["description"], tags=config["youtube"]["tags"])
    video.set_privacy_status(config["youtube"]["privacy"])
    video.set_tags(config["youtube"]["tags"])
    video = channel.upload_video(video)

    print(f"Your video has been uploaded to YouTube!")
    print(f"> ID: {video.id}")
    print(f"> Link: https://youtu.be/{video.id}")
    print(f"> Title: {title}")


def construct_video():
    global input_video_path

    clip_files = [file_name for file_name in os.listdir("./clips") if file_name.endswith(".mp4")]

    clips_to_select = int(config["clips_per_video"])
    if len(clip_files) < clips_to_select:
        print(f"Not enough clips available. You have {len(clip_files)}, but need at least {clips_to_select} to construct a video.")
        return

    selected_clips = random.sample(clip_files, clips_to_select)
    output_file_name = f"output-{config["part"]}.mp4"

    print("\nConcatenating clips, please wait...")
    vfc_list = [VideoFileClip(f"clips/{clip}", target_resolution=(1920, 1080)) for clip in selected_clips]

    video = concatenate_videoclips(vfc_list, method="compose")
    video.write_videofile(output_file_name, audio_codec="aac", fps=30)

    print(f"Exported video to {output_file_name}!")
    print(f"Clips used: {", ".join(selected_clips)}")

    if config["delete_after_use"]:
        for clip in selected_clips:
            send2trash(f"clips/{clip}")
        print(f"Deleted {clips_to_select} used clip{"s" if clips_to_select != 1 else ""}.")

    input_video_path = output_file_name


def split_video():
    print("Analyzing scenes, please wait...")
    scene_list = detect(input_video_path, AdaptiveDetector(adaptive_threshold=config["threshold"]), show_progress=True)

    print(f"\nDetected {len(scene_list)} scenes, filtering...")

    # Remove scenes that are less than three seconds long
    scene_list = list(filter(lambda s: s[1].get_seconds() - s[0].get_seconds() > 3, scene_list))

    for i, scene in enumerate(scene_list):
        print("- Scene %d | Start: %s (Frame %4d) / End: %s (Frame %4d) / Length: %.3fs" % (
            i + 1,
            scene[0].get_timecode(), scene[0].get_frames(),
            scene[1].get_timecode(), scene[1].get_frames(),
            scene[1].get_seconds() - scene[0].get_seconds()))

    print(f"\nExporting {len(scene_list)} scenes...")

    video_name = get_file_name(input_video_path, include_extension=False).replace(" ", "_")
    code = split_video_ffmpeg(input_video_path, scene_list, output_file_template=f"clips/{video_name}-Clip-$SCENE_NUMBER.mp4", show_progress=True)
    if code != 0:
        return

    print("Scenes exported with ffmpeg code 0.")


if __name__ == "__main__":
    with open("config/settings.json", "r") as f:
        config = json.load(f)

    print(f"shorts-splicer (YouTube: {config["youtube"]["enabled"]} | TikTok: {config["tiktok"]["enabled"]})\n")

    if len(sys.argv) > 1:
        input_video_path = sys.argv[1]
        action = 1
    else:
        input_video_path = None
        action = -1
        while True:
            try:
                action = int(input("What would you like to do? [1: split, 2: construct]\n> "))
                if action == 1 or action == 2:
                    break
                print("Please enter a valid option.")
            except ValueError:
                print("Please enter a valid option.")
                pass
    
    match action:
        case 1:
            if input_video_path is None:
                input_video_path = input("Video path:\n> ")
            split_video()
        case 2:
            construct_video()

            if config["youtube"]["enabled"]:
                print("\nUploading to YouTube...")
                upload_to_youtube()
            
            if config["tiktok"]["enabled"]:
                print("\nUploading to TikTok...")
                # TODO: tiktok support
            
            with open("config/settings.json", "w") as fw:
                config["part"] += 1
                json.dump(config, fw, indent=2)
