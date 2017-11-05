from bs4 import BeautifulSoup
from selenium import webdriver
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import smtplib


class MovieList:
    def __init__(self):
        self.movie_list = []

    def add_movie(self, movie):
        movie_obj = Movie()
        movie_obj.score = movie[0]
        movie_obj.title = movie[1]
        self.movie_list.append(movie_obj)

    def get_movie_links(self, table):
        links = []
        for movie in self.movie_list:
            link = table[0].find_all('a', href=True, text=movie.title)
            links.append(link)

        return links

    def get_movie_titles(self):
        titles = []
        for movie in self.movie_list:
            titles.append(movie.title)

        return titles

    def get_movie_info(self, driver):
        try:
            for movie in self.movie_list:
                driver.find_element_by_link_text(movie.title).click()
                movie.synopsis = driver.find_element_by_xpath("""//*[@id="movieSynopsis"]""").text
                movie.rating = driver.find_element_by_xpath(
                    """//*[@id="mainColumn"]/section[4]/div/div/ul/li[1]/div[2]""").text
                movie.genre = driver.find_element_by_xpath(
                    """//*[@id="mainColumn"]/section[4]/div/div/ul/li[2]/div[2]""").text
                movie.directed_by = driver.find_element_by_xpath(
                    """//*[@id="mainColumn"]/section[4]/div/div/ul/li[3]/div[2]/a""").text
                movie.written_by = driver.find_element_by_xpath(
                    """//*[@id="mainColumn"]/section[4]/div/div/ul/li[4]/div[2]/a""").text
                movie.release_date = driver.find_element_by_xpath(
                    """//*[@id="mainColumn"]/section[4]/div/div/ul/li[5]/div[2]/time""").text
                movie.runtime = driver.find_element_by_xpath(
                    """//*[@id="mainColumn"]/section[4]/div/div/ul/li[6]/div[2]/time""").text
                movie.studio = driver.find_element_by_xpath(
                    """//*[@id="mainColumn"]/section[4]/div/div/ul/li[7]/div[2]/a""").text
                driver.back()
        except:
            driver.save_screenshot('screenshot.png')


    def print_movie_info(self):
        for movie in self.movie_list:
            print(movie.title, movie.score, movie.release_date, movie.rating, movie.genre, movie.directed_by,
                  movie.written_by, movie.release_date, movie.runtime, movie.studio)

    def send_mail(self):
        toaddr = 'brian2najera@gmail.com'

        # opens text file with email username and password in order to login and send mail from it.
        with open(r'C:\Users\Brian\PycharmProjects\movie_scraper\info.txt') as f:
            temp1 = [x.rstrip('\n') for x in f.readline()]
            temp2 = [x.rstrip('\n') for x in f.readline()]
            login = ''.join(temp1)
            password = ''.join(temp2)

        msg = MIMEMultipart()
        msg['Subject'] = "New Movie Results!"
        msg['From'] = login
        msg['To'] = toaddr
        html_slices = []

        f = open(r'C:\Users\Brian\PycharmProjects\movie_scraper\header.txt')
        html_slices.append(f.read())

        # html_slices.append("<h2>{} results for {} </h2>".format(len(items_list), search))

        for movie in self.movie_list:  # generating listing html for all the results
            html_slices.append('<div data-role="collapsible">')
            html_slices.append(
                '<h4>Rotton Tomatos Score: {}  &nbsp;&nbsp;&nbsp;&nbsp; {}  &nbsp;&nbsp;&nbsp;&nbsp; In Theaters: {}</h4>'.format(movie.score, movie.title, movie.release_date))
            html_slices.append('<ul data-role="listview">')
            html_slices.append("<li>")
            html_slices.append("{}".format(movie.synopsis))
            html_slices.append("</li>")
            html_slices.append('<br>')
            html_slices.append("Genre:      {}".format(movie.genre))
            html_slices.append('<br>')
            html_slices.append("Directed By:    {}".format(movie.directed_by))
            html_slices.append('<br>')
            html_slices.append("Written By:     {}".format(movie.written_by))
            html_slices.append('<br>')
            html_slices.append("Runtime:    {}".format(movie.runtime))
            html_slices.append('<br>')
            html_slices.append("Studio:     {}".format(movie.studio))
            html_slices.append('</ul>')
            html_slices.append('</div>')
            html_slices.append('<br>')

        html_slices.append("""
         </div>
    </div> 
    </body>
    </html>
        """)
        html = '\n'.join(html_slices)
        msg.attach(MIMEText(html, 'html'))
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(login, password)
        text = msg.as_string()
        server.sendmail(login, toaddr, text)
        server.quit()


class Movie:
    def __init__(self):
        self.title = ''
        self.score = ''
        self.release_date = ''
        self.rating = ''
        self.genre = ''
        self.directed_by = ''
        self.written_by = ''
        self.runtime = ''
        self.studio = ''
        self.synopsis = ''


def main():
    movie_list = MovieList()
    phantomjs = r"C:\Users\Brian\Desktop\phantomjs-2.1.1-windows\bin\phantomjs.exe"
    driver = webdriver.PhantomJS(phantomjs)
    driver.get("https://www.rottentomatoes.com/")
    page_source = driver.page_source
    soup = BeautifulSoup(page_source, "lxml")

    table = soup.select("#Opening")
    rows = table[0].find_all('tr')
    movies = []
    # parse all movies from the table
    for row in rows:
        cols = row.find_all('td')
        cols = [element.text.strip() for element in cols]
        movies.append([element for element in cols if element])

    # filter movies based on score above 85%
    for movie in movies:
        try:
            if int(movie[0].strip('%')) >= 85:
                movie_list.add_movie(movie)
        except ValueError:
            pass

    movie_list.get_movie_info(driver)
    movie_list.send_mail()
    driver.close()


if __name__ == '__main__':
    main()
