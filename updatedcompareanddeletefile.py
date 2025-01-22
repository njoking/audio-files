#!/usr/bin/env python

"""ProcessAudioFiles.py: Process audio files listed in a CSV, check against background music list, and delete if older than 30 days."""

import csv
import os
import getpass
import cloudinary
import cloudinary.api
import logging
from datetime import datetime, timedelta

# Background music URL list (filenames that should not be deleted)
BACKGROUND_MUSIC_URLS = {
    "none": "",
    "default": "https://res.cloudinary.com/dsw0dw6j6/video/upload/v1731607560/tiktok_audio/default.mp3",
    "hard-as": "https://res.cloudinary.com/dsw0dw6j6/video/upload/v1731607548/tiktok_audio/hard-as.mp3",
    "wonders": "https://res.cloudinary.com/dsw0dw6j6/video/upload/v1731607550/tiktok_audio/wonders.mp3",
    "hot-pepper": "https://res.cloudinary.com/dsw0dw6j6/video/upload/v1731607551/tiktok_audio/hot-pepper.mp3",
    "transition": "https://res.cloudinary.com/dsw0dw6j6/video/upload/v1731607553/tiktok_audio/transition.mp3",
    "daylight": "https://res.cloudinary.com/dsw0dw6j6/video/upload/v1731607556/tiktok_audio/daylight.mp3",
    "cinematic-epic": "https://res.cloudinary.com/dsw0dw6j6/video/upload/v1731607558/tiktok_audio/cinematic-epic.mp3",
    "lovely": "https://res.cloudinary.com/dsw0dw6j6/video/upload/v1731607562/tiktok_audio/lovely.mp3",
    "emotional-chill": "https://res.cloudinary.com/dsw0dw6j6/video/upload/v1731607564/tiktok_audio/emotional-chill.mp3",
    "epic-cinematic": "https://res.cloudinary.com/dsw0dw6j6/video/upload/v1731607567/tiktok_audio/epic-cinematic.wav",
    "aura-fast": "https://res.cloudinary.com/dsw0dw6j6/video/upload/v1731607569/tiktok_audio/aura-fast.mp3",
    "summit": "https://res.cloudinary.com/dsw0dw6j6/video/upload/v1731607571/tiktok_audio/summit.mp3",
}

class ProcessAudioFiles:
    def __init__(self, cloud_name, api_key, api_secret):
        # Configure Cloudinary
        cloudinary.config(
            cloud_name=cloud_name,
            api_key=api_key,
            api_secret=api_secret
        )
        self.logger = logging.getLogger(__name__)
        logging.basicConfig(level=logging.INFO)

    def process_audio_files(self, csv_filename):
        """Process audio files: check if they match the background music list, check age, and delete if older than 30 days."""
        try:
            if not os.path.exists(csv_filename):
                self.logger.error(f"CSV file '{csv_filename}' does not exist.")
                return

            # Read the CSV file
            with open(csv_filename, mode="r", encoding="utf-8") as csvfile:
                reader = list(csv.reader(csvfile))
                if len(reader) <= 1:
                    self.logger.error("CSV file does not contain enough data to process.")
                    return

                # Exclude the header row
                audio_details = reader[1:]

                # List for files to be deleted and the remaining files
                files_to_delete = []
                remaining_files = []

                # Process each file
                for file_detail in audio_details:
                    filename = file_detail[0]  # Assuming the first column is the filename
                    created_at = datetime.strptime(file_detail[1], "%Y-%m-%d %H:%M:%S")  # Assuming the 2nd column is the creation date
                    
                    # Check if the filename matches any in the background music list
                    if filename in BACKGROUND_MUSIC_URLS.values():
                        self.logger.info(f"Skipping {filename} as it is in the background music list.")
                        remaining_files.append([filename, file_detail[1]])  # Add to remaining files
                        continue

                    # Check if the file is older than 30 days
                    if created_at < datetime.now() - timedelta(days=30):
                        # Placeholder for file deletion action
                        self.logger.info(f"File {filename} is older than 30 days and would be deleted.")
                        files_to_delete.append(filename)
                    else:
                        # If file is not older than 30 days, add to remaining files
                        remaining_files.append([filename, file_detail[1]])

                # Print files to be deleted (this is just a placeholder)
                if files_to_delete:
                    self.logger.info("The following files would be deleted: ")
                    for file in files_to_delete:
                        self.logger.info(f" - {file}")
                else:
                    self.logger.info("No files are older than 30 days and eligible for deletion.")

            # Save the remaining audio file details to a new CSV
            self.save_remaining_details_to_csv(remaining_files)

        except Exception as e:
            self.logger.error(f"Unexpected error while processing audio files: {e}")

    def save_remaining_details_to_csv(self, remaining_files):
        """Save the remaining audio file details to a new CSV file."""
        new_csv_filename = "RemainingAudioFileDetails.csv"
        try:
            with open(new_csv_filename, mode="w", newline="", encoding="utf-8") as csvfile:
                writer = csv.writer(csvfile)
                # Write header
                writer.writerow(["Filename", "Created At"])
                # Write remaining file details
                for detail in remaining_files:
                    writer.writerow([detail[0], detail[1]])  # Filename and Created At
            self.logger.info(f"Remaining audio file details saved to {new_csv_filename}")
        except Exception as e:
            self.logger.error(f"Error writing remaining audio file details to CSV: {e}")


if __name__ == "__main__":
    # Input Cloudinary credentials
    cloud_name = input("Your Cloudinary cloud name: ")
    api_key = input("Your Cloudinary API key: ")
    api_secret = getpass.getpass("Your Cloudinary API secret: ")

    # Input the CSV filename
    csv_filename = input("Enter the name of the CSV file with audio details: ")

    # Initialize and process the audio files
    process_files = ProcessAudioFiles(cloud_name, api_key, api_secret)
    process_files.process_audio_files(csv_filename)
