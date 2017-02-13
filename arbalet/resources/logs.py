from termcolor import colored

def info(message, author=None):
    full_message = message if author is None else "[Arbalet {}] {}".format(author, message)
    print(colored(message, 'blue'))