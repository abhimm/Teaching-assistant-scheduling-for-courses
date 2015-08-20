__author__ = 'Abhinav'
import load_data
import copy



"""
This method is the driver method for the implementation which reads the data using load_data utility
provided I load_data.py module and initiates backtracking search by calling
backtracking_search(ta_capacity, course_capacity_req) method.
"""

def main():
    load_data.load_data("D:\STONY_BROOK\SPRING_2015\AI\HW3\dataset_AI_CSP_Modified_test")

    # build available TA skills
    ta_skill_set = set()
    for ta, skill in load_data.ta_skill.items():
        ta_skill_set = ta_skill_set | set(skill)

    # build TA capacity
    ta_capacity = list()
    for ta, val in load_data.ta_resp.items():
        ta_capacity.append([ta, 1.0])


    # build course capacity requirement
    course_capacity_req = list()
    course_without_ta = list()
    course_without_skilled_ta = list()

    for crs, val in load_data.course_details.items():
        capacity = 0.0

        if int(val[0]) >= 25 and int(val[0]) < 40:
            capacity = 0.5
        elif int(val[0]) >= 40 and int(val[0]) < 60:
            capacity = 1.5
        elif int(val[0]) >= 60:
            capacity = 2.0

        if capacity > 0:
            skill_found = False
            for skill in load_data.course_skill_req[crs]:
                if skill in ta_skill_set:
                    skill_found = True
                    break
            if skill_found:
                course_capacity_req.append([crs, capacity])
            else:
                course_without_skilled_ta.append([crs, capacity])
        else:
            course_without_ta.append(crs)

    solution = dict()
    ta_allocation = dict()
    solution = backtracking_search(ta_capacity, course_capacity_req)

    print "TA ASSIGNMENT FOR COURSES:"

    for crs, assinment in solution.items():
        print crs, assinment

        for value in assinment:
            if value[0] == "needed":
                continue
            if ta_allocation.has_key(value[0]):
                ta_allocation[value[0]].append((crs, value[1]))
            else:
                ta_allocation[value[0]] = [(crs, value[1])]

    for crs in course_without_skilled_ta:
        print crs[0], " [('needed', %.1f)]" % crs[1]

    for crs in course_without_ta:
        print crs, " [('needed', 0.0)]"

    print "****************************************************"
    print "COURSE ASSGINED TO TAs:"
    for ta, crs in ta_allocation.items():
        print ta, crs

"""
This method creates a solution dictionary and triggers recursive backtracking call.
"""

def backtracking_search(ta_capacity, course_capacity_req):
    solution = dict()
    result = recursive_backtracking_search(ta_capacity, course_capacity_req, solution)
    return solution


"""
This method finds the best solution from a solution list generate by recursive backtracking method based on maximum
assignment of TAs to courses
"""
def get_optimal_solution(solution_list):
    optimal_assignment = dict()
    optimal_val = 0.0
    for sol in solution_list:
        assignment_list = sol.values()
        local_val = 0.0
        for crs_assgnment in assignment_list:
            for values in crs_assgnment:
                local_val += values[1]

        if local_val > optimal_val:
            optimal_val = local_val
            optimal_assignment = sol

    return optimal_assignment

"""
This method is the core method of implementation. In this method an unassigned course is picked and TA from the TA list
is assigned to this course. Before assigning the TA to the course check constraints methods are called to assess the
viability of TA assignment. Once a TA is assigned a recursive call is made again to assign TAs to remaining courses.
If the results of recursive call is failure which means if some course remained unassigned then different TA is assigned
 and recursive call is made again. In this way a solution list is generated which is later used to find an optimal
 solution based on maximum TA assignment. If recursive call result is not failure then the current assignment and
 result of remaining course assignment is combined and returned as an optimal solution.
Apart from assignment, to perform forward checking , domain values for all remaining courses are reduced based on the
current assignment.
"""
def recursive_backtracking_search(ta_capacity, course_capacity_req, solution):
    if len(course_capacity_req) == 0:
        return True
    unassigned_course = course_capacity_req[0]
    i = 0
    solution_list = list()
    for ta in ta_capacity:

        num_skill_req = len(load_data.course_skill_req[unassigned_course[0]])
        if check_constraint(ta, unassigned_course, num_skill_req, solution):
            # create copy
            solution_copy = copy.deepcopy(solution)
            course_cap_req_copy = copy.deepcopy(course_capacity_req)
            ta_capacity_copy = copy.deepcopy(ta_capacity)
            filled_capacity = 0.0

            if unassigned_course[1] > ta[1]:
                filled_capacity = ta[1]
                del ta_capacity_copy[ta_capacity_copy.index(ta)]
                course_cap_req_copy[course_cap_req_copy.index(unassigned_course)][1] -= filled_capacity

            elif unassigned_course[1] < ta[1]:
                filled_capacity = unassigned_course[1]
                del course_cap_req_copy[course_cap_req_copy.index(unassigned_course)]
                ta_capacity_copy[ta_capacity_copy.index(ta)][1] -= filled_capacity
            else:
                del ta_capacity_copy[ta_capacity_copy.index(ta)]
                del course_cap_req_copy[course_cap_req_copy.index(unassigned_course)]
                filled_capacity = ta[1]
            i += 1
            if solution_copy.has_key(unassigned_course[0]):
                solution_copy[unassigned_course[0]].append((ta[0], filled_capacity))
            else:
                solution_copy[unassigned_course[0]] = [(ta[0], filled_capacity)]
            result = recursive_backtracking_search(ta_capacity_copy, course_cap_req_copy, solution_copy)
            if result == False:
                solution_list.append(solution_copy)
            else:
                solution.clear()
                solution.update(solution_copy)
                return True
    # if solution list is empty, it means none of the values were assigned to variable

    if len(solution_list) == 0:
        if len(ta_capacity) == 0:
            for course_left in course_capacity_req:
                if solution.has_key(course_left[0]):
                    solution[course_left[0]].append(("needed", course_left[1]))
                else:
                    solution[course_left[0]] = [("needed", course_left[1])]
            return True
        else:
            # create copy
            solution_copy = copy.deepcopy(solution)
            course_cap_req_copy = copy.deepcopy(course_capacity_req)
            ta_capacity_copy = copy.deepcopy(ta_capacity)
            del course_cap_req_copy[course_cap_req_copy.index(unassigned_course)]
            if solution_copy.has_key(unassigned_course[0]):
                solution_copy[unassigned_course[0]].append(("needed", unassigned_course[1]))
            else:
                solution_copy[unassigned_course[0]] = [("needed", unassigned_course[1])]
            result = recursive_backtracking_search(ta_capacity_copy, course_cap_req_copy, solution_copy)
            solution.clear()
            solution.update(solution_copy)
            return False
    else:
        solution.clear()
        solution.update(get_optimal_solution(solution_list))
        return False

"""
This method is central point of constraint checking which triggers different constraint check methods, combines
the results and return the result to recursive backtracking method for further processing.
"""
def check_constraint(ta, course, num_skill_req, solution):
    time_match = check_timing_constraint(ta, course)
    skill_match = False

    while (num_skill_req > 0):
        skill_match = check_skill_constraint(ta, course, num_skill_req)
        if skill_match:
            break
        num_skill_req -= 1

    course_timing_clash = check_course_timing_clash_constraint(ta, course, solution)
    if time_match and skill_match and not course_timing_clash:
        return True
    else:
        return False


def convert_24_format(time):
    time_part = time.split()
    time_24 = 0.0
    if time_part[1] == "PM":
        time_24 += 12
    hour_part = time_part[0].split(':')
    time_24 += float(hour_part[0]) % 12 + float(hour_part[1]) / 60.0
    return time_24

"""
This method checks if TA responsibility time is conflicting with course recitation time and course lecture time if
attendance is required.
"""
def check_timing_constraint(ta, course):
    # check recitation time first
    if load_data.course_recite.has_key(course[0]):
        if load_data.ta_resp[ta[0]][0] == load_data.course_recite[course[0]][0] \
                and convert_24_format(load_data.course_recite[course[0]][1]) <= convert_24_format(
                        load_data.ta_resp[ta[0]][1]) <= (convert_24_format(load_data.course_recite[course[0]][1]) \
                                                                                     + 1.5):
            return False
    # course lecture timing
    if load_data.course_details[course[0]][1] == 'yes':
        if load_data.ta_resp[ta[0]][0] == load_data.course_sched[course[0]][0] \
                and convert_24_format(load_data.course_sched[course[0]][1]) <= convert_24_format(
                        load_data.ta_resp[ta[0]][1]) <= (convert_24_format(load_data.course_sched[course[0]][1]) \
                                                                                     + 1.34):
            return False

        if load_data.ta_resp[ta[0]][0] == load_data.course_sched[course[0]][2] \
                and convert_24_format(load_data.course_sched[course[0]][3]) <= convert_24_format(
                        load_data.ta_resp[ta[0]][1]) <= (convert_24_format(load_data.course_sched[course[0]][3]) \
                                                                                     + 1.34):
            return False
    return True


"""
This method checks if TA is a single skill match between TA and course.
"""
def check_skill_constraint(ta, course, num_skill_req):
    num_skill_match = 0
    course_skills = load_data.course_skill_req[course[0]]
    for skill in course_skills:
        if load_data.ta_skill[ta[0]].count(skill) > 0:
            num_skill_match += 1

    if num_skill_match < num_skill_req:
        return False
    else:
        return True

"""
A TA can be assigned to two course. It could lead to a use case where both course have times clashing between either
lecture or recitation or lecture and recitation. This method detects such clashes.
"""
def check_course_timing_clash_constraint(ta, course, solution):
    conflicting_course = ""
    for course_id, ta_assignment in solution.items():
        for assignment in ta_assignment:
            if assignment[0] == ta[0]:
                conflicting_course = course_id
                break
    if conflicting_course == "":
        return False
    result = False
    # if recitation is present for both course and they lie on same day
    if load_data.course_recite.has_key(course[0]) and load_data.course_recite.has_key(conflicting_course):
        # check recitation timing clash
        if check_time_period_clash(load_data.course_recite[course[0]][0],
                                   convert_24_format(load_data.course_recite[course[0]][1]), 1.5,
                                   load_data.course_recite[conflicting_course][0],
                                   convert_24_format(load_data.course_recite[conflicting_course][1]), 1.5):
            return True

    # if recitation of one course clashes with a lecture of another course where TA attendance is required
    if load_data.course_recite.has_key(course[0]) and load_data.course_details[conflicting_course][1]:
        #check timing clash
        if check_time_period_clash(load_data.course_recite[course[0]][0],
                                   convert_24_format(load_data.course_recite[course[0]][1]), 1.5,
                                   load_data.course_sched[conflicting_course][0],
                                   convert_24_format(load_data.course_sched[conflicting_course][1]), 1.34):
            return True

        if check_time_period_clash(load_data.course_recite[course[0]][0],
                                   convert_24_format(load_data.course_recite[course[0]][1]), 1.5,
                                   load_data.course_sched[conflicting_course][2],
                                   convert_24_format(load_data.course_sched[conflicting_course][3]), 1.34):
            return True

    #course lectures confilct
    if load_data.course_details[conflicting_course][1] and load_data.course_details[course[0]][1]:
        if check_time_period_clash(load_data.course_sched[conflicting_course][0],
                                   convert_24_format(load_data.course_sched[conflicting_course][1]), 1.34,
                                   load_data.course_sched[course[0]][0],
                                   convert_24_format(load_data.course_sched[conflicting_course][1]), 1.34):
            return True

        if check_time_period_clash(load_data.course_sched[conflicting_course][2],
                                   convert_24_format(load_data.course_sched[conflicting_course][3]), 1.34,
                                   load_data.course_sched[course[0]][0],
                                   convert_24_format(load_data.course_sched[conflicting_course][1]), 1.34):
            return True

        if check_time_period_clash(load_data.course_sched[conflicting_course][0],
                                   convert_24_format(load_data.course_sched[conflicting_course][1]), 1.34,
                                   load_data.course_sched[course[0]][2],
                                   convert_24_format(load_data.course_sched[conflicting_course][3]), 1.34):
            return True

        if check_time_period_clash(load_data.course_sched[conflicting_course][2],
                                   convert_24_format(load_data.course_sched[conflicting_course][3]), 1.34,
                                   load_data.course_sched[course[0]][2],
                                   convert_24_format(load_data.course_sched[conflicting_course][3]), 1.34):
            return True


def check_time_period_clash(day_1, start_time_1, len_1, day_2, start_time_2, len_2):
    if day_1 == day_2:
        if ((start_time_2 <= start_time_1 <= start_time_2 + len_2) or (start_time_2 <= start_time_1 +
            len_1 <= start_time_2 + len_2) or (
                        start_time_1 < start_time_2 and start_time_1 + len_1 > start_time_2 + len_2)):
            return True
        else:
            return False
    else:
        return False


if __name__ == '__main__':
    main()