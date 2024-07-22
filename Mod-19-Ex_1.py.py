import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import streamlit as st
import timeit
from PIL import Image
from io import BytesIO

custom_params = {'axes.spines.right': False, 'axes.spines.top': False}
sns.set_theme(style='ticks', rc=custom_params)


def multiselect_filter(relatorio, col, selecionados):
    if 'all' in selecionados:
        return relatorio
    else:
        return relatorio[relatorio[col].isin(selecionados)].reset_index(drop=True)


@st.cache_data(show_spinner=True)
def load_data(file_data):
    try:
        return pd.read_csv(file_data, sep=';')
    except:
        return pd.read_excel(file_data)


@st.cache_data(show_spinner=True)
def multiselect_filter(relatorio, col, selecionados):
    if 'all' in selecionados:
        return relatorio
    else:
        return relatorio[relatorio[col].isin(selecionados)].reset_index(drop=True)


@st.cache_data(show_spinner=True)
def df_toString(df):
    return df.to_csv(index=False)


@st.cache_data(show_spinner=True)
def to_excel(df):
    output = BytesIO()
    writer = pd.ExcelWriter(output, engine='xlsxwriter')
    df.to_excel(writer, index=False, sheet_name='Sheet1')
    writer.close()
    processed_data = output.getvalue()
    return processed_data


st.set_page_config(page_title='Telemarketing analisys',
                   page_icon='./img/telmarketing_icon.png',
                   layout='wide',
                   initial_sidebar_state='expanded'
                   )


st.write('# Telemarketing analisys')
st.write('---')

image = Image.open('./img/Bank-Branding.jpg')
st.sidebar.image(image)

st.sidebar.write('## Suba o arquivo')
data_file_1 = st.sidebar.file_uploader(
    'Bank marketing data', type=['csv', 'xlsx'])

if (data_file_1 is not None):
    start = timeit.default_timer()
    bank_raw = load_data(data_file_1)

    st.write('time ', timeit.default_timer() - start)
    bank = bank_raw.copy()

    # bank_raw = pd.read_csv('./input/bank-additional-full.csv', delimiter=";")
    # bank = bank_raw.copy()

    st.write('## Antes dos filtros')
    st.write(bank_raw.head())

    csv_brutos = df_toString(bank_raw)

    st.write('### Download CSV dados brutos')
    st.download_button(label='Download data as CSV', data=csv_brutos,
                       file_name='df_csv_brutos.csv', mime='text/csv')

    df_xlsx_brutos = to_excel(bank_raw)

    st.write('### Download Excel dados brutos')
    st.download_button(label='Download Data as Excel',
                       data=df_xlsx_brutos, file_name='df_excel_brutos1.xlsx')

    with st.sidebar.form(key='sidebar_form'):
        # SELECIONA O TIPO DE GRAFICO
        graph_type = st.radio('Tipo de gráfico:', ('Barras', 'Pizza'))

        # IDADES
        max_age = int(bank['age'].max())
        min_age = int(bank['age'].min())
        idades = st.slider(label='Idade',
                           min_value=min_age,
                           max_value=max_age,
                           value=(min_age, max_age),
                           step=1)
        st.write('IDADES:', idades)
        st.write('IDADE min:', idades[0])
        st.write('IDADE max:', idades[1])

        # PROFISSOES
        jobs_list = bank['job'].unique().tolist()
        jobs_list.append('all')
        jobs_selected = st.multiselect('Profissão', jobs_list, ['all'])

        # ESTADO CIVIL
        marital_list = bank['marital'].unique().tolist()
        marital_list.append('all')
        marital_selected = st.multiselect(
            'Estado civil', marital_list, ['all'])

        # DEFAULT
        default_list = bank['default'].unique().tolist()
        default_list.append('all')
        default_selected = st.multiselect('Default', default_list, ['all'])

        # FINANCIAMENTO IMOBILIARIO
        housing_list = bank['housing'].unique().tolist()
        housing_list.append('all')
        housing_selected = st.multiselect(
            'Tem financiamento imob.?', housing_list, ['all'])

        # EMPRESTIMO?
        loan_list = bank['loan'].unique().tolist()
        loan_list.append('all')
        loan_selected = st.multiselect('Tem emprestimo?', loan_list, ['all'])

        # MEIO DE CONTATO
        contact_list = bank['contact'].unique().tolist()
        contact_list.append('all')
        contact_selected = st.multiselect(
            'Meio de contato', contact_list, ['all'])

        # MES DO CONTATO
        month_list = bank['month'].unique().tolist()
        month_list.append('all')
        month_selected = st.multiselect('Mês do contato', month_list, ['all'])

        # DIAS DA SEMANA
        day_of_week_list = bank['day_of_week'].unique().tolist()
        day_of_week_list.append('all')
        day_of_week_selected = st.multiselect(
            'Dia da semana', day_of_week_list, ['all'])

        bank = (bank.query('age >= @idades[0] and age <= @idades[1]')
                .pipe(multiselect_filter, 'job', jobs_selected)
                .pipe(multiselect_filter, 'marital', marital_selected)
                .pipe(multiselect_filter, 'default', default_selected)
                .pipe(multiselect_filter, 'housing', housing_selected)
                .pipe(multiselect_filter, 'loan', loan_selected)
                .pipe(multiselect_filter, 'contact', contact_selected)
                .pipe(multiselect_filter, 'month', month_selected)
                .pipe(multiselect_filter, 'day_of_week', day_of_week_selected)
                )

        submit_button = st.form_submit_button(label='Aplicar')

        if submit_button:
            bank = bank[(bank['age'] >= idades[0]) &
                        (bank['age'] <= idades[1])]
            bank = multiselect_filter(bank, 'job', jobs_selected)

    st.write('## Após os filtros')
    st.write(bank.head())

    csv = df_toString(bank)

    st.write('### Download CSV dados filtrados')
    st.download_button(label='Download data as CSV', data=csv,
                       file_name='df_csv_filtrados.csv', mime='text/csv')

    df_xlsx = to_excel(bank)

    st.write('### Download Excel dados filtrados')
    st.download_button(label='Download Data as Excel',
                       data=df_xlsx, file_name='df_excel_filtrados.xlsx')

    st.markdown("---")

    st.write('## Proporção de aceite')
    # # # PLOTS
    fig, ax = plt.subplots(1, 2, figsize=(10, 5))

    bank_raw_target_perc = bank_raw['y'].value_counts(
        normalize=True).to_frame()*100
    bank_raw_target_perc.columns = ['proportion']
    bank_raw_target_perc = bank_raw_target_perc.sort_index()
    try:
        bank_target_perc = bank['y'].value_counts(
            normalize=True).to_frame()*100
        bank_target_perc.columns = ['proportion']
        bank_target_perc = bank_target_perc.sort_index()
    except Exception as e:
        st.error(f'Erro no filtro: {e}')

    if graph_type == 'Barras':
        sns.barplot(x='y', y='proportion',
                    data=bank_raw_target_perc, ax=ax[0])
        ax[0].set_title('Dados brutos', fontweight='bold')
        for container in ax[0].containers:
            ax[0].bar_label(container)

        sns.barplot(x='y', y='proportion', data=bank_target_perc, ax=ax[1])
        ax[1].set_title('Dados filtrados', fontweight='bold')
        for container in ax[1].containers:
            ax[1].bar_label(container)

    else:
        bank_raw_target_perc.plot(
            kind='pie', y='proportion', autopct='%.2f', labels=bank_raw_target_perc.index, ax=ax[0])
        ax[0].set_title('Dados Brutos', fontweight='bold')

        bank_target_perc.plot(kind='pie', y='proportion',
                              autopct='%.2f', labels=bank_target_perc.index, ax=ax[1])
        ax[1].set_title('Dados Filtrados', fontweight='bold')

    st.pyplot(fig)
