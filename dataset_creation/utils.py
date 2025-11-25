from urllib import parse
import csv
import re
from langdetect import detect_langs

def get_playlist_id(url: str):
    parsed = parse.urlparse(url)
    path = parsed.path.split("/")

    if len(path) < 2:
        raise ValueError(f"Path: {path} \n does not contain a playlist id")

    if path[1] != 'playlist':
        raise ValueError(f"Link: {path} \n does not contain a playlist")

    # path[2] gets the playlist ID
    return path[2]


def unique_lyrics(lyrics: str) -> str:
    """
    Returns the unique and cleaned lyrics, meaning they have
    no new line characters
    """
    if not lyrics:
        return ""
    # normalize newlines
    lyrics = re.sub(r"\r\n?", "\n", lyrics).strip()
    # split into stanzas (separated by one or more blank lines), keep first occurrence only
    stanzas = []

    # "\n\s*\n" splitting where a string is in between two new lines
    for s in re.split(r"\n\s*\n", lyrics):
        stripped = s.strip()
        if stripped:
            stanzas.append(stripped)
    
    seen = set()
    unique = []
    for s in stanzas:
        if s not in seen:
            seen.add(s)
            unique.append(s)

    # removes all new line characters
    unique_lyrics = " ".join(" ".join(unique).split())

    return unique_lyrics


def create_csv(path: str, header: list[str]):
    """
  Creates the csv file that will have songs written into it later. Header
  should be an array of strings to be written as the first row

  Returns the path to be used later when appending to csv
  """

    with open(path, "w", newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(header)

    return path

def is_english(text):
    if not text:
        raise LookupError("No text was provided")
    
    languages = detect_langs(text)
    predict_lang = max(languages, key= lambda x: x.prob).lang

    return predict_lang == "en"
    
    
