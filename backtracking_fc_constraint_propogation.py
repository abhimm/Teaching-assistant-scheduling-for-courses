import load_data
import copy


course_domain_dict_main = dict()
course_without_ta = list()
course_without_skilled_ta = list()

"""
This method is central point of constraint checking which triggers different constraint check methods, combines
the results and return the result to recursive backtracking method for further processing.
"""
def check_constraint(ta, course, num_skill_req):
    time_match = check_timing_constraint(ta, course)
    skill_match = False
    i = 0
    while (num_skill_req > 0):
        skill_match = check_skill_constraint(ta, course, num_skill_req)
        if skill_match or i == 2:
            break
        num_skill_req -= 1
        i += 1
    if time_match and skill_match:
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
    if num_skill_match==0:
        return False
    else:
        return True

"""
This method is used to create the domain for each course, by checking both the time and skill constraints. This method
creates a dictionary, where, each course is the key and the value consists of the list of possible TA assignments for
 the course.
"""
def create_list_of_dictionaries():
    global course_domain_dict_main, course_without_ta
    ta_capacity = list()
    for ta, val in load_data.ta_resp.items():
        ta_capacity.append([ta, 1.0])
    course_capacity_req = list()
    all_course_list = list()
    for crs, val in load_data.course_details.items():
        capacity = 0.0
        if int(val[0]) >= 25 and int(val[0]) < 40:
            capacity = 0.5
        elif int(val[0]) >= 40 and int(val[0]) < 60:
            capacity = 1.5
        elif int(val[0]) >= 60:
            capacity = 2.0
        if capacity > 0.0:
            all_course_list.append([crs,capacity])
        else:
            course_without_ta.append(crs)
    for course in all_course_list:
        course_domain_dict_main[course[0]] = list()
        temp_list = []
        temp_list.append(course[1])
        course_domain_dict_main[course[0]].append(temp_list)
        for ta in ta_capacity:
            constr_check = check_constraint(ta,course,1)
            if constr_check == True:
                course_domain_dict_main[course[0]].append(ta)
    sample_dict = copy.deepcopy(course_domain_dict_main)
    for key, value in course_domain_dict_main.items():
        if len(sample_dict[key])==1:
            course_without_skilled_ta.append([key, value[0][0]])
            sample_dict.pop(key,None)
    course_domain_dict_main = copy.deepcopy(sample_dict)

"""This method triggers  the recursive_backtracking_search(course_domain_dict, solution) which gives the solution"""
def backtracking_search(course_domain_dict):
    solution = dict()
    result = recursive_backtracking_search(course_domain_dict, solution)
    ta_allocation = dict()
    print "TA ASSIGNMENT FOR COURSES:"
    for crs, assignment in solution.items():
        print crs, assignment
        for value in assignment:
            if value[0] == "needed":
                continue
            if ta_allocation.has_key(value[0]):
                ta_allocation[value[0]].append((crs , value[1]))
            else:
                ta_allocation[value[0]] = [(crs ,value[1])]

    for crs in course_without_skilled_ta:
        print crs[0], " [('needed', %.1f)]"%crs[1]

    for crs in course_without_ta:
        print crs, " [('needed', 0.0)]"

    print "****************************************************"
    print "COURSE ASSGINED TO TAs:"
    for ta, crs in ta_allocation.items():
        print ta, crs

"""
This method is the core method of implementation. In this method an unassigned course is picked and TA from the TA list
is assigned to this course. Before assigning the TA to the course check constraints methods are called to assess the
viability of TA assignment. Once a TA is assigned a recursive call is made again to assign TAs to remaining courses.
If the results of recursive call is failure which means if some course remained unassigned then different TA is assigned
 and recursive call is made again. In this way a solution list is generated which is later used to find an optimal
 solution based on maximum TA assignment. If recursive call result is not failure then the current assignment and
 result of remaining course assignment is combined and returned as an optimal solution.

Apart from assignment,domain values for all remaining courses are reduced based on the current assignment as in forward checking
and constraint propagation method is called after every assignment as a post processing step.
"""
def recursive_backtracking_search(course_domain_dict, solution):
    if(not bool(course_domain_dict)):
        return True
    else:
        unassigned_course = course_domain_dict.keys()[0]
        solution_list = list()
        for t_a in course_domain_dict[unassigned_course]:
            if(len(t_a)>1):
                solution_copy = copy.deepcopy(solution)
                course_domain_dict_copy = copy.deepcopy(course_domain_dict)
                filled_capacity = update_course_ta_in_dict(course_domain_dict_copy, unassigned_course,t_a)
                if solution_copy.has_key(unassigned_course):
                    solution_copy[unassigned_course].append((t_a[0], filled_capacity))
                else:
                    solution_copy[unassigned_course] = [(t_a[0], filled_capacity)]
                    constraint_propagation(course_domain_dict_copy,solution_copy)
                result = recursive_backtracking_search(course_domain_dict_copy,solution_copy)
                if result == False:
                    solution_list.append(solution_copy)
                else:
                    solution.clear()
                    solution.update(solution_copy)
                    return True
        if len(solution_list) == 0:
            ta_capacity_present = False
            for course_id, course_domain in course_domain_dict.items():
                if len(course_domain) > 1:
                    ta_capacity_present = True
                    break
            if not ta_capacity_present:
                for course_id, course_domain in course_domain_dict.items():
                    if solution.has_key(course_id):
                        solution[course_id].append(('needed', course_domain[0][0]))
                    else:
                        solution[course_id] = [('needed', course_domain[0][0])]
                    return True
                else:
                    solution_copy = copy.deepcopy(solution)
                    course_domain_dict_copy = copy.deepcopy(course_domain_dict)
                    course_domain_dict_copy.pop(unassigned_course,None)
                    result = recursive_backtracking_search(course_domain_dict_copy, solution_copy)
                    solution.clear()
                    solution.update(solution_copy)
                    return False
        elif len(solution_list)>0:
            solution.clear()
            solution.update(get_optimal_solution(solution_list))
            return False

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


"""Constraint propagation is done in addition to the forward checking, after every assignment. Constraint propagation is
a recursive method which is used to reduce the domain of each course. In this method, we pick the courses which have
only one possible assignment and assign the TAs to those courses. Then, we do a forward checking and reduce the domain
for other courses and recursively call constraint propagation again. The method exits, when all courses have more than
one possible assignment because in this case, the domain cannot be reduced anymore.
"""
def constraint_propagation(course_domain_dict_copy,solution_copy):
    course_list = list()
    for course in course_domain_dict_copy:
        if course_domain_dict_copy[course] == 2:
            course_list.append(course)
    if len(course_list)==0:
        return
    else:
        for course in course_list:
            unassigned_course = course
            t_a = course_domain_dict_copy[unassigned_course][1]
            filled_capacity = 0
            filled_capacity = update_course_ta_in_dict(course_domain_dict_copy,unassigned_course, t_a,filled_capacity)
            if solution_copy.has_key(unassigned_course):
                solution_copy[unassigned_course].append((t_a[0], filled_capacity))
            else:
                solution_copy[unassigned_course] = [(t_a[0], filled_capacity)]
            constraint_propagation(course_domain_dict_copy,solution_copy)




"""This method is a part of the forward checking process, and is used to reduce the TA domain for the other courses
based on the current assignment.
"""
def update_course_ta_in_dict(course_domain_dict_copy, unassigned_course, t_a):
    if course_domain_dict_copy[unassigned_course][0][0]>t_a[1]:
        filled_capacity = t_a[1]
        course_domain_dict_copy[unassigned_course][0][0] -= filled_capacity
        del course_domain_dict_copy[unassigned_course][course_domain_dict_copy[unassigned_course].index(t_a)]
        for key in course_domain_dict_copy:
            if t_a in course_domain_dict_copy[key]:
                del course_domain_dict_copy[key][course_domain_dict_copy[key].index(t_a)]
    elif course_domain_dict_copy[unassigned_course][0][0]<t_a[1]:
        filled_capacity = course_domain_dict_copy[unassigned_course][0][0]
        course_domain_dict_copy.pop(unassigned_course,None)
        for key in course_domain_dict_copy:
            if t_a in course_domain_dict_copy[key]:
                course_domain_dict_copy[key][course_domain_dict_copy[key].index(t_a)][1]-=filled_capacity
    elif course_domain_dict_copy[unassigned_course][0][0]==t_a[1]:
        filled_capacity = t_a[1]
        course_domain_dict_copy.pop(unassigned_course,None)
        for key in course_domain_dict_copy:
            if t_a in course_domain_dict_copy[key]:
                if course_domain_dict_copy[key][course_domain_dict_copy[key].index(t_a)][1]-filled_capacity>0:
                    course_domain_dict_copy[key][course_domain_dict_copy[key].index(t_a)][1]-=filled_capacity
                if course_domain_dict_copy[key][course_domain_dict_copy[key].index(t_a)][1]-filled_capacity==0:
                    del course_domain_dict_copy[key][course_domain_dict_copy[key].index(t_a)]
    return filled_capacity

"""
This method is the driver method for the implementation which reads the data using load_data utility
provided I load_data.py module and initiates backtracking along with constraint propagation by calling
backtracking_search(course_domain_dict) method.
"""
def main():
    load_data.load_data("D:\STONY_BROOK\SPRING_2015\AI\HW3\dataset_AI_CSP_Modified_test")
    create_list_of_dictionaries()
    course_domain_dict = dict()
    course_domain_dict = copy.deepcopy(course_domain_dict_main)
    backtracking_search(course_domain_dict)



if __name__ == '__main__':
    main()