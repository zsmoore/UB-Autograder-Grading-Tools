from bs4 import BeautifulSoup
import sys
from selenium import webdriver
import json

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

def to_assignment(driver, assignment, section):

    driver.find_element_by_partial_link_text(assignment).click()
    for ele in driver.find_elements_by_class_name('collapsible-header'):
        ele.click()

    driver.find_element_by_partial_link_text('Grade all').click()
    driver.find_element_by_xpath('//label[input]').send_keys(section)

    return driver


def get_quizzes(driver):

    html = driver.page_source
    soup = BeautifulSoup(html, 'html.parser')

    to_traverse = []
    for ele in soup.find_all('a', href=True):
        if ele['href'].endswith('/view'):
            to_traverse.append(ele['href'])

    print('You have {0} Submissions to grade'.format(len(to_traverse)))
    return (driver, to_traverse)

def extract_submissions(driver, links):

    base = 'https://autograder.cse.buffalo.edu'
    soup = None
    submissions = []
    for link in links:
        driver.get(base + link)
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        name = soup.find('h2').contents[-1].strip().strip('(').strip(')')

        for ele in soup.find_all('code'):
            submissions.append((name, ele.text))
            break

    driver.close()
    return submissions

def to_file(assignment, submissions, section):

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
    driver = to_assignment(driver, assignment, section)
    res_tup = get_quizzes(driver)

    submissions = extract_submissions(res_tup[0], res_tup[1])

    to_file(assignment, submissions, section)

    print('Submissions are in file {0}-{1}.txt'.format(assignment,section))
    exit()


if __name__ == '__main__':
    main()
