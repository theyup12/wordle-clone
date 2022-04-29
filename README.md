# wordle-api
# CPSC 449 - Project 3: Microservice

Team Members: 

Ryan Broguiere: ryanbroguiere123@csu.fullerton.edu <br/>
Andy Cao: dongyicao123@csu.fullerton.edu <br/>
Gavin Gray: graygavin11@csu.fullerton.edu

## Project Description
Created two services for a server-side game like Wordle.
1. The word validation service should expose the following operations:
* Checking if a guess is a valid five-letter word
* Adding and removing possible guesses
2. The answer checking service should expose the following operations:
* Checking a valid guess against the answer for the current day.
* If the guess is incorrect, the response should identify the letters that are:
  * in the word and in the correct spot,
  * in the word but in the wrong spot, and
  * not in the word in any spot
* Changing the answers for future games.


## Project Requirements
This project will run using Tuffix 2020 using Python 3.8.10 and will be implemented using fastapi and sqlite3.
require user install fastapi, ruby-foreman, sqlite3, and httpie 

## Run the Program
1. install pip package installer and other tools:
    sudo apt update
    sudo apt install --yes python3-pip ruby-foreman httpie sqlite3

2. Install FastAPI:
    python3 -m pip install 'fastapi[all]'
    
3. Then run the command:
    ### To initialize the database, type:
        cd into the api folder directory wordle-project3/api
        ./bin/init_s1.sh
        ./bin/init_s2.sh
        python3 shard.py
    ### To start the gunicorn servers, type:
        foreman start
