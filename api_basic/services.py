import pandas as pd
import numpy as np
from .models import Exercises, VehiclesSelected, Vehicles, DataFinalExercisePc, DataFinalExercise, CoursesStudents, PPR, ExercisesSelected, Students, Courses, Venues, FinalExercisesSelected
from .serializers import ExercisesSerializer, ExercisesSelectedSerializer, VehiclesSelectedSerializer, VehiclesSerializer, DataFinalExercisePcSerializer, DataFinalExerciseSerializer, CoursesStudentsSerializer, PPRSerializer, StudentsSerializer, CoursesSerializer, VenuesSerializer, FinalExercisesSelectedSerializer



#Constants
SLALOM_ID = 1
LANE_CHANGE_ID = 2
#ID de student DEMO
demoId = 37




def getFinalTimeWithPenalties(data, courseValues):
    timesPc = []
    finalTimes = []
    for index, row in data.iterrows():
        cones = row['cones']
        gates = row['gates']
        time = row['time']
        finalTime = (time + (cones * courseValues['conePenalty']) + (gates * courseValues['gatePenalty']))
        timePc = (-(((finalTime / courseValues['idealTime']) * 100) - 200) / 100)
        timePc = round(timePc, 2)
        timesPc.append(timePc)
        finalTimes.append(finalTime)

    result = pd.DataFrame(columns=['finalTime','finalResult'])

    result['finalTime'] = finalTimes
    result['finalResult'] = timesPc

    return result


def radius(data):
    x = data['chord']
    y = data['mo']
    rd = (x ** 2) / (8 * y) + (y / 2)
    return rd

def mse_slalom_pc(data, idCourse):

    ex = FinalExercisesSelected.objects.get(idCourse=idCourse, idExercise=SLALOM_ID)
    exSerializer = FinalExercisesSelectedSerializer(ex).data
    R = radius(exSerializer)

    result = []
    for index, row in data.iterrows():

        vehicleSelected = VehiclesSelected.objects.get(pk=row['idVehicleSelected'])
        vehicle = Vehicles.objects.get(pk=VehiclesSelectedSerializer(vehicleSelected).data['idVehicle'])
        latAcc = VehiclesSerializer(vehicle).data['latAcc']

        vx = row['slalom']
        v = round(vx, 2)
        LA = ((v ** 2) / (R * 15))
        if LA >= latAcc:
            res = 0
        else:
            res = round(LA, 2) / latAcc
        result.append(int((round(res, 2)) * 100))

    return result


def mse_LnCh_pc(data, idCourse):

    ex = FinalExercisesSelected.objects.get(idCourse=idCourse, idExercise=LANE_CHANGE_ID)
    exSerializer = FinalExercisesSelectedSerializer(ex).data
    R = radius(exSerializer)

    result = []
    for index, row in data.iterrows():

        vehicleSelected = VehiclesSelected.objects.get(pk=row['idVehicleSelected'])
        vehicle = Vehicles.objects.get(pk=VehiclesSelectedSerializer(vehicleSelected).data['idVehicle'])
        latAcc = VehiclesSerializer(vehicle).data['latAcc']

        vx = row['laneChange']
        v = round(vx, 2)
        LA = ((v ** 2) / (R * 15))
        if LA >= latAcc:
            res = 0
        else:
            res = round(LA, 2) / latAcc
        result.append(int((round(res, 2)) * 100))

    return result


def saveDataPc(data):
    for index, row in data.iterrows():

        serializer = DataFinalExercisePcSerializer(data=row.to_dict())

        if serializer.is_valid():
            serializer.save()
        else:
            return False
    return True

def deleteDemoData(idCourse):

    DataFinalExercise.objects.filter(idCourse=idCourse,idStudent=demoId).delete()



def createPPR(idCourse, eventDate, idVenue):

    dataPc = DataFinalExercisePc.objects.filter(idCourse=idCourse)
    dataPcSerializer = DataFinalExercisePcSerializer(dataPc, many=True).data
    dataFrame = pd.DataFrame(data=dataPcSerializer)

    studentsSelected = CoursesStudents.objects.filter(idCourse=idCourse)
    studentsSelectedSerializer = pd.DataFrame(CoursesStudentsSerializer(studentsSelected, many=True).data)

    venueSerializer = VenuesSerializer(Venues.objects.get(pk=idVenue)).data



    for index, row in studentsSelectedSerializer.iterrows():

        studentId = row['idStudent']

        student_runs = dataFrame.loc[(dataFrame['idStudent'] == studentId), 'finalResult'].count()

        student_best_run_idx = dataFrame.loc[(dataFrame['idStudent'] == studentId), 'finalResult'].idxmax()
        student_best_run = dataFrame.iloc[student_best_run_idx]

        ppr_penalties = 20 - ((student_best_run['cones'] + student_best_run['gates']) * 5)
        if ppr_penalties < 0:
            ppr_penalties = 0
        if student_best_run['slalom'] >= 40:
            ppr_slalom = round(25 * (student_best_run['slalom'] / 100), 0)
        else:
            ppr_slalom = 0
        if student_best_run['laneChange'] >= 40:
            ppr_LnCh = round(25 * (student_best_run['laneChange'] / 100), 0)
        else:
            ppr_LnCh = 0
        if student_best_run['finalResult'] >= .4:
            ppr_final_result = round(30 * student_best_run['finalResult'], 0)
        else:
            ppr_final_result = 0
        student_ppr = ppr_penalties + ppr_slalom + ppr_LnCh + ppr_final_result

        studentSerializer = StudentsSerializer(Students.objects.get(pk=studentId)).data

        newPPR = {
            'idCourse': idCourse,
            'idStudent': studentId,
            'idCompany': studentSerializer['idCompany'],
            'idCountry': venueSerializer['idCountry'],
            'PPR': student_ppr,
            'runs': student_runs,
            'eventDate': eventDate
        }

        serializer = PPRSerializer(data=newPPR)
        if serializer.is_valid():
            serializer.save()
        else:
            return False

    return True


def dataFinalExercisePcExists(idCourse):

    dataPc = DataFinalExercisePc.objects.filter(idCourse=idCourse).count()

    if dataPc > 0:
        return True

    return False

def getDataExercisePc(exercises, idCourse, idStudent):

    exercises['exercisePc'] = ex_percetage(exercises)
    exercises['vehiclePc'] = v_percetage(exercises)

    counts = getCountsDataExercise(exercises, idCourse)
    groupAverage = getGroupAverage(counts, exercises, idCourse)
    studentValues = getStudentValues(exercises,counts,idStudent, idCourse)
    studentPlots = getStudentPlots(exercises, idStudent, idCourse)

    result = {
        "groupAverage": groupAverage,
        "studentValues": studentValues,
        "studentPlot": studentPlots
    }

    return result

def getStudentPlots(exercises, idStudent, idCourse):
    exerciseSelected = ExercisesSelected.objects.filter(idCourse=idCourse)
    dataExercise = pd.DataFrame(ExercisesSelectedSerializer(exerciseSelected, many=True).data)
    result =[]
    for index, row in dataExercise.iterrows():
        exerciseData = round(exercises.loc[(exercises['idStudent'] == idStudent) & (exercises['idExerciseSelected'] == row['id'])]['exercisePc'] * 100, 2)
        vehicleData = round(exercises.loc[(exercises['idStudent'] == idStudent) & (exercises['idExerciseSelected'] == row['id'])]['vehiclePc']* 100, 2)

        exerciseName = ExercisesSerializer(Exercises.objects.get(pk=row['idExercise'])).data['name']

        res = {
            'exercise': exerciseName,
            'exerciseData': exerciseData,
            'vehicleData': vehicleData
        }
        result.append(res)
    return result

def getStudentValues(exercises, counts, idStudent, idCourse):
    exerciseSelected = ExercisesSelected.objects.filter(idCourse=idCourse)
    dataExercise = pd.DataFrame(ExercisesSelectedSerializer(exerciseSelected, many=True).data)

    vehiclePc = pd.DataFrame(exercises.replace(0, np.nan)
                             .groupby(['idStudent', 'idExerciseSelected'])
                             .agg({'vehiclePc': 'mean'})).unstack(level=1)
    result= []
    for index, row in dataExercise.iterrows():
        numberRuns = int(counts['Count'][row['id']][idStudent])
        completedExercisesPc = int(round(counts[str(row['id'])+' Passed Pc'][idStudent] * 100, 0))
        averageExercisePc = int(round(counts['Av Score'][row['id']][idStudent] * 100, 0))
        averageVehicleControl = int(round(vehiclePc['vehiclePc'][row['id']][idStudent] * 100, 0))
        finalPerformanceLevel = int(round(counts['End Score'][row['id']][idStudent] * 100))

        exerciseName = ExercisesSerializer(Exercises.objects.get(pk=row['idExercise'])).data['name']

        res = {
            "exercise": exerciseName,
            "numberRuns": numberRuns,
            "completedExercisesPc": completedExercisesPc,
            "averageExercisePc": averageExercisePc,
            "averageVehicleControl": averageVehicleControl,
            "finalPerformanceLevel": finalPerformanceLevel
        }
        result.append(res)
    return result

def getGroupAverage(counts, exercises, idCourse):
    exerciseSelected = ExercisesSelected.objects.filter(idCourse=idCourse)
    dataExercise = pd.DataFrame(ExercisesSelectedSerializer(exerciseSelected, many=True).data)


    result = []
    for index, row in dataExercise.iterrows():

        numberRuns = int((counts['Count'][row['id']].agg('mean')))
        completedExercisesPc = int((counts[str(row['id'])+' Passed Pc'].mean()) * 100)
        averageExercisePc = int((counts['Av Score'][row['id']].mean()) * 100)
        averageVehicleControl = int((exercises.loc[exercises['idExerciseSelected'] == row['id']]['vehiclePc'].mean()) * 100)

        exerciseName = ExercisesSerializer(Exercises.objects.get(pk=row['idExercise'])).data['name']

        res = {
            "exercise": exerciseName,
            "numberRuns" : numberRuns,
            "completedExercisesPc": completedExercisesPc,
            "averageExercisePc": averageExercisePc,
            "averageVehicleControl": averageVehicleControl
        }
        result.append(res)

    return result

def getCountsDataExercise(exercises, idCourse):
    exerciseSelected = ExercisesSelected.objects.filter(idCourse=idCourse)
    dataExercise = pd.DataFrame(ExercisesSelectedSerializer(exerciseSelected, many=True).data)


    counts = pd.DataFrame(exercises.replace(0, np.nan)
                             .groupby(['idStudent', 'idExerciseSelected'])
                             .agg(
        {'idExerciseSelected': 'size', 'exercisePc': ['count', 'mean'], 'vehiclePc': ['min', 'max']})
                             .rename(
        columns={'size': 'Count', 'count': 'Passed', 'mean': 'Av Score', 'min': 'Start Score',
                 'max': 'End Score'})).unstack(level=1)
    counts.columns = counts.columns.droplevel(0)


    for index, row in dataExercise.iterrows():

        count = counts['Count'][row['id']]
        passed = counts['Passed'][row['id']]
        counts[str(row['id'])+' Passed Pc'] = (passed/count)

    return counts

def ex_percetage(data):
    result = []
    for index, row in data.iterrows():
        x = row[['v1', 'v2', 'v3']].mean()
        sd = row[['v1', 'v2', 'v3']].std()
        cns = row['penalties']
        y = round(x, 2)
        z = row['speedReq']
        p = ((y / z))
        res = round(p, 2)
        if sd < 3 and cns == 0:
            pass
        else:
            res = 0
        result.append(res)
    return result


def v_percetage(data):
    result = []
    for index, row in data.iterrows():
        vx = row[['v1', 'v2', 'v3']].mean()
        sd = row[['v1', 'v2', 'v3']].std()
        exerciseSelected = ExercisesSelected.objects.get(pk=row['idExerciseSelected'])
        exSerializer = ExercisesSelectedSerializer(exerciseSelected).data
        R = radius(exSerializer)
        v = round(vx, 2)
        LA = ((v ** 2) / (R * 15))

        vehicleSelected = VehiclesSelected.objects.get(pk=row['idVehicleSelected'])
        vehicle = Vehicles.objects.get(pk=VehiclesSelectedSerializer(vehicleSelected).data['idVehicle'])
        latAcc = VehiclesSerializer(vehicle).data['latAcc']

        res = round(LA, 2) / latAcc

        result.append(res)
    return result







