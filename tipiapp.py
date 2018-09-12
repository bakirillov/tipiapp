import os
import time
import uuid
import dash
import datetime
import numpy as np
import pandas as pd
import plotly.tools as tls
import scipy.stats as stats
from flask_caching import Cache
import matplotlib.pyplot as plt
from sqlitedict import SqliteDict
import dash_core_components as dcc
import dash_html_components as html
from matplotlib.patches import Patch
from dash.dependencies import Input, Output

db = SqliteDict("responses.sqlite", autocommit=False)
app = dash.Dash()

def serve_layout():
    session_id = str(uuid.uuid4())
    return html.Div([
        html.Div(session_id, id='session-id', style={'display': 'none'}),
        html.Center([
        html.H1("TIPI-RU"),
        html.Div(id="output"),
        html.H3("Демографическая информация"),
        ]),
        html.Hr(),
        html.Div([
            html.Div(["Ваш возраст (полных лет):  ", dcc.Input(
                placeholder='Введите возраст...',
                type='number',
                size=100, inputmode="numeric",
                value='', id="age"
            )], className="four columns"),
            html.Div(["Ваш пол:", dcc.Slider(
                min=0,
                max=1,
                marks={i: a for i,a in enumerate(["мужской", "женский"])},
                value=0, id="gender"
            )], className="four columns"),
            html.Div(["Ваше образование:",
            dcc.Dropdown(
                options=[
                    {'label': 'среднее общее', 'value': 'highschool'},
                    {'label': 'среднее специальное', 'value': 'ptu'},
                    {'label': 'неоконченное высшее', 'value': 'dropout'},
                    {'label': 'высшее (бакалавриат)', 'value': 'bachelor'},
                    {'label': 'высшее (специалитет)', 'value': 'specialist'},
                    {'label': 'высшее (магистратура)', 'value': 'master'},
                    {'label': 'кандидатская степень', 'value': 'phd'},
                    {'label': 'докторская степень', 'value': 'dsc'},
                ],
                value='na', id="education"
            )], className="four columns")
        ], className="row"),
        html.Div([
        html.Div([
        html.Hr(),
        html.Center([
        html.H3("Я воспринимаю себя как")
        ]),
        html.Hr(),
        html.Div([
        html.Div([html.Center(["открытого, полного энтузиазма"]),
        dcc.Slider(
            min=1,
            max=7,
            marks={i: str(i) for i in range(1,8)},
            value=0, id="tipi1"
        )], className="six columns"),
        html.Div([html.Center(["критичного, склонного спорить"]),
        dcc.Slider(
            min=1,
            max=7,
            marks={i: str(i) for i in range(1,8)},
            value=0, id="tipi2"
        )], className="six columns")], className="row"),
        html.Hr(),
        html.Div([
        html.Div([html.Center(["надежного и дисциплинированного"]),
        dcc.Slider(
            min=1,
            max=7,
            marks={i: str(i) for i in range(1,8)},
            value=0, id="tipi3"
        )], className="six columns"),
        html.Div([html.Center(["тревожного, меня легко расстроить"]),
        dcc.Slider(
            min=1,
            max=7,
            marks={i: str(i) for i in range(1,8)},
            value=0, id="tipi4"
        )], className="six columns")
        ], className="row"),
        html.Hr(),
        html.Div([
        html.Div([html.Center(["открытого для нового опыта, сложного"]),
        dcc.Slider(
            min=1,
            max=7,
            marks={i: str(i) for i in range(1,8)},
            value=0, id="tipi5"
        )],className="six columns"),
        html.Div([html.Center(["замкнутого, тихого"]),
        dcc.Slider(
            min=1,
            max=7,
            marks={i: str(i) for i in range(1,8)},
            value=0, id="tipi6"
        )],className="six columns")], className="row"),
        html.Hr(),
        html.Div([
        html.Div([html.Center(["сочувствующего, сердечного"]),
        dcc.Slider(
            min=1,
            max=7,
            marks={i: str(i) for i in range(1,8)},
            value=0, id="tipi7"
        )],className="six columns"),
        html.Div([html.Center(["неорганизованного, беспечного"]),
        dcc.Slider(
            min=1,
            max=7,
            marks={i: str(i) for i in range(1,8)},
            value=0, id="tipi8"
        )],className="six columns")], className="row"),
        html.Hr(),
        html.Div([
        html.Div([html.Center(["спокойного, эмоционально устойчивого"]),
        dcc.Slider(
            min=1,
            max=7,
            marks={i: str(i) for i in range(1,8)},
            value=0, id="tipi9"
        )],className="six columns"),
        html.Div([html.Center(["обыкновенного, не творческогоо"]),
        dcc.Slider(
            min=1,
            max=7,
            marks={i: str(i) for i in range(1,8)},
            value=0, id="tipi10"
        )],className="six columns")], className="row"),
        html.Hr(),
        html.Center([html.Button("Получить результаты", id='button')]),], id="main-field"),
        ])
    ], id="page-content")

app.layout = serve_layout

population_statistics = {
    "Экстравертность": {0: [4.716, 1.503111], 1: [4.838164, 1.480678]}, 
    "Конформизм": {0: [3.848, 1.198706], 1: [4.292271, 1.176599]}, 
    "Добросовестность": {0: [4.852, 1.378440], 1: [5.152174, 1.255820]},
    "Эмоциональная стабильность": {0: [4.856, 1.493072], 1: [3.739130, 1.513088]}, 
    "Открытость новому опыту": {0: [4.974, 1.186728], 1: [5.178744, 1.233366]}
}

def plot_picture(v):
    name = v[0]
    value = v[1]
    numb = v[2]
    gender = v[3]
    h = np.linspace(1,7)
    mpl_fig = plt.figure()
    ax = mpl_fig.add_subplot(111)
    st = population_statistics[name][gender]
    pdf = stats.norm.pdf(h, st[0], st[1])
    graph = dcc.Graph(
        id="pic"+str(numb), 
        figure={
            'data': [
                {'x': h, 'y': pdf, 'type': 'bar', 'name': 'Популяция'},
                {"x": [value], "y": [0.2], "type": "scatter", "name": "Ваш результат"}
            ],
            'layout': {
                'title': name,
                "showlegend": True,
                "shapes": [{
                    'type': 'line',
                    'x0': value,
                    'y0': 0,
                    'x1': value,
                    'y1': 0.5,
                    'line': {
                        'color': 'rgb(255, 127, 14)',
                        'width': 3,
                    },
                }],
            }
        }
    )
    return(graph)

descriptions = {
    "Экстравертность": ["Вы - общительны, легко находите общий язык с самыми разными людьми, умеете получать удовольствие от хорошей беседы. Вы умеете убеждать других людей в своей правоте, можете быть даже чересчур настойчивым. И, наверняка у вас отлично получается быстро объединять людей для решения общей задачи (особенно - в краткосрочной перспективе). Помимо этого вы не любите сидеть на одном месте и всегда готовы к неожиданным приключениям и ярким эмоциям", "Вы не слишком общительны. Вы не любите находиться в центре внимания других людей. Когда вы беседуете, особенно с незнакомыми людьми, вы часто мучительно думаете, что надо сказать, сравниваете разные варианты. В итоге бывает, что когда вы, наконец, придумали, что сказать, момент уже упущен. При этом вы - отличный слушатель, и действительно слушаете, что говорит Ваш собеседник, не пытаясь перебить его или перевести разговор на себя. Вы внимательно выбираете людей для общения, и особенно - для дружбы. Вам не нравятся шумные сборища, особенно те, где много незнакомых вам людей."],
    "Конформизм": ["Вы - добрый, тактичный человек, умеющий уважать себя и окружающих. Бывают ситуации, когда вы готовы поступиться своими интересами во имя другого человека или важной общей цели. Вы умеете чувствовать эмоции других людей, сопереживать и помогать. Вы готовы доверять другим людям, даже если сталкивались с ситуациями, когда доверие не было оправдано. Вам бы хотелось работать с людьми, разделяющими ваши ценности и убеждения", "Вы - независимый одиночка. Часто вы высказываете свое мнение не заботясь о том, что оно может кого-то обидеть. Вы предпочитаете не доверять другим людям. Вы с сарказмом относитесь к социальным нормам и правилам, даже если придерживаетесь их. Вряд ли кто-то назовет вас добрым или понимающим человеком, зато мало кто попытается заставить вас решать чужие проблемы."],
    "Добросовестность": ["Вы умеете ставить цели и добиваться их исполнения. Вы - дисциплинированы, способны к системной работе, умеете адекватно оценивать получившиеся результаты. У вас часто получается фокусироваться на задаче, не отвлекаясь на посторонние раздражители. Вас не нужно контролировать - работа будет выполнена в срок и качественно", "Вам часто трудно контролировать себя, свои желания, чувства и поступки. Под влиянием минутного импульса вы можете сказать или сделать что-то, о чем потом будете сожалеть. Даже если работа вам нравится, приходится бороться с приступами прокрастинации; в то же время, если вы увлеклись по- настоящему, то можете работать практически круглые сутки, забывая о сне и еде."],
    "Открытость новому опыту": ["Вам нравится учиться новому и расширять кругозор. Скорее всего, у вас богатое воображение и вы умеете находить новые, нестандартные решения как в рабочих так и в житейских задачах. Вам очень быстро надоедает однообразие, монотонная деятельность. Вы любопытны и сообразительны.", "Вы предпочитаете стандартную, упорядоченную деятельность, даже если она иногда оказывается монотонной. Вы знаете то, что вы знаете и не гонитесь за разнообразием впечатлений и новой информацией. Скорее всего вы предпочитаете классическое искусство современному. Вы человек практической хватки и практических интересов и редко витаете в облаках"],
    "Эмоциональная стабильность": ["Вас легко взволновать или расстроить. Вы часто переживаете, в том числе по незначительным поводам. Вас могут раздражать неумеренно восторженные или пофигистичные люди. К себе вы относитесь критически и вам кажется, что и прочие люди в глаза и за глаза вас критикуют. Вам трудно не сравнивать себя с другими. К планам на будущее вы подходите с умеренным пессимизмом.", "Вы склонны доверять себе, своему опыту и интуиции. Вас трудно расстроить или вывести из себя. В сложных, напряженных ситуациях вы умеете не поддаваться панике и продолжать действовать."]
}

@app.callback(Output('output', 'children'),
              [Input('button', 'n_clicks'),
               Input('session-id', 'children'),
               Input('tipi1', 'value'),
               Input('tipi2', 'value'),
               Input('tipi3', 'value'),
               Input('tipi4', 'value'),
               Input('tipi5', 'value'),
               Input('tipi6', 'value'),
               Input('tipi7', 'value'),
               Input('tipi8', 'value'),
               Input('tipi9', 'value'),
               Input('tipi10', 'value'),
               Input("gender", "value"),
               Input("education", "value"),
               Input("age", "value")
              ])
def display_value(n_clicks, session_id, t1, t2, t3, t4, t5, t6, t7, t8, t9, t10, gender, education, age):
    if n_clicks:
        uD = [7,6,5,4,3,2,1]
        answers = [t1, t2, t3, t4, t5, t6, t7, t8, t9, t10]
        names = [
            "Экстравертность", "Конформизм", "Добросовестность",
            "Эмоциональная стабильность", "Открытость новому опыту"
        ]
        if 0 in answers:
            results = ["Вы ответили не на все вопросы!"]
        else:
            values = list(zip(names, [
                0.5*(answers[0] + uD.index(answers[5])),
                0.5*(answers[6] + uD.index(answers[1])),
                0.5*(answers[2] + uD.index(answers[7])),
                0.5*(answers[8] + uD.index(answers[3])),
                0.5*(answers[4] + uD.index(answers[9]))
            ], range(5), [gender]*5))
            store = {}
            store["answers"] = answers
            store["items"] = [a[1] for a in values]
            store["gender"] = gender
            store["age"] = age
            store["education"] = education
            db[session_id] = store
            db.commit()
            results = [
                    html.Div([
                        html.Div([descriptions[values[0][0]][0]], className="four columns"),
                        html.Div([plot_picture(values[0])], className="four columns"), 
                        html.Div([descriptions[values[0][0]][1]], className="four columns")
                    ], className="row"),
                    html.Div([
                        html.Div([descriptions[values[1][0]][0]], className="four columns"),
                        html.Div([plot_picture(values[1])], className="four columns"),
                        html.Div([descriptions[values[1][0]][1]], className="four columns")
                    ], className="row"),
                    html.Div([
                        html.Div([descriptions[values[2][0]][0]], className="four columns"),
                        html.Div([plot_picture(values[2])], className="four columns"),
                        html.Div([descriptions[values[2][0]][1]], className="four columns")
                    ], className="row"),
                    html.Div([
                        html.Div([descriptions[values[3][0]][0]], className="four columns"),
                        html.Div([plot_picture(values[3])], className="four columns"),
                        html.Div([descriptions[values[3][0]][1]], className="four columns")
                    ], className="row"),
                    html.Div([
                        html.Div([descriptions[values[4][0]][0]], className="four columns"),
                        html.Div([plot_picture(values[4])], className="four columns"),
                        html.Div([descriptions[values[4][0]][1]], className="four columns")
                    ], className="row"),
                ]
        return(
            html.Div([
                html.Hr(), html.Center(html.H3("Результаты")), html.Hr(),
                *results,
                html.Hr()
            ])
        )
    
    
app.css.append_css(
    {
         "external_url": "https://codepen.io/chriddyp/pen/bWLwgP.css"
    }
)
app.css.append_css(
    {
        "external_url": "https://codepen.io/chriddyp/pen/brPBPO.css"
    }
)

if __name__ == '__main__':
    app.run_server(debug=True)
