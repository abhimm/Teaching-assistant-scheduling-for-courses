__author__ = 'Abhinav'

course_sched = dict()
course_recite = dict()
course_details = dict()
course_skill_req = dict()
ta_skill = dict()
ta_resp = dict()


def load_data(file_path):
    # open the file
    file_ref = open(file_path, "rb")
    data = file_ref.readlines()
    i = 1
    # fill the lists created above
    for row in data:
        temp = row.strip()
        if not temp:
            i += 1
            continue
        temp = temp.split(", ")
        if i == 1:
            course_sched[temp[0]] = temp[1:]
        elif i == 2:
            course_recite[temp[0]] = temp[1:]
        elif i == 3:
            course_details[temp[0]] = temp[1:]
        elif i == 4:
            course_skill_req[temp[0]] = temp[1:]
        elif i == 5:
            ta_resp[temp[0]] = temp[1:]
        elif i == 6:
            ta_skill[temp[0]] = temp[1:]


