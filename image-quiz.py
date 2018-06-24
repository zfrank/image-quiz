#!/usr/bin/env python3

# Copyright 2018 Francesc Zacarias
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.


import wx
import sys
import os.path
import random
import json
from argparse import ArgumentParser

TITLE = 'Quiz'


class InvalidConfig(Exception):
    def __str__(self):
        return("Invalid configuration: {}".format(self.args[0]))


def load_config(cfgpath):
    with open(cfgpath) as f:
        j = json.load(f)
    return j


def validate_config(cfg):
    if 'title' not in cfg:
        cfg['title'] = TITLE
    for q in cfg['questions']:
        if len(q) != 2:
            raise InvalidConfig(
                "Wrong number of elements in question {}".format(q),
            )
            return False
        if type(q[0]) != str or type(q[1]) != str:
            raise InvalidConfig(
                "Wrong types in question {}".format(q),
            )
            return False
        if not os.path.exists(q[0]):
            raise InvalidConfig(
                "Cannot find file {}".format(q[0]),
            )
            return False
    return True


def load_images(questions):
    '''
    Return questions list with Image objects instead of file paths
    '''
    img_questions = []
    for imgpath, answer in questions:
        img_questions.append(
            (
                wx.Image(imgpath, wx.BITMAP_TYPE_ANY,).ConvertToBitmap(),
                answer,
            )
        )
    return img_questions


class Game():
    def __init__(self, num_questions, cfg):
        self.title = cfg['title']
        self.results = []
        self.images = load_images(cfg['questions'])
        if num_questions == 0:
            self.questions = random.sample(self.images, len(self.images))
        else:
            self.questions = random.sample(self.images, num_questions)
        self.current = 0
        self.frame = QuestionFrame(
            None,
            game=self,
            results=self.results,
            title=self.title
        )
        self.nextImage()
        self.frame.Show()

    def nextImage(self):
        if self.current < len(self.questions):
            img, answer = self.questions[self.current]
            self.frame.setImage(img, answer)
            self.current += 1
        else:
            self.frame.Close()
            endFrame = ResultsFrame(
                None,
                results=self.results,
                title="Results"
            )
            endFrame.Show()


def get_success(results):
    num_success = len([x for x in results if x[1]])
    return num_success / len(results) * 100


def get_grade(rate):
    grades = [
        (100.0, "Perfect! You made it!"),
        (99.0, "Nearly perfect! Keep trying!"),
        (90.0, "Very good!"),
        (75.0, "Good!"),
        (50.0, "You pass, but there is room for improvement"),
        (0.0, "You fail. You must practice more"),
    ]
    for max_grade, response in grades:
        if rate >= max_grade:
            return response
    raise ValueError('get_grade: Rate must be a positive number')


class ResultsFrame(wx.Frame):
    def __init__(self, *args, **kw):
        self.results = kw.pop('results')
        super().__init__(*args, **kw)
        success_rate = get_success(self.results)
        grade = get_grade(success_rate)
        txt = wx.StaticText(
            self,
            id=wx.ID_ANY,
            label="Result: {:.2f}%\n{}".format(success_rate, grade),
        )
        lst = wx.ListCtrl(self, id=wx.ID_ANY, style=wx.LC_REPORT)
        lst.InsertColumn(0, "#")
        lst.InsertColumn(1, "Question")
        lst.InsertColumn(2, "Correct")
        count = 1
        for answer, correct in self.results:
            lst.Append((count, answer.title(), 'YES' if correct else 'NO'))
            count += 1
        lst.SetColumnWidth(0, wx.LIST_AUTOSIZE_USEHEADER)
        lst.SetColumnWidth(1, wx.LIST_AUTOSIZE_USEHEADER)
        lst.SetColumnWidth(2, wx.LIST_AUTOSIZE_USEHEADER)
        btn = wx.Button(self, label='Done')
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(
            txt,
            proportion=0,
            flag=wx.ALIGN_CENTER | wx.ALL,
            border=10,
        )
        sizer.Add(
            lst,
            proportion=1,
            flag=wx.EXPAND | wx.ALL,
            border=10,
        )
        sizer.Add(
            btn,
            proportion=0,
            flag=wx.ALIGN_CENTER | wx.ALL,
            border=10,
        )
        sizer.SetSizeHints(self)
        self.SetSizer(sizer)
        btn.SetFocus()
        btn.Bind(wx.EVT_BUTTON, self.done)

    def done(self, event):
        self.Close()


class QuestionFrame(wx.Frame):
    def __init__(self, *args, **kw):
        self.game = kw.pop('game')
        self.results = kw.pop('results')
        super().__init__(*args, **kw)
        self.bitmap = wx.StaticBitmap(self, pos=(0, 0))
        self.txt = wx.TextCtrl(
            self, value="", style=wx.TE_PROCESS_ENTER | wx.TE_CENTRE)
        self.sizer = wx.BoxSizer(wx.VERTICAL)
        self.sizer.Add(
            self.bitmap,
            proportion=1,
            flag=wx.EXPAND | wx.ALL,
            border=5)
        self.sizer.Add(
            self.txt,
            proportion=0,
            flag=wx.EXPAND | wx.ALL,
            border=10)
        self.sizer.SetSizeHints(self)
        self.SetSizer(self.sizer)
        self.txt.Bind(wx.EVT_TEXT_ENTER, self.validateAnswer)

    def validateAnswer(self, event):
        # user_answer = event.GetEventObject().GetLineText(0).lower()
        user_answer = self.txt.GetLineText(0).lower()
        if user_answer == self.answer:
            wx.MessageBox(
                message="That's correct!",
                caption=self.game.title,
                style=wx.ICON_INFORMATION,
            )
            self.results.append((self.answer, True))
        else:
            wx.MessageBox(
                message="You're wrong!\nThe correct answer was:\n{}".format(
                    self.answer.title()
                ),
                caption=self.game.title,
                style=wx.ICON_EXCLAMATION,
            )
            self.results.append((self.answer, False))
        self.game.nextImage()

    def setImage(self, image, answer):
        self.bitmap.SetBitmap(image)
        self.bitmap.SetSize(image.GetSize())
        self.sizer.Fit(self)
        self.answer = answer
        self.txt.SetValue("")


if __name__ == '__main__':
    argp = ArgumentParser(
        description='Image quiz. Type the answer for each image.'
    )
    argp.add_argument(
        '-n',
        '--num-questions',
        type=int,
        default=0,
        help='How many questions to ask (default: 0, all questions)'
    )
    argp.add_argument(
        '-c',
        '--config',
        default='config.json',
        help='Path to config file in JSON format (default: config.json)'
    )
    args = argp.parse_args()

    cfg = load_config(args.config)
    try:
        validate_config(cfg)
    except InvalidConfig as e:
        print(e)
        sys.exit(1)
    if args.num_questions > len(cfg['questions']):
        print(
            "Number of questions option is bigger than number of questions "
            "available: {}".format(len(cfg['questions'])),
            file=sys.stderr
        )
        sys.exit(1)
    if args.num_questions < 0:
        print(
            "Number of questions must be a positive number",
            file=sys.stderr
        )
        sys.exit(1)
    app = wx.App()
    g = Game(args.num_questions, cfg)
    app.MainLoop()
