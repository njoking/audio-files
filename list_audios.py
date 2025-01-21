#!/usr/bin/env python

"""CloudinaryFileCounts.py: Fetch all files and generate CSV with audio file details."""

import csv
import os
import getpass
import cloudinary
import cloudinary.api
import logging
import json


class CloudinaryFileCounts:
    AUDIO_DETAILS_FILENAME = "AudioFileDetails.csv"

    def __init__(self, cloud_name, api_key, api_secret):
        # Configure Cloudinary
        cloudinary.config(
            cloud_name=cloud_name,
            api_key=api_key,
            api_secret=api_secret
        )
        self.base_dir = os.path.dirname(__file__)
        self.logger = logging.getLogger(__name__)
        logging.basicConfig(level=logging.INFO)

    def get_audio_files_details(self):
        """Fetch the details of audio files (stored as video resources)."""
        audio_details = []
        try:
            self.logger.info("Fetching details for audio files (video type in Cloudinary).")
            next_cursor = None

            while True:
                response = cloudinary.api.resources(
                    resource_type="video",
                    type="upload",
                    max_results=50,  # Reduced batch size for faster responses
                    next_cursor=next_cursor,
                    timeout=60  # Set timeout to 60 seconds
                )

                if not response or 'resources' not in response:
                    self.logger.warning(f"No valid response for video (audio) files. Response: {response}")
                    break

                for resource in response['resources']:
                    filename = resource.get('public_id', 'Unknown')
                    created_at = resource.get('created_at', 'Unknown')
                    audio_details.append({"filename": filename, "created_at": created_at})

                next_cursor = response.get('next_cursor')
                if not next_cursor:
                    break

            self.logger.info(f"Fetched {len(audio_details)} audio files.")
        except cloudinary.exceptions.Error as e:
            self.logger.error(f"Cloudinary error fetching audio files: {e}")
        except json.JSONDecodeError as e:
            self.logger.error(f"JSON decoding error while parsing the response: {e}")
        except KeyboardInterrupt:
            self.logger.warning("Script interrupted by user.")
        except Exception as e:
            self.logger.error(f"Unexpected error: {e}")

        return audio_details

    def save_details_to_csv(self, filename, audio_details):
        """Save the audio file details to a CSV file."""
        output_path = os.path.join(self.base_dir, filename)
        try:
            with open(output_path, mode="w", newline="", encoding="utf-8") as csvfile:
                writer = csv.writer(csvfile)
                # Write header
                writer.writerow(["Filename", "Created At"])
                # Write file details
                for detail in audio_details:
                    writer.writerow([detail["filename"], detail["created_at"]])
            self.logger.info(f"Audio file details saved to {output_path}")
        except Exception as e:
            self.logger.error(f"Error writing audio file details to CSV file: {e}")

    def process_audio_details(self):
        """Fetch audio file details and save them to a CSV file."""
        audio_files_details = self.get_audio_files_details()  # Fetch audio file details

        # Save the details of audio files to a CSV file
        self.save_details_to_csv(self.AUDIO_DETAILS_FILENAME, audio_files_details)


if __name__ == "__main__":
    # Input Cloudinary credentials
    cloud_name = input("Your Cloudinary cloud name: ")
    api_key = input("Your Cloudinary API key: ")
    api_secret = getpass.getpass("Your Cloudinary API secret: ")

    # Initialize and process audio details
    cloudinary_file_counts = CloudinaryFileCounts(cloud_name, api_key, api_secret)
    cloudinary_file_counts.process_audio_details()
