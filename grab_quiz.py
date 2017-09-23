from bs4 import BeautifulSoup
import sys
from selenium import webdriver
import time

def login(user, password):

    base = 'https://autograder.cse.buffalo.edu/auth/users/sign_in'

    driver = webdriver.Firefox()
    driver.implicitly_wait(30)
    driver.get(base)
    driver.find_element_by_class_name('button_to').click()

    driver.find_element_by_id('login').send_keys(user)
    driver.find_element_by_id('password').send_keys(password)
    driver.find_element_by_id('login-button').click()

    return driver

def to_assignment(driver, assignment):

    driver.find_element_by_partial_link_text(assignment).click()
    for ele in driver.find_elements_by_class_name('collapsible-header'):
        ele.click()

    driver.find_element_by_partial_link_text('Grade all submissions').click()
    time.sleep(7)

    return driver


def get_quizzes(driver, section):
    
    last_height = driver.execute_script('return document.body.scrollHeight')
    while True:
        driver.execute_script('window.scrollTo(0, document.body.scrollHeight);')
        time.sleep(1)
        new_height =  driver.execute_script('return document.body.scrollHeight')
        if new_height == last_height:
            break
        last_height = new_height

    html = driver.page_source
    soup = BeautifulSoup(html, 'html.parser')
    

    correct_rows = []
    table = soup.findChildren('table')[0]
    rows = table.findChildren('tr')
    for row in rows:
        cells = row.findChildren('td', {'class': 'sec'})
        for cell in cells:
            if cell.text == section:
                correct_rows.append(row)

    to_traverse = []
    for row in correct_rows:
        data = row.findChildren('td', {'class' : 'id sorting_1'})[0]
        name = ''
        link = ''
        for ele in data.find_all('a', href=False):
            name = ele.text
        for ele in data.find_all('a', href=True):
            link = ele['href']
        to_traverse.append((name,link))
       
    print('You have {0} Submissions to grade'.format(len(to_traverse)))
    return (driver, to_traverse)

def extract_submissions(driver, tups):

    base = 'https://autograder.cse.buffalo.edu'
    soup = None
    submissions = []
    for tup in tups:
        driver.get(base + tup[1])
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        
        for ele in soup.find_all('code'):
            submissions.append((tup[0], ele.text))
            break
    
    driver.close()
    return submissions

def to_file(assignment, section, submissions):

    fout = open(assignment + '-' + section + '.txt', 'w')

    for sub in submissions:
        fout.write(sub[0] + '\n')

        data = eval(sub[1])
        fout.write('Question 1:\t' + data['question-1'] + '\n')
        fout.write('Question 2:\t' + data['question-2'] + '\n')
        fout.write('Question 3:\t' + data['question-3'] + '\n')
        fout.write('Question 4"\t' + data['question-4'] + '\n')
        fout.write('\n\n\n')

    fout.close()

def main():

    if len(sys.argv) < 5:
        print('Incorrect usage arg1: username, arg2: pass, arg3: what you want to grade, arg4: section to grade')
        exit()

    user = sys.argv[1]
    password = sys.argv[2]
    assignment = sys.argv[3]
    section = sys.argv[4]

    driver = login(user, password)
    driver = to_assignment(driver, assignment)
    res_tup = get_quizzes(driver, section)

    submissions = extract_submissions(res_tup[0], res_tup[1])

    to_file(assignment, section, submissions)

    print('Submissions are in file {0}-{1}.txt'.format(assignment, section))
    exit()


if __name__ == '__main__':
    main()

