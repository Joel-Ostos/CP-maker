#!python3
import sys   
import os 
import requests
import xml.etree.ElementTree as ET
from bs4 import BeautifulSoup
from datetime import date

def make_tests(problem_name, contest_id, url):
    response = requests.get(url)
    html_content = response.content
    soup = BeautifulSoup(html_content, 'html.parser')

    sample_tests_div = soup.find('div', class_='sample-tests')
    sample_tests = sample_tests_div.find_all('div', class_='sample-test')

    for sample_test in sample_tests:
        input_div = sample_test.find('div', class_='input')
        output_div = sample_test.find('div', class_='output')

        input_lines = input_div.find('pre').find_all('div')
        input_text = '\n'.join(line.get_text(strip=True) for line in input_lines)

        output_text = output_div.find('pre').get_text(strip=True)

        input_name = contest_id + "/" + problem_name + "_input.txt"
        output_name = contest_id + "/" + problem_name + "_output.txt"

        with open(input_name , "a") as file:
            file.write(input_text)
        with open(output_name, "a") as file:
            file.write(output_text)

def init_contest(contest_id):
    signature_route = "signature.txt"
    template_route = "template.cpp"
    
    try:
        with open(signature_route, 'r') as file:
            header_pre = file.readlines()
    except Exception as e:
        print("An unexpected error happened {e}, your name is going to be requested to be able to make the signature for the templates")
        print("Write your name")
        name = str(input())
        header_pre = "/*\nAuthor: " + name + "\nDate:  \nProblem:  */"
        with open("signature.txt", "a") as file:
            file.write(header_pre)
    try: 
        with open(template_route, 'r') as file:
            template_pre = file.readlines()
    except Exception as e:
        print("An unexpected error happened {e}\nThe directoy must have a template to continue\nCannot continue without the template")

    os.mkdir(contest_id)
    try: 
        with open("credentials.xml", 'r') as file:
            credentials = ''.join(file.readlines())
    except Exception as e:
        print("{e} The xml file has not found, if you want to upload your problems from local don't forget to make the xml file with your credentials and run again the file")

    with open(contest_id + "/credentials.xml", "a") as an:
        an.write(str(credentials))

    today = str(date.today())
    for i in range(0, 5):
        n_problem = chr(ord('A')+i)
        problem = "https://codeforces.com/contest/" + contest_id + "/problem/" + n_problem
        cont = 1
        header = header_pre[0] + header_pre[1]
        for sub in header_pre: 
            idx = sub.find(":") 
            if idx != -1 and idx+2 < len(sub) and sub[idx+2] == ' ':
                if cont == 1:
                    header += sub[:idx+2] + today + sub[idx+2:]
                if cont == 2:
                    header += sub[:idx+2] + problem + sub[idx+2:]
                cont+=1
    
        header += header_pre[len(header_pre)-1] + '\n'
    
        template = ""
        for i in template_pre:
            template += i
    
        final_file =  header + template
    
        route_file = contest_id + "/" + n_problem + ".cpp"
        with open(route_file, "a") as file:
            file.write(final_file)

        make_tests(n_problem, str(contest_id), problem)

#def check_tests():


def extract_user(filename):
    tree = ET.parse(filename)
    root = tree.getroot()

    user = root.find('user')
    handle = user.find('handle').text
    passwd = user.find('passwd').text

    return (handle, passwd)

def upload_file(contest_id, problem_id):
    user = extract_user("credentials.xml")
    handle = user[0]
    passwd = user[1]
    
    login_url = 'https://codeforces.com/enter'
    profile_url = 'https://codeforces.com/profile/' + handle
    submit_url = 'https://codeforces.com/contest/' + contest_id +'/submit' 

    session = requests.Session()

    login_page = session.get(login_url)
    login_soup = BeautifulSoup(login_page.content, 'html.parser')
    csrf_token = login_soup.find('input', {'name': 'csrf_token'})['value']

    login_data = {
        'csrf_token': csrf_token,
        'action': 'enter',
        'ftaa': '',
        'bfaa': '',
        'handleOrEmail': handle, 
        'password': passwd,   
        'remember': 'on'
    }

    response = session.post(login_url, data=login_data)

    if response.status_code != 200:
        print('Error on session login')
    else:
        profile_page = session.get(profile_url)
        if handle in profile_page.text:
            print('Succesfull login')
        else:
            print('The credentials are wrong')

    submit_zone = session.get(submit_url)
    submit_soup = BeautifulSoup(submit_zone.content, 'html.parser')
    csrf_token = submit_soup.find('input', {'name': 'csrf_token'})['value']
    ftaa = submit_soup.find('input', {'name': 'ftaa'})['value']
    bfaa = submit_soup.find('input', {'name': 'bfaa'})['value']

    solution_name = str(problem_id) + ".cpp"
    with open(solution_name, "r") as file:
        source_code = file.readlines()

    language_id = '54' 

    submit_data = {
    'csrf_token': csrf_token,
    'ftaa': ftaa,
    'bfaa': bfaa,
    'action': 'submitSolutionFormSubmitted',
    'submittedProblemIndex': problem_id,
    'programTypeId': language_id,
    'source': source_code
    }

    response = session.post(submit_url, data=submit_data)

    if response.status_code == 200:
        print('Code sent successfully')
    else:
        print('Error sending the code')

def main():
    today = str(date.today())
    argc = len(sys.argv)
    if argc < 2:
        print("Incorrect usage, write cptool --help to get info about how to use the program")
        exit()
    petition = sys.argv[1]
    match petition: 
        case "-c":
            if argc != 3:
                print("Incorrect usage, write cptool --help to get info about how to use the program")
                exit()
            init_contest(str(sys.argv[2]))
        case "--create-files":
            if argc != 3:
                print("Incorrect usage, write cptool --help to get info about how to use the program")
                exit()
            init_contest(sys.argv[2])
        case "-u":
            if argc != 4:
                print("Incorrect usage, write cptool --help to get info about how to use the program")
                exit()
            upload_file(sys.argv[2], sys.argv[3])
        case "--upload-file":
            if argc != 4:
                print("Incorrect usage, write cptool --help to get info about how to use the program")
                exit()
            upload_file(sys.argv[2], sys.argv[3])
        ##case "-v":

        ##case "--validate-tests":



if __name__ == "__main__":
    main()
