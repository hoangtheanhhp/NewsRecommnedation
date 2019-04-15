from crawler import crawler
import datetime, time
import utils
import os
from io import open



class master:
    def __init__(self):
        self.crawler = crawler()
        self.first_run = True
        self.date = datetime.datetime.now().date()


    def check_date(self):
        present = datetime.datetime.now().date()
        if self.date < present:
            self.date = present
            return True
        return False


    def save_stories_to_file(self):
        print('save stories to file...')
        utils.mkdir('result')
        date = self.date.strftime('%Y-%m-%d')
        output_dir = os.path.join('result', date)
        utils.mkdir(output_dir)
        for story in self.crawler.new_stories:
            story_name = utils.id_generator()
            with open(os.path.join(output_dir, story_name), 'w', encoding='utf-8') as f:
                f.write(story)


    def run(self):
        while True:
            # remove docs of yesterday
            if self.check_date() or self.first_run:
                self.crawler.remove_old_documents()
                self.first_run = False

            print('run crawler...')
            self.crawler.run()
            self.save_stories_to_file()

            time.sleep(3600)




if __name__ == '__main__':
    m = master()
    m.run()