import argparse
import subprocess

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("parsha")
    parser.add_argument("parsha_url_name_lechaim")

    args = parser.parse_args()

    PARSHA = args.parsha
    PARSHA_URL_NAME = args.parsha_url_name_lechaim

    subprocess_args_list = [
        ["python", "parsers/shabat_shalom_parser.py", PARSHA],
        ["python", "parsers/reformjudaism_parser.py", PARSHA],
        ["python", "parsers/lechaim_parser.py", PARSHA, PARSHA_URL_NAME],
        ["python", "parsers/ramban_commentary_parser.py", PARSHA],
        ["python", "parsers/or_hachaim_commentary_parser.py", PARSHA],
        ["python", "parsers/hebrew_parser.py", PARSHA],
        ["python", "parsers/upload.py", PARSHA],
    ]

    for subprocess_args in subprocess_args_list:
        print("=========\nRunning\n$ " + " ".join(subprocess_args) + "\n")
        subprocess.run(subprocess_args, check=True)
