import os
import shutil
import logging
import argparse

# Configure logging
logging.basicConfig(
    filename="organizer.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

# File categories
CATEGORIES = {
    ".py": "Python_Code",
    ".txt": "Documents",
    ".jpg": "Images",
    ".png": "Images"
}


def get_unique_filename(folder, filename):
    """Handle duplicate file names"""

    name, ext = os.path.splitext(filename)
    counter = 1
    new_filename = filename

    while os.path.exists(
        os.path.join(folder, new_filename)
    ):
        new_filename = (
            f"{name}({counter}){ext}"
        )
        counter += 1

    return new_filename


def organize_directory(
    source_folder,
    dry_run=False
):

    files_moved = 0
    errors_count = 0

    try:
        # Recursive scan
        for root, dirs, files in os.walk(
            source_folder
        ):

            for file in files:

                file_path = os.path.join(
                    root,
                    file
                )

                # Get extension
                ext = os.path.splitext(
                    file
                )[1].lower()

                # Get category
                folder_name = (
                    CATEGORIES.get(
                        ext,
                        "Other"
                    )
                )

                target_folder = (
                    os.path.join(
                        source_folder,
                        folder_name
                    )
                )

                # Create folder
                if not os.path.exists(
                    target_folder
                ):
                    os.makedirs(
                        target_folder
                    )

                # Skip if already organized
                if (
                    os.path.dirname(
                        file_path
                    )
                    == target_folder
                ):
                    continue

                # Handle duplicates
                new_filename = (
                    get_unique_filename(
                        target_folder,
                        file
                    )
                )

                target_path = (
                    os.path.join(
                        target_folder,
                        new_filename
                    )
                )

                # Dry run
                if dry_run:
                    print(
                        f"[DRY RUN] "
                        f"Would move: "
                        f"{file} → "
                        f"{folder_name}"
                    )

                else:
                    shutil.move(
                        file_path,
                        target_path
                    )

                    logging.info(
                        f"Moved: "
                        f"{file} -> "
                        f"{folder_name}"
                    )

                    files_moved += 1

    except Exception as e:
        logging.error(
            f"Error: {e}"
        )
        errors_count += 1

    # Summary
    print(
        "\nFile Organizer Summary"
    )
    print("----------------------")
    print(
        f"Files moved: "
        f"{files_moved}"
    )
    print(
        f"Errors encountered: "
        f"{errors_count}"
    )


# Command line arguments
parser = argparse.ArgumentParser()

parser.add_argument(
    "source",
    help="Folder path to organize"
)

parser.add_argument(
    "--dry-run",
    action="store_true",
    help="Preview without moving files"
)

args = parser.parse_args()

organize_directory(
    args.source,
    args.dry_run
)

