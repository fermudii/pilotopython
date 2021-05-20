from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework.parsers import JSONParser
#from .models import Article, Piloto, Course, FinalExercise
from .models import Courses, DataFinalExercise, DataExercises
from .serializers import CoursesSerializer, DataFinalExerciseSerializer, DataExercisesSerializer
from .services import *
#from .serializers import ArticleSerializer, PilotoSerializer, ReportSerializer, CountSerializer, \
   # FinalExerciseSerializer, CommentsSerializer, SlalomAvgSerializer, CourseSerializer
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView
from rest_framework import generics
from rest_framework import mixins
from rest_framework.authentication import SessionAuthentication, BasicAuthentication, TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework import viewsets
from django.shortcuts import get_object_or_404
import os
from django.conf import settings

import base64


# Librerias de piloto
# In[1]:
import pandas as pd
import numpy as np
from datetime import datetime
import pytz
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
from matplotlib.offsetbox import (TextArea, DrawingArea, OffsetImage, AnnotationBbox)
from docxtpl import DocxTemplate, InlineImage
import jinja2
import sys
import os
import time
from docx2pdf import convert
# Create your views here.


class DataExercisePCView(APIView):
    def post(self, request):

        #Obteniendo parametro idCourse and idStudent
        dictionary = request.data
        idCourse = dictionary['idCourse']
        idStudent = dictionary['idStudent']

        dataExercise = DataExercises.objects.filter(idCourse=idCourse)

        exercises = pd.DataFrame(DataExercisesSerializer(dataExercise, many=True).data)

        dataPc = getDataExercisePc(exercises, idCourse, idStudent)

        return Response(dataPc,status=status.HTTP_200_OK)


class DataFinalPcView(APIView):
    def post(self, request):

        #Obteniendo parametro idCourse
        dictionary= request.data
        idCourse = dictionary['idCourse']

        #Eliminando data del demo
        deleteDemoData(idCourse)

        #Verificando que no exista ya el DataExercisePc
        dataExists = dataFinalExercisePcExists(idCourse)
        if dataExists:
            return Response({'messsage': 'Data exists'}, status=status.HTTP_400_BAD_REQUEST)

        #Obteniendo course y dataFinalExercise de base de datos
        dataCourse = Courses.objects.get(pk=idCourse)
        dataFinalExercise = DataFinalExercise.objects.filter(idCourse=idCourse)

        #Serializando data
        course = CoursesSerializer(dataCourse).data
        finalExercise = pd.DataFrame(DataFinalExerciseSerializer(dataFinalExercise, many=True).data)

        dataPc = getFinalTimeWithPenalties(finalExercise, course)

        dataPc['rev'] = finalExercise.apply(lambda x: round((x['revSlalom'] / x['time']), 2), axis=1)
        dataPc['cones'] = finalExercise['cones']
        dataPc['gates'] = finalExercise['gates']

        slalomPc = mse_slalom_pc(finalExercise)
        dataPc['slalom'] = slalomPc

        laneChangePc = mse_LnCh_pc(finalExercise)
        dataPc['laneChange'] = laneChangePc

        dataPc['idCourse'] = finalExercise['idCourse']
        dataPc['idStudent'] = finalExercise['idStudent']

        result = saveDataPc(dataPc)

        if result:
            PPRCreated = createPPR(idCourse, course['eventDate'])
            if PPRCreated:
                return Response({'message': 'OK'}, status=status.HTTP_200_OK)
            else:
                return Response({'message': 'PPR not created'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        else:
            return Response({'error': 'Something is wrong'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)





class FinalExercisePlotView(APIView):
    def post(self, request):
        dictionary = request.data
        student = dictionary['student']

        data = FinalExercise.objects.filter(company=dictionary['company'],
                                            fulldate=dictionary['fulldate'])

        serializer = FinalExerciseSerializer(data, many=True)

        if not serializer.data:
            return Response({"message": "No hay data"}, status=status.HTTP_400_BAD_REQUEST)

        finalx_df = pd.DataFrame(serializer.data)

        finalx_df['fTime'] = pd.to_timedelta(finalx_df['fTime']);
        finalx_df['revSlalom'] = pd.to_timedelta(finalx_df['revSlalom'])

        data_time = finalx_df.loc[finalx_df['student'] == student].fTime.dt.total_seconds()
        data_time = data_time.reset_index(drop=True)
        data_performance = finalx_df.loc[finalx_df['student'] == student].finalResult * 100
        data_performance = data_performance.reset_index(drop=True)
        data_rv = finalx_df.loc[finalx_df['student'] == student].revSlalom.dt.total_seconds()
        data_rv = data_rv.reset_index(drop=True)
        data_tm_fn = data_time - data_rv
        cones_fn = finalx_df.loc[finalx_df['student'] == student].cones
        cones_fn = cones_fn.reset_index(drop=True)
        gates_fn = finalx_df.loc[finalx_df['student'] == student].gates
        gates_fn = gates_fn.reset_index(drop=True)
        #xtick = mse_report[student][0]['f_time']
        cone_img = mpimg.imread('assets/cones_for_reports.png')

        av_rev_result = finalx_df['revSlalom'].mean().total_seconds()
        av_gp_time = finalx_df['fTime'].mean().total_seconds()

        pass_time = (80 * 1.2)

        passes = data_time.index.tolist()
        passes.append(2)

        label = finalx_df.loc[finalx_df['student'] == student].stress
        label = label.reset_index(drop=True).replace(0, "Low Stress").replace(1, 'High Stress')

        imagebox = OffsetImage(cone_img, zoom=0.1)

        fig, ax = plt.subplots(figsize=(8, 3))

        imagebox.image.axes = ax

        data_sx = finalx_df.loc[finalx_df['student'] == student].finalResult.iat[0]
        min_stdx = 80 - data_sx
        if min_stdx < 0:
            min_stdx = 0
        else:
            pass
        data_yx = 100 - (min_stdx + data_sx)

        barHeight = .8



        #Data necesaria
        mseg_t_pre = str(finalx_df['fTime'].mean())
        mseg_t = mseg_t_pre[mseg_t_pre.find(':') + 1: mseg_t_pre.find('.') + 3:]  # mse_group_av_time
        mseg_c = int((finalx_df['cones'].mean()))  # mse_group_av_cones
        mseg_g = int((finalx_df['gates'].mean()))  # mse_group_av_gates
        mseg_perf = int((finalx_df['finalResult'].mean()) * 100)  # mse_group_av_performance
        mseg_per = int((finalx_df['finalResult'].quantile()) * 100)  # mse_group_av_percentile
        mse_obj = str(80)[10::]  # mse_objective_obj
        mseg_rev_pre = str(finalx_df['revSlalom'].mean())  # strings mse_group_used_in_rev
        mseg_rev = mseg_rev_pre[
                   mseg_rev_pre.find(':') + 4: mseg_rev_pre.find('.') + 3:]  # strings mse_group_used_in_rev
        mseg_rev_pc = int(round(((finalx_df['revPc'].mean()) * 100), 0))

        # Average Bar
        ax.barh('Av', av_rev_result, color='khaki', edgecolor='white', height=.3)
        ax.barh('Av', av_gp_time - av_rev_result, left=av_rev_result, color='gold', edgecolor='white', height=.3)
        ax.annotate("""Average: """ + str(mseg_t), (mseg_perf, .3), color='black', va='center', ha='right',
                    fontsize=8)
        ax.annotate('Av. Rev: ' + str(mseg_rev), (2, .3), color='black', va='center', ha='left', fontsize=8)
        ax.annotate(""" Av. Penalties: """ + str(mseg_c) + " | " + str(mseg_g), (mseg_perf - 50, .3), color='black',
                    fontsize=8, va='center')
        ax.annotate('Gp. Average ' + str(mseg_perf) + '%', xy=(av_gp_time + .3, 0), xytext=(av_gp_time + 10, 0),
                    ha='left', fontsize=10,
                    arrowprops=dict(arrowstyle='->'), va='center')

        td_start, td_stop, td_step = 10, -4, 1

        finalx_df['fTime'] = finalx_df['fTime'].astype(str)
        finalx_df['fTime'] = finalx_df['fTime'].str.slice(td_start, td_stop, td_step)

        print(finalx_df)

        # Main Bar Legend
        for i, v in data_tm_fn.items():
            # Student Bar
            ax.barh(i + 1, data_rv[i], color='darkred', edgecolor='white', height=barHeight)
            ax.barh(i + 1, data_tm_fn[i], left=data_rv[i], color='red', edgecolor='white', height=barHeight)

            xtick1 = finalx_df.loc[finalx_df['student'] == student].fTime.iat[i]
            xtick2 = str(datetime.strptime(xtick1, '%M:%S.%f').time())[4:-4]

            ax.annotate("""Score: """ + xtick2, ((v + data_rv[i]) - 1, i + 1), color='w', fontsize=10,
                        fontweight='bold', va='center', ha='right')
            ax.annotate(str(int(data_performance[i])) + '%', ((v + data_rv[i]) + 1, i + 1), color='black',
                        fontsize=10, fontweight='bold', va='center', ha='left')

            # Acceptable Reverse Annotation
            ax.annotate('', (.1, i + 1.4), xytext=((data_time[i] * .2), i + 1.4), arrowprops=dict(arrowstyle='|-|'),
                        va='top')
            ax.annotate("""Acceptable Reverse""", (.5, 1.5), xytext=(data_time[i] * .21, i + 1.5), va='center',
                        fontsize=8)

            # Stress Labels
            if label[i] == "High Stress":
                label_color = 'orangered'
            else:
                label_color = 'yellowgreen'
            ax.annotate(label[i], ((v + data_rv[i]) + 1, i + .8), ha='left', va='top', fontsize=8,
                        fontweight='bold', color=(label_color))
            # Add Penalties
            ab = AnnotationBbox(imagebox,
                                (data_rv[i] + 5, i + 1),  # Bar Image
                                xybox=(0., 0.),
                                xycoords='data',
                                boxcoords="offset points",
                                frameon=False)
            ax.add_artist(ab)
            ax.annotate("""Penalties: """ + str(cones_fn[i]) + " | " + str(gates_fn[i]), (data_rv[i] + 9, i + 1),
                        color='w', fontsize=10, fontweight='bold', va='center')

        for i, v in data_rv.items():
            ax.annotate("Reverse:\n" + str(round(float(v), 2)), (2, i + 1), color='w', fontsize=10, fontweight='bold',
                        va='center')  # Reverse Bar Legend

        # Pass or Fail Annotation
        ax.axvline(pass_time, linestyle='--', ymax=len(passes), color='silver')
        ax.annotate('Security Driver', xy=(pass_time - 25, len(passes) - .3),
                    xytext=(pass_time - 1, len(passes) - .3), ha='right', fontsize=10,
                    arrowprops=dict(arrowstyle='->'), va='center')
        ax.annotate('Needs More Work', xy=(pass_time + 28, len(passes) - .3),
                    xytext=(pass_time + 1, len(passes) - .3), fontsize=10,
                    arrowprops=dict(arrowstyle='->'), va='center')

        ax.set_yticks([])
        ax.set_xticks([])
        ax.axis('off')

        fig.tight_layout()
        plt.xlim(xmin=0, xmax=pass_time + 30)
        plt.ylim(ymin=-.5, ymax=len(passes))
        plt.savefig('plots/final_exercise.png', format="png", bbox_inches='tight', dpi=100)
        plt.close()

        with open('plots/final_exercise.png', 'rb') as f:
            contents = f.read()

        pic_base64 = base64.b64encode(contents);

        return Response({"data": pic_base64},status=status.HTTP_200_OK)




class SlalomPlotView(APIView):
    def post(self, request):
        dictionary = request.data

        data = Course.objects.filter(student=dictionary['student'], company=dictionary['company'],
                                     fulldate=dictionary['fulldate'], exercise=dictionary['exercise'])

        serializer = CourseSerializer(data, many=True)

        if not serializer.data:
            return Response({"message": "No hay data"}, status=status.HTTP_400_BAD_REQUEST)

        ax1_slalom_plt = []
        ax2_slalom_plt = []

        for row in serializer.data:
            ax1_slalom_plt.append(row['pcExercise'] * 100)
            ax2_slalom_plt.append(row['pcVehicle'] * 100)

        # Slalom Graph
        plt.style.use('seaborn-dark-palette')
        plt.figure(figsize=(6.5, 2))
        plt.axhline(y=80, color='#C87867', ls='--', lw=3)
        plt.annotate('Ideal', (0, 90), ha='center', va='center', fontsize=8, color='#C87867')
        plt.axhline(y=100, color='#67BEC8', ls='--', lw=3)
        plt.annotate('Ideal', (0, 110), ha='center', va='center', fontsize=8, color='#67BEC8')

        plt.plot(ax1_slalom_plt, label='% Del Ejercicio', linewidth=3, color='#001EBA')
        plt.plot(ax2_slalom_plt, label='% Del Vehículo', linewidth=3, color='#BA0000')
        plt.title('Resultados de ' + dictionary['exercise'] + ' - ' + dictionary['student'])

        plt.ylim(ymin=0, ymax=120)
        plt.legend()
        plt.xlabel('Runs')
        plt.ylabel('%')
        plt.tight_layout()

        plt.savefig('plots/slalomGraph.png',format="png", bbox_inches='tight', dpi=100)
        plt.close()

        with open('plots/slalomGraph.png', 'rb') as f:
            contents = f.read()

        pic_base64 = base64.b64encode(contents);

        return Response({"data": pic_base64},status=status.HTTP_200_OK)


class FilesAPIView(APIView):
    def post(self, request):
        data = []
        for filename, file in request.FILES.items():
            data.append(file)

        data_file = data[0]
        car1_mse_data = data[1]
        car2_mse_data = data[2]
        car3_mse_data = np.nan

        # VBox Data import
        if pd.isnull(car1_mse_data):
            c1_df = pd.DataFrame(columns=['Run', 'Time (s)', 'Speed (Avg) (mph)', 'Speed (Std Dev) (mph)',
                                          'UTC time (At Start)', 'car'])
        else:
            c1_df = pd.read_csv(car1_mse_data, skiprows=[0])
            c1_df['car'] = 1

        if pd.isnull(car2_mse_data):
            c2_df = pd.DataFrame(columns=['Run', 'Time (s)', 'Speed (Avg) (mph)', 'Speed (Std Dev) (mph)',
                                          'UTC time (At Start)', 'car'])
        else:
            c2_df = pd.read_csv(car2_mse_data, skiprows=[0])
            c2_df['car'] = 2

        if pd.isnull(car3_mse_data):
            c3_df = pd.DataFrame(columns=['Run', 'Time (s)', 'Speed (Avg) (mph)', 'Speed (Std Dev) (mph)',
                                          'UTC time (At Start)', 'car'])
        else:
            c3_df = pd.read_csv(car3_mse_data, skiprows=[0])
            c3_df['car'] = 3

        # In[5]:

        # c1_df_to_drop = c1_df[~c1_df['Run'].str.isdigit()].index.tolist()
        # # c1_df.iloc[c1_df_to_drop].tail(50)
        # c1_df.drop(c1_df.index[c1_df_to_drop], inplace=True)

        # In[6]:

        # Course data import from excel file
        students = pd.read_excel(data_file, sheet_name=("Students"))
        raw_runs = pd.read_excel(data_file, sheet_name=("Skill Building"))  # bSkill building
        raw_values = pd.read_excel(data_file, sheet_name=("Course Values"), skiprows=1)
        finalx_df = pd.read_excel(data_file, sheet_name=("Final Exercise"))
        comments_x = pd.read_excel(data_file, sheet_name=(
            'Instructor Comments')).dropna()  # .set_index('participant', inplace=True)

        # In[7]:

        finalx_df.head()

        # In[8]:

        finalx_df_empty_rows = finalx_df[finalx_df['Participant'].isnull()].index.tolist()
        finalx_df.drop(finalx_df.index[finalx_df_empty_rows], inplace=True)

        # In[9]:

        comments = pd.Series(comments_x['comment']).astype(str)

        # In[10]:

        # students['comment'] = comments['comment']

        # In[11]:

        # comments
        raw_values
        # raw_runs

        # In[12]:

        raw_values['Date'] = pd.to_datetime(raw_values['Date'])

        # In[13]:

        raw_values['Ideal_Time Sec'] = pd.to_timedelta(raw_values['Ideal_Time Sec'], unit='s')

        # In[14]:

        students_df = pd.DataFrame(students, columns=["firstname", "lastname", "gender", "dob"])

        # In[15]:

        exercise_values = pd.DataFrame(raw_values, columns=["Exercise", "Chord", "MO", ])
        exercise_values.dropna(inplace=True)

        # In[16]:

        exercise_values.set_index('Exercise', inplace=True)

        # In[17]:

        exercise_values

        # In[18]:

        rds = []

        # In[19]:

        def radius(data):
            for index, row in data.iterrows():
                x = row['Chord']
                y = row['MO']
                rd = (x ** 2) / (8 * y) + (y / 2)
                rds.append(rd)

        # In[20]:

        radius(exercise_values)

        # In[21]:

        exercise_values['Radius'] = rds

        # In[22]:

        exercise_values

        # In[23]:

        course_cars = pd.DataFrame(raw_values, columns=["Car", "Make", "LatAcc", ], )
        course_cars.set_index('Car', inplace=True)

        # In[24]:

        course_df = pd.DataFrame(
            raw_runs,
            columns=[
                "ID",
                "Car #",
                "Participant",
                "Exercise",
                "Speed Req",
                "V1",
                "V2",
                "V3",
                "Cones",
            ],
        ).replace('NaN', np.nan)

        # In[25]:

        all_empty_row = course_df[
            course_df[['Speed Req', 'V1', 'V2', 'V3']].isnull().all(axis=1) == True].index.tolist()
        course_df.drop(course_df.index[all_empty_row], inplace=True)

        # In[26]:

        # Units of Measure (Metric or Imperial)
        units = raw_values.loc[0, 'Units']
        kms_per_mile = 1.609344

        # In[27]:

        # Conversion formula 1.609344 kms per mile
        if units == 'MPH':
            pass
        else:
            course_df['Speed Req'] = round((course_df['Speed Req'] / kms_per_mile), 0).astype(int)
            course_df['V1'] = round((course_df['V1'] / kms_per_mile), 0).astype(int)
            course_df['V2'] = round((course_df['V2'] / kms_per_mile), 0).astype(int)
            course_df['V3'] = round((course_df['V3'] / kms_per_mile), 0).astype(int)

        # In[28]:

        course_df.tail(80)

        # In[29]:

        course_df.tail(50)

        # In[30]:

        course_df.columns = course_df.columns.str.replace(' ', '_')
        course_df.columns = (x.lower() for x in course_df.columns)
        course_df.set_index('id', inplace=True)

        # In[31]:

        course_df['cones'] = course_df['cones'].fillna(0)
        course_df['cones'] = course_df['cones'].astype(int)

        # In[32]:

        course_df

        # In[33]:

        exercise_values.columns = exercise_values.columns.str.replace(' ', '_')
        exercise_values.columns = (x.lower() for x in exercise_values.columns)

        # In[34]:

        class Students:
            num_of_students = 0

            def __init__(self, first, last, bdate):
                self.first = first
                self.last = last
                self.bdate = bdate
                self.bdate = (
                    datetime.strptime(self.bdate, "%Y-%m-%d %H:%M:%S")
                        #             datetime.strptime(self.bdate, "%m/%d/%Y")

                        .date()
                        .strftime("%m-%d-%Y")
                )

                Students.num_of_students += 1

                self.unique_id = "{}{}{}{}".format(
                    self.last[0].upper(),
                    self.last[-1].upper(),
                    self.first[0].upper(),
                    self.birth_date(),
                )

            def birth_date(self):
                datetime_object = datetime.strptime(self.bdate, "%m-%d-%Y").date()
                date3 = datetime_object.strftime("%y%m%d")
                return date3

            def fullname(self):
                return "{} {}".format(self.first, self.last)

        # In[35]:

        # Adding unique IDs to participants
        unique_ids = []

        def add_ids(data):
            for index, row in data.iterrows():
                drvr = Students(row.firstname, row.lastname, str(row.dob))
                unique_ids.append(drvr.unique_id)

        # In[36]:

        """
        Clean empty rows covering for Excel BS
        """

        first_emprty_row = students_df[students_df.isnull().all(axis=1) == True].index.tolist()
        students_df.drop(students_df.index[first_emprty_row], inplace=True)
        # students_df

        # In[37]:

        first_emprty_row

        # In[38]:

        add_ids(students_df)

        # In[39]:

        students_df['Unique_Id'] = unique_ids

        # In[40]:

        students_df

        # In[41]:

        students_df.set_index('Unique_Id', inplace=True)

        # In[42]:

        students_df.firstname = students_df.firstname.str.strip()
        students_df.lastname = students_df.lastname.str.strip()

        # In[43]:

        students_df['fullname'] = students_df.apply(lambda row: row['firstname'] + ' ' + row['lastname'], axis=1)

        # In[44]:

        percetages_of_ex = []

        def ex_percetage(data):
            for index, row in data.iterrows():
                x = row[['v1', 'v2', 'v3']].mean()
                sd = row[['v1', 'v2', 'v3']].std()
                cns = row['cones']
                y = round(x, 2)
                z = row['speed_req']
                p = ((y / z))
                res = round(p, 2)
                if sd < 3 and cns == 0:
                    pass
                else:
                    res = 0
                percetages_of_ex.append(res)

        # In[45]:

        # Calculations call
        ex_percetage(course_df)

        # In[46]:

        # percetages_of_ex

        # In[47]:

        course_df['%_of_exercise'] = percetages_of_ex

        # In[48]:

        Car_1 = course_cars.loc[1, 'LatAcc']

        # In[49]:

        # We are seeing Gs not percetages

        percetages_of_v = []

        def v_percetage(data):
            for index, row in data.iterrows():
                vx = row[['v1', 'v2', 'v3']].mean()
                sd = row[['v1', 'v2', 'v3']].std()
                ex = row['exercise']
                R = exercise_values.loc[ex, 'radius']
                v = round(vx, 2)
                LA = ((v ** 2) / (R * 15))
                res = round(LA, 2) / course_cars.loc[1]['LatAcc']
                #         if sd < 3:
                #             pass
                #         else:
                #             res = '0'
                percetages_of_v.append(res)

        # In[50]:

        course_df

        # In[51]:

        # Calculations call
        v_percetage(course_df)

        # In[52]:

        course_df['%_of_vehicle'] = percetages_of_v

        # In[53]:

        # course_df[['participant', '%_of_vehicle']]

        # In[54]:

        # cero_value = course_df.loc[course_df['participant'] == 'Bracy Maynard']['%_of_exercise'].astype(float).apply(lambda x: (x > 0)).value_counts()[1]
        # cero_value

        # In[55]:

        counts_df = pd.DataFrame(course_df[['participant', 'exercise']])
        counts_df['%_of_exercise'] = course_df['%_of_exercise'].astype('float')
        counts_df['%_of_vehicle'] = course_df['%_of_vehicle'].astype('float')

        # In[94]:

        course_df

        # In[57]:

        counts_df = pd.DataFrame(counts_df.replace(0, np.nan)
            .groupby(['participant', 'exercise'])
            .agg(
            {'exercise': 'size', '%_of_exercise': ['count', 'mean'], '%_of_vehicle': ['min', 'max']})
            .rename(
            columns={'size': 'Count', 'count': 'Passed', 'mean': 'Av Score', 'min': 'Start Score',
                     'max': 'End Score'})).unstack(level=1)
        counts_df.columns = counts_df.columns.droplevel(0)

        # In[58]:

        # Slalom average
        slalom_avg = pd.DataFrame(course_df.replace(0, np.nan)
                                  .groupby(['participant', 'exercise'])
                                  .agg({'%_of_vehicle': 'mean'})
                                  .rename(columns={'%_of_vehicle': 'vehicle_pc_avg'})).unstack(level=1)
        # counts_df.columns = counts_df.columns.droplevel(0)

        # In[59]:

        # slalom_avg

        # In[60]:

        LnCh_count = counts_df['Count']['Lane Change']
        LnCh_passed = counts_df['Passed']['Lane Change']
        counts_df['LnCh Passed'] = (LnCh_passed / LnCh_count)
        slalom_count = counts_df['Count']['Slalom']
        slalom_passed = counts_df['Passed']['Slalom']
        counts_df['Slalom Passed'] = (slalom_passed / slalom_count)

        # In[61]:

        # counts_df.loc[counts_df['End Score']['Slalom'] < .8] #People that did not get to 80%

        # In[62]:

        finalx_df.rename(
            columns={'Exercise': 'exercise', 'Participant': 'participant', 'Car': 'car_ID', 'Pressure': 'stress',
                     'Reverse Slalom': 'rev_slalom', 'SV1': 's_v1',
                     'SV2': 's_v2', 'SV3': 's_v3', 'LChV1': 'LCh_v1', 'LChV2': 'LCh_v2', 'LChV3': 'LCh_v3',
                     'Cones': 'cones', 'Doors': 'gates', 'Time': 'g_time'}, inplace=True)

        # In[63]:

        # Time conversion to Time Delta
        finalx_df['g_time'] = pd.to_timedelta(finalx_df['g_time'], unit='s')
        finalx_df['rev_slalom'] = pd.to_timedelta(finalx_df['rev_slalom'], unit='s')
        finalx_df[['cones', 'gates']] = finalx_df[['cones', 'gates']].fillna(0).astype(int)

        # In[64]:

        finalx_df.drop('ID', axis=1, inplace=True)

        # In[95]:

        # finalx_df
        counts_df

        # In[66]:

        # Final exercise variables

        ideal_time = raw_values.loc[0, 'Ideal_Time Sec']
        c_penalty = raw_values.loc[0, 'Cone Penalty Sec']
        g_penalty = raw_values.loc[0, 'Door Penalty Sec']
        ideal_time = pd.to_timedelta(ideal_time, unit='s')
        c_penalty = pd.to_timedelta(c_penalty, unit='s')
        g_penalty = pd.to_timedelta(g_penalty, unit='s')

        # In[67]:

        # Final exercise - final time calculations

        final_fx = []

        def fx_fnl_res(data):
            for index, row in data.iterrows():
                sp = row[['s_v1', 's_v2', 's_v3']].mean()
                lcp = row[['LCh_v1', 'LCh_v2', 'LCh_v3']].mean()
                cns = row['cones']
                gts = row['gates']
                tme1 = row['g_time']
                g_tme = (tme1 + (cns * c_penalty) + (gts * g_penalty))
                f_time = (-(((g_tme / ideal_time) * 100) - 200) / 100)
                f_time = round(f_time, 2)
                final_fx.append(f_time)

        # In[68]:

        fx_fnl_res(finalx_df)

        # In[69]:

        # finalx_df

        # In[70]:

        finalx_df['f_time'] = finalx_df.apply(
            lambda row: row['g_time'] + ((row['cones'] * c_penalty) + (row['gates'] * g_penalty)), axis=1)

        # In[71]:

        # finalx_df['slalom'] = finalx_df.apply(lambda row:
        #                                       round(
        #                                           (
        #                                               (row[['s_v1', 's_v2', 's_v3']].mean())**2
        #                                           )/(
        #                                               (exercise_values.loc['Slalom', 'radius'])*15
        #                                           )
        #                                       ),
        #                                       axis=1
        #                                      )

        # In[72]:

        # finalx_df['LnCh'] = finalx_df.apply(lambda row:
        #                                       round(
        #                                           (
        #                                               (row[['LCh_v1', 'LCh_v2', 'LCh_v3']].mean())**2
        #                                           )
        #                                           /
        #                                           (
        #                                               (exercise_values.loc['Lane Change', 'radius'])*15
        #                                           )
        #                                       ),
        #                                       axis=1)

        # In[73]:

        # VBox Data procesing

        # Car 1 DataFrame
        c1_df.rename(columns={'UTC time (At Start)': 'UTC_Time'}, inplace=True)
        c1_df.drop(c1_df.index[-4:], inplace=True)
        c1_df.rename(columns={'Time (s)': 'rev_slalom'}, inplace=True)
        c1_rs_time = c1_df[['car', 'rev_slalom', 'UTC_Time']][::3]
        c1_rs_time.reset_index(drop=True, inplace=True)

        # Slalom Structure
        c1_slalom = c1_df[['Speed (Avg) (mph)', 'Speed (Std Dev) (mph)']][1::3]
        c1_slalom.reset_index(drop=True, inplace=True)
        c1_slalom.rename(columns={
            'Speed (Avg) (mph)': 'slalom_avg',
            'Speed (Std Dev) (mph)': 'slalom_std_dev',
            #     'UTC time (At Start)':'UTC_Time'
        }, inplace=True)

        # Lane Change Structure
        c1_LnCh = c1_df[['Speed (Avg) (mph)', 'Speed (Std Dev) (mph)']][2::3]
        c1_LnCh.rename(columns={
            'Speed (Avg) (mph)': 'LnCh_avg',
            'Speed (Std Dev) (mph)': 'LnCh_std_dev',
            #     'UTC time (At Start)':'UTC_Time'
        }, inplace=True)
        c1_LnCh.reset_index(drop=True, inplace=True)

        # Frame variables
        c1_frames = [c1_rs_time, c1_slalom, c1_LnCh]

        # Final DataFrames
        c1_result = pd.concat(c1_frames, join='inner', axis=1)

        # Creating Time Deltas
        c1_result['rev_slalom'] = c1_result['rev_slalom'].astype(float)
        c1_result['rev_slalom'] = pd.to_timedelta(c1_result['rev_slalom'], unit='s')

        # Converting time to datetime64
        c1_result['UTC_Time'] = (pd.to_datetime(c1_result['UTC_Time'], format=('%H:%M:%S.%f')).dt.time)

        # Changind types to float
        c1_result[['slalom_avg', 'slalom_std_dev', 'LnCh_avg', 'LnCh_std_dev']] = c1_result[
            ['slalom_avg', 'slalom_std_dev', 'LnCh_avg', 'LnCh_std_dev']].astype(float)
        c1_result.rename(columns={'car': 'car_ID'}, inplace=True)
        c1_result['car_ID'] = c1_result['car_ID'].astype(int)

        # Car 2 DataFrame
        c2_df.rename(columns={'UTC time (At Start)': 'UTC_Time'}, inplace=True)
        c2_df.drop(c2_df.index[-4:], inplace=True)
        c2_df.rename(columns={'Time (s)': 'rev_slalom'}, inplace=True)
        c2_rs_time = c2_df[['car', 'rev_slalom', 'UTC_Time']][::3]
        c2_rs_time.reset_index(drop=True, inplace=True)

        # Slalom Structure
        c2_slalom = c2_df[['Speed (Avg) (mph)', 'Speed (Std Dev) (mph)']][1::3]
        c2_slalom.reset_index(drop=True, inplace=True)
        c2_slalom.rename(columns={
            'Speed (Avg) (mph)': 'slalom_avg',
            'Speed (Std Dev) (mph)': 'slalom_std_dev',
            #     'UTC time (At End)':'UTC_Time'
        }, inplace=True)

        # Lane Change Structure
        c2_LnCh = c2_df[['Speed (Avg) (mph)', 'Speed (Std Dev) (mph)']][2::3]
        c2_LnCh.rename(columns={
            'Speed (Avg) (mph)': 'LnCh_avg',
            'Speed (Std Dev) (mph)': 'LnCh_std_dev',
            #     'UTC time (At End)':'UTC_Time'
        }, inplace=True)
        c2_LnCh.reset_index(drop=True, inplace=True)

        # Frame variables
        c2_frames = [c2_rs_time, c2_slalom, c2_LnCh]

        # Final DataFrames
        c2_result = pd.concat(c2_frames, join='inner', axis=1)

        # Creating Time Deltas
        c2_result['rev_slalom'] = pd.to_timedelta(c2_result['rev_slalom'], unit='s')

        # Converting time to datetime64
        c2_result['UTC_Time'] = (pd.to_datetime(c2_result['UTC_Time'], format=('%H:%M:%S.%f')).dt.time)

        # Changind types to float
        c2_result[['slalom_avg', 'slalom_std_dev', 'LnCh_avg', 'LnCh_std_dev']] = c2_result[
            ['slalom_avg', 'slalom_std_dev', 'LnCh_avg', 'LnCh_std_dev']].astype(float)
        c2_result.rename(columns={'car': 'car_ID'}, inplace=True)
        c2_result['car_ID'] = c2_result['car_ID'].astype(int)

        # Creating a sigle DataFrame
        vbox_df = pd.concat([c1_result, c2_result], ignore_index=True).sort_values(by=['UTC_Time']).reset_index().drop(
            ['index'], axis=1)

        # In[74]:

        vbox_df
        # c1_result

        # In[75]:

        # MSE slalom and LnCh percentages
        mse_slalom_prcnt = []
        mse_LnCh_prcnt = []

        def mse_slalom_pc(data):
            for index, row in data.iterrows():
                vx = row['slalom_avg']
                ex = 'Slalom'
                R = exercise_values.loc[ex, 'radius']
                v = round(vx, 2)
                LA = ((v ** 2) / (R * 15))
                if LA >= course_cars.loc[1]['LatAcc']:
                    res = 0
                else:
                    res = round(LA, 2) / course_cars.loc[1]['LatAcc']
                mse_slalom_prcnt.append(int((round(res, 2)) * 100))

        def mse_LnCh_pc(data):
            for index, row in data.iterrows():
                vx = row['LnCh_avg']
                ex = 'Lane Change'
                R = exercise_values.loc[ex, 'radius']
                v = round(vx, 2)
                LA = ((v ** 2) / (R * 15))
                if LA >= course_cars.loc[1]['LatAcc']:
                    res = 0
                else:
                    res = round(LA, 2) / course_cars.loc[1]['LatAcc']
                mse_LnCh_prcnt.append(int((round(res, 2)) * 100))

        # In[93]:

        # len(mse_slalom_prcnt)
        # len(finalx_df)
        finalx_df
        # vbox_df

        # In[77]:

        mse_slalom_pc(vbox_df)
        mse_LnCh_pc(vbox_df)
        finalx_df['slalom'] = mse_slalom_prcnt
        finalx_df['LnCh'] = mse_LnCh_prcnt

        # In[78]:

        finalx_df['final_result'] = final_fx

        # In[79]:

        demo_rows = finalx_df[finalx_df['participant'] == 'Demo'].index
        finalx_df.drop(demo_rows, inplace=True)
        # finalx_df

        # In[80]:

        finalx_df['rev_%'] = finalx_df.apply(lambda x: round((x['rev_slalom'] / x['g_time']), 2), axis=1)

        # In[81]:

        finalx_df = finalx_df[
            ['exercise', 'participant', 'car_ID', 'stress', 'rev_slalom', 'rev_%', 'slalom', 'LnCh', 'cones', 'gates',
             'f_time', 'final_result']]

        # In[82]:

        # Group Variables
        gasnor = int((counts_df['Count']['Slalom'].agg('mean')))  # .astype(int) # group_average_slalom_runs
        gaspoce = int((counts_df['Slalom Passed'].mean()) * 100)  # group_average_slalom_prcnt_completed
        gasaoep = int(((counts_df['Av Score']['Slalom'].mean()) * 100))  # group_average_slalom_ex_prcnt
        gasaovc = int((course_df.loc[course_df['exercise'] == 'Slalom'][
                           '%_of_vehicle'].mean()) * 100)  # group_average_slalom_vehicle_control
        galnor = int((counts_df['Count']['Lane Change'].agg('mean')))  # .astype(int) # group_average_lnch_runs
        galpoce = int((counts_df['LnCh Passed'].mean()) * 100)  # group_average_lnch_prcnt_completed
        galaoep = int(((counts_df['Av Score']['Lane Change'].mean()) * 100))  # group_average_lnch_ex_prcnt
        galaovc = int((course_df.loc[course_df['exercise'] == 'Lane Change'][
                           '%_of_vehicle'].mean()) * 100)  # group_average_lnch_vehicle_control
        mseg_t_pre = str(finalx_df['f_time'].mean())
        mseg_t = mseg_t_pre[mseg_t_pre.find(':') + 1: mseg_t_pre.find('.') + 3:]  # mse_group_av_time
        mseg_c = int((finalx_df['cones'].mean()))  # mse_group_av_cones
        mseg_g = int((finalx_df['gates'].mean()))  # mse_group_av_gates
        mseg_perf = int((finalx_df['final_result'].mean()) * 100)  # mse_group_av_performance
        mseg_per = int((finalx_df['final_result'].quantile()) * 100)  # mse_group_av_percentile
        mse_obj = str(raw_values['Ideal_Time Sec'][0])[10::]  # mse_objective_obj
        mseg_rev_pre = str(finalx_df['rev_slalom'].mean())  # strings mse_group_used_in_rev
        mseg_rev = mseg_rev_pre[
                   mseg_rev_pre.find(':') + 4: mseg_rev_pre.find('.') + 3:]  # strings mse_group_used_in_rev
        mseg_rev_pc = int(round(((finalx_df['rev_%'].mean()) * 100), 0))

        # In[83]:

        # Temporary Variables waiting for code
        msed_per = np.nan  # MSE Driver Percentile (Quantile)
        msed_rev = np.nan  # MSE Driver % Used in Reverse
        msed_rev_time = np.nan  # MSE Driver Reverse Time
        paragraph = np.nan  # Lead Instructor Feedback

        # In[84]:

        # students_df
        # raw_values
        # counts_df
        # course_df
        finalx_df
        # slalom_avg
        # slalom_avg

        # In[85]:

        # Final report DataFrame Lineup
        report_df = pd.DataFrame(students_df, columns=['fullname'])
        report_df['company'] = raw_values.loc[0, 'Client']
        report_df['program'] = raw_values.loc[0, 'Program']
        report_df['date'] = raw_values.loc[0, 'Date']

        # Versiones en ambos idiomas
        if raw_values.loc[0, 'Country'] == 'MX':
            report_df['vehicle'] = (
                    raw_values.loc[0, 'Make'] + ' (Capacidad ' + raw_values.loc[0, 'LatAcc'].astype(str) + 'g)')
        else:
            report_df['vehicle'] = (
                    raw_values.loc[0, 'Make'] + ' (' + raw_values.loc[0, 'LatAcc'].astype(str) + 'g Capability)')

        # Slalom variables
        report_df['s_no_runs'] = \
            pd.merge(left=report_df, right=(counts_df['Count']['Slalom']).astype(int), left_on='fullname',
                     right_index=True)[
                'Slalom']
        report_df['s_passed'] = \
            pd.merge(left=report_df, right=counts_df['Passed']['Slalom'], left_on='fullname', right_index=True)[
                'Slalom']
        report_df['prcnt_s_pass'] = \
            pd.merge(left=report_df, right=round((counts_df['Slalom Passed']) * 100, 0), left_on='fullname',
                     right_index=True)[
                'Slalom Passed']
        report_df['avg_ex_control_s'] = \
            pd.merge(left=report_df, right=round((counts_df['Av Score']['Slalom']) * 100, 0), left_on='fullname',
                     right_index=True)[
                'Slalom']
        report_df['avg_v_control_s'] = \
            pd.merge(left=report_df, right=round((slalom_avg['vehicle_pc_avg']['Slalom']) * 100, 0), left_on='fullname',
                     right_index=True)['Slalom']
        report_df['slalom_max'] = \
            pd.merge(left=report_df, right=round((counts_df['End Score']['Slalom']) * 100), left_on='fullname',
                     right_index=True)[
                'Slalom']

        # LnCh Variables
        report_df['lc_no_runs'] = \
            pd.merge(left=report_df, right=(counts_df['Count']['Lane Change']).astype(int), left_on='fullname',
                     right_index=True)[
                'Lane Change']
        report_df['lc_passed'] = \
            pd.merge(left=report_df, right=counts_df['Passed']['Lane Change'], left_on='fullname', right_index=True)[
                'Lane Change']
        report_df['prcnt_lc_pass'] = \
            pd.merge(left=report_df, right=round((counts_df['LnCh Passed']) * 100, 0), left_on='fullname',
                     right_index=True)[
                'LnCh Passed']
        report_df['avg_ex_control_lc'] = \
            pd.merge(left=report_df, right=round((counts_df['Av Score']['Lane Change']) * 100, 0), left_on='fullname',
                     right_index=True)['Lane Change']
        report_df['avg_v_control_lc'] = \
            pd.merge(left=report_df, right=round((slalom_avg['vehicle_pc_avg']['Lane Change']) * 100, 0),
                     left_on='fullname',
                     right_index=True)['Lane Change']
        report_df['lnch_max'] = \
            pd.merge(left=report_df, right=round((counts_df['End Score']['Lane Change']) * 100), left_on='fullname',
                     right_index=True)['Lane Change']

        # Including Comments

        # In[86]:

        finalx_df.loc[finalx_df['final_result'] < .8]

        print(finalx_df)


        # In[87]:

        report_df['prcnt_lc_pass'].astype(int)

        # In[88]:

        # Final Exercise Variables - Possible setting as table for multiple occurances
        td_start, td_stop, td_step = 10, -4, 1
        mse_report = pd.DataFrame(finalx_df.replace(np.nan, '-')
                                  .drop(['exercise', 'rev_slalom'], axis=1)
                                  )

        mse_report['f_time'] = mse_report['f_time'].astype(str)
        mse_report['f_time'] = mse_report['f_time'].str.slice(td_start, td_stop, td_step)

        if raw_values.loc[0, 'Country'] == 'MX':
            mse_report['stress'].replace((1, 0), ('Alto', 'Bajo'), inplace=True)
        else:
            mse_report['stress'].replace((1, 0), ('High', 'Low'), inplace=True)

        mse_report[['rev_%', 'final_result']] = mse_report[['rev_%', 'final_result']].apply(lambda x: x * 100).astype(
            int)
        mse_report.rename(columns={'rev_%': 'rev_pc'}, inplace=True)

        # mse_report = mse_report.set_index('participant', inplace=True)
        mse_report = mse_report.groupby('participant').apply(lambda x: x.to_dict(orient='records'))

        # ## Jinja Variables Loading

        # In[89]:

        tmplt_data = pd.read_excel('jinja_variables.xlsx', skiprows=2)
        tmplt_context = dict(zip(tmplt_data['var'], tmplt_data['value']))

        # ## Final Report Creation

        # In[90]:

        print(comments)

        ax1_slalom_plt = (course_df.loc[
                              ((course_df['participant'] == 'Student One') &
                               (course_df['exercise'] == 'Slalom')), '%_of_exercise'
                          ].astype(float)) * 100
        ax1_slalom_plt = ax1_slalom_plt.reset_index(drop=True)
        ax2_slalom_plt = (course_df.loc[
                              ((course_df['participant'] == 'Student One') &
                               (course_df['exercise'] == 'Slalom')), '%_of_vehicle'
                          ].astype(float)) * 100
        ax2_slalom_plt = ax2_slalom_plt.reset_index(drop=True)

        print(ax1_slalom_plt)
        print(ax2_slalom_plt)


        print(report_df)
        print(counts_df)
        print(course_df)
        # print(course_df.loc['participant'] == 'Student One')

        return Response({"message": "Test"}, status=status.HTTP_200_OK)

        # Cargando % de exercise and vehicle

        for index, row in course_df.iterrows():

            fullname = row['participant']

            print(fullname)

            if report_df.loc[report_df['fullname'] == fullname]['date'].empty:
                continue
            else:
                fulldate = report_df.loc[report_df['fullname'] == fullname]['date'].item()

            courseObject = {
                "student": row['participant'],
                "company": report_df.loc[report_df['fullname'] == fullname]['company'].item(),
                "program": report_df.loc[report_df['fullname'] == fullname]['program'].item(),
                "fulldate": fulldate,
                "exercise": row['exercise'],
                "pcExercise": row['%_of_exercise'],
                "pcVehicle": row['%_of_vehicle']
            }

            serializer = CourseSerializer(data=courseObject)
            if serializer.is_valid():
                serializer.save()
            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        # Cargando Final Exercise a DB

        for index, row in finalx_df.iterrows():

            fullname = row['participant']

            fulldate = report_df.loc[report_df['fullname'] == fullname]['date'].item()

            finalExercise = {
                "student": row['participant'],
                "company": report_df.loc[report_df['fullname'] == fullname]['company'].item(),
                "program": report_df.loc[report_df['fullname'] == fullname]['program'].item(),
                "fulldate": fulldate,
                "carId": row['car_ID'],
                "stress": row['stress'],
                "revSlalom": str(row['rev_slalom']),
                "revPc": row['rev_%'],
                "slalom": row['slalom'],
                "lnCh": row['LnCh'],
                "cones": row['cones'],
                "gates": row['gates'],
                "fTime": str(row['f_time']),
                "finalResult": row['final_result']
            }
            print(finalExercise)

            serializer = FinalExerciseSerializer(data=finalExercise)
            if serializer.is_valid():
                serializer.save()
            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        # Cargando Counts, Report, Slalom_avg and comments
        i = 0
        for index, row in report_df.iterrows():
            if i > len(report_df):
                break
            else:
                # Define variables for template
                student = row['fullname']
                fullname = student
                company = row['company']
                program = row['program']

                fulldate = row['date']

                vehicle = row['vehicle']
                snor = row['s_no_runs']
                spoce = int(row['prcnt_s_pass'])
                saoep = int(row['avg_ex_control_s'])
                saovc = int(row['avg_v_control_s'])
                sfpl = int(row['slalom_max'])
                lnor = row['lc_no_runs']
                lpoce = int(row['prcnt_lc_pass'])
                laoep = int(row['avg_ex_control_lc'])
                laovc = int(row['avg_v_control_lc'])  # Missing Variable
                lfpl = int(row['lnch_max'])

                reportObject = {
                    "student": student,
                    "company": company,
                    "program": program,
                    "fulldate": fulldate,
                    "vehicle": vehicle,
                    "snor": snor,
                    "spoce": spoce,
                    "saoep": saoep,
                    "saovc": saovc,
                    "sfpl": sfpl,
                    "lnor": lnor,
                    "lpoce": lpoce,
                    "laoep": laoep,
                    "laovc": laovc,
                    "lfpl": lfpl
                }

                serializer = ReportSerializer(data=reportObject)
                if serializer.is_valid():
                    serializer.save()
                else:
                    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

                countObject = {
                    "student": student,
                    "company": company,
                    "program": program,
                    "fulldate": fulldate,
                    "countLnCh": counts_df.loc[student]['Count']['Lane Change'],
                    "countSlalom": counts_df.loc[student]['Count']['Slalom'],
                    "passedLnCh": counts_df.loc[student]['Passed']['Lane Change'],
                    "passedSlalom": counts_df.loc[student]['Passed']['Slalom'],
                    "avScoreLnCh": counts_df.loc[student]['Av Score']['Lane Change'],
                    "avScoreSlalom": counts_df.loc[student]['Av Score']['Slalom'],
                    "startScoreLnCh": counts_df.loc[student]['Start Score']['Lane Change'],
                    "startScoreSlalom": counts_df.loc[student]['Start Score']['Slalom'],
                    "endScoreLnCh": counts_df.loc[student]['End Score']['Lane Change'],
                    "endScoreSlalom": counts_df.loc[student]['End Score']['Slalom'],
                    "lnChPassed": counts_df.loc[student]['LnCh Passed'],
                    "slalomPassed": counts_df.loc[student]['Slalom Passed']

                }

                serializer0 = CountSerializer(data=countObject)
                if serializer0.is_valid():
                    serializer0.save()
                else:
                    return Response(serializer0.errors, status=status.HTTP_400_BAD_REQUEST)

                slalomAvgObject = {
                    "student": student,
                    "company": company,
                    "program": program,
                    "fulldate": fulldate,
                    "vehiclePcAvgLnCh": slalom_avg.loc[student]['vehicle_pc_avg']['Lane Change'],
                    "vehiclePcAvgSlalom": slalom_avg.loc[student]['vehicle_pc_avg']['Slalom'],
                }

                serializer1 = SlalomAvgSerializer(data=slalomAvgObject)
                if serializer1.is_valid():
                    serializer1.save()
                else:
                    return Response(serializer1.errors, status=status.HTTP_400_BAD_REQUEST)

                commentsObject = {
                    "student": student,
                    "company": company,
                    "program": program,
                    "fulldate": fulldate,
                    "comment": comments.iloc[i]
                }

                i += 1

                serializer2 = CommentsSerializer(data=commentsObject)
                if serializer2.is_valid():
                    serializer2.save()
                else:
                    return Response(serializer2.errors, status=status.HTTP_400_BAD_REQUEST)

        return Response("Success", status=status.HTTP_200_OK)
