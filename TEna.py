from datetime import date
from datetime import timedelta
import json
import os
import sys

version = "v0.3.1"
#versiondesc = ""
fileprotocol = 3
jsontemplate = json.loads('{"protocol": %d, "tasks": []}' %(fileprotocol))
tasksfilename = "tasks.json"
maxtask_id = 1000

def readfile(filename):
    with open(filename, "r") as file:
        jsoncontent = json.load(file)
    return jsoncontent

def writefile(filename, jsontowrite):
    with open(filename, "w") as file:
        json.dump(jsontowrite, file)

def friendlyprint(task):
    print("%d: %s (%s)" %(task["task_id"], task["task_name"], task["task_category"]))
    if task["task_assigned"] != None:
        print("  assigned ISO %d %d, raw %s" %(task["task_assigned"]["year"], task["task_assigned"]["week"], task["task_assigned"]["raw_date"]))
    if task["task_due"] != None:
        print("  due ISO %d %d" %(task["task_due"]["year"], task["task_due"]["week"]))
        if task["task_complete"] == None:
            assignediso = date.fromisocalendar(task["task_assigned"]["year"], task["task_assigned"]["week"], 1)
            dueiso = date.fromisocalendar(task["task_due"]["year"], task["task_due"]["week"], 1)
            currentiso = date.fromisocalendar(currentisoyear, currentisoweek, 1)
            deadlinedelta = (dueiso - assignediso).days // 7
            remainingdelta = (dueiso - currentiso).days // 7
            print("  deadline %d, remaining %d" %(deadlinedelta, remainingdelta))
        else:
            assignediso = date.fromisocalendar(task["task_assigned"]["year"], task["task_assigned"]["week"], 1)
            dueiso = date.fromisocalendar(task["task_due"]["year"], task["task_due"]["week"], 1)
            completeiso = date.fromisocalendar(task["task_complete"]["year"], task["task_complete"]["week"], 1)
            deadlinedelta = (dueiso - assignediso).days // 7
            remainingdelta = (dueiso - completeiso).days // 7
            print("  deadline %d, remaining %d" %(deadlinedelta, remainingdelta))
    if task["task_complete"] != None:
        print("  completed ISO %d %d, raw %s" %(task["task_complete"]["year"], task["task_complete"]["week"], task["task_complete"]["raw_date"]))

os.system("clear")
print("Running TEna %s (using file protocol %d)..." %(version, fileprotocol))
print("Working directory: " + os.getcwd())

currentdate = date.today()
print(currentdate.strftime("%A, %d %B %Y (ISO week %V, %G)"))
rawdate = currentdate.isoformat()
currentisoweek = currentdate.isocalendar().week
currentisoyear = currentdate.isocalendar().year

if not os.path.isfile(tasksfilename):
    print("JSON file missing! Creating %s..." %(tasksfilename))
    writefile(tasksfilename, jsontemplate)

print("Reading %s..." %(tasksfilename))
jsoncontent = readfile(tasksfilename)
print("File protocol %d" %(jsoncontent["protocol"]))
if jsoncontent["protocol"] != fileprotocol:
    print("Expected file protocol %d, got %d! Exiting..." %(fileprotocol, jsoncontent["protocol"]))
    sys.exit()
print("Found %d tasks" %(len(jsoncontent["tasks"])))
for task in jsoncontent["tasks"]:
    friendlyprint(task)
    if task["task_id"] > maxtask_id:
        maxtask_id = task["task_id"]

unsaved = False
print("Do what?")
while True:
    if unsaved:
        userinput = input("*> ").lower()
    else:
        userinput = input(" > ").lower()

    if userinput == "":
        pass
    elif userinput == "addtask" or userinput == "newtask":
        newtask_id = maxtask_id + 1
        print("New task will be assigned ID %d" %(newtask_id))
        newtask_assigned = {"raw_date": rawdate, "week": currentisoweek, "year": currentisoyear}
        newtask_name = input("Enter task name: ")
        inputgate = True
        while inputgate:
            newtask_category = input("Enter task category: (normal/deferred/blacklisted) ").lower()
            if newtask_category == "normal" or newtask_category == "n":
                newtask_category = "normal"
                inputgate = False
            elif newtask_category == "deferred" or newtask_category == "d":
                newtask_category = "deferred"
                inputgate = False
            elif newtask_category == "blacklisted" or newtask_category == "b":
                newtask_category = "blacklisted"
                inputgate = False
        if newtask_category == "normal":
            try:
                weekdelta = int(input("Due in how many weeks? "))
            except ValueError:
                print("Hit ValueError! (requires integer input)")
                print("Setting 0 weeks...")
                weekdelta = 0
            duedate = currentdate + timedelta(weeks = weekdelta)
            newtask_due = {"week": duedate.isocalendar().week, "year": duedate.isocalendar().year}
        else:
            newtask_due = None
        if newtask_category != "blacklisted":
            inputgate = True
            while inputgate:
                newtask_complete = input("Task complete? (yes/no) ").lower()
                if newtask_complete == "yes" or newtask_complete == "y":
                    newtask_complete = {"raw_date": rawdate, "week": currentisoweek, "year": currentisoyear}
                    inputgate = False
                elif newtask_complete == "no" or newtask_complete == "n":
                    newtask_complete = None
                    inputgate = False
        else:
            newtask_complete = None
        newtask = {"task_id": newtask_id, "task_name": newtask_name, "task_category": newtask_category, "task_assigned": newtask_assigned, "task_due": newtask_due, "task_complete": newtask_complete}
        jsoncontent["tasks"].append(newtask)
        print("New task added!")
        friendlyprint(newtask)
        unsaved = True
        maxtask_id += 1
    elif userinput == "edittask":
        try:
            task_id = int(input("Enter task ID: "))
        except ValueError:
            print("Hit ValueError! (requires integer input)")
        else:
            taskfound = False
            for task in jsoncontent["tasks"]:
                if task_id == task["task_id"]:
                    taskfound = True
                    friendlyprint(task)
                    task_name = input("Rename task [%s]: " %(task["task_name"]))
                    if task_name != "":
                        print("Renaming...")
                        task["task_name"] = task_name
                    inputgate = True
                    while inputgate:
                        task_category = input("Enter new task category [%s]: " %(task["task_category"])).lower()
                        if task_category == "":
                            inputgate = False
                        elif task_category == "normal" or task_category == "n":
                            print("Changing category...")
                            task["task_category"] = "normal"
                            inputgate = False
                        elif task_category == "deferred" or task_category == "d":
                            print("Changing category...")
                            task["task_category"] = "deferred"
                            inputgate = False
                        elif task_category == "blacklisted" or task_category == "b":
                            print("Changing category...")
                            task["task_category"] = "blacklisted"
                            inputgate = False
                    inputgate = True
                    while inputgate:
                        task_assigned = input("Reassign task? (yes/no) ").lower()
                        if task_assigned == "yes" or task_assigned == "y":
                            task["task_assigned"] = {"raw_date": rawdate, "week": currentisoweek, "year": currentisoyear}
                            inputgate = False
                        elif task_assigned == "no" or task_assigned == "n":
                            inputgate = False
                    if task["task_category"] == "normal":
                        try:
                            weekdelta = int(input("Due in how many weeks? "))
                        except ValueError:
                            print("Hit ValueError! (requires integer input)")
                            print("Setting 0 weeks...")
                            weekdelta = 0
                        duedate = date.fromisoformat(task["task_assigned"]["raw_date"]) + timedelta(weeks = weekdelta)
                        task["task_due"] = {"week": duedate.isocalendar().week, "year": duedate.isocalendar().year}
                    else:
                        task["task_due"] = None
                    if task["task_category"] != "blacklisted":
                        inputgate = True
                        while inputgate:
                            task_complete = input("Task complete? (yes/no) ").lower()
                            if task_complete == "yes" or task_complete == "y":
                                task["task_complete"] = {"raw_date": rawdate, "week": currentisoweek, "year": currentisoyear}
                                inputgate = False
                            elif task_complete == "no" or task_complete == "n":
                                task["task_complete"] = None
                                inputgate = False
                    else:
                        task["task_complete"] = None
                    print("Task edited!")
                    friendlyprint(task)
                    unsaved = True
                    break
            if not taskfound:
                print("Task not found!")
    elif userinput == "deletetask" or userinput == "deltask":
        try:
            task_id = int(input("Enter task ID: "))
        except ValueError:
            print("Hit ValueError! (requires integer input)")
        else:
            taskfound = False
            for task in jsoncontent["tasks"]:
                if task_id == task["task_id"]:
                    taskfound = True
                    friendlyprint(task)
                    inputgate = True
                    while inputgate:
                        userinput = input("Are you sure? (yes/no) ").lower()
                        if userinput == "yes" or userinput == "y":
                            print("Deleting...")
                            task["task_name"] = "(deleted)"
                            task["task_category"] = "deleted"
                            task["task_assigned"] = None
                            task["task_due"] = None
                            task["task_complete"] = None
                            print("Task deleted!")
                            # vv -- remove this later
                            friendlyprint(task)
                            # ^^ --
                            unsaved = True
                            inputgate = False
                        elif userinput == "no" or userinput == "n":
                            print("Cancelled deletion.")
                            inputgate = False
                    break
            if not taskfound:
                print("Task not found!")
    elif userinput == "save" or userinput == "write":
        print("Writing to %s..." %(tasksfilename))
        writefile(tasksfilename, jsoncontent)
        print("Done!")
        unsaved = False
    elif userinput == "exit" or userinput == "quit":
        if unsaved:
            userinput = input("You have unsaved changes! Save? (yes/no) ").lower()
            if userinput == "yes" or userinput == "y":
                print("Writing to %s..." %(tasksfilename))
                writefile(tasksfilename, jsoncontent)
                print("Done!")
                #unsaved = False
                print("Exiting...")
                sys.exit()
            elif userinput == "no" or userinput == "n":
                print("Exiting without saving...")
                sys.exit()
            else:
                print("Cancelled exit.")
        else:
            print("Exiting...")
            sys.exit()
    else:
        print("Unrecognised command")
