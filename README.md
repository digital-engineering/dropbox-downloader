# Dropbox Downloader

## Summary

#### Python CLI tool with two functions

1) Download all files and folders recursively for a given path, or entire 
   Dropbox if no path is given. Files are placed in the `dl_dir` folder
   specified in the `dbx-dl.ini` file. May also specify `to_dl` csv list to 
   download specific root files / folders by name.
   
2) Columnar list of all files / folders in a given `path`.

## Requirements

- python3

## Installing in virtual environment

    #!/bin/bash
    LOCAL_PATH="/path/to/clone/repo" # change this to your preferred location
    
    git clone git@github.com:digitalengineering/dropbox-downloader.git "$LOCAL_PATH"
    
    cd "$LOCAL_PATH" 
    python3 -m venv env
    . env/bin/activate
    pip install -r requirements.txt
    
    echo "
    [main]
    api_key =  MyDropboxApiKey
    dl_dir = $LOCAL_PATH/Download
    to_dl = Folder 1,Folder B,Another Folder Name,onemore.txt
    " >> "$LOCAL_PATH/dbx-dl.py"

## Obtaining Dropbox Api Key

@see here: https://www.dropbox.com/developers/apps 

## Examples
    
    # Show help
    ./dbx-dl.py --help
    
    # Download entire dropbox to folder specificied in `dl_dir` 
    ./dbx-dl.py download-recursive
    
    # List contents of root folder 
    ./dbx-dl.py ls ""

    # List contents of other folder 
    ./dbx-dl.py ls "/path/to/folder"
