# Image Quiz
This is my first wxPython application, a simple image quiz. It shows a picture
and expects the user to type the right answer.
My objective was to learn how to use the wxPython framework by writing this toy
as an exercise.

The program comes with list of the flags of the World Cup 2018 as an example.

## Installation
This program is written in Python3 which is installed by default in most Linux
distributions.
The only extra requirement is the wxPython v4 libraries. You can install them in
Debian/Ubuntu with:

`sudo apt install python3-wxgtk4.0`

Or you can use the included requirements.txt file with pip:

`pip3 install --user -r requirements.txt`

## Configuration
This program is configurable with a JSON file with the following format:

    {
      # An option title field. If not defined, the default is 'Quiz'.
      "title":"My Quiz title",
      # A list of questions to ask to the user. Each question is a list with
      # two elements:
      # * a path to an image file
      # * a string which is the answer expected from the user
      "questions":[
        [
          "animals/lion.png",  # this picture will be shown to the user
          "león"               # this is the answer expected from the user
        ],
        [
          "animals/turtle.jpg",
          "tortuga"
        ]
      ]
    }

When running this program, make sure to pass the path of your configuration file
as a parameter. You can also specify the number of questions you want to ask.
Example:
`python3 ./world-cup-flags.py -c my-config-file.json -n 10`

If the number of questions is 0, all the questions will be asked (the default).

## License
This application is licensed under the GNU General Public License v3.
All images have been obtained from the Wikipedia and they're Public Domain.
