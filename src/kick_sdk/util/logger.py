from pystyle import *
from art import *


def info(message: str):
    print(
        f"[{Colorate.Color(color=Colors.light_blue, text='*')}] {Colorate.Color(color=Colors.light_gray, text=message)}")


def error(message: str):
    print(f"[{Colorate.Color(color=Colors.red, text='X')}] {Colorate.Color(color=Colors.light_gray, text=message)}")


def success(message: str):
    print(
        f"[{Colorate.Color(color=Colors.green, text='!')}] {Colorate.Color(color=Colors.light_gray, text=message)}")


def warning(message: str):
    print(
        f"[{Colorate.Color(color=Colors.yellow, text='!')}] {Colorate.Color(color=Colors.light_gray, text=message)}")