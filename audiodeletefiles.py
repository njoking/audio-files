#!/usr/bin/env python

"""DeleteLastFiveAudioFiles.py: Delete the last 5 audio files listed in a CSV and generate a new CSV with remaining files."""

import csv
import os
import getpass
import cloudinary
import cloudinary.api
import logging


class DeleteLastFiveAudioFiles:
    def __init__(self, cloud_name, api_key, api_secret):
        # Configure Cloudinary
        cloudinary.config(
            cloud_name=cloud_name,
            api_key=api_key,
            api_secret=api_secret
        )
        self.logger = logging.getLogger(__name__)
        logging.basicConfig(level=logging.INFO)

    def delete_audio_files(self, csv_filename):
        """Delete the last 5 audio files listed in the CSV and create a new CSV with remaining files."""
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

                # Check if there are at least 5 files to delete
                if len(audio_details) < 5:
                    self.logger.warning("The CSV file has fewer than 5 audio files. Deleting all available files.")
                
                # Get the last 5 (or fewer) entries to delete
                files_to_delete = audio_details[-5:]
                remaining_files = audio_details[:-5]  # Keep the files that aren't deleted

                # Delete the last 5 audio files
                for file_detail in files_to_delete:
                    filename = file_detail[0]  # Assuming the first column is the filename
                    try:
                        response = cloudinary.api.delete_resources([filename], resource_type="video")
                        if response.get("deleted", {}).get(filename) == "deleted":
                            self.logger.info(f"Successfully deleted: {filename}")
                        else:
                            self.logger.warning(f"Failed to delete: {filename}")
                    except cloudinary.exceptions.Error as e:
                        self.logger.error(f"Error deleting file '{filename}': {e}")

            # Save the remaining audio file details to a new CSV
            self.save_remaining_details_to_csv(remaining_files)

        except Exception as e:
            self.logger.error(f"Unexpected error while deleting audio files: {e}")

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

    # Initialize and delete the last 5 audio files
    delete_files = DeleteLastFiveAudioFiles(cloud_name, api_key, api_secret)
    delete_files.delete_audio_files(csv_filename)
