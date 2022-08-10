import threading
import time


def mythread():
    time.sleep(1000)


def main():
    threads = 0  # thread counter
    y = 1000000  # a MILLION of 'em!
    for i in range(y):
        try:
            x = threading.Thread(target=mythread, daemon=True)
            threads += 1  # thread counter
            print(threads)
            x.start()  # start each thread
        except RuntimeError:  # too many throws a RuntimeError
            break
    print("{} threads created.\n".format(threads))


if __name__ == "__main__":
    main()

    def __stop_mode_processing(self):
        # If user want to start Emma
        # if Checkers.run_checker(self.__input['text']):
        #    self.__output['text'] = self.run()
        # # Tell user i stopped
        # else:
        #     self.__output['text'] = "I'm stopped, please first run me.\nYou can do it by say \"Run\". "
        # # Process stop mode output
        # self.__output_processing()
        pass
