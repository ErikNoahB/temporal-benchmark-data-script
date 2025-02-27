import os
import re
import random
import csv
import argparse
import calendar
import sys

# Centrally defined default values for random ranges
DEFAULT_YEARS_RANGE = (5, 10)
DEFAULT_VALID_START_RANGE = (3, 5)
DEFAULT_VALID_END_RANGE = (2, 7)

# Regex pattern to match date format YYYY-MM-DDTHH:MM:SS.sss+0000
pattern = r"(\d{4})-(\d{2})-(\d{2})T(\d{2}:\d{2}:\d{2}\.\d{3}\+\d{4})"

def is_leap_year(year):
    """
    Check if a given year is a leap year.
    
    :param year: The year to check.
    :type year: int
    :return: True if leap year, False otherwise.
    :rtype: bool
    """
    return (year % 4 == 0 and year % 100 != 0) or (year % 400 == 0)


def generate_random_date(year):
    """
    Generate a random, valid date for a given year.
    
    :param year: Year for which the date is generated.
    :type year: int
    :return: A string representing a random date in the format YYYY-MM-DD.
    :rtype: str
    """
    month = random.randint(1, 12)
    
    if month == 2:
        if is_leap_year(year):
            max_day = 29
        else:
            max_day = 28
    else:
        max_day = calendar.monthrange(year, month)[1]
    
    day = random.randint(1, max_day)
    return f"{year}-{month:02d}-{day:02d}"


def generate_dates(match, random_years, random_valid_start_year, random_valid_end_year):
    """
    Generate deletion and validation dates based on a given creation date.
    
    :param match: Regex match object containing the creation date.
    :type match: re.Match
    :param random_years: Number of years to add for deletion date.
    :type random_years: int
    :param random_valid_start_year: Offset for valid start year.
    :type random_valid_start_year: int
    :param random_valid_end_year: Offset for valid end year.
    :type random_valid_end_year: int
    :return: Tuple containing deletion date, valid start, and valid end.
    :rtype: tuple[str, str, str]
    """
    creation_year = int(match.group(1))
    time_part = match.group(4)

    deletion_year = creation_year + random_years
    valid_start_year = creation_year + random_valid_start_year
    valid_end_year = valid_start_year + random_valid_end_year

    deletion_date = f"{deletion_year}-{generate_random_date(deletion_year)[5:]}T{time_part}"
    valid_start = f"{valid_start_year}-{generate_random_date(valid_start_year)[5:]}T{time_part}"
    valid_end = f"{valid_end_year}-{generate_random_date(valid_end_year)[5:]}T{time_part}"

    return deletion_date, valid_start, valid_end


def process_csv_file(input_file, output_directory, random_years_range, random_valid_start_range, random_valid_end_range):
    """
    Process a CSV file, adding deletion and validation dates.
    
    :param input_file: Path to the input CSV file.
    :type input_file: str
    :param output_directory: Directory where the processed CSV will be stored.
    :type output_directory: str
    :param random_years_range: Range for random deletion years.
    :type random_years_range: tuple[int, int]
    :param random_valid_start_range: Range for random valid start years.
    :type random_valid_start_range: tuple[int, int]
    :param random_valid_end_range: Range for random valid end years.
    :type random_valid_end_range: tuple[int, int]
    """
    output_file = os.path.join(output_directory, os.path.basename(input_file))
    try:
        with open(input_file, mode="r", encoding="utf-8") as infile:
            reader = csv.reader(infile, delimiter="|")
            header = next(reader)

            try:
                creation_date_index = header.index("creationDate")
            except ValueError:
                print(f"Skipping '{input_file}' (No 'creationDate' column found)")
                return

            with open(output_file, mode="w", encoding="utf-8", newline="") as outfile:
                writer = csv.writer(outfile, delimiter="|")
                updated_header = header + ["deletionDate", "validStart", "validEnd"]
                writer.writerow(updated_header)

                for row in reader:
                    if len(row) <= creation_date_index:
                        continue
                    
                    creation_date = row[creation_date_index]
                    match = re.search(pattern, creation_date)

                    if match:
                        random_years = random.randint(*random_years_range)
                        random_valid_start_year = random.randint(*random_valid_start_range)
                        random_valid_end_year = random.randint(*random_valid_end_range)

                        deletion_date, valid_start, valid_end = generate_dates(
                            match, random_years, random_valid_start_year, random_valid_end_year
                        )
                        updated_row = row + [deletion_date, valid_start, valid_end]
                    else:
                        updated_row = row
                    writer.writerow(updated_row)
        print(f"Processed: {input_file} -> {output_file}")
    except Exception as e:
        print(f"Error processing '{input_file}': {e}")


def process_directory(input_directory, output_directory, random_years_range, random_valid_start_range, random_valid_end_range):
    """
    Process all CSV files in the specified input directory and output the results to the specified output directory.

    This function searches for CSV files in the `input_directory`, processes each file using the `process_csv_file`
    function, and saves the results in the `output_directory`. It also accepts ranges for years and valid start/end 
    dates that can be used during processing.

    :param input_directory: The directory containing the CSV files to be processed.
    :type input_directory: str
    :param output_directory: The directory where the processed files will be saved.
    :type output_directory: str
    :param random_years_range: A tuple containing the minimum and maximum values for random year generation.
    :type random_years_range: tuple of int
    :param random_valid_start_range: A tuple containing the minimum and maximum values for random valid start date.
    :type random_valid_start_range: tuple of int
    :param random_valid_end_range: A tuple containing the minimum and maximum values for random valid end date.
    :type random_valid_end_range: tuple of int

    :raises FileNotFoundError: If no CSV files are found in the input directory.
    
    :return: None. The processed files are saved in the output directory.
    :rtype: None

    If no CSV files are found in the `input_directory`, a message will be printed. Otherwise, the function will process
    each CSV file and output the results in the `output_directory`.
    """
    os.makedirs(output_directory, exist_ok=True)
    csv_files = [f for f in os.listdir(input_directory) if f.endswith(".csv")]

    if not csv_files:
        print(f"No CSV files found in directory: {input_directory}")
    else:
        print(f"Processing {len(csv_files)} CSV files in '{input_directory}'...")
        for file in csv_files:
            process_csv_file(
                os.path.join(input_directory, file),
                output_directory,
                random_years_range,
                random_valid_start_range,
                random_valid_end_range
            )


def parse_range(value):
    """
    Parse a string containing a range in the format 'min,max'.
    
    :param value: Range string.
    :type value: str
    :return: A tuple containing the min and max values.
    :rtype: tuple[int, int]
    """
    try:
        min_val, max_val = map(int, value.split(","))
        if min_val > max_val:
            raise argparse.ArgumentTypeError(f"Invalid range: {value}. Min must be <= Max.")
        return (min_val, max_val)
    except ValueError:
        raise argparse.ArgumentTypeError(f"Invalid format: {value}. Expected format: min,max")


def get_range_input(prompt, default):
    """
    Prompt the user for a range input and use default values if the input is empty or invalid.

    :param prompt: The message to display to the user when asking for input.
    :type prompt: str
    :param default: The default values to return if the input is empty or invalid.
    :type default: tuple
    :return: A tuple containing two integers representing the range.
    :rtype: tuple

    If the user input is empty, the default range is returned. If the input is invalid (not in the form 'min,max'),
    the default range is also returned.
    """
    user_input = input(prompt).strip()
    if not user_input:
        return default
    try:
        return tuple(map(int, user_input.split(",")))
    except ValueError:
        print("Invalid input. Using default values:", default)
        return default



def main(input_path="", output_directory="processed_csv", is_directory=False, 
         random_years_range=DEFAULT_YEARS_RANGE, 
         random_valid_start_range=DEFAULT_VALID_START_RANGE, 
         random_valid_end_range=DEFAULT_VALID_END_RANGE):

    os.makedirs(output_directory, exist_ok=True)

    has_directory_arg = any(arg in sys.argv for arg in ['-d', '--directory'])
    has_file_arg = any(arg in sys.argv for arg in ['-f', '--file'])

    if has_directory_arg and has_file_arg:
        print("Error: -d/--directory and -f/--file cannot be used simultaneously.")
        sys.exit(1)
    
    if not input_path:
        print("\n*** CSV Processing Script ***")
        choice = input("1 - Process a directory\n2 - Process a single file\nEnter your choice (1 or 2): ").strip()
        if choice == "1":
            input_path = input("Enter the directory path containing CSV files: ").strip()
            is_directory = True
        elif choice == "2":
            input_path = input("Enter the CSV file path: ").strip()
            is_directory = False
        else:
            print("Invalid choice. Exiting.")
            sys.exit(1)
        
        if not input_path:
            print("Error: No valid path provided. Exiting.")
            sys.exit(1)

        custom_random = input(f"Do you want to set custom random values? \n Default: dyr={DEFAULT_YEARS_RANGE} vsr={DEFAULT_VALID_START_RANGE} ver={DEFAULT_VALID_END_RANGE}\n(y/N):").strip().lower()
    
        if custom_random == "y":
            random_years_range = get_range_input("Enter random deletion years range <min,max>: ", random_years_range)
            random_valid_start_range = get_range_input("Enter random valid start range <min,max>: ", random_valid_start_range)
            random_valid_end_range = get_range_input("Enter random valid end range <min,max>: ", random_valid_end_range)

    if is_directory:
        process_directory(input_path, output_directory, random_years_range, random_valid_start_range, random_valid_end_range)
    else:
        if os.path.exists(input_path):
            process_csv_file(input_path, output_directory, random_years_range, random_valid_start_range, random_valid_end_range)
        else:
            print(f"File not found: {input_path}")
            sys.exit(1)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Process CSV files by adding deletion and validation dates.")
    parser.add_argument("-d", "--directory", help="Path to a directory containing CSV files", type=str)
    parser.add_argument("-f", "--file", help="Path to a single CSV file", type=str)
    parser.add_argument("-o", "--output", help="Output directory for processed CSV files", type=str, default="processed_csv")

    parser.add_argument("--dyr", help=f"Range for random deletion years (default: {DEFAULT_YEARS_RANGE})", type=parse_range, default=DEFAULT_YEARS_RANGE)
    parser.add_argument("--vsr", help=f"Range for random valid start year (default: {DEFAULT_VALID_START_RANGE})", type=parse_range, default=DEFAULT_VALID_START_RANGE)
    parser.add_argument("--ver", help=f"Range for random valid end year (default: {DEFAULT_VALID_END_RANGE})", type=parse_range, default=DEFAULT_VALID_END_RANGE)

    args = parser.parse_args()
    
    main(
        input_path=args.directory or args.file, 
        output_directory=args.output, 
        is_directory=bool(args.directory),
        random_years_range=args.dyr,
        random_valid_start_range=args.vsr,
        random_valid_end_range=args.ver,
    )