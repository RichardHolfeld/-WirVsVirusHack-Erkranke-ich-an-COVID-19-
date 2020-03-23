# -*- coding: utf-8 -*-
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from matplotlib import style
from tkinter import *

OPTIONS = ["Baden-Württemberg", "Bayern", "Berlin", "Brandenburg", "Bremen", "Hamburg", "Hessen", "Mecklenburg-Vorpommern",
           "Niedersachsen", "Nordrhein-Westfalen", "Rheinland-Pfalz", "Saarland", "Sachsen", "Sachsen-Anhalt",
           "Schleswig-Holstein", "Thüringen", "Gesamt"]

duration = [10, 20, 30, 60, 90, 150, 200, 250]

germany = {"Baden-Württemberg": 11069533, "Bayern": 13076721, "Berlin": 3644826, "Brandenburg": 2511917,
"Bremen": 682986, "Hamburg": 1841179, "Hessen": 6265809, "Mecklenburg-Vorpommern": 1609675, "Niedersachsen": 7982448,
"Nordrhein-Westfalen": 17932651, "Rheinland-Pfalz": 4084844, "Saarland": 990509, "Sachsen": 4077937, "Sachsen-Anhalt": 2208321,
"Schleswig-Holstein": 2896712, "Thüringen": 2143145, "Gesamt": 83019213}

window = Tk()
window.title("Geben Sie Ihr Bundesland an.")
window.geometry("400x400")

my_location = []
def ok():
    Label(window, text=variable.get()).pack()
    my_location.append(str(variable.get()))
    window.destroy()
variable = StringVar(window)
variable.set(OPTIONS[0]) # default value
w = OptionMenu(window, variable, *OPTIONS)
w.pack()
button = Button(window, text="OK", command=ok)
button.pack()
window.mainloop()
my_location=my_location[0]
print(my_location)

window = Tk()
window.title("Geben Sie die Simulationsdauer an.")
window.geometry("400x400")

t_max = []
def ok():
    Label(window, text=variable.get()).pack()
    t_max.append(str(variable.get()))
    window.destroy()
variable = StringVar(window)
variable.set(duration[0]) # default value
w = OptionMenu(window, variable, *duration)
w.pack()
button = Button(window, text="OK", command=ok)
button.pack()
window.mainloop()
t_max=t_max[0]

df_pop = pd.DataFrame(germany, index=[0])
#my_location = str('Bayern')
#print('Sie sind in ' + my_location)

for key in list(germany):
    if key != my_location:
        del germany[key]
print(germany)

url = r'https://raw.githubusercontent.com/covid19-eu-zh/covid19-eu-data/master/dataset/covid-19-de.csv'
df = pd.read_csv(url, encoding='utf-8', sep=',|,,', engine ='python')
#df = pd.read_csv(r'C:\Users\richa\OneDrive\Dokumente\Programming\Hackathon\de_cases.csv')
df = df[df.nuts_1 == my_location]

#Population in Germany
#df_pop = pd.read_csv(r'C:\Users\richa\OneDrive\Dokumente\Programming\Hackathon\pop_ger.csv', encoding='latin1')
#df_pop = df_pop[df_pop[my_location] == my_location]
Population = germany[my_location]
print(Population)
#Create numpy-arrays for the fit.
#nf_pop = np.array(germany[my_location])
nf_case = df['cases'].to_numpy()
#nf_d = df['datetime'].to_numpy() if you got the datetime nicely.
nf_d = np.array(range(0,len(nf_case)))
#By subtracting by 7, I am assuming that cases will be diagnosed in one week, so the confirmed cases are a week behind.
nf_d = np.add(nf_d,-len(nf_case))
#print('NFPOP')
#print(nf_pop)

#SEIR model obtained from this link:
#https://towardsdatascience.com/social-distancing-to-slow-the-coronavirus-768292f04296
def seir_model(init_vals, params, t):
    S_0, E_0, I_0, R_0 = init_vals
    S, E, I, R = [S_0], [E_0], [I_0], [R_0]
    alpha, beta, gamma = params
    dt = t[1] - t[0]
    for _ in t[1:]:
        next_S = S[-1] - (beta*S[-1]*I[-1])*dt
        next_E = E[-1] + (beta*S[-1]*I[-1] - alpha*E[-1])*dt
        next_I = I[-1] + (alpha*E[-1] - gamma*I[-1])*dt
        next_R = R[-1] + (gamma*I[-1])*dt
        S.append(next_S)
        E.append(next_E)
        I.append(next_I)
        R.append(next_R)
    #print(I)
    return np.stack([S, E, I, R]).T

def seir_model_with_soc_dist(init_vals, params2, t):
    S_0, E_0, I_0, R_0 = init_vals
    S, E, I, R = [S_0], [E_0], [I_0], [R_0]
    alpha, beta, gamma, rho = params2
    dt = t[1] - t[0]
    for _ in t[1:]:
        next_S = S[-1] - (rho*beta*S[-1]*I[-1])*dt
        next_E = E[-1] + (rho*beta*S[-1]*I[-1] - alpha*E[-1])*dt
        next_I = I[-1] + (alpha*E[-1] - gamma*I[-1])*dt
        next_R = R[-1] + (gamma*I[-1])*dt
        S.append(next_S)
        E.append(next_E)
        I.append(next_I)
        R.append(next_R)
    return np.stack([S, E, I, R]).T

#Define parameters
t_max=int(t_max)
#t_max = 60
dt = .1
t = np.linspace(0, t_max, int(t_max/dt) + 1)
N = Population
R0 = 3.5
cases = nf_case[-1]
#N = 10000
init_vals = 1 - R0*cases/N, R0*cases/N, cases/N, 0
#init_vals = N-1692, 1692, 0, 0
alpha = 0.2
beta = 1.75
gamma = 0.5
rho = 0.5
params = alpha, beta, gamma
params2 = alpha, beta, gamma, rho
#Run simulation
results = seir_model(init_vals, params, t)
#Wie oft führt eine Begegnung zu einer Infektion?
Q = 0.5

#With social distancing
results2 = seir_model_with_soc_dist(init_vals, params2, t)

#####Plotting
style.use('fivethirtyeight')
#Plot Infected People
y2 = np.multiply(1, [item[2] for item in results2])
y2 = np.multiply(N, [item[2] for item in results2])
plt.plot(t, y2, label = 'Mit Social Distancing')
y = np.multiply(N, [item[2] for item in results])
plt.plot(t, y, label = 'Ohne Social Distancing')
plt.plot(nf_d, df['cases'], '.', label = 'Daten ' + my_location)

plt.ylabel('Infizierte', fontsize = 15)
plt.xlabel('Tage', fontsize = 15)
plt.title('Vorhersage infizierte Menschen', fontsize = 16)
plt.gcf().subplots_adjust(bottom=0.15, left=0.2)
plt.legend(fontsize=10)
plt.show()

#Pk = lamb^k/np.math.factorial(k)*exp(-lamb)
def CalculateProb(list, result, name, meetings):
    Pk_List = []
    for element in list:
        lamb = element / N * meetings
        Pk = 0
        for k in range(1,10):
            Pk = Pk+lamb**k*Q/np.math.factorial(k)*np.exp(-lamb)
        Pk_List.append(Pk)
    print(Pk_List)
    Pk_List = np.multiply(100, [item for item in Pk_List])
    plt.plot(t, Pk_List, label = name)
    return

#Wahrscheinlichkeit dass man sich nicht ansteckt
#p_not = p0+p1(1-Q)+p2(1-Q)^2+p3(1-Q)^3+p4(1-Q)^4+p5(1-Q)^5
#Plot Probabilities
#y2 = np.multiply(100, [item[2] for item in results2])
#plt.plot(t, y2, label = 'Mit Social Distancing')
#y = np.multiply(100,[item[2] for item in results])
#plt.plot(t, y, label = 'Ohne Social Distancing')
#plt.plot(nf_d, 100*df['cases']/N, '.', label = 'Daten ' + my_location)

CalculateProb(y2, results2, 'Mit Social Distancing', 1)
CalculateProb(y, results, 'Ohne Social Distancing', 8)

plt.ylabel('Wahrscheinlichkeit in %', fontsize = 15)
plt.xlabel('Tage', fontsize = 15)
plt.title('Wahrscheinlichkeit, an COVID-19 zu erkranken', fontsize = 16)
plt.gcf().subplots_adjust(bottom=0.15, left=0.2)
plt.legend(fontsize=10)
plt.show()
