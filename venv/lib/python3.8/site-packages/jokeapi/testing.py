from main import Jokes
import jokeapi

j = Jokes()
joke = j.get_joke(blacklist=['racist'])
if joke["type"] == "single":
    print(joke["joke"])
else:
    print(joke["setup"])
    print(joke["delivery"])
